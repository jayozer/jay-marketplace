# Goal Orchestrator Behavioral Evals

Acceptance cases for the `goal-orchestrator` skill: simulated host traces with fixed tool responses, plus optional Claude model-backed runs. Wording tests remain documentation tripwires; neither wording nor trace validation proves a real native Goal launched.

## Simulated host decisions

`runtime_cases.json` contains 18 independent prompts and immutable mock tool
responses. They cover draft/Plan mode, explicit current-task launch, unfinished
goals, unavailable tools, failed creation, mismatched activation, requested and
unrequested budgets, pending/failed/new-task activation, real destination IDs,
preserving a parent Goal, recursion prevention, and evidence before completion.
Claude and Kimi cases exercise user-command handovers, including a Kimi `next`
request that must stay a draft because no Goal is active.

The trace format is:

```json
{
  "case_id": "tools-unavailable",
  "calls": [],
  "final": {"state": "handover", "destination": "current"},
  "response": "Not launched: the Goal tools are unavailable."
}
```

Calls name the fixture's tool, `arguments`, and optional `target` (default
`current`). The grader supplies results from the fixture in call order; a model
cannot insert its own successful result. Final states are `draft`, `handover`,
`pending`, `failed`, `conflict`, `active`, `complete`, or `unfinished`.
Mock `run_check` and `review_artifact` expose the fixed completion evidence;
they are not native Goal APIs. The fixture's `read_thread`/`wait_threads` result
is normalized evidence from the destination's post-creation `get_goal` output,
not a claim about raw desktop response schemas or an agent's unsupported summary.

```sh
python3 goal-orchestrator/scripts/grade_runtime_trace.py \
  goal-orchestrator/evals/fixtures/runtime-traces/forward-2026-09-10.json
python3 -m unittest discover -s goal-orchestrator/tests -p 'test_runtime_traces.py'
```

The saved trace was produced by an independent agent applying the shared skill
and relevant references to these cases on 2026-09-10. The agent did not read the
grader, implementation tests, or review conclusions and did not invoke any real
Goal, task, provider, or external service. Its responses are retained for manual
inspection. The grader initially incorrectly rejected a correctly reported
activation mismatch; a regression now distinguishes that conflict from a false
active claim. All 18 traces then passed.

Rerunning a saved trace validates the grading contract; it is not a fresh model
evaluation. The Python suite also feeds incorrect order, fake results, wrong IDs,
unrequested budgets, missing evidence, and forbidden lifecycle actions to the
grader and requires rejection. Review the natural-language response separately:
the deterministic grader covers state/actions, not every wording or product choice.

For a new authorized forward test, give an independent agent only the skill,
relevant references, and raw cases. Use a disposable directory for outputs and
forbid real host calls. Real host discovery and native activation require separate
authorized checks with captured host state and actual workspace evidence.

## Optional Claude model-backed cases

All seven cases run in Claude Code, with the system prompt telling the model it is in Claude Code 2.1.263 and has no goal tool. Each case runs once, with at most 8 turns and a 240-second timeout, against a copy of the `fixtures/sample-repo` workspace (one passing and one deliberately failing unittest).

| Case | Tags | Checks |
| --- | --- | --- |
| `draft-only` | draft | Draft mode returns a five-field brief and a canonical `/goal` block, implements nothing, and never claims a launch. |
| `explicit-run-handover` | launch | Explicit run mode hands over the exact `/goal` block, says it cannot launch, offers `or stop after N turns`, and mentions permission mode and that a new `/goal` replaces an active one. |
| `active-goal-conflict` | lifecycle | With a goal already active, warns that a new `/goal` replaces it and asks how to proceed (or offers `/goal clear`) instead of saying "paste it now". |
| `new-task-unavailable` | launch | A requested new Codex task is reported as unavailable in Claude Code; the reply is a copy-ready prompt or a question, never a claimed launch. |
| `budget-requested` | launch | A requested token budget gets "Claude Code has no native token budget" plus the textual turn clause; no budget is claimed as applied. |
| `evidence-before-completion` | completion | Completion is reported only after running `python3 -m unittest discover -s tests` and showing its output; the fixture fails, so the goal is reported as not met. |
| `already-precise-defers` | draft | An already-precise `/goal` is deferred to native `/goal` instead of being rewritten into a brief. |

Every case also carries a `skill-invoked` grader (`tool_used: Skill`, `arm: with-only`), the plugin-fired indicator that shows the skill, not baseline Claude, produced the behavior. This same grader is scored under `--ablation none` and becomes an unscored plugin-fired indicator only under `--ablation with-without`, so a run with `--ablation none` should expect it to count.

## What it cannot test

