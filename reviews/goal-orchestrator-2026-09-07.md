# Goal Orchestrator review

Reviewed September 7, 2026 (PDT), on branch `review` at `937c3e47bc68be57b35fd7ef96e8c05e72d7421a`.

Implementation follow-up: [September 10 changes and validation](goal-orchestrator-2026-09-10-implementation.md). The findings below preserve the reviewed snapshot.

## Assessment

Keep the Codex planning workflow. Its separation of drafting, explicit execution, bounded scope, and evidence-based completion is sound. The current package needs fixes to its verification helpers and documentation before their results should be used as an execution or completion gate. Claude Code compatibility is an outline; Kimi Code compatibility has not been implemented in the skill.

This review covers the skill and UI metadata, all helper scripts, tests, examples, plugin manifests, installation instructions, and the relevant marketplace architecture documentation. It compares them with current official Codex, Claude Code, and Kimi documentation. Kimi K3 is assessed as a model used through Kimi Code for the goal workflow; this is not a comparative model-performance benchmark.

## What works

- **A useful purpose:** discover the outcome and evidence before asking the native runtime to persist toward it. Already precise tasks can use native goals directly; small tasks can use ordinary prompts.
- **Clear intent boundaries:** selecting the skill defaults to drafting. Plan mode stays in planning, and native goal creation requires an explicit run request.
- **A practical brief:** outcome, context, output, boundaries, and verification help expose missing decisions without imposing a long questionnaire.
- **A sensible suitability check:** require a verifiable, authorized, bounded result. Observable behavior and artifacts matter in addition to passing tests.
- **Careful Codex task routing:** current task by default, new task only on request, saved-project discovery, Git worktrees, preservation of an unfinished parent goal, a recursion guard, and checking destination goal activation after asynchronous task creation.
- **Clear ownership:** one coordinating agent remains responsible; independent work can be delegated, concurrent writers need isolation, and returned claims must be verified.
- **Good completion discipline:** do not call incomplete work complete, do not confuse a budget limit with success, and retain existing permissions. The three-turn blocked rule matches the Goal tool contract exposed in this Codex session.
- **The common parser path works:** canonical blocks, legacy one-line goals, capitalized objective verbs, ordinary lifecycle filtering, and hidden/vendor directory pruning pass the included checks.
- **The rename and package metadata are consistent:** both Claude manifests validate, and the installed Codex skill and UI metadata are byte-identical to the repository copies.

These are source and local-check findings. They do not establish that every model will obey the prose on every run.

## Defects and gaps, in priority order

### R1 — High: a file mentioned for inspection can be executed

Location: `goal-orchestrator/scripts/benchmark_goals.py:43-50, 72-89`.

Every backticked fragment in a verification clause is treated as a possible shell command. A synthetic goal containing `Read \`./inspect-only.sh\` and review its contents` caused `--test-commands` to execute that script. The script only wrote a marker inside a temporary directory; the marker confirmed execution.

This requires the explicit `--test-commands` option; ordinary benchmarking does not execute commands. The defect is that opting into verification-command execution also executes things that were only named as files to read.

**Improve:** represent executable checks explicitly, separately from file references and human review criteria. Preserve the exact command and working directory. Display the execution list before running it. Do not infer executable shell from arbitrary Markdown code spans.

### R2 — High: failed command checks still produce a successful benchmark exit

Location: `goal-orchestrator/scripts/benchmark_goals.py:198-208, 241-246`.

With a structurally valid synthetic goal and verification command `exit 7`, `--test-commands` reported `exit_code: 7`, but the overall process exited `0` and `goals_with_issues` remained `0`. Execution results are collected but never contribute to the final verdict. `can_run: true` describes launchability, not success.

**Impact:** a caller using the process exit code or summary as verification evidence gets a false success. Timeouts and missing executables also need explicit failure treatment in the aggregate verdict.

**Improve:** distinguish structural lint results, command execution results, and outstanding manual checks. A failed required executable check must cause a nonzero verification result. Preserve legitimate nonzero expected statuses only when explicitly specified in the check definition.

### R3 — Medium: required commands disappear during extraction

