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

## Corpus ingestor

[`tools/distill_synthesis.py`](../../../../tools/distill_synthesis.py) is the deterministic
distiller for the youtube-sync synthesis corpus.

> ⚠️ **Provenance caveat:** the ingestor reads a **hard-coded external path** —
> `D:\Cowork projects\youtube-sync\docs\synthesis-report.html` — outside this repo. That
> source is **not version-pinned here** and is not reproducible by another consumer of
> this template. Before the corpus may back any canonical claim, its source must be
> captured with a `content_hash` and a recorded retrieval date in an `_imported/`
> manifest. Treat the existing digest as **untrusted** until then.
