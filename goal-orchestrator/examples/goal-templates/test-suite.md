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

Done when:
- Critical behavior, failure paths, and edge cases have deterministic coverage.
- Coverage reaches [COVERAGE TARGET] without weakening existing tests.

Constraints:
- Do not modify production code.
- Use existing test patterns and mock external dependencies.

Verification:
- `[COVERAGE COMMAND]` shows [TARGET]% coverage; show the coverage total.
- `[TEST COMMAND]` exits 0; show the test summary line.

If blocked:
- Report what was tried and what would unblock progress, then stop.
```

## Example Goal Condition

```
/goal Create test suite for authentication module with 80% code coverage.

Done when:
- Authentication success, validation, authorization, expiry, and error paths are covered.
- Coverage reaches at least 80% without weakening existing assertions.

Constraints:
- Do not modify production code.
- Use existing Jest patterns and mock the database and external APIs.

Verification:
- `npm run coverage` shows at least 80% coverage; show the coverage total.
- `npm test` exits 0; show the test summary line.

If blocked:
- If coverage cannot reach 80% without weakening assertions, report the gap and ask whether to lower the target.
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
- [ ] Goal body is within 4,000 characters
- [ ] Commit, push, and publication authority are explicit

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
4. Ask the user to edit, pause, or clear the goal before changing the coverage target
