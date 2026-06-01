---
title: "Source-notes home"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-01
---

# `sources/` — source-notes

**Status:** PROPOSAL — container scaffolding, awaiting owner ratification. Not canonical.

One **source-note** per cited source. A source-note is the atom of trust in this
knowledge base: a [claim](../claims/README.md) may only cite a source-note that
**exists here and validates** against
[`schemas/source-note.schema.json`](../../../../schemas/source-note.schema.json).

## Contract

- One JSON file per source, named after its `id` (e.g. `SRC-acsc-ism-2025.json`).
- Every source-note carries: `url` **or** codebase `locator`, `retrieval_date`,
  `source_tier`, `publisher`, `classification`, `trust`, and a `content_hash`
  (SHA-256 — the provenance checksum).
- Records here are the **canonical** tier: `trust` MUST be `trusted`. Untrusted,
  unreviewed material stays in [`_staging/`](../_staging/README.md) or
  [`_imported/`](../_imported/README.md) until promoted.
- Source tiers and the YouTube-corpus down-rank are defined in
  [`_meta/trust-policy.md`](../_meta/trust-policy.md).

## What does NOT live here

- Conclusions, recommendations, or verdicts — those are [claims](../claims/README.md)
  (evidence) or decisions (made by `@architect`/`@pm` + owner ratification), never
  source-notes.
- Raw, unconformed engine output — that lands in `_staging/` first.

The fail-closed validator (`scripts/check_research.py`) rejects any source-note that
fails the schema or omits provenance.
