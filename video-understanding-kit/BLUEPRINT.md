# Video Understanding Kit Blueprint

Use these prompts with Claude Code, Codex, or any AI agent that can run local
commands and read local files. Replace paths with your own video paths.

## Quick Summary

```text
Use the video-understanding skill to summarize `/path/to/demo.mp4`.
Use standard mode and give me a concise timeline with timestamps.
Save Markdown and JSON artifacts under `~/video-understanding`.
```

Manual helper:

```bash
python3 skills/video-understanding/analyze_video_gemini.py "/path/to/demo.mp4" \
  --question "Summarize this video with timestamped key moments." \
  --mode standard \
  --output-dir ~/video-understanding
```

## Inspect UI Changes

```text
Analyze `/path/to/screen-recording.mov` with video-understanding.
Focus on UI changes over time: navigation, controls clicked, visible state
changes, loading states, errors, and final outcome. Include timestamps.
Use deep mode and save artifacts under `~/video-understanding`.
```

Manual helper:

```bash
python3 skills/video-understanding/analyze_video_gemini.py "/path/to/screen-recording.mov" \
  --question "Describe the important UI changes over time with timestamps." \
  --mode deep \
  --output-dir ~/video-understanding
```

## Read On-Screen Text

```text
Use video-understanding on `/path/to/walkthrough.mp4`.
Read the on-screen text and explain how it changes over time.
Call out uncertain text rather than guessing. Use deep mode.
```

Manual helper:

```bash
python3 skills/video-understanding/analyze_video_gemini.py "/path/to/walkthrough.mp4" \
  --question "Read the on-screen text and explain how it changes over time. Mention uncertainty instead of guessing." \
  --mode deep \
  --output-dir ~/video-understanding
```

## Deep Product Walkthrough

```text
Analyze `/path/to/product-demo.mov` with video-understanding in deep mode.
Give me timestamped findings for the user journey, important visual states,
spoken/audio evidence, on-screen text, bugs or confusing moments, and the final
result. Save Markdown and JSON artifacts.
```

Manual helper:

```bash
python3 skills/video-understanding/analyze_video_gemini.py "/path/to/product-demo.mov" \
  --question "Give timestamped findings for the user journey, important visual states, spoken/audio evidence, on-screen text, bugs or confusing moments, and the final result." \
  --mode deep \
  --output-dir ~/video-understanding
```

## Compare Moments

```text
Use video-understanding on `/path/to/demo.mp4`.
Compare what is visible around 00:15, 01:10, and 02:30.
Explain what changed and cite the evidence from the video.
```

Manual helper:

```bash
python3 skills/video-understanding/analyze_video_gemini.py "/path/to/demo.mp4" \
  --question "Compare what is visible around 00:15, 01:10, and 02:30. Explain what changed and cite evidence." \
  --mode standard \
  --output-dir ~/video-understanding
```

## Privacy Note

The helper deletes the Gemini Files API upload after analysis by default. Add
`--keep-upload` only when you intentionally want the uploaded file to remain
available for debugging, auditing, or follow-up work.
