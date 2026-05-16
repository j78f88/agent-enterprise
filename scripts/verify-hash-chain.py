#!/usr/bin/env python3
"""Verify the hash chain in a FILE_HASHES.md-style registry.

Each data row in the registry table has a ``Prior Hash`` column. For the first
data row it must equal ``GENESIS``. For every subsequent row it must equal the
first 8 characters of the lowercase SHA-256 hex digest of the previous row's
``SHA-256`` field.

Usage: ``python scripts/verify-hash-chain.py <path-to-FILE_HASHES.md>``.

Exit codes:
  0 — chain valid (or no data rows present, which is treated as a clean slate)
  1 — chain invalid (tamper detected or malformed table)
  2 — bad CLI usage or file not found
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

GENESIS = "GENESIS"
PRIOR_LEN = 8
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


def parse_rows(text: str) -> tuple[list[str], list[list[str]]]:
    header: list[str] = []
    rows: list[list[str]] = []
    seen_header = False
    skipped_separator = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not seen_header:
            header = cells
            seen_header = True
            continue
        if not skipped_separator:
            if all(set(c) <= set("-: ") for c in cells):
                skipped_separator = True
                continue
            skipped_separator = True
        rows.append(cells)
    return header, rows


def prior_for(sha: str) -> str:
    return hashlib.sha256(sha.lower().encode("ascii")).hexdigest()[:PRIOR_LEN]


def verify(text: str) -> list[str]:
    header, rows = parse_rows(text)
    if not header:
        return ["no table found in registry"]
    try:
        sha_idx = header.index("SHA-256")
        prior_idx = header.index("Prior Hash")
    except ValueError:
        return [f"table is missing required columns: header={header!r}"]

    errors: list[str] = []
    expected_prior = GENESIS
    for i, row in enumerate(rows, start=1):
        if len(row) <= max(sha_idx, prior_idx):
            errors.append(f"row {i}: too few columns ({len(row)})")
            continue
        sha = row[sha_idx]
        prior = row[prior_idx]
        if not HEX64.match(sha):
            errors.append(f"row {i}: SHA-256 field is not 64 hex chars: {sha!r}")
            continue
        if prior != expected_prior:
            errors.append(
                f"row {i}: Prior Hash mismatch — got {prior!r}, expected {expected_prior!r}"
            )
        expected_prior = prior_for(sha)
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.exists():
        print(f"not found: {path}", file=sys.stderr)
        return 2
    errors = verify(path.read_text(encoding="utf-8"))
    if errors:
        for e in errors:
            print(f"INVALID: {e}", file=sys.stderr)
        return 1
    print(f"OK: hash chain valid in {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
