# Video Understanding Kit

**Claude Code and Codex-compatible skills for analyzing local video files with extracted visual, audio, OCR, and timeline evidence.**

Use this kit when you want an agent to answer questions about what happens in a
video, summarize a recording, inspect on-screen text, compare moments, or ground
an answer in timestamps.

---

## Before You Start

- **Claude Code or Codex** - the skill is written to work in either environment.
- **Python 3** - only needed for local validation.
- **PyYAML** - only needed if you want to validate the skill locally: run `pip install -r requirements-dev.txt`.
- **vidclaude CLI** - must be installed and available on `PATH`.
- **ffmpeg** - required by the video extraction pipeline.
- **Tesseract OCR** - optional, but recommended when you need on-screen text extraction.

---

## What's In Here

- `skills/video-understanding` - analyze videos by extracting frames, audio transcript, OCR text, and a timestamped evidence report with `vidclaude`.

## Install

For Claude Code:

1. Find or create your skills folder: `~/.claude/skills/`
2. Copy `skills/video-understanding/` into it, so you have `~/.claude/skills/video-understanding/`
3. Start or restart Claude Code so it picks up the new skill.

For Codex:

1. Copy `skills/video-understanding/` into your configured Codex skills folder.
2. Restart Codex if needed so it refreshes available skills.

## How To Use It

Ask in plain English and include a video path when possible:

- "Analyze this video: `/path/to/demo.mp4`"
- "What happens in `/path/to/meeting.mov`?"
- "Summarize the key moments in this screen recording."
- "Read the on-screen text in this video and tell me what changes over time."
- "Use deep mode on this product walkthrough and give me timestamped findings."

The skill defaults to standard extraction. Use quick mode for fast overviews and
deep mode when you need more frames, more OCR, or closer visual inspection.

## Validate The Skill

From this folder:

```bash
pip install -r requirements-dev.txt
python3 scripts/validate_skills.py
```

You can also run the validator without installing globally:

```bash
uv run --with PyYAML python scripts/validate_skills.py
```
