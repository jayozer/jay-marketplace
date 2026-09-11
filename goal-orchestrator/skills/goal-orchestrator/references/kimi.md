# Kimi Code runtime

Read this only in Kimi Code, including when Kimi K3 is selected. Kimi Chat and a Kimi model in another app do not imply Kimi Code controls. Last checked: 2026-09-10 against the official pages below. Live model launches and host discovery are separate acceptance checks.

## Launch preflight

Check the app identity, permission/Plan mode, current goal state, and actual tools. Do not invent Codex Goal tools. The documented interface is the user's `/goal` command. Without a callable launch/status interface, return the complete command as a handover with state "not launched: user command required". Request `/goal status` only if current state is unknown; preserve an unfinished goal and obtain direction before replacement.

When execution is already authorized, prepare that handover without another generic approval request. If an exposed tool can launch goals, read its current schema, preserve prior work, and inspect the matching objective after creation before reporting active state. A requested new Codex task requires another host; return a copy-ready prompt instead of pretending to create it.

## User controls

| Command | Effect |
| --- | --- |
| `/goal <objective>` | Start work toward the objective |
| `/goal` or `/goal status` | Inspect goal state and progress |
| `/goal pause` | Retain and pause current work |
| `/goal resume` | Continue a paused or blocked goal |
| `/goal cancel` | Remove the current goal |
| `/goal replace <objective>` | Explicitly replace the saved objective |
| `/goal next <objective>` | Queue work; starts immediately if no goal is active |
| `/goal next manage` | Manage queued goals in the TUI |

The lowercase first word selects a lifecycle command. Use `/goal -- <objective>` when that word belongs to the objective. The parser's `--runtime kimi` excludes `status`, `replace`, and `next` forms from goal extraction; it is not a queue editor. Only creation works in prompt mode; management commands are TUI controls. Prompt-mode exits distinguish completion (`0`), blocking (`3`), and pausing (`6`). See [Kimi slash commands](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/slash-commands.html).

For an explicitly requested headless handover, put the exact creation block in `goal.md` and provide `kimi -p "$(cat ./goal.md)"`. Do not inline goal text containing backticks in a double-quoted shell command. Running a CLI is additional model execution; printing this instruction is not activation evidence.

## Stops, evidence, and queues

Objectives have a 4,000-character limit. Put stop conditions in the objective; do not invent a `/goal` stop-limit flag or apply Codex's three-turn blocked rule. Interruption, session restoration, and runtime errors can pause work. A blocked or paused result is unfinished work, even if a local test passed.

Queued objectives are hidden from the working agent until the current goal completes. Paused, canceled, or blocked goals do not advance the queue. Never use `next` merely to store a draft: without an active goal it runs immediately. Keep permissions unchanged. See [Kimi Goals](https://www.kimi.com/code/docs/en/kimi-code-cli/guides/goals.html).

## Discovery and delegation

Copy the complete skill folder into `~/.agents/skills` or `.agents/skills`. Host-specific locations are `~/.kimi-code/skills` (or `$KIMI_CODE_HOME/skills`) and `.kimi-code/skills`. Invoke `/skill:goal-orchestrator` and check the command list in a new session. See [Kimi skills](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html).

Use the available `Agent` tool for authorized independent work; inspect its schema and profile allowlist. Its `prompt` must include a self-contained task and its `description` should identify the work. Do not turn on swarm mode or change models as a side effect of choosing this skill. Collect required final handoffs, inspect artifacts and verification results, then report the main goal's evidence separately. See [Kimi tools](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/tools.html) and [agent configuration](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/agents.html).
