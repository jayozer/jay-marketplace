# API Development Brief Template

## Template

```
Goal: Deliver [API ENDPOINT/SERVICE].
Context: [BACKEND FRAMEWORK/PROJECT], [CURRENT API], [DATABASE/ORM].
Output: [CONTROLLER CODE/MIGRATIONS/API DOCS] covering [ENDPOINTS], [SCHEMAS], [AUTHORIZATION], and [ERROR HANDLING].
Boundaries: Preserve [COMPATIBILITY/PROTECTED FILES]; require approval for [DEPLOYMENT/PUBLICATION].
Verification: [FOCUSED TESTS], [FULL SUITE], [OPENAPI/LINT CHECK], and direct response-shape review.
```

## Example: User Authentication API

```
Goal: Deliver a user authentication API in the existing Express.js application.
Context: Node.js, PostgreSQL with Prisma, Joi validation, and the current user model.
Output: Login, signup, password-reset, and token-refresh handlers with authorization, rate limiting, error responses, and OpenAPI 3.0 documentation.
Boundaries: Preserve existing authentication contracts and migration history; do not deploy or publish.
Verification: Run focused and full API tests, lint the OpenAPI document, and review every documented response against the routes.
```

## Field Explanations

- **OUTCOME:** The API endpoints or service being built
- **CONTEXT:** Backend framework (Express, FastAPI, Django, etc.) and project context
- **CORE DELIVERABLES:** Route handlers, middleware, validation, database operations
- **BEHAVIOR:** HTTP methods, status codes, error responses, rate limiting
- **QUALITY BAR:** API design standards, security best practices, performance targets
- **ENVIRONMENT:** Database, caching layer, authentication provider, deployment environment
- **ARTIFACT:** Controller code, middleware, migrations, API documentation

## Common API Development Constraints

- Follow RESTful design principles
- Use appropriate HTTP methods and status codes
- Implement proper authentication/authorization
- Validate all input data
- Handle errors consistently
- Rate limit sensitive endpoints
- Log important events
- Document with OpenAPI/Swagger
- Version the API if breaking changes are needed
