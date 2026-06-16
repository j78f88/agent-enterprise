#!/usr/bin/env bash
# Bootstrap a fresh git worktree so it can build.
#
# A linked worktree starts with no resolved/ tree and no installed deps.
# Run this once after `git worktree add` (e.g. when an agent gets its own
# worktree) to install runtime deps and produce a working resolved/ tree.
#
# Worktree-safe: resolves the repo root via `git rev-parse --show-toplevel`
# rather than assuming an absolute path, so it behaves correctly from any
# linked worktree (shared hooks/config across worktrees would otherwise
# point at the wrong directory).
#
# Usage:
#   ./scripts/setup-worktree.sh [config]
#
# Default config: config/project.config.example.yml

set -euo pipefail

# init.py prints non-ASCII status glyphs; force UTF-8 so it does not crash
# under a legacy console codepage (e.g. Windows cp1252 in git-bash).
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

CONFIG="${1:-config/project.config.example.yml}"
# Prefer an explicit $PYTHON, else python3, else python (Windows ships `python`).
if [[ -n "${PYTHON:-}" ]]; then
  :
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  PYTHON=python
fi

root="$(git rev-parse --show-toplevel)"
cd "$root"

echo "=== agent-enterprise worktree setup ==="
echo "Worktree: $root"
echo "Python:   $($PYTHON --version)"
echo "Config:   $CONFIG"
echo

echo "--- 1/2 install runtime deps ---"
$PYTHON -m pip install --quiet -r requirements.txt

echo "--- 2/2 build resolved/ artifacts ---"
$PYTHON init.py --config "$CONFIG"

echo
echo "=== worktree ready ==="
