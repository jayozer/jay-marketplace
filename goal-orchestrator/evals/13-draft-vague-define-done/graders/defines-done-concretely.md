---
type: llm
focus: last_message
---
Pass only if all of the following hold:
1. The response produces a /goal block with a Done when section; it does not stop at a list of questions with no draft.
2. Every Done when bullet is observable and checkable (for example: all tests pass with a shown summary line, a pyproject.toml exists and the package installs, a README documents usage). A bullet like "code is clean" or "production quality" with no observable check fails.
3. The Done when bullets are specific to this package (a Python package with src/calc.py and unittest tests), not a generic checklist that never references anything in the repo.
4. Any decision the response leaves open for the user is listed explicitly with a stated default, rather than blocking the draft on it.
