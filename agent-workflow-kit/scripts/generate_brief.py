#!/usr/bin/env python3
"""Auto-generate a brief from project context (README, package.json, etc.)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None

JS_TECH = {
    "react": "React",
    "next": "React",
    "vue": "Vue",
    "express": "Express",
    "typescript": "TypeScript",
}

PYTHON_TECH = {
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
}


def _first_paragraph_after(content: str, pos: int) -> str:
    """Return the first non-heading paragraph after pos, or ''."""
    paragraph: list[str] = []
    for line in content[pos:].splitlines():
        stripped = line.strip()
        if not stripped:
            if paragraph:
                break
            continue
        if stripped.startswith("#"):
            break
        paragraph.append(stripped)
    return " ".join(paragraph)


def extract_from_readme(readme_path: Path) -> dict[str, Any]:
    """Extract project information from README.md. Only found fields are returned."""
    content = readme_path.read_text(encoding="utf-8")
    info: dict[str, Any] = {}

    # Project name: first heading; description: first paragraph after it.
    name_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if name_match:
        info["name"] = name_match.group(1).strip()
        description = _first_paragraph_after(content, name_match.end())
        if description:
            info["description"] = description

    # Tech stack from common sections
    tech_patterns = [
        r"Tech Stack[:\s]*([^\n]+)",
        r"Technologies[:\s]*([^\n]+)",
        r"Built with[:\s]*([^\n]+)",
        r"Stack[:\s]*([^\n]+)",
    ]
    for pattern in tech_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            tech_items = re.split(r"[,•\-\*]", match.group(1))
            tech_stack = [item.strip() for item in tech_items if item.strip()]
            if tech_stack:
                info["tech_stack"] = tech_stack
            break

    # Features: bullets under a Features/Highlights heading only — the first
    # bullets anywhere in a README are often prerequisites or navigation.
    features_section = re.search(
        r"^#{1,6}[^\n]*(?:features|highlights)[^\n]*\n(.*?)(?=^#{1,6}\s|\Z)",
        content,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    if features_section:
        bullets = re.findall(r"^\s*[-*]\s+(.+)$", features_section.group(1), re.MULTILINE)
        if bullets:
            info["key_features"] = [bullet.strip() for bullet in bullets[:5]]

    return info


def extract_from_package_json(package_json_path: Path) -> dict[str, Any]:
    """Extract project information from package.json. Only found fields are returned."""
    try:
        content = json.loads(package_json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    info: dict[str, Any] = {}
    if content.get("name"):
        info["name"] = content["name"]
    if content.get("description"):
        info["description"] = content["description"]

    deps = list(content.get("dependencies", {})) + list(content.get("devDependencies", {}))
    tech_stack = sorted({JS_TECH[dep] for dep in deps if dep in JS_TECH})
    if tech_stack:
        info["tech_stack"] = tech_stack

    return info


def extract_from_pyproject(pyproject_path: Path) -> dict[str, Any]:
    """Extract project information from pyproject.toml. Only found fields are returned."""
    if tomllib is None:
        return {}
    try:
        data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError):
        return {}

    project = data.get("project", {})
    info: dict[str, Any] = {}
    if project.get("name"):
        info["name"] = project["name"]
    if project.get("description"):
        info["description"] = project["description"]

    tech_stack = []
    for dep in project.get("dependencies", []):
        dep_name = re.match(r"[A-Za-z0-9._\-]+", dep.strip())
        label = PYTHON_TECH.get(dep_name.group(0).lower()) if dep_name else None
        if label and label not in tech_stack:
            tech_stack.append(label)
    if tech_stack:
        info["tech_stack"] = tech_stack

    return info


def _merge_info(target: dict[str, Any], source: dict[str, Any]) -> None:
    """Merge extractor output; tech stacks are unioned, other fields overridden."""
    for key, value in source.items():
        if key == "tech_stack":
            merged = target.get("tech_stack", [])
            merged += [item for item in value if item not in merged]
            target["tech_stack"] = merged
        else:
            target[key] = value


def generate_brief(project_dir: Path, task_description: str = "") -> str:
    """Generate a brief template filled with project context."""
    project_info: dict[str, Any] = {}

    readme_path = project_dir / "README.md"
    package_json_path = project_dir / "package.json"
    pyproject_path = project_dir / "pyproject.toml"

    if readme_path.exists():
        _merge_info(project_info, extract_from_readme(readme_path))

    if package_json_path.exists():
        _merge_info(project_info, extract_from_package_json(package_json_path))

    if pyproject_path.exists():
        _merge_info(project_info, extract_from_pyproject(pyproject_path))

    name = project_info.get("name") or "this project"
    description = project_info.get("description") or "No description available"
    tech_stack = ", ".join(project_info.get("tech_stack") or ["Unknown"])
    key_features = ", ".join(project_info.get("key_features") or ["None specified"])

    brief = f"""# Brief Template

Build or deliver [TASK DESCRIPTION] in {name}.
It should include [CORE DELIVERABLES], with [BEHAVIOR/INTERACTION DETAILS].
Make it meet [QUALITY BAR], using [RELEVANT CONSTRAINTS], [ENVIRONMENT OR INTEGRATION DETAILS], and [FINISHING TOUCHES].
Output as [ARTIFACT OR FORMAT].

## Project Context

**Name:** {project_info.get('name') or 'Unknown'}

**Description:** {description}

**Tech Stack:** {tech_stack}

**Key Features:** {key_features}

## Task Description

{task_description if task_description else '[Specify the task or feature to build]'}

## Field Explanations

- **TASK DESCRIPTION:** The specific outcome to produce
- **CORE DELIVERABLES:** Files, features, analysis, fixes, or decisions needed
- **BEHAVIOR/INTERACTION DETAILS:** What must work, how it behaves, edge cases
- **QUALITY BAR:** Correctness, performance, UX, safety, tone, or evidence standard
- **RELEVANT CONSTRAINTS:** What must stay unchanged; fenced-off files or actions
- **ENVIRONMENT OR INTEGRATION DETAILS:** APIs, data sources, deploy targets, permissions
- **FINISHING TOUCHES:** Polish, docs, or cleanup that rounds out the deliverable
- **ARTIFACT OR FORMAT:** Code changes, a file, a report, a PR, a patch, or an answer

## Next Steps

1. Fill in the [BRACKETED PLACEHOLDERS] with specific details
2. Remove any placeholder text
3. Add any missing context specific to this task
4. Use this brief to create a goal condition or supervised orchestration plan
"""

    return brief


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a brief from project context"
    )
    parser.add_argument(
        "project_dir",
        type=Path,
        help="Path to the project directory",
    )
    parser.add_argument(
        "--task",
        "-t",
        default="",
        help="Task description to include in the brief",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file for the generated brief",
    )
    args = parser.parse_args()

    if not args.project_dir.exists():
        print(f"Project directory not found: {args.project_dir}", file=sys.stderr)
        return 1

    brief = generate_brief(args.project_dir, args.task)

    if args.output:
        args.output.write_text(brief, encoding="utf-8")
        print(f"Brief generated and saved to {args.output}")
    else:
        print(brief)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
