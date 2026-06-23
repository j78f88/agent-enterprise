#!/usr/bin/env python3
"""Normalise raw research bundles in _staging/raw/ into canonical source-notes
and claims, then register them in INDEX.md.

This is the boundary normaliser the researcher contract requires: the
deep-research engine's raw output is NEVER the artefact. It lands in
``_staging/raw/*.bundle.json`` as ``untrusted``; this script promotes it into
``sources/`` + ``claims/`` only after applying the contract:

  * compute a SHA-256 ``content_hash`` over each source-note's excerpt
    (honest provenance: proves what was *recorded*, not executed);
  * normalise non-conformant ``source_tier`` values to the schema enum;
  * flip ``trust`` to ``trusted`` (this conform step IS the reviewed promotion);
  * enforce the verdict rules: ``verified`` / ``contested`` need >=2 INDEPENDENT
    sources, else auto-adjust (verified->plausible, contested->false) and log it;
  * write one JSON file per record named after its id;
  * regenerate the INDEX.md canonical tables between the BEGIN/END markers.

It is a one-off ingestor for research bundles, NOT part of init.py.
After running, ``scripts/check_research.py`` must be green.

Usage:
  python scripts/conform_research.py [research_home]
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VALID_TIERS = {
    "authoritative-standard", "official-guidance", "primary",
    "practitioner-signal", "community",
}
# Map non-conformant raw tier labels (e.g. from the adversarial bundle) -> enum.
TIER_MAP = {
    "vendor-primary": "primary",
    "government-primary": "official-guidance",
    "standards-body": "authoritative-standard",
    "secondary-analysis": "community",
}


def normalise_tier(tier: str) -> str:
    if tier in VALID_TIERS:
        return tier
    return TIER_MAP.get(tier, "community")


def short(text: str, n: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


def conform(home: Path) -> int:
    raw_dir = home / "_staging" / "raw"
    sources_dir = home / "sources"
    claims_dir = home / "claims"
    index = home / "INDEX.md"

    if not raw_dir.is_dir():
        print(f"conform-research: no raw bundles at {raw_dir}", file=sys.stderr)
        return 2

    source_notes: dict[str, dict] = {}
    claims: dict[str, dict] = {}
    log: list[str] = []

    for bundle_path in sorted(raw_dir.glob("*.bundle.json")):
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        for sn in bundle.get("source_notes", []):
            sid = sn["id"]
            if sid in source_notes:
                log.append(f"DUPLICATE source-note id across bundles: {sid} (skipped)")
                continue
            sn = dict(sn)
            sn["source_tier"] = normalise_tier(sn.get("source_tier", "community"))
            sn["trust"] = "trusted"  # reviewed promotion
            excerpt = sn.get("excerpt", "")
            sn["content_hash"] = "sha256:" + hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
            source_notes[sid] = sn
        for cl in bundle.get("claims", []):
            cid = cl["id"]
            if cid in claims:
                log.append(f"DUPLICATE claim id across bundles: {cid} (skipped)")
                continue
            claims[cid] = dict(cl)

    # Enforce evidence + independence contract on claims.
    known_sources = set(source_notes)
    for cid, cl in claims.items():
        cl["trust"] = "trusted"
        evidence = cl.get("evidence") or []
        independent = sum(1 for e in evidence if isinstance(e, dict) and e.get("independent") is True)
        verdict = cl.get("verdict")
        if verdict == "verified" and independent < 2:
            cl["verdict"] = "plausible"
            log.append(f"{cid}: verified->plausible (only {independent} independent source)")
        if cl.get("contested") is True and independent < 2:
            cl["contested"] = False
            log.append(f"{cid}: contested->false (only {independent} independent source)")
        # Dangling-evidence guard (the gate will also catch this).
        for e in evidence:
            sid = e.get("source_id") if isinstance(e, dict) else None
            if sid and sid not in known_sources:
                log.append(f"{cid}: WARNING evidence source_id not found: {sid}")

    # Write records.
    sources_dir.mkdir(parents=True, exist_ok=True)
    claims_dir.mkdir(parents=True, exist_ok=True)
    for sid, sn in sorted(source_notes.items()):
        (sources_dir / f"{sid}.json").write_text(json.dumps(sn, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for cid, cl in sorted(claims.items()):
        (claims_dir / f"{cid}.json").write_text(json.dumps(cl, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Regenerate INDEX tables between markers.
    _write_index(index, source_notes, claims)

    print(f"conform-research: wrote {len(source_notes)} source-notes, {len(claims)} claims to {home}")
    if log:
        print("conform-research: contract adjustments / notes:")
        for line in log:
            print(f"  {line}")
    return 0


def _replace_between(text: str, begin: str, end: str, payload: str) -> str:
    b = text.index(begin) + len(begin)
    e = text.index(end)
    return text[:b] + "\n" + payload + "\n" + text[e:]


def _write_index(index: Path, source_notes: dict, claims: dict) -> None:
    sn_rows = ["| ID | Title | Tier | Publisher | Retrieved | Class. | Hash |",
               "| --- | --- | --- | --- | --- | --- | --- |"]
    for sid, sn in sorted(source_notes.items()):
        sn_rows.append(
            f"| `{sid}` | {short(sn.get('title',''),50)} | {sn['source_tier']} | "
            f"{short(sn.get('publisher',''),28)} | {sn.get('retrieval_date','')} | "
            f"{sn.get('classification','')} | `{sn['content_hash'][:14]}…` |"
        )
    cl_rows = ["| ID | Statement (short) | Verdict | Evidence (SRC) | Control anchor | Class. |",
               "| --- | --- | --- | --- | --- | --- |"]
    for cid, cl in sorted(claims.items()):
        ev = ", ".join(e.get("source_id", "") for e in (cl.get("evidence") or []) if isinstance(e, dict))
        ca = cl.get("control_anchor") or {}
        ca_str = f"{ca.get('framework','')} {ca.get('control_id','')}".strip() or "—"
        cl_rows.append(
            f"| `{cid}` | {short(cl.get('statement',''),60)} | **{cl.get('verdict','')}** | "
            f"{short(ev,40)} | {short(ca_str,30)} | {cl.get('classification','')} |"
        )

    text = index.read_text(encoding="utf-8")
    text = _replace_between(
        text,
        "<!-- BEGIN:source-notes (generated by scripts/conform_research.py — do not edit by hand) -->",
        "<!-- END:source-notes -->",
        "\n".join(sn_rows),
    )
    text = _replace_between(
        text,
        "<!-- BEGIN:claims (generated by scripts/conform_research.py — do not edit by hand) -->",
        "<!-- END:claims -->",
        "\n".join(cl_rows),
    )
    index.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) > 1:
        print("Usage: python scripts/conform_research.py [research_home]", file=sys.stderr)
        return 2
    home = Path(argv[0]) if argv else ROOT / "docs" / "planning" / "research"
    return conform(home)


if __name__ == "__main__":
    sys.exit(main())
