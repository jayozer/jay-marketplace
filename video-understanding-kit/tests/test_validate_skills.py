from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_skills


def write_skill(skill_dir: Path) -> None:
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: video-understanding",
                "description: Analyze local video files.",
                "allowed-tools: Bash(python3:*), Read, Glob, Grep",
                "---",
                "",
                "# Video Understanding",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_validate_video_understanding_requires_helper_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(validate_skills, "ROOT", tmp_path)
    skill_dir = tmp_path / "skills" / "video-understanding"
    write_skill(skill_dir)

    errors = validate_skills.validate_skill(skill_dir)

    assert "skills/video-understanding/analyze_video_gemini.py: missing required file" in errors
    assert "skills/video-understanding/requirements.txt: missing required file" in errors


def test_validate_video_understanding_accepts_required_helper_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(validate_skills, "ROOT", tmp_path)
    skill_dir = tmp_path / "skills" / "video-understanding"
    write_skill(skill_dir)
    (skill_dir / "analyze_video_gemini.py").write_text("# helper\n", encoding="utf-8")
    (skill_dir / "requirements.txt").write_text("google-genai>=2.8.0\n", encoding="utf-8")

    errors = validate_skills.validate_skill(skill_dir)

    assert errors == []