Location: `goal-orchestrator/scripts/benchmark_goals.py:43-50, 53-67`.

Two reproductions:

| Input | Actual extracted commands |
| --- | --- |
| `` `pytest -q` exits 0; ruff check . passes `` | Only `pytest -q` |
| `pytest -q exits 0; pytest -q tests/auth passes` | Only `pytest -q tests/auth` |

The first happens because any backticked text causes an early return. The second happens because prefix matching treats a complete-suite command and a focused-suite command as duplicates.

**Improve:** parse every explicit check independently and deduplicate exact command/working-directory pairs only. Do not remove the existing placeholder guard while fixing mixed quoting.

### R4 — Medium: normal Markdown spacing can truncate the goal

Location: `goal-orchestrator/scripts/goal_parsing.py:73-108`.

A blank line between two verification bullets causes extraction to stop after the first bullet. A wrapped objective line before the first section causes the rest of the goal to disappear. Neither condition produces a truncation diagnostic.

**Impact:** extracted goals can omit constraints or required evidence while looking valid. The resulting character count describes the shortened extraction, not necessarily the submitted goal.

**Improve:** support blank-separated lists and wrapped objectives, or reject unsupported formatting with a precise location. Preserve the original goal body and source span for auditing. Silent shortening is the behavior to eliminate.

### R5 — Medium: an empty input is reported as a successful benchmark

Location: `goal-orchestrator/scripts/benchmark_goals.py:190-196, 241-246`.

A Markdown file with no goal yielded process exit `0`, `total_goals: 0`, and `goals_with_issues: 0`. The extraction CLI correctly treats no goals as an error, so the two commands disagree.

**Improve:** return a distinct no-goals error unless an explicit allow-empty mode is requested.

An unfilled template also passes structural benchmarking. That is useful when linting templates, but it is not evidence that a goal is ready to run. Add separate template and execution-readiness modes; the latter should identify unresolved placeholders, missing concrete evidence, and outstanding human decisions. The current smoke message describing all template blocks as measurable/verifiable overstates what is checked.

### R6 — Medium: the architecture document contradicts the skill

Location: `ARCHITECTURE.md:64-99`.

The architecture still describes a Haiku checker as the common execution engine, lists automatic tool approval and a turn cap as guardrails, and says Codex supports supervised orchestration only. The actual skill is Codex-first, preserves permission settings, has no mandatory textual turn cap, and uses native Codex Goals.

`goal-orchestrator/examples/goal-templates/refactor.md:123-131` also tells the reader to clear and restart a stuck goal without carrying the core skill's explicit user-direction qualification.

**Improve:** reconcile the complete package, including root documentation and recovery examples. Keep the shared workflow separate from platform-specific execution descriptions. Current [Codex Goal guidance](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex) supports native persistent objectives and unchanged permission boundaries.

### R7 — Medium: the Claude marketplace migration gives the wrong invocation syntax

Location: `README.md:59-72`.

