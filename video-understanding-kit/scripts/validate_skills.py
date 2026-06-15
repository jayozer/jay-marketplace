#!/usr/bin/env python3
"""Validate Claude Code skill frontmatter in this kit."""

from __future__ import annotations

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


def validate_skill(skill_dir: Path) -> list[str]:
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

    return errors


def main() -> int:
    if not SKILLS_DIR.exists():
        print(f"Missing skills directory: {SKILLS_DIR}", file=sys.stderr)
        return 1

    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    errors = [error for skill_dir in skill_dirs for error in validate_skill(skill_dir)]

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
