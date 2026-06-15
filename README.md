# Jay Marketplace

A collection of installable AI-agent skill kits. Each project is packaged as its
own folder with a README, a `skills/` directory, and any project-specific helper
files.

## Projects

| Project | What it is for | Start here |
|---|---|---|
| `yt-automation-kit` | Research, plan, title, thumbnail, and repurpose YouTube videos. | `yt-automation-kit/README.md` |
| `agent-workflow-kit` | Turn broad tasks into goals, parallel subgoals, synthesis, and verification. | `agent-workflow-kit/README.md` |
| `video-understanding-kit` | Analyze local videos with Gemini multimodal models and timestamped answers. | `video-understanding-kit/README.md` |

## How The Repo Is Organized

Each project follows the same basic shape:

```text
project-name/
  README.md
  skills/
    skill-name/
      SKILL.md
```

Some projects also include:

- `requirements-dev.txt` for optional validation dependencies.
- `scripts/validate_skills.py` for checking skill frontmatter.
- Skill-specific scripts or assets when the skill needs them.

## Installing A Skill

Open the README for the project you want, then copy its skill folders into your
agent's skills directory. For Claude Code, that is usually:

```bash
~/.claude/skills/
```

For Codex, copy the skill folder into your configured Codex skills directory and
restart Codex if needed.
