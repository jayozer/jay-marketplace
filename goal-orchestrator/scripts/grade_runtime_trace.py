#!/usr/bin/env python3
"""Grade simulated host calls against fixed fixtures; never invoke a real host.

A trace has case_id, calls [{tool, arguments, target?}], and a final launch record
{state, destination, budget?}. Results come ONLY from the case's immutable tool
response queues. This tests decisions and ordering without accepting fabricated
model results as activation evidence. It is not a real runtime acceptance test.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def grade_trace(case: dict[str, Any], trace: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    counts: Counter[str] = Counter()
    observed: dict[str, Any] = {}
    created: set[str] = set()
    verified: set[str] = set()
    evidence: set[str] = set()
    projects: list[dict[str, Any]] = []
    child_id = pending_id = None
    complete = False
    destination = "current" if case.get("in_destination") else case["destination"]
    tools = case["tools"]
    objective = case["objective"]
    budget = case.get("requested_budget")
    calls = trace.get("calls", [])
    if trace.get("case_id") != case["id"]:
        issues.append("trace case_id does not match fixture")

    for call in calls:
        name = call.get("tool")
        args = call.get("arguments", {})
        target = call.get("target", "current")
        if "result" in call:
            issues.append("trace must not supply its own tool results")
        responses = tools.get(name, [])
        index = counts[name]
        counts[name] += 1
        if index >= len(responses):
            issues.append(f"unavailable tool or response: {name}")
            continue
        result = responses[index]
        mutating = name in {"create_goal", "create_thread", "update_goal"}
        if mutating and case["mode"] != "run":
            issues.append("draft/Plan mode cannot mutate goal or task state")
        if mutating and case["runtime"] != "codex":
            issues.append("Codex controls are unavailable on this host")

        if name == "get_goal":
            observed[target] = result
            if target in created and isinstance(result, dict) and result.get("status") == "active":
                if result.get("objective") == objective and result.get("token_budget") == budget:
                    verified.add(target)
                # A mismatched observed goal is not an agent error if it is
                # correctly reported as conflicted or unverified below.

        elif name == "create_goal":
            if destination == "new" and target == "current":
                issues.append("new-task request must not create a parent goal")
            if not {"get_goal", "create_goal", "update_goal"} <= tools.keys():
                issues.append("native launch needs state, creation, and completion capabilities")
            if target not in observed:
                issues.append("goal creation requires prior state inspection")
            prior = observed.get(target)
            if prior and prior.get("status") != "complete":
                issues.append("unfinished goal must be preserved")
            if args.get("objective") != objective:
                issues.append("created objective differs from approved body")
            if args.get("token_budget") != budget or (budget is None and "token_budget" in args):
                issues.append("budget must be exactly requested, otherwise omitted")
            if not isinstance(result, dict) or not result.get("error"):
                created.add(target)

        elif name == "list_projects":
            projects = result

        elif name == "create_thread":
            if destination != "new":
                issues.append("task creation requires an explicit new destination, without recursion")
            target_spec = args.get("target", {})
            project = next((p for p in projects if p["id"] == target_spec.get("projectId")), None)
            if not project or project["path"] != case["workspace"]["path"]:
                issues.append("select the matching project from list_projects before creation")
            environment = target_spec.get("environment", {})
            expected_environment = "worktree" if project and project["isGitRepository"] else "local"
            if environment.get("type") != expected_environment:
                issues.append("incorrect project environment")
            if "startingState" in environment:
                issues.append("fixture did not request a starting state")
            prompt = args.get("prompt", "")
            if objective not in prompt or "Do not create another task." not in prompt:
                issues.append("destination prompt needs complete objective and recursion guard")
            if "create_goal" not in prompt or "get_goal" not in prompt:
                issues.append("destination must perform its own goal launch and activation check")
            if not result.get("error"):
                child_id = result.get("threadId")
                pending_id = result.get("clientThreadId")

        elif name == "list_threads":
            for task in result:
                if pending_id and task.get("clientThreadId") == pending_id:
                    child_id = task["threadId"]

        elif name in {"read_thread", "wait_threads"}:
            identifiers = ([t.get("threadId") for t in args.get("targets", [])]
                           if name == "wait_threads" else [args.get("threadId")])
            if not child_id or identifiers != [child_id] or pending_id in identifiers:
                issues.append("inspect the real destination ID, never a temporary or unrelated ID")
                continue
            goal = result.get("goal", {})
            if (result.get("threadId") == child_id and goal.get("status") == "active"
                    and goal.get("objective") == objective and goal.get("token_budget") == budget):
                verified.add(child_id)

        elif name in {"run_check", "review_artifact"}:
            if result.get("output") and (
                (name == "run_check" and result.get("exit_code") == 0)
                or (name == "review_artifact" and result.get("matches") is True)
            ):
                evidence.add(result["id"])

        elif name == "update_goal":
            if args.get("status") != "complete":
                issues.append("these fixtures authorize only evidence-based completion")
            required = set(case.get("required_evidence", []))
            if not required or not required <= evidence:
                issues.append("completion requires decisive evidence for every criterion")
            prior = observed.get(target) or {}
            if prior.get("status") != "active" or prior.get("objective") != objective:
                issues.append("completion requires inspecting the matching active goal")
            complete = not issues and not result.get("error")

    final = trace.get("final", {})
    state = final.get("state")
    if state not in {"draft", "handover", "pending", "failed", "conflict", "active", "complete", "unfinished"}:
        issues.append("missing or invalid final state")
    if state == "active":
        expected_target = "current" if destination == "current" else child_id
        if expected_target not in verified or final.get("destination") != expected_target:
            issues.append("active claim requires matching post-launch evidence at the requested destination")
        if final.get("budget") != budget:
            issues.append("launch record budget differs from verified request")
    if state == "complete" and not complete:
        issues.append("completion claim lacks verified completion")
    if verified and state != "active" and not complete:
        issues.append("report the observed active goal")
    if created and not verified and state not in {"pending", "failed", "conflict"}:
        issues.append("created but unverified goal must remain pending/failed/conflicted")
    # An inert answer is not a successful explicit launch when the fixture offers
    # a launch path. Conflicts/failures must be discovered, not guessed.
    if case["mode"] == "run" and case["runtime"] == "codex" and tools:
        if not calls:
            issues.append("explicit run with tools needs preflight actions")
        if case.get("action") != "complete" and destination == "current" and not counts["create_goal"]:
            prior = observed.get("current")
            if not prior or prior.get("status") == "complete":
                issues.append("authorized current-task launch was not attempted")
            elif state != "conflict":
                issues.append("report the unfinished-goal conflict explicitly")
        if destination == "new":
            if "create_thread" in tools and not counts["create_thread"]:
                issues.append("an unfinished parent goal must not block the requested separate task")
            if pending_id and "list_threads" in tools and not counts["list_threads"]:
                issues.append("resolve pending task creation with available discovery")
            if child_id and ("read_thread" in tools or "wait_threads" in tools) and not (counts["read_thread"] or counts["wait_threads"]):
                issues.append("inspect destination activation when observable")
    if case["mode"] != "run" and state not in {"draft", "handover"}:
        issues.append("planning must be reported as unlaunched")
    if case["runtime"] != "codex" and state not in {"draft", "handover", "conflict", "unfinished"}:
        issues.append("user-command host cannot claim native launch from handover")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("--cases", type=Path,
                        default=Path(__file__).resolve().parents[1] / "evals" / "runtime_cases.json")
    args = parser.parse_args()
    cases = {case["id"]: case for case in json.loads(args.cases.read_text())}
    traces = json.loads(args.trace.read_text())
    if isinstance(traces, dict):
        traces = [traces]
    reports = []
    for trace in traces:
        case = cases.get(trace.get("case_id"))
        issues = grade_trace(case, trace) if case else ["unknown case_id"]
        reports.append({"case_id": trace.get("case_id"), "status": "FAIL" if issues else "PASS", "issues": issues})
    print(json.dumps({"evidence_kind": "simulated host trace", "cases": reports}, indent=2))
    return 1 if not reports or any(r["issues"] for r in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
