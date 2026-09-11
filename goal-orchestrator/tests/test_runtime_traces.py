from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from grade_runtime_trace import grade_trace

CASES = {case["id"]: case for case in json.loads((ROOT / "evals/runtime_cases.json").read_text())}


def call(tool, arguments=None, target="current"):
    return {"tool": tool, "arguments": arguments or {}, "target": target}


def current_trace(case_id="current-launch"):
    case = CASES[case_id]
    args = {"objective": case["objective"]}
    if case.get("requested_budget"):
        args["token_budget"] = case["requested_budget"]
    return {"case_id": case_id, "calls": [call("get_goal"), call("create_goal", args), call("get_goal")],
            "final": {"state": "active", "destination": "current", "budget": case.get("requested_budget")}}


def new_trace(case_id="new-task-activated"):
    case = CASES[case_id]
    prompt = (case["objective"] + "\nYou are already the destination task created by Goal Orchestrator. "
              "Launch the native Goal in this task. Do not create another task. "
              "Check get_goal, then create_goal, then get_goal to confirm activation.")
    return {"case_id": case_id, "calls": [call("get_goal"), call("list_projects"),
            call("create_thread", {"target": {"type": "project", "projectId": "project-1", "environment": {"type": "worktree"}}, "prompt": prompt}),
            call("list_threads"), call("read_thread", {"threadId": "child-1"})],
            "final": {"state": "active", "destination": "child-1"}}


