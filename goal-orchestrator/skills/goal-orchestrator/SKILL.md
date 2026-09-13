---
name: goal-orchestrator
description: Turn broad requests into an execution-ready brief and a measurable native goal for Codex, Claude Code, or Kimi Code. Use when the user asks to draft, refine, start, or run a goal whose outcome or verification still needs definition. Already precise tasks can use native /goal or an ordinary prompt directly.
---

# Goal Orchestrator

Prepare bounded work for the current app's native Goal feature. Codex is the primary host; Claude Code and Kimi Code have their own launch and lifecycle instructions. Model names, including Kimi K3, do not determine the host's controls.

## 1. Ground the Request and Choose a Mode

Inspect the workspace, applicable instructions, implementation, and available goal state. Resolve facts locally before asking about intent, authority, or material tradeoffs. Preserve existing work.

### Choose how decisions are made

- **Guided (default):** Inspect first, then ask about unresolved decisions that materially affect architecture, product direction, scope, compatibility, or the finish line. Offer a recommendation and explain the meaningful tradeoff when evidence supports one. If the request is already sufficiently defined, proceed without an interview.
- **Autonomous (explicit preference):** Choose reasonable implementation defaults within the user's outcome and boundaries. Record consequential assumptions and why they fit the workspace. Ask only when missing information or authority prevents responsible progress; do not infer permission for a product-scope change or an external action from the route name.

Use the user's route preference from this conversation; otherwise use Guided. `Guided:` and `Autonomous:` are ordinary prompt labels, not slash commands or native Goal controls. Natural language such as "ask me about the architecture first" or "choose implementation details yourself" also selects the route. State the selected route and execution mode briefly with the brief; do not ask the user to select a route when their preference or the default is sufficient.

In Guided, ask a small batch of high-impact questions using the host's supported question interface or concise prose. Ask only what remains unresolved after inspection and prior conversation: desired user outcome, architectural direction, tradeoffs, compatibility, or decisive acceptance evidence. Do not repeat settled questions, ask for facts available locally, or force a fixed questionnaire. Distinguish a required decision from an optional preference. For optional preferences, allow a reasonable opportunity to answer and then proceed with a stated default; an unanswered required decision remains unresolved. Continue independent authorized work while waiting.

### Choose whether execution is authorized

The route controls decision-making; draft/run mode controls execution. Choosing Autonomous alone does not authorize implementation, goal creation, delegation, or a new task.

- **Draft mode (default):** Return a brief, suitability decision, and proposed goal. Skill selection alone does not authorize implementation, goal creation, or delegation.
- **Run mode (explicit only):** Use when the user asks to start, run, execute, or pursue this goal now. Carry existing authorization forward without demanding approval again for the same work.
- **Supervised fallback:** When the goal is not verifiable, authorized, or bounded, propose a supervised path in draft mode; in explicit run mode do the authorized portion and stop at unresolved decisions.

Remain in draft mode when the current host is in Plan mode or otherwise forbids execution.

| Request | Route and execution |
| --- | --- |
| Bare skill invocation or "help me define this" | Guided + draft |
| "Autonomous: draft a goal; choose the approach yourself" | Autonomous + draft |
| "Guided: resolve the architecture questions, then run it" | Guided + run; resolve required decisions before dependent work, then use existing launch authority |
| "Autonomous: define and run this goal" | Autonomous + run within the stated boundaries |

Route changes preserve agreed decisions, scope, destination, budget, and prior execution authority. "Let's discuss storage before continuing" switches to Guided for that decision and holds dependent work; it does not silently pause or edit native Goal state. "Choose the remaining details yourself" switches to Autonomous but does not launch a draft. "Those decisions are settled; run autonomously from here" also authorizes execution. If the Goal is already active, continue that Goal; use the host's lifecycle rules for any user-requested objective or state change instead of creating a replacement.

### Select the runtime

Identify the app and actual exposed capabilities, then load only its reference:

| Host | Instructions | Skill invocation |
| --- | --- | --- |
| Codex | [Codex](references/codex.md) | `$goal-orchestrator` |
| Claude Code | [Claude Code](references/claude.md) | `/goal-orchestrator:goal-orchestrator` for a plugin; `/goal-orchestrator` for a personal copy |
| Kimi Code | [Kimi Code](references/kimi.md) | `/skill:goal-orchestrator` |

For an unknown host, return the brief and goal text with state "not launched: unsupported runtime". Do not invent lifecycle tools or silently substitute another app. If a known host lacks required launch/status capabilities, use its documented handover and state what is unavailable.

