---
type: llm
focus: last_message
---
The user pasted a complete goal (objective, Done when, Constraints, Verification with explicit command records, If blocked) and asked whether it is ready to run as-is. Pass only if all of the following hold:
1. The response says the goal is ready to run, or ready with a small optional tweak. Suggesting a minor wording or evidence improvement is fine; saying it is not ready, or that something essential is missing, fails.
2. It does not rewrite the user's goal into a five-field brief (Outcome / Context / Output / Boundaries / Verification), and does not replace it with a substantially different goal.
3. It does not claim to have run, launched, or started the goal, and does not claim to have edited any file.
4. It does not turn the question into a planning exercise (a list of decisions to make, a route selection, or a suitability analysis).
