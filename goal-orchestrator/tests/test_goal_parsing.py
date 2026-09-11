from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from goal_parsing import collect_goals, extract_goals_from_text, parse_goal  # noqa: E402

EXTRACT_GOAL = ROOT / "scripts" / "extract_goal.py"

CANONICAL_GOAL = """/goal Fix password-reset expiry.

Done when:
- Expired tokens are rejected.
- Valid tokens still work.

Constraints:
- Do not change the database schema.

Verification:
- `pytest -q tests/test_auth.py` exits 0.
- Review the final diff.
"""


class LooseListTests(unittest.TestCase):
    def test_blank_line_between_verification_bullets_keeps_both(self) -> None:
        text = """/goal Fix password-reset expiry.

Done when:
- Expired tokens are rejected.

Verification:
- `pytest -q tests/test_auth.py` exits 0.

- Review the final diff.
"""
        [goal] = extract_goals_from_text(text)

        self.assertEqual(goal["done_when"], ["Expired tokens are rejected"])
        self.assertEqual(
            goal["verification"],
            "`pytest -q tests/test_auth.py` exits 0; Review the final diff",
        )
        self.assertEqual(goal["diagnostics"], [])

    def test_numbered_and_plus_bullets_are_items(self) -> None:
        text = """/goal Ship the release.

Done when:
1. The changelog is updated.
2. The tag is pushed.

Constraints:
+ Do not bump the major version.

Verification:
- `make release-check` exits 0.
"""
        [goal] = extract_goals_from_text(text)

        self.assertEqual(
            goal["done_when"], ["The changelog is updated", "The tag is pushed"]
        )
        self.assertEqual(goal["constraints"], ["Do not bump the major version"])
        self.assertEqual(goal["verification"], "`make release-check` exits 0")
        self.assertEqual(goal["diagnostics"], [])


class IfBlockedSectionTests(unittest.TestCase):
    def test_if_blocked_items_parse_into_if_blocked(self) -> None:
        text = """/goal Migrate the billing table.

Done when:
- The migration applies cleanly.

Constraints:
- Do not drop columns.

Verification:
- `make migrate-check` exits 0.

If blocked:
- Stop and report the blocking migration step.
- Do not retry destructive steps.
"""
        [goal] = extract_goals_from_text(text)

        self.assertEqual(
            goal["if_blocked"],
            [
                "Stop and report the blocking migration step",
                "Do not retry destructive steps",
            ],
        )
        self.assertEqual(goal["verification"], "`make migrate-check` exits 0")
        self.assertEqual(goal["diagnostics"], [])

    def test_if_blocked_is_empty_when_absent(self) -> None:
        [goal] = extract_goals_from_text(
            "/goal Fix it.\nDone when:\n- It works.\nVerification:\n- `make check` exits 0.\n"
        )
        self.assertEqual(goal["if_blocked"], [])


