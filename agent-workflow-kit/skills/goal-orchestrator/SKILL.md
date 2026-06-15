---
name: goal-orchestrator
description: Turn a broad task into an execution-ready brief, a concrete top-level goal, optional parallel subagent goals, synthesized results, and verification. Use when the user asks to write goals, use /goal, fill a build brief, spawn parallel agents or subagents, or handle complex work through independent workstreams in Claude Code or Codex.
---

# Goal Orchestrator

Use this skill to convert a raw request into a clear goal, split independent work across agents when useful, and synthesize the result into one verified answer or artifact.

The main agent owns the outcome. Subagents provide research, plans, review, or isolated implementation help; they do not replace final judgment.

## 1. Fill The Brief

Translate the user request into a completed brief before dispatching work. Use this universal form:

```text
Build or deliver [OUTCOME] in [CONTEXT, TECH, OR FRAMEWORK].
It should include [CORE DELIVERABLES], with [BEHAVIOR, INTERACTION, WORKFLOW, OR ACCEPTANCE DETAILS].
Make it feel or meet [QUALITY BAR], using [RELEVANT STYLE, ARCHITECTURE, CONSTRAINTS], [ENVIRONMENT OR INTEGRATION DETAILS], and [FINISHING TOUCHES].
Output as [ARTIFACT OR FORMAT].
```

Do not leave bracketed placeholders. Infer conservative defaults from the user's request and the current project. Ask only when a missing detail makes the task impossible, destructive, or materially risky.

For non-visual tasks, adapt the fields:

- `OUTCOME`: the concrete result to produce.
- `CONTEXT, TECH, OR FRAMEWORK`: the repo, language, toolchain, platform, or domain.
- `CORE DELIVERABLES`: files, features, analysis, fixes, tests, or decisions needed.
- `BEHAVIOR OR ACCEPTANCE DETAILS`: what must work, how it should behave, and edge cases.
- `QUALITY BAR`: correctness, maintainability, performance, UX, safety, tone, or evidence standard.
- `ENVIRONMENT OR INTEGRATION DETAILS`: APIs, data sources, deployment targets, permissions, or constraints.
- `ARTIFACT OR FORMAT`: code changes, a single file, a report, a PR, a patch, or a final answer.

Example for a visual build:

```text
Build a first-person roller coaster POV ride in Three.js. It should include a camera traveling along a looping track with drops, banked turns, and at least one inversion, with smooth acceleration on descents and slowing on climbs. Make it feel fast and cinematic, using track geometry, supports, a skybox, terrain below, lighting that sells speed, and sound effects. Output as a single HTML file.
```

## 2. Define The Goal

Before substantial work, write a top-level goal with done criteria. Use an actual goal tool or `/goal` workflow only when the user explicitly requested goals or the platform permits skill-driven goal creation. If goal creation is unavailable, blocked by an active goal, or not appropriate, write the goal block into the working plan instead.

Use this shape:

```text
/goal [ONE SENTENCE OBJECTIVE]

Brief:
[Filled brief.]

Done when:
- [Concrete finishing criterion.]
- [Concrete finishing criterion.]
- [Concrete finishing criterion.]

Artifacts:
- [Expected files, answer, report, PR, or other output.]

Verification:
- [Smallest reliable checks that prove the result.]

Constraints:
- [User constraints, repo boundaries, approval limits, and non-goals.]
```

## 3. Decide Whether To Parallelize

Parallelize only when it will improve speed, quality, or coverage. Do direct work when the task is small, tightly coupled, or likely to create edit conflicts.

Good parallel workstreams:

- Existing-context research: repo structure, prior patterns, docs, APIs, product requirements.
- Architecture or implementation plan: data flow, module boundaries, migration strategy.
- Independent implementation shards: separate files, modules, routes, components, tests, or docs.
- UX, copy, or content pass: interface behavior, wording, examples, polish.
- Verification pass: tests, edge cases, performance, accessibility, security, regression review.

Avoid parallel agents for:

- One small edit that is faster to do directly.
- Work that requires multiple agents to modify the same lines or make the same central decision.
- Secrets, credentials, destructive operations, or production changes unless explicitly authorized.
- High-stakes claims that cannot be verified from authoritative sources.

Use a practical agent count:

- `0 agents`: trivial or tightly coupled task.
- `2-4 agents`: most nontrivial tasks with independent research, build, and review tracks.
- `5+ agents`: only broad tasks with clearly separable subsystems.

## 4. Dispatch Subgoals

When multi-agent or subagent tools exist, dispatch independent work concurrently. When they do not, parallelize safe local inspection commands if useful, then perform the remaining work directly.

Give each agent a self-contained prompt with its own dedicated goal:

```text
/goal [ONE CLEAR SUBGOAL]

Context:
[Filled brief.]
[Relevant repo, files, constraints, user preferences, and current plan.]

Deliverable:
[Specific output the main agent needs: findings, patch, design, tests, risks, examples, or recommendation.]

Boundaries:
[Files, modules, decisions, or questions this agent owns.]
[Files, modules, decisions, or actions this agent must avoid.]

Verification:
[Checks to run, evidence to collect, or reasoning standard to meet.]

Return format:
- Summary
- Evidence or file references
- Recommendation or produced artifact
- Verification performed
- Unknowns or risks
```

Keep subgoals non-overlapping. Prefer read-only research agents plus one implementation owner when edit conflicts are likely. For implementation agents, assign explicit file ownership or require patch output instead of direct edits when the platform does not isolate workspaces.

## 5. Synthesize Results

As results return:

1. Compare each result against the actual repo, user request, and filled brief.
2. Verify any claim before relying on it, especially if it affects code, tests, security, legal, financial, medical, or current factual information.
3. Resolve conflicts explicitly. Prefer evidence from the current workspace over agent opinion.
4. Apply only the pieces that fit the request and constraints.
5. Keep edits focused. Avoid unrelated refactors, churn, or speculative extras.
6. Run the smallest reliable verification that proves the outcome.

If an agent produced a patch, inspect it before applying. If multiple agents touched overlapping code, reconcile manually and rerun the relevant checks.

## 6. Report Back

Final responses should be concise and user-facing:

- State what was produced or changed.
- Mention the main parallel workstreams only when useful.
- List verification performed and any checks that could not be run.
- Call out remaining risks, assumptions, or next steps only when they matter.

Do not dump every subagent transcript. Summarize the synthesis, not the machinery.
