#!/usr/bin/env python3
"""Analyze videos with Gemini multimodal models."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "gemini-3.1-pro-preview"
ENV_KEY_PATTERN = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
SUPPORTED_VIDEO_MIME_TYPES = {
    ".mp4": "video/mp4",
    ".mpeg": "video/mpeg",
    ".mov": "video/quicktime",
    ".avi": "video/avi",
    ".flv": "video/x-flv",
    ".mpg": "video/mpg",
    ".webm": "video/webm",
    ".wmv": "video/wmv",
    ".3gp": "video/3gpp",
}


@dataclass(frozen=True)
class AnalysisResult:
    video_path: str
    question: str
    model: str
    mode: str
    mime_type: str
    file_uri: str
    answer: str


def mime_type_for_path(path: Path) -> str:
    mime_type = SUPPORTED_VIDEO_MIME_TYPES.get(path.suffix.lower())
    if not mime_type:
        extensions = ", ".join(sorted(SUPPORTED_VIDEO_MIME_TYPES))
        raise ValueError(
            f"Unsupported video format: {path.suffix or '(none)'}. "
            f"Supported extensions: {extensions}."
        )
    return mime_type


def build_prompt(*, question: str, mode: str) -> str:
    return f"""Analyze the attached video in {mode} mode.

User question:
{question}

Answer requirements:
- Ground important claims in visible or audible evidence from the video.
- Include timestamps for key moments whenever possible.
- Distinguish what is seen, heard, or read on screen when useful.
- If something is uncertain, say that it is uncertain instead of guessing.
- Prefer a concise timeline for summaries and a focused explanation for direct questions.
"""


def load_env_files(*, explicit_env_file: Path | None = None) -> list[Path]:
    paths = [explicit_env_file] if explicit_env_file else _candidate_env_files()
    loaded: list[Path] = []
    seen: set[Path] = set()

    for raw_path in paths:
        if raw_path is None:
            continue
        path = raw_path.expanduser().resolve()
        if path in seen:
            continue
        seen.add(path)

        explicit_path = explicit_env_file.expanduser().resolve() if explicit_env_file else None
        if explicit_path and path == explicit_path and not path.exists():
            raise FileNotFoundError(f"Environment file does not exist: {path}")
        if not path.is_file():
            continue

        _load_env_file(path)
        loaded.append(path)

    return loaded


def _candidate_env_files() -> list[Path]:
    candidates: list[Path] = []
    for base in (Path.cwd().resolve(), Path(__file__).resolve().parent):
        candidates.append(base / ".env")
        candidates.extend(parent / ".env" for parent in base.parents)

    home = Path.home()
    candidates.extend([home / ".claude" / ".env", home / ".env"])
    return candidates


def _load_env_file(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        match = ENV_KEY_PATTERN.match(stripped)
        if not match:
            continue

        key, value = match.groups()
        os.environ.setdefault(key, _clean_env_value(value))


def _clean_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def wait_for_active_file(
    client: Any,
    uploaded_file: Any,
    *,
    poll_interval_seconds: float,
    timeout_seconds: float,
) -> Any:
    deadline = time.monotonic() + timeout_seconds
    current = uploaded_file

    while _file_state_name(current) == "PROCESSING":
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out waiting for Gemini file {current.name} to process")
        time.sleep(poll_interval_seconds)
        current = client.files.get(name=current.name)

    state = _file_state_name(current)
    if state and state != "ACTIVE":
        raise RuntimeError(f"Gemini file {current.name} is in unexpected state: {state}")

    return current


def analyze_video(
    *,
    client: Any,
    video_path: Path,
    question: str,
    model: str,
    mode: str,
    markdown_output: Path | None = None,
    json_output: Path | None = None,
    poll_interval_seconds: float = 2,
    timeout_seconds: float = 600,
) -> AnalysisResult:
    video_path = video_path.expanduser().resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"Video path does not exist: {video_path}")
    if not video_path.is_file():
        raise ValueError(f"Video path must be a file: {video_path}")

    mime_type = mime_type_for_path(video_path)
    uploaded_file = client.files.upload(
        file=str(video_path),
        config={"mime_type": mime_type, "display_name": video_path.name},
    )
    active_file = wait_for_active_file(
        client,
        uploaded_file,
        poll_interval_seconds=poll_interval_seconds,
        timeout_seconds=timeout_seconds,
    )

    prompt = build_prompt(question=question, mode=mode)
    response = client.models.generate_content(
        model=model,
        contents=[active_file, prompt],
        config={"temperature": 0.2},
    )

    answer = getattr(response, "text", "") or ""
    result = AnalysisResult(
        video_path=str(video_path),
        question=question,
        model=model,
        mode=mode,
        mime_type=mime_type,
        file_uri=getattr(active_file, "uri", ""),
        answer=answer,
    )

    if markdown_output:
        write_markdown(markdown_output, result)
    if json_output:
        write_json(json_output, result)

    return result


def write_markdown(path: Path, result: AnalysisResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(result), encoding="utf-8")


def write_json(path: Path, result: AnalysisResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")


def render_markdown(result: AnalysisResult) -> str:
    return f"""# Gemini Video Analysis

- Video: `{result.video_path}`
- Model: `{result.model}`
- Mode: `{result.mode}`
- MIME type: `{result.mime_type}`
- File URI: `{result.file_uri}`

## Question

{result.question}

## Answer

{result.answer.strip()}
"""


def create_client(*, env_file: Path | None = None) -> Any:
    load_env_files(explicit_env_file=env_file)

    try:
        from google import genai
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: google-genai. Install with "
            "`pip install -r requirements.txt`."
        ) from exc

    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("Missing GEMINI_API_KEY environment variable.")

    return genai.Client()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video_path", help="Local video file path to analyze")
    parser.add_argument(
        "-q",
        "--question",
        default="Summarize this video with timestamped key moments.",
        help="Question to ask about the video",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL),
        help=f"Gemini model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--mode",
        choices=("quick", "standard", "deep"),
        default="standard",
        help="Analysis mode used to shape the prompt",
    )
    parser.add_argument("-o", "--output", type=Path, help="Markdown output path")
    parser.add_argument("--json-output", type=Path, help="JSON output path")
    parser.add_argument("--poll-interval", type=float, default=2)
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Optional .env file to load before reading GEMINI_API_KEY",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = analyze_video(
        client=create_client(env_file=args.env_file),
        video_path=Path(args.video_path),
        question=args.question,
        model=args.model,
        mode=args.mode,
        markdown_output=args.output,
        json_output=args.json_output,
        poll_interval_seconds=args.poll_interval,
        timeout_seconds=args.timeout,
    )

    if not args.output:
        print(render_markdown(result))
    return 0


def _file_state_name(file_ref: Any) -> str:
    state = getattr(file_ref, "state", None)
    if state is None:
        return ""
    return str(getattr(state, "name", state)).upper()


if __name__ == "__main__":
    raise SystemExit(main())
