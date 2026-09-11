from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from benchmark_goals import analyze_goal, extract_verification_commands  # noqa: E402
from goal_parsing import extract_goals_from_text, parse_goal  # noqa: E402


class GoalParsingTests(unittest.TestCase):
    def test_canonical_multiline_goal(self) -> None:
        text = """/goal Fix password-reset expiry.

Done when:
- Expired tokens are rejected.
- Valid tokens still work.

Constraints:
- Do not change the database schema.

Verification:
- `pytest -q tests/test_auth.py` exits 0.
- Review the final diff.
"""
        [goal] = extract_goals_from_text(text)

        self.assertEqual(goal["objective"], "Fix password-reset expiry.")
        self.assertEqual(
            goal["done_when"],
            ["Expired tokens are rejected", "Valid tokens still work"],
        )
        self.assertEqual(goal["constraints"], ["Do not change the database schema"])
        self.assertIn("pytest -q tests/test_auth.py", goal["verification"])
        self.assertIsNone(goal["turn_limit"])
        self.assertEqual(goal["character_count"], len(goal["goal"]))

    def test_legacy_one_line_goal_remains_compatible(self) -> None:
        [goal] = extract_goals_from_text(
            "/goal Fix the leak. Done only when pytest -q exits 0, proven by "
            "running it. Constraints: Do not change the API. Stop after 12 turns."
        )

        self.assertEqual(goal["objective"], "Fix the leak.")
        self.assertEqual(goal["turn_limit"], 12)
        self.assertTrue(goal["done_when"])
        self.assertEqual(goal["constraints"], ["Do not change the API"])

    def test_current_and_legacy_subcommands_are_not_goals(self) -> None:
        commands = (
            "edit New objective",
            "pause",
            "resume",
            "clear",
            "stop",
            "off",
            "reset",
            "none",
            "cancel",
            "--resume",
        )
        text = "\n".join(f"/goal {command}" for command in commands)
        self.assertEqual(extract_goals_from_text(text), [])

    def test_capitalized_lifecycle_verbs_remain_valid_objectives(self) -> None:
        text = "\n".join(
            (
                "/goal Edit the README",
                "/goal Pause background jobs during deployment",
                "/goal Resume interrupted uploads",
                "/goal Clear stale cache entries",
                "/goal Stop retry loops",
            )
        )

        self.assertEqual(
            [goal["objective"] for goal in extract_goals_from_text(text)],
            [
                "Edit the README",
                "Pause background jobs during deployment",
                "Resume interrupted uploads",
                "Clear stale cache entries",
                "Stop retry loops",
            ],
        )

    def test_manual_review_is_valid_verification(self) -> None:
        goal = parse_goal(
            "Prepare the decision memo.\n"
            "Done when:\n- Cost, risk, and migration are compared.\n"
            "Verification:\n- Every recommendation cites a supplied source."
        )
        analysis = analyze_goal(goal)

        self.assertEqual(analysis["issues"], [])
        self.assertEqual(analysis["verification_commands"], [])

    def test_command_verification_is_extracted(self) -> None:
        commands = extract_verification_commands(
            "`pytest -q` exits 0; `ruff check .` passes; review the final diff"
        )
        self.assertEqual(commands, ["pytest -q", "ruff check ."])

    def test_template_placeholders_are_not_commands(self) -> None:
        commands = extract_verification_commands(
            "`[TEST COMMAND]` exits 0; `[LINTER]` passes"
        )
        self.assertEqual(commands, [])

    def test_character_limit_boundary(self) -> None:
        at_limit = parse_goal("x" * 4000)
        over_limit = parse_goal("x" * 4001)

        self.assertTrue(analyze_goal(at_limit)["within_character_limit"])
        over_analysis = analyze_goal(over_limit)
        self.assertFalse(over_analysis["within_character_limit"])
        self.assertIn(
            "Goal body exceeds the 4,000-character authoring limit",
            over_analysis["issues"],
        )

    def test_missing_completion_criteria_is_an_issue(self) -> None:
        analysis = analyze_goal(
            parse_goal("Fix the bug.\nVerification:\n- `pytest -q` exits 0.")
        )
        self.assertIn("Missing measurable completion criteria", analysis["issues"])


class GoalOrchestratorLaunchRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (
            ROOT / "skills" / "goal-orchestrator" / "SKILL.md"
        ).read_text(encoding="utf-8")
        # These are documentation tripwires; runtime behavior is checked by the
        # separate trace acceptance cases, not inferred from these strings.
        for runtime in ("codex", "claude"):
            cls.skill += (ROOT / "skills" / "goal-orchestrator" / "references" / f"{runtime}.md").read_text(encoding="utf-8")
        cls.metadata = (
            ROOT / "skills" / "goal-orchestrator" / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")
        cls.guide = (ROOT / "GUIDE.md").read_text(encoding="utf-8")
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_current_task_is_the_default_launch_destination(self) -> None:
        self.assertIn(
            '**Current task:** Default when the user says only "start," "run," or '
            '"execute."',
            self.skill,
        )
        self.assertIn("call `create_goal` here", self.guide)

    def test_new_task_launch_requires_an_explicit_request(self) -> None:
        self.assertIn(
            "Use only when the user explicitly asks for a new, separate, parallel, "
            "or background task",
            self.skill,
        )
        self.assertIn("Do not call `create_goal` in the parent task", self.skill)
        self.assertIn("complete brief and canonical Goal text", self.skill)
        self.assertIn("launch it here or in a new task on explicit request", self.metadata)
        self.assertIn(
            "Use $goal-orchestrator to launch this as a new Codex task.",
            self.readme,
        )

    def test_destination_prompt_prevents_recursive_task_creation(self) -> None:
        guard = (
            "You are already the destination task created by Goal Orchestrator.\n"
            "   Launch the native Goal in this task. Do not create another task."
        )
        self.assertIn(guard, self.skill)
        self.assertIn(guard, self.guide)

    def test_active_parent_goal_blocks_only_the_current_task(self) -> None:
        self.assertIn(
            "it blocks another current-task Goal but does not block a Goal in a "
            "separately created task",
            self.skill,
        )
        self.assertIn(
            "An active Goal blocks another Goal in the same task, not a Goal in a "
            "separate task.",
            self.readme,
        )

    def test_git_projects_default_to_a_worktree_without_starting_state(self) -> None:
        for phrase in (
            "Call `list_projects` before `create_thread`",
            "Check the project's `isGitRepository` value",
            "For a Git project, create the task in a Codex worktree by default",
            "Omit worktree `startingState` by default",
            "only when the user explicitly requests that starting state",
        ):
            self.assertIn(phrase, self.skill)

    def test_pending_task_id_is_not_treated_as_a_real_thread(self) -> None:
        self.assertIn(
            "A returned `clientThreadId` is temporary and must not be passed to "
            "tools that require `threadId`",
            self.skill,
        )
        self.assertIn("using `list_threads` to resolve pending creation", self.skill)
        self.assertIn("Use `wait_threads` or `read_thread`", self.skill)
        self.assertIn("report whether the Goal is active", self.skill)

    def test_unavailable_task_creation_never_falls_back_silently(self) -> None:
        self.assertIn(
            "do not silently launch in the current task",
            self.skill,
        )
        self.assertIn("Return a copy-ready new-task prompt", self.skill)
        self.assertIn("Never change destinations silently", self.guide)

    def test_claude_code_launch_is_a_handover(self) -> None:
        for phrase in (
            "Launch is a handover, never an action",
            "Never report a goal as created, active, or launched",
            "or stop after N turns",
            "Permission mode is unchanged by a goal",
        ):
            self.assertIn(phrase, self.skill)

    def test_launch_record_and_run_ending_facts_are_documented(self) -> None:
        for phrase in (
            "report a launch record",
            "Goal state:",
            "A run can end without a verdict",
            "resets its turn count",
        ):
            self.assertIn(phrase, self.skill)


if __name__ == "__main__":
    unittest.main()
