---
from: "@researcher"
to: "@pm"
date: 2026-06-01
feature: substrate-safety-validation
artifact: docs/planning/research/INDEX.md
status: complete
notes: Disconfirmation-first run on both core claims. Both largely DISCONFIRMED as "novel"; residual is an integration/orchestration + AU-gov-template story. 54 source-notes, 46 claims, gate green. Evidence only — verdicts/decisions are @pm + owner's.
---

# Handoff — @researcher → @pm

## What was done

A disconfirmation-first research run (4 parallel deep-research sweeps, normalised into the
conformed knowledge base) tested the two core claims plus the compliance anchor map, with a
dedicated adversarial critic. All evidence is canonical and gate-green
(`scripts/check_research.py` exit 0): **54 source-notes, 46 claims** registered in
[`research/INDEX.md`](../research/INDEX.md).

## Evidence summary (verdicts are evidence, not decisions)

| Line of inquiry | Evidence verdict | Key claim IDs |
| --- | --- | --- |
| Claim A — substrate "author-once → multi-target" novel? | **Disconfirmed** — commoditised (ruler/rulesync/ai-rulez/block; AGENTS.md; Agent Skills) | `CLM-multitarget-is-commoditised`, `CLM-no-build-time-security-validation`, `CLM-agententerprise-residual-novelty` |
| Claim B — build-time safety gate novel? | **Largely disconfirmed** — Snyk Agent Scan + Vercel ship it; CSA prescribes CI Unicode lint; MS toolkit covers much | `CLM-buildtime-skill-gating-already-exists`, `CLM-ci-unicode-linting-recommended-standard`, `CLM-residual-novelty-is-orchestration-not-primitives` |
| Residual novelty | **Plausible, contested** — unified build-time pipeline + nonce data-fence over multi-platform artefacts | `CLM-nonce-data-fence-not-found-in-competitors` |
| Problem materiality | **Verified** — 36.8% of 3,984 scanned skills flawed (Snyk ToxicSkills) | `CLM-skill-supply-chain-is-real-active-threat` |
| AU-gov template redundancy | **Partial** — UK GDS has a reusable gov baseline; no AU one | `CLM-uk-gds-overlap`, `CLM-no-reusable-gov-template-exists` |
| Adversarial kill-case | **Well-sourced, survivable** — each criticism carries a falsifier = the repositioning | `CLM-adv-distribution-redundant`, `CLM-adv-safety-redundant-msgov`, `CLM-adv-not-runtime-operate-gap`, `CLM-adv-no-irap` |

## What @pm should validate next

1. Convert the evidence into **adopt / build-on / greenfield** recommendations per claim
   (PM decision, owner ratifies). The evidence points to: **adopt** an existing emitter for
   raw distribution; **build-on** for the safety layer (orchestrate, don't reinvent);
   **greenfield** only on the genuinely-unoccupied slice (nonce data-fence + gov-compliance
   template binding).
2. Weigh the redundancy risk honestly against the AU-gov-template gap.
3. Flag for owner: the project's value proposition likely needs **repositioning** from
   "novel substrate + novel safety" to "opinionated, AU-government-grade integration +
   compliance-bound template over best-of-breed tools."

## Fallback context block

Research complete; gate green; evidence-only. PM to produce validated recommendations in
`docs/planning/validation/`. Do not assert as canonical — proposal-tier for owner.
