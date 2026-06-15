from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "video-understanding"))

import analyze_video_gemini as gemini_video


class FakeFiles:
    def __init__(self) -> None:
        self.upload_calls = []
        self.get_calls = []
        self._uploaded = SimpleNamespace(
            name="files/video-123",
            uri="gemini://files/video-123",
            mime_type="video/mp4",
            state=SimpleNamespace(name="PROCESSING"),
        )

    def upload(self, *, file: str, config: dict) -> SimpleNamespace:
        self.upload_calls.append((file, config))
        return self._uploaded

    def get(self, *, name: str) -> SimpleNamespace:
        self.get_calls.append(name)
        self._uploaded.state = SimpleNamespace(name="ACTIVE")
        return self._uploaded


class FakeModels:
    def __init__(self) -> None:
        self.generate_calls = []

    def generate_content(self, *, model: str, contents: list, config: dict) -> SimpleNamespace:
        self.generate_calls.append((model, contents, config))
        return SimpleNamespace(text="00:00 The demo opens.\n00:10 A settings panel is shown.")


class FakeClient:
    def __init__(self) -> None:
        self.files = FakeFiles()
        self.models = FakeModels()


def test_supported_mime_types_include_common_gemini_video_formats() -> None:
    assert gemini_video.mime_type_for_path(Path("demo.mp4")) == "video/mp4"
    assert gemini_video.mime_type_for_path(Path("demo.mov")) == "video/quicktime"
    assert gemini_video.mime_type_for_path(Path("demo.webm")) == "video/webm"


def test_unsupported_video_format_has_helpful_error() -> None:
    with pytest.raises(ValueError, match="Unsupported video format"):
        gemini_video.mime_type_for_path(Path("demo.mkv"))


def test_build_prompt_requests_timestamp_grounded_answer() -> None:
    prompt = gemini_video.build_prompt(
        question="What changes in the UI?",
        mode="deep",
    )

    assert "What changes in the UI?" in prompt
    assert "timestamps" in prompt.lower()
    assert "deep" in prompt.lower()
    assert "uncertain" in prompt.lower()


def test_generation_config_sets_high_thinking_for_deep_mode() -> None:
    config = gemini_video.build_generation_config(mode="deep", thinking_level=None)

    assert config["temperature"] == 0.2
    assert config["thinking_config"] == {"thinking_level": "high"}


def test_generation_config_respects_explicit_thinking_level_override() -> None:
    config = gemini_video.build_generation_config(mode="deep", thinking_level="medium")

    assert config["thinking_config"] == {"thinking_level": "medium"}


def test_load_env_files_sets_missing_values_without_overwriting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                "# local credentials",
                "GEMINI_API_KEY=file-key",
                "GEMINI_MODEL='gemini-3.1-pro-preview'",
                "EXISTING_VALUE=from-file",
            ]
        )
        + "\n"
    )
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setenv("EXISTING_VALUE", "from-env")

    loaded = gemini_video.load_env_files(explicit_env_file=env_path)

    assert loaded == [env_path]
    assert "GEMINI_API_KEY" in os.environ
    assert os.environ["GEMINI_API_KEY"] == "file-key"
    assert os.environ["GEMINI_MODEL"] == "gemini-3.1-pro-preview"
    assert os.environ["EXISTING_VALUE"] == "from-env"


def test_analyze_video_uploads_generates_and_writes_outputs(tmp_path: Path) -> None:
    video_path = tmp_path / "demo.mp4"
    video_path.write_bytes(b"fake video bytes")
    markdown_path = tmp_path / "analysis.md"
    json_path = tmp_path / "analysis.json"
    client = FakeClient()

    result = gemini_video.analyze_video(
        client=client,
        video_path=video_path,
        question="Summarize the video.",
        model="gemini-3.1-pro-preview",
        mode="standard",
        thinking_level=None,
        markdown_output=markdown_path,
        json_output=json_path,
        poll_interval_seconds=0,
        timeout_seconds=5,
    )

    assert client.files.upload_calls == [
        (str(video_path), {"mime_type": "video/mp4", "display_name": "demo.mp4"})
    ]
    assert client.files.get_calls == ["files/video-123"]
    assert client.models.generate_calls
    model, contents, config = client.models.generate_calls[0]
    assert model == "gemini-3.1-pro-preview"
    assert contents[0].uri == "gemini://files/video-123"
    assert contents[0].mime_type == "video/mp4"
    assert "Summarize the video." in contents[1]
    assert config == {"temperature": 0.2}

    assert result.answer.startswith("00:00")
    assert "gemini-3.1-pro-preview" in markdown_path.read_text()
    payload = json.loads(json_path.read_text())
    assert payload["model"] == "gemini-3.1-pro-preview"
    assert payload["video_path"] == str(video_path)
    assert payload["answer"] == result.answer
