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

    If blocked:
    - <what to do instead of looping when a step cannot proceed>

The ``If blocked:`` section is optional. Bullets may use ``- ``, ``* ``,
``+ ``, or ``N. `` markers, and a blank line between bullets or before the
next section heading does not end the block. Legacy one-line goals and
optional ``Stop after N turns`` clauses remain readable for
backward-compatible extraction.

Every parsed goal carries a ``diagnostics`` list. It is empty when the block
parsed cleanly and otherwise names the line where the parser stopped or
guessed, so a truncated block is never silent.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


CURRENT_GOAL_SUBCOMMANDS = {"edit", "pause", "resume", "clear"}
LEGACY_GOAL_SUBCOMMANDS = {"stop", "off", "reset", "none", "cancel", "--resume"}
GOAL_SUBCOMMANDS = CURRENT_GOAL_SUBCOMMANDS | LEGACY_GOAL_SUBCOMMANDS
SECTION_HEADINGS = {"done when:", "constraints:", "verification:", "if blocked:"}
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


# Bullet markers accepted inside sections: "- ", "* ", "+ ", and "N. ".
BULLET_RE = re.compile(r"^(?:[-*+] |\d+\. )")


def _is_bullet(line: str) -> bool:
    return bool(BULLET_RE.match(line))


def _strip_bullet(line: str) -> str:
    return BULLET_RE.sub("", line, count=1)


def _is_section_like(line: str) -> bool:
    """True for a section name dressed as markdown ('### Done when:', '**Done when:**').

    A plain ``Done when:`` line is a real heading and returns False here.
    """
    lower = line.lower()
    if lower in SECTION_HEADINGS:
        return False
    core = re.sub(r"^#+\s*", "", lower)
    core = re.sub(r"[*_`]+", "", core).strip().rstrip(":")
    return f"{core}:" in SECTION_HEADINGS


def _is_plain_prose(line: str) -> bool:
    """True for a non-empty line that carries no goal structure of its own."""
    lower = line.lower()
    return bool(line) and not (
        line.startswith(("```", "#", "/goal"))
        or _is_bullet(line)
        or lower in SECTION_HEADINGS
        or lower.startswith(LEGACY_PREFIXES)
        or _is_section_like(line)
    )


def _next_nonempty_index(lines: list[str], start: int) -> int | None:
    for index in range(start, len(lines)):
        if lines[index].strip():
            return index
    return None


def _line_ref(number: int, source: str | None) -> str:
    """Describe a 1-based line number, naming the file when one is known."""
    return f"line {number}" if source is None else f"line {number} of {source}"


