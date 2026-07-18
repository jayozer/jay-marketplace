# Goal Orchestrator Guide

A deep dive into writing effective goal conditions, subgoal orchestration, and advanced patterns.

## Table of Contents

1. [Goal Condition Writing](#goal-condition-writing)
2. [Subgoal Orchestration Patterns](#subgoal-orchestration-patterns)
3. [When to Use /goal vs Supervised Orchestration](#when-to-use-goal-vs-supervised-orchestration)
4. [Platform-Specific Considerations](#platform-specific-considerations)
5. [Token Budget Estimation](#token-budget-estimation)
6. [Multi-Session Goal Patterns](#multi-session-goal-patterns)

## Goal Condition Writing

### The Four-Part Structure

A strong goal condition has exactly four parts:

1. **Measurable end state** - The observable result
2. **Verification method** - How the agent proves it
3. **Constraints** - What must stay true
4. **Hard cap** - Turn or time limit

### Writing Effective Objectives

**Good objectives:**
- "Implement user authentication with login, signup, and password reset"
- "Fix memory leak in image processing module"
- "Add test suite for payment service with 80% coverage"

**Bad objectives:**
- "Make the codebase better"
- "Improve performance"
- "Clean up the code"

**Why:** Good objectives are specific and bounded. Bad objectives are open-ended and subjective.

### Choosing Verification Methods

The verification method forces evidence into the transcript. Choose methods that:

- **Exit with clear status codes** - `pytest -q`, `npm test`, `go test ./...`
- **Produce observable output** - File counts, grep results, build logs
- **Are fast to run** - Avoid commands that take minutes
- **Are deterministic** - Same result every time

**Verification patterns:**

```text
# Test suite
Done only when pytest -q exits 0 with all tests passing, proven by running pytest -q and showing its output in this conversation.

# File existence
Done only when the file src/auth/service.py exists and contains the authenticate function, proven by running grep -n "def authenticate" src/auth/service.py and showing its output in this conversation.

# Build success
Done only when npm run build exits 0 with no errors, proven by running the command and showing its output in this conversation.

# Count check
Done only when grep -r "TODO" src/ returns 0 results, proven by running the command and showing its output in this conversation.
```

### Writing Effective Constraints

Constraints fence dangerous actions and keep the goal focused:

**Good constraints:**
- "Do not modify database schema files in migrations/"
- "Do not add new npm packages without justification"
- "Make minimal changes to existing code"
- "Do not touch production configuration files"

**Bad constraints:**
- "Don't break anything" (too vague)
- "Be careful" (not actionable)
- "Write good code" (subjective)

**Why:** Good constraints are specific and actionable. Bad constraints are subjective or impossible to verify.

### Setting Turn Limits

Turn limits prevent token drain on stuck goals:

- **Simple fixes:** 15-20 turns
- **Feature builds:** 25-35 turns
- **Complex refactoring:** 30-40 turns
- **Research-heavy tasks:** 20-30 turns

**Formula:** Estimate turns = (complexity × 10) + 10

### Common Mistakes

**Mistake 1: Vague verification**
```text
❌ Done only when the feature works.
✅ Done only when npm test exits 0 with all feature tests passing.
```

**Mistake 2: Missing turn cap**
```text
❌ Done only when all tests pass.
✅ Done only when all tests pass. Stop after 30 turns if not met.
```

**Mistake 3: Over-constraining**
```text
❌ Constraints: Do not modify any files; do not add any code; use only existing functions.
✅ Constraints: Do not modify database schema; follow existing patterns.
```

**Mistake 4: No evidence forcing**
```text
❌ Done only when tests pass.
✅ Done only when tests pass, proven by running npm test and showing its output in this conversation.
```

## Subgoal Orchestration Patterns

### When to Split into Subgoals

Split into subgoals when:

- **Work is naturally independent** - Different features, layers, or components
- **Parallelization helps** - Speed, quality, or coverage benefits
- **Complexity is high** - Single goal would be too large or unclear
- **Specialization matters** - Different subgoals need different agent types

**Don't split when:**
- Work is tightly coupled
- Subgoals are too small (overhead > benefit)
- Dependencies are complex
- Single goal is clearer

### Subgoal Prompt Structure

Each subagent needs a self-contained prompt:

```text
[ONE CLEAR SUBGOAL]

Context: [Filled brief + relevant repo, files, constraints, current plan.]
Deliverable: [Specific output: findings, patch, design, tests, risks, recommendation.]
Boundaries: [What this agent owns; what it must not touch or decide.]
Verification: [Checks to run or evidence to collect.]
Return: summary · evidence/file refs · artifact/recommendation · verification done · unknowns/risks.
```

### Parallel Execution

In Claude Code, emit all Task calls in one message:

```text
[Task: Explore agent for research]
[Task: Plan agent for design]
[Task: general-purpose agent for implementation]
```

This runs them concurrently. In Codex, use multiple `spawn_agent` calls.

### Synthesis Pattern

After subgoals complete, synthesize results:

1. **Compare against repo** - Workspace evidence beats agent opinion
2. **Verify claims** - Don't trust agent assertions without evidence
3. **Reconcile conflicts** - Prioritize concrete evidence over opinions
4. **Apply selectively** - Only use what fits the brief
5. **Run verification** - Smallest reliable check that proves outcome

### Common Subgoal Patterns

See `examples/subgoal-patterns/` for detailed patterns:

- **Layered Architecture** - Split by architectural layers (data, logic, API, UI)
- **Feature-by-Feature** - Split by independent features
- **Test-Driven** - Tests first, then implementation
- **Research-Then-Build** - Research phase, then build phase

## When to Use /goal vs Supervised Orchestration

### Use /goal When

✅ **Verifiable finish line exists**
- Test suite can prove completion
- File counts or existence checks work
- Exit codes clearly indicate success/failure

✅ **Safe to run unsupervised**
- No destructive actions
- No production deployments
- No credential operations
- Mistakes are recoverable (git, sandbox)

✅ **Bounded scope**
- Realistic end within turn budget
- Not an open research rabbit hole
- Clear acceptance criteria

### Use Supervised Orchestration When

❌ **No verifiable finish line**
- "Make it better"
- "Improve UX"
- "Clean up code"

❌ **Unsafe unsupervised**
- Production deployments
- Database migrations
- Credential operations
- Irreversible changes

❌ **Open-ended**
- Research tasks
- Creative work
- Exploration without clear destination

### Decision Flowchart

```
Task Request
    │
    ├─→ Is there a verifiable finish line?
    │       ├─ No → Supervised Orchestration
    │       └─ Yes → Continue
    │
    ├─→ Is it safe to run unsupervised?
    │       ├─ No → Supervised Orchestration
    │       └─ Yes → Continue
    │
    ├─→ Is the scope bounded?
    │       ├─ No → Supervised Orchestration
    │       └─ Yes → Use /goal
    │
    └─→ Otherwise → Supervised Orchestration
```

## Platform-Specific Considerations

### Claude Code

**Tool mapping:**
- `Task` / Agent tool → Dispatch subagents
- `TodoWrite` → Task tracking
- `Skill` tool → Invoke skills
- Native tools for file/shell operations

**Goal command:** `/goal` is native (v2.1.139+)

**Checker model:** Haiku by default

### Codex

**Tool mapping:**
- `spawn_agent` / `wait_agent` → Dispatch subagents (needs `multi_agent = true`)
- `update_plan` → Task tracking
- Skills load natively
- Native tools for file/shell operations

**Goal command:** Not native, use supervised orchestration

**Configuration:** Enable multi-agent in `~/.codex/config.toml`

### Platform Adaptation Checklist

- [ ] Translate tool names for target platform
- [ ] Adjust goal command usage (Claude Code only)
- [ ] Configure multi-agent if using subgoals (Codex)
- [ ] Test verification commands on target platform
- [ ] Adjust file paths for platform conventions

## Token Budget Estimation

### Goal Condition Cost

The checker re-reads the goal condition every turn. Keep it under 4000 characters (~1000 tokens).

**Cost formula:** `turns × (goal_tokens + transcript_tokens)`

**Example:** 30 turns × (1000 + 2000) = 90,000 tokens

### Optimization Strategies

1. **Keep goal tight** - Move details to brief, not goal
2. **Use turn caps** - Prevent runaway token usage
3. **Prefer short verification** - Fast commands = fewer turns
4. **Avoid verbose constraints** - Be specific, not wordy

### Budget Planning

**Conservative budget:** 100,000 tokens per goal
**Aggressive budget:** 200,000 tokens per goal
**Large tasks:** Split into subgoals to reduce per-goal cost

## Multi-Session Goal Patterns

### Resuming Goals

Claude Code supports goal resumption:

```text
/goal --resume
```

This restores the goal in a new session (the turn counter and token baseline reset). To cancel a goal instead, use `/goal clear`.

### Session Handoff Pattern

When a goal spans sessions:

1. **Session 1:** Launch goal, make progress
2. **Session 2:** Resume with `--resume`, continue
3. **Session 3:** Resume again if needed

**Important:** The turn counter and token baseline reset on resume.

### Long-Running Goals

For very long tasks, consider:

1. **Split into sequential goals** - Each phase is a separate goal
2. **Use supervised orchestration** - More control across sessions
3. **Document progress** - Save state to files for handoff

### State Persistence

Save goal state to files for cross-session continuity:

```text
# Save progress
echo "Phase 1 complete: Database layer done" > goal-progress.txt

# Load in new session
cat goal-progress.txt
```

## Advanced Patterns

### Conditional Goals

Use goals that adapt based on conditions:

```text
/goal Implement feature X.
Done only when either npm test exits 0 OR manual verification checklist is complete, proven by running the check and showing the result.
```

### Fallback Verification

Provide multiple verification methods:

```text
/goal Fix the bug.
Done only when either pytest -q exits 0 OR the manual test case passes, proven by running the appropriate check and showing the result.
```

### Progressive Goals

Chain goals for complex work:

```text
# Goal 1: Database layer
/goal Implement database schema and migrations.

# Goal 2: Service layer (after Goal 1)
/goal Implement service layer using the database from Goal 1.

# Goal 3: API layer (after Goal 2)
/goal Implement API endpoints using the service from Goal 2.
```

## Troubleshooting Deep Dive

### Goal Loops Without Progress

**Symptoms:** Agent reports progress but checker never advances

**Causes:**
- Verification command not actually running
- Test suite is flaky
- Evidence not being forced into transcript
- Goal condition too vague

**Solutions:**
1. Manually run verification command
2. Add explicit evidence forcing ("proven by running X and showing output")
3. Tighten goal condition
4. Break into supervised orchestration

### Goal Fails Prematurely

**Symptoms:** Goal marked "not-met" when work is actually done

**Causes:**
- Checker misinterprets transcript
- Verification command output unclear
- Goal condition ambiguous
- Evidence buried in long transcript

**Solutions:**
1. Make verification output explicit and clear
2. Simplify goal condition
3. Force evidence to appear at end of turn
4. Use more specific verification

### Goal Runs Too Long

**Symptoms:** Goal hits turn cap without completion

**Causes:**
- Turn cap too low for task complexity
- Verification too slow
- Goal too broad
- Agent getting stuck in loops

**Solutions:**
1. Increase turn cap appropriately
2. Use faster verification methods
3. Split into smaller goals
4. Add constraints to prevent loops

## Best Practices Summary

1. **Be specific** - Vague goals fail
2. **Force evidence** - Checker only sees transcript
3. **Set caps** - Prevent token drain
4. **Test verification** - Ensure commands work
5. **Know when to split** - Subgoals for complex work
6. **Choose right approach** - /goal vs supervised
7. **Optimize for tokens** - Keep goals tight
8. **Plan for sessions** - Resume patterns for long work
