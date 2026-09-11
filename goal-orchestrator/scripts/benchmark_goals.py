#!/usr/bin/env python3
"""Lint goal templates, check readiness, or run explicitly declared checks.

Prose extraction is a migration aid only. Only Command JSON records execute.
Exit codes: 0 structure/ready/pass (see summary.status), 1 failure, 2 no goals,
3 pending executable or manual evidence. No model or native Goal is invoked.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

from goal_parsing import RUNTIME_SUBCOMMANDS, collect_goals
from verification_checks import parse_checks

# First words that mark a generic reference ("the command", "all checks"),
# not a runnable command.
GENERIC_WORDS = {
    "the", "all", "both", "it", "them", "each", "every",
    "validation", "checks", "commands", "running", "showing",
}


# Openers of unresolved template placeholders: [TEST SUITE], <command>,
# {command}, $COMMAND.
PLACEHOLDER_OPENERS = ("[", "<", "{", "$")

# Clause separators between checks: ', ' ';' ', and' ' and'.
CLAUSE_SEPARATOR = re.compile(r"[,;]\s*(?:and\s+)?|\s+and\s+")
BACKTICKED = re.compile(r"`([^`]+)`")
# A backticked span is a command only when a check keyword follows it ...
CHECK_FOLLOWS = re.compile(r"^\W*(?:exits 0|passes\b|shows\b)", re.IGNORECASE)
# ... or 'proven by running' precedes it, possibly through a list of other
# backticked commands ('proven by running `a`, `b`, and `c`').
PROVEN_BY_RUNNING_PRECEDES = re.compile(
    r"proven by running(?:\W*`[^`]*`\W*(?:and\s+)?)*\W*$", re.IGNORECASE
)
BARE_CHECK = re.compile(
    r"(?:proven by running\s+)?(.+?)\s+(?:exits 0|passes\b|shows\b)", re.IGNORECASE
)
BARE_PROVEN_BY_RUNNING = re.compile(r"proven by running\s+(.+)$", re.IGNORECASE)
# Unresolved template placeholders: [UPPER WORDS], <...>, {...}, ${...}, $NAME.
UNRESOLVED_PLACEHOLDER = re.compile(
    r"\[[A-Z][A-Z0-9 /_-]*\]|<[A-Za-z_][A-Za-z0-9 /_-]*>|"
    r"\$?\{[A-Za-z_][A-Za-z0-9 /_-]*\}|\$[A-Z][A-Z0-9_]*\b"
)


def _plausible_command(candidate: str) -> str | None:
    candidate = re.sub(r"^running\s+", "", candidate.strip(), flags=re.IGNORECASE)
    if not candidate or candidate.split()[0].lower() in GENERIC_WORDS:
        return None
    if candidate.startswith(PLACEHOLDER_OPENERS):
        return None
    return candidate


def _split_clauses(verification: str) -> list[tuple[int, str]]:
    """Split on clause separators outside backticked spans; keep each clause's offset."""
    clauses: list[tuple[int, str]] = []
    start = position = 0
    for index, part in enumerate(re.split(r"(`[^`]*`)", verification)):
        if index % 2 == 0:  # plain text; backticked spans stay whole
            for separator in CLAUSE_SEPARATOR.finditer(part):
                clauses.append((start, verification[start : position + separator.start()]))
                start = position + separator.end()
        position += len(part)
    clauses.append((start, verification[start:]))
    return [(offset, clause) for offset, clause in clauses if clause.strip()]


def extract_verification_commands(verification: str | None) -> list[str]:
    """Suggest legacy commands for migration/lint ONLY; never execute this output.

    Handles the kit's canonical styles, including multi-check clauses like
    'pytest -q exits 0, ruff check . passes, and npm run coverage shows 80%+
    coverage, proven by running all checks ...', as well as backticked commands.

    A backticked span counts as a command only when it is followed by
    'exits 0', 'passes', or 'shows', or preceded by 'proven by running'; other
    backticked spans (file names, paths to read) are ignored. The bare-prose
    text of a clause is examined only when none of its backticked spans passed
    that gate, so '`pytest -q` exits 0; ruff check . passes' yields both
    commands while 'Lint clean: `ruff check .` passes' yields only the command,
    not the 'Lint clean:' label that precedes it.
    """
    if not verification:
        return []

    candidates: list[str] = []
    for offset, clause in _split_clauses(verification):
        gated_span = False
        for match in BACKTICKED.finditer(clause):
            following = clause[match.end() :]
            preceding = verification[: offset + match.start()]
            if CHECK_FOLLOWS.match(following) or PROVEN_BY_RUNNING_PRECEDES.search(preceding):
                gated_span = True
                command = _plausible_command(match.group(1))
                if command:
                    candidates.append(command)
        if gated_span:
            # The check keyword belongs to the span; any prose around it is a
            # label ('Lint clean:', 'Run'), not a second command.
            continue

        prose = BACKTICKED.sub(" ", clause).strip()
        match = BARE_CHECK.match(prose) or BARE_PROVEN_BY_RUNNING.match(prose)
        command = _plausible_command(match.group(1)) if match else None
        if command:
            candidates.append(command)

    return list(dict.fromkeys(candidates))


