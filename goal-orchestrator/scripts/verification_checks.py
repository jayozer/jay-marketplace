"""Parse explicit executable records; ordinary Markdown is never shell input.

One Verification bullet is one check. A command bullet is a single JSON object:
Command: {"command": "pytest -q", "cwd": ".", "expected_exit": 0}
All checks are required. Manual/file/prose bullets remain outstanding evidence.
"""

from __future__ import annotations

import json
from typing import Any


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate field {key!r}")
        result[key] = value
    return result


def parse_checks(items: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    commands: list[dict[str, Any]] = []
    manual: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, item in enumerate(items, 1):
        label, separator, body = item.partition(":")
        kind = label.strip().lower() if separator else "prose"
        if kind != "command":
            criterion = body.strip() if kind in {"manual", "file"} else item
            if not criterion.strip():
                errors.append(f"Verification bullet {index}: empty {kind} check")
            else:
                manual.append({"kind": kind if kind in {"manual", "file"} else "prose",
                               "criterion": criterion, "check_index": index, "status": "MANUAL"})
            continue
        try:
            check = json.loads(body, object_pairs_hook=_unique_object)
            if not isinstance(check, dict):
                raise ValueError("Command must be a JSON object")
            unknown = check.keys() - {"command", "cwd", "expected_exit", "evidence"}
            if unknown:
                raise ValueError(f"unknown fields: {', '.join(sorted(unknown))}")
            for field in ("command", "cwd"):
                if not isinstance(check.get(field), str) or not check[field].strip():
                    raise ValueError(f"{field} must be a nonempty string")
                if "\x00" in check[field] or "\n" in check[field] or "\r" in check[field]:
                    raise ValueError(f"{field} must be a single line without NUL")
            expected = check.get("expected_exit", 0)
            if type(expected) is not int or not 0 <= expected <= 255:
                raise ValueError("expected_exit must be an integer from 0 to 255")
            if "evidence" in check and (
                not isinstance(check["evidence"], str) or not check["evidence"].strip()
            ):
                raise ValueError("evidence must be a nonempty string")
            commands.append({**check, "expected_exit": expected, "check_index": index})
        except (ValueError, TypeError) as exc:
            errors.append(f"Verification bullet {index}: invalid Command record: {exc}")
    return commands, manual, errors
