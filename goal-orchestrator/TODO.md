# TODO

## SKILL.md: require Command records to name the output that proves the check

**Filed:** 2026-09-14, from the draft-mode eval suite (`evals/11-` to `evals/17-`).

**Problem.** In section 4 ("Draft the Native Goal"), the template shows
`"evidence": "<output to show>"` but never says the field must name what the
output has to contain. In practice the skill sometimes emits
`"evidence": "stdout"` or `"evidence": "full output"`, which tells the executor
nothing about what a passing run looks like. Case `15-draft-oversized-context`
failed its `verification-names-evidence` grader in 3 of 3 runs on exactly this;
case `13-draft-vague-define-done` failed once on `"evidence": "clean output"`.

**Change to make.** In SKILL.md section 4, after the template, add a rule along
the lines of:

> Each Command record's `evidence` field names what the output must show: the
> summary line, the printed value, the exit code, or the file content to quote.
> A bare "stdout", "output", or "passes" is not evidence.

Consider the same sentence in `references/verification.md` where the record
schema is defined, and in `examples/verification-goal.md`.

**How to verify.** Re-run the draft-mode suite:

```bash
claude plugin eval . --tag draft-mode --ablation with-without --scaffold --judge-model sonnet --max-cost-usd 12
```

The `verification-names-evidence` grader on cases 11 to 15 should pass in the
with-plugin arm; case 15's with-arm score should move from about 0.84 toward
1.00. Baseline (without-plugin) scores should not change.

**Not done during eval authoring** because the plugin under test is read-only
while its suite is being calibrated.
