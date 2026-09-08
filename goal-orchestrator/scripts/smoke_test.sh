#!/usr/bin/env bash
# Smoke test for goal-orchestrator: skill structure + helper scripts.
# Usage: bash goal-orchestrator/scripts/smoke_test.sh   (from anywhere)
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1

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

step "3. Standard-library parser and benchmark regressions"
if python3 -m unittest discover -s "$KIT/tests" -p 'test_*.py'; then ok; else bad "unittest regressions"; fi

step "4. extract_goal.py parses every goal template fully"
if python3 "$KIT/scripts/extract_goal.py" "$KIT/examples/goal-templates" | python3 -c '
import json, sys
goals = json.load(sys.stdin)
assert goals, "no goals found in goal-templates/"
missing = [g["source_file"] for g in goals if not (g["done_when"] and g["verification"])]
oversized = [g["source_file"] for g in goals if g["character_count"] > 4000]
assert not missing, f"goals missing completion criteria or verification: {missing}"
assert not oversized, f"goals over 4,000 characters: {oversized}"
print(f"   {len(goals)} goals, all with completion criteria and verification, and within 4,000 characters")
'; then ok; else bad "extract_goal.py on goal-templates/"; fi

step "5. Goal lifecycle commands and prose are not treated as goals"
printf 'Run `/goal clear` and retry.\n/goal edit new objective\n/goal pause\n/goal resume\n/goal clear\n/goal --resume\nsee skills/goal-orchestrator\n/goal-templates/ is a dir\n' > "$TMP/prose.md"
OUT="$(python3 "$KIT/scripts/extract_goal.py" "$TMP/prose.md" 2>&1)"
if echo "$OUT" | grep -q "No goals found"; then ok; else bad "junk goals extracted from prose"; fi

step "6. A typo'd filename is an error, not silent goal text"
OUT="$(python3 "$KIT/scripts/extract_goal.py" no-such-file.md 2>&1)"
if echo "$OUT" | grep -q "input not found"; then ok; else bad "missing file not reported"; fi

step "7. benchmark_goals.py passes the kit's own templates"
if python3 "$KIT/scripts/benchmark_goals.py" "$KIT/examples/goal-templates" > "$TMP/bench.json"; then
    if python3 -c '
import json, sys
r = json.load(sys.stdin)
assert r["summary"]["goals_with_issues"] == 0, r["summary"]
cmds = {c for a in r["analyses"] for c in a["verification_commands"]}
# refactor.md and test-suite.md carry multi-check clauses; every command must survive.
for expected in ("npm test", "pytest -q", "ruff check .", "npm run coverage"):
    assert expected in cmds, (expected, sorted(cmds))
print("  ", r["summary"]["total_goals"], "goals, 0 issues, multi-check commands extracted")
' < "$TMP/bench.json"; then ok; else bad "benchmark summary wrong"; fi
else bad "benchmark exited nonzero on own templates"; fi

step "8. --test-commands --yes runs real commands and fails the run on a missing one (exit 127)"
python3 "$KIT/scripts/benchmark_goals.py" \
    "/goal A. Done only when echo hello exits 0, proven by running echo hello." \
    "/goal B. Done only when definitely-not-a-cmd-xyz exits 0, proven by running it." \
    --test-commands --yes -o "$TMP/tests.json" >/dev/null 2>&1
STATUS=$?
if [ "$STATUS" -ne 0 ] && python3 -c '
import json, sys
r = json.load(open(sys.argv[1]))
tests = {t["command"]: t for a in r["analyses"] for t in a.get("command_tests", [])}
assert tests["echo hello"]["can_run"] and tests["echo hello"]["exit_code"] == 0
assert not tests["definitely-not-a-cmd-xyz"]["can_run"]
assert tests["definitely-not-a-cmd-xyz"]["exit_code"] == 127
issues = [i for a in r["analyses"] for i in a["issues"]]
assert any("could not run" in i for i in issues), issues
print("   echo ran and passed; the missing command failed the run (exit", sys.argv[2] + ")")
' "$TMP/tests.json" "$STATUS"; then ok; else bad "--test-commands --yes behavior (exit $STATUS)"; fi

step "8b. --test-commands without --yes lists commands and runs nothing"
python3 "$KIT/scripts/benchmark_goals.py" \
    "/goal A. Done only when touch $TMP/ran-without-yes exits 0, proven by running it." \
    --test-commands -o "$TMP/skipped.json" >/dev/null 2>"$TMP/skipped.err"
STATUS=$?
if [ "$STATUS" -eq 0 ] && [ ! -e "$TMP/ran-without-yes" ] && python3 -c '
import json, sys
r = json.load(open(sys.argv[1]))
assert r["execution"] == "skipped: pass --yes to run", r.get("execution")
assert all(a["command_tests"] == [] for a in r["analyses"])
listing = open(sys.argv[2]).read()
assert "command_line: touch" in listing, listing
print("   exit 0, nothing ran, execution reported as skipped")
' "$TMP/skipped.json" "$TMP/skipped.err"; then ok; else bad "--test-commands without --yes (exit $STATUS)"; fi

step "9. generate_brief.py emits the Codex brief without clobbering README values"
mkdir -p "$TMP/proj"
printf '# MyProject\n\nA great CLI tool.\n\nTech Stack: React, Express\n\n## Features\n\n- Fast\n- Reliable\n' > "$TMP/proj/README.md"
printf '{"dependencies": {"lodash": "^4.0.0"}}\n' > "$TMP/proj/package.json"
printf '[tool.ruff]\nline-length = 100\n' > "$TMP/proj/pyproject.toml"
if python3 "$KIT/scripts/generate_brief.py" "$TMP/proj" | python3 -c '
import sys
brief = sys.stdin.read()
for needle in ("**Name:** MyProject", "**Description:** A great CLI tool.",
               "React, Express", "Fast, Reliable", "## Goal", "## Context",
               "## Output", "## Boundaries", "## Verification"):
    assert needle in brief, f"missing: {needle}"
print("   name/description/tech stack/features all survive merging")
'; then ok; else bad "generate_brief merge"; fi

step "10. Directory scans skip node_modules and hidden dirs"
mkdir -p "$TMP/scan/node_modules" "$TMP/scan/.hidden"
printf '/goal Vendor. Done only when x exits 0.\n' > "$TMP/scan/node_modules/v.md"
printf '/goal Hidden. Done only when x exits 0.\n' > "$TMP/scan/.hidden/h.md"
printf '/goal Real goal. Done only when echo ok exits 0, proven by running it.\n' > "$TMP/scan/real.md"
if python3 "$KIT/scripts/extract_goal.py" "$TMP/scan" | python3 -c '
import json, sys
goals = json.load(sys.stdin)
assert len(goals) == 1 and goals[0]["objective"] == "Real goal.", goals
print("   only real.md scanned")
'; then ok; else bad "pruning"; fi

step "11. benchmark_goals.py reports a goal-free file distinctly (exit 2)"
printf '# Notes\n\nNo goal here.\n' > "$TMP/no-goal.md"
OUT="$(python3 "$KIT/scripts/benchmark_goals.py" "$TMP/no-goal.md" 2>&1 >/dev/null)"
STATUS=$?
if [ "$STATUS" -eq 2 ] && echo "$OUT" | grep -q "No goals found."; then ok; else bad "expected exit 2 with 'No goals found.', got exit $STATUS: $OUT"; fi

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
