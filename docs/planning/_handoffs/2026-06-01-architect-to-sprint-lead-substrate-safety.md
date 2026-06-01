---
from: "@architect"
to: "@sprint-lead"
date: 2026-06-01
feature: substrate-safety-validation
artifact: docs/decisions/design-reviews/2026-06-01-substrate-safety-reposition.md
status: complete
notes: 6 proposed ADRs (101-106). Sequence into a sprint; ADR-105 nonce-fence + kill-criteria must be a verify-first gate before any greenfield build. Load-bearing — ADR-102 orchestrate, ADR-103 gov hard-fail, ADR-106 compliance spine. Owner ratifies ADRs first.
---

# Handoff — @architect → @sprint-lead

## What to sequence

Six proposed ADRs in
[`decisions/design-reviews/2026-06-01-substrate-safety-reposition.md`](../../decisions/design-reviews/2026-06-01-substrate-safety-reposition.md):

- ADR-101 emitter build-on · ADR-102 scanner orchestration (DG-6) · ADR-103 profile-driven
  fail-closed · ADR-104 runtime-scope boundary · ADR-105 nonce data-fence (verify-first) ·
  ADR-106 compliance control register (spine).

## Sequencing constraints

1. **Verify-first gate:** ADR-105's nonce-fence and the PM kill-criteria
   (`CLM-agententerprise-residual-novelty` falsifier; ai-rulez security-auditor reality)
   must be confirmed **before** committing build budget to the greenfield slice.
2. **Owner ratification** of the reposition + ADRs precedes implementation.
3. Highest leverage-to-effort first: compliance register + orchestration MVP are the
   defensible core; emitter reposition is mostly subtractive.

## Constraint

Proposal-tier. The sprint plan is a draft for owner approval; no implementation until ADRs
are ratified and the verify-first gate passes.
