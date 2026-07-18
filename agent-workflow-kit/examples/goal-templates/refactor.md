# Refactor Goal Template

## When to Use This Template

Use this template when refactoring existing code to improve quality, maintainability, or performance while preserving behavior.

## Brief Template

```
Build or deliver [REFACTORING TYPE] for [MODULE/CODEBASE].
It should include [SPECIFIC IMPROVEMENTS], with [BEHAVIOR PRESERVATION] and [TEST COVERAGE].
Make it meet [CODE QUALITY BAR], using [REFACTORING PATTERNS], [SAFETY CHECKS], and [PERFORMANCE TARGETS].
Output as [ARTIFACT OR FORMAT].
```

## Example Brief

```
Build or deliver code quality improvements for the payment processing module.
It should include extracting duplicate logic into reusable functions, improving error handling, and adding type hints.
Make it meet production code quality standards with zero behavior changes, using extract method, replace conditional with polymorphism, and comprehensive test coverage.
Output as refactored code with passing tests and performance benchmarks.
```

## Goal Condition Template

```
/goal Refactor [MODULE] with [IMPROVEMENTS] while preserving all behavior.
Done only when [TEST SUITE] exits 0, [LINTER] passes, and [PERFORMANCE BENCHMARK] shows no regression, proven by running all checks and showing their output in this conversation.
Constraints: Do not change external API contracts; all existing tests must pass; add tests for new code.
Stop after 30 turns if not met and report what remains.
```

## Example Goal Condition

```
/goal Refactor payment processing module with extracted functions and improved error handling while preserving all behavior.
Done only when pytest -q exits 0, ruff check . passes, and benchmarks show no performance regression, proven by running all checks and showing their output in this conversation.
Constraints: Do not change payment API contracts; all existing tests must pass; add unit tests for extracted functions.
Stop after 30 turns if not met and report what remains.
```

## Verification Methods

- **Test suite:** Ensure all existing tests pass
- **Behavior verification:** Run integration tests
- **Linting:** `ruff check .`, `eslint`, `golint`
- **Type checking:** `mypy`, `tsc`, `gotype`
- **Performance:** Benchmark before/after
- **Manual testing:** Verify key workflows still work

## Refactoring Types

- **Extract method/function:** Break down large functions
- **Extract class/module:** Organize related code
- **Replace conditional with polymorphism:** Eliminate complex conditionals
- **Introduce parameter object:** Reduce parameter lists
- **Remove duplication:** DRY principle
- **Improve naming:** Better variable/function names
- **Add type hints:** Improve type safety
- **Optimize performance:** Improve algorithms/data structures

## Common Constraints

- Do not change external API contracts
- All existing tests must pass
- Add tests for new/refactored code
- Follow existing code style
- Maintain backward compatibility
- Document non-obvious changes
- No performance regressions

## Pre-Flight Checklist

- [ ] Current code has test coverage
- [ ] Baseline performance is measured
- [ ] Refactoring scope is clearly defined
- [ ] API contracts are identified
- [ ] Safety checks are in place
- [ ] Turn limit set appropriately (25-35 turns)

## Subgoal Splitting Pattern

For large refactoring, consider splitting into:

1. **Baseline measurement** - Record current test results and performance
2. **Incremental refactoring** - Small, testable changes
3. **Test addition** - Add tests for new code
4. **Verification** - Run tests after each change
5. **Performance check** - Compare against baseline
6. **Documentation** - Update comments/docs

## Refactoring Safety Checklist

- [ ] All tests pass before starting
- [ ] Test coverage is sufficient
- [ ] Changes are made incrementally
- [ ] Each change is tested immediately
- [ ] API contracts are preserved
- [ ] Performance is not degraded
- [ ] Code review is done (if team workflow)

## Recovery from Stuck Goals

If the goal loops without progress:

1. Verify test coverage is adequate for the changes
2. Check if refactoring scope is too large
3. Break into supervised orchestration with smaller changes
4. Run `/goal clear` and restart with more focused scope
5. Consider reverting and trying a different approach

## Refactoring Principles

- **Two hats:** Separate "adding functionality" from "refactoring"
- **Small steps:** Make tiny, verifiable changes
- **Test constantly:** Run tests after every change
- **Preserve behavior:** Refactoring should not change what code does
- **Improve design:** Make code easier to understand and modify
