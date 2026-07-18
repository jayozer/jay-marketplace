# Research-Then-Build Subgoal Pattern

## When to Use

Use this pattern when the task requires significant research, exploration, or learning before implementation.

## Pattern

Split work into research/exploration phase and implementation phase, with clear handoff.

## Example: Implementing a New Authentication System

### Subgoal 1: Technology Research
```
Research authentication options and recommend best approach for the project.
Context: Need to implement authentication. Multiple options available (JWT, OAuth, sessions, etc.).
Deliverable: Research report comparing authentication approaches with recommendations.
Boundaries: Do not implement any code. Focus only on research and recommendation.
Verification: Research covers all relevant options, includes pros/cons, provides clear recommendation.
Return: summary · research report · recommendation with justification · implementation considerations.
```

### Subgoal 2: Architecture Design
```
Design authentication architecture based on research recommendation.
Context: Research from Subgoal 1 recommends JWT with refresh tokens. Need to design the architecture.
Deliverable: Architecture diagram, data model, API contracts, security considerations.
Boundaries: Follow research recommendation. Do not implement code yet.
Verification: Architecture is complete, addresses security concerns, aligns with project constraints.
Return: summary · architecture diagrams · data models · API contracts · security checklist.
```

### Subgoal 3: Core Implementation
```
Implement core authentication logic based on architecture design.
Context: Architecture is complete from Subgoal 2. Ready to implement.
Deliverable: Authentication service, token generation/validation, user session management.
Boundaries: Follow architecture design exactly. Do not deviate without justification.
Verification: Unit tests pass, tokens work correctly, sessions manage properly.
Return: summary · implementation code · test results · any deviations from architecture.
```

### Subgoal 4: Integration & Testing
```
Integrate authentication with existing application and run security tests.
Context: Core implementation is complete from Subgoal 3. Need to integrate with app.
Deliverable: API middleware, login/signup UI, security audit, penetration testing.
Boundaries: Do not modify core authentication logic. Focus on integration and security.
Verification: Integration tests pass, security audit finds no critical issues, UI works correctly.
Return: summary · integration code · security audit results · test results · deployment checklist.
```

## Synthesis

After all subgoals complete:
1. Verify implementation matches research recommendation
2. Review architecture decisions against actual implementation
3. Document any lessons learned during implementation
4. Update research findings with real-world insights
5. Create maintenance guide for authentication system

## Benefits

- Informed technology choices
- Architecture is thought through before coding
- Reduces rework from poor initial decisions
- Clear documentation of decision rationale

## Considerations

- Research phase can be time-consuming
- Recommendations may change during implementation
- Need to balance research time with delivery speed
- Ensure research is actionable, not academic
