---
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---
Here's a goal I wrote for this repo. Is it ready to run as-is with /goal, or is something missing?

/goal Make add(a, b) in src/calc.py return the sum so that all calc tests pass.

Done when:
- python3 -m unittest discover -s tests reports OK with 2 tests run.
- src/calc.py still defines add(a, b) with the same name and two positional parameters.

Constraints:
- Do not modify tests/test_calc.py.
- Do not add dependencies, commit, or push.

Verification:
- Command: {"command": "python3 -m unittest discover -s tests -v", "cwd": ".", "expected_exit": 0, "evidence": "show both test names and the final OK line with Ran 2 tests"}
- Manual: show the final contents of src/calc.py and confirm the return expression is a + b.

If blocked:
- Report which test still fails and the exact assertion output.
