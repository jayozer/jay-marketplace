---
name: video-understanding
description: Analyze local video files or folders by extracting frames, audio transcripts, OCR text, and timelines with the vidclaude CLI, then answer grounded questions with timestamps. Use when the user asks to analyze, understand, describe, summarize, inspect, or answer questions about videos, including .mp4, .mov, .mkv, or .webm files.
allowed-tools: Bash(vidclaude:*), Bash(which:*), Bash(ffmpeg:*), Read, Glob, Grep
---

# Video Understanding

Analyze videos by extracting visual frames, audio transcripts, OCR text, and a
timestamped evidence report, then reason over the combined evidence.

The extraction is performed by the `vidclaude` CLI. The agent reads the
resulting evidence and key frame images to answer the user's question.

## 1. Parse The Request

Identify:

- The video file or folder path.
- The user's question or desired output.
- The extraction mode, if specified.

Use `standard` mode by default. Use `quick` for fast overviews. Use `deep` when
the user asks for detailed visual inspection, OCR-heavy analysis, small text,
complex scenes, or a high-confidence timeline.

If the path is missing, ask for it. If the file is in a protected macOS folder
and cannot be opened, ask the user to move it to an accessible location or grant
the terminal/IDE the needed file access.

## 2. Extract Evidence

Run one of these commands.

Standard analysis:

```bash
vidclaude "<video_path>" --extract --mode standard --verbose
```

Quick analysis:

```bash
vidclaude "<video_path>" --extract --mode quick --verbose
```

Deep analysis:

```bash
vidclaude "<video_path>" --extract --mode deep --verbose
```

For a folder of videos:

```bash
vidclaude "<folder_path>" --extract --mode standard --verbose
```

The command prints a cache directory path, such as:

```text
Cache: /path/.vidcache/<hash>
```

If the user asks a follow-up question about the same video, reuse the cache.
Only force re-extraction with `--no-cache` when the user asks for it or when the
cached evidence is stale.

## 3. Read The Evidence

Read `<cache>/evidence.md`. Use it as the primary timeline, transcript, OCR, and
frame index.

Then inspect representative frames from the evidence report:

- Choose 5-10 frames for normal questions.
- Spread frames across the full duration.
- Include extra frames around timestamps relevant to the user's question.
- Use the platform's image-viewing ability: Claude Code can read image paths;
  Codex may use `view_image` or an equivalent local image viewer.

## 4. Answer The Question

Ground claims in the extracted evidence:

- Cite timestamps for important observations.
- Distinguish visual evidence, transcript evidence, and OCR evidence when useful.
- Mention uncertainty when frames, audio, or OCR are ambiguous.
- Avoid claiming exact details that are not visible, audible, or present in the
  extracted report.

For summaries, prefer a timeline with the most important moments. For debugging,
walk through the relevant segment and describe what changes on screen.

## CLI Reference

| Flag | Default | Description |
|------|---------|-------------|
| `input` | required | Video file or folder path |
| `--extract` | off | Extract evidence only |
| `-q "..."` | none | Question for standalone API mode |
| `-f N` | mode default | Frames per second override |
| `-m N` | mode default | Max frames override |
| `--no-audio` | off | Skip audio transcription |
| `--no-ocr` | off | Skip OCR extraction |
| `--mode` | standard | `quick`, `standard`, or `deep` |
| `--verbose` | off | Detailed progress output |
| `--no-cache` | off | Force re-extraction |
| `--api` | off | Standalone mode, if configured |
| `-o file` | stdout | Write output to file |

## Modes

| Aspect | quick | standard | deep |
|--------|-------|----------|------|
| Frame sampling | 0.2fps, max 20 | 0.5fps plus shot boundaries, max 60 | 1.0fps plus burst, max 150 |
| Audio | whisper base | whisper base | whisper small |
| OCR | skipped | keyframes only | all frames |

## Prerequisites

- `vidclaude` CLI on `PATH` (`which vidclaude`).
- `ffmpeg` on `PATH` (`ffmpeg -version`).
- Optional OCR support: Tesseract 5.x and `pytesseract`.

## Troubleshooting

- `Path not found` or `No such file or directory` for a real file: this is often
  macOS privacy protection. Move the video to an accessible folder or grant Full
  Disk Access to the terminal/IDE in System Settings.
- `ffmpeg not found`: install ffmpeg and ensure it is on `PATH`.
- Audio skipped: install the audio dependencies expected by `vidclaude`.
- OCR skipped: install Tesseract and `pytesseract`.
- Extraction is slow: use `--mode quick` or lower the frame cap with `-m`.
