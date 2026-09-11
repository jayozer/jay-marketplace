# Verification records

Use one `Verification:` bullet per executable check or human criterion. A file mentioned for inspection is not an executable check. The optional repository helper never executes legacy prose or arbitrary Markdown code spans.

```text
Verification:
- Command: {"command": "pytest -q", "cwd": ".", "expected_exit": 0, "evidence": "show the test summary"}
- Command: {"command": "pytest -q tests/auth", "cwd": ".", "expected_exit": 0}
- File: Inspect `scripts/setup.sh` and cite the lines that preserve existing data.
- Manual: Confirm the documented navigation matches the two supplied screenshots; record the comparison.
```

`Command:` takes a single-line JSON object. `command` and `cwd` are required nonempty strings. The optional `expected_exit` defaults to `0` and must be an integer from 0 to 255. Optional `evidence` names output to surface. Every check is required. Unknown or duplicate fields and malformed records are errors. Keep command bytes intact, including quoting and punctuation. Use JSON escaping inside strings; do not wrap the record in Markdown backticks.

Each record retains its declared directory. For the repository helper, a relative `cwd` resolves against the goal file's directory, or the invocation directory for literal goals; `--cwd` explicitly supplies a different base. Absolute directories stay absolute. The execution plan shows resolved directories and source files. The same command in two directories is two executions; exact command/directory pairs execute once and every record's expected status is evaluated independently.

Template placeholders must be replaced before execution. Missing executables, permission errors, shell syntax failures, timeouts, and unexpected exit statuses fail verification. An expected `127` does not excuse a missing executable. Ordinary prose remains a pending manual criterion, even if the lint helper can suggest a command from it.

In explicit command strings, reserve `[TEST COMMAND]` or `<command>` for authoring placeholders. Dollar expressions such as `$HOME` and `${NAME}`, and brace expressions such as awk's `{print}`, are treated as executable syntax rather than placeholders. The helper does not prove that referenced variables are set. Prose, directory, and evidence fields retain the broader placeholder checks; directories are literal paths, not shell-expanded strings.

## Interpreting helper results

The repository's `benchmark_goals.py` is optional authoring tooling; it is not the native Goal runtime and is not included in a standalone skill copy.

| Operation | Result means |
| --- | --- |
| `--mode template` (default) | `STRUCTURE_ONLY`: headings, fields and size were checked; no readiness or completion claim |
| `--mode readiness` or `--strict` | `READY`: structural checks passed and detected placeholders/decisions are resolved; verification has not run |
| `--test-commands` | Prints the explicit plan, returns `PENDING` or `MANUAL`, executes nothing |
| `--test-commands --yes` | Runs explicit checks after readiness passes; reports `PASS`, `FAIL`, or outstanding `MANUAL` evidence |

The last operation returns exit `0` only for passing executable checks with no outstanding manual evidence; failures return `1`, no goals `2`, and pending commands or manual checks `3`. `--allow-empty` changes an empty scan to `EMPTY_ALLOWED` with exit `0`. Inspect `summary.status`: structure/readiness/allowed-empty success is never verification success. Parser diagnostics block execution. `--timeout` bounds each check; checks do not inherit standard input.

The helper cannot determine whether a weak human criterion proves the outcome, whether an observation was actually made, or whether execution has been authorized. The coordinating agent remains responsible for scope, concrete evidence, and any human decision before completion.
