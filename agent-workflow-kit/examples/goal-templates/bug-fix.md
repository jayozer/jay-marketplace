# Bug Fix Goal Template

## When to Use This Template

Use this template when fixing a specific bug with reproducible steps and clear expected behavior.

## Brief Template

```
Build or deliver [BUG FIX] in [PROJECT/REPO].
It should include [ROOT CAUSE ANALYSIS], with [FIX IMPLEMENTATION] and [REGRESSION PREVENTION].
Make it meet [QUALITY BAR], using [MINIMAL CHANGE PRINCIPLE], [TESTING REQUIREMENTS], and [VERIFICATION STEPS].
Output as [ARTIFACT OR FORMAT].
```

## Example Brief

```
Build or deliver fix for memory leak in image processing module in the web application.
It should include identification of the unclosed file handles, with proper resource cleanup and added monitoring.
Make it meet production stability standards, using minimal changes to existing code, comprehensive edge case testing, and memory profiling verification.
Output as code changes with test cases and performance benchmarks.
```

## Goal Condition Template

```
/goal Fix [BUG DESCRIPTION] without introducing regressions.
Done only when [VERIFICATION COMMAND] exits 0 with all tests passing, proven by running the command and showing its output in this conversation.
Constraints: Make minimal changes; do not modify unrelated code; add regression test for this specific bug.
Stop after 20 turns if not met and report what remains.
```

## Example Goal Condition

```
/goal Fix memory leak in image processing module when processing large files.
Done only when pytest -q tests/test_image_processing.py exits 0 with all tests passing, proven by running the command and showing its output in this conversation.
Constraints: Make minimal changes; do not modify unrelated modules; add regression test for large file processing.
Stop after 20 turns if not met and report what remains.
```

## Verification Methods

- **Reproduce bug first:** Run steps to confirm bug exists
- **Run test suite:** Ensure fix doesn't break existing functionality
- **Run specific test:** Test the exact bug scenario
- **Manual verification:** Follow reproduction steps to confirm fix

## Common Constraints

- Make minimal changes (single-responsibility principle)
- Do not modify unrelated code
- Add regression test for this specific bug
- Do not change API contracts
- Follow existing error handling patterns
- Document the fix in comments/changelog

## Pre-Flight Checklist

- [ ] Bug is reproducible with clear steps
- [ ] Root cause is understood
- [ ] Expected behavior is defined
- [ ] Test suite passes before fix
- [ ] Regression test can be added
- [ ] Turn limit set appropriately (15-25 turns for focused fixes)

## Subgoal Splitting Pattern

For complex bugs, consider splitting into:

1. **Reproduction** - Create minimal reproducible test case
2. **Root cause analysis** - Identify where bug originates
3. **Fix implementation** - Apply minimal fix
4. **Regression testing** - Add test case
5. **Verification** - Confirm fix works and doesn't break others
6. **Documentation** - Update comments/docs if needed

## Recovery from Stuck Goals

If the goal loops without progress:

1. Verify the bug is actually reproducible in current environment
2. Check if test suite has flaky tests
3. Break into supervised orchestration with manual investigation
4. Run `/goal clear` and restart with more specific verification

## Minimal Change Principle

When fixing bugs:
- Change only what's necessary
- Prefer fixing over rewriting
- Maintain existing patterns
- Add tests before fixing (TDD approach)
- Document why the fix works
