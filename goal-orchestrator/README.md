# Goal Orchestrator

**Codex-first workflow tools for turning broad requests into safe, measurable goals and verified results.**

> Native Codex `/goal` is the persistence and execution engine. `$goal-orchestrator` is the planner and project manager that prepares work for that engine.

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
- Run the focused authentication tests and the full test suite.
- Review the final diff for unrelated changes.
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

For Git projects, the new task starts in a Codex worktree by default. A requested branch/ref or the current working tree is used only when you name that starting state. The parent task keeps any existing Goal, and the new task creates and verifies its own Goal.

Selecting the skill by itself uses **draft mode**. It does not create a goal, edit files, or spawn subagents.

## The Goal Artifact

The canonical Codex goal format is:

```text
/goal <specific outcome>

Done when:
- <measurable acceptance criterion>

Constraints:
- <scope, compatibility, approval, or non-goal boundary>

Verification:
- <command, observation, or review criterion proving completion>
```

The goal body must be no more than 4,000 characters. Put background detail in the preceding brief or a referenced file. A textual turn cap is not required. Supply a native token budget only when the user explicitly asks for one.

## Codex Goal Lifecycle

- `/goal` starts or displays a goal.
- `/goal edit` revises the objective.
- `/goal pause` and `/goal resume` control execution.
- `/goal clear` removes the goal.
- One unfinished native goal can be active in a task at a time.

An active Goal blocks another Goal in the same task, not a Goal in a separate task. Goal mode keeps the task's existing sandbox and approval policy. It can still pause for user input, approval, or missing authority. Completing a goal requires real verification; passing tests alone is insufficient when they do not prove the requested behavior.

## Delegation Rules

The skill may spawn subagents only during an explicitly requested run. It delegates independent read-heavy work, tests, review, or isolated implementation, then waits and synthesizes the results.

Avoid multiple agents writing to the same checkout. Prefer one implementation owner or separate git worktrees. The main agent remains responsible for validating every result against the actual workspace.

## Contents

- `skills/goal-orchestrator/` — the Codex-first skill and UI metadata.
- `examples/goal-templates/` — feature, bug-fix, test, documentation, and refactor goal patterns.
- `examples/brief-templates/` — domain-specific brief prompts.
- `examples/subgoal-patterns/` — decomposition patterns for independent work.
- `scripts/generate_brief.py` — generate a structured brief from local project context.
- `scripts/extract_goal.py` — extract canonical and legacy goal blocks.
- `scripts/benchmark_goals.py` — check goal structure, verification, and character limits.
- `scripts/validate_skills.py` — validate skill metadata and required sections.
- `GUIDE.md` — detailed authoring, lifecycle, delegation, and troubleshooting guidance.

## Install for Codex

Codex discovers personal skills from its configured skills directory. This checkout is currently compatible with `$CODEX_HOME/skills` (normally `~/.codex/skills`):

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/goal-orchestrator "${CODEX_HOME:-$HOME/.codex}/skills/"
```

For a repository-scoped skill shared with the project:

```bash
mkdir -p /path/to/repo/.agents/skills
cp -R skills/goal-orchestrator /path/to/repo/.agents/skills/
```

Current Codex releases also discover user-level skills under `~/.agents/skills`. Use the Skills UI, `/skills`, or a `$goal-orchestrator` mention to confirm discovery. Codex normally detects skill changes automatically; restart it if an update does not appear.

## Claude Code Compatibility

The skill retains a small Claude Code compatibility layer for the shared brief, safety, delegation, and verification workflow. Use current Claude Code documentation for its native goal and agent controls; do not project Codex lifecycle details onto Claude Code.

Manual Claude Code installation remains:

```bash
mkdir -p ~/.claude/skills
cp -R skills/goal-orchestrator ~/.claude/skills/
```

## Helper Commands

Generate a brief:

```bash
python3 scripts/generate_brief.py /path/to/project --task "Implement password reset"
```

Extract goals:

```bash
python3 scripts/extract_goal.py examples/goal-templates
python3 scripts/extract_goal.py /path/to/goal.md
```

Benchmark goals without running their verification commands:

```bash
python3 scripts/benchmark_goals.py examples/goal-templates
```

Running extracted commands is opt-in and executes shell content from the input:

```bash
python3 scripts/benchmark_goals.py goal.md --test-commands --cwd /path/to/project
```

## Validate Goal Orchestrator

From `goal-orchestrator/`:

```bash
pip install -r requirements-dev.txt
python3 scripts/validate_skills.py
python3 scripts/validate_skills.py --check-content
bash scripts/smoke_test.sh
```

See [GUIDE.md](GUIDE.md) for detailed goal authoring, approval boundaries, delegation patterns, and troubleshooting.
