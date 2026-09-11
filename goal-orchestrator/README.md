# Goal Orchestrator

**Codex-first workflow tools for turning broad requests into safe, measurable goals and verified results.**

> Native Codex `/goal` is the persistence and execution engine. `$goal-orchestrator` is the planner and project manager that prepares work for that engine.

Platform instructions: Codex, Claude Code, and Kimi Code (including Kimi K3). Runtime behavior is verified separately from local parser/package tests.

## What Goal Orchestrator Does

Use Goal Orchestrator when a request needs more structure before long-running execution. It helps Codex:

- inspect the actual workspace before defining the work;
- turn a broad request into an execution-ready brief;
- decide whether the task is verifiable, safe and authorized, and bounded;
- draft a native Codex goal with measurable completion criteria;
- launch the goal only when the user explicitly requests execution;
- coordinate independent subagents during an explicit run when useful; and
- verify the real result before completion.

The skill works across coding, research, documentation, design, and other bounded workflows. It does not grant permissions, publish changes, or make unsafe work autonomous.

## Choose the Smallest Workflow

| Situation | Use |
| --- | --- |
| The outcome, scope, constraints, and verification are already clear | Native `/goal` |
| The request is broad or its finish line still needs definition | `$goal-orchestrator` |
| The task is small, conversational, or open-ended | A normal Codex prompt |
| The work needs production, destructive, credential, financial, or publication approval | Supervised work with explicit approval points |

### Use `/goal` Directly

Use native Goal mode for an already-understood, bounded task:

```text
/goal Fix password-reset token expiration without changing the database schema.

Done when:
- Expired tokens are rejected and valid tokens still work.
- A regression test covers both cases.

Constraints:
- Do not add dependencies, commit, push, or deploy.

Verification:
- Run the focused authentication tests and the full test suite; show each summary line.
- Review the final diff for unrelated changes; show `git diff --stat`.
```

### Use `$goal-orchestrator`

Use the skill when Codex needs to discover what done means:

```text
Use $goal-orchestrator to turn the authentication redesign into an execution-ready brief and native Codex goal. Draft it, but do not start it.
```

To authorize execution, say so explicitly:

```text
Use $goal-orchestrator to prepare and run this work end to end. Use independent subagents only where they materially help, and do not commit or push.
```

That launches in the current task by default. To route the run elsewhere, request a separate task explicitly:

```text
Use $goal-orchestrator to launch this as a new Codex task.
```

For Git projects, the new task starts in a Codex worktree by default. A requested branch/ref or the current working tree is used only when you name that starting state. A new branch is created only when you ask for that exact name. The parent task keeps any existing Goal, and the new task creates and verifies its own Goal.

Selecting the skill by itself uses **draft mode**. It does not create a goal, edit files, or spawn subagents.

## The Goal Artifact

The portable native goal format is:

```text
/goal <specific outcome>

Done when:
- <measurable acceptance criterion>

Constraints:
- <scope, compatibility, approval, or non-goal boundary>

Verification:
- <command and the printed output that proves it, or the observation or review evidence to show>

If blocked:
- <report what was tried and what would unblock progress, then stop>
```

The goal body must be no more than 4,000 characters. Put background detail in the preceding brief or a referenced file. Each verification bullet names the output that proves it. Claude’s evaluator needs that evidence in the conversation; Codex and Kimi also need a reviewable completion record. Use the selected runtime reference for budgets, stops, and user controls. A limit reached is unfinished work.

## Codex Goal Lifecycle

- `/goal` starts or displays a goal.
- `/goal edit` revises the objective.
- `/goal pause` and `/goal resume` control execution.
- `/goal clear` removes the goal.
- One unfinished native goal can be active in a task at a time.

An active Goal blocks another Goal in the same task, not a Goal in a separate task. Goal mode keeps the task's existing sandbox and approval policy. It can still pause for user input, approval, or missing authority. Completing a goal requires real verification; passing tests alone is insufficient when they do not prove the requested behavior.

