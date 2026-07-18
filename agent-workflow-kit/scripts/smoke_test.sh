#!/usr/bin/env bash
# Smoke test for agent-workflow-kit: skill structure + helper scripts.
# Usage: bash agent-workflow-kit/scripts/smoke_test.sh   (from anywhere)
set -uo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
PASS=0; FAIL=0

step() { printf '\n== %s\n' "$1"; }
ok()   { echo "   PASS"; PASS=$((PASS + 1)); }
bad()  { echo "   FAIL: $1"; FAIL=$((FAIL + 1)); }

# validate_skills.py needs PyYAML; use uv as a fallback when it isn't installed.
if python3 -c 'import yaml' 2>/dev/null; then
    VALIDATOR=(python3)
elif command -v uv >/dev/null 2>&1; then
    VALIDATOR=(uv run --quiet --with pyyaml python)
else
    VALIDATOR=()
fi

step "1. Skill frontmatter validation"
if [ ${#VALIDATOR[@]} -eq 0 ]; then
    echo "   SKIP: PyYAML not installed (pip install -r requirements-dev.txt)"
elif "${VALIDATOR[@]}" "$KIT/scripts/validate_skills.py"; then ok; else bad "validate_skills.py"; fi

step "2. Skill content-structure validation (required sections, internal links)"
if [ ${#VALIDATOR[@]} -eq 0 ]; then
    echo "   SKIP: PyYAML not installed"
elif "${VALIDATOR[@]}" "$KIT/scripts/validate_skills.py" --check-content; then ok; else bad "--check-content"; fi

step "3. extract_goal.py parses every goal template fully"
if python3 "$KIT/scripts/extract_goal.py" "$KIT/examples/goal-templates" | python3 -c '
import json, sys
goals = json.load(sys.stdin)
assert goals, "no goals found in goal-templates/"
missing = [g["source_file"] for g in goals if not (g["verification"] and g["turn_limit"])]
assert not missing, f"goals missing verification/turn limit: {missing}"
print(f"   {len(goals)} goals, all with verification + turn limit")
'; then ok; else bad "extract_goal.py on goal-templates/"; fi

step "4. Prose mentions of /goal are not treated as goals"
printf 'Run `/goal clear` and retry.\n/goal clear\nsee skills/goal-orchestrator\n/goal-templates/ is a dir\n' > "$TMP/prose.md"
OUT="$(python3 "$KIT/scripts/extract_goal.py" "$TMP/prose.md" 2>&1)"
if echo "$OUT" | grep -q "No goals found"; then ok; else bad "junk goals extracted from prose"; fi

step "5. A typo'd filename is an error, not silent goal text"
OUT="$(python3 "$KIT/scripts/extract_goal.py" no-such-file.md 2>&1)"
if echo "$OUT" | grep -q "input not found"; then ok; else bad "missing file not reported"; fi

step "6. benchmark_goals.py passes the kit's own templates"
if python3 "$KIT/scripts/benchmark_goals.py" "$KIT/examples/goal-templates" > "$TMP/bench.json"; then
    if python3 -c '
import json, sys
r = json.load(sys.stdin)
assert r["summary"]["goals_with_issues"] == 0, r["summary"]
cmds = [a["verification_command"] for a in r["analyses"]]
assert "npm test" in cmds, cmds
print("  ", r["summary"]["total_goals"], "goals, 0 issues, commands extracted")
' < "$TMP/bench.json"; then ok; else bad "benchmark summary wrong"; fi
else bad "benchmark exited nonzero on own templates"; fi

step "7. --test-commands runs real commands and flags missing ones (exit 127)"
if python3 "$KIT/scripts/benchmark_goals.py" \
    "/goal A. Done only when echo hello exits 0, proven by running echo hello. Stop after 5 turns." \
    "/goal B. Done only when definitely-not-a-cmd-xyz exits 0, proven by running it. Stop after 5 turns." \
    --test-commands 2>/dev/null | python3 -c '
import json, sys
r = json.load(sys.stdin)
tests = {a["verification_command"]: a["command_test"] for a in r["analyses"]}
assert tests["echo hello"]["can_run"] and tests["echo hello"]["exit_code"] == 0
assert not tests["definitely-not-a-cmd-xyz"]["can_run"]
assert tests["definitely-not-a-cmd-xyz"]["exit_code"] == 127
print("   echo ran; missing command reported as not runnable")
'; then ok; else bad "--test-commands behavior"; fi

step "8. generate_brief.py: empty package.json fields must not clobber README values"
mkdir -p "$TMP/proj"
printf '# MyProject\n\nA great CLI tool.\n\nTech Stack: React, Express\n\n## Features\n\n- Fast\n- Reliable\n' > "$TMP/proj/README.md"
printf '{"dependencies": {"lodash": "^4.0.0"}}\n' > "$TMP/proj/package.json"
printf '[tool.ruff]\nline-length = 100\n' > "$TMP/proj/pyproject.toml"
if python3 "$KIT/scripts/generate_brief.py" "$TMP/proj" | python3 -c '
import sys
brief = sys.stdin.read()
for needle in ("**Name:** MyProject", "**Description:** A great CLI tool.",
               "React, Express", "Fast, Reliable"):
    assert needle in brief, f"missing: {needle}"
print("   name/description/tech stack/features all survive merging")
'; then ok; else bad "generate_brief merge"; fi

step "9. Directory scans skip node_modules and hidden dirs"
mkdir -p "$TMP/scan/node_modules" "$TMP/scan/.hidden"
printf '/goal Vendor. Done only when x exits 0. Stop after 5 turns.\n' > "$TMP/scan/node_modules/v.md"
printf '/goal Hidden. Done only when x exits 0. Stop after 5 turns.\n' > "$TMP/scan/.hidden/h.md"
printf '/goal Real goal. Done only when echo ok exits 0, proven by running it. Stop after 5 turns.\n' > "$TMP/scan/real.md"
if python3 "$KIT/scripts/extract_goal.py" "$TMP/scan" | python3 -c '
import json, sys
goals = json.load(sys.stdin)
assert len(goals) == 1 and goals[0]["objective"] == "Real goal.", goals
print("   only real.md scanned")
'; then ok; else bad "pruning"; fi

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
