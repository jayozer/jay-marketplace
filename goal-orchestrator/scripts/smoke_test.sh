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

step "2b. Standalone copy includes every linked runtime and artifact reference"
cp -R "$KIT/skills/goal-orchestrator" "$TMP/goal-orchestrator"
if [ ${#VALIDATOR[@]} -eq 0 ]; then
    bad "PyYAML is required to validate the standalone copy"
elif "${VALIDATOR[@]}" "$KIT/scripts/validate_skills.py" --check-content --skill-dir "$TMP/goal-orchestrator"; then ok; else bad "standalone copy references"; fi

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

step "5b. Kimi lifecycle syntax is filtered with --runtime kimi"
printf '/goal status\n/goal replace new objective\n/goal next queued objective\n/goal next manage\n' > "$TMP/kimi-prose.md"
OUT="$(python3 "$KIT/scripts/extract_goal.py" "$TMP/kimi-prose.md" --runtime kimi 2>&1)"
if echo "$OUT" | grep -q "No goals found"; then ok; else bad "Kimi controls extracted as new objectives"; fi

step "6. A typo'd filename is an error, not silent goal text"
OUT="$(python3 "$KIT/scripts/extract_goal.py" no-such-file.md 2>&1)"
if echo "$OUT" | grep -q "input not found"; then ok; else bad "missing file not reported"; fi

step "7. Template structure passes without claiming readiness or completion"
if python3 "$KIT/scripts/benchmark_goals.py" "$KIT/examples/goal-templates" > "$TMP/bench.json"; then
    if python3 -c '
import json, sys
r = json.load(sys.stdin)
assert r["summary"]["goals_with_issues"] == 0, r["summary"]
assert r["summary"]["status"] == "STRUCTURE_ONLY", r["summary"]
cmds = {c for a in r["analyses"] for c in a["verification_commands"]}
# refactor.md and test-suite.md carry multi-check clauses; every command must survive.
for expected in ("npm test", "pytest -q", "ruff check .", "npm run coverage"):
    assert expected in cmds, (expected, sorted(cmds))
print("  ", r["summary"]["total_goals"], "goals, 0 structural issues, legacy migration suggestions preserved")
' < "$TMP/bench.json"; then ok; else bad "benchmark summary wrong"; fi
else bad "benchmark exited nonzero on own templates"; fi

step "8. Explicit command records run and required command failures fail verification"
python3 - "$TMP" <<'PYFIXTURE'
from pathlib import Path
import json, sys
root = Path(sys.argv[1])
def goal(command):
    record = json.dumps({"command": command, "cwd": ".", "expected_exit": 0})
    return "/goal Check the fixture.\nDone when:\n- The command succeeds.\nVerification:\n- Command: " + record + "\n"
(root / "checks.md").write_text(goal("echo hello") + goal("definitely-not-a-cmd-xyz"))
(root / "preview.md").write_text(goal("touch ran-without-yes"))
PYFIXTURE
python3 "$KIT/scripts/benchmark_goals.py" "$TMP/checks.md" \
    --test-commands --yes -o "$TMP/tests.json" >/dev/null 2>&1
STATUS=$?
if [ "$STATUS" -eq 1 ] && python3 - "$TMP/tests.json" <<'PYRESULT'
import json, sys
r = json.load(open(sys.argv[1]))
tests = {t["command"]: t for a in r["analyses"] for t in a["command_tests"]}
assert tests["echo hello"]["status"] == "PASS"
assert tests["definitely-not-a-cmd-xyz"]["status"] == "FAIL"
assert tests["definitely-not-a-cmd-xyz"]["exit_code"] == 127
assert r["summary"]["status"] == "FAIL"
print("   successful check recorded; missing command failed verification")
PYRESULT
then ok; else bad "explicit execution failure verdict (exit $STATUS)"; fi

step "8b. Preview reports pending checks and executes nothing"
python3 "$KIT/scripts/benchmark_goals.py" "$TMP/preview.md" \
    --test-commands -o "$TMP/skipped.json" >/dev/null 2>"$TMP/skipped.err"
STATUS=$?
if [ "$STATUS" -eq 3 ] && [ ! -e "$TMP/ran-without-yes" ] && python3 - "$TMP/skipped.json" <<'PYPREVIEW'
import json, sys
r = json.load(open(sys.argv[1]))
assert r["execution"] == "skipped: pass --yes to run"
assert r["summary"]["status"] == "PENDING"
assert all(a["command_tests"] == [] for a in r["analyses"])
assert r["execution_plan"][0]["command"] == "touch ran-without-yes"
print("   exit 3, explicit plan shown, nothing executed")
PYPREVIEW
then ok; else bad "preview (exit $STATUS)"; fi

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
