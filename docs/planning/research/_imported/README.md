---
title: "Imported corpora home"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-01
---

# `_imported/` — ingested external corpora (untrusted)

**Status:** PROPOSAL — container scaffolding, awaiting owner ratification. Not canonical.

External corpora ingested wholesale (research datasets, synthesis exports, third-party
note collections) land here, **provenance-tagged and `untrusted`**, before any of their
content is distilled into [claims](../claims/README.md). Same posture as
[`_staging/`](../_staging/README.md): nothing here is canonical, and no canonical
document may cite an `_imported/` path as a source.

## Contract

- Each corpus gets a subdirectory with a manifest recording: origin, retrieval date,
  ingestor, source `content_hash`, licence/terms, and classification.
- Content items are `trust: untrusted`. (This README is the home contract and is exempt.)
- Distillation into source-notes/claims is a reviewed promotion, identical to `_staging/`.
