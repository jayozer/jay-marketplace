---
name: goal-orchestrator
description: Use when a broad or vague request must become an execution-ready brief and a measurable native goal before autonomous work starts, or when the user asks to write, refine, start, or run a goal, define done criteria, or coordinate an end-to-end task. Not for tasks whose outcome and checks are already precise; use native /goal or a normal prompt for those.
---

# Goal Orchestrator

Treat native Codex Goal mode as the persistence and execution engine. Use this skill as the planner and project manager that makes the goal precise, safe, bounded, and verifiable. Supported hosts are Codex and Claude Code.

## 1. Ground the Request and Choose a Mode

Inspect the workspace, relevant instructions, existing implementation, and goal state before asking questions. Resolve discoverable facts from the environment. Ask only about product intent, authority, or tradeoffs that materially change the result.

Choose one mode:

- **Draft mode (default):** Produce the brief, goal-shaped decision, and proposed goal. Do not create a native goal, implement the work, or spawn subagents merely because this skill was selected.
- **Run mode (explicit only):** Enter only when the user clearly asks to start, run, execute, or pursue the goal now. In run mode, create and pursue a native goal when the task passes the gate below.
- **Supervised fallback:** Applies within either mode when the goal-shaped gate in section 3 fails. In draft mode, propose the supervised path. In explicit run mode, perform only the work the user actually authorized and preserve approval points.

If the current runtime is in Plan mode or otherwise forbids execution, remain in draft mode and hand back an execution-ready plan and goal.

## 2. Build the Brief

Capture only information that changes execution:

```text
Outcome: [specific result]
Context: [repo, system, current behavior, relevant sources]
Output: [artifacts or user-facing result]
Boundaries: [scope, compatibility, approval limits, non-goals]
Verification: [tests, observations, measurements, or review criteria]
```

Fill every applicable field. Preserve existing dirty work and applicable `AGENTS.md` or skill instructions. Treat commits, pushes, pull requests, deployments, destructive changes, credential use, purchases, and external messages as separate authority unless the user explicitly included them.

For provider API or SDK work, consult the current provider documentation skill before fixing model names, parameters, limits, or API shapes in the brief.

## 3. Decide Whether the Task Is Goal-Shaped

Require all three:

- **Verifiable:** Observable evidence can prove the result, including behavior that tests alone do not cover.
- **Safe and authorized:** The work is recoverable and does not hide a required human decision or broaden permissions.
- **Bounded:** The scope has a realistic finish line rather than an open-ended research or creative loop.

State the decision in one line, for example: `Goal-shaped: yes — verified by the focused regression, full test suite, and final diff review.`

If any requirement fails, do not force the request into Goal mode. In draft mode, explain the missing condition and propose a supervised path. In explicit run mode, perform only safe, authorized supervised work and stop at required approval points.

## 4. Draft the Native Goal

Use this canonical artifact:

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

The `/goal <specific outcome>` line must itself name an observable result (a file, a behavior, a passing check), because the checker judges the whole text and a vague headline can never be shown met.

Keep the goal body at or below 4,000 characters. Put supporting detail in the preceding brief or a referenced file. In Codex, do not add a mandatory textual turn limit; supply a native token budget only when the user explicitly requests one. In Claude Code, an `or stop after N turns` clause is the only bound available, so offer one. Reaching a budget or cap is an unsuccessful stop, not completion.

Make the goal self-contained enough to serve as both the first execution prompt and the completion criteria. Include actual behavior and artifact checks; do not use a green test suite as the sole proof when it cannot establish the requested outcome.

Write each verification bullet so the proof appears in the conversation: name the command and the output that must be shown, such as the test summary line, `git diff --stat`, the response body, or the file listing. The native checker judges only what the transcript shows. A statement that a command passed, without its output, is not evidence.

## 5. Preflight and Launch

Show the draft before launch unless the user already approved that exact goal text.

### Choose the Launch Destination

After execution is explicitly authorized, resolve where it should run:

- **Current task:** Default when the user says only "start," "run," or "execute." Create the native Goal in the current task.
- **New Codex task:** Use only when the user explicitly asks for a new, separate, parallel, or background task. Do not create a separate task merely because isolation would be convenient.

For a current-task launch:

1. Inspect native Goal state with `get_goal`.
2. Preserve any unfinished Goal. Do not silently replace, clear, edit, pause, or resume it; report the conflict and request direction.
3. Confirm the current workspace, dirty-tree boundaries, verification commands, and required approval points.
4. Create the native Goal with `create_goal`, passing the Goal body without the `/goal` prefix as the objective. Pass `token_budget` only when explicitly requested. Then call `get_goal` and report whether the Goal is active. If `create_goal` is unavailable in this runtime, do not claim a launch; return the exact `/goal` text for the user to run.

For an explicitly requested new-task launch:

