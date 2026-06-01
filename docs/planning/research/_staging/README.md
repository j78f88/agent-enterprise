---
title: "Staging quarantine home"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-01
---

# `_staging/` — quarantine (untrusted, never canonical)

**Status:** PROPOSAL — container scaffolding, awaiting owner ratification. Not canonical.

This is the **fail-closed landing zone**. Anything that has **not** passed the contract
lives here as `untrusted` and **cannot become canonical** until it conforms.

This is the structural guarantee that *"all research follows the contract regardless of
slash command"*: a bare `deep-research` (or any) run that produces raw output lands here
first. It is only promoted into [`sources/`](../sources/README.md) /
[`claims/`](../claims/README.md) once it passes
`scripts/check_research.py` — citations + dates + provenance + classification + an
`INDEX.md` entry.

## Rules (enforced by the validator)

- Every research **content** item here (notes/claims/digests, JSON or Markdown) MUST be
  `trust: untrusted`. (Home-contract docs like this README are exempt.)
- **No canonical document may cite a `_staging/` path as a source.** The only file
  permitted to list staged items is [`INDEX.md`](../INDEX.md), in its quarantine
  register.
- Promotion is a **deliberate, reviewed act**: add provenance (hash, retrieval date,
  source-tier, classification), restructure into the schema, register in INDEX, then
  move the record into `sources/`/`claims/`. The validator must be green afterwards.

## Currently quarantined

- `youtube-synthesis-digest.md` — the distilled 241-note corpus, produced
  out-of-contract before this container existed. Secondary source, **down-ranked** to
  practitioner-signal tier (see [trust-policy](../_meta/trust-policy.md)). Retro-conform
  before any claim may cite it.
