#!/usr/bin/env python3
"""Shared parsing of /goal blocks, used by extract_goal.py and benchmark_goals.py.

The canonical goal format this parses (see SKILL.md section 3):

    /goal [ONE-SENTENCE OBJECTIVE].
    Done only when [END STATE], proven by [COMMAND] with its output shown in this conversation.
    Constraints: [CONSTRAINT]; [CONSTRAINT].
    Stop after [N] turns if not met and report what remains.

The same fields may also appear on a single line.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

# `/goal <subcommand>` mentions are commands, not goal conditions.
GOAL_SUBCOMMANDS = {"clear", "stop", "off", "reset", "none", "cancel", "--resume"}

# Directories skipped when scanning a directory for markdown files.
PRUNED_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", "vendor"}


def find_goal_blocks(text: str) -> list[str]:
    """Find goal blocks: a line starting with '/goal ' plus its contiguous following lines.

    A block ends at a blank line, a code-fence marker, a heading, or the next /goal line.
    Prose mentions like 'skills/goal-orchestrator' or '/goal clear' are not goal blocks.
    """
    blocks: list[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        rest = stripped[len("/goal "):].strip() if stripped.startswith("/goal ") else ""
        if rest and rest.split()[0] not in GOAL_SUBCOMMANDS:
            block = [rest]
            i += 1
            while i < len(lines):
                line = lines[i].strip()
                if not line or line.startswith(("```", "#", "/goal")):
                    break
                block.append(line)
                i += 1
            blocks.append("\n".join(block))
        else:
            i += 1
    return blocks


def _extract_field(block: str, pattern: str) -> str | None:
    match = re.search(pattern, block, re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    return match.group(1).rstrip(" .")


def _extract_constraints(block: str) -> list[str]:
    text = _extract_field(block, r"Constraints:\s*(.+?)(?=\s+Stop after\s+\d|$)")
    if not text:
        return []
    return [item.strip(" .") for item in text.split(";") if item.strip(" .")]


def _extract_turn_limit(block: str) -> int | None:
    match = re.search(r"Stop after\s+(\d+)\s+turns", block, re.IGNORECASE)
    return int(match.group(1)) if match else None


def parse_goal(block: str) -> dict[str, Any]:
    """Parse one goal block into its four parts."""
    first_line = block.splitlines()[0]
    objective = re.split(r"(?<=[.!?])\s", first_line)[0].strip()
    return {
        "goal": block,
        "objective": objective,
        "verification": _extract_field(
            block, r"Done only when\s+(.+?)(?=\s+Constraints:|\s+Stop after\s+\d|$)"
        ),
        "constraints": _extract_constraints(block),
        "turn_limit": _extract_turn_limit(block),
    }


def extract_goals_from_text(text: str) -> list[dict[str, Any]]:
    return [parse_goal(block) for block in find_goal_blocks(text)]


def extract_goals_from_file(file_path: Path) -> list[dict[str, Any]]:
    goals = extract_goals_from_text(file_path.read_text(encoding="utf-8"))
    for index, goal in enumerate(goals, 1):
        goal["source_file"] = str(file_path)
        goal["index"] = index
    return goals


def iter_markdown_files(root: Path):
    """Yield .md files under root, skipping vendored and hidden directories."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            name for name in dirnames if name not in PRUNED_DIRS and not name.startswith(".")
        )
        for filename in sorted(filenames):
            if filename.endswith(".md"):
                yield Path(dirpath) / filename


def collect_goals(inputs: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    """Resolve CLI inputs (file, directory, or literal '/goal ...' text) into parsed goals.

    A nonexistent path is an error unless the argument itself is /goal text —
    a typo'd filename must not be silently reinterpreted as a goal.
    """
    goals: list[dict[str, Any]] = []
    errors: list[str] = []
    for item in inputs:
        path = Path(item)
        if path.is_file():
            goals.extend(extract_goals_from_file(path))
        elif path.is_dir():
            for md_file in iter_markdown_files(path):
                goals.extend(extract_goals_from_file(md_file))
        elif item.lstrip().startswith("/goal"):
            for goal in extract_goals_from_text(item):
                goal["source"] = "command_line"
                goals.append(goal)
        else:
            errors.append(f"input not found (and not /goal text): {item}")
    return goals, errors
