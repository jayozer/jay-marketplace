# Video Understanding Kit

**Claude Code and Codex-compatible skills for analyzing local video files with Gemini multimodal models.**

Use this kit when you want an agent to answer questions about what happens in a
video, summarize a recording, inspect on-screen text, compare moments, or ground
an answer in timestamps without running a local video extraction stack.

---

## Before You Start

- **Claude Code or Codex** - the skill is written to work in either environment.
- **Python 3** - required for the bundled Gemini helper.
- **Gemini API key** - set `GEMINI_API_KEY` in your environment or in a `.env` file.
- **google-genai** - install with `pip install -r skills/video-understanding/requirements.txt`.
- **PyYAML** - only needed if you want to validate the skill locally: run `pip install -r requirements-dev.txt`.

---

## What's In Here

- `BLUEPRINT.md` - copy-paste prompts and manual usage examples.
- `skills/video-understanding` - upload local videos to Gemini, answer timestamp-grounded questions with `gemini-3.1-pro-preview` by default, save Markdown and JSON artifacts, and delete the uploaded Gemini file after analysis unless `--keep-upload` is used.

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
   The helper also auto-loads `~/.claude/.env`, so you can put `GEMINI_API_KEY=...` there instead.
5. Start or restart Claude Code so it picks up the new skill.

For Codex:

1. Copy `skills/video-understanding/` into your configured Codex skills folder.
2. Install the helper dependency from the copied skill folder.
3. Set `GEMINI_API_KEY` in your shell, in a parent-directory `.env`, or with the helper's `--env-file` option.
4. Restart Codex if needed so it refreshes available skills.

## How To Use It

Ask in plain English and include a video path when possible:

- "Analyze this video: `/path/to/demo.mp4`"
- "What happens in `/path/to/meeting.mov`?"
- "Summarize the key moments in this screen recording."
- "Read the on-screen text in this video and tell me what changes over time."
- "Use deep mode on this product walkthrough and give me timestamped findings."

The skill defaults to `gemini-3.1-pro-preview` and standard mode. Use quick mode
for brief summaries, standard mode for concise timelines, and deep mode when you
want more careful timestamped analysis of details such as small on-screen text or
subtle UI changes. Deep mode explicitly sends Gemini's highest Gemini 3 thinking
level, `high`.

Manual helper usage:

```bash
python3 skills/video-understanding/analyze_video_gemini.py "/path/to/demo.mp4" \
  --question "What happens in this video?" \
  --mode standard \
  --output-dir ~/video-understanding
```

For maximum reasoning effort:

```bash
python3 skills/video-understanding/analyze_video_gemini.py "/path/to/demo.mp4" \
  --question "Explain the important visual changes with timestamps." \
  --mode deep
```

You can override the Gemini 3 thinking level with `--thinking-level low`,
`--thinking-level medium`, or `--thinking-level high`.

The helper deletes the Gemini Files API upload after analysis by default. Use
`--keep-upload` only when you intentionally want the uploaded file to remain
available for debugging, auditing, or follow-up work.

For local repo development, a `.env` at the repo root works because the helper
searches the current directory and its parents before resolving `GEMINI_API_KEY`
and `GEMINI_MODEL`. The `.env` file is ignored by Git.

By default, saved artifacts go under
`~/video-understanding/<YYYY-MM-DD>-<video-slug>/` when you use `--output-dir`.
Each run writes `analysis.md` and `analysis.json`.

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
uv run --with PyYAML --with pytest --with google-genai pytest
uv run --with PyYAML python scripts/validate_skills.py
```
