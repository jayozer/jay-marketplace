---
name: goal-orchestrator
description: Turn a broad task into a launch-ready fire-and-forget /goal — an airtight, verifiable completion condition with guardrails — then run it autonomously to done; fall back to supervised multi-agent orchestration when a task can't be made verifiable. Use when the user asks to write a goal, use /goal, run something autonomously or fire-and-forget, fill a build brief, spawn parallel agents or subagents, or handle broad work end to end in Claude Code or Codex.
argument-hint: "[the broad task to turn into a /goal]"
user-invocable: true
---

# Goal Orchestrator

Turn a broad request into a **fire-and-forget `/goal`**: one verifiable completion condition the agent works toward autonomously, across turns, until an independent checker confirms it is met. Your job is to make the condition airtight and the run safe — then step back.

`/goal` is a native Claude Code command (v2.1.139+); Codex has no equivalent — there, use supervised orchestration (§7). After each turn a checker model (Haiku by default) reads the transcript and rules *met* / *not-met*; a *not-met* returns its reason as guidance for the next turn. **The checker only sees what the agent wrote in the conversation — it cannot run commands.** A condition is therefore only as good as the evidence it forces the agent to surface. One goal is active at a time; `/goal clear` stops it.

When a task has no verifiable finish line (open-ended, creative, or unsafe to run unsupervised), do not force it into `/goal` — drop to supervised orchestration (§7).

## Platform Adaptation

This skill is written in Claude Code terms; the coding agent already knows which harness it is running in, so take the matching branch.

**Provider API docs — API/SDK goals only.** When the goal builds on the model provider's API or SDK (an agent, an SDK app, tool/function calling, model selection, pricing, caching, or a model/prompt migration), consult the harness-native docs skill *before* writing the condition (§3) so model IDs, API shapes, and limits are grounded rather than guessed. Skip it for goals that don't touch the provider API — test fixes, refactors, UI work.

- **Claude Code** → invoke the `claude-api` skill via the `Skill` tool (Anthropic/Claude model IDs, params, pricing, tool use, MCP, caching, token counting, migration).
- **Codex** → the `openai-docs` skill loads natively; follow it — it drives the `openaiDeveloperDocs` MCP tools and its bundled helper for OpenAI model selection, API reference, and migration.

### Tool Name Translation

The tool names elsewhere in this skill (notably §7) are Claude Code's. In Codex, translate:

| This skill says | Codex equivalent |
| --- | --- |
| `Task` / Agent tool (dispatch a subagent) | `spawn_agent`, then `wait_agent` (needs `multi_agent = true` in `~/.codex/config.toml`) |
| Several parallel `Task` calls | several `spawn_agent` calls (spawn all before calling `wait_agent` — they run concurrently) |
| `TodoWrite` (task tracking) | `update_plan` |
| `Skill` tool (invoke a skill) | skills load natively — just follow the instructions |
| `Read` / `Write` / `Edit` / `Bash` | native file and shell tools |

### Platform Notes

**Claude Code** — `/goal` is native (v2.1.139+); the checker model is Haiku by default. Fire-and-forget needs a trusted workspace and auto-approved tools (see §4).

