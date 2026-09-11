# Codex runtime

Read this reference only in Codex. Last checked: 2026-09-10 against the Goal and desktop task tool schemas exposed by the host, plus the official links below. Tool names here are native capabilities to discover; do not emulate missing ones with shell commands.

Invoke the skill with `$goal-orchestrator`. Personal discovery uses `~/.agents/skills`; project discovery uses `.agents/skills`. The existing `$CODEX_HOME/skills` install path can be retained when supported by the installed host. Check discovery in the Skills UI or `/skills`.

### Choose the Launch Destination

After execution is explicitly authorized, resolve where it should run:

- **Current task:** Default when the user says only "start," "run," or "execute." Create the native Goal in the current task.
- **New Codex task:** Use only when the user explicitly asks for a new, separate, parallel, or background task. Do not create a separate task merely because isolation would be convenient.

For a current-task launch:

1. Confirm that `get_goal`, `create_goal`, and `update_goal` are exposed in the current task. If a required capability is missing, return the exact `/goal` text as a handover with state "not launched: unavailable tools". Do not create a goal whose prior state or activation you cannot inspect. Otherwise inspect native Goal state with `get_goal`.
2. Preserve any unfinished Goal. Do not silently replace, clear, edit, pause, or resume it; report the conflict and request direction.
3. Confirm the current workspace, dirty-tree boundaries, verification commands, and required approval points.
4. Create the native Goal with `create_goal`, passing the Goal body without the `/goal` prefix as the objective. Pass `token_budget` only when explicitly requested. Then call `get_goal` and report whether the Goal is active. Confirm the stored objective and any requested budget match the request; an active but different goal is a conflict, not activation evidence. If `create_goal` is unavailable in this runtime, do not claim a launch; return the exact `/goal` text for the user to run.

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

6. Instruct the destination task to check that its own Goal tools are available, inspect its own Goal state with `get_goal`, preserve and report any conflict, call `create_goal` there with the Goal body without the `/goal` prefix, then call `get_goal` again and report whether the Goal is active.
7. Treat task creation as asynchronous. A returned `clientThreadId` is temporary and must not be passed to tools that require `threadId`; wait until the created task exposes its real `threadId` and `hostId`, using `list_threads` to resolve pending creation when needed.
8. Use `wait_threads` or `read_thread` with the real identifiers to inspect destination activation evidence. If the summary lacks the actual post-creation `get_goal` result, read the destination with `includeOutputs: true`. Confirm an active Goal with the requested objective, budget, and task identity from that state evidence. Task creation or an agent's unsupported active claim is insufficient. If setup or activation is pending, failed, or unobservable, report that exact state; never label it active or silently retry task creation.
9. Switch the Codex UI with `navigate_to_codex_page` only when the user asks to open or show the new task.
10. If task creation is unavailable or cannot yield a real task, do not silently launch in the current task. Return a copy-ready new-task prompt containing the brief, Goal, and recursion guard, or ask whether current-task execution is acceptable.

For either destination, keep the existing sandbox and approval policy. Goal mode and task creation do not grant broader filesystem, network, connector, credential, or publication access.

## Completion and recovery

Use `update_goal` when available:

- Mark `complete` only when the full objective is achieved and no required work remains.
- Mark `blocked` only after the same blocking condition has persisted for at least three consecutive goal turns and no meaningful in-scope progress remains. Do not mark blocked the first time a blocker appears. Once that threshold is met, set `blocked` rather than continuing to report a blocker while the goal stays active. A resumed blocked goal starts a fresh blocked audit.
- Do not mark a goal complete or blocked merely because it is hard, slow, uncertain, incomplete, or near its budget.

Leave editing, pausing, resuming, and clearing to the user-facing Goal controls (`/goal edit`, `/goal pause`, `/goal resume`, `/goal clear`) unless the user explicitly requests the corresponding action. When a budgeted goal completes, report the final token usage returned by the goal tool.

## Sources and drift

The current tool schema is authoritative for `token_budget`, task creation, temporary IDs, `startingState.onMissing`, and the three-turn blocked rule. Those are host contracts, not portable rules or claims about other apps.

The [Codex command reference](https://learn.chatgpt.com/docs/developer-commands) documents the 4,000-character objective limit and user lifecycle commands. The [Goal guide](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex) describes task persistence. Recheck capabilities after host upgrades; an installed skill is not proof that Goal tools are enabled.
