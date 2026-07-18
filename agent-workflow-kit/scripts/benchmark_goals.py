#!/usr/bin/env python3
"""Test goal conditions against sample tasks to verify they are checkable."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from goal_parsing import collect_goals

# Vague references that are not runnable commands.
NON_COMMANDS = {"the command", "the check", "the appropriate check", "it"}


def extract_verification_command(verification: str | None) -> str | None:
    """Extract the runnable command from a verification clause.

    Handles the kit's canonical style ('npm test exits 0 ... proven by running
    npm test ...') as well as backticked commands.
    """
    if not verification:
        return None

    match = re.search(r"`([^`]+)`", verification)
    if match:
        return match.group(1).strip()

    match = re.search(r"^(?:running\s+)?(.+?)\s+exits 0", verification, re.IGNORECASE)
    if not match:
        match = re.search(
            r"proven by running\s+(.+?)(?:\s+and\s+|,|$)", verification, re.IGNORECASE
        )
    if match:
        command = match.group(1).strip()
        if command.lower() not in NON_COMMANDS:
            return command

    return None


def test_verification_command(command: str, cwd: Path | None = None) -> dict[str, Any]:
    """Test if a verification command can run and what it returns."""
    result = {
        "command": command,
        "can_run": False,
        "exit_code": None,
        "output": None,
        "error": None,
    }

    try:
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd,
        )
        result["exit_code"] = process.returncode
        result["output"] = process.stdout
        result["error"] = process.stderr
        # POSIX shells report a missing command as exit code 127.
        if process.returncode == 127:
            result["error"] = f"command not found (exit 127): {process.stderr.strip()}"
        else:
            result["can_run"] = True
    except subprocess.TimeoutExpired:
        result["error"] = "Command timed out after 30 seconds"
    except OSError as exc:
        result["error"] = str(exc)

    return result


def analyze_goal(goal: dict[str, Any]) -> dict[str, Any]:
    """Analyze a parsed goal for quality and checkability."""
    analysis = {
        **goal,
        "has_objective": bool(goal["objective"]),
        "has_verification": goal["verification"] is not None,
        "has_constraints": bool(goal["constraints"]),
        "has_turn_limit": goal["turn_limit"] is not None,
        "verification_command": extract_verification_command(goal["verification"]),
        "estimated_complexity": estimate_complexity(goal),
        "issues": [],
        "suggestions": [],
    }

    # Check for issues
    if not analysis["has_objective"]:
        analysis["issues"].append("Missing clear objective")

    if not analysis["has_verification"]:
        analysis["issues"].append("Missing verification method")

    if not analysis["has_constraints"]:
        analysis["suggestions"].append("Consider adding constraints to fence dangerous actions")

    if not analysis["has_turn_limit"]:
        analysis["suggestions"].append("Consider adding a turn limit to prevent token drain")

    if analysis["verification_command"]:
        # Check if command looks executable
        cmd = analysis["verification_command"]
        if not any(char in cmd for char in [" ", "-", "/"]):
            analysis["issues"].append(f"Verification command '{cmd}' may not be a valid command")

    return analysis


def estimate_complexity(goal: dict[str, Any]) -> str:
    """Estimate the complexity of a goal based on its content."""
    complexity_score = min(len(goal["goal"]) // 100, 5)
    complexity_score += min(len(goal["constraints"]), 3)
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
        help="Actually run verification commands (use with caution)",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        help="Working directory for running commands",
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

    analyses = [analyze_goal(goal) for goal in goals]

    # Test commands if requested, running each unique command once.
    if args.test_commands:
        results: dict[str, dict[str, Any]] = {}
        for analysis in analyses:
            command = analysis.get("verification_command")
            if not command:
                continue
            if command not in results:
                print(f"Running verification command: {command}", file=sys.stderr)
                results[command] = test_verification_command(command, args.cwd)
            analysis["command_test"] = results[command]

    # Generate report
    total_goals = len(analyses)
    goals_with_issues = sum(1 for a in analyses if a["issues"])
    goals_with_verification = sum(1 for a in analyses if a["has_verification"])

    report = {
        "summary": {
            "total_goals": total_goals,
            "goals_with_issues": goals_with_issues,
            "goals_with_verification": goals_with_verification,
            "complexity_breakdown": {
                "low": sum(1 for a in analyses if a["estimated_complexity"] == "low"),
                "medium": sum(1 for a in analyses if a["estimated_complexity"] == "medium"),
                "high": sum(1 for a in analyses if a["estimated_complexity"] == "high"),
            },
        },
        "analyses": analyses,
    }

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