class DiagnosticsTests(unittest.TestCase):
    def test_indented_continuation_after_blank_is_not_silently_lost(self) -> None:
        text = '/goal Check both cases.\nDone when:\n- The behavior is correct.\nVerification:\n- Review the output.\n\n  Also inspect the second artifact.\n'
        [goal] = extract_goals_from_text(text)
        self.assertIn('line 7', goal['diagnostics'][0])
        self.assertEqual(goal['source_excerpt'], text)

    def test_command_record_cannot_be_normalized_across_lines(self) -> None:
        text = '/goal Check output.\nDone when:\n- The command passes.\nVerification:\n- Command: {"command":"printf one\ntwo", "cwd":"."}\n'
        [goal] = extract_goals_from_text(text)
        self.assertIn('Command record must occupy one line', goal['diagnostics'][0])

    def test_unrecognized_line_in_open_section_is_diagnosed_not_silent(self) -> None:
        text = """/goal Fix it.

Done when:
this line is not a bullet
- It works.

Verification:
- `make check` exits 0.
"""
        [goal] = extract_goals_from_text(text)

        # The parser stops at the stray line, but it must say so and name it.
        self.assertEqual(goal["done_when"], [])
        self.assertEqual(
            goal["diagnostics"],
            ["Goal block ended at line 4: unrecognized line 'this line is not a bullet'"],
        )

    def test_markdown_heading_styled_section_after_blank_line_is_diagnosed(self) -> None:
        text = """/goal Fix it.

### Done when:
- It works.
"""
        [goal] = extract_goals_from_text(text)

        self.assertEqual(goal["done_when"], [])
        self.assertEqual(len(goal["diagnostics"]), 1)
        self.assertIn("line 3", goal["diagnostics"][0])
        self.assertIn("### Done when:", goal["diagnostics"][0])

    def test_bold_heading_styled_section_inside_open_section_is_diagnosed(self) -> None:
        text = """/goal Fix it.
Done when:
- It works.
**Constraints:**
- Do not touch the schema.
"""
        [goal] = extract_goals_from_text(text)

        # The bold heading must not be glued onto the previous bullet.
        self.assertEqual(goal["done_when"], ["It works"])
        self.assertEqual(goal["constraints"], [])
        self.assertEqual(len(goal["diagnostics"]), 1)
        self.assertIn("line 4", goal["diagnostics"][0])
        self.assertIn("**Constraints:**", goal["diagnostics"][0])

    def test_bullet_after_blank_line_outside_any_section_is_diagnosed(self) -> None:
        text = """/goal Fix it.

- It works.
- Nothing else changes.
"""
        [goal] = extract_goals_from_text(text)

        self.assertEqual(goal["done_when"], [])
        self.assertEqual(len(goal["diagnostics"]), 1)
        self.assertIn("line 3", goal["diagnostics"][0])
        self.assertIn("- It works.", goal["diagnostics"][0])

    def test_bullet_directly_after_objective_outside_any_section_is_diagnosed(self) -> None:
        # The blank-line case above, minus the blank line: the block must not
        # end silently just because the stray bullet follows immediately.
        text = """/goal Fix it.
- It works.
- Nothing else changes.
"""
        [goal] = extract_goals_from_text(text)

        self.assertEqual(goal["done_when"], [])
        self.assertEqual(goal["source_span"], {"start_line": 1, "end_line": 1})
        self.assertEqual(
            goal["diagnostics"],
            ["Goal block ended at line 1: bullet at line 2 is outside any section: '- It works.'"],
        )

    def test_bullet_before_a_later_heading_does_not_lose_the_section_silently(self) -> None:
        text = """/goal Fix the bug that
- It works.
Done when:
- It works.
"""
        [goal] = extract_goals_from_text(text)

        # The 'Done when:' section is still cut off, but the cut is named.
        self.assertEqual(goal["done_when"], [])
        self.assertEqual(len(goal["diagnostics"]), 1)
        self.assertIn("bullet at line 2 is outside any section", goal["diagnostics"][0])
        self.assertIn("- It works.", goal["diagnostics"][0])

    def test_file_diagnostics_name_the_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "goal.md"
            path.write_text("/goal Fix it.\nDone when:\nnot a bullet\n", encoding="utf-8")
            goals, errors = collect_goals([str(path)])

        self.assertEqual(errors, [])
        self.assertEqual(
            goals[0]["diagnostics"],
            [f"Goal block ended at line 3 of {path}: unrecognized line 'not a bullet'"],
        )


class CompatibilityTests(unittest.TestCase):
    def test_canonical_block_parses_as_before(self) -> None:
        [goal] = extract_goals_from_text(CANONICAL_GOAL)

        self.assertEqual(goal["objective"], "Fix password-reset expiry.")
        self.assertEqual(
            goal["done_when"],
            ["Expired tokens are rejected", "Valid tokens still work"],
        )
        self.assertEqual(goal["constraints"], ["Do not change the database schema"])
        self.assertEqual(
            goal["verification"],
            "`pytest -q tests/test_auth.py` exits 0; Review the final diff",
        )
        self.assertIsNone(goal["turn_limit"])
        self.assertEqual(goal["character_count"], len(goal["goal"]))
        self.assertEqual(goal["if_blocked"], [])
        self.assertEqual(goal["diagnostics"], [])
        self.assertEqual(goal["source_span"], {"start_line": 1, "end_line": 12})

    def test_legacy_one_liner_has_no_diagnostics(self) -> None:
        [goal] = extract_goals_from_text(
            "/goal Fix the leak. Done only when pytest -q exits 0, proven by "
            "running it. Constraints: Do not change the API. Stop after 12 turns."
        )

        self.assertEqual(goal["turn_limit"], 12)
        self.assertEqual(goal["diagnostics"], [])
        self.assertEqual(goal["if_blocked"], [])

    def test_parse_goal_on_a_bare_block_carries_the_new_fields(self) -> None:
        goal = parse_goal("Fix it.\nDone when:\n- It works.")

        self.assertEqual(goal["diagnostics"], [])
        self.assertEqual(goal["if_blocked"], [])
        self.assertEqual(goal["raw_character_count"], goal["character_count"])
        self.assertEqual(goal["source_span"], {"start_line": 1, "end_line": 3})


