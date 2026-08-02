# Documentation Goal Template

## When to Use This Template

Use this template when creating or updating documentation for code, APIs, or features.

## Brief Template

```
Build or deliver [DOCUMENTATION TYPE] for [SUBJECT].
It should include [CONTENT SECTIONS], with [EXAMPLES] and [DIAGRAMS/SCREENSHOTS].
Make it meet [CLARITY/COMPLETENESS BAR], using [DOCUMENTATION FORMAT], [STYLE GUIDE], and [AUDIENCE CONSIDERATIONS].
Output as [ARTIFACT OR FORMAT].
```

## Example Brief

```
Build or deliver API documentation for user authentication endpoints.
It should include endpoint descriptions, request/response schemas, authentication requirements, error codes, and usage examples.
Make it meet OpenAPI 3.0 standards with clear explanations for developers, using Markdown with code examples and curl commands.
Output as API documentation files with OpenAPI specification.
```

## Goal Condition Template

```
/goal Create [DOCUMENTATION TYPE] for [SUBJECT] with all required sections.

Done when:
- Every required topic and example is present and accurate.
- The documentation matches the current implementation.

Constraints:
- Follow the existing documentation style and formatting.

Verification:
- `[LINTING/VALIDATION COMMAND]` exits 0.
- The review checklist is complete.
```

## Example Goal Condition

```
/goal Create API documentation for authentication endpoints with OpenAPI 3.0 specification.

Done when:
- Every authentication endpoint has schemas, errors, and a curl example.
- The specification matches the implemented routes.

Constraints:
- Follow the existing API documentation style and OpenAPI 3.0 formatting.

Verification:
- `spectral lint openapi.yaml` exits 0.
- The endpoint review checklist is complete.
```

## Verification Methods

- **Linting:** `spectral lint`, `markdownlint`, `vale`
- **Link checking:** `markdown-link-check`
- **Spelling:** `cspell`, `aspell`
- **Manual review:** Checklist completion
- **Build verification:** Documentation builds successfully

## Documentation Types

- **API documentation:** Endpoints, schemas, examples
- **User guides:** How-to guides, tutorials
- **Developer docs:** Architecture, contribution guidelines
- **README:** Project overview, quick start
- **Changelog:** Version history, changes
- **Code comments:** Inline documentation

## Common Constraints

- Follow existing documentation style guide
- Include working code examples
- Use proper formatting (Markdown, reStructuredText)
- Keep language clear and concise
- Target the right audience level
- Include diagrams for complex concepts
- Update table of contents/indices

## Pre-Flight Checklist

- [ ] Documentation type is clearly defined
- [ ] Target audience is identified
- [ ] Style guide exists or is defined
- [ ] Examples can be tested/verified
- [ ] Diagrams/screenshots can be created
- [ ] Goal body is within 4,000 characters
- [ ] Publication authority is explicit

## Subgoal Splitting Pattern

For large documentation projects, consider splitting into:

1. **Outline/structure** - Create table of contents
2. **Core content** - Write main sections
3. **Examples** - Create code examples and tutorials
4. **Diagrams** - Create visual aids
5. **Review** - Proofread and validate
6. **Formatting** - Apply style guide consistently

## Documentation Quality Checklist

- [ ] All sections from outline are present
- [ ] Code examples are tested and work
- [ ] Links are valid and not broken
- [ ] Spelling and grammar are correct
- [ ] Formatting is consistent
- [ ] Diagrams are clear and labeled
- [ ] Audience level is appropriate
- [ ] Technical accuracy is verified

## Recovery from Stuck Goals

If the goal loops without progress:

1. Verify the scope is realistic for time budget
2. Check if examples can be tested/verified
3. Break into supervised orchestration by section
4. Ask the user to edit, pause, or clear the goal before restarting with smaller scope
