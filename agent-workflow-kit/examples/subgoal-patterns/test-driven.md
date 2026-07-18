# Test-Driven Subgoal Pattern

## When to Use

Use this pattern when test coverage is critical and you want to ensure quality from the start.

## Pattern

Split work into test-writing and implementation phases, with tests driving the development.

## Example: Building a Payment Processing Service

### Subgoal 1: Test Specification
```
Write comprehensive test suite for payment processing service.
Context: Building payment service. Need to ensure all edge cases are covered before implementation.
Deliverable: Test suite with unit tests, integration tests, and edge case scenarios.
Boundaries: Do not implement any payment logic; minimal interface stubs are allowed so the tests import and run.
Verification: Test suite runs and every test fails against the stubbed service — show the failing run output.
Return: summary · test suite · scenarios covered · edge cases identified · acceptance criteria.
```

### Subgoal 2: Core Implementation
```
Implement payment processing logic to pass the test suite.
Context: Test suite is complete from Subgoal 1. All requirements are specified in tests.
Deliverable: Payment service implementation that passes all tests.
Boundaries: Follow test specifications exactly. Do not add untested features.
Verification: All tests from Subgoal 1 pass. No test failures.
Return: summary · implementation code · test results · any test modifications needed.
```

### Subgoal 3: Error Handling & Edge Cases
```
Implement error handling and edge case scenarios from test suite.
Context: Core implementation passes happy path tests. Need to handle errors and edge cases.
Deliverable: Error handling logic, retry mechanisms, graceful degradation.
Boundaries: Do not modify core payment logic. Focus only on error paths.
Verification: All error case tests pass. Edge cases handled correctly.
Return: summary · error handling code · test results · error scenarios documented.
```

### Subgoal 4: Integration & Documentation
```
Integrate payment service with external payment gateway and document usage.
Context: All tests pass from Subgoals 1-3. Service is functionally complete.
Deliverable: Gateway integration, API documentation, usage examples.
Boundaries: Do not modify payment logic. Focus on integration and docs.
Verification: Integration tests with mock gateway pass. Documentation is complete.
Return: summary · integration code · documentation · integration test results · deployment notes.
```

## Synthesis

After all subgoals complete:
1. Verify all tests still pass
2. Run integration tests with real payment gateway (staging)
3. Review test coverage is adequate
4. Document any test modifications or gaps
5. Create test maintenance guide

## Benefits

- High confidence in implementation
- Requirements are explicitly defined in tests
- Easy to refactor when tests are comprehensive
- Edge cases are handled from the start

## Considerations

- Test writing takes time upfront
- Requirements may change during implementation
- Need to balance test coverage with development speed
- Some tests may be expensive to maintain
