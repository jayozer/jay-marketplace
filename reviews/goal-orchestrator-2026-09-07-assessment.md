# Assessment of `reviews/goal-orchestrator-2026-09-07.md`

Final report, 2026-09-08. Covers a claim-verification pass (13 adversarial verifiers, every R-item reproduced with real commands and every doc claim checked against fetched pages), a six-lens completeness pass hunting for what the review missed, and a two-skeptic refute panel over the 43 candidate additions that pass produced. Repo state: branch `review` at `c08f182`, clean tree. Nothing in the repo was modified.

## Bottom line

The review is factually accurate and the code defects are real. All eight numbered items reproduce, the four "What works" and "Verification performed" sections check out, and the Codex, Claude, and Kimi documentation claims are correct (seven of seven Claude facts, all five Codex facts, all Kimi URLs resolve and say what the review says).

I disagree with the review's priorities, its scope, and about half of its proposed fixes:

1. It ranks five helper-script bugs above every prose defect, but the scripts are not on any execution path. `SKILL.md` and `agents/openai.yaml` are the only files a standalone install ships, and neither mentions `benchmark_goals.py`, `--test-commands`, or `scripts/` at all. The skill prose is what runs on every invocation.
2. It treats Kimi as a deliverable for a repo with zero Kimi references, and it lists Kimi lifecycle parsing under "Defects reproduced" for a parser whose docstring says "Codex /goal blocks".
3. It under-argues the one platform gap that matters for how you use this: Claude Code has no model-callable goal tool, so the skill's run mode cannot execute there, and the skill never says to hand back the `/goal` text instead.
4. Several proposed fixes redesign the verification-clause format or add modes and schemas where a few lines suffice.

## Verdict per item

| Item | Reproduces | Severity | Fix proposed by review | My view |
| --- | --- | --- | --- | --- |
| R1 backticked file executed | Yes, exactly | High is overstated. Medium, unless justified by the directory-scan amplification the review omits | Explicit check records, new format | Over-scoped. Fix inside the script. |
| R2 failed command, exit 0 | Yes, plus timeout and exit-127 paths | Medium. Same class as R5, which the review rates Medium | Tri-state results, declared expected statuses | Over-scoped. Nine-line fix, prototyped, 16 tests still pass. |
| R3 commands dropped | Yes, both rows | Medium at the upper bound. Only bites once R2 is fixed | Per-check parse, exact dedup | Right direction. Delete the prefix dedup outright. |
| R4 blank line truncates | Yes; line cites are 85 and 110, not 73-108 | Medium, low edge. Broader than "spacing" | Support loose lists and wrapped objectives, or diagnose | Loose lists: two lines. Wrapped objectives: diagnose, do not guess. |
| R5 empty input exits 0 | Yes, also 0-byte file, empty dir, and lifecycle literals | Low-Medium | No-goals error plus template/readiness modes | Mirror the three-line guard in `extract_goal.py`. Modes are YAGNI. |
| R6 ARCHITECTURE contradicts skill | Yes | Medium, but the two halves are in the wrong order | Reconcile the package | `refactor.md:130` should lead. It is the only template the Codex-first commit missed. |
| R7 wrong Claude invocation | Yes, confirmed against live docs | Medium | Four-row invocation table incl. Kimi | Right fix, drop the Kimi row. |
| R8 runtime compat | Partially. Facts right, framing wrong | Split it | Runtime selection, capability check | Claude gap deserves its own finding. Kimi is scope, not a defect. |

## Where the review is right and I would keep it

- The five reproductions in R1 to R5 are exact. Cited line ranges are accurate except R4 (the two `break` statements are at `goal_parsing.py:85` and `:110`) and R1's `72-89`, which stops mid-call at line 89 while `shell=True` sits inside it at line 84.
- The Claude Code facts: transcript-only small-model evaluator, three verdicts, replacement on a new `/goal`, `/goal` and `/goal clear` only, 4,000-character limit, textual turn clause, hooks and trust can disable. Seven of seven verified against `code.claude.com/docs/en/goal`, and the 4,000 limit was also confirmed with a live `claude -p` probe that returned "Goal condition is limited to 4000 characters (got 4118)".
- R7's namespace rule. The docs say plugin skills become `/plugin-name:skill-name`, so the rename changed the Claude command from `/agent-workflow-kit:goal-orchestrator` to `/goal-orchestrator:goal-orchestrator`. The review's sentence at `README.md:70` is wrong as written.
- The "three consecutive goal turns" rule matches Codex's runtime contract. It appears nowhere in public docs, but `strings` on the installed `codex` 0.151.0 binary contains the `update_goal` tool text word for word.
- The `onMissing: "create-branch"` claim is true. The `create_thread` schema is cached in `~/.codex/.codex-global-state.json` and says exactly that.
- "Seven of the 16 unit tests assert wording" is exact. Local versions all match.