def test_verification_command(
    command: str, cwd: Path | None = None, timeout: float = 30
) -> dict[str, Any]:
    """Test if a verification command can run and what it returns."""
    result = {
        "command": command,
        "cwd": str((cwd or Path.cwd()).resolve()),
        "can_run": False,
        "exit_code": None,
        "output": None,
        "error": None,
        "timed_out": False,
    }

    try:
        # The command runs as its own session leader so a timeout can kill
        # everything it spawned, and it never inherits the benchmark's stdin.
        with subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            cwd=cwd,
            start_new_session=True,
        ) as process:
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                _kill_process_group(process)
                result["output"], _ = process.communicate()
                result["timed_out"] = True
                result["error"] = f"Command timed out after {timeout:g} seconds"
                return result
    except OSError as exc:
        result["error"] = str(exc)
        return result

    result["exit_code"] = process.returncode
    result["output"] = stdout
    result["error"] = stderr
    stderr = stderr.strip()
    # POSIX shells report a missing command as 127, a command that was
    # found but could not be executed as 126, and a syntax error as 2.
    if process.returncode == 127:
        result["error"] = f"command not found (exit 127): {stderr}"
    elif process.returncode == 126:
        result["error"] = f"command not executable (exit 126): {stderr}"
    elif process.returncode == 2 and re.search(r"syntax error", stderr, re.IGNORECASE):
        result["error"] = f"shell syntax error (exit 2): {stderr}"
    else:
        result["can_run"] = True

    return result


def _kill_process_group(process: subprocess.Popen[str]) -> None:
    """Kill a timed-out command and every process it spawned, then reap it."""
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.kill()
    process.wait()


def find_unresolved_placeholders(goal: dict[str, Any]) -> list[str]:
    """Inspect textual fields, not JSON delimiters used by explicit records."""
    checks, manual, _ = parse_checks(goal.get("verification_items", [goal["verification"] or ""]))
    texts = [*(item["criterion"] for item in manual), *goal["done_when"],
             goal["objective"], *goal["constraints"], *goal.get("decisions_needed", [])]
    for check in checks:
        texts.extend([check["command"], check["cwd"], check.get("evidence", "")])
    tokens = [token for text in texts for token in UNRESOLVED_PLACEHOLDER.findall(text)]
    return list(dict.fromkeys(tokens))