class WrappedObjectiveTests(unittest.TestCase):
    def test_wrapped_objective_is_absorbed_when_a_heading_follows(self) -> None:
        text = """/goal Fix the password-reset expiry bug that
lets expired tokens through.
Done when:
- Expired tokens are rejected.
Verification:
- `pytest -q tests/test_auth.py` exits 0.
"""
        [goal] = extract_goals_from_text(text)

        self.assertEqual(
            goal["objective"],
            "Fix the password-reset expiry bug that lets expired tokens through.",
        )
        self.assertTrue(
            goal["goal"].startswith(
                "Fix the password-reset expiry bug that lets expired tokens through.\n"
                "Done when:"
            )
        )
        self.assertEqual(goal["done_when"], ["Expired tokens are rejected"])
        self.assertEqual(goal["diagnostics"], [])

    def test_wrapped_objective_before_a_blank_then_heading_is_preserved(self) -> None:
        text = """/goal Fix the password-reset expiry bug that
lets expired tokens through.

Done when:
- Expired tokens are rejected.
"""
        [goal] = extract_goals_from_text(text)

        self.assertEqual(goal["objective"], "Fix the password-reset expiry bug that lets expired tokens through.")
        self.assertEqual(goal["done_when"], ["Expired tokens are rejected"])
        self.assertEqual(goal["diagnostics"], [])

    def test_wrapped_objective_without_sections_has_a_location_diagnostic(self) -> None:
        [goal] = extract_goals_from_text("/goal Fix the bug that\nlets expired tokens through.\n")
        self.assertIn("line 2", goal["diagnostics"][0])


class SourceSpanTests(unittest.TestCase):
    def test_raw_goal_preserves_crlf_and_original_indentation(self) -> None:
        text = '/goal Fix it.\r\n\r\nDone when:\r\n  - It works.\r\nVerification:\r\n- Command: {"command":"true","cwd":"."}\r\n'
        [goal] = extract_goals_from_text(text)
        self.assertEqual(goal["raw_goal"], text[len("/goal "):].rstrip("\r\n"))
        self.assertEqual(goal["raw_character_count"], len(goal["raw_goal"]))

    def test_rejected_source_is_retained_with_a_span(self) -> None:
        text = '/goal Fix it.\nDone when:\nnot a bullet\nVerification:\n- Review the diff.\n'
        [goal] = extract_goals_from_text(text)
        self.assertTrue(goal["diagnostics"])
        self.assertEqual(goal["source_excerpt"], text)
        self.assertEqual(goal["source_excerpt_span"], {"start_line": 1, "end_line": 5})

    def test_multisentence_objective_is_not_shortened(self) -> None:
        [goal] = extract_goals_from_text('/goal Fix expiry. Preserve valid tokens.\nDone when:\n- Both cases pass.')
        self.assertEqual(goal["objective"], 'Fix expiry. Preserve valid tokens.')

    def test_raw_character_count_includes_blank_lines_and_span_is_reported(self) -> None:
        body = """/goal Fix it.

Done when:
- It works.

Verification:
- `make check` exits 0."""
        text = body + "\n\nUnrelated prose after the goal.\n"
        [goal] = extract_goals_from_text(text)

        # Old field is unchanged: the normalized block without blank lines.
        self.assertEqual(goal["goal"], "Fix it.\nDone when:\n- It works.\nVerification:\n- `make check` exits 0.")
        self.assertEqual(goal["character_count"], len(goal["goal"]))
        # New field counts the raw lines from /goal through the last absorbed line,
        # blank lines included, without the "/goal " prefix and trailing prose.
        self.assertEqual(goal["raw_character_count"], len(body) - len("/goal "))
        self.assertEqual(goal["raw_goal"], body[len("/goal "):])
        self.assertEqual(goal["raw_character_count"], goal["character_count"] + 2)
        self.assertEqual(goal["source_span"], {"start_line": 1, "end_line": 7})

    def test_span_uses_input_line_numbers_not_block_line_numbers(self) -> None:
        text = "Intro line.\n\n/goal Fix it.\nDone when:\n- It works.\n"
        [goal] = extract_goals_from_text(text)

        self.assertEqual(goal["source_span"], {"start_line": 3, "end_line": 5})
        self.assertEqual(goal["raw_character_count"], len("Fix it.\nDone when:\n- It works."))


