---
type: llm
---
Pass only if all of the following hold:
1. The response contains a brief with all five fields labeled Outcome, Context, Output, Boundaries, and Verification.
2. Every bullet under Verification (in the brief and in the /goal block) names the output that must be printed or shown, such as a test summary line, a command's printed output, or `git diff --stat`. A bullet that only says a command passes or exits 0, without naming the output to show, fails this criterion.
3. Nothing was implemented: the response does not claim to have edited src/calc.py or any other file, and does not claim that the failing test now passes.
4. The response does not claim that a goal was created, launched, started, or is active.
