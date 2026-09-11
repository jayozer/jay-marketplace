from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verification_checks import parse_checks
from test_benchmark_goals import executable_goal, run_benchmark


class ExplicitExecutionTests(unittest.TestCase):
    def test_inspection_files_never_execute_even_when_prose_says_shows_or_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            script = directory / "inspect-only.sh"
            script.write_text("#!/bin/sh\ntouch marker\n")
            script.chmod(0o755)
            for verb in ("and review its contents", "shows the config", "passes review", "exits 0"):
                goal = ("/goal Review the script.\nDone when:\n- Its contents are reviewed.\n"
                        f"Verification:\n- Read `./inspect-only.sh` {verb}.")
                result = run_benchmark(goal, "--test-commands", "--yes", cwd=directory)
                self.assertEqual(result.returncode, 3, result.stderr)
                self.assertFalse((directory / "marker").exists())
                self.assertEqual(json.loads(result.stdout)["execution_plan"], [])

    def test_exact_command_bytes_and_cwd_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = "printf '%s' 'a; b, c and d'; printf '.'"
            result = run_benchmark(executable_goal(command, tmp), "--test-commands", "--yes")
            self.assertEqual(result.returncode, 0, result.stderr)
            [check] = json.loads(result.stdout)["analyses"][0]["command_tests"]
            self.assertEqual(check["command"], command)
            self.assertEqual(check["cwd"], str(Path(tmp).resolve()))
            self.assertEqual(check["output"], "a; b, c and d.")

    def test_expected_nonzero_is_success_only_when_declared(self):
        result = run_benchmark(executable_goal("exit 7", expected_exit=7), "--test-commands", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["summary"]["status"], "PASS")
        missing = run_benchmark(executable_goal("missing-check-xyz", expected_exit=127), "--test-commands", "--yes")
        self.assertEqual(missing.returncode, 1)

    def test_literal_json_in_a_command_is_not_a_template_placeholder(self):
        command = '''printf '%s' '{"ok": true}' '''.rstrip()
        result = run_benchmark(executable_goal(command), "--test-commands", "--yes")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)["analyses"][0]["command_tests"][0]["output"], '{"ok": true}')

    def test_shell_variables_and_awk_are_not_authoring_placeholders(self):
        cases = [
            ('GOAL_CHECK_VALUE=expected; printf \'%s\' "$GOAL_CHECK_VALUE"', 'expected'),
            ('GOAL_CHECK_VALUE=expected; printf \'%s\' "${GOAL_CHECK_VALUE}"', 'expected'),
            ("printf 'expected\\n' | awk '{print}'", 'expected\n'),
        ]
        for command, expected in cases:
            with self.subTest(command=command):
                result = run_benchmark(executable_goal(command), "--test-commands", "--yes")
                self.assertEqual(result.returncode, 0, result.stdout)
                report = json.loads(result.stdout)
                self.assertEqual(report["analyses"][0]["unresolved_placeholders"], [])
                self.assertEqual(report["analyses"][0]["command_tests"][0]["output"], expected)

    def test_exact_pairs_deduplicate_but_prefix_commands_and_directories_survive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = [root / name for name in ("one", "two")]
            for path in paths:
                path.mkdir()
                checks = [
                    {"command": "echo hit >> count", "cwd": "."},
                    {"command": "echo hit >> count", "cwd": "."},
                    {"command": "echo hit >> count; echo extra >> count", "cwd": "."},
                ]
                text = "/goal Count.\nDone when:\n- Both checks pass.\nVerification:\n"
                text += "\n".join("- Command: " + json.dumps(c) for c in checks)
                (path / "goal.md").write_text(text)
            result = run_benchmark(str(root), "--test-commands", "--yes")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(len(report["execution_plan"]), 4)
            for path in paths:
                self.assertEqual((path / "count").read_text(), "hit\nhit\nextra\n")

    def test_conflicting_expected_exits_share_execution_but_each_is_evaluated(self):
        first = executable_goal("exit 7", expected_exit=7)
        second = executable_goal("exit 7", expected_exit=0)
        result = run_benchmark(first, second, "--test-commands", "--yes")
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(report["execution_plan"]), 1)
        self.assertEqual([a["verification_status"] for a in report["analyses"]], ["PASS", "FAIL"])

    def test_successful_commands_do_not_discharge_manual_checks(self):
        goal = executable_goal("true") + "\n- Manual: Confirm the two screenshots have the same labels."
        result = run_benchmark(goal, "--test-commands", "--yes")
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(report["summary"]["status"], "MANUAL")
        self.assertEqual(report["summary"]["manual_checks"], 1)
        self.assertEqual(report["analyses"][0]["command_tests"][0]["status"], "PASS")

    def test_placeholder_or_malformed_record_prevents_all_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "marker"
            for invalid in ('{"command":"true"}', '{"command":"<COMMAND>","cwd":"."}',
                            '{"command":"[TEST COMMAND]","cwd":"."}'):
                goal = executable_goal(f"touch {marker}") + "\n- Command: " + invalid
                result = run_benchmark(goal, "--test-commands", "--yes")
                self.assertEqual(result.returncode, 1)
                self.assertFalse(marker.exists())

    def test_missing_working_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_benchmark(executable_goal("true", str(Path(tmp) / "missing")), "--test-commands", "--yes")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["analyses"][0]["command_tests"][0]["can_run"])

    def test_complete_plan_is_shown_before_any_command_starts(self):
        result = run_benchmark(executable_goal("true"), executable_goal("echo last"), "--test-commands", "--yes")
        last_preview = result.stderr.index('"command": "echo last"')
        first_run = result.stderr.index("Running verification command")
        self.assertLess(last_preview, first_run)


