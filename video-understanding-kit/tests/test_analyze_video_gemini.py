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
        self.delete_calls = []
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

    def delete(self, *, name: str) -> None:
        self.delete_calls.append(name)


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


class ProcessingFiles:
    def __init__(self) -> None:
        self.get_calls = []

    def get(self, *, name: str) -> SimpleNamespace:
        self.get_calls.append(name)
        return SimpleNamespace(name=name, state=SimpleNamespace(name="PROCESSING"))


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


def test_build_prompt_uses_mode_specific_instructions() -> None:
    quick_prompt = gemini_video.build_prompt(question="Summarize this.", mode="quick")
    standard_prompt = gemini_video.build_prompt(question="Summarize this.", mode="standard")
    deep_prompt = gemini_video.build_prompt(question="Summarize this.", mode="deep")

    assert "brief" in quick_prompt.lower()
    assert "timeline" in standard_prompt.lower()
    assert "small on-screen text" in deep_prompt.lower()
    assert quick_prompt != standard_prompt
    assert standard_prompt != deep_prompt


def test_generation_config_sets_high_thinking_for_deep_mode() -> None:
    config = gemini_video.build_generation_config(mode="deep", thinking_level=None)

    assert config["temperature"] == 0.2
    assert config["thinking_config"] == {"thinking_level": "high"}


def test_generation_config_respects_explicit_thinking_level_override() -> None:
    config = gemini_video.build_generation_config(mode="deep", thinking_level="medium")

    assert config["thinking_config"] == {"thinking_level": "medium"}


def test_wait_for_active_file_rejects_unexpected_state() -> None:
    failed_file = SimpleNamespace(
        name="files/video-123",
        state=SimpleNamespace(name="FAILED"),
    )

    with pytest.raises(RuntimeError, match="unexpected state: FAILED"):
        gemini_video.wait_for_active_file(
            SimpleNamespace(files=FakeFiles()),
            failed_file,
            poll_interval_seconds=0,
            timeout_seconds=5,
        )


def test_wait_for_active_file_times_out_processing_state() -> None:
    processing_file = SimpleNamespace(
        name="files/video-123",
        state=SimpleNamespace(name="PROCESSING"),
    )

    with pytest.raises(TimeoutError, match="Timed out waiting"):
        gemini_video.wait_for_active_file(
            SimpleNamespace(files=ProcessingFiles()),
            processing_file,
            poll_interval_seconds=0,
            timeout_seconds=0,
        )


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


def test_parse_args_rejects_invalid_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["analyze_video_gemini.py", "demo.mp4", "--mode", "turbo"],
    )

    with pytest.raises(SystemExit):
        gemini_video.parse_args()


def test_main_uses_env_model_when_model_flag_is_omitted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    video_path = tmp_path / "demo.mp4"
    video_path.write_bytes(b"fake video bytes")
    env_path = tmp_path / ".env"
    env_path.write_text(
        "GEMINI_API_KEY=file-key\nGEMINI_MODEL=gemini-env-model\n",
        encoding="utf-8",
    )
    client = FakeClient()

    def fake_create_client(*, env_file: Path | None = None) -> FakeClient:
        gemini_video.load_env_files(explicit_env_file=env_file)
        return client

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.setattr(gemini_video, "create_client", fake_create_client)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "analyze_video_gemini.py",
            str(video_path),
            "--env-file",
            str(env_path),
            "--poll-interval",
            "0",
        ],
    )

    assert gemini_video.main() == 0

    model, _, _ = client.models.generate_calls[0]
    assert model == "gemini-env-model"


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
    assert client.files.delete_calls == ["files/video-123"]
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
    assert payload["upload_deleted"] is True


def test_analyze_video_can_keep_uploaded_file(tmp_path: Path) -> None:
    video_path = tmp_path / "demo.mp4"
    video_path.write_bytes(b"fake video bytes")
    client = FakeClient()

    result = gemini_video.analyze_video(
        client=client,
        video_path=video_path,
        question="Summarize the video.",
        model="gemini-3.1-pro-preview",
        mode="standard",
        thinking_level=None,
        poll_interval_seconds=0,
        timeout_seconds=5,
        keep_upload=True,
    )

    assert client.files.delete_calls == []
    assert result.upload_deleted is False


def test_resolve_output_paths_uses_slugged_output_dir(tmp_path: Path) -> None:
    markdown_path, json_path = gemini_video.resolve_output_paths(
        video_path=Path("Demo Walkthrough.mov"),
        output_dir=tmp_path,
        slug="custom-demo",
        markdown_output=None,
        json_output=None,
    )

    assert markdown_path == tmp_path / "custom-demo" / "analysis.md"
    assert json_path == tmp_path / "custom-demo" / "analysis.json"


def test_resolve_output_paths_derives_slug_from_video_name(tmp_path: Path) -> None:
    markdown_path, json_path = gemini_video.resolve_output_paths(
        video_path=Path("Demo Walkthrough.mov"),
        output_dir=tmp_path,
        slug=None,
        markdown_output=None,
        json_output=None,
    )

    expected_dir = tmp_path / f"{gemini_video.today_slug()}-demo-walkthrough"
    assert markdown_path == expected_dir / "analysis.md"
    assert json_path == expected_dir / "analysis.json"
