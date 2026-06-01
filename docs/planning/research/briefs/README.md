---
title: "Research briefs home"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-01
---

# `briefs/` — scoped research briefs

**Status:** PROPOSAL — container scaffolding, awaiting owner ratification. Not canonical.

A **brief** is the scoped question that drives a research run, with its
**kill-questions baked in** (disconfirmation-first). The `@researcher` skill drives the
`deep-research` engine from a brief and normalises the engine's output into
[source-notes](../sources/README.md) and [claims](../claims/README.md).

## Contract

A brief (Markdown, with frontmatter) states:

- **Question** — the precise claim under test, not a topic.
- **Kill-questions** — what evidence would disconfirm it (so the run can fail fast).
- **Scope** — which consumer profile(s): own-agency / other-gov-orgs / vendor-baseline.
- **Source-tier floor** — minimum tier required for a `verified` verdict.
- **Output targets** — the source-note/claim ids the run is expected to produce.

A brief is **evidence-gathering scaffolding**, not a decision. It never records a
recommendation. The two claims queued by the handoff (substrate commoditisation;
build-time safety layer) plus the compliance anchor map are the first briefs to author
**after** this container is ratified.
