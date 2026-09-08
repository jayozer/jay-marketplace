# Feature Build Goal Template

## When to Use This Template

Use this template when building a new software feature with clear acceptance criteria and testable behavior.

## Brief Template

```
Build or deliver [FEATURE NAME] in [PROJECT/REPO].
It should include [CORE FUNCTIONALITY], with [BEHAVIOR/INTERACTION DETAILS].
Make it meet [QUALITY BAR], using [TECHNICAL CONSTRAINTS], [INTEGRATION REQUIREMENTS], and [FINISHING TOUCHES].
Output as [ARTIFACT OR FORMAT].
```

## Example Brief

```
Build or deliver user authentication system in the web application.
It should include login, signup, password reset, and session management, with JWT tokens and secure cookie handling.
Make it meet OWASP security standards, using existing user model, PostgreSQL database, and Express.js framework.
Output as code changes with migration files and API documentation.
```

## Goal Condition Template

```
/goal Implement [FEATURE NAME] with all acceptance criteria met.

Done when:
- Every stated behavior and acceptance criterion works.
- Focused regression coverage protects the new behavior.

Constraints:
- Do not modify [PROTECTED FILES/DIRS] or add dependencies without explicit justification.
- Follow existing architecture and code style.

Verification:
- `[VERIFICATION COMMAND]` exits 0; show the command's output.
- The requested behavior and final diff are reviewed directly; show the behavior demonstration and `git diff --stat`.

If blocked:
- Report what was tried and what would unblock progress, then stop.
```

## Example Goal Condition

```
/goal Implement user authentication system with login, signup, password reset, and session management.

Done when:
- Login, signup, password reset, and session management satisfy the documented API behavior.
- Focused tests cover success, validation, authorization, and expiry cases.

Constraints:
- Do not edit existing migration files or add packages without explicit justification.
- Follow existing Express.js middleware patterns.

Verification:
- `npm test` exits 0 with all authentication tests passing; show the test summary line.
- The API behavior and final diff are reviewed directly; show the API response and `git diff --stat`.

If blocked:
- If session management conflicts with the existing user model, report the conflict and ask before changing the schema.
```

## Verification Methods

Choose based on your tech stack:

- **Node.js/JavaScript:** `npm test` or `yarn test`
- **Python:** `pytest -q` or `python -m pytest`
- **Ruby:** `bundle exec rspec`
- **Go:** `go test ./...`
- **Rust:** `cargo test`
- **Java:** `mvn test` or `gradle test`

## Common Constraints

- Do not modify existing migration files
- Do not break existing API contracts
- Do not add new dependencies without justification
- Follow existing code style and patterns
- Maintain backward compatibility
- Do not modify configuration files in production/

## Pre-Flight Checklist

- [ ] Workspace, sandbox, and approval boundaries are understood
- [ ] Test suite exists and passes baseline
- [ ] Database migrations are reversible
- [ ] Feature has clear acceptance criteria
- [ ] Goal body is within 4,000 characters
- [ ] Commit, push, deployment, and publication authority are explicit

## Subgoal Splitting Pattern

For complex features, consider splitting into:

1. **Database layer** - Schema, migrations, models
2. **API layer** - Endpoints, validation, error handling
3. **Business logic** - Core feature implementation
4. **Integration** - Connecting layers together
5. **Testing** - Unit tests, integration tests
6. **Documentation** - API docs, usage examples

## Recovery from Stuck Goals

If the goal repeats progress without resolving the objective:

1. Check if verification command is actually running
2. Verify test suite is not flaky
3. Break into smaller subgoals using supervised orchestration
4. Ask the user to edit, pause, or clear the goal before restarting with tighter constraints