The bundled [runtime references](skills/goal-orchestrator/SKILL.md#select-the-runtime) carry source links and their last-checked date (2026-09-10). Current host tools and state must still be checked before each launch.

## Delegation Rules

The skill may spawn subagents only during an explicitly requested run. It delegates independent read-heavy work, tests, review, or isolated implementation, then waits and synthesizes the results.

Avoid multiple agents writing to the same checkout. Prefer one implementation owner or separate git worktrees. The main agent remains responsible for validating every result against the actual workspace.

## Contents

- `skills/goal-orchestrator/` — the shared skill, UI metadata, and bundled runtime, artifact, and verification references.
- `examples/goal-templates/` — feature, bug-fix, test, documentation, and refactor goal patterns.
- `examples/brief-templates/` — domain-specific brief prompts.
- `examples/subgoal-patterns/` — decomposition patterns for independent work.
- `scripts/generate_brief.py` — generate a draft metadata scaffold; Git state and actual verification still need discovery.
- `scripts/extract_goal.py` — extract canonical and legacy goal blocks.
- `scripts/benchmark_goals.py` — check goal structure, verification, and character limits.
- `scripts/validate_skills.py` — validate skill metadata and required sections.
- `GUIDE.md` — detailed authoring, lifecycle, delegation, and troubleshooting guidance.
- `evals/` — behavioral acceptance cases for `claude plugin eval` (early access); see `evals/README.md`.

## Install and confirm discovery

Run these copy commands from `goal-orchestrator/` in this checkout. Copy the entire
skill directory so its `references/` and UI metadata travel with it.

| Host/install | Destination | Invoke and check discovery |
| --- | --- | --- |
| Codex personal | `~/.agents/skills/goal-orchestrator` | Skills UI or `/skills`; `$goal-orchestrator` |
| Codex project | `.agents/skills/goal-orchestrator` in the target repo | Same, from the target repo |
| Claude personal | `~/.claude/skills/goal-orchestrator` | Slash-command list; `/goal-orchestrator` |
| Claude project | `.claude/skills/goal-orchestrator` | Same, from the target repo |
| Claude plugin | `/plugin install goal-orchestrator@jay-marketplace` | `/goal-orchestrator:goal-orchestrator` |
| Kimi personal | `~/.agents/skills/goal-orchestrator` or `~/.kimi-code/skills/goal-orchestrator` | New session, `/skill:goal-orchestrator` |
| Kimi project | `.agents/skills/goal-orchestrator` or `.kimi-code/skills/goal-orchestrator` | Same, from the target repo |

Personal installation shared by Codex and Kimi:

```sh
mkdir -p ~/.agents/skills
cp -R skills/goal-orchestrator ~/.agents/skills/
```

For a repository-scoped shared copy:

```sh
mkdir -p /path/to/repo/.agents/skills
cp -R skills/goal-orchestrator /path/to/repo/.agents/skills/
```

For Claude Code:

```sh
mkdir -p ~/.claude/skills
cp -R skills/goal-orchestrator ~/.claude/skills/
```

Existing Codex installations may use `$CODEX_HOME/skills` (normally
`~/.codex/skills`). Kimi's host-specific user directory follows `KIMI_CODE_HOME`.
Use one installed copy per scope to avoid version ambiguity. Check discovery after
copying; restart the host if changes do not appear. The local package check below
verifies a complete copy, but does not prove discovery or Goal activation in each app.

## Platform instructions

Load only the matching reference:

- [Codex](skills/goal-orchestrator/references/codex.md): native tool preflight, active-goal conflicts, current/new-task activation, budgets, and blocked-state rules.
- [Claude Code](skills/goal-orchestrator/references/claude.md): user-command handover, transcript evidence, replacement, hooks/trust, and textual stops.
- [Kimi Code](skills/goal-orchestrator/references/kimi.md): status/pause/resume/cancel/replace/next, queues, prompt-mode outcomes, and skill discovery.

If the runtime or required capabilities are unavailable, return the prepared
artifact and state that it was not launched. Keep the requested destination and
permission mode. For Claude and Kimi, printing `/goal` is a handover; it cannot
establish an active goal. A model name never selects the host adapter.

## Helper commands

Helpers use Python 3.10 or newer and the standard library. `generate_brief.py`
reads README/package metadata only (Python 3.11+ also reads `pyproject.toml`). Its
output labels itself a draft scaffold and includes provenance, unresolved
decisions, acceptance-to-evidence mapping, and iteration/stopping records.

```sh
python3 scripts/generate_brief.py /path/to/project --task "Implement password reset"
python3 scripts/extract_goal.py /path/to/goal.md
python3 scripts/extract_goal.py /path/to/kimi-history.md --runtime kimi
python3 scripts/benchmark_goals.py examples/goal-templates --mode template
python3 scripts/benchmark_goals.py /path/to/goal.md --mode readiness
```

Extraction preserves `raw_goal`, its source span and character count, and the
source excerpt around a rejected block. Unsupported formatting produces a
location diagnostic and nonzero exit. `--runtime` selects Codex (default), Claude,
or Kimi lifecycle filtering; extraction does not launch or manage goals.

To run a check, declare it explicitly in a `Verification:` bullet:

```text
- Command: {"command": "python3 -m unittest discover -s tests", "cwd": ".", "expected_exit": 0, "evidence": "show the unittest summary"}
- File: Inspect `setup.sh`; cite the relevant lines without running it.
- Manual: Compare the rendered page with the approved screenshot and record differences.
```

See the [record schema and verdicts](skills/goal-orchestrator/references/verification.md)
and [complete example](examples/verification-goal.md). All records are required.
Commands execute exactly as written, subject to current authorization. Relative
working directories resolve from the goal file, or from the explicit `--cwd`
base. The full source/command/directory plan is printed before execution.

```sh
# Preview only, exit 3 while executable/manual evidence is pending.
python3 scripts/benchmark_goals.py /path/to/goal.md --test-commands --cwd /path/to/project

# Run only explicit records after readiness checks pass.
python3 scripts/benchmark_goals.py /path/to/goal.md --test-commands --yes --cwd /path/to/project --timeout 30
```

Legacy prose extraction is retained as `legacy_command_suggestions` for migration.
It never supplies executable checks, even with `--yes`. Backticked file names and
prose such as "shows" or "passes" cannot authorize execution. Convert only intended
commands to records, preserving the command and working directory; mark inspections
and human criteria separately.

| Result | Exit | Meaning |
| --- | --- | --- |
| `STRUCTURE_ONLY` | 0 | Template lint passed; no commands ran |
| `READY` | 0 | Detected placeholders/decisions resolved; verification remains unrun |
| `PASS` | 0 | Explicit executable checks passed, no pending manual evidence |
| `FAIL` | 1 | Input, structure, readiness, or executable checks failed |
| `NO_GOALS` | 2 | Nothing to benchmark |
| `PENDING` / `MANUAL` | 3 | Executable or human evidence remains outstanding |
| `EMPTY_ALLOWED` | 0 | Empty input explicitly accepted with `--allow-empty` |

`--strict` aliases readiness mode. `--test-commands` always requires readiness and
cannot be combined with template mode. A nonzero expected status is accepted only
when declared; missing executables, timeout, and launch failures still fail. A
readiness or template success never proves goal completion. Human evidence is
recorded by the coordinator outside this helper; it is never silently dismissed.

## Validate Goal Orchestrator

Only the metadata/content validator needs PyYAML. Use an isolated environment;
these checks do not invoke paid models or launch native goals:

```sh
uv run --with pyyaml python scripts/validate_skills.py --check-content
bash scripts/smoke_test.sh
```

Alternatively, install `requirements-dev.txt` into a virtual environment. The smoke
suite uses `uv --with pyyaml` if the active Python lacks PyYAML. It checks unit
regressions, explicit execution and failure verdicts, template structure, lifecycle
filtering, and a standalone copy's bundled links.

[Behavioral acceptance cases](evals/README.md) cover simulated host decisions and
optional Claude model-backed evals. Local and simulated checks are separate from
host discovery, real Codex/Claude/Kimi launches, and model success-rate evidence.
See [GUIDE.md](GUIDE.md) for workflow examples.