def analyze_goal(goal: dict[str, Any], *, strict: bool = False) -> dict[str, Any]:
    """Analyze a parsed goal for quality and checkability.

    With ``strict``, unresolved placeholders are issues; otherwise they are
    only listed under ``unresolved_placeholders``.
    """
    checks, manual, check_errors = parse_checks(goal.get("verification_items", [goal["verification"] or ""]))
    legacy_commands = list(dict.fromkeys(
        command for item in manual if item["kind"] == "prose"
        for command in extract_verification_commands(item["criterion"])
    ))
    analysis = {
        **goal,
        "has_objective": bool(goal["objective"]),
        "has_done_when": bool(goal["done_when"]),
        "has_verification": goal["verification"] is not None,
        "has_constraints": bool(goal["constraints"]),
        "has_turn_limit": goal["turn_limit"] is not None,
        "within_character_limit": goal.get("raw_character_count", goal["character_count"]) <= 4000,
        "verification_commands": list(dict.fromkeys([*(c["command"] for c in checks), *legacy_commands])),
        "legacy_command_suggestions": legacy_commands,
        "executable_checks": checks,
        "manual_checks": manual,
        "unresolved_placeholders": find_unresolved_placeholders(goal),
        "estimated_complexity": estimate_complexity(goal),
        "issues": list(check_errors),
        "suggestions": [],
    }

    # Check for issues
    if not analysis["has_objective"]:
        analysis["issues"].append("Missing clear objective")

    if not analysis["has_done_when"]:
        analysis["issues"].append("Missing measurable completion criteria")

    if not analysis["has_verification"]:
        analysis["issues"].append("Missing verification method")

    if not analysis["within_character_limit"]:
        analysis["issues"].append("Goal body exceeds the 4,000-character authoring limit")

    # The parser may attach diagnostics (structural problems it noticed).
    analysis["issues"].extend(goal.get("diagnostics", []))

    analysis["structural_issues"] = list(analysis["issues"])
    analysis["readiness_issues"] = []
    if strict:
        for token in analysis["unresolved_placeholders"]:
            analysis["readiness_issues"].append(f"Unresolved placeholder: {token}")
        for decision in goal.get("decisions_needed", []):
            analysis["readiness_issues"].append(f"Unresolved decision: {decision}")
        analysis["issues"].extend(analysis["readiness_issues"])

    if not analysis["has_constraints"]:
        analysis["suggestions"].append("Consider adding constraints to fence dangerous actions")

    if analysis["has_turn_limit"]:
        analysis["suggestions"].append(
            "Legacy 'Stop after N turns' clause found; prefer a native budget in Codex "
            "or an 'or stop after N turns' clause in Claude Code"
        )

    return analysis