## 2. Build the Brief

Capture the five fields that guide execution:

```text
Outcome: [specific observable result]
Context: [workspace, current behavior, sources and provenance]
Output: [artifacts or user-facing result]
Boundaries: [scope, compatibility, authority, non-goals]
Verification: [each acceptance criterion mapped to decisive evidence]
```

Record workspace/ref, source dates, assumptions, unresolved decisions, and an iteration policy when they affect the work. Use the [brief and evidence record](references/artifacts.md) when a run spans multiple attempts. The metadata brief generator is a draft scaffold; the orchestrator still inspects Git state, applicable instructions, and actual verification scripts.

Record consequential decisions with their rationale and whether the user selected them or the agent assumed them. Update the brief and proposed goal when answers change the approach; preserve settled decisions so a later route change does not restart discovery.

Treat commits, pushes, pull requests, deployment, credential use, purchases, destructive actions, and external messages as separate authority unless included in the user's request. A goal does not broaden permissions.

## 3. Decide Whether the Task Is Goal-Shaped

Require a **verifiable**, **safe and authorized**, and **bounded** result. State the decision and decisive evidence in one line. Keep unresolved human choices visible; do not weaken success criteria to make a goal appear ready.

If the outcome and checks are already precise, use native `/goal` directly when explicitly requested. Avoid rewriting a sufficient objective into a planning exercise.

## 4. Draft the Native Goal

Use plain headings and bullet lists. Blank lines and wrapped objectives are allowed. Keep the complete body within 4,000 characters, with supporting context in the brief.

```text
/goal <specific observable outcome>

Done when:
- <acceptance criterion>

Constraints:
- <scope, authority, compatibility, or non-goal boundary>

Verification:
- Command: {"command": "<exact command>", "cwd": "<working directory>", "expected_exit": 0, "evidence": "<output to show>"}
- Manual: <observation or review criterion and the evidence to show>

If blocked:
- <report attempts, remaining work, and what would unblock progress>
```

Use [verification records](references/verification.md) to distinguish commands from files to inspect and human checks. Omit inapplicable bullets and replace placeholders. Prose criteria remain valid for native goals; the optional helper executes only explicit Command records.

Show actual output, artifacts, or observations for each acceptance criterion. A green suite cannot prove behavior it does not cover. Transcript evidence is essential for Claude's evaluator; the other hosts also need a reviewable completion record.

Keep native budgets and stop controls in the selected runtime reference. A budget limit or unsuccessful stop must not become a completion claim.

## 5. Preflight and Launch

Show the goal text as part of the launch record. An already authorized run does not require another approval of unchanged scope; ask only for missing decisions or authority. Follow the selected runtime's state inspection, conflict handling, launch/handover, and activation checks.

The current task is the default destination. A new task requires an explicit request and the destination's own launch checks. If already in the destination task, launch there; do not create another task.

After launch or handover, report a launch record:

- Runtime and available goal capabilities.
- Workspace: path, branch/ref, commit, and relevant dirty-tree boundaries.
- Destination: current task, real new-task identifier, or user handover.
- Goal state: verified active with matching objective, pending, failed, or not launched; include the observation that establishes it.
- Budget: requested native budget, textual stop condition, or none; state whether it was actually applied.

Never equate a displayed goal, created task, subagent, or proposed command with an active native Goal.

## 6. Execute and Coordinate Work

Keep one main agent responsible. Delegate only during an explicit run when independent work materially helps and the host permits it. Give each subagent the objective, context, boundaries, verification, and return format. Isolate concurrent writers. Wait for required results and verify each against the workspace before synthesizing the outcome. Use the runtime reference for actual agent tools.

After each meaningful attempt, record what changed, decisive evidence, remaining uncertainty, the next useful experiment, and what would unblock progress. Change the approach when evidence warrants it; do not repeat an unchanged failing action or loosen the finish line. Continue useful in-scope work while waiting for input.

## 7. Verify, Complete, or Block

Re-run the relevant verification, inspect its output, check the requested behavior and artifacts, and review the final diff and authority boundaries. Map every acceptance criterion to its evidence. Template lint and readiness are not completion evidence; pending manual checks remain pending until their results are observed.

Follow the selected host's completion and blocked-state rules. Codex's three-turn rule does not apply to Claude or Kimi. Before an unsuccessful stop, report the attempts and evidence, unfinished criteria, blocker, preserved workspace/artifacts, and concrete next step using the [stopping record](references/artifacts.md#unsuccessful-stop). Do not clear, replace, or restart a goal without the user's direction.
