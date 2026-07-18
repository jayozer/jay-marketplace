#!/usr/bin/env python3
"""Validate Claude Code skill frontmatter and content structure in this kit."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
ALLOWED_FRONTMATTER_KEYS = {
    "allowed-tools",
    "argument-hint",
    "description",
    "license",
    "metadata",
    "name",
    "user-invocable",
}

# Required sections for goal-orchestrator skill
REQUIRED_SECTIONS = {
    "goal-orchestrator": [
        "Platform Adaptation",
        "Fill the Brief",
        "Is This `/goal`-Shaped?",
        "Write the Completion Condition",
        "Pre-Flight",
        "Launch and Walk Away",
        "On Completion",
        "Fallback: Supervised Orchestration",
    ]
}


def validate_skill(skill_dir: Path, check_content: bool = False) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return [f"{skill_dir.relative_to(ROOT)}: missing SKILL.md"]

    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return [f"{skill_md.relative_to(ROOT)}: missing YAML frontmatter"]

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return [f"{skill_md.relative_to(ROOT)}: invalid YAML: {exc}"]

    if not isinstance(frontmatter, dict):
        return [f"{skill_md.relative_to(ROOT)}: frontmatter must be a mapping"]

    unexpected = sorted(set(frontmatter) - ALLOWED_FRONTMATTER_KEYS)
    if unexpected:
        errors.append(
            f"{skill_md.relative_to(ROOT)}: unexpected keys: {', '.join(unexpected)}"
        )

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append(f"{skill_md.relative_to(ROOT)}: missing string name")
    elif not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append(
            f"{skill_md.relative_to(ROOT)}: name must be lowercase hyphen-case"
        )

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{skill_md.relative_to(ROOT)}: missing string description")

    if name and skill_dir.name != name:
        errors.append(
            f"{skill_md.relative_to(ROOT)}: folder name should match skill name"
        )

    # Content validation
    if check_content and name:
        content_errors = validate_skill_content(name, content, skill_md, frontmatter)
        errors.extend(content_errors)

    return errors


def github_slug(heading: str) -> str:
    """Approximate GitHub's heading-to-anchor slug (lowercase, drop punctuation, spaces to hyphens)."""
    text = heading.strip().lower().replace("`", "")
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def validate_skill_content(
    skill_name: str, content: str, skill_md: Path, frontmatter: dict
) -> list[str]:
    """Validate the content structure of a skill file."""
    errors: list[str] = []

    headings = re.findall(r"^#{1,6}\s+(.+?)\s*$", content, re.MULTILINE)
    # Headings may carry a numeric prefix ("## 1. Fill the Brief"); strip it for matching.
    normalized = [re.sub(r"^\d+\.\s*", "", heading) for heading in headings]

    if skill_name in REQUIRED_SECTIONS:
        for section in REQUIRED_SECTIONS[skill_name]:
            if not any(heading.startswith(section) for heading in normalized):
                errors.append(
                    f"{skill_md.relative_to(ROOT)}: missing required section '{section}'"
                )

    # Check internal links against GitHub-style anchors derived from the actual headings.
    slugs: set[str] = set()
    slug_counts: dict[str, int] = {}
    for heading in headings:
        slug = github_slug(heading)
        if slug in slug_counts:
            slug_counts[slug] += 1
            slug = f"{slug}-{slug_counts[slug]}"
        else:
            slug_counts[slug] = 0
        slugs.add(slug)
    for match in re.finditer(r"\[([^\]]+)\]\(#([^)]+)\)", content):
        link_text, anchor = match.groups()
        if anchor not in slugs:
            errors.append(
                f"{skill_md.relative_to(ROOT)}: broken internal link '{link_text}' -> '#{anchor}'"
            )

    allowed_tools = frontmatter.get("allowed-tools")
    if allowed_tools is not None:
        if isinstance(allowed_tools, str):
            valid = bool(allowed_tools.strip())
        elif isinstance(allowed_tools, list):
            valid = bool(allowed_tools) and all(
                isinstance(tool, str) and tool.strip() for tool in allowed_tools
            )
        else:
            valid = False
        if not valid:
            errors.append(
                f"{skill_md.relative_to(ROOT)}: allowed-tools must be a"
                " non-empty string or list of tool names"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Claude Code skills")
    parser.add_argument(
        "--check-content",
        action="store_true",
        help="Validate skill content structure (required sections, links, etc.)",
    )
    args = parser.parse_args()

    if not SKILLS_DIR.exists():
        print(f"Missing skills directory: {SKILLS_DIR}", file=sys.stderr)
        return 1

    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    errors = [
        error
        for skill_dir in skill_dirs
        for error in validate_skill(skill_dir, check_content=args.check_content)
    ]

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} skills.")
    if args.check_content:
        print("Content structure validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