class RuntimeTraceTests(unittest.TestCase):
    def assert_passes(self, trace):
        self.assertEqual(grade_trace(CASES[trace["case_id"]], trace), [])

    def assert_fails(self, trace, fragment):
        issues = grade_trace(CASES[trace["case_id"]], trace)
        self.assertTrue(any(fragment in issue for issue in issues), issues)

    def test_current_launch_requires_preflight_and_matching_activation(self):
        trace = current_trace()
        self.assert_passes(trace)
        trace["calls"].pop(0)
        self.assert_fails(trace, "prior state inspection")
        trace = current_trace()
        trace["calls"].pop()
        self.assert_fails(trace, "post-launch evidence")

    def test_draft_and_plan_requests_do_not_mutate_state(self):
        for case_id in ("draft-only", "plan-mode"):
            self.assert_passes({"case_id": case_id, "calls": [], "final": {"state": "draft", "destination": "current"}})
            self.assert_fails(current_trace(case_id), "draft/Plan mode")

    def test_current_goal_conflict_is_preserved(self):
        trace = {"case_id": "active-conflict", "calls": [call("get_goal")], "final": {"state": "conflict", "destination": "current"}}
        self.assert_passes(trace)
        trace["calls"].append(call("create_goal", {"objective": CASES["active-conflict"]["objective"]}))
        self.assert_fails(trace, "unfinished goal")

    def test_unavailable_tools_produce_handover(self):
        trace = {"case_id": "tools-unavailable", "calls": [], "final": {"state": "handover", "destination": "current"}}
        self.assert_passes(trace)
        trace["final"]["state"] = "active"
        self.assert_fails(trace, "post-launch evidence")

    def test_failed_creation_cannot_claim_activation(self):
        trace = current_trace("creation-failed")
        trace["calls"].pop()
        trace["final"]["state"] = "failed"
        self.assert_passes(trace)
        trace["final"]["state"] = "active"
        self.assert_fails(trace, "post-launch evidence")

    def test_activation_of_another_objective_is_rejected(self):
        trace = current_trace("activation-mismatch")
        self.assert_fails(trace, "post-launch evidence")
        trace["final"]["state"] = "conflict"
        self.assert_passes(trace)

    def test_requested_budget_is_passed_and_unrequested_budget_omitted(self):
        self.assert_passes(current_trace("budget-requested"))
        trace = current_trace("budget-requested")
        trace["calls"][1]["arguments"].pop("token_budget")
        self.assert_fails(trace, "budget must be exactly requested")
        trace = current_trace()
        trace["calls"][1]["arguments"]["token_budget"] = 10000
        self.assert_fails(trace, "budget must be exactly requested")

    def test_new_task_uses_matching_project_and_real_destination(self):
        trace = new_trace()
        self.assert_passes(trace)
        trace["calls"][2]["arguments"]["target"]["projectId"] = "guessed-id"
        self.assert_fails(trace, "matching project")
        trace = new_trace()
        trace["calls"][4]["arguments"]["threadId"] = "pending-1"
        self.assert_fails(trace, "real destination ID")
        trace = new_trace()
        trace["final"]["destination"] = "current"
        self.assert_fails(trace, "requested destination")

    def test_new_task_cannot_launch_in_parent_or_block_on_parent_goal(self):
        trace = new_trace()
        trace["calls"].append(call("create_goal", {"objective": CASES[trace["case_id"]]["objective"]}))
        # The fixture has no parent creation capability; guessed calls fail closed.
        self.assert_fails(trace, "unavailable tool")
        trace = new_trace()
        trace["calls"] = [call("get_goal")]
        trace["final"]["state"] = "conflict"
        self.assert_fails(trace, "must not block")

    def test_pending_task_setup_is_not_activation(self):
        trace = new_trace("new-task-pending")
        trace["calls"] = trace["calls"][:3]
        trace["final"] = {"state": "pending", "destination": "new"}
        self.assert_passes(trace)
        trace["final"]["state"] = "active"
        self.assert_fails(trace, "post-launch evidence")

    def test_failed_task_setup_does_not_change_destination(self):
        trace = new_trace("new-task-failed")
        trace["calls"] = trace["calls"][:3]
        trace["final"] = {"state": "failed", "destination": "new"}
        self.assert_passes(trace)

    def test_recursion_guard_and_default_worktree_are_required(self):
        trace = new_trace()
        trace["calls"][2]["arguments"]["prompt"] = CASES[trace["case_id"]]["objective"]
        self.assert_fails(trace, "recursion guard")
        trace = new_trace()
        trace["calls"][2]["arguments"]["target"]["environment"] = {"type": "local"}
        self.assert_fails(trace, "incorrect project environment")
        self.assert_passes(current_trace("destination-no-recursion"))

    def test_model_cannot_forge_a_tool_result(self):
        trace = current_trace()
        trace["calls"][0]["result"] = None
        self.assert_fails(trace, "must not supply its own tool results")

    def test_every_acceptance_criterion_needs_evidence_before_completion(self):
        trace = {"case_id": "completion-evidence", "calls": [call("get_goal"), call("run_check", {"id": "suite"}),
                 call("review_artifact", {"id": "artifact"}), call("update_goal", {"status": "complete"})],
                 "final": {"state": "complete", "destination": "current"}}
        self.assert_passes(trace)
        skipped = copy.deepcopy(trace)
        skipped["calls"].pop(2)
        self.assert_fails(skipped, "decisive evidence for every criterion")
        failed = copy.deepcopy(trace)
        failed["case_id"] = "completion-failed-check"
        self.assert_fails(failed, "decisive evidence for every criterion")

    def test_evidence_calls_must_request_the_matching_record(self):
        for index in (1, 2):
            for arguments in ({}, {"id": "WRONG"}, {"id": "suite" if index == 1 else "artifact", "other": True}):
                with self.subTest(index=index, arguments=arguments):
                    trace = {"case_id": "completion-evidence", "calls": [
                        call("get_goal"), call("run_check", {"id": "suite"}),
                        call("review_artifact", {"id": "artifact"}),
                        call("update_goal", {"status": "complete"})],
                        "final": {"state": "complete", "destination": "current"}}
                    trace["calls"][index]["arguments"] = arguments
                    self.assert_fails(trace, "evidence call arguments")
                    self.assert_fails(trace, "decisive evidence for every criterion")

    def test_user_command_hosts_handover_without_native_calls(self):
        for case_id in ("claude-handover", "claude-budget", "kimi-handover"):
            trace = {"case_id": case_id, "calls": [], "final": {"state": "handover", "destination": "current"}}
            self.assert_passes(trace)
            trace["final"]["state"] = "active"
            self.assert_fails(trace, "user-command host")

    def test_kimi_next_does_not_queue_a_draft_when_no_goal_is_active(self):
        trace = {"case_id": "kimi-next-without-active-goal", "calls": [], "final": {"state": "draft", "destination": "current"}}
        self.assert_passes(trace)
        trace["final"]["state"] = "active"
        self.assert_fails(trace, "planning must be reported as unlaunched")

    def test_all_acceptance_cases_have_a_user_request_and_fixed_results(self):
        self.assertEqual(len(CASES), 18)
        for case in CASES.values():
            self.assertTrue(case["user_request"])
            self.assertIsInstance(case["tools"], dict)


if __name__ == "__main__":
    unittest.main()
