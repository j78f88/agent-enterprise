# ADR 0001 — Modes as standalone products

> **Status:** Accepted. Supersedes v1 ADR 0001 (containerize-in-enterprise).

## Context

agent-enterprise v1 treated three deployability modes (team, orchestration,
choreography) as additive layers on top of a single substrate. v1 also
co-located the framework with author-specific program-of-works content
under a `command centre/` folder, with a plan to graduate generic parts
later.

Two clarifications made this design untenable:

1. agent-enterprise must remain 100% generic — no project-specific files.
2. The three modes must be consumable individually or in any combination,
   including a consumer who only wants Mode 2 and runs it against their
   own callables.

If Mode 2 requires Mode 1 substrate to operate, the second constraint
cannot be met. Same for Mode 3.

Full reasoning: [design-history §7-8](../00-overview/design-history.md#7-the-two-clarifications-that-locked-v2s-shape).

## Decision

Each delivery mode is a **standalone product**. Each ships:

- A `contract.md` describing what it means to satisfy the mode, in
  runtime- and substrate-agnostic terms.
- One or more `reference-impl/` subfolders demonstrating the contract.
- An `install-contract.md` describing standalone installation with no
  assumption that any other mode is present.

Modes depend only on [`01-protocols/`](../01-protocols/) at the root.
Modes do not depend on each other.

## Consequences

**Positive**
- All 7 non-empty subsets of {Mode 1, Mode 2, Mode 3} are valid
  consumption profiles.
- Reference implementations evolve, are replaced, or sit alongside
  alternatives without changing the contract.
- Contract changes are explicit and tag-versioned independently
  (see [ADR 0003](0003-unified-semver-plus-contract-tags.md)).

**Negative**
- Each mode requires a conformance test against its contract.
- Each mode requires at least one worked example proving portability
  against a non-substrate consumer.
- ~1 day of additional design effort over the simpler additive-layers
  alternative.

## Alternatives considered

- **Reading A — modes as additive layers on Mode 1.** Simpler but fails
  the standalone-consumption requirement.
- **Bundle all three modes into one product.** Defeats the separability
  the author asked for.
- **Ship modes as separate repos.** Maximises independence but creates
  three release pipelines and breaks the shared-protocol layer.
  Co-location in one repo with strict folder boundaries chosen instead.