After Claude `/plugin` migration commands, the documentation says invocation remains `$goal-orchestrator`. That is Codex syntax. Claude plugin skills use a plugin/skill namespace, so this manifest and directory layout imply `/goal-orchestrator:goal-orchestrator`; a personal Claude skill uses `/goal-orchestrator`. Renaming the plugin therefore changes the namespaced Claude invocation even though the inner skill name stays the same. This conclusion follows from the manifests and [Claude's skill namespace rules](https://code.claude.com/docs/en/skills).

**Improve:** show a small invocation table for Codex, personal Claude, plugin Claude, and Kimi Code. Verify discovery in each supported host.

### R8 — Medium: runtime compatibility is left to the model to invent

Location: `goal-orchestrator/skills/goal-orchestrator/SKILL.md:3, 82-106, 133-143`.

The operational body assumes Codex. Claude gets one sentence asking the agent to consult current documentation. Kimi has no adapter, installation instructions, or lifecycle mapping. This is an unsupported feature area, not proof that the underlying Kimi model cannot follow the planning workflow.

The current-task Codex route also says to use Goal tools "when available" without defining what to return when they are absent. Unlike the new-task route, it does not explicitly check activation after creation. This can leave a normal task looking like a launched Goal.

**Improve:** select the runtime and check actual capabilities before launch. Define explicit unsupported-runtime behavior and confirm activation for both destinations. For hosts with user-only lifecycle commands, hand over the exact command instead of claiming it ran.

A smaller Codex drift: line 94 forbids using `startingState` to create a new branch. The `create_thread` schema exposed in this session now supports an explicitly named missing branch with `onMissing: "create-branch"`. Refresh that rule from the actual host schema while keeping the default starting state unchanged.

## Comparison with current official documentation

### Codex

The core lifecycle is aligned: a task-scoped persistent goal, measurable evidence, preserved permissions, and separate user/system controls for pause, resume, and clear. Official documentation confirms `/goal edit` and a 4,000-character objective limit. The currently installed CLI reports `0.151.0`; the official Goal guide names `0.128.0` as the introduction version. [Goal guide](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex), [command reference](https://learn.chatgpt.com/docs/developer-commands).

The biggest workflow addition is an iteration policy: record the last attempt, decisive evidence, next useful experiment, and what would unblock progress. The existing brief describes success well but says less about adapting between attempts. Native tool names and the three-turn blocked policy should remain in the Codex reference, because they are runtime rules.

Use the currently documented `~/.agents/skills` location as the primary portable personal-install example. The older `~/.codex/skills` copy demonstrably works in this environment, so it is not a broken local installation. Bundle references and helpers inside the skill directory if they are intended to be available after a standalone copy. Currently that copy contains only `SKILL.md` and `agents/openai.yaml`. [Codex skill documentation](https://developers.openai.com/codex/skills).

### Claude Code

Claude uses a separate small-model evaluator over the transcript. It cannot independently inspect files or run commands. It can judge the condition unmet, met, or impossible. A new `/goal <condition>` replaces an active goal, so preserving existing work needs an explicit preflight. Its documented management surface is `/goal` and `/goal clear`, with clear aliases; Codex's edit/pause/resume commands must not be assumed. Conditions have a 4,000-character limit; optional time/turn stops are textual and judged from the conversation. Hook/trust settings can disable goals. [Claude Goal documentation](https://code.claude.com/docs/en/goal).

**Adapter requirements:** surface decisive evidence in the transcript, check the existing condition before replacement, define stop outcomes, check hook availability, and use the correct skill invocation. A subagent result is a handoff requiring main-agent verification; its tool access and execution context need to be chosen deliberately. [Claude skills](https://code.claude.com/docs/en/skills), [Claude subagents](https://code.claude.com/docs/en/sub-agents).

### Kimi Code with Kimi K3

K3 is available through Kimi Code as well as other Kimi products. Model selection does not make those products share one control surface. This review uses Kimi Code's documented goal and skill interfaces; it does not infer CLI behavior from K3 Cluster marketing. [Kimi product overview](https://www.kimi.com/en/help/agent/agent-overview), [K3 model/mode guidance](https://www.kimi.ai/help/others/model-mode-selection).

Kimi Code documents persistent goals and `/goal status`, `pause`, `resume`, `cancel`, `replace`, and `next`. Queued goals begin after completion; if no current goal exists, `next` starts work immediately. Prompt mode supports goal creation and reports completion/block/pause with exit codes `0`/`3`/`6`. These differences need their own mapping. The current parser incorrectly extracts `status`, `replace ...`, and `next ...` as new goal objectives, confirming that it should not be advertised as a Kimi lifecycle parser. [Kimi slash-command reference](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/slash-commands.html).

Kimi's goal documentation calls for stop conditions in the objective rather than a separate stop-limit flag. Interrupted sessions and errors can pause goals, and blocked/paused/canceled goals do not automatically advance the queue. The Codex-specific three-turn blocked rule is not a portable lifecycle contract. [Kimi Goals](https://www.kimi.ai/help/kimi-code/cli-goals).

Kimi supports this basic `name`/`description` skill format, shared `.agents/skills` directories, and `/skill:goal-orchestrator` invocation. Its current documentation uses `~/.kimi-code/skills` and `.kimi-code/skills` for host-specific locations. A Kimi adapter should state these paths and preserve permission mode. [Kimi skills](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html).

Its custom-agent documentation also supports tool/subagent allowlists and calls for a self-contained final handoff from delegated custom agents. The skill's existing ownership and evidence rules fit that workflow; runtime tools and agent definitions still need explicit mapping. [Kimi agents](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/agents.html).

## Recommended improvements

1. **Repair the verification helpers first.** Resolve R1-R5 with focused regression tests. Use explicit executable check records, exact deduplication, faithful extraction, and distinct structural/pass/fail/manual/empty results.
2. **Retain one shared planning skill with three runtime references.** Keep the concise outcome/authorization/verification workflow at the entry point. Load only the matching Codex, Claude, or Kimi reference, including exact launch/status/stop controls and failure recovery. This keeps the existing Codex-first direction while making compatibility concrete.
3. **Make launch evidence explicit.** Record the runtime, workspace/ref, destination, actual goal state, and any requested budget. Show the proposed goal when required, but distinguish showing it from demanding approval again when execution is already authorized. Handle unavailable capabilities without implying a successful launch.
4. **Add behavioral acceptance cases.** Seven of the 16 current unit tests assert that routing phrases exist in Markdown. They catch wording drift but do not test decisions, tool order, or actual activation. Cover draft-only requests, explicit launch, active-goal conflicts, unavailable tools, failed/pending task creation, correct destination, no recursive creation, requested budgets, and final evidence before completion. Run model-backed cases in disposable workspaces when that evaluation is authorized.
5. **Improve the reusable artifacts.** Add iteration policy, source provenance, acceptance-to-evidence mapping, unresolved decisions, and an explicit unsuccessful stopping report. Keep uncertainty visible instead of weakening the success condition.
6. **Reduce documentation and packaging drift.** Correct root architecture and migration syntax, link all runtime references from the entry skill, ship referenced materials in standalone installations, document Python/PyYAML requirements, and give official references a last-checked date.

Additional lower-priority helper findings: a valid single-word check such as `true` is flagged as possibly invalid; angle-bracket placeholders are treated as commands; the brief generator remains a README/package metadata scaffold and does not inspect Git state, applicable instructions, or actual verification scripts. Label it as a draft scaffold and keep project discovery in the orchestrator.

## Verification performed

| Check | Result | What it establishes |
| --- | --- | --- |
| Skill frontmatter and content validation | PASS | Current metadata, required headings, and checked internal anchors |
| Included unit suite | PASS, 16 tests | Parser cases and seven wording-based routing checks |
| Smoke suite | PASS, 10 checks | Local helper/package behavior for included fixtures |
| Goal-template benchmark | PASS, 10 blocks | Structure and size of five templates plus five examples |
| Claude marketplace/plugin validation | PASS, both | Manifest validity |
| Installed Codex source parity | PASS | Skill and UI metadata match repository bytes |
| Adversarial local probes | Defects reproduced | R1-R5, plus unsupported Kimi lifecycle parsing |
| Live Codex/Claude/Kimi goal launches | NOT RUN | No runtime/model success-rate claim |
| Hosted, production, or paid provider execution | NOT RUN | Review used local synthetic fixtures and public docs |

Local versions observed: Codex CLI `0.151.0`, Claude Code `2.1.263`, Kimi Code `0.39.1`, Python `3.14.3`. PyYAML was absent from the base interpreter; the complete smoke suite passed using an isolated `uv --with pyyaml` environment with its cache under `/private/tmp`.

Re-run the existing checks from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/goal-orchestrator-review-uv uv run --with pyyaml bash goal-orchestrator/scripts/smoke_test.sh
claude plugin validate .
claude plugin validate ./goal-orchestrator
```

Minimal reproduction of R2 (the shell command only exits):

```sh
python3 goal-orchestrator/scripts/benchmark_goals.py '/goal Check a fixture. Done only when exit 7 exits 0, proven by running exit 7.' --test-commands
```

Observed: command exit `7`, benchmark exit `0`, and zero structural issues. This report records findings and recommendations; no skill, helper, manifest, or runtime configuration was changed by the review.
