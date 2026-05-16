#!/usr/bin/env bash
# session-start.sh
#
# Resolution freshness check. If any source file under skills/ or
# instructions/ has been modified more recently than the matching artifact
# under resolved/, warn the operator that they probably want to re-run
# init.py before trusting the resolved tree.
#
# Exit codes:
#   0 — resolved/ is up to date (or no resolved/ tree exists yet).
#   2 — at least one source file is newer than resolved/. The shell does not
#       hard-fail (so the session still starts), but the warning is loud.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [[ ! -d "resolved" ]]; then
  echo "[session-start] resolved/ is missing; run: python init.py --config <your.yml>"
  exit 0
fi

# Newest mtime under resolved/ — used as the "last build" timestamp.
resolved_latest=$(find resolved -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -n1 || echo 0)
if [[ -z "$resolved_latest" ]]; then
  resolved_latest=0
fi

stale=()
while IFS= read -r -d '' f; do
  src_mtime=$(stat -c '%Y' "$f" 2>/dev/null || stat -f '%m' "$f" 2>/dev/null || echo 0)
  # awk handles the float compare without depending on bc.
  if awk -v s="$src_mtime" -v r="$resolved_latest" 'BEGIN{exit !(s+0 > r+0)}'; then
    stale+=("$f")
  fi
done < <(find skills instructions -type f \( -name '*.md' -o -name '*.skill.md' \) -print0)

if (( ${#stale[@]} > 0 )); then
  echo "[session-start] WARNING: ${#stale[@]} source file(s) newer than resolved/:"
  for f in "${stale[@]}"; do
    echo "  - $f"
  done
  echo "[session-start] Run: python init.py --config <your.yml> to refresh."
  exit 2
fi

echo "[session-start] resolved/ is up to date."
exit 0
