# API Development Brief Template

## Template

```
Build or deliver [API ENDPOINT/SERVICE] in [BACKEND FRAMEWORK/PROJECT].
It should include [ENDPOINT DEFINITIONS], with [REQUEST/RESPONSE SCHEMAS], [AUTHENTICATION/AUTHORIZATION], and [ERROR HANDLING].
Make it meet [API DESIGN STANDARDS], using [DATABASE/ORM], [VALIDATION LIBRARY], and [DOCUMENTATION FORMAT].
Output as [CONTROLLER CODE/MIGRATIONS/API DOCS].
```

## Example: User Authentication API

```
Build or deliver user authentication API in Express.js/Node.js application.
It should include login, signup, password reset, and token refresh endpoints, with JWT authentication, bcrypt password hashing, rate limiting, and comprehensive error responses.
Make it meet REST API best practices and OpenAPI 3.0 specification, using PostgreSQL with Prisma ORM, Joi validation, and Swagger documentation.
Output as Express route handlers, Prisma schema migrations, and OpenAPI specification.
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
