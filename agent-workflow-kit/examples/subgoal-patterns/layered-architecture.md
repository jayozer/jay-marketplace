# Layered Architecture Subgoal Pattern

## When to Use

Use this pattern when building systems with clear architectural layers (UI, API, business logic, data).

## Pattern

Split work by architectural layers, from bottom to top or top to bottom depending on dependencies.

## Example: Building a User Management Feature

### Subgoal 1: Data Layer
```
Implement user database schema, migrations, and repository pattern.
Context: Building user management feature in Express.js/PostgreSQL app.
Deliverable: Prisma schema, migration files, repository classes with CRUD operations.
Boundaries: Do not touch API routes or business logic yet. Focus only on data access.
Verification: Run migrations and test repository operations with test database.
Return: summary · migration files · repository code · test results · unknowns.
```

### Subgoal 2: Business Logic Layer
```
Implement user service layer with validation and business rules.
Context: Data layer is complete from Subgoal 1. Need business logic for user operations.
Deliverable: Service classes with validation, password hashing, email verification logic.
Boundaries: Use repository from Subgoal 1. Do not create API routes yet.
Verification: Unit tests for service layer with mocked repositories.
Return: summary · service code · test results · edge cases identified.
```

### Subgoal 3: API Layer
```
Implement REST API endpoints for user operations.
Context: Data and business logic layers are complete from Subgoals 1-2.
Deliverable: Express route handlers, middleware, request/response validation.
Boundaries: Use service layer from Subgoal 2. Do not modify data layer.
Verification: Integration tests hitting API endpoints with test database.
Return: summary · route handlers · API tests · OpenAPI documentation.
```

### Subgoal 4: Integration & Testing
```
Integrate all layers and run end-to-end tests.
Context: All three layers are complete from Subgoals 1-3.
Deliverable: E2E test suite, API documentation, deployment configuration.
Boundaries: Do not add new features. Focus on integration and testing.
Verification: Run full test suite and manual API testing.
Return: summary · integration test results · documentation · deployment readiness.
```

## Synthesis

After all subgoals complete:
1. Verify each layer works independently
2. Test end-to-end workflows
3. Review API contracts match requirements
4. Check performance across layers
5. Document the architecture decisions

## Benefits

- Clear separation of concerns
- Each layer can be tested independently
- Parallel development possible once interfaces are defined
- Easy to swap implementations within a layer

## Considerations

- Define clear interfaces between layers first
- Mock dependencies when testing individual layers
- Watch for layering violations (business logic in API layer)
