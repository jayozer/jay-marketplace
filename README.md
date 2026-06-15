# Jay Marketplace

A Claude Code **plugin marketplace** of installable AI-agent skill kits. Add the
marketplace once, then pick which kits to install — globally or per-repo.

## Projects (plugins)

| Plugin | What it is for | Skills | Start here |
|---|---|---|---|
| `agent-workflow-kit` | Turn broad tasks into goals, parallel subgoals, synthesis, and verification. | `goal-orchestrator` | `agent-workflow-kit/README.md` |
| `yt-automation-kit` | Research, plan, title/SEO, thumbnail, and repurpose YouTube videos. | `yt-search`, `yt`, `seo`, `thumbnail`, `repurpose` | `yt-automation-kit/README.md` |
| `video-understanding-kit` | Analyze local videos with Gemini multimodal models and timestamped answers. | `video-understanding` | `video-understanding-kit/README.md` |

## Install via the marketplace (recommended)

In Claude Code:

```text
# 1. Add this marketplace (once per machine)
/plugin marketplace add jayozer/jay-marketplace

# 2. Browse and install interactively...
/plugin

# ...or install a specific kit directly
/plugin install agent-workflow-kit@jay-marketplace
/plugin install yt-automation-kit@jay-marketplace
/plugin install video-understanding-kit@jay-marketplace
```

Equivalent non-interactive CLI:

```bash
claude plugin marketplace add jayozer/jay-marketplace
claude plugin install yt-automation-kit@jay-marketplace
```

### Choosing where a kit installs

When installing through the `/plugin` menu you pick a **scope**:

- **User** — available in every project on your machine (good for general tools
  like `agent-workflow-kit`).
- **Project** — recorded in the repo's `.claude/settings.json` and committed, so
  teammates who trust the workspace get prompted to install it too.
- **Local** — recorded in `.claude/settings.local.json` (gitignored); a personal,
  repo-scoped choice that is not shared.

To wire a kit into *another repo* for your whole team, install it at **Project**
scope from inside that repo, then commit the resulting `.claude/settings.json`.

### Update / remove

```text
/plugin marketplace update jay-marketplace   # pull the latest kits
/plugin uninstall yt-automation-kit@jay-marketplace
```

## Manual install (no marketplace)

Each kit still works the old way — copy its skill folders into your skills dir:

```bash
# Example: just the YouTube kit
cp -R yt-automation-kit/skills/* ~/.claude/skills/
```

Bundled scripts are referenced with `${CLAUDE_SKILL_DIR}` (the directory holding
the skill's `SKILL.md`), which Claude Code resolves correctly for **personal,
project, and plugin** installs — so the **same SKILL.md works under both the
marketplace install and this manual copy** with no edits.

For Codex, copy the skill folder into your configured Codex skills directory and
restart Codex if needed.

## How the repo is organized

```text
.claude-plugin/
  marketplace.json          # lists every plugin + where it lives

<kit>/                      # one plugin per kit
  .claude-plugin/
    plugin.json             # plugin manifest (name, version, metadata)
  README.md
  skills/
    <skill-name>/
      SKILL.md              # auto-discovered; frontmatter name + description
      <helper scripts>      # optional, referenced via ${CLAUDE_SKILL_DIR}
```

`skills/` is auto-discovered — a plugin does not list its skills in `plugin.json`.
Drop a new `skills/<name>/SKILL.md` into a kit and it ships on the next update.

Some kits also include `requirements-dev.txt` and `scripts/validate_skills.py`
for validating skill frontmatter locally.

## Validate before publishing

```bash
claude plugin validate .                       # marketplace.json
claude plugin validate ./agent-workflow-kit    # an individual plugin
```
