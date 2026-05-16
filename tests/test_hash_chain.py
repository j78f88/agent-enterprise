"""Tests for scripts/verify-hash-chain.py."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify-hash-chain.py"

spec = importlib.util.spec_from_file_location("verify_hash_chain", SCRIPT)
assert spec and spec.loader
vhc = importlib.util.module_from_spec(spec)
sys.modules["verify_hash_chain"] = vhc
spec.loader.exec_module(vhc)


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def prior(prev_sha: str) -> str:
    return hashlib.sha256(prev_sha.lower().encode("ascii")).hexdigest()[:8]


def registry(rows: list[tuple[str, str, str]]) -> str:
    lines = [
        "| File | SHA-256 | Prior Hash | Last Verified | Changed By |",
        "|------|---------|------------|---------------|------------|",
    ]
    for file_, sha_, prior_ in rows:
        lines.append(f"| {file_} | {sha_} | {prior_} | 2026-05-16 | @security |")
    return "\n".join(lines) + "\n"


def test_empty_starter_template_passes():
    text = (ROOT / "starters" / "FILE_HASHES.md").read_text(encoding="utf-8")
    assert vhc.verify(text) == []


def test_genesis_only_valid():
    h1 = sha("file-1-contents")
    text = registry([("a.txt", h1, "GENESIS")])
    assert vhc.verify(text) == []


def test_valid_chain():
    h1, h2, h3 = sha("a"), sha("b"), sha("c")
    text = registry(
        [
            ("a.txt", h1, "GENESIS"),
            ("b.txt", h2, prior(h1)),
            ("c.txt", h3, prior(h2)),
        ]
    )
    assert vhc.verify(text) == []


def test_tampered_middle_row_detected():
    h1, h2, h3 = sha("a"), sha("b"), sha("c")
    text = registry(
        [
            ("a.txt", h1, "GENESIS"),
            ("b.txt", sha("tampered"), prior(h1)),  # sha changed, prior left alone
            ("c.txt", h3, prior(h2)),  # downstream prior no longer matches
        ]
    )
    errors = vhc.verify(text)
    assert any("row 3" in e for e in errors)


def test_missing_genesis_detected():
    h1 = sha("a")
    text = registry([("a.txt", h1, "DEADBEEF")])
    errors = vhc.verify(text)
    assert any("row 1" in e and "GENESIS" in e for e in errors)


def test_bad_sha_format_detected():
    text = registry([("a.txt", "notarealhash", "GENESIS")])
    errors = vhc.verify(text)
    assert any("not 64 hex chars" in e for e in errors)


def test_main_exit_codes(tmp_path: Path):
    good = tmp_path / "good.md"
    good.write_text(registry([("a.txt", sha("a"), "GENESIS")]), encoding="utf-8")
    assert vhc.main(["verify-hash-chain.py", str(good)]) == 0

    bad = tmp_path / "bad.md"
    bad.write_text(registry([("a.txt", sha("a"), "DEADBEEF")]), encoding="utf-8")
    assert vhc.main(["verify-hash-chain.py", str(bad)]) == 1

    assert vhc.main(["verify-hash-chain.py"]) == 2
    assert vhc.main(["verify-hash-chain.py", str(tmp_path / "nope.md")]) == 2