def find_goal_block_records(text: str, source: str | None = None) -> list[dict[str, Any]]:
    """Find canonical and legacy goal blocks without treating subcommands as goals.

    Each record carries the normalized ``block`` text and a ``diagnostics``
    list that names any line where the parser had to stop early.
    """
    records: list[dict[str, Any]] = []
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
        diagnostics: list[str] = []
        current_section: str | None = None
        start_index = i
        end_index = i  # index of the last line absorbed into the block
        i += 1

        def ended(reason: str) -> str:
            return f"Goal block ended at {_line_ref(end_index + 1, source)}: {reason}"

        while i < len(lines):
            line = lines[i].strip()
            lower = line.lower()

            if _is_section_like(line):
                diagnostics.append(
                    ended(
                        f"section heading at {_line_ref(i + 1, source)} is not in "
                        f"the plain 'Done when:' form: '{line}'"
                    )
                )
                break

            if line.startswith(("```", "#", "/goal")):
                break

            if not line:
                next_index = _next_nonempty_index(lines, i + 1)
                following = lines[next_index].strip() if next_index is not None else ""
                if following.lower() in SECTION_HEADINGS or (
                    current_section and _is_bullet(following)
                ):
                    i += 1
                    continue
                if _is_section_like(following):
                    diagnostics.append(
                        ended(
                            f"section heading at {_line_ref(next_index + 1, source)} "
                            f"is not in the plain 'Done when:' form: '{following}'"
                        )
                    )
                elif _is_bullet(following):
                    diagnostics.append(
                        ended(
                            f"bullet at {_line_ref(next_index + 1, source)} is "
                            f"outside any section: '{following}'"
                        )
                    )
                break

            if lower in SECTION_HEADINGS:
                current_section = lower[:-1]
                block.append(line)
                end_index = i
                i += 1
                continue

            if current_section and _is_bullet(line):
                block.append(line)
                end_index = i
                i += 1
                continue

            if lower.startswith(LEGACY_PREFIXES):
                block.append(line)
                end_index = i
                i += 1
                continue

            # Allow a wrapped line inside a structured section, but do not absorb
            # unrelated prose that follows a complete goal block.
            if current_section and _is_bullet(block[-1]):
                block[-1] = f"{block[-1]} {line}"
                end_index = i
                i += 1
                continue

            if current_section is None and len(block) == 1 and _is_plain_prose(line):
                # A wrapped objective is absorbed only when a section heading
                # follows before the next blank line. Otherwise diagnose it
                # rather than guess whether the prose belongs to the goal.
                j = i
                while j < len(lines) and _is_plain_prose(lines[j].strip()):
                    j += 1
                if j < len(lines) and lines[j].strip().lower() in SECTION_HEADINGS:
                    block[0] = " ".join([block[0], *(lines[k].strip() for k in range(i, j))])
                    end_index = j - 1
                    i = j
                    continue
                diagnostics.append(
                    f"Possible wrapped objective at {_line_ref(i + 1, source)}: '{line}'"
                )
                break

            if current_section:
                diagnostics.append(
                    f"Goal block ended at {_line_ref(i + 1, source)}: "
                    f"unrecognized line '{line}'"
                )
            elif _is_bullet(line):
                # A bullet with no section open is the blank-line case above
                # without the blank line; it must be named the same way.
                diagnostics.append(
                    ended(
                        f"bullet at {_line_ref(i + 1, source)} is "
                        f"outside any section: '{line}'"
                    )
                )
            break

        # The raw body keeps blank lines and original spacing; only the
        # "/goal " prefix on the first line is dropped.
        first_raw = lines[start_index].lstrip()[len("/goal ") :]
        raw = "\n".join([first_raw, *lines[start_index + 1 : end_index + 1]])
        records.append(
            {
                "block": "\n".join(block),
                "diagnostics": diagnostics,
                "source_span": {"start_line": start_index + 1, "end_line": end_index + 1},
                "raw_character_count": len(raw),
            }
        )

    return records


def find_goal_blocks(text: str) -> list[str]:
    """Return only the block text of every goal found in ``text``."""
    return [record["block"] for record in find_goal_block_records(text)]


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
        if collecting and _is_bullet(stripped):
            items.append(_strip_bullet(stripped).strip().rstrip(" ."))
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
        "if_blocked": _section_items(block, "if blocked"),
        "character_count": len(block),
        # Defaults for callers that pass a bare block; extract_goals_from_text
        # replaces them with the values measured against the original input.
        "raw_character_count": len(block),
        "source_span": {"start_line": 1, "end_line": len(block.splitlines()) or 1},
        "diagnostics": [],
    }


def extract_goals_from_text(text: str, source: str | None = None) -> list[dict[str, Any]]:
    goals: list[dict[str, Any]] = []
    for record in find_goal_block_records(text, source):
        goal = parse_goal(record["block"])
        goal["raw_character_count"] = record["raw_character_count"]
        goal["source_span"] = dict(record["source_span"])
        goal["diagnostics"] = list(record["diagnostics"])
        goals.append(goal)
    return goals


def extract_goals_from_file(
    file_path: Path, errors: list[str] | None = None
) -> list[dict[str, Any]]:
    """Parse one markdown file; an undecodable file yields no goals and an error.

    A UTF-8 byte-order mark is tolerated. When ``errors`` is given, a decode
    failure is appended there instead of raised so a directory scan continues.
    """
    try:
        text = file_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        message = (
            f"could not decode {file_path} as UTF-8 "
            f"({exc.reason} at byte {exc.start}); file skipped"
        )
        if errors is None:
            raise ValueError(message) from exc
        errors.append(message)
        return []

    goals = extract_goals_from_text(text, source=str(file_path))
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
            goals.extend(extract_goals_from_file(path, errors))
        elif path.is_dir():
            for md_file in iter_markdown_files(path):
                goals.extend(extract_goals_from_file(md_file, errors))
        elif item.lstrip().startswith("/goal "):
            for goal in extract_goals_from_text(item):
                goal["source"] = "command_line"
                goals.append(goal)
        else:
            errors.append(f"input not found (and not /goal text): {item}")
    return goals, errors
