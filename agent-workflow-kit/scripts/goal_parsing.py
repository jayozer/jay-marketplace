#!/usr/bin/env python3
"""Shared parsing of Codex /goal blocks.

The canonical format is:

    /goal <specific outcome>

    Done when:
    - <measurable acceptance criterion>

    Constraints:
    - <scope, compatibility, approval, or non-goal boundary>

    Verification:
    - <command, observation, or review criterion>

Legacy one-line goals and optional ``Stop after N turns`` clauses remain
readable for backward-compatible extraction.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


CURRENT_GOAL_SUBCOMMANDS = {"edit", "pause", "resume", "clear"}
LEGACY_GOAL_SUBCOMMANDS = {"stop", "off", "reset", "none", "cancel", "--resume"}
GOAL_SUBCOMMANDS = CURRENT_GOAL_SUBCOMMANDS | LEGACY_GOAL_SUBCOMMANDS
SECTION_HEADINGS = {"done when:", "constraints:", "verification:"}
LEGACY_PREFIXES = ("done only when", "constraints:", "verification:", "stop after")

# Directories skipped when scanning a directory for markdown files.
PRUNED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    "vendor",
}


def _next_nonempty(lines: list[str], start: int) -> str:
    for line in lines[start:]:
        if line.strip():
            return line.strip()
    return ""


def find_goal_blocks(text: str) -> list[str]:
    """Find canonical and legacy goal blocks without treating subcommands as goals."""
    blocks: list[str] = []
    lines = text.splitlines()
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()
        rest = stripped[len("/goal ") :].strip() if stripped.startswith("/goal ") else ""
        first_word = rest.split()[0] if rest else ""
        if not rest or first_word in GOAL_SUBCOMMANDS:
            i += 1
            continue

        block = [rest]
        current_section: str | None = None
        i += 1

        while i < len(lines):
            line = lines[i].strip()
            lower = line.lower()

            if line.startswith(("```", "#", "/goal")):
                break

            if not line:
                following = _next_nonempty(lines, i + 1).lower()
                if following in SECTION_HEADINGS:
                    i += 1
                    continue
                break

            if lower in SECTION_HEADINGS:
                current_section = lower[:-1]
                block.append(line)
                i += 1
                continue

            if current_section and line.startswith(("- ", "* ")):
                block.append(line)
                i += 1
                continue

            if lower.startswith(LEGACY_PREFIXES):
                block.append(line)
                i += 1
                continue

            # Allow a wrapped line inside a structured section, but do not absorb
            # unrelated prose that follows a complete goal block.
            if current_section and block[-1].startswith(("- ", "* ")):
                block[-1] = f"{block[-1]} {line}"
                i += 1
                continue

            break

        blocks.append("\n".join(block))

    return blocks


def _extract_field(block: str, pattern: str) -> str | None:
    match = re.search(pattern, block, re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    return match.group(1).rstrip(" .")


def _section_items(block: str, heading: str) -> list[str]:
    lines = block.splitlines()
    items: list[str] = []
    collecting = False

    for line in lines[1:]:
        stripped = line.strip()
        lower = stripped.lower()
        if lower in SECTION_HEADINGS:
            collecting = lower == f"{heading.lower()}:"
            continue
        if collecting and stripped.startswith(("- ", "* ")):
            items.append(stripped[2:].strip().rstrip(" ."))
        elif collecting and stripped:
            items.append(stripped.rstrip(" ."))

    return [item for item in items if item]


def _legacy_done_when(block: str) -> list[str]:
    text = _extract_field(
        block,
        r"Done only when\s+(.+?)(?=,?\s+proven by|\s+Constraints:|\s+Verification:|\s+Stop after\s+\d|$)",
    )
    return [text] if text else []


def _extract_constraints(block: str) -> list[str]:
    structured = _section_items(block, "constraints")
    if structured:
        return structured

    text = _extract_field(
        block,
        r"Constraints:\s*(.+?)(?=\s+Verification:|\s+Stop after\s+\d|$)",
    )
    if not text:
        return []
    return [item.strip(" .") for item in text.split(";") if item.strip(" .")]


def _extract_verification(block: str) -> str | None:
    structured = _section_items(block, "verification")
    if structured:
        return "; ".join(structured)

    explicit = _extract_field(
        block,
        r"Verification:\s*(.+?)(?=\s+Stop after\s+\d|$)",
    )
    if explicit:
        return explicit

    return _extract_field(
        block,
        r"Done only when\s+(.+?)(?=\s+Constraints:|\s+Stop after\s+\d|$)",
    )


def _extract_turn_limit(block: str) -> int | None:
    match = re.search(r"Stop after\s+(\d+)\s+turns", block, re.IGNORECASE)
    return int(match.group(1)) if match else None


def parse_goal(block: str) -> dict[str, Any]:
    """Parse one goal body while preserving the legacy output fields."""
    first_line = block.splitlines()[0]
    objective = re.split(r"(?<=[.!?])\s", first_line)[0].strip()
    done_when = _section_items(block, "done when") or _legacy_done_when(block)

    return {
        "goal": block,
        "objective": objective,
        "verification": _extract_verification(block),
        "constraints": _extract_constraints(block),
        "turn_limit": _extract_turn_limit(block),
        "done_when": done_when,
        "character_count": len(block),
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
            name
            for name in dirnames
            if name not in PRUNED_DIRS and not name.startswith(".")
        )
        for filename in sorted(filenames):
            if filename.endswith(".md"):
                yield Path(dirpath) / filename


def collect_goals(inputs: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    """Resolve file, directory, or literal /goal inputs into parsed goals."""
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
