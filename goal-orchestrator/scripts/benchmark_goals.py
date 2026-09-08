#!/usr/bin/env python3
"""Test goal conditions against sample tasks to verify they are checkable."""

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

from goal_parsing import collect_goals

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
    r"\[[A-Z][A-Z0-9 /_-]*\]|<[^<>\s][^<>]*>|\$?\{[^{}\s][^{}]*\}|\$[A-Z][A-Z0-9_]*\b"
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
    """Extract the runnable commands from a verification clause.

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
    command: str, cwd: Path | None = None, timeout: int = 30
) -> dict[str, Any]:
    """Test if a verification command can run and what it returns."""
    result = {
        "command": command,
        "can_run": False,
        "exit_code": None,
        "output": None,
        "error": None,
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
            cwd=cwd,
            start_new_session=True,
        ) as process:
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                _kill_process_group(process)
                result["error"] = f"Command timed out after {timeout} seconds"
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
    """List template placeholders left in the verification and completion criteria."""
    texts = [goal["verification"] or "", *goal["done_when"]]
    tokens = [token for text in texts for token in UNRESOLVED_PLACEHOLDER.findall(text)]
    return list(dict.fromkeys(tokens))


def analyze_goal(goal: dict[str, Any], *, strict: bool = False) -> dict[str, Any]:
    """Analyze a parsed goal for quality and checkability.

    With ``strict``, unresolved placeholders are issues; otherwise they are
    only listed under ``unresolved_placeholders``.
    """
    analysis = {
        **goal,
        "has_objective": bool(goal["objective"]),
        "has_done_when": bool(goal["done_when"]),
        "has_verification": goal["verification"] is not None,
        "has_constraints": bool(goal["constraints"]),
        "has_turn_limit": goal["turn_limit"] is not None,
        "within_character_limit": goal["character_count"] <= 4000,
        "verification_commands": extract_verification_commands(goal["verification"]),
        "unresolved_placeholders": find_unresolved_placeholders(goal),
        "estimated_complexity": estimate_complexity(goal),
        "issues": [],
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
        analysis["issues"].append("Goal body exceeds Codex's 4,000-character limit")

    # The parser may attach diagnostics (structural problems it noticed).
    analysis["issues"].extend(goal.get("diagnostics", []))

    if strict:
        for token in analysis["unresolved_placeholders"]:
            analysis["issues"].append(f"Unresolved placeholder: {token}")

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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark goal conditions for quality and checkability"
    )
    parser.add_argument(
        "input",
        nargs="+",
        help="File paths, directories, or literal '/goal ...' text to benchmark",
    )
    parser.add_argument(
        "--test-commands",
        action="store_true",
        help="Run verification commands; requires --yes to execute (use with caution)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Actually execute under --test-commands; without it the command "
        "list is printed and nothing runs",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        help="Working directory for running commands",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        metavar="SECONDS",
        help="Seconds each verification command may run under --test-commands (default 30)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat unresolved [...], <...>, {...}, and $NAME placeholders in "
        "verification and completion criteria as issues",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file for benchmark results (JSON format)",
    )
    args = parser.parse_args()

    goals, errors = collect_goals(args.input)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    if not goals:
        # Exit 2 so "nothing to benchmark" is distinct from "goals have issues".
        print("No goals found.", file=sys.stderr)
        return 2

    analyses = [analyze_goal(goal, strict=args.strict) for goal in goals]

    # Test commands if requested, running each unique command once.
    execution: str | None = None
    if args.test_commands:
        # Map each unique command to the source that first named it.
        planned: dict[str, str] = {}
        for analysis in analyses:
            source = analysis.get("source_file") or analysis.get("source", "command_line")
            for command in analysis["verification_commands"]:
                planned.setdefault(command, source)

        if not args.yes:
            execution = "skipped: pass --yes to run"
            print(
                "Verification commands that would run (pass --yes to run them):",
                file=sys.stderr,
            )
            for command, source in planned.items():
                print(f"{source}: {command}", file=sys.stderr)
            for analysis in analyses:
                analysis["command_tests"] = []
        else:
            results: dict[str, dict[str, Any]] = {}
            for command, source in planned.items():
                print(
                    f"Running verification command from {source}: {command}",
                    file=sys.stderr,
                )
                results[command] = test_verification_command(
                    command, args.cwd, args.timeout
                )
            for analysis in analyses:
                analysis["command_tests"] = [
                    results[command] for command in analysis["verification_commands"]
                ]
                # A verification command that cannot run cannot prove the goal.
                for command_test in analysis["command_tests"]:
                    command = command_test["command"]
                    if not command_test["can_run"]:
                        analysis["issues"].append(
                            f"Verification command '{command}' could not run: "
                            f"{command_test['error']}"
                        )
                    elif command_test["exit_code"] != 0:
                        analysis["issues"].append(
                            f"Verification command '{command}' exited "
                            f"{command_test['exit_code']}"
                        )

    # Generate report
    total_goals = len(analyses)
    goals_with_issues = sum(1 for a in analyses if a["issues"])
    goals_with_verification = sum(1 for a in analyses if a["has_verification"])
    goals_with_done_when = sum(1 for a in analyses if a["has_done_when"])
    goals_within_character_limit = sum(
        1 for a in analyses if a["within_character_limit"]
    )

    report = {
        "summary": {
            "total_goals": total_goals,
            "goals_with_issues": goals_with_issues,
            "goals_with_verification": goals_with_verification,
            "goals_with_done_when": goals_with_done_when,
            "goals_within_character_limit": goals_within_character_limit,
            "complexity_breakdown": {
                "low": sum(1 for a in analyses if a["estimated_complexity"] == "low"),
                "medium": sum(1 for a in analyses if a["estimated_complexity"] == "medium"),
                "high": sum(1 for a in analyses if a["estimated_complexity"] == "high"),
            },
        },
    }
    if execution is not None:
        report["execution"] = execution
    report["analyses"] = analyses

    if args.output:
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Benchmark results saved to {args.output}")
    else:
        print(json.dumps(report, indent=2))

    # Exit with error if any goals have issues
    if goals_with_issues > 0:
        print(f"\n{goals_with_issues} goal(s) have issues.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
