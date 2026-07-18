# Test Suite Goal Template

## When to Use This Template

Use this template when creating or expanding test coverage for existing code.

## Brief Template

```
Build or deliver [TEST COVERAGE] for [MODULE/FEATURE].
It should include [TEST TYPES], with [COVERAGE TARGETS] and [TEST QUALITY STANDARDS].
Make it meet [RELIABILITY BAR], using [TESTING FRAMEWORK], [MOCKING STRATEGY], and [CI INTEGRATION].
Output as [ARTIFACT OR FORMAT].
```

## Example Brief

```
Build or deliver comprehensive test suite for user authentication module.
It should include unit tests for all functions, integration tests for API endpoints, and edge case tests for error scenarios.
Make it meet 80% code coverage with all critical paths covered, using Jest, mocking external services, and GitHub Actions integration.
Output as test files with coverage report and CI configuration.
```

## Goal Condition Template

```
/goal Create test suite for [MODULE] with [COVERAGE TARGET] coverage.
Done only when [COVERAGE COMMAND] shows [TARGET]% coverage and [TEST COMMAND] exits 0, proven by running both commands and showing their output in this conversation.
Constraints: Do not modify production code; use existing test patterns; mock external dependencies.
Stop after 25 turns if not met and report what remains.
```

## Example Goal Condition

```
/goal Create test suite for authentication module with 80% code coverage.
Done only when npm run coverage shows 80%+ coverage and npm test exits 0, proven by running both commands and showing their output in this conversation.
Constraints: Do not modify production code; use existing Jest patterns; mock database and external APIs.
Stop after 25 turns if not met and report what remains.
```

## Verification Methods

- **Run tests:** `npm test`, `pytest`, `go test ./...`
- **Check coverage:** `npm run coverage`, `pytest --cov`, `go test -cover`
- **Check specific coverage:** `pytest --cov=module tests/`
- **CI verification:** Ensure tests pass in CI environment

## Coverage Targets by Module Type

- **Critical business logic:** 90%+ coverage
- **API endpoints:** 80%+ coverage
- **Utility functions:** 95%+ coverage
- **Configuration:** 70%+ coverage
- **UI components:** 60%+ coverage (visual testing separate)

## Common Constraints

- Do not modify production code (unless fixing bugs found)
- Use existing test patterns and framework
- Mock external dependencies (database, APIs, file system)
- Write descriptive test names
- Test both happy path and error cases
- Include edge cases and boundary conditions

## Pre-Flight Checklist

- [ ] Module to test is clearly identified
- [ ] Testing framework is already set up
- [ ] Coverage tool is configured
- [ ] Mocking strategy is defined
- [ ] Coverage target is realistic
- [ ] Turn limit set appropriately (20-30 turns)

## Subgoal Splitting Pattern

For large modules, consider splitting into:

1. **Unit tests** - Test individual functions/methods
2. **Integration tests** - Test component interactions
3. **Edge case tests** - Test boundary conditions
4. **Error handling tests** - Test error scenarios
5. **Performance tests** - Test performance characteristics
6. **Setup/teardown** - Test configuration and cleanup

## Test Quality Standards

- **Descriptive names:** `test_userLogin_withValidCredentials_returnsToken`
- **Arrange-Act-Assert:** Clear test structure
- **Independence:** Tests don't depend on each other
- **Fast:** Unit tests should run in milliseconds
- **Deterministic:** Same result every time
- **Maintainable:** Easy to understand and modify

## Recovery from Stuck Goals

If the goal loops without progress:

1. Check if coverage target is realistic for the module
2. Verify mocking strategy is working correctly
3. Break into supervised orchestration by test type
4. Run `/goal clear` and restart with lower coverage target
