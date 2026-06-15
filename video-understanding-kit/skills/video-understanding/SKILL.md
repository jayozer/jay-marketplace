---
name: video-understanding
description: Analyze local video files with Gemini multimodal models, especially Gemini 3.1 Pro Preview, by uploading supported video formats and answering grounded questions with timestamps. Use when the user asks to analyze, understand, describe, summarize, inspect, or answer questions about videos such as .mp4, .mov, .webm, .avi, .wmv, .mpeg, .mpg, .flv, or .3gp files.
allowed-tools: Bash(python3:*), Read, Glob, Grep
---

# Video Understanding

Analyze videos by sending the video directly to Gemini, then answer the user's
question with timestamp-grounded observations.

Use the bundled `analyze_video_gemini.py` helper. It uploads a local video with
the Gemini Files API, waits for processing, asks the configured Gemini model to
analyze the video, and writes optional Markdown and JSON outputs.

## 1. Parse The Request

Identify:

- The local video file path.
- The user's question or desired output.
- The analysis mode, if specified.
- Optional output paths.

Use `standard` mode by default. Use `quick` for fast summaries. Use `deep` when
the user asks for detailed visual inspection, small on-screen text, complex UI
changes, or high-confidence timestamped findings.

If the path is missing, ask for it. If the file is in a protected macOS folder
and cannot be opened, ask the user to move it to an accessible location or grant
the terminal/IDE the needed file access.

## 2. Check Setup

The user needs:

- `GEMINI_API_KEY` in the environment.
- Python dependencies installed from this skill's `requirements.txt`.

The helper auto-loads `.env` files from the current directory, parent
directories, `~/.claude/.env`, and `~/.env`. For a specific file, pass
`--env-file`.

For Claude Code default installs, the dependency command is:

```bash
python3 -m pip install -r ~/.claude/skills/video-understanding/requirements.txt
```

The default model is `gemini-3.1-pro-preview`. The user can override it with
`GEMINI_MODEL` or the helper's `--model` flag.

## 3. Run Gemini Analysis

For Claude Code default installs:

```bash
python3 ~/.claude/skills/video-understanding/analyze_video_gemini.py "<video_path>" \
  --question "<question>" \
  --mode standard
```

To save artifacts:

```bash
python3 ~/.claude/skills/video-understanding/analyze_video_gemini.py "<video_path>" \
  --question "<question>" \
  --mode deep \
  --output "<analysis.md>" \
  --json-output "<analysis.json>"
```

If running from the project checkout instead of an installed skill, use:

```bash
python3 skills/video-understanding/analyze_video_gemini.py "<video_path>" \
  --question "<question>"
```

## 4. Answer The User

Use the helper output as the evidence-backed answer.

When reporting:

- Include timestamps for important observations.
- Distinguish visual evidence, spoken/audio evidence, and on-screen text when useful.
- Mention uncertainty when Gemini is uncertain or when the video is ambiguous.
- Avoid claiming exact details that are not supported by the model output.

For summaries, prefer a concise timeline. For debugging or product walkthroughs,
walk through the relevant segment and describe what changes on screen.

## Supported Formats

Gemini API supports these video MIME types:

- `video/mp4`
- `video/mpeg`
- `video/quicktime`
- `video/avi`
- `video/x-flv`
- `video/mpg`
- `video/webm`
- `video/wmv`
- `video/3gpp`

If the user provides `.mkv`, ask them to convert it to `.mp4` or another
supported format before analysis.

## Helper Reference

```text
usage: analyze_video_gemini.py [-h] [-q QUESTION] [--model MODEL]
                               [--mode {quick,standard,deep}] [-o OUTPUT]
                               [--json-output JSON_OUTPUT]
                               [--poll-interval POLL_INTERVAL]
                               [--timeout TIMEOUT]
                               [--env-file ENV_FILE]
                               video_path
```

Important options:

- `--question` / `-q`: question to ask about the video.
- `--model`: Gemini model, defaulting to `GEMINI_MODEL` or `gemini-3.1-pro-preview`.
- `--mode`: `quick`, `standard`, or `deep`; shapes the analysis prompt.
- `--output`: write Markdown output.
- `--json-output`: write structured JSON output.
- `--timeout`: maximum seconds to wait for Gemini file processing.
- `--env-file`: load a specific `.env` file before reading `GEMINI_API_KEY`.

## Troubleshooting

- `Missing GEMINI_API_KEY`: export a Gemini API key before running the helper.
- `Missing dependency: google-genai`: install this skill's `requirements.txt`.
- `Unsupported video format`: convert the video to a supported format such as `.mp4`.
- `Timed out waiting for Gemini file`: retry later, use a smaller video, or increase `--timeout`.
- `Path not found`: move the video to an accessible folder or grant the terminal/IDE file access.