def estimate_complexity(goal: dict[str, Any]) -> str:
    """Estimate the complexity of a goal based on its content."""
    complexity_score = min(len(goal["goal"]) // 100, 5)
    complexity_score += min(len(goal["constraints"]), 3)
    complexity_score += min(len(goal["done_when"]), 3)
    if goal["verification"] and " and " in goal["verification"].lower():
        complexity_score += 1

    if complexity_score <= 3:
        return "low"
    elif complexity_score <= 7:
        return "medium"
    else:
        return "high"


def _check_key(check: dict[str, Any]) -> tuple[str, str]:
    return check["command"], check["cwd"]


def _emit_report(report: dict[str, Any], output: Path | None) -> None:
    rendered = json.dumps(report, indent=2) + "\n"
    if output:
        output.write_text(rendered, encoding="utf-8")
        print(f"Benchmark results saved to {output}", file=sys.stderr)
    else:
        print(rendered, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="+", help="Files, directories, or literal /goal text")
    parser.add_argument("--runtime", choices=sorted(RUNTIME_SUBCOMMANDS), default="codex")
    parser.add_argument("--mode", choices=["template", "readiness"],
                        help="Default: template, or readiness with --test-commands")
    parser.add_argument("--strict", action="store_true", help="Alias for --mode readiness")
    parser.add_argument("--allow-empty", action="store_true", help="Allow a scan with no goals")
    parser.add_argument("--test-commands", action="store_true",
                        help="Verify explicit Command JSON records; prose never executes")
    parser.add_argument("--yes", action="store_true", help="Execute the displayed command plan")
    parser.add_argument("--cwd", type=Path,
                        help="Base for relative check cwd values; default: source file directory")
    parser.add_argument("--timeout", type=float, default=30, metavar="SECONDS")
    parser.add_argument("--output", "-o", type=Path)
    args = parser.parse_args()
    if not 0 < args.timeout < float("inf"):
        parser.error("--timeout must be a positive finite number")
    if args.mode == "template" and (args.strict or args.test_commands):
        parser.error("template mode cannot be combined with --strict or --test-commands")
    if args.yes and not args.test_commands:
        parser.error("--yes requires --test-commands")
    mode = args.mode or ("readiness" if args.strict or args.test_commands else "template")

    goals, errors = collect_goals(args.input, runtime=args.runtime)
    if errors or not goals:
        status = "FAIL" if errors else ("EMPTY_ALLOWED" if args.allow_empty else "NO_GOALS")
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        if not goals:
            print("No goals found.", file=sys.stderr)
        _emit_report({"summary": {"status": status, "mode": mode, "total_goals": len(goals),
                                  "goals_with_issues": 0}, "errors": errors, "analyses": []}, args.output)
        return 1 if errors else (0 if args.allow_empty else 2)

    analyses = [analyze_goal(goal, strict=mode == "readiness") for goal in goals]
    planned: dict[tuple[str, str], dict[str, Any]] = {}
    for analysis in analyses:
        source = analysis.get("source_file") or analysis.get("source", "command_line")
        base = args.cwd or (Path(analysis["source_file"]).resolve().parent
                            if analysis.get("source_file") else Path.cwd())
        for check in analysis["executable_checks"]:
            check["declared_cwd"] = check["cwd"]
            check["cwd"] = str((base / check["cwd"]).resolve())
            check["source"] = source
            planned.setdefault(_check_key(check), check)
        analysis["command_tests"] = []

    execution = "not requested"
    if args.test_commands:
        # Print the entire plan before executing its first command. Deduplication
        # is by exact command/resolved-directory pair, never prefixes or source labels.
        print("Explicit verification command plan:", file=sys.stderr, flush=True)
        for check in planned.values():
            print(json.dumps({k: check[k] for k in ("source", "command", "cwd")}),
                  file=sys.stderr, flush=True)
        if any(a["issues"] for a in analyses):
            execution = "blocked: fix structural/readiness issues before execution"
        elif not args.yes:
            execution = "skipped: pass --yes to run"
        else:
            execution = "ran explicit checks" if planned else "no executable checks"
            results = {}
            for key, check in planned.items():
                print(f"Running verification command from {check['source']}: {check['command']}",
                      file=sys.stderr, flush=True)
                results[key] = test_verification_command(check["command"], Path(check["cwd"]), args.timeout)
            for analysis in analyses:
                for check in analysis["executable_checks"]:
                    result = {**results[_check_key(check)], "expected_exit": check["expected_exit"],
                              "check_index": check["check_index"], "source": check["source"]}
                    passed = result["can_run"] and result["exit_code"] == check["expected_exit"]
                    result["status"] = "PASS" if passed else "FAIL"
                    analysis["command_tests"].append(result)
                    if not result["can_run"]:
                        analysis["issues"].append(
                            f"Verification command '{check['command']}' could not run: {result['error']}"
                        )
                    elif not passed:
                        analysis["issues"].append(
                            f"Verification command '{check['command']}' exited {result['exit_code']} "
                            f"(expected {check['expected_exit']})"
                        )

    for analysis in analyses:
        if analysis["issues"]:
            analysis["verification_status"] = "FAIL"
        elif analysis["manual_checks"]:
            analysis["verification_status"] = "MANUAL"
        elif not analysis["command_tests"]:
            analysis["verification_status"] = "PENDING"
        else:
            analysis["verification_status"] = "PASS"
        analysis["readiness_status"] = ("NOT_CHECKED" if mode == "template" else
                                        "FAIL" if analysis["structural_issues"] or analysis["readiness_issues"]
                                        else "READY")

    goals_with_issues = sum(bool(a["issues"]) for a in analyses)
    manual_count = sum(len(a["manual_checks"]) for a in analyses)
    pending_count = sum(len(a["executable_checks"]) - len(a["command_tests"]) for a in analyses)
    if goals_with_issues:
        status, exit_code = "FAIL", 1
    elif not args.test_commands:
        status, exit_code = ("STRUCTURE_ONLY" if mode == "template" else "READY"), 0
    elif manual_count:
        status, exit_code = "MANUAL", 3
    elif pending_count or not planned:
        status, exit_code = "PENDING", 3
    else:
        status, exit_code = "PASS", 0
    report = {
        "summary": {
            "status": status, "mode": mode, "total_goals": len(analyses),
            "goals_with_issues": goals_with_issues,
            "goals_with_verification": sum(a["has_verification"] for a in analyses),
            "goals_with_done_when": sum(a["has_done_when"] for a in analyses),
            "goals_within_character_limit": sum(a["within_character_limit"] for a in analyses),
            "manual_checks": manual_count, "pending_commands": pending_count,
            "failed_commands": sum(t["status"] == "FAIL" for a in analyses for t in a["command_tests"]),
            "complexity_breakdown": {level: sum(a["estimated_complexity"] == level for a in analyses)
                                     for level in ("low", "medium", "high")},
        },
        "execution": execution,
        "execution_plan": list(planned.values()),
        "analyses": analyses,
    }
    _emit_report(report, args.output)
    if goals_with_issues:
        print(f"{goals_with_issues} goal(s) have issues.", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
