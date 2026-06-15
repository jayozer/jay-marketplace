# Video Understanding Kit

**Claude Code and Codex-compatible skills for analyzing local video files with Gemini multimodal models.**

Use this kit when you want an agent to answer questions about what happens in a
video, summarize a recording, inspect on-screen text, compare moments, or ground
an answer in timestamps without running a local video extraction stack.

---

## Before You Start

- **Claude Code or Codex** - the skill is written to work in either environment.
- **Python 3** - required for the bundled Gemini helper.
- **Gemini API key** - set `GEMINI_API_KEY` in your environment.
- **google-genai** - install with `pip install -r skills/video-understanding/requirements.txt`.
- **PyYAML** - only needed if you want to validate the skill locally: run `pip install -r requirements-dev.txt`.

---

## What's In Here

- `skills/video-understanding` - upload local videos to Gemini and answer timestamp-grounded questions with `gemini-3.1-pro-preview` by default.

## Install

For Claude Code:

1. Find or create your skills folder: `~/.claude/skills/`
2. Copy `skills/video-understanding/` into it, so you have `~/.claude/skills/video-understanding/`
3. Install the helper dependency:
   ```bash
   python3 -m pip install -r ~/.claude/skills/video-understanding/requirements.txt
   ```
4. Set your Gemini API key:
   ```bash
   export GEMINI_API_KEY=your_key_here
   ```
5. Start or restart Claude Code so it picks up the new skill.

For Codex:

1. Copy `skills/video-understanding/` into your configured Codex skills folder.
2. Install the helper dependency from the copied skill folder.
3. Set `GEMINI_API_KEY`.
4. Restart Codex if needed so it refreshes available skills.

## How To Use It

Ask in plain English and include a video path when possible:

- "Analyze this video: `/path/to/demo.mp4`"
- "What happens in `/path/to/meeting.mov`?"
- "Summarize the key moments in this screen recording."
- "Read the on-screen text in this video and tell me what changes over time."
- "Use deep mode on this product walkthrough and give me timestamped findings."

The skill defaults to `gemini-3.1-pro-preview` and standard mode. Use quick mode
for fast overviews and deep mode when you want more careful timestamped analysis.

Manual helper usage:

```bash
python3 skills/video-understanding/analyze_video_gemini.py "/path/to/demo.mp4" \
  --question "What happens in this video?" \
  --mode standard \
  --output analysis.md \
  --json-output analysis.json
```

Supported input formats follow Gemini API video support: `.mp4`, `.mpeg`,
`.mov`, `.avi`, `.flv`, `.mpg`, `.webm`, `.wmv`, and `.3gp`. Convert `.mkv`
files to `.mp4` before analysis.

## Validate The Skill

From this folder:

```bash
pip install -r requirements-dev.txt
pytest
python3 scripts/validate_skills.py
```

You can also run the validator without installing globally:

```bash
uv run --with PyYAML --with pytest pytest
uv run --with PyYAML python scripts/validate_skills.py
```
