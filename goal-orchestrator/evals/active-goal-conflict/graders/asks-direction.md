---
type: llm
---
Pass only if all of the following hold:
1. The response warns that running a new `/goal` in Claude Code replaces the currently active goal (`/goal all tests pass`).
2. It asks the user how to proceed, or offers `/goal clear` (or keeping or finishing the existing goal) as an explicit choice, instead of instructing the user to paste or run the new goal immediately.
3. It does not claim to have inspected, cleared, replaced, or launched any goal itself.
