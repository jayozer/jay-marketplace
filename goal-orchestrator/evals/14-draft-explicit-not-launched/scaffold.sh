#!/usr/bin/env bash
# Copies the shared sample-repo fixture into the sandbox cwd so the prompt's
# "this repo" is a real workspace. `claude plugin eval` runs this only with
# --scaffold, as `bash <this file>` from the sandbox cwd.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -R "$here/../fixtures/sample-repo/." "$PWD/"
