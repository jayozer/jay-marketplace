# Goal Orchestrator implementation follow-up

Implemented September 10, 2026 (PDT), in `/Users/acrobat/GitHub/jay-marketplace` on
`main`, starting from clean commit `03949b1` (merged PR #7).

This follows the [September 7 review](goal-orchestrator-2026-09-07.md). PR #7 had
already repaired several parser and command-runner defects, corrected recovery
language, added Claude acceptance fixtures, and introduced CI. This change
preserves that work and completes the explicit verification format, bundled
platform instructions, source auditing, behavioral cases, and documentation.

## Review findings mapped to changes

| Finding | Resulting behavior | Main evidence |
| --- | --- | --- |
| R1: file references could execute | Only explicit `Command:` JSON records execute. File references and prose remain manual evidence. `--test-commands` previews the full source/command/directory plan; `--yes` executes it only after readiness passes. | `verification_checks.py`; `test_explicit_checks.py` verifies inspect-only files never run and preview creates no marker. |
| R2: failed checks returned success | Each required record is compared with its explicit expected exit status. Unexpected statuses, timeouts, and launch failures fail the aggregate result. `can_run` remains a launchability field. | `test_benchmark_goals.py` and `test_explicit_checks.py` cover exit 7, expected nonzero status, missing executables, timeout cleanup, and stdin isolation. |
| R3: checks disappeared | Commands preserve quoting and punctuation. Execution deduplicates only exact command/resolved-directory pairs; each record's expected result is still evaluated. Legacy extraction is retained only for migration suggestions. | `test_explicit_checks.py` covers distinct directories, command prefixes, punctuation, and duplicate records with different expectations. Existing mixed-prose extraction regressions remain. |
| R4: extraction silently shortened goals | Blank-separated bullets and wrapped/multiple-sentence objectives are supported. Unsupported continuations have source locations and block execution. JSON retains the raw body, source spans, and rejected source excerpt; Markdown diagnostics show the rejected tail too. | `test_goal_parsing.py` covers spacing, CRLF, wrapped objectives, source spans, rejected continuations, and diagnostic CLI output. |
| R5: empty/template input looked verified | Empty input returns `NO_GOALS`/exit 2 unless `--allow-empty` is explicit. Template structure, readiness, executed checks, and manual evidence have separate results. Readiness detects placeholders, missing required fields, and `Decisions needed:` items. | Empty-input and readiness regressions; smoke assertions require `STRUCTURE_ONLY` for the 10 template/example blocks. |
| R6: conflicting architecture/recovery guidance | Root architecture, package README, and guide describe the shared planning workflow and distinct native execution paths. Existing explicit-user-direction recovery text is retained. | Documentation diff; skill content/link validation. |
| R7: incorrect Claude invocation | Invocation/install tables distinguish Codex, personal Claude, namespaced Claude plugin, and Kimi. Standalone instructions copy the entire skill directory with its references. | Root/package README and bundled references; both Claude manifests and a disposable standalone copy validate. Actual host discovery remains manual. |
| R8: platforms left to model invention | One shared entrypoint selects Codex, Claude Code, or Kimi Code instructions. They define capability checks, conflicts, launch/handover, budgets, lifecycle, evidence, and unavailable-host behavior. Both Codex destinations require matching native state evidence. Kimi parsing excludes its lifecycle commands. | Three runtime references; 18 fixed-response cases, a trace grader, 17 behavioral contract tests, and one saved independent forward test. |

The brief scaffold and bundled artifact reference now include source provenance,
unresolved decisions, an acceptance-to-evidence map, iteration records, and an
unsuccessful stopping report. The generator explicitly labels its metadata-based
output as a draft; it does not claim to inspect Git state or prove readiness.

The standalone skill contains all linked instructions and artifact formats.
Repository helpers and example projects remain optional plugin-level authoring
tools and are documented as such. Runtime references carry a September 10 source
check date and official links. The former CI prohibition on Kimi wording was
removed because it contradicted this review's requested Kimi support.

## Verification helper migration

Native goals can still contain prose verification. To execute a check through the
repository helper, replace inferred shell prose with one explicit record per
verification bullet:

```text
- Command: {"command": "pytest -q", "cwd": ".", "expected_exit": 0, "evidence": "show the test summary"}
- File: Inspect README.md and cite the documented invocation.
- Manual: Record how the diff meets the acceptance criteria.
```

Relative check directories resolve against the goal file's directory, or the
invocation directory for a literal goal. `--cwd` supplies an explicit base.
Commands with the same text in different directories remain separate executions.

| Operation/result | Exit | Meaning |
| --- | --- | --- |
| Template `STRUCTURE_ONLY` | 0 | Structural lint passed; placeholders may remain. |
| Readiness `READY` | 0 | Detected structural/placeholder/decision issues are absent; verification has not run. |
| Executed `PASS` | 0 | All explicit checks passed and no manual criteria remain in this helper input. |
| `FAIL` | 1 | Input, structural, readiness, or executable verification failed. |
| `NO_GOALS` | 2 | No goal found; `--allow-empty` explicitly changes this to `EMPTY_ALLOWED`/0. |
| `PENDING` or `MANUAL` | 3 | Commands were previewed or human/file evidence remains outstanding. |

Consumers must inspect `summary.status`; exit 0 alone is not a completion verdict.
`--strict` aliases `--mode readiness`. Parser diagnostics prevent execution.
The helper cannot judge whether a human criterion is strong enough, observe an
external review, or establish authority to execute. The coordinator records and
assesses manual evidence separately before native completion.

## Validation evidence

| Check | Result | Scope |
| --- | --- | --- |
| Python regression suite | PASS, 127 tests | Local synthetic parser, helper, routing-contract, and CLI behavior. |
| Smoke suite | PASS, 14 checks | Helper integration, 10 template/example blocks, package validation, and a disposable standalone copy. The full suite passed before the final Markdown diagnostic-output refinement; all 127 unit tests passed afterward. |
| Independent forward test | PASS, 18 simulated cases | An independent agent read only the skill/references and raw fixed-response cases, then produced reviewable traces without actual host calls. |
| Trace grading contract | PASS | Negative cases reject wrong order/IDs, forged results, unrequested budgets, conflicts, and completion without required evidence. Saved traces are also checked in CI. |
| Skill creator/frontmatter/content validation | PASS | Skill metadata, required sections, bundled references, and local anchors. |
| Claude marketplace and plugin manifests | PASS, both | `claude plugin validate .` and `claude plugin validate ./goal-orchestrator`. |
| Live Codex/Claude/Kimi native Goal launch | NOT RUN | No actual launch, evaluator, or model-reliability claim. |
| Discovery in installed Codex/Claude/Kimi hosts | MANUAL | Installation paths and manifest structure are documented; no installed skill was updated in this task. |
| Optional Claude paid model-backed runner | NOT RUN | Existing seven cases remain available; no provider evaluation was invoked. |

The saved forward trace is under
[`evals/fixtures/runtime-traces`](../goal-orchestrator/evals/fixtures/runtime-traces/forward-2026-09-10.json).
Replaying it validates the grader and fixture contract, not fresh model behavior.
Mock state responses normalize observed host state; they do not validate actual
desktop API response parsing. The evaluator initially rejected a correctly
reported activation mismatch; a targeted regression corrected that grader bug.

Re-run local checks from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/goal-orchestrator-review-uv uv run --with pyyaml bash goal-orchestrator/scripts/smoke_test.sh
PYTHONDONTWRITEBYTECODE=1 python3 goal-orchestrator/scripts/grade_runtime_trace.py goal-orchestrator/evals/fixtures/runtime-traces/forward-2026-09-10.json
claude plugin validate .
claude plugin validate ./goal-orchestrator
git diff --check
```

The timeout cleanup tests need local process inspection (`ps`). They passed with
that capability available; a sandbox denying process inspection cannot establish
the cleanup assertion. These are local checks, not hosted CI or production proof.

Remaining manual acceptance is to install/discover the revised skill in each
host and capture actual activation/handover state in disposable workspaces when
requested. No commit, push, release, installation, or native Goal was performed
by this implementation task.
