# Web Development Brief Template

## Template

```
Goal: Deliver [FEATURE/COMPONENT].
Context: [WEB FRAMEWORK/PROJECT], [CURRENT UI], [API], and [DESIGN SYSTEM].
Output: [CODE/STORIES/DOCUMENTATION] implementing [BEHAVIOR], [RESPONSIVENESS], and [ACCESSIBILITY].
Boundaries: Preserve [ROUTES/API/DESIGN CONTRACTS]; require approval for dependency or deployment changes.
Verification: [COMPONENT TESTS], [BROWSER FLOWS], [ACCESSIBILITY CHECK], [BUILD], and visual review.
```

## Example: User Dashboard

```
Goal: Deliver a responsive user dashboard in the existing React/Next.js application.
Context: The current shadcn/ui system, Redux Toolkit state, API client, and dark-mode behavior.
Output: Profile, activity, settings, and notification components with Storybook stories and API documentation.
Boundaries: Preserve existing routes and API contracts; do not add dependencies or deploy without approval.
Verification: Run component and browser tests, verify WCAG AA behavior, build successfully, and review mobile, tablet, desktop, and dark-mode layouts.
```

## Field Explanations

- **OUTCOME:** The specific feature or component being built
- **CONTEXT:** Web framework (React, Vue, Next.js, etc.) and project context
- **CORE DELIVERABLES:** UI components, API calls, state management, routing
- **BEHAVIOR:** User interactions, responsive behavior, loading states, error handling
- **QUALITY BAR:** Performance metrics, accessibility standards, security requirements
- **ENVIRONMENT:** API endpoints, authentication, deployment target, CDN configuration
- **ARTIFACT:** Component files, stories, documentation, deployment configs

## Common Web Development Constraints

- Follow existing component library patterns
- Use established state management approach
- Maintain responsive design standards
- Ensure accessibility compliance (WCAG)
- Optimize for Core Web Vitals
- Follow security best practices (CORS, CSP, XSS prevention)
- Use existing API client patterns