Codex-only routes have no counterpart in Claude Code and are not covered here:

- current-task launch through `get_goal` and `create_goal`, including `token_budget` passing;
- new-task launch: `list_projects`, `create_thread`, worktree and `startingState` selection, the recursion guard, and resolving a real `threadId` with `list_threads`, `wait_threads`, or `read_thread`;
- `update_goal` with the `complete` and three-turn `blocked` rules;
- `/goal edit`, `/goal pause`, and `/goal resume`.

The simulated trace cases cover those routing decisions without a real host.
Actual Codex Goal execution, discovery, and runtime integration remain separate
manual acceptance checks. Kimi model-backed execution is also not covered by the
Claude runner.

## Layout

```text
evals/
├── README.md
├── .gitignore                 (ignores results/)
├── runtime_cases.json         fixed prompts and simulated host responses
├── fixtures/runtime-traces/   saved independent forward-test responses
├── fixtures/sample-repo/      shared workspace: README.md, AGENTS.md, src/calc.py, tests/test_calc.py
└── <case>/
    ├── case.yaml              schema_version "1.1", tags, runs, scaffold_script, execution settings
    ├── prompt.md              the user prompt (body only; case.yaml carries the settings)
    ├── scaffold.sh            copies fixtures/sample-repo into the sandbox cwd
    └── graders/*.md           one grader per file; frontmatter `type:` is regex, tool_used, or llm
```

The runner merges `case.yaml` with `prompt.md` and `graders/*.md` in the same directory. Case-authored paths such as `scaffold_script` must stay inside the case directory (`..` is rejected), and the sandbox cwd starts empty, so each case carries its own `scaffold.sh` that copies the shared fixture in. `context.add_dirs` is not used: it only grants read access in place and never tells the model where the directory is.

## Run

Run from the repository root. Two flags are always required: `--scaffold` (runs each case's `scaffold.sh`, off by default) and `--allow-tools Bash` (a case's `allowed_tools: [Bash]` is honored only with this operator grant; without it `evidence-before-completion` cannot run the tests).

Cheap check, one run per case, no baseline arm, results kept local:

```bash
claude plugin eval ./goal-orchestrator --ablation none --runs 1 --no-publish --max-cost-usd 10 \
  --scaffold --allow-tools Bash --json goal-orchestrator/evals/results/latest.json
```

Threshold run for CI, failing when any case scores below 0.75:

```bash
claude plugin eval ./goal-orchestrator --ablation none --runs 1 --no-publish --max-cost-usd 10 \
  --scaffold --allow-tools Bash --threshold 0.75 --json goal-orchestrator/evals/results/latest.json
```

With-without ablation, adding a no-plugin baseline arm and reporting the score delta:

```bash
claude plugin eval ./goal-orchestrator --ablation with-without --runs 1 --no-publish --max-cost-usd 20 \
  --scaffold --allow-tools Bash --json goal-orchestrator/evals/results/ablation.json
```

Useful variations: `--case draft-only` or `--tag launch` to filter, `--judge-model sonnet` for a stronger LLM judge (the default is haiku), and `--keep-temp` to inspect the scaffolded sandbox after a failure. Results also land in `goal-orchestrator/evals/results/<timestamp>/`, which is gitignored.

## Early access gate

`claude plugin eval` is early access. On an account without access, every invocation (including `claude plugin eval init`) prints exactly:

```text
`plugin eval` is currently in early access
```

and exits 1 before reading any case. The suite is kept structurally complete so it runs unchanged once the gate opens; until then, validate it with the structural checks below.

## Structural checks without the runner

```bash
# every case.yaml and grader frontmatter parses, from the repository root
uv run --quiet --with pyyaml python - <<'EOF'
import re, yaml
from pathlib import Path
root = Path("goal-orchestrator/evals")
for case in sorted(p for p in root.iterdir() if (p / "case.yaml").exists()):
    yaml.safe_load((case / "case.yaml").read_text())
    for g in sorted((case / "graders").glob("*.md")):
        fm = re.match(r"^---\n(.*?)\n---\n", g.read_text(), re.DOTALL)
        assert fm and yaml.safe_load(fm.group(1))["type"], g
    print("ok", case.name)
EOF

# the fixture fails exactly one test, as evidence-before-completion expects
(cd goal-orchestrator/evals/fixtures/sample-repo && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests)
```

## Cost

Seven cases, one run each, one LLM grader per case: roughly one to five US dollars per full run with the default agent model (the skill and fixture add about 10k tokens of context per turn, and each case takes a few turns). The with-without ablation doubles the agent runs. LLM grading on haiku is a few cents. `--max-cost-usd 10` is a safe ceiling for the single-arm runs.
