---
type: llm
focus: last_message
---
Look only at the Verification section of the /goal block in the response.

Pass only if every bullet in that section names the concrete output that proves its criterion. Acceptable forms:
- A Command bullet whose "evidence" field (or trailing prose) says what must appear in the output, for example "the unittest summary line showing Ran 2 tests and OK", "stdout must read 5", "the OK line with the test count", or "exit code and the stderr message". The exact test name or count does not need to be quoted, but the bullet must say what to look for.
- A Manual bullet that names the file, diff, or observation to show and what it must contain.

Fail if any Verification bullet gives only a command with an evidence field such as "stdout", "output", or "full output" that names nothing to look for, or only says that tests pass or a command exits 0, or if the /goal block has no Verification section.
