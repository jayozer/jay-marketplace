# Claude Code runtime

Read this only in Claude Code. Last checked: 2026-09-10 against the official pages linked below. Capability checks still depend on the installed host.

## Launch and status

**Launch is a handover, never an action through a Codex tool.** Claude Code has no documented model-callable Goal tool. In explicit run mode, return the exact `/goal` block for the user to submit. Never report a goal as created, active, or launched from merely printing it. If current goal state is not already available in context, request the result of `/goal` before offering immediate launch; preserve any unfinished condition. Once that information or replacement authorization is already known, do not ask again.

**Permission mode is unchanged by a goal.** Explain that unattended work needs commands allowed under the user's chosen policy. Keep that policy; do not enable auto mode or bypass approvals. If workspace trust or hook policy disables goals, preserve the draft and report the command's diagnostic rather than changing configuration.

For a requested headless handover, save the exact block to `goal.md` and provide:

```sh
claude -p "$(cat ./goal.md)"
```

This reads the file as data without evaluating its backticks or dollar expressions in the outer shell. Executing this command starts a model run and needs the user's authorization; writing or displaying it is only preparation. Report the observed verdict and output if such a run is authorized. Never infer completion from a successful process launch.

## Runtime differences

- A new condition replaces the session's current goal. `/goal` displays state; `/goal clear` removes it. Do not import Codex edit/pause/resume controls.
- The condition is limited to 4,000 characters. Offer an optional turn or time clause, such as `or stop after N turns`; there is no Codex `token_budget` argument to apply.
- A separate evaluator assesses conversation evidence without inspecting files or executing checks itself. Surface decisive outputs before claiming success.
- The evaluator can continue, record success, or record impossibility. A cap or impossible condition is an unsuccessful stop under this skill's completion rule.
- Wait for required subagents and background commands; evaluation is deferred while they run.
- There is no Codex `blocked` tool status. Persistent lack of progress can stop the loop while keeping the condition.
- **A run can end without a verdict.** Certain unrecoverable errors clear the condition. Session resume can restore active work but resets its turn count, timer, and spend baseline. Report observed state and retain the stopping record before proposing a restart.

These behavior differences come from the [Claude Goal documentation](https://code.claude.com/docs/en/goal). Use its current requirements and diagnostic when the installed version differs.

## Discovery and delegation

Use `/goal-orchestrator:goal-orchestrator` after installing the `goal-orchestrator` plugin, or `/goal-orchestrator` for a copy at `~/.claude/skills/goal-orchestrator`. Project copies use `.claude/skills/goal-orchestrator`. Confirm discovery in the slash-command list. See [Claude skills](https://code.claude.com/docs/en/skills).

Discover the host's actual subagent tool and available profiles. Give a subagent only the tools and context its work needs, wait for its final result, and independently inspect its evidence. A subagent is not a separately launched native Goal. A requested new Codex task is unavailable here: provide a destination prompt or request direction, without silently changing the destination. See [Claude subagents](https://code.claude.com/docs/en/sub-agents).
