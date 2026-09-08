from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
BENCHMARK = SCRIPTS / "benchmark_goals.py"
sys.path.insert(0, str(SCRIPTS))

from benchmark_goals import analyze_goal, extract_verification_commands  # noqa: E402
from benchmark_goals import test_verification_command as run_verification_command  # noqa: E402
from goal_parsing import parse_goal  # noqa: E402


def run_benchmark(
    *args: str, cwd: Path | None = None, stdin_text: str = ""
) -> subprocess.CompletedProcess[str]:
    """Run benchmark_goals.py as a subprocess so exit codes are observed for real."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, str(BENCHMARK), *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        check=False,
    )


def legacy_goal(command: str) -> str:
    return f"/goal Check. Done only when {command} exits 0, proven by running {command}."


class TestCommandsExecutionTests(unittest.TestCase):
    def test_test_commands_without_yes_runs_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "marker"
            report_path = Path(tmp) / "report.json"
            result = run_benchmark(
                legacy_goal(f"touch {marker}"),
                "--test-commands",
                "-o",
                str(report_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(marker.exists(), "command ran without --yes")
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["execution"], "skipped: pass --yes to run")
            self.assertEqual(report["analyses"][0]["command_tests"], [])
            self.assertIn(f"command_line: touch {marker}", result.stderr)

    def test_missing_command_fails_the_run(self) -> None:
        result = run_benchmark(
            legacy_goal("definitely-not-a-cmd-xyz"), "--test-commands", "--yes"
        )

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        [analysis] = report["analyses"]
        [command_test] = analysis["command_tests"]
        self.assertFalse(command_test["can_run"])
        self.assertEqual(command_test["exit_code"], 127)
        self.assertEqual(report["summary"]["goals_with_issues"], 1)
        self.assertTrue(
            any(
                issue.startswith(
                    "Verification command 'definitely-not-a-cmd-xyz' could not run: "
                )
                for issue in analysis["issues"]
            ),
            analysis["issues"],
        )

    def test_nonzero_exit_fails_the_run(self) -> None:
        result = run_benchmark(legacy_goal("exit 7"), "--test-commands", "--yes")

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        [analysis] = report["analyses"]
        [command_test] = analysis["command_tests"]
        self.assertTrue(command_test["can_run"])
        self.assertEqual(command_test["exit_code"], 7)
        self.assertIn("Verification command 'exit 7' exited 7", analysis["issues"])
        self.assertIn("1 goal(s) have issues.", result.stderr)

    def test_successful_command_passes(self) -> None:
        result = run_benchmark(legacy_goal("echo hello"), "--test-commands", "--yes")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        [analysis] = report["analyses"]
        [command_test] = analysis["command_tests"]
        self.assertTrue(command_test["can_run"])
        self.assertEqual(command_test["exit_code"], 0)
        self.assertEqual(command_test["output"], "hello\n")
        self.assertEqual(analysis["issues"], [])
        self.assertIn(
            "Running verification command from command_line: echo hello",
            result.stderr,
        )

    def test_prose_label_before_a_backticked_command_does_not_fail_the_run(self) -> None:
        result = run_benchmark(
            "/goal Check. Done only when lint is clean. "
            "Verification: Lint clean: `true` passes.",
            "--test-commands",
            "--yes",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        [analysis] = report["analyses"]
        self.assertEqual(analysis["verification_commands"], ["true"])
        self.assertEqual([test["command"] for test in analysis["command_tests"]], ["true"])
        self.assertEqual(analysis["issues"], [])


class CommandIsolationTests(unittest.TestCase):
    def test_commands_do_not_inherit_the_benchmark_stdin(self) -> None:
        result = run_benchmark(
            legacy_goal("cat -"), "--test-commands", "--yes", stdin_text="from-parent\n"
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        [analysis] = json.loads(result.stdout)["analyses"]
        [command_test] = analysis["command_tests"]
        self.assertEqual(command_test["exit_code"], 0)
        self.assertEqual(command_test["output"], "")


class TimeoutTests(unittest.TestCase):
    def test_timeout_flag_bounds_the_command(self) -> None:
        started = time.monotonic()
        result = run_benchmark(
            legacy_goal("sleep 5"), "--test-commands", "--yes", "--timeout", "1"
        )
        elapsed = time.monotonic() - started

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertLess(elapsed, 4)
        [analysis] = json.loads(result.stdout)["analyses"]
        [command_test] = analysis["command_tests"]
        self.assertFalse(command_test["can_run"])
        self.assertIsNone(command_test["exit_code"])
        self.assertIn(
            "Verification command 'sleep 5' could not run: Command timed out after "
            "1 seconds",
            analysis["issues"],
        )


    def test_timeout_kills_the_whole_process_group(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            spawner = Path(tmp) / "spawn.sh"
            pid_file = Path(tmp) / "pid"
            spawner.write_text(
                'sleep 30 & echo $! > "$1"; wait\n', encoding="utf-8"
            )
            result = run_benchmark(
                legacy_goal(f"sh {spawner} {pid_file}"),
                "--test-commands",
                "--yes",
                "--timeout",
                "1",
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            child_pid = int(pid_file.read_text(encoding="utf-8").strip())

        deadline = time.monotonic() + 3
        while time.monotonic() < deadline and _process_alive(child_pid):
            time.sleep(0.05)
        if _process_alive(child_pid):
            os.kill(child_pid, signal.SIGKILL)
            self.fail(f"background child {child_pid} survived the timeout")


def _process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


class CanRunTests(unittest.TestCase):
    def test_non_executable_file_is_not_runnable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "noexec.sh"
            script.write_text("#!/bin/sh\necho hi\n", encoding="utf-8")
            script.chmod(0o644)
            result = run_verification_command(str(script))

        self.assertEqual(result["exit_code"], 126)
        self.assertFalse(result["can_run"])
        self.assertIn("exit 126", result["error"])

    def test_shell_syntax_error_is_not_runnable(self) -> None:
        result = run_verification_command("echo (")

        self.assertEqual(result["exit_code"], 2)
        self.assertFalse(result["can_run"])
        self.assertIn("syntax error", result["error"].lower())

    def test_plain_exit_2_is_still_runnable(self) -> None:
        result = run_verification_command("exit 2")

        self.assertEqual(result["exit_code"], 2)
        self.assertTrue(result["can_run"])


class ExtractionTests(unittest.TestCase):
    def test_backticked_span_without_a_check_keyword_is_not_a_command(self) -> None:
        commands = extract_verification_commands(
            "Read `./inspect-only.sh` and review its contents"
        )
        self.assertEqual(commands, [])

    def test_backticked_and_bare_commands_in_one_clause_both_survive(self) -> None:
        commands = extract_verification_commands(
            "`pytest -q` exits 0; ruff check . passes"
        )
        self.assertEqual(commands, ["pytest -q", "ruff check ."])

    def test_prefix_commands_are_not_collapsed(self) -> None:
        commands = extract_verification_commands(
            "pytest -q exits 0; pytest -q tests/auth passes"
        )
        self.assertEqual(commands, ["pytest -q", "pytest -q tests/auth"])

    def test_show_clause_after_a_command_adds_nothing(self) -> None:
        commands = extract_verification_commands(
            "`pytest -q` exits 0; show its summary line"
        )
        self.assertEqual(commands, ["pytest -q"])

    def test_template_style_show_clause_keeps_the_command(self) -> None:
        commands = extract_verification_commands(
            "`npm test` exits 0; show all authentication tests passing"
        )
        self.assertEqual(commands, ["npm test"])

    def test_angle_bracket_placeholder_is_not_a_command(self) -> None:
        self.assertEqual(extract_verification_commands("`<TEST COMMAND>` exits 0"), [])

    def test_brace_and_dollar_placeholders_are_not_commands(self) -> None:
        self.assertEqual(
            extract_verification_commands("`{TEST_COMMAND}` exits 0; `$TEST_COMMAND` passes"),
            [],
        )

    def test_backticked_span_after_proven_by_running_is_a_command(self) -> None:
        commands = extract_verification_commands(
            "All tests pass, proven by running `pytest -q`"
        )
        self.assertEqual(commands, ["pytest -q"])

    def test_backticked_list_after_proven_by_running_is_all_commands(self) -> None:
        commands = extract_verification_commands(
            "Checks pass, proven by running `pytest -q`, `ruff check .`, and `mypy .`"
        )
        self.assertEqual(commands, ["pytest -q", "ruff check .", "mypy ."])

    def test_exact_duplicates_are_collapsed(self) -> None:
        commands = extract_verification_commands(
            "`pytest -q` exits 0; `pytest -q` passes; pytest -q shows no failures"
        )
        self.assertEqual(commands, ["pytest -q"])

    def test_prose_before_a_gated_span_is_not_a_command(self) -> None:
        cases = {
            "Lint clean: `ruff check .` passes": ["ruff check ."],
            "Tests: `pytest -q` exits 0; show the summary line": ["pytest -q"],
            "Run `pytest -q` exits 0": ["pytest -q"],
        }
        for verification, expected in cases.items():
            with self.subTest(verification=verification):
                self.assertEqual(extract_verification_commands(verification), expected)

    def test_prose_before_a_gated_placeholder_span_is_not_a_command(self) -> None:
        self.assertEqual(
            extract_verification_commands("Lint clean: `[LINT COMMAND]` passes"), []
        )


class EmptyInputTests(unittest.TestCase):
    def test_markdown_without_goals_exits_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            no_goal = Path(tmp) / "notes.md"
            no_goal.write_text("# Notes\n\nNothing to launch here.\n", encoding="utf-8")
            result = run_benchmark(str(no_goal))

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("No goals found.", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_missing_input_is_still_exit_1(self) -> None:
        result = run_benchmark("no-such-file-for-benchmark.md")

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("input not found", result.stderr)


class PlaceholderTests(unittest.TestCase):
    PLACEHOLDER_GOAL = "/goal Check. Done only when `[TEST COMMAND]` exits 0."

    def test_strict_turns_placeholders_into_issues(self) -> None:
        result = run_benchmark(self.PLACEHOLDER_GOAL, "--strict")

        self.assertEqual(result.returncode, 1, result.stderr)
        [analysis] = json.loads(result.stdout)["analyses"]
        self.assertIn("Unresolved placeholder: [TEST COMMAND]", analysis["issues"])

    def test_placeholders_are_listed_but_not_issues_without_strict(self) -> None:
        result = run_benchmark(self.PLACEHOLDER_GOAL)

        self.assertEqual(result.returncode, 0, result.stderr)
        [analysis] = json.loads(result.stdout)["analyses"]
        self.assertEqual(analysis["unresolved_placeholders"], ["[TEST COMMAND]"])
        self.assertEqual(analysis["issues"], [])

    def test_every_placeholder_style_is_found_in_verification_and_done_when(self) -> None:
        goal = parse_goal(
            "Check.\n"
            "Done when:\n"
            "- Coverage reaches [TARGET]% on {module}.\n"
            "- The [x] checkbox and a < b stay untouched.\n"
            "Verification:\n"
            "- `<TEST COMMAND>` exits 0.\n"
            "- `$LINTER` passes and `[TEST COMMAND]` exits 0."
        )
        analysis = analyze_goal(goal)

        self.assertEqual(
            analysis["unresolved_placeholders"],
            ["<TEST COMMAND>", "$LINTER", "[TEST COMMAND]", "[TARGET]", "{module}"],
        )
        self.assertEqual(analysis["issues"], [])

        strict = analyze_goal(goal, strict=True)
        self.assertEqual(
            strict["issues"],
            [
                "Unresolved placeholder: <TEST COMMAND>",
                "Unresolved placeholder: $LINTER",
                "Unresolved placeholder: [TEST COMMAND]",
                "Unresolved placeholder: [TARGET]",
                "Unresolved placeholder: {module}",
            ],
        )

    def test_goal_without_placeholders_has_an_empty_list(self) -> None:
        analysis = analyze_goal(
            parse_goal("Check. Done only when `pytest -q` exits 0, proven by running it.")
        )
        self.assertEqual(analysis["unresolved_placeholders"], [])


class AnalysisTests(unittest.TestCase):
    def test_single_word_commands_are_not_flagged_by_shape(self) -> None:
        analysis = analyze_goal(
            parse_goal("Check. Done only when true exits 0, proven by running true.")
        )

        self.assertEqual(analysis["verification_commands"], ["true"])
        self.assertEqual(analysis["issues"], [])


    def test_legacy_turn_limit_gets_a_native_budget_suggestion(self) -> None:
        analysis = analyze_goal(
            parse_goal(
                "Fix the leak. Done only when pytest -q exits 0, proven by running it. "
                "Stop after 12 turns."
            )
        )

        self.assertTrue(analysis["has_turn_limit"])
        self.assertIn(
            "Legacy 'Stop after N turns' clause found; prefer a native budget in Codex "
            "or an 'or stop after N turns' clause in Claude Code",
            analysis["suggestions"],
        )
        self.assertEqual(analysis["issues"], [])

    def test_goal_without_turn_limit_gets_no_budget_suggestion(self) -> None:
        analysis = analyze_goal(
            parse_goal("Fix the leak. Done only when pytest -q exits 0, proven by running it.")
        )

        self.assertFalse(analysis["has_turn_limit"])
        self.assertFalse(any("Stop after N turns" in s for s in analysis["suggestions"]))


    def test_parser_diagnostics_become_issues(self) -> None:
        goal = parse_goal("Check. Done only when `pytest -q` exits 0, proven by running it.")
        goal["diagnostics"] = ["Objective is longer than one sentence", "Second note"]

        analysis = analyze_goal(goal)

        self.assertIn("Objective is longer than one sentence", analysis["issues"])
        self.assertIn("Second note", analysis["issues"])

    def test_goal_without_diagnostics_key_still_analyzes(self) -> None:
        goal = parse_goal("Check. Done only when `pytest -q` exits 0, proven by running it.")
        goal.pop("diagnostics", None)

        self.assertEqual(analyze_goal(goal)["issues"], [])


if __name__ == "__main__":
    unittest.main()
