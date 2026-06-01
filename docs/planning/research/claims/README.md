---
title: "Claims home"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-01
---

# `claims/` — sourced claims

**Status:** PROPOSAL — container scaffolding, awaiting owner ratification. Not canonical.

One **claim** per JSON file, validating against
[`schemas/claim.schema.json`](../../../../schemas/claim.schema.json). A claim is a
**falsifiable proposition with a verdict and an evidence link** — never a
recommendation, never a decision.

## Contract

- Named after its `id` (e.g. `CLM-substrate-ruler-overlap.json`).
- Carries a `verdict` — `verified | plausible | overhyped | unverified`:
  - `verified` requires **≥2 independent** evidence sources of sufficient tier.
  - `overhyped` records a claim the evidence does **not** support (anti-hype guardrail).
  - `unverified` = no adequate source found; it is never smuggled in as fact.
- Every `evidence[].source_id` MUST resolve to a [source-note](../sources/README.md)
  that exists and validates. Dangling evidence fails the gate.
- `contested` claims require ≥2 independent sources.
- `falsifier` (what would overturn the verdict) is expected for `verified`/`plausible`.
- May anchor to an AU gov control via `control_anchor` (see
  [`controls/`](../controls/README.md)).

## Evidence vs decision separation (load-bearing)

Claims are **evidence**. The **adopt / build-on / greenfield** verdicts and the ADRs
are **decisions**, made by `@architect`/`@pm` plus **owner ratification** — recorded
outside this home, and required to cite claim `id`s. The engine gathers; the owner
decides. This is the structural guard against the agent overstepping into
recommendations.
