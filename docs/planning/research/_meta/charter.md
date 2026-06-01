---
title: "Research knowledge base — charter"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-01
---

# Research Knowledge Base — Charter

> **Status: PROPOSAL — awaiting owner ratification. Not canonical.**
> This charter is container scaffolding produced by a build session. It describes the
> *contract* for a sovereign research knowledge base. The **goals and design intent it
> serves are the owner's to ratify** — they are recorded as candidate proposals (see
> [`docs/planning/vision/safety-in-consumption-design-goals.md`](../../vision/safety-in-consumption-design-goals.md),
> itself flagged as authored with an overstep), not as settled fact. Nothing here is
> canonical until the owner promotes it.

## 1. Purpose

A **sovereign, provenance-first, agency-owned** research and decision knowledge base
that lives **inside this repository** — plain Markdown + JSON, git-versioned, with **no
external SaaS dependency**. It applies the project's own *"safety in consumption"* thesis
to **ideas**: every claim is sourced or it does not become canonical.

It is also, by design, a **reusable template**: every portable path is tokenised
(`{{paths.research_*}}`) so other AU gov organisations can re-home the container, and it
doubles as a **minimum-expectation baseline for vendors** in the coding-delivery stream.

## 2. Principles

1. **Provenance-first.** No claim is canonical without a source-note carrying a URL (or
   codebase locator), a retrieval date, a source tier, a classification, and a content
   hash. Unsourced ⇒ `unverified`, never smuggled in.
2. **Evidence is not decision.** The knowledge base surfaces **evidence** (source-notes
   and verdict-tagged claims). The **adopt / build-on / greenfield** verdicts and the
   ADRs are **decisions** made by `@architect`/`@pm` plus **owner ratification**. The
   engine gathers; the owner decides. This is the structural guard against an agent
   overstepping into recommendations.
3. **Fail closed.** Unconformed material lands in [`_staging/`](../_staging/README.md) as
   `untrusted` and cannot become canonical until it passes the gate
   (`scripts/check_research.py`). Process is followed **regardless of which slash command
   produced the research.**
4. **Proposal-tier by default.** Agent/Claude output is proposal-tier. It does not assert
   the owner's goals as fact and is not canonical until ratified.
5. **Compliance is the spine.** Claims are made defensible by tracing to authoritative AU
   gov guidance (the [control register](../controls/README.md)), not by assertion.
6. **Optimise for correctness and defensibility**, not adoption hand-holding.

## 3. Three consumer profiles

A design choice right for one profile can fail another, so scope is always explicit
(`claim.consumer_profile`):

| Profile | Who | What they need from this base |
| --- | --- | --- |
| `own-agency` | The owning AU federal agency | Defensible, traceable evidence for its own decisions. |
| `other-gov-orgs` | Other AU gov organisations | A re-homeable template — tokenised paths, portable contract. |
| `vendor-baseline` | Delivery-stream vendors | A minimum-expectation baseline to meet (e.g. SFIA-anchored). |

## 4. The homes (container map)

All paths are tokenised; defaults nest under `{{paths.research}}` (`docs/planning/research/`).

| Home | Token | Holds |
| --- | --- | --- |
| `sources/` | `{{paths.research_sources}}` | Source-notes (one per cited source). |
| `claims/` | `{{paths.research_claims}}` | Verdict-tagged claims with evidence links. |
| `controls/` | `{{paths.research_controls}}` | AU gov control register / anchors. |
| `briefs/` | `{{paths.research_briefs}}` | Scoped research briefs (question + kill-questions). |
| `_staging/` | `{{paths.research_staging}}` | Quarantine — untrusted, unconformed. |
| `_imported/` | `{{paths.research_imported}}` | Ingested external corpora (provenance-tagged). |
| `INDEX.md` | `{{paths.research_index}}` | Registry of canonical artefacts + quarantine ledger. |
| `_meta/` | — | This charter + the [trust-policy](trust-policy.md). |

## 5. Constitution & engine

- The **`@researcher` skill is the constitution** for ALL research: it owns the artefact
  home, the citation/falsifiability rules, the approval gate, the subagent return tiers,
  and the never-recommend guarantee.
- **`deep-research` is a breadth *engine*** the researcher drives for wide prior-art and
  landscape sweeps. It is not editable here, so its **raw output is never the artefact** —
  it is normalised into this home's schema + provenance + INDEX, then registered. The
  boundary is enforced by the gate.
- **Codebase research is permitted** for self-validation (owner-approved), under the same
  citation/provenance discipline (use a `locator.kind = codebase` source-note).

## 6. Schemas & gate

- [`schemas/source-note.schema.json`](../../../../schemas/source-note.schema.json)
- [`schemas/claim.schema.json`](../../../../schemas/claim.schema.json)
- [`scripts/check_research.py`](../../../../scripts/check_research.py) — fail-closed
  validator (degrades gracefully when optional external scanners are absent).

## 7. Ratification path

This container is delivered on a feature branch as a **proposal**. Promotion to canonical
requires the owner to: (a) ratify the design goals (or amend them), (b) accept the
trust-policy source hierarchy and classification handling, and (c) confirm the four open
decisions recorded in the build handoff. Until then, every doc here carries
`status: proposal`.
