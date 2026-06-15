---
name: video-understanding
description: Analyze local video files with Gemini multimodal models, especially Gemini 3.1 Pro Preview, by uploading supported video formats and answering grounded questions with timestamps. Use when the user asks to analyze, understand, describe, summarize, inspect, or answer questions about videos such as .mp4, .mov, .webm, .avi, .wmv, .mpeg, .mpg, .flv, or .3gp files.
argument-hint: '[video_path] [--mode quick|standard|deep] [--question "..."]'
allowed-tools: Bash(python3:*), Read, Glob, Grep
user-invocable: true
---

# Video Understanding

Analyze local videos by sending the video directly to Gemini, then answer the
user's question with timestamp-grounded observations.

Use the bundled `analyze_video_gemini.py` helper. It uploads a local video with
the Gemini Files API, waits for processing, asks the configured Gemini model to
analyze the video, deletes the uploaded file by default after analysis, and
writes Markdown plus JSON artifacts for follow-up use.

## Workflow Context

Use this skill for direct video understanding, screen recording review, product
walkthrough inspection, UI change analysis, and on-screen text questions.

Do not use this skill for YouTube channel research, script planning, thumbnail
generation, or social repurposing. Those belong to the YouTube automation kit.

## Data Location

Default artifacts should be written under:

```text
~/video-understanding/<YYYY-MM-DD>-<video-slug>/
```

The helper writes:

- `analysis.md`: human-readable Gemini analysis.
- `analysis.json`: structured fields for follow-up questions.

When the user provides explicit `--output` or `--json-output` paths, use those
paths instead. For follow-up questions, read the existing `analysis.json` and
`analysis.md` first. Re-run Gemini only when the stored analysis does not answer
the new question.

## Parsing Arguments

Parse `$ARGUMENTS` for:

- **Video path**: required positional path to one local video file.
- `--question`: optional question to ask about the video. If omitted, ask for a
  timestamped summary of key moments.
- `--mode`: optional `quick`, `standard`, or `deep`. Default: `standard`.
- `--output`: optional Markdown output path.
- `--json-output`: optional JSON output path.
- `--output-dir`: optional artifact root directory.
- `--slug`: optional folder slug inside `--output-dir`.
- `--thinking-level`: optional `low`, `medium`, or `high`.
- `--model`: optional Gemini model override.
- `--timeout`: optional processing timeout in seconds.
- `--env-file`: optional `.env` file path.
- `--keep-upload`: keep the Gemini Files API upload instead of deleting it.

If the path is missing, ask for it. If the file is in a protected macOS folder
and cannot be opened, ask the user to move it to an accessible location or grant
the terminal or IDE the needed file access.

## Flow

### Step 1: Validate Setup

The user needs:

- `GEMINI_API_KEY` in the environment or an auto-loaded `.env` file.
- Python dependencies installed from this skill's `requirements.txt`.

For Claude Code default installs, the dependency command is:

```bash
python3 -m pip install -r "${CLAUDE_SKILL_DIR}/requirements.txt"
```

The helper auto-loads `.env` files from the current directory, parent
directories, `~/.claude/.env`, and `~/.env`. For a specific file, pass
`--env-file`.

The default model is `gemini-3.1-pro-preview`. The user can override it with
`GEMINI_MODEL` in the environment or `.env`, or with the helper's `--model`
flag.

### Step 2: Choose Mode

Use `standard` mode by default.

- `quick`: brief summaries and first-pass triage.
- `standard`: concise timeline with key visual, audio, and on-screen text evidence.
- `deep`: detailed visual inspection, small on-screen text, complex UI changes,
  or high-confidence timestamped findings.

Deep mode explicitly uses Gemini's highest Gemini 3 thinking level, `high`,
unless the user passes a different `--thinking-level`.

### Step 3: Run Analysis

Prefer saving both Markdown and JSON artifacts:

```bash
python3 "${CLAUDE_SKILL_DIR}/analyze_video_gemini.py" "<video_path>" \
  --question "<question>" \
  --mode standard \
  --output-dir ~/video-understanding \
  --slug "<YYYY-MM-DD>-<video-slug>"
```