## Where I disagree

**Priority inversion.** The review says "Repair the verification helpers first." The scripts live at `goal-orchestrator/scripts/`, outside the skill directory, and no install command copies them. `grep` of `SKILL.md`, `GUIDE.md`, and `openai.yaml` for `benchmark`, `script`, or `.py` returns only the frontmatter line. The README already says `--test-commands` "executes shell content from the input", and the flag's help text says "use with caution". These are bugs in optional dev tooling. They matter to a maintainer running the benchmark in CI, but there is no CI, Makefile, or pre-commit in the repo. The review should say plainly that R1 to R5 do not change what the agent does.

**R1 is under-described and over-rated at the same time.** The headline blames backticks, but the prose path (no backticks) executes just as readily: `proven by running rm -rf ./prose-target` deleted the directory in a scratch run. Directory scanning runs every `/goal` block in every non-hidden `.md` file, and the block finder does not track code fences, so documentation examples count as goals. A repo-root dry run of this kit would attempt `npm test`, `pytest -q`, `ruff check .`, `npm run coverage`, `spectral lint openapi.yaml`, and the `<broader command>` placeholder from `GUIDE.md`. If R1 keeps High, that amplification is the reason, and the review does not mention it.

**R2's proposed fix is a redesign.** There is no check schema in which an "expected nonzero status" could be declared, and every template and the extractor regex only recognize `exits 0`, `passes`, and `shows`. The nine-line alternative (any `command_tests` entry with `can_run` false or nonzero exit becomes an issue) was prototyped and makes exit 7, exit 127, and timeout all exit 1 while leaving the no-flag path byte-identical. Two companion changes the review misses: smoke step 8 runs under `set -uo pipefail` and asserts nothing about the exit status, so it turns red the moment R2 is fixed and should become the regression test; and the hard-coded 30-second timeout will produce false failures on real suites once timeout counts as failure, so a `--timeout` flag is needed alongside.

**R8 mischaracterizes the Claude section.** "Left to the model to invent" is wrong. `SKILL.md:141-143` explicitly says to translate from current Claude Code documentation and not to assume Codex tool names. The accurate and stronger criticism: Claude Code exposes no model-callable goal tool. `/goal` is a user-typed command, the Skill tool refuses it ("goal is a UI command, not a skill"), and the only model-side primitive in the binary (`ProposeGoal`) is undocumented, flag-gated off, and unavailable in agent contexts. So `SKILL.md:17` "create and pursue a native goal" and `:87` "Create the native Goal with `create_goal`" have no Claude counterpart, and nothing tells the model to hand back the exact `/goal` text. The review's own Claude section contains every fact needed to say this and never connects them to R8. Note the softening: `claude -p "/goal ..."` does run the loop from a shell, so "cannot launch at all" would overstate it.

**Kimi is scope creep.** `grep -ri kimi` outside `reviews/` returns nothing. README calls this "A Claude Code plugin marketplace"; the plugin and skill metadata say Codex. The review's own qualifier ("an unsupported feature area") concedes it. Recommending a Kimi adapter, a Kimi table row, and "three runtime references" turns an unrequested platform into deliverables, and the "unsupported Kimi lifecycle parsing" row under Defects reproduced inflates the count: `/goal replace deprecated API calls` is a legitimate Codex objective. One honest counterpoint: Kimi Code 0.39.1 is installed and authenticated on this machine with sessions from late August, so it is not foreign to you. That makes it an owner decision, not a defect. A one-line "Supported hosts" statement is the proportionate change.

**Recommendation 5 contradicts the review's own praise.** Line 15 credits the brief for exposing decisions "without imposing a long questionnaire". Recommendation 5 then adds five artifact fields. The one addition worth keeping is the cookbook's "blocked stop condition" element, which the review names in the Codex section and then drops.

**Recommendation 6 is partly moot.** "Ship referenced materials in standalone installations" has nothing to ship: `SKILL.md` references no scripts, examples, or guide, and the installed copy is byte-identical to the repo skill directory. "Document Python/PyYAML requirements" is already done in `requirements-dev.txt` and the kit README. What is actually missing is a Python floor and a note that the documented `pip install` fails on Homebrew Python while `smoke_test.sh` already falls back to `uv` silently.

## What the review missed

