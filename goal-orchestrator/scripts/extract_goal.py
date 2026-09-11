#!/usr/bin/env python3
"""Extract successful goal patterns from conversation history or goal files.

Exit codes: 0 when every goal parsed cleanly, 1 when no goals were found or
an input could not be read, and 2 when goals were extracted but the parser
recorded diagnostics (printed to stderr as ``WARNING: <file>: <diagnostic>``).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from goal_parsing import RUNTIME_SUBCOMMANDS, collect_goals


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract goal patterns from text or files"
    )
    parser.add_argument(
        "--runtime", choices=sorted(RUNTIME_SUBCOMMANDS), default="codex",
        help="Host whose lifecycle subcommands should be excluded (default: codex)",
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

    goals, errors = collect_goals(args.input, runtime=args.runtime)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1

    if not goals:
        print("No goals found.", file=sys.stderr)
        return 1

    # A diagnostic means the parser stopped early or guessed; say so loudly
    # but still emit what was extracted.
    warned = False
    for goal in goals:
        source = goal.get("source_file") or goal.get("source", "command_line")
        for diagnostic in goal.get("diagnostics", []):
            if source in diagnostic:
                print(f"WARNING: {diagnostic}", file=sys.stderr)
            else:
                print(f"WARNING: {source}: {diagnostic}", file=sys.stderr)
            warned = True

    if args.format == "json":
        output = json.dumps(goals, indent=2)
    else:
        # Markdown format
        output = "# Extracted Goals\n\n"
        for i, goal in enumerate(goals, 1):
            output += f"## Goal {i}\n\n"
            output += f"**Objective:** {goal['objective']}\n\n"
            if goal.get("done_when"):
                output += "**Done When:**\n"
                for criterion in goal["done_when"]:
                    output += f"- {criterion}\n"
                output += "\n"
            if goal.get('verification'):
                output += f"**Verification:** {goal['verification']}\n\n"
            if goal.get('constraints'):
                output += "**Constraints:**\n"
                for constraint in goal['constraints']:
                    output += f"- {constraint}\n"
                output += "\n"
            if goal.get("if_blocked"):
                output += "**If Blocked:**\n"
                for item in goal["if_blocked"]:
                    output += f"- {item}\n"
                output += "\n"
            if goal.get('turn_limit'):
                output += f"**Legacy Turn Limit:** {goal['turn_limit']}\n\n"
            output += f"**Character Count:** {goal['character_count']}\n\n"
            output += f"**Raw Character Count:** {goal.get('raw_character_count', goal['character_count'])}\n\n"
            span = goal["source_span"]
            output += f"**Source:** {goal.get('source_file', goal.get('source', 'text'))}, lines {span['start_line']}-{span['end_line']}\n\n"
            # Keep rejected source visible too; a diagnostic must not leave a
            # shortened goal looking like the complete original submission.
            if goal.get("diagnostics"):
                original = goal["source_excerpt"]
                excerpt_span = goal["source_excerpt_span"]
                label = f"Source excerpt including rejected text (lines {excerpt_span['start_line']}-{excerpt_span['end_line']})"
            else:
                original = goal["raw_goal"]
                label = "Original goal body"
            # Longer fences also preserve Markdown containing backticks.
            fence = '`' * max(3, max((len(m.group()) + 1 for m in re.finditer(r'`+', original)), default=3))
            output += f"**{label}:**\n\n{fence}text\n{original}\n{fence}\n\n"
            if goal.get("diagnostics"):
                output += "**Diagnostics:**\n"
                for diagnostic in goal["diagnostics"]:
                    output += f"- {diagnostic}\n"
                output += "\n"
            output += "---\n\n"

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Extracted {len(goals)} goal(s) to {args.output}")
    else:
        print(output)

    return 2 if warned else 0


if __name__ == "__main__":
    raise SystemExit(main())