class ReadinessTests(unittest.TestCase):
    def test_template_and_readiness_are_distinct(self):
        goal = "/goal Produce [OUTPUT].\nDone when:\n- All required fields exist.\nVerification:\n- Manual: Review [OUTPUT]."
        template = run_benchmark(goal, "--mode", "template")
        ready = run_benchmark(goal, "--mode", "readiness")
        self.assertEqual(template.returncode, 0)
        self.assertEqual(json.loads(template.stdout)["summary"]["status"], "STRUCTURE_ONLY")
        self.assertEqual(ready.returncode, 1)

    def test_unresolved_boundary_and_decision_prevent_readiness(self):
        for addition in ("\nConstraints:\n- Only modify [FILES].", "\nDecisions needed:\n- Owner must select a deployment environment."):
            result = run_benchmark(executable_goal("true") + addition, "--strict")
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertTrue(json.loads(result.stdout)["analyses"][0]["readiness_issues"])

    def test_ready_is_not_verification_pass(self):
        result = run_benchmark(executable_goal("false"), "--mode", "readiness")
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["summary"]["status"], "READY")
        self.assertEqual(report["analyses"][0]["verification_status"], "PENDING")

    def test_allow_empty_is_explicit_and_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = run_benchmark(tmp)
            allowed = run_benchmark(tmp, "--allow-empty")
        self.assertEqual(empty.returncode, 2)
        self.assertEqual(allowed.returncode, 0)
        self.assertEqual(json.loads(allowed.stdout)["summary"]["status"], "EMPTY_ALLOWED")

    def test_invalid_execution_arguments_fail_before_running(self):
        for value in ("0", "-1", "nan", "inf"):
            result = run_benchmark(executable_goal("true"), "--test-commands", "--yes", "--timeout", value)
            self.assertEqual(result.returncode, 2)
        result = run_benchmark(executable_goal("true"), "--test-commands", "--mode", "template")
        self.assertEqual(result.returncode, 2)


class RecordValidationTests(unittest.TestCase):
    def test_rejects_ambiguous_or_malformed_records(self):
        cases = [
            '{"command":"true","cwd":".","expected_exit":true}',
            '{"command":"true","cwd":".","expected_exit":256}',
            '{"command":"true","cwd":".","expected_exit":0,"expected_exit":7}',
            '{"command":"true","cwd":".","optional":true}',
            '{"command":"","cwd":"."}',
            '{"command":"true","cwd":"","expected_exit":0}',
            '["true"]', 'true', 'invalid',
        ]
        for body in cases:
            with self.subTest(body=body):
                commands, _, errors = parse_checks(["Command: " + body])
                self.assertEqual(commands, [])
                self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