Most important, given your fire-and-forget use:

- **The canonical goal is judged by an evaluator that reads only the transcript, and the review never asks whether the artifact survives that.** A live probe (Claude Code 2.1.263, `claude -p`, no tools) returned `met: true` for the condition "`pytest -q` exits 0" on the strength of a bare assistant claim, in a repo where pytest was not even installed. Command criteria and review criteria are equally assertion-satisfiable. The fix is the one the review states in passing ("surface decisive evidence in the transcript") and it belongs at the top, not in the Claude comparison paragraph.
- **Permission mode.** The Claude doc says a goal does not change permission mode and Manual mode still prompts before tool calls. A walk-away goal stalls at the first prompt unless auto mode or pre-allowed commands are set. Absent from the review.
- **Turn cap.** `SKILL.md:67` forbids a mandatory textual turn limit. Claude's only bounding mechanism is a textual "or stop after N turns" clause. Your memory note from June wants a hard cap; your own PR #5 on 2026-08-02 removed it and named "required conventional turn caps" as a defect. That is a deliberate owner decision and I would not reopen it, but the Claude reference should offer the optional clause and state that a cap stop is reported as unsuccessful, not complete.
- **A new `/goal` silently replaces the active one**, and there is no model-side way to check goal state in Claude Code. The review's "check the existing condition before replacement" presumes a `get_goal` analogue that does not exist. Both this and the hooks-disabled conditions were in the July version of `SKILL.md` and were removed by the Codex-first commit; they can be recovered from git rather than re-researched.

Smaller items worth folding into existing R-items rather than adding new ones:

