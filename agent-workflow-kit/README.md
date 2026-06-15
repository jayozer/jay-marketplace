# Agent Workflow Kit
**Claude Code and Codex-compatible skills for turning big requests into clear goals, parallel subgoals, and verified results.**

> These are agent workflow skills. They are separate from product-specific kits like the YouTube Automation Kit, so you can reuse them across coding, research, design, and build tasks.

---

## What This Is For

Use this kit when a request is too broad to handle as one unstructured prompt.
It helps the agent create a filled brief, define what done means, split work
into independent subgoals where useful, and synthesize the final result with
verification.

It is not tied to YouTube, video, or any single product workflow.

## Before You Start

- **Claude Code or Codex** — the skill is written to work in either environment.
- **Python 3** — only needed for local validation.
- **PyYAML** — only needed if you want to validate the skills locally: run `pip install -r requirements-dev.txt`.

---

## What's In Here

- `skills/goal-orchestrator` — turn a broad task into a filled brief, a top-level goal, parallel subgoals when useful, synthesized results, and verification.

## Install

For Claude Code:

1. Find or create your skills folder: `~/.claude/skills/`
2. Copy each folder from `skills/` into it, so you have `~/.claude/skills/goal-orchestrator/`
3. Start or restart Claude Code so it picks up the new skill.

For Codex:

1. Copy each folder from `skills/` into your Codex skills folder.
2. Restart Codex if needed so it refreshes available skills.

## How To Use It

Ask in plain English:

- "Write a goal and use parallel agents for this build."
- "Turn this request into a proper goal with subgoals."
- "Fill the build brief, create a top-level goal, and split the work across agents."
- "Use goal orchestration for this task."

## Validate The Skills

From this folder:

```bash
pip install -r requirements-dev.txt
python3 scripts/validate_skills.py
```
