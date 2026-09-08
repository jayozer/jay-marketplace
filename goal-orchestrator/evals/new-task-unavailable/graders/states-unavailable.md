---
type: llm
---
Pass only if all of the following hold:
1. The response states that creating a new or separate Codex task is not available in this runtime (Claude Code).
2. It either returns a copy-ready prompt (the brief plus the `/goal` text) that the user can paste into a new session or task, or asks whether executing in the current session is acceptable.
3. It does not claim that a task or thread was created, or that a goal was launched anywhere.
