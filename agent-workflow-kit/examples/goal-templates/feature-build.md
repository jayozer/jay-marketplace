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
Done only when [VERIFICATION COMMAND] exits 0 with all tests passing, proven by running the command and showing its output in this conversation.
Constraints: Do not modify [PROTECTED FILES/DIRS]; do not add new dependencies without justification; follow existing code style.
Stop after 30 turns if not met and report what remains.
```

## Example Goal Condition

```
/goal Implement user authentication system with login, signup, password reset, and session management.
Done only when npm test exits 0 with all authentication tests passing, proven by running npm test and showing its output in this conversation.
Constraints: Do not edit existing migration files (add new migrations as needed); do not add new npm packages without justification; follow existing Express.js middleware patterns.
Stop after 30 turns if not met and report what remains.
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

- [ ] Trusted workspace enabled
- [ ] Auto-approve tools enabled
- [ ] Test suite exists and passes baseline
- [ ] Database migrations are reversible
- [ ] Feature has clear acceptance criteria
- [ ] Turn limit set appropriately (20-40 turns)

## Subgoal Splitting Pattern

For complex features, consider splitting into:

1. **Database layer** - Schema, migrations, models
2. **API layer** - Endpoints, validation, error handling
3. **Business logic** - Core feature implementation
4. **Integration** - Connecting layers together
5. **Testing** - Unit tests, integration tests
6. **Documentation** - API docs, usage examples

## Recovery from Stuck Goals

If the goal loops on "acknowledgement" without progress:

1. Check if verification command is actually running
2. Verify test suite is not flaky
3. Break into smaller subgoals using supervised orchestration
4. Run `/goal clear` and restart with tighter constraints
