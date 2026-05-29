#!/usr/bin/env bash
# Canonical install + verification path for agent-enterprise.
# Runs from a clean checkout. Exits non-zero on any failure.
#
# Usage:
#   ./scripts/smoke-test.sh [config]
#
# Default config: profiles/python-api.config.yml

set -euo pipefail

CONFIG="${1:-profiles/python-api.config.yml}"
PYTHON="${PYTHON:-python3}"

echo "=== agent-enterprise smoke test ==="
echo "Python:  $($PYTHON --version)"
echo "Config:  $CONFIG"
echo

echo "--- 1/4 install runtime deps ---"
$PYTHON -m pip install --quiet -r requirements.txt

echo "--- 2/4 install dev deps ---"
$PYTHON -m pip install --quiet -r requirements-dev.txt

echo "--- 3/4 build (twice, determinism check) ---"
rm -rf resolved
$PYTHON init.py --config "$CONFIG" > /dev/null
HASH_1=$(find resolved -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1)
rm -rf resolved
$PYTHON init.py --config "$CONFIG" > /dev/null
HASH_2=$(find resolved -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1)
if [ "$HASH_1" != "$HASH_2" ]; then
  echo "FAIL: resolved/ output differs across two builds"
  echo "  run 1: $HASH_1"
  echo "  run 2: $HASH_2"
  exit 1
fi
echo "OK: byte-identical resolved/ ($HASH_1)"

echo "--- 4/4 pytest ---"
$PYTHON -m pytest -q

echo
echo "=== smoke test PASS ==="
