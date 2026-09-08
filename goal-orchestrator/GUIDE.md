# Goal Orchestrator Guide

This guide explains how to turn broad work into safe, measurable native Codex goals. The short operational rules live in `skills/goal-orchestrator/SKILL.md`; this document provides examples and rationale.

## Contents

1. [The Two-Layer Model](#the-two-layer-model)
2. [Build an Execution-Ready Brief](#build-an-execution-ready-brief)
3. [Decide Whether Work Is Goal-Shaped](#decide-whether-work-is-goal-shaped)
4. [Write the Goal](#write-the-goal)
5. [Launch and Lifecycle](#launch-and-lifecycle)
6. [Delegate Independent Work](#delegate-independent-work)
7. [Verify Completion](#verify-completion)
8. [Troubleshooting](#troubleshooting)
9. [Claude Code Compatibility](#claude-code-compatibility)

## The Two-Layer Model

Native Codex Goal mode and `goal-orchestrator` solve different problems:

- **Native `/goal`** keeps a persistent target attached to the task and continues working toward it.
- **`$goal-orchestrator`** discovers the real outcome, constraints, approval points, and proof needed before execution.

Use `/goal` directly when the objective is already precise. Use `$goal-orchestrator` when words such as "production-ready," "reliable," "redesign," or "handle this end to end" still need to be grounded in the current workspace.

The skill defaults to drafting. Only explicit language such as "start it," "run it," "execute this goal," or "handle it end to end now" authorizes native goal creation and execution.

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
Goal-shaped: yes — verified by the focused regression, full suite, browser check, and final diff review.
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
- `<focused command>` exits 0; show its summary line.
- `<broader command>` exits 0; show its summary line.
- The final diff contains no unrelated changes; show `git diff --stat`.

If blocked:
- <report what was tried and what would unblock progress, then stop>
```

The goal body becomes the execution prompt and completion criteria. Keep it at or below 4,000 characters. Move background detail into the brief or a referenced file.

Each verification bullet names the output that proves it. The native checker judges only what the conversation shows, so a claim that a command passed, without its output, is not evidence.

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

In Codex, do not insert a conventional turn limit into every goal; pass the native token budget only when the user explicitly requests one. In Claude Code, an `or stop after N turns` clause is the only bound available, so offer it. A budget or cap limits a run; reaching it is an unsuccessful stop, not completion.

## Launch and Lifecycle

Before an explicit launch:

1. Show the proposed goal unless the exact text is already approved.
2. Choose the launch destination.
3. Inspect the relevant goal state and preserve unfinished work.
4. Confirm the workspace, dirty tree, verification commands, and approval points.
5. Start the goal without changing sandbox or approval settings.

After launch or handover, report a launch record: the runtime (Codex or Claude Code), the workspace (repository path, branch, and commit), the destination (current task, new task with its real `threadId`, or handover of the `/goal` text), the goal state (the result of the last `get_goal`, or "not launched: handed over"), and the budget (the requested `token_budget` or turn clause, or "none").

### Launch in the current task

This is the default when the user says only "start," "run," or "execute." Inspect the current task with `get_goal`. If an unfinished Goal already exists, preserve it and ask for direction; otherwise call `create_goal` here.

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
7. Treat `create_thread` as asynchronous. A temporary `clientThreadId` is not a usable `threadId`; wait for the real task identifiers, then use `wait_threads` or `read_thread` to confirm Goal activation.
8. Open the new task in the Codex UI only when the user asks to see it.

If task creation is unavailable, provide the complete prompt for the user to paste into a new task or ask whether launching in the current task is acceptable. Never change destinations silently.

Codex provides these user controls:

- `/goal` — start or view the task goal;
- `/goal edit` — revise its objective;
- `/goal pause` — pause work;
- `/goal resume` — resume work; and
- `/goal clear` — remove it.

The agent should not silently invoke those lifecycle controls. New authority, irreversible actions, or material product decisions still require the user.

Runtime rules above were verified against Codex 0.151.0 and Claude Code 2.1.263 on 2026-09-07. The Codex three-turn blocked rule and the `create_goal` budget rule come from the CLI's embedded tool contract, not public documentation; re-check them after upgrading either host.

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

Mark it blocked only after the same blocking condition has persisted for at least three consecutive goal turns and no meaningful in-scope progress remains. If a blocked goal is resumed, begin a fresh blocked audit. Difficulty, uncertainty, incomplete work, or a nearly exhausted budget are not blocking verdicts by themselves.

For a budgeted goal, report the final token usage returned by the goal tool after successful completion.

## Troubleshooting

### The goal is vague

Return to the brief. Replace activities such as "improve" or "review" with an observable result, boundaries, and proof.

### Verification passes but the feature is wrong

The check is too weak. Add direct behavior, artifact, or UI evidence and a final diff review. Do not weaken the objective to match an incomplete test suite.

### The run needs a new decision

Pause execution and ask. "Do not ask questions" is not a safe substitute for missing authority or a material product choice.

### An unfinished goal already exists

For a current-task launch, preserve it and ask whether the user wants to continue, edit, pause, or clear it. Do not create a competing Goal in that task. For an explicitly requested new-task launch, preserve and disclose the parent Goal, then continue with the separate task because each task has its own Goal state.

### Subagents conflict

Stop concurrent writing, select one implementation owner, reconcile the workspace manually, and rerun the relevant checks. Use worktrees for future independent writers.

### The task is open-ended or unsafe

Use supervised planning or execution with explicit approval points. A persistent goal is not a reason to remove the human from high-impact decisions.

## Claude Code Compatibility

The brief, goal-shaped gate, explicit launch rule, safety boundaries, selective delegation, and final verification are portable. Claude Code exposes no goal tool to the model: `/goal <condition>` is a user command, so a run there is a handover of the exact `/goal` text (for a headless run, write it to a file and pass `claude -p "$(cat goal.md)"`; never inline it in double quotes, because the shell would execute its backticked commands first), and the checker judges only what the conversation shows. Invoke the skill as `/goal-orchestrator:goal-orchestrator` from a marketplace install or `/goal-orchestrator` from a manual copy. Claude Code goal commands, checker behavior, permissions, and agent tools can change independently, so translate those controls from current Claude Code documentation instead of copying Codex-specific lifecycle rules.

A goal does not change permission mode, so a walk-away run needs auto mode or pre-allowed verification and edit commands; Manual mode stalls at the first prompt. Wait for every subagent and background shell before ending a turn, because evaluation is skipped while they run. There is no blocked status: when a blocker persists, state it and what would unblock it in plain text, then stop. Unrecoverable errors such as expired credentials that Claude Code manages, exhausted credits, an uncompactable context, or an unavailable model clear the goal with a warning, so tell the user to re-run `/goal`; resuming a session restores an active goal but resets its turn count, timer, and token-spend baseline as shown by `/goal`, and a textual turn clause is still judged from the conversation.
