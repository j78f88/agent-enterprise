# PLAN — Command Centre v2

> Generic implementation roadmap for v2. No project-specific content.
> Pairs with [README.md](README.md) (orientation) and
> [00-overview/design-history.md](00-overview/design-history.md) (why).

## Goals

- Deliver three standalone delivery modes that satisfy the user's
  three stated outcomes.
- Keep agent-homebase 100% generic.
- Make all 7 non-empty mode combinations valid consumption profiles.
- Establish a small, slow-changing protocol layer that all modes
  share.
- Make harvest a steady-state obligation with explicit ownership and
  cadence.
- Version contracts independently of repo semver to support N-1
  coexistence.

## Non-goals

- Authoring project-specific content. Substrate ships zero project
  content.
- Building a CLI for cross-project synchronisation. Native git is
  sufficient.
- Owning a specific Mode 2 dispatcher implementation. Reference impls
  only; runtimes are interchangeable.
- Owning a specific runtime (Copilot, Claude Code, etc.). Build
  artifacts target multiple runtimes; the framework prefers none.
- Backward compatibility with v1 layout. v1 retires; v2 supersedes.

## Phases

### Phase 1 — Protocols layer

Deliverables:
- Five protocol files under [`01-protocols/`](01-protocols/) (done).
- Canonical JSON Schemas added to [`schemas/`](../schemas/) where
  missing.
- Frontmatter validation in `init.py` upgraded to enforce the v1
  protocol.

Exit criteria: protocol files reviewed and accepted; `protocol-v1`
tag candidate identified.

### Phase 2 — Mode contracts + reference implementations

Deliverables:
- Three `contract.md` files (done).
- Three `install-contract.md` files (done).
- Mode 1 reference substrate mapping (done).
- Mode 2 reference-impl directory populated with at least one worked
  dispatcher example.
- Mode 3 reference-impl directory populated with at least one worked
  coordinator example (CI-driven cadence is acceptable).

Exit criteria: each contract has at least one passing reference impl
and a non-homebase example.

### Phase 3 — Promotion contract + harvest cadence

Deliverables:
- [`05-promotion-contract.md`](05-promotion-contract.md) (done).
- [`harvest-cadence.md`](04-mode-choreography/harvest-cadence.md) (done).
- [`meta-agents.md`](04-mode-choreography/meta-agents.md) (done).
- Mixed-fleet example walked end-to-end with a fabricated registry.

Exit criteria: a dry-run harvest cycle completes against a fake
registry of three projects and produces a valid audit record.

### Phase 4 — Adopter onboarding template

Deliverables:
- Quickstart guide per mode pointing to install contracts.
- Adoption checklist for each consumption combination from the
  consumption matrix.
- Pin-file templates per mode.
- Migration note template per contract bump.

Exit criteria: a new consumer can install any single mode using only
this workbench in under one working session.

### Phase 5 — v1 retirement

Deliverables:
- Commit removing [`command centre/`](../command%20centre/) in
  isolation.
- Note in repo changelog pointing at the final v1 commit hash.
- Final tag candidates: `agent-homebase@2.0.0`, `protocol-v1`,
  `mode-1-contract-v1`, `mode-2-contract-v1`, `mode-3-contract-v1`.

Exit criteria: v2 is the single workbench; v1 is removed from `main`
but retrievable via tag.

## Success criteria

1. Each mode has a contract that a consumer can verify their
   substrate or dispatcher or coordinator satisfies.
2. Each mode has at least one reference implementation.
3. Each mode has a non-homebase example (or, for Mode 1, an explicit
   replaceability section).
4. The seven valid consumption combinations are documented and
   actionable.
5. The repo contains zero project-specific content.
6. Versioning supports N-1 coexistence per [ADR 0003](decisions/0003-unified-semver-plus-contract-tags.md).
7. Conformance tests under [`tests/`](../tests/) cover each contract.

## Open questions

Deferred for review after Phase 2:

- **Q1.** Which Mode 2 reference-impl runtimes should ship in v1?
  (Candidates: a CI-driven dispatcher; a long-running daemon. The
  contract permits any; the question is which proves the contract
  best.)
- **Q2.** Should Mode 3 reference-impl include a scheduled CI
  example or remain a documentation-only contract?
- **Q3.** Are three meta-agents sufficient, or should a fourth
  (`@migration`) be required for substrate-version upgrades affecting
  multiple projects?
- **Q4.** Does the protocol layer need a `dispatcher-contract.md`
  separate from `callable-contract.md`, or is the current single
  contract enough?

These are documented as Q1–Q4 in
[design-history.md §12](00-overview/design-history.md#12-open-questions-deferred-for-after-skeleton-review).
