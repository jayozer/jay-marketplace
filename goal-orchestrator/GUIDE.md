# Goal Orchestrator Guide

This guide explains how to turn broad work into safe, measurable native goals. The shared operational rules live in [the skill](skills/goal-orchestrator/SKILL.md); the bundled runtime references adapt them to Codex, Claude Code, or Kimi Code.

## Contents

Start with these practical sections:

- [How to use the skill in Codex](#how-to-use-the-skill-in-codex)
- [Guided or Autonomous](#guided-or-autonomous)
- [Switch routes during a conversation](#switch-routes-during-a-conversation)
- [A complete draft-to-run example](#a-complete-draft-to-run-example)
- [Native Goal controls](#skill-invocation-and-native-goal-controls)
- [Optional terminal helpers](#optional-terminal-helpers)

1. [The Two-Layer Model](#the-two-layer-model)
2. [Build an Execution-Ready Brief](#build-an-execution-ready-brief)
3. [Decide Whether Work Is Goal-Shaped](#decide-whether-work-is-goal-shaped)
4. [Write the Goal](#write-the-goal)
5. [Launch and Lifecycle](#launch-and-lifecycle)
6. [Delegate Independent Work](#delegate-independent-work)
7. [Verify Completion](#verify-completion)
8. [Troubleshooting](#troubleshooting)
9. [Select the host before launch](#select-the-host-before-launch)
10. [Preserve provenance and iteration evidence](#preserve-provenance-and-iteration-evidence)
11. [Use explicit executable checks](#use-explicit-executable-checks)
12. [Acceptance evidence](#acceptance-evidence)

## How to use the skill in Codex

Invoke the skill by including `$goal-orchestrator` in your message. It turns a broad request into a clear objective, bounded work, and concrete evidence of completion. It defaults to **Guided + draft**: it inspects the workspace, asks about consequential unresolved decisions, and proposes the work without starting implementation or launching a native Goal.

### Guided or Autonomous

Choose how decisions are made separately from when execution starts:

| | Guided (default) | Autonomous |
| --- | --- | --- |
| Best for | Architecture, product direction, and significant tradeoffs | Outcomes where you want the agent to choose implementation details |
| First step | Inspect the workspace and existing decisions | Same |
| Questions | Ask about consequential unresolved choices, with recommendations where supported | Ask when missing information or authority prevents responsible progress |
| Decisions | Resolve material choices with you; skip questions already answered | Choose reasonable defaults within scope and record consequential assumptions |
| Launch | Only when execution is requested | Only when execution is requested |

In Guided, the agent should ask a small number of useful questions after inspection. These might cover the user outcome, extending the existing architecture versus a redesign, speed/cost/simplicity tradeoffs, required compatibility, or evidence of success. It should explain the tradeoff and recommend an answer where the workspace supports one. A fully defined task does not need an interview.

For example: "The existing storage layer supports this feature with a small extension. I recommend keeping it. A replacement would support offline synchronization but substantially expand the work. Is offline synchronization required for this release?"

In Autonomous, the agent chooses implementation details within your boundaries and records consequential assumptions. The route does not grant permission for new product scope, commits, publishing, deployment, or other external actions. Required decisions remain unresolved until answered; optional preferences can use a stated default after a reasonable opportunity to respond. Independent authorized work can continue while input is pending.

Use these copy-ready prompts:

```text
$goal-orchestrator Guided:
Help me define this feature. Inspect the project, then ask about
architecture and product decisions before drafting the goal.
```

```text
$goal-orchestrator Autonomous:
Define and run a goal for this feature. Choose implementation details
that fit the existing architecture. Preserve public APIs.
Do not commit, push, or deploy.
```

The labels are ordinary prompt conventions, not new slash commands. "Autonomous: draft a goal" delegates planning choices but stays in draft mode. "Guided: resolve the architecture questions, then run it" authorizes launch once the required decisions are settled, without another approval of unchanged scope. Plan mode still prevents execution in either route.

### Switch routes during a conversation

```text
Let's discuss the storage decision before continuing.
```

This switches to Guided for that decision and holds dependent work. It does not silently pause, edit, clear, or replace a native Goal.

```text
Those decisions are settled. Run autonomously from here.
```

This selects Autonomous and authorizes execution. If the Goal is already active, the agent continues it. Agreed decisions, scope, destination, and budgets carry forward. Saying only "choose the remaining details yourself" changes the route but does not authorize launching a draft.

### Choose what happens next

There are no separate skill subcommands such as `$goal-orchestrator run`. Express the mode in ordinary language:

| What you want | Example message |
| --- | --- |
| Explore and draft | `$goal-orchestrator Draft a goal for improving onboarding reliability.` |
| Refine a proposal | `$goal-orchestrator Refine this goal with measurable completion criteria.` |
| Define and start work | `$goal-orchestrator Define and run a goal to fix the failing onboarding tests.` |
| Start an already drafted goal | `Run this goal now in the current task.` |
| Use a separate task | `$goal-orchestrator Define and run this in a new Codex task.` |
| Apply a native token budget | `Run the approved goal with a 50,000-token budget.` |

Execution stays in the current task unless you explicitly request a separate task. A token budget is applied only when requested; reaching the limit does not count as completion. In Plan mode, the skill remains in draft mode.

### A complete draft-to-run example

Start with a request that describes the result and boundaries:

```text
$goal-orchestrator

Draft a goal to improve parser reliability in this repository.

Inspect the current implementation and tests first.
Focus on malformed input and ambiguous command extraction.
Preserve supported syntax and existing uncommitted work.
Include the exact checks that would establish success.
Do not start implementation yet.
```

The skill should return:

1. A grounded brief with **Outcome, Context, Output, Boundaries, and Verification**.
2. A decision on whether the work is verifiable, authorized, and bounded, with any unresolved decisions visible.
3. Proposed `/goal` text with acceptance criteria, constraints, verification, and a blocked-work report requirement.

You can refine that proposal conversationally:

```text
Narrow this to malformed input handling. Keep supported syntax unchanged,
and include regression evidence for both rejected and accepted inputs.
```

When the scope is right, launch it:

```text
Run the proposed goal now in this task. Do not commit or push.
```

Existing authorization carries forward. The agent asks again only for missing decisions or authority, rather than requesting approval of unchanged scope. If you want commits, pushes, PR creation, or deployment included, explicitly include those actions in the request.

You can state your coordination preference in the same message:

```text
Use subagents for independent review and test analysis where useful.
```

Or:

```text
Run this goal with one agent.
```

### Skill invocation and native Goal controls

`$goal-orchestrator` prepares the work and coordinates an explicitly requested run. The following commands belong to Codex's native Goal feature:

| Command | Purpose |
| --- | --- |
| `/goal <objective>` | Start a goal directly when its outcome and checks are already precise |
| `/goal` | View or access the task's goal |
| `/goal edit` | Revise the objective |
| `/goal pause` | Pause goal work |
| `/goal resume` | Resume goal work |
| `/goal clear` | Remove the goal |

Before an orchestrated launch, the agent checks existing Goal state and preserves unfinished work. After creation, it reads the state back to confirm the correct objective and any requested budget are active. Proposed goal text or a newly created task alone is not activation evidence. See [Launch and Lifecycle](#launch-and-lifecycle) for conflict handling and separate-task behavior.

### What to expect during a run

The agent records meaningful attempts: what changed, what the evidence showed, what remains uncertain, and what useful step comes next. It adapts its approach without weakening the acceptance criteria and continues independent authorized work while a decision is pending.

Completion requires evidence for the full objective. Tests establish only the behavior they cover; required manual review remains pending until the observation is recorded. An unsuccessful stop should identify completed work, unmet criteria, attempts, the blocker, preserved artifacts, and the next step. Goal mode keeps the existing permissions and approval policy.

## The Two-Layer Model

Native Codex Goal mode and `goal-orchestrator` solve different problems:

- **Native `/goal`** keeps a persistent target attached to the task and continues working toward it.
- **`$goal-orchestrator`** discovers the real outcome, constraints, approval points, and proof needed before execution.

Use `/goal` directly when the objective is already precise. Use `$goal-orchestrator` when words such as "production-ready," "reliable," "redesign," or "handle this end to end" still need to be grounded in the current workspace.

The skill defaults to Guided + draft. Guided/Autonomous determines how decisions are made; draft/run determines whether execution is authorized. Only explicit language such as "start it," "run it," "execute this goal," or "handle it end to end now" authorizes native goal creation and execution, subject to the host's controls.

## Build an Execution-Ready Brief

Inspect before asking. Read applicable `AGENTS.md`, relevant code and docs, current git state, and existing goal state. Questions should resolve product intent, authority, or a material tradeoff—not facts the workspace can answer.

Use five fields:

```text
Outcome: The observable result.
Context: The repo, system, current behavior, and relevant sources.
Output: The code, report, artifact, or user-facing result.
Boundaries: Scope, compatibility, approval limits, and non-goals.
Verification: Tests, observations, measurements, and review criteria.
```

Record the selected route and draft/run mode alongside the brief. Distinguish required decisions from optional preferences; retain settled choices, rationale, and whether the user selected them or the agent assumed them. This keeps follow-up questions and route changes from reopening resolved decisions. The [brief and evidence record](skills/goal-orchestrator/references/artifacts.md) provides the supporting fields.

### Strong boundaries

- Preserve pre-existing dirty changes.
- Do not modify migration files.
- Keep the public API backward compatible.
- Do not add dependencies.
- Do not commit, push, open a pull request, deploy, or send messages.

Avoid vague boundaries such as "be careful" or "do not break anything."

## Decide Whether Work Is Goal-Shaped

Require three properties.

### Verifiable

The finish line must produce observable evidence. Prefer a combination of:

- focused regression tests;
- the relevant broader suite;
- builds, type checks, or linters;
- exact file, count, schema, or output checks;
- browser or device behavior when user-visible interaction matters; and
- final diff review against the request.

Do not claim that a green suite proves behavior the suite never exercises.

### Safe and authorized

Goal mode does not broaden the sandbox, network, connector, credential, or publication authority. Exclude—or preserve approval points for—production deployment, destructive data changes, purchases, secret use, external messages, commits, pushes, merges, and pull requests unless the user explicitly included them.

### Bounded

The result needs a realistic end state. Open-ended research, subjective creative exploration, and "make it better" are not native-goal objectives until the orchestrator turns them into measurable work.

State the decision explicitly:

```text
Goal-shaped: yes — verifiable with the focused regression, full suite, browser check, and final diff review; checks have not run yet.
```

If any property is missing, stay supervised. The orchestrator can still produce a plan or perform explicitly authorized work without pretending the task is autonomous.

## Write the Goal

Use this format:

```text
/goal <specific outcome>

Done when:
- <measurable acceptance criterion>
- <measurable acceptance criterion>

Constraints:
- <scope, compatibility, approval, or non-goal boundary>

Verification:
- Command: {"command": "<focused command>", "cwd": "<project directory>", "expected_exit": 0, "evidence": "show the test summary"}
- Command: {"command": "<broader command>", "cwd": "<project directory>", "expected_exit": 0, "evidence": "show the test summary"}
- Manual: Review the final diff for unrelated changes and record the result.

If blocked:
- <report attempts, unmet criteria, and what would unblock progress; follow the host's stopping rules>
```

The goal body becomes the execution prompt and completion criteria. Keep it at or below 4,000 characters. Move background detail into the brief or a referenced file.

Replace all placeholders before launch. Native goals also accept prose verification criteria; explicit `Command:` records are required only for execution by the optional repository helper described below.

Each verification bullet names the output that proves it. Claude’s native evaluator judges conversation evidence. In every host, report the decisive output or observation so completion can be reviewed.

### Good objective

```text
/goal Reject expired password-reset tokens while preserving valid-token behavior and the existing database schema.
```

### Weak objective

```text
/goal Improve authentication.
```

### Verification without a shell command

Commands are not the only valid proof. Documentation, design, research, and UX work can use measurable review criteria:

```text
Verification:
- Every recommendation cites one of the supplied sources.
- The final comparison covers cost, migration risk, and operational tradeoffs.
- Conflicting or missing evidence is identified explicitly.
```

### Budgets

In Codex, do not insert a conventional turn limit into every goal; pass the native token budget only when the user explicitly requests one. In Claude Code, offer an optional turn or time clause; do not claim that a Codex token budget was applied. In Kimi Code, put stop conditions in the objective and keep queue controls separate. A budget or cap limits a run; reaching it is an unsuccessful stop, not completion.

## Launch and Lifecycle

Before an explicit launch:

1. Show the proposed goal as part of the launch record. Carry existing execution authorization forward; ask again only for missing decisions or authority.
2. Choose the launch destination.
3. Inspect the relevant goal state and preserve unfinished work.
4. Confirm the workspace, dirty tree, verification commands, and approval points.
5. Start the goal without changing sandbox or approval settings.

After launch or handover, report a launch record: the runtime (Codex, Claude Code, or Kimi Code) and available capabilities, workspace (repository path, branch, commit, and relevant existing changes), destination (current task, new Codex task with its real identifier, or user handover), goal state with the observation that establishes it, and budget or textual stop condition. State whether a requested limit was actually applied. In Codex, matching post-creation `get_goal` state establishes activation; a displayed command in any host is only a handover.

### Launch in the current task

This is the default destination when the user says only "start," "run," or "execute." In Codex, confirm that `get_goal`, `create_goal`, and `update_goal` are available, then inspect the current task with `get_goal`. If an unfinished Goal already exists, preserve it; continue it when the user requests continuation of that same Goal, or surface a conflict before launching different work. Otherwise call `create_goal` here and verify the stored objective and requested budget with `get_goal`. If required tools are unavailable, return the exact goal text with state "not launched: unavailable tools." Claude Code and Kimi Code follow their own launch/handover references.

### Launch in a new Codex task

Use this route only when the user explicitly asks for a new, separate, parallel, or background task. An unfinished Goal in the parent task is preserved and disclosed, but it does not prevent a different Goal in the new task.

1. Do not call `create_goal` in the parent task.
2. Discover the matching saved project with `list_projects` before calling `create_thread`.
3. If the saved project is a Git repository, create a Codex worktree by default. Use the saved project directly only for a non-Git project or when the user explicitly requests it.
4. Omit worktree `startingState` unless the user explicitly asks to start from a particular existing branch/ref, include the current working tree, or create a new branch with the exact name they gave via `onMissing: "create-branch"`. Never invent a branch name.
5. Send the complete brief and Goal text in the new task's prompt, plus this guard:

   ```text
   You are already the destination task created by Goal Orchestrator.
   Launch the native Goal in this task. Do not create another task.
   ```

6. Tell the destination to inspect its own Goal state, call `create_goal`, inspect again, and report that the Goal is active.
7. Treat `create_thread` as asynchronous. A temporary `clientThreadId` is not a usable `threadId`; wait for the real task identifiers, then use `wait_threads` or `read_thread` to inspect activation evidence. Read outputs when needed to confirm the destination's post-creation `get_goal` result matches the objective and budget; an unsupported active claim is insufficient.
8. Open the new task in the Codex UI only when the user asks to see it.

If task creation is unavailable, provide the complete prompt for the user to paste into a new task or ask whether launching in the current task is acceptable. Never change destinations silently.

Codex provides these user controls:

- `/goal` — start or view the task goal;
- `/goal edit` — revise its objective;
- `/goal pause` — pause work;
- `/goal resume` — resume work; and
- `/goal clear` — remove it.

The agent should not silently invoke those lifecycle controls. New authority, irreversible actions, or material product decisions still require the user.

The [Codex reference](skills/goal-orchestrator/references/codex.md) records the native tool contract and current sources. The three-turn blocked rule and native budget argument belong to Codex, not to Claude or Kimi. Each runtime reference carries a last-checked date; inspect actual capabilities before launch.

## Delegate Independent Work

Delegation is available only during an explicitly requested run. Use it when independent work materially improves speed, quality, or coverage.

Good subagent work includes:

- read-only codebase exploration;
- isolated test or log analysis;
- independent review dimensions;
- research over separate source sets; and
- implementation in non-overlapping files or isolated worktrees.

Avoid delegation for a tiny edit, a tightly coupled decision, or multiple writers in the same checkout.

Give each subagent:

```text
Objective: [one independent result]
Context: [brief, relevant files, and current state]
Boundaries: [owned area and forbidden actions]
Verification: [checks or evidence to collect]
Return: [summary, evidence/file refs, result, verification, risks]
```

Spawn independent agents before waiting. The main agent must wait for required results, compare them with the real workspace, reconcile disagreements, and run final verification itself.

## Verify Completion

Completion is an evidence decision, not a progress report.

Before marking a goal complete:

1. Re-run the real checks and inspect their output.
2. Confirm the requested behavior and artifacts.
3. Review the final diff for scope and regressions.
4. Distinguish passed, failed, blocked, and skipped checks.
5. Report assumptions and remaining risks.

Mark a native goal complete only when the entire objective is achieved and no required work remains.

In Codex, mark it blocked only after the same blocking condition has persisted for at least three consecutive goal turns and no meaningful in-scope progress remains. If a blocked goal is resumed, begin a fresh blocked audit. Difficulty, uncertainty, incomplete work, or a nearly exhausted budget are not blocking verdicts by themselves.

For a budgeted Codex goal, report the final token usage returned by the goal tool after successful completion.

## Troubleshooting

### The goal is vague

Return to the brief. Replace activities such as "improve" or "review" with an observable result, boundaries, and proof.

### Verification passes but the feature is wrong

The check is too weak. Add direct behavior, artifact, or UI evidence and a final diff review. Do not weaken the objective to match an incomplete test suite.

### The run needs a new decision

Hold work that depends on a required decision and ask; continue independent authorized work. Record whether the question is required or an optional preference. Autonomous can choose reasonable implementation defaults, but "do not ask questions" cannot supply missing authority or settle an unapproved product-scope change. Discussing a decision does not itself change native Goal lifecycle state.

### An unfinished goal already exists

For a current-task launch, preserve it and ask whether the user wants to continue, edit, pause, or clear it. Do not create a competing Goal in that task. For an explicitly requested new-task launch, preserve and disclose the parent Goal, then continue with the separate task because each task has its own Goal state.

### Subagents conflict

Stop concurrent writing, select one implementation owner, reconcile the workspace manually, and rerun the relevant checks. Use worktrees for future independent writers.

### The task is open-ended or unsafe

Use supervised planning or execution with explicit approval points. A persistent goal is not a reason to remove the human from high-impact decisions.

## Select the host before launch

The entry skill keeps the shared workflow and loads only the applicable
[Codex](skills/goal-orchestrator/references/codex.md),
[Claude Code](skills/goal-orchestrator/references/claude.md), or
[Kimi Code](skills/goal-orchestrator/references/kimi.md) reference. Identify the app
from the environment and exposed tools, never from the model's name.

Claude and Kimi normally hand over user `/goal` commands. Displaying one is not a
launch. Codex requires preflight state inspection, creation, and a matching
post-creation state in the actual destination task. If those tools are missing,
report a handover. If task setup or activation is pending or fails, report that
state and preserve the requested destination.

Keep current permissions. If a host reports a trust, hook, or capability problem,
record the diagnostic; do not change policy to force autonomous execution. Use
only that host's lifecycle controls. Claude replacement and Kimi queued `next`
have different effects; Kimi `next` starts immediately when no goal is active.

## Preserve provenance and iteration evidence

The [brief and evidence record](skills/goal-orchestrator/references/artifacts.md)
adds the decision route and execution mode, source paths/dates, workspace/ref,
acceptance-to-evidence mapping, required decisions versus optional preferences,
settled choices and assumptions, and what to record between attempts. The brief generator fills metadata
only; it does not replace Git, instruction, or verification-script discovery.

After an attempt, capture decisive evidence, what was learned, the next useful
experiment, and what would unblock progress. Keep the finish line stable while
adapting the approach. For an unsuccessful stop, list unfinished criteria,
attempts/output, preserved artifacts/native state, and a concrete next step.

## Use explicit executable checks

Native goals can still contain prose review criteria. For optional helper
execution, use the [verification record format](skills/goal-orchestrator/references/verification.md)
and [complete example](examples/verification-goal.md). Each command names its exact
working directory and expected exit status. Inspection files and human checks
remain separate; the helper never executes inferred prose.

The helper's default template mode checks structure only. Readiness detects
unresolved placeholders/decisions without executing anything. Execution requires
`--test-commands --yes`, prints the whole plan first, and returns nonzero when a
required check fails or manual evidence remains pending. A `PASS` only covers the
declared checks; the main agent must still establish that they prove the outcome.

### Optional terminal helpers

Normal conversational use does not require these utilities. They live in the repository's `goal-orchestrator/scripts/` directory and are not bundled into a standalone installed skill copy. They do not launch or manage native Goals.

Run the following commands from the repository's `goal-orchestrator/` directory. Replace example paths and task text with your own.

Generate a preliminary brief from project metadata (actual code, Git state, and verification still need inspection):

```sh
python3 scripts/generate_brief.py /path/to/project --task "Implement password reset"
```

Extract goal text from a document:

```sh
python3 scripts/extract_goal.py /path/to/goal.md
```

Check template structure, then readiness:

```sh
python3 scripts/benchmark_goals.py /path/to/goal.md --mode template
python3 scripts/benchmark_goals.py /path/to/goal.md --mode readiness
```

Preview the explicit command plan without executing it:

```sh
python3 scripts/benchmark_goals.py /path/to/goal.md \
  --test-commands --cwd /path/to/project
```

Execute the declared checks when authorized:

```sh
python3 scripts/benchmark_goals.py /path/to/goal.md \
  --test-commands --yes --cwd /path/to/project --timeout 30
```

Only explicit `Command:` JSON records execute. File references, backticked text, and prose do not become shell commands. `--cwd` supplies the base for relative check directories; without it, relative directories resolve from the goal file. `--timeout` limits each check in seconds.

| Verdict | Meaning |
| --- | --- |
| `STRUCTURE_ONLY` | Template structure passed; no commands ran |
| `READY` | Authoring checks passed; verification has not run |
| `PASS` | Declared executable checks passed with no pending manual evidence |
| `FAIL` | An input, readiness, or executable check failed |
| `PENDING` / `MANUAL` | Required executable or human evidence remains outstanding |
| `NO_GOALS` | No goals were found |
| `EMPTY_ALLOWED` | An empty scan was explicitly accepted with `--allow-empty` |

A zero exit status can mean structure, readiness, or executable-check success: inspect `summary.status` before interpreting the result. See the [helper reference](README.md#helper-commands) for exit codes and the [verification schema](skills/goal-orchestrator/references/verification.md) for exact record requirements.

## Acceptance evidence

The smoke suite and Python tests exercise parsing, verdicts, exact command and
working-directory handling, timeouts, and packaging. The [behavioral cases](evals/README.md)
include simulated host calls with fixed results, independently reviewed
Guided/Autonomous conversation scenarios, and optional Claude model-backed
evals. Passing parser tests does not establish conversational question quality.
These are separate evidence levels. Confirm skill discovery and actual
native activation in each host only when those runs are authorized; never relabel
simulated results as live platform acceptance.
