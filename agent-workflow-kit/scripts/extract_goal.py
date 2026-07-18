#!/usr/bin/env python3
"""Extract successful goal patterns from conversation history or goal files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from goal_parsing import collect_goals


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract goal patterns from text or files"
    )
    parser.add_argument(
        "input",
        nargs="+",
        help="File paths, directories, or literal '/goal ...' text to extract goals from",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file for extracted goals (JSON format)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format",
    )
    args = parser.parse_args()

    goals, errors = collect_goals(args.input)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1

    if not goals:
        print("No goals found.", file=sys.stderr)
        return 1

    if args.format == "json":
        output = json.dumps(goals, indent=2)
    else:
        # Markdown format
        output = "# Extracted Goals\n\n"
        for i, goal in enumerate(goals, 1):
            output += f"## Goal {i}\n\n"
            output += f"**Objective:** {goal['objective']}\n\n"
            if goal.get('verification'):
                output += f"**Verification:** {goal['verification']}\n\n"
            if goal.get('constraints'):
                output += "**Constraints:**\n"
                for constraint in goal['constraints']:
                    output += f"- {constraint}\n"
                output += "\n"
            if goal.get('turn_limit'):
                output += f"**Turn Limit:** {goal['turn_limit']}\n\n"
            output += "---\n\n"

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Extracted {len(goals)} goal(s) to {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