**Codex** — no `/goal` equivalent: always use supervised orchestration (§7). Subagents need `multi_agent = true` in `~/.codex/config.toml`; skills load natively. Codex has no named agent types (`Explore`, `Plan`, `general-purpose` are Claude Code's) — put the role in each agent's prompt instead:

```text
spawn_agent [read-only research prompt, e.g. "Research auth patterns in this codebase and recommend an approach. Do not implement."]
spawn_agent [implementation prompt, e.g. "Implement the recommended approach. Run npm test and show the results."]
wait_agent
wait_agent
```

## 1. Fill the Brief

Capture the request before writing any condition. Use this universal form:

```text
Build or deliver [OUTCOME] in [CONTEXT, TECH, OR FRAMEWORK].
It should include [CORE DELIVERABLES], with [BEHAVIOR, INTERACTION, WORKFLOW, OR ACCEPTANCE DETAILS].
Make it meet [QUALITY BAR], using [RELEVANT CONSTRAINTS], [ENVIRONMENT OR INTEGRATION DETAILS], and [FINISHING TOUCHES].
Output as [ARTIFACT OR FORMAT].
```

Do not leave bracketed placeholders. Infer conservative defaults from the request and the current project. Ask the user up front only when a missing detail makes the task impossible, destructive, or materially risky — because once `/goal` is running, clarifying questions stall the loop (see §4).

Field meanings:

- `OUTCOME`: the concrete result to produce.
- `CONTEXT, TECH, OR FRAMEWORK`: repo, language, toolchain, platform, or domain.
- `CORE DELIVERABLES`: files, features, analysis, fixes, tests, or decisions needed.
- `BEHAVIOR OR ACCEPTANCE DETAILS`: what must work, how it behaves, edge cases.
- `QUALITY BAR`: correctness, performance, UX, safety, tone, or evidence standard.
- `ENVIRONMENT OR INTEGRATION DETAILS`: APIs, data sources, deploy targets, permissions.
- `ARTIFACT OR FORMAT`: code changes, a file, a report, a PR, a patch, or an answer.

## 2. Is This `/goal`-Shaped?

Fire-and-forget only works when "done" is checkable from the transcript. Confirm all three before continuing; if any fails, go to §7.

- **Verifiable finish line** — done can be proven by a command, exit code, file or count check, or other concrete evidence the agent can print. Not "make it better" or "feels right."
- **Safe unsupervised** — no destructive, production, financial, or credential actions that need a human in the loop; mistakes are recoverable (git, sandbox, test env).
- **Bounded** — the work has a realistic end within a turn/token budget, not an open research rabbit hole.

State your call in one line — e.g. "`/goal`-shaped: yes, verified by `pytest -q` exit 0" — so the choice is explicit.

## 3. Write the Completion Condition

This is the heart of the skill. A strong condition has four parts:

1. **Measurable end state** — the observable result. ("All 3 endpoints return 200 with the documented JSON shape.")
2. **Verification method that forces evidence into the transcript** — exactly how the agent proves it, run and shown every turn. ("Met only after `npm test` is run and its output showing 0 failures appears in this conversation.")
3. **Constraints** — what must stay true or unchanged. ("Do not edit `db/migrations/`. Do not add new dependencies.")
4. **Hard cap** — a turn or time ceiling so a stuck run can't drain tokens. ("Or stop after 40 turns and summarize what's left.")

Template:

```text
/goal [ONE-SENTENCE OBJECTIVE].
Done only when [MEASURABLE END STATE], proven by [VERIFICATION COMMAND/CHECK] with its output shown in this conversation.
Constraints: [WHAT MUST STAY UNCHANGED]; do not ask clarifying questions — make a reasonable choice and note it.
Stop after [N] turns if not met and report what remains.
```

Good vs. bad:

- ✅ "Done only when `ruff check .` and `pytest -q` both exit 0, output shown; don't touch `legacy/`; stop after 30 turns." (checkable, evidence forced, capped)
- ✅ "Turn this screenshot into a working app; met once every feature is tested end-to-end in the browser and the steps are shown." (forces demonstrated evidence)
- ❌ "Make the codebase cleaner / production-ready." (no finish line — loops, burns tokens)
- ❌ "Complete the feature." (checker can be fooled by an unproven 'done')

**Ground it first (API/SDK goals).** If the goal builds on the provider's API or SDK, pull the harness-native docs skill before drafting (see Platform Adaptation) — don't pin model IDs, params, or limits the agent only half-remembers into the condition.

**Keep it tight.** Claude Code hard-caps the `/goal` condition at 4000 characters (≈1000 tokens), and the checker re-reads it every turn — so a bloated condition costs tokens each turn and blurs the met/not-met target. If you brush the cap, detail has leaked in: move it to the brief (§1) and working context, which have no such limit, and keep the `/goal` line to the four parts above.

Show the drafted condition to the user before firing.

## 4. Pre-Flight (Guardrails)

Before launching, set up for unattended execution:

- **Trusted workspace** — `/goal` requires a trusted directory; it is blocked in untrusted repos and when hooks are disabled (`disableAllHooks` / `allowManagedHooksOnly`).
- **Auto-approve tools** — enable auto-accept so permission prompts don't halt the loop, but only once destructive actions are fenced off (below).
- **No clarifying questions** — the condition must tell the agent to decide and note assumptions rather than stop and ask; any pause ends the walk-away.
- **Fence danger** — exclude prod/deploy/secret/irreversible actions in the constraints; prefer a branch, git worktree, or sandbox so mistakes are recoverable.
- **Confirm the cap** — re-check that the turn/time limit from §3 is present.

## 5. Launch and Walk Away

- Fire the condition with `/goal`.
- **Watch the first ~hour** (or first several turns) for stuck or *acknowledgement* loops — the agent reporting progress while the checker never advances. Kill early if you see one.
- `/goal clear` (aliases: `stop`, `off`, `reset`, `none`, `cancel`) halts immediately. `--resume` restores the goal in a later session (the turn counter and token baseline reset).

## 6. On Completion — Verify and Report

When the goal clears, do not take the checker's word as final — it only saw the transcript.

1. **Re-run the real verification yourself** (the §3 command) and read the actual output.
2. Reconcile against the brief and the repo; if the checker passed but the evidence doesn't hold, reopen the work.
3. Report concisely: what was produced, the verification you re-ran and its result, turns or cost if notable, and any remaining risks or assumptions the autonomous run made.

## 7. Fallback: Supervised Orchestration

When §2 said the task is **not** `/goal`-shaped, run it yourself with subagents instead of an autonomous loop. The main agent owns the outcome; subagents research, plan, review, or implement in isolation — they do not replace your judgment.

**Parallelize only when it helps** (speed, quality, coverage); do small or tightly coupled work directly. In Claude Code the subagent mechanism is the `Task`/Agent tool (in Codex, `spawn_agent`/`wait_agent` — see Platform Adaptation) — emit all calls in one message to run them concurrently, match the agent type to the subgoal (`Explore` for read-only research, `Plan` for design, `general-purpose` for build/verify), and isolate parallel writers with git worktrees to avoid edit conflicts. See `superpowers:dispatching-parallel-agents`.

Give each agent a self-contained prompt with its own dedicated subgoal:

```text
[ONE CLEAR SUBGOAL]

Context: [Filled brief + relevant repo, files, constraints, current plan.]
Deliverable: [Specific output: findings, patch, design, tests, risks, recommendation.]
Boundaries: [What this agent owns; what it must not touch or decide.]
Verification: [Checks to run or evidence to collect.]
Return: summary · evidence/file refs · artifact/recommendation · verification done · unknowns/risks.
```

Then synthesize: compare each result against the real repo and brief, verify claims before relying on them, reconcile conflicts (workspace evidence beats agent opinion), apply only what fits, and run the smallest reliable check that proves the outcome. Report the synthesis, not the machinery.