For maximum reasoning effort:

```bash
python3 "${CLAUDE_SKILL_DIR}/analyze_video_gemini.py" "<video_path>" \
  --question "<question>" \
  --mode deep \
  --output-dir ~/video-understanding \
  --slug "<YYYY-MM-DD>-<video-slug>"
```

If running from the project checkout instead of an installed skill, use:

```bash
python3 skills/video-understanding/analyze_video_gemini.py "<video_path>" \
  --question "<question>" \
  --output-dir ~/video-understanding
```

Uploaded Gemini files are deleted after analysis by default. Pass
`--keep-upload` only when the user intentionally wants the uploaded file to
remain available for debugging, auditing, or follow-up work.

### Step 4: Read Artifacts

After the helper finishes, read `analysis.json` when present. Use `analysis.md`
for a human-readable version of the same answer.

If the user asks a follow-up:

1. Read the prior `analysis.json` and `analysis.md`.
2. Answer from those artifacts if they contain the needed evidence.
3. Re-run the helper only when the prior analysis is insufficient.

Do not claim a deleted Gemini file can be reused. Reuse remote uploads only when
the user explicitly used `--keep-upload` and the artifact says upload deletion
did not happen.

### Step 5: Present Findings

Use the helper output as the evidence-backed answer.

For summaries, prefer a concise timeline. For debugging or product walkthroughs,
walk through the relevant segment and describe what changes on screen.

Always include the artifact directory or output file paths when files were saved.

## Output

For a video named `Demo Walkthrough.mov`, default saved outputs should look like:

```text
~/video-understanding/<YYYY-MM-DD>-demo-walkthrough/analysis.md
~/video-understanding/<YYYY-MM-DD>-demo-walkthrough/analysis.json
```

The JSON includes the video path, question, model, mode, MIME type, Gemini file
URI, answer text, and whether the upload was deleted.

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
                               [--output-dir OUTPUT_DIR] [--slug SLUG]
                               [--poll-interval POLL_INTERVAL]
                               [--timeout TIMEOUT]
                               [--env-file ENV_FILE]
                               [--thinking-level {low,medium,high}]
                               [--keep-upload]
                               video_path
```

Important options:

- `--question` / `-q`: question to ask about the video.
- `--model`: Gemini model, defaulting to `GEMINI_MODEL` or `gemini-3.1-pro-preview`.
- `--mode`: `quick`, `standard`, or `deep`; shapes the analysis prompt.
- `--thinking-level`: Gemini 3 thinking level. Deep mode defaults to `high`.
- `--output`: write Markdown output.
- `--json-output`: write structured JSON output.
- `--output-dir`: write `analysis.md` and `analysis.json` under a slugged folder.
- `--slug`: folder slug to use inside `--output-dir`.
- `--timeout`: maximum seconds to wait for Gemini file processing.
- `--env-file`: load a specific `.env` file before reading `GEMINI_API_KEY`.
- `--keep-upload`: leave the uploaded Gemini file in place instead of deleting it after analysis.

## Rules

- Ground important claims in visible or audible evidence from the video.
- Include timestamps for important observations whenever possible.
- Distinguish visual evidence, spoken/audio evidence, and on-screen text when useful.
- Mention uncertainty when Gemini is uncertain or when the video is ambiguous.
- Avoid claiming exact details that are not supported by the model output.
- Prefer saved JSON artifacts for follow-ups before re-uploading the same video.
- Delete uploads by default; keep uploads only when the user explicitly asks.

## Troubleshooting

- `Missing GEMINI_API_KEY`: export a Gemini API key before running the helper.
- `Missing dependency: google-genai`: install this skill's `requirements.txt`.
- `Unsupported video format`: convert the video to a supported format such as `.mp4`.
- `Timed out waiting for Gemini file`: retry later, use a smaller video, or increase `--timeout`.
- `Upload deleted: false` in output: the helper could not confirm deletion, or you passed `--keep-upload`.
- `Path not found`: move the video to an accessible folder or grant the terminal or IDE file access.
