# Agent Workflow Kit
**Claude Code and Codex-compatible skills for turning big requests into clear goals, parallel subgoals, and verified results.**

> These are agent workflow skills. They are separate from product-specific kits like the YouTube Automation Kit, so you can reuse them across coding, research, design, and build tasks.

---

## What This Is For

Use this kit when a request is too broad to handle as one unstructured prompt.
It helps the agent create a filled brief, define what done means, split work
into independent subgoals where useful, and synthesize the final result with
verification.

It is not tied to YouTube, video, or any single product workflow.

## Before You Start

- **Claude Code or Codex** — the skill is written to work in either environment.
- **Python 3** — only needed for local validation and helper scripts.
- **PyYAML** — only needed if you want to validate the skills locally: run `pip install -r requirements-dev.txt`.

---

## What's In Here

- `skills/goal-orchestrator` — turn a broad task into a filled brief, a top-level goal, parallel subgoals when useful, synthesized results, and verification.
- `examples/` — pre-built templates and patterns for common workflows:
  - `goal-templates/` — Ready-to-use goal templates for feature builds, bug fixes, test suites, documentation, and refactoring
  - `brief-templates/` — Domain-specific brief templates for web development, API development, data pipelines, and ML
  - `subgoal-patterns/` — Common subgoal decomposition patterns (layered architecture, feature-by-feature, test-driven, research-then-build)
- `scripts/` — Helper utilities for goal management:
  - `validate_skills.py` — Validate skill frontmatter and content structure
  - `extract_goal.py` — Extract goal patterns from files or text
  - `benchmark_goals.py` — Test goal conditions for quality and checkability
  - `generate_brief.py` — Auto-generate briefs from project context

## Install

For Claude Code:

1. Find or create your skills folder: `~/.claude/skills/`
2. Copy each folder from `skills/` into it, so you have `~/.claude/skills/goal-orchestrator/`
3. Start or restart Claude Code so it picks up the new skill.

For Codex:

1. Copy each folder from `skills/` into your Codex skills folder.
2. Restart Codex if needed so it refreshes available skills.

## How To Use It

Ask in plain English:

- "Write a goal and use parallel agents for this build."
- "Turn this request into a proper goal with subgoals."
- "Fill the build brief, create a top-level goal, and split the work across agents."
- "Use goal orchestration for this task."

## Common Patterns

### Feature Development

Use the feature-build goal template for new features:

```bash
# Reference the template
cat examples/goal-templates/feature-build.md

# Apply to your task
/goal Implement user authentication system with login, signup, password reset, and session management.
Done only when npm test exits 0 with all authentication tests passing, proven by running npm test and showing its output in this conversation.
Constraints: Do not edit existing migration files (add new migrations as needed); do not add new npm packages without justification; follow existing Express.js middleware patterns.
Stop after 30 turns if not met and report what remains.
```

### Bug Fixes

Use the bug-fix goal template for focused fixes:

```bash
# Reference the template
cat examples/goal-templates/bug-fix.md

# Apply to your task
/goal Fix memory leak in image processing module when processing large files.
Done only when pytest -q tests/test_image_processing.py exits 0 with all tests passing, proven by running the command and showing its output in this conversation.
Constraints: Make minimal changes; do not modify unrelated modules; add regression test for large file processing.
Stop after 20 turns if not met and report what remains.
```

### Parallel Subgoals

Split complex work using subgoal patterns:

```bash
# Use layered architecture pattern
cat examples/subgoal-patterns/layered-architecture.md

# Or feature-by-feature pattern
cat examples/subgoal-patterns/feature-by-feature.md
```

## Troubleshooting

### Goal Stuck in Acknowledgement Loop

If the goal keeps reporting progress without the checker advancing:

1. **Check verification command** - Ensure it actually runs and produces output
2. **Verify test suite** - Make sure tests aren't flaky
3. **Break into subgoals** - Use supervised orchestration instead
4. **Restart with tighter constraints** - Run `/goal clear` and try again

### Goal Not /goal-Shaped

If the task lacks a verifiable finish line:

1. **Use supervised orchestration** - Follow §7 in the skill documentation
2. **Split into smaller goals** - Each subgoal should be verifiable
3. **Add concrete verification** - Define what "done" looks like

### Verification Command Fails

If the verification command doesn't work:

1. **Test the command manually** - Run it outside the goal to see the error
2. **Check dependencies** - Ensure required tools are installed
3. **Use helper scripts** - Run `benchmark_goals.py` to test commands
4. **Adjust the command** - Make it more specific or add error handling

## Helper Scripts

### Validate Skills

Check skill frontmatter and content structure:

```bash
# Basic validation
python3 scripts/validate_skills.py

# Content structure validation
python3 scripts/validate_skills.py --check-content
```

### Extract Goals

Extract goal patterns from files:

```bash
# Extract from a file
python3 scripts/extract_goal.py path/to/file.md

# Extract from directory
python3 scripts/extract_goal.py path/to/directory/

# Extract from text
python3 scripts/extract_goal.py "/goal Implement feature X..."

# Output to file
python3 scripts/extract_goal.py path/to/file.md -o goals.json
```

### Benchmark Goals

Test goal conditions for quality:

```bash
# Analyze goals without running commands
python3 scripts/benchmark_goals.py path/to/file.md

# Actually test verification commands (use with caution)
python3 scripts/benchmark_goals.py path/to/file.md --test-commands

# Specify working directory
python3 scripts/benchmark_goals.py path/to/file.md --test-commands --cwd /path/to/project
```

### Generate Brief

Auto-generate brief from project context:

```bash
# Generate brief for current directory
python3 scripts/generate_brief.py .

# Generate with task description
python3 scripts/generate_brief.py . --task "Implement user authentication"

# Save to file
python3 scripts/generate_brief.py . -o brief.md
```

## Validate The Skills

From this folder:

```bash
pip install -r requirements-dev.txt
python3 scripts/validate_skills.py
python3 scripts/validate_skills.py --check-content
```

## Advanced Usage

See `GUIDE.md` for:
- Deep dive into goal condition writing
- Subgoal orchestration patterns
- When to use `/goal` vs supervised orchestration
- Platform-specific considerations
- Token budget estimation
- Multi-session goal patterns