- R1: on macOS APFS, sentence-case prose bullets like "Touch base with QA once ..." resolve to real binaries under the prose path. `PRUNED_DIRS` omits `third_party/`. Exit 126 (permission denied) and exit 2 (shell syntax error) are both reported `can_run: true`.
- R2: the single-word command heuristic at `benchmark_goals.py:141` flags `true`, `make`, `pytest`, and `tox` as invalid, so with R2 the exit code is inverted for the simplest pair: `true` exits 1, `false --x` exits 0. Delete the heuristic when R2 is fixed.
- R3: the split on ` and ` mangles quoted arguments (`pytest -k 'a and b'` becomes `b'`), and `cd app; npm test` loses its working directory. The prefix dedup's motivating case (`spectral lint` vs `spectral lint openapi.yaml`) never occurs in any parsed template clause.
- R4: numbered lists, `+` bullets, `**Done when:**`, and `### Done when:` all truncate too. `character_count` is measured on the normalized block, so a 4,151-character pasted body reported 3,956 and passed.
- R5: a nonexistent path that starts with `/goal` (this repo's own directory name with a leading slash) is swallowed as literal goal text. One-character fix: `startswith("/goal ")` at `goal_parsing.py:241`, matching line 63.
- R6: `ARCHITECTURE.md` is stale in more places than 64-99. The overview box at lines 27-28 still says `agent-workflow-kit`, split across two lines so a grep misses it. Line 85 says "4-part ... hard cap". Line 464-465 gives `~/.claude/skills/` as the user-scope plugin path. Lines 498-501 promise a "tool name translation table" that does not exist. Line 505-506 says no Python dependencies.
- R7: your own machine still has `agent-workflow-kit@jay-marketplace` 1.0.0 installed at local scope for `/Users/acrobat/GitHub/gooooal`, and the marketplace checkout is at a pre-rename commit. The documented migration path has never been run. The kit README and GUIDE give no Claude invocation at all.
- Citations: "/goal edit" and the 4,000 limit are confirmed only by the command reference, not the cookbook Goal guide the review cites alongside it. The `~/.codex/skills` path is undocumented on the current build-skills page but is still the default of Codex's own bundled installer and is skill root `r0` in 0.151.0, so "older" undersells it.

## What I would change in the review

Remove:

- The Kimi adapter recommendation, the Kimi table row in R7, and the "unsupported Kimi lifecycle parsing" line under Defects reproduced. Replace with one sentence: supported hosts are Codex and Claude Code; others untested.
- "Template mode vs execution-readiness mode" (R5). A `--strict` flag that fails on unresolved `[...]`/`<...>` placeholders is enough.
- The check-record schema and declared expected statuses (R1, R2, Rec 1).
- "Ship referenced materials in standalone installations" and "document PyYAML" (Rec 6).
- "Check hook availability" as a model step. The doc says the command explains itself when disabled.
- The Codex version trivia (0.151.0 vs 0.128.0).

Add:

- A standalone Claude Code finding: launch is a handover, never an action; emit the exact `/goal` block or a `claude -p` command; every verification bullet must be a command whose output Claude prints; require auto mode or pre-allowed commands; state that a new `/goal` replaces the active one.
- Under R1: the prose path and the directory-scan amplification, plus "restrict `--test-commands` to explicit file inputs or print `source_file` before each run".
- Under R2: smoke step 8 as the regression test, and a `--timeout` flag.
- Under R6: `refactor.md:130` as the lead item with the git evidence that it is the sole unfixed template, and the extra `ARCHITECTURE.md` lines.
- Under R7: the concrete before and after command, and that the migration path has not been exercised locally.
- For the two in-session claims (three-turn rule, `onMissing`): the `strings` and cached-schema evidence, so a reader can check them.

Improve:

- Severity ladder: R1 Medium unless justified by directory scanning; R2 Medium; R5 Low-Medium; split R8 into Claude launch gap (Medium or High), Codex "when available" wording (Low), Kimi (informational).
- Lead the defects list with the skill prose, since that is what executes, and label R1 to R5 as auxiliary-tool bugs.
- Rec 4 should say "supplement" the seven wording tests, not replace them. They are cheap deletion tripwires with no history of breakage. One does pin `$goal-orchestrator` in the kit README, so R7's fix will touch it.

## Second-pass outcome

The completeness pass produced 43 candidate additions after dedup. Each went to two skeptics, one told to reproduce it and one told to argue it does not matter for this kit, both defaulting to "refuted" when uncertain.

- **2 survived both skeptics**, both Low and both in `benchmark_goals.py`: `can_run` is true for exit 126 (found but not executable) and for shell syntax errors (exit 2); and `has_turn_limit` is computed and emitted but nothing consumes it, so a legacy "Stop after N turns" clause produces no issue or summary entry even though `SKILL.md:67` discourages textual turn limits.
- **31 were refuted on materiality only.** Every one of them reproduced. The skeptic's reasons were almost always "fold into Rn" or "the script is off the agent's path". That is a calibration artifact of the panel design, not evidence the candidates are wrong. Their "fold into" notes are the source of the addenda listed under "What the review missed" above.
- **3 were refuted on the text itself** and are dropped: the description "contradicts the body" (the same qualifier appears in both), the subagent authority fence "never propagates" (the brief's Boundaries field carries it), and the worktree "drops the dirty tree" (a fresh worktree leaves the parent's edits intact).
- **10 lost their skeptics to the usage limit.** All Low, all documentation or packaging. I checked each by hand instead of re-spawning agents. All reproduce: no `LICENSE` file despite three manifests declaring MIT; `ARCHITECTURE.md:505` says goal-orchestrator has no Python dependencies while `requirements-dev.txt` pins PyYAML; the kit README's `pip install` fails on Homebrew Python with the PEP 668 externally-managed error and the `uv` fallback in `smoke_test.sh` is undocumented; `ARCHITECTURE.md:498-501` promises a translation table that does not exist; root README and ARCHITECTURE say helpers live in the skill directory and are reached via `${CLAUDE_SKILL_DIR}`, which is true for the other two kits but not this one; verification commands inherit the benchmark's stdin; the migration path has never been run on this machine; one routing test pins `$goal-orchestrator` in the kit README; and the GENERIC_WORDS filter, `--output`, and `estimate_complexity` have no tests. None changes the conclusions above. They belong in one "packaging nits" bullet under Recommendation 6.

## Verification I ran

| Check | Result |
| --- | --- |
| R1 to R5 reproductions with real commands | All reproduce |
| Unit suite | 16 tests, OK |
| Smoke suite via `uv --with pyyaml` | 10 passed, 0 failed |
| `claude plugin validate .` and `./goal-orchestrator` | Both pass |
| `~/.codex/skills/goal-orchestrator` vs repo | Byte-identical, two files |
| Live doc fetches: Codex command reference, cookbook, build-skills; Claude goal, skills, plugins, sub-agents; four Kimi pages | All resolve; claims match |
| `strings` on codex 0.151.0 for the update_goal contract | Present |
| `~/.codex/.codex-global-state.json` for `create_thread.onMissing` | Present |
| Live `claude -p` probes: 4,000 limit, evaluator on bare claims | Limit enforced; evaluator accepted unverified claims |
| Local versions | Python 3.14.3, codex 0.151.0, claude 2.1.263, kimi 0.39.1 |
| Workflow agents | 106 launched, 86 completed, 20 lost to the usage limit (all second-round skeptics on Low items, replaced by manual spot-checks) |