class CollectGoalsTests(unittest.TestCase):
    def test_long_literal_is_not_statted_as_a_filename(self) -> None:
        text = "/goal " + "a" * 5000
        goals, errors = collect_goals([text])
        self.assertEqual(errors, [])
        self.assertEqual(goals[0]["raw_goal"], "a" * 5000)

    def test_kimi_lifecycle_forms_are_filtered_only_for_that_host(self) -> None:
        commands = ["status", "replace New objective", "next Next objective", "next manage",
                    "pause", "resume", "cancel"]
        text = "\n".join("/goal " + command for command in commands)
        self.assertEqual(extract_goals_from_text(text, runtime="kimi"), [])
        goals = extract_goals_from_text("/goal status page is documented", runtime="codex")
        self.assertEqual(goals[0]["objective"], "status page is documented")

    def test_kimi_escaped_subcommand_and_capitalized_verb_are_objectives(self) -> None:
        text = "/goal -- cancel stale work\n/goal Replace deprecated calls"
        goals = extract_goals_from_text(text, runtime="kimi")
        self.assertEqual([g["objective"] for g in goals], ["cancel stale work", "Replace deprecated calls"])

    def test_claude_aliases_are_filtered(self) -> None:
        text = "\n".join("/goal " + command for command in ["clear", "stop", "off", "reset", "none", "cancel"])
        self.assertEqual(extract_goals_from_text(text, runtime="claude"), [])

    def test_mistyped_path_starting_with_goal_is_input_not_found(self) -> None:
        goals, errors = collect_goals(["/goal-orchestrator/nope"])

        self.assertEqual(goals, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("input not found", errors[0])
        self.assertIn("/goal-orchestrator/nope", errors[0])

    def test_literal_goal_text_still_parses(self) -> None:
        goals, errors = collect_goals(
            ["/goal Fix the leak. Done only when pytest -q exits 0, proven by running it."]
        )

        self.assertEqual(errors, [])
        self.assertEqual([goal["source"] for goal in goals], ["command_line"])

    def test_undecodable_file_is_an_error_and_does_not_abort_the_scan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Latin-1 "Café" is not valid UTF-8.
            (root / "bad.md").write_bytes(
                b"/goal Fix Caf\xe9. Done only when x exits 0, proven by running x.\n"
            )
            (root / "good.md").write_text(
                "\ufeff/goal Real goal. Done only when echo ok exits 0, proven by running it.\n",
                encoding="utf-8",
            )

            goals, errors = collect_goals([tmp])

        self.assertEqual([goal["objective"] for goal in goals], ["Real goal."])
        self.assertEqual(len(errors), 1)
        self.assertIn("bad.md", errors[0])
        self.assertIn("UTF-8", errors[0])


class ExtractGoalCliTests(unittest.TestCase):
    def test_runtime_option_filters_kimi_management_commands(self) -> None:
        result = self.run_cli("/goal next queued work", "--runtime", "kimi")
        self.assertEqual(result.returncode, 1)
        self.assertIn("No goals found", result.stderr)

    @staticmethod
    def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run(
            [sys.executable, str(EXTRACT_GOAL), *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def test_clean_input_exits_0_without_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clean.md"
            path.write_text(CANONICAL_GOAL, encoding="utf-8")
            result = self.run_cli(str(path))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("WARNING", result.stderr)
        [goal] = json.loads(result.stdout)
        self.assertEqual(goal["diagnostics"], [])

    def test_diagnostics_are_warnings_on_stderr_and_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "loose.md"
            path.write_text("/goal Fix it.\nDone when:\nnot a bullet\n", encoding="utf-8")
            result = self.run_cli(str(path))

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(
            f"WARNING: Goal block ended at line 3 of {path}: "
            "unrecognized line 'not a bullet'",
            result.stderr,
        )
        # The goal is still emitted; the warning is additive, not a replacement.
        [goal] = json.loads(result.stdout)
        self.assertEqual(goal["objective"], "Fix it.")

    def test_no_goals_still_exits_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prose.md"
            path.write_text("Nothing to see here.\n", encoding="utf-8")
            result = self.run_cli(str(path))

        self.assertEqual(result.returncode, 1)
        self.assertIn("No goals found", result.stderr)

    def test_markdown_output_shows_raw_count_and_if_blocked(self) -> None:
        text = CANONICAL_GOAL + "\nIf blocked:\n- Stop and report the failing step.\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "blocked.md"
            path.write_text(text, encoding="utf-8")
            result = self.run_cli(str(path), "--format", "markdown")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("**Character Count:**", result.stdout)
        self.assertIn("**Raw Character Count:**", result.stdout)
        self.assertIn("**If Blocked:**\n- Stop and report the failing step\n", result.stdout)

    def test_markdown_diagnostics_preserve_the_rejected_tail_for_review(self) -> None:
        text = "/goal Fix it.\nDone when:\nnot a bullet\nVerification:\n- Review `setup.sh`.\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rejected.md"
            path.write_text(text, encoding="utf-8")
            result = self.run_cli(str(path), "--format", "markdown")

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("including rejected text (lines 1-5)", result.stdout)
        self.assertIn(text, result.stdout)
        self.assertIn("**Diagnostics:**", result.stdout)


if __name__ == "__main__":
    unittest.main()
