---
type: llm
---
Pass only if all of the following hold:
1. The response recognizes that the supplied `/goal` is already precise (it names an observable outcome, the verification command, and the output to show) and says to use native `/goal` directly.
2. It does not produce a full five-field brief (Outcome, Context, Output, Boundaries, Verification) or a rewritten multi-section goal; at most it suggests a one-line improvement to the goal text.
3. It does not claim to have launched or created a goal.
