# Sprint 3 (DRAFT) — Substrate & Safety Reposition

**Status:** PROPOSED — sprint draft for owner approval. Not canonical; no implementation
until ADRs are ratified and the verify-first gate (S3-1) passes.
**Author:** @sprint-lead · **Date:** 2026-06-01
**Handoff in:** [`../_handoffs/2026-06-01-architect-to-sprint-lead-substrate-safety.md`](../_handoffs/2026-06-01-architect-to-sprint-lead-substrate-safety.md)
**Source ADRs:** [`decisions/design-reviews/2026-06-01-substrate-safety-reposition.md`](../../decisions/design-reviews/2026-06-01-substrate-safety-reposition.md)

## Sprint goal

Reposition agent-enterprise to an **AU-government-grade, vendor-neutral integration +
compliance template** and land the defensible core — **without** building anything the
research proved is commoditised, and **without** committing greenfield budget until the
kill-criteria are re-checked.

## Precondition gates (must pass before the sprint commits)

- **G0 — Owner ratification:** owner accepts the reposition + ADR-101…106 (or amends).
- **G1 — Verify-first (S3-1):** re-confirm the residual-novelty falsifiers. If a falsifier
  fires (a shipped tool already bundles the multi-artefact gate, or ai-rulez's security
  auditor is a real build-time gate), **stop** and re-run research before S3-5/S3-6.

## Backlog (6 items — within the 5–8 sprint band)

| ID | Item | ADR | Evidence | Size | Acceptance |
| --- | --- | --- | --- | --- | --- |
| **S3-1** | **Verify-first spike**: confirm nonce-fence absence + ai-rulez/competitor multi-artefact-gate absence | ADR-105 | `CLM-nonce-data-fence-not-found-in-competitors`, `CLM-agententerprise-residual-novelty` | S | New source-notes/claims in the KB; gate green; go/no-go recorded |
| **S3-2** | **Compliance control register MVP**: populate `research/controls/` + build-time register binding gates → ISM/PSPF/DTA-AI-Policy/NIST/SLSA, with a UK GDS ten-principle crosswalk | ADR-106 | `CLM-no-reusable-gov-template-exists`, `CLM-uk-gds-overlap`, `CLM-adv-ism1730`, `CLM-pspf-classifications` | L | ≥1 control record per framework; crosswalk doc; each binds a real gate |
| **S3-3** | **Scanner-orchestration MVP (DG-6)**: ASH-style fan-out → SARIF, integrating Invariant `mcp-scan` (artefact) + our unicode/bidi + injection-marker lint | ADR-102 | `CLM-buildtime-skill-gating-already-exists`, `CLM-ci-unicode-linting-recommended-standard`, `CLM-residual-novelty-is-orchestration-not-primitives` | L | Build emits unified SARIF; unicode/bidi lint blocks a planted sample |
| **S3-4** | **Profile-driven fail-closed posture**: `strict` (gov, hard-fail + pinned toolchain) vs `standard` (degrade); record scanner run/skip in provenance | ADR-103 | `CLM-adv-scanners-not-bundled` | M | `strict` build fails on missing required scanner; `standard` warns; both recorded |
| **S3-5** | **Runtime-scope boundary + Operate hand-off**: declare Discover/build-time scope; document hand-off to runtime guardrails; map DTA Discover/Operate/Retire | ADR-104 | `CLM-adv-not-runtime-operate-gap`, `CLM-most-named-guardrails-are-runtime`, `CLM-adv-no-irap` | S | Scope + hand-off doc; DTA lifecycle map; IRAP-feeds-not-replaces framing |
| **S3-6** | **Emitter reposition**: emit to AGENTS.md + Agent Skills open standards; freeze bespoke per-agent emitter expansion | ADR-101 | `CLM-skills-open-standard-portable`, `CLM-multitarget-is-commoditised` | M | Resolved output validates as AGENTS.md/Skills; non-goal recorded |

## Sequencing

```
G0 owner ratify ──▶ S3-1 verify-first ──▶ (gate G1)
                                           ├─▶ S3-2 compliance register  (defensible core)
                                           ├─▶ S3-3 scanner orchestration (defensible core)
                                           ├─▶ S3-4 fail-closed posture   (depends on S3-3)
                                           ├─▶ S3-5 runtime boundary       (doc, parallel)
                                           └─▶ S3-6 emitter reposition     (gated on S3-1)
```

Highest leverage-to-effort first: S3-2 + S3-3 are the defensible core; S3-6 is mostly
subtractive; S3-5 is documentation. S3-4 depends on the S3-3 orchestrator existing.

## Composition / risk notes

- 6 items, mixed S/M/L — within the repo's 5–8 band, feature-heavy but anchored by two
  doc/spike items that de-risk.
- **Carries forward** the design-goals Sprint 3–6 roadmap but **re-prioritises**: compliance
  spine and orchestration lead; signing/SLSA (heaviest) stays deferred.
- **Kill switch:** G1 failure halts S3-5/S3-6 and triggers a research re-run — the
  evidence-gated state machine the corpus endorsed.

## Natural conclusion

This draft closes the research→pm→architect→sprint-lead chain. Next real action is the
owner's: ratify the reposition + ADRs (G0), then S3-1 executes as the first verify-first
increment. Nothing here is canonical until ratified.