1. Inspect the parent task's Goal state when available. Preserve and disclose any unfinished parent Goal; it blocks another current-task Goal but does not block a Goal in a separately created task. Do not call `create_goal` in the parent task.
2. Call `list_projects` before `create_thread` and select the saved project that matches the grounded workspace. Do not guess a project ID.
3. Check the project's `isGitRepository` value. For a Git project, create the task in a Codex worktree by default; use the saved project directly for a non-Git project or when the user explicitly requests it.
4. Omit worktree `startingState` by default. Use a specific existing branch/ref or the current working tree only when the user explicitly requests that starting state. Name a new branch only when the user requested that exact name, via `onMissing: "create-branch"`; never invent a branch name.
5. Put the complete brief and canonical Goal text in the new task's initial prompt, followed by this recursion guard:

   ```text
   You are already the destination task created by Goal Orchestrator.
   Launch the native Goal in this task. Do not create another task.
   ```

6. Instruct the destination task to inspect its own Goal state with `get_goal`, preserve and report any conflict, call `create_goal` there with the Goal body without the `/goal` prefix, then call `get_goal` again and report whether the Goal is active.
7. Treat task creation as asynchronous. A returned `clientThreadId` is temporary and must not be passed to tools that require `threadId`; wait until the created task exposes its real `threadId` and `hostId`, using `list_threads` to resolve pending creation when needed.
8. Use `wait_threads` or `read_thread` with the real identifiers to confirm that the destination reported an active Goal. Task creation alone is not successful launch evidence.
9. Switch the Codex UI with `navigate_to_codex_page` only when the user asks to open or show the new task.
10. If task creation is unavailable or cannot yield a real task, do not silently launch in the current task. Return a copy-ready new-task prompt containing the brief, Goal, and recursion guard, or ask whether current-task execution is acceptable.

For either destination, keep the existing sandbox and approval policy. Goal mode and task creation do not grant broader filesystem, network, connector, credential, or publication access.

During execution, make conservative in-scope assumptions and record material ones. Request input when progress needs new authority, an irreversible action, or a product choice that would materially change the result.

## 6. Execute and Coordinate Work

Keep the main agent responsible for the outcome. Use subagents only in explicit run mode, when independent work materially improves speed, quality, or coverage and the runtime permits delegation.

- Delegate read-heavy exploration, tests, review, or clearly isolated implementation.
- Give each subagent one self-contained objective, context, boundaries, verification request, and return format.
- Spawn independent agents before waiting so they can run concurrently.
- Avoid concurrent writers in one checkout. Use one implementation owner or isolated worktrees.
- Wait for every required result, verify claims against the workspace, reconcile conflicts, and synthesize one answer.

Do direct work when the task is small, tightly coupled, or cheaper than orchestration.

## 7. Verify, Complete, or Block

Before completion:

1. Re-run the real verification and read the actual output.
2. Check the requested behavior and artifacts, not only exit codes.
3. Review the final diff and confirm boundaries, existing work, and approval limits were preserved.
4. Report commands, decisive results, skipped checks, assumptions, and remaining risks.

Use `update_goal` when available:

- Mark `complete` only when the full objective is achieved and no required work remains.
- Mark `blocked` only after the same blocking condition has persisted for at least three consecutive goal turns and no meaningful in-scope progress remains. Do not mark blocked the first time a blocker appears. Once that threshold is met, set `blocked` rather than continuing to report a blocker while the goal stays active. A resumed blocked goal starts a fresh blocked audit.
- Do not mark a goal complete or blocked merely because it is hard, slow, uncertain, incomplete, or near its budget.

Leave editing, pausing, resuming, and clearing to the user-facing Goal controls (`/goal edit`, `/goal pause`, `/goal resume`, `/goal clear`) unless the user explicitly requests the corresponding action. When a budgeted goal completes, report the final token usage returned by the goal tool.

## Claude Code Compatibility

Reuse the brief, goal-shaped gate, explicit-launch rule, permission boundaries, selective delegation, and independent final verification in Claude Code. Do not assume Codex tool names, lifecycle rules, or implementation details apply there. Translate the goal and agent controls as follows, and consult current Claude Code documentation for anything not listed.

- **Launch is a handover, never an action.** Claude Code exposes no goal tool to the model; `/goal <condition>` is a user command. In explicit run mode, return the exact `/goal` block for the user to run, or `claude -p "/goal ..."` for a headless run. Never report a goal as created, active, or launched.
- **Permission mode is unchanged by a goal.** In the handover, tell the user to run in auto mode or pre-allow the verification and edit commands; in Manual mode the run stalls at the first prompt. `/goal` is disabled in an untrusted workspace and when `disableAllHooks` or `allowManagedHooksOnly` is set.
- **The checker reads only the conversation.** A separate small model judges the condition against the transcript; it cannot run commands or read files. Every verification bullet names output to be shown, and the agent prints that output before claiming completion.
- **One goal per session, and a new `/goal` replaces it.** The model cannot inspect goal state. Before handing over, ask whether a goal is already active. Only `/goal` (view) and `/goal clear` exist; there is no edit, pause, or resume.
- **Bounding is textual.** Offer an optional `or stop after N turns` clause. A stop at the cap is reported as an unsuccessful stop with the remaining work listed, not as completion.
- **Completion is the checker's verdict.** There is no `update_goal`. Report commands, decisive output, skipped checks, and remaining risks in the final message so the checker can judge them.
- **Wait for delegated work.** Wait for every subagent and background shell before ending a turn; evaluation is skipped while they run.
- **There is no `blocked` status.** When no tool call is made for several turns, the loop stops with the goal still set, so state the blocker and what would unblock it in plain text and stop working.
