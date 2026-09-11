# Goal with explicit executable and manual checks

Use this pattern from the target project. Replace the paths and checks with those
actually discovered in that project. Preview with `--test-commands`; execute only
the intended records with `--test-commands --yes --cwd /path/to/project`.

```text
/goal Correct addition in src/calc.py and document the result without changing the public function signature.

Done when:
- Addition returns the correct result for the existing passing and failing test cases.
- The README accurately describes how to run those tests.

Constraints:
- Preserve unrelated changes; do not commit, push, or publish.

Verification:
- Command: {"command": "python3 -m unittest discover -s tests", "cwd": ".", "expected_exit": 0, "evidence": "show the test count and OK summary"}
- File: Inspect README.md and cite the test invocation.
- Manual: Compare the diff with the two acceptance criteria; record why each is met.

If blocked:
- Report attempts, failing output, remaining criteria, and the input needed to proceed.
```

Even after the executable check passes, the helper returns `MANUAL` for this
example's file/diff criteria. It cannot observe reviews performed outside the
helper. The coordinator records those reviews separately and requires their
evidence before native completion.
