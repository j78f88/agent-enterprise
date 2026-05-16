# ADR 0002 — Protocols as shared root

> **Status:** Accepted.

## Context

Modes are standalone products ([ADR 0001](0001-modes-as-standalone-products.md))
but they share a small set of conventions: how a unit of work is
described (callable contract), how a project is described (project
contract), how results are returned (tier 1/2/3 schemas), how files
declare metadata (frontmatter), and how versions are pinned.

If each mode defined these independently, drift is inevitable: Mode 2's
result shape ≠ Mode 3's expected input shape; Mode 1's frontmatter ≠
Mode 2's. Modes would couple to each other through implicit shared
assumptions.

## Decision

A tiny, stable, slow-changing **protocols layer** at
[`01-protocols/`](../01-protocols/) carries all shared conventions:

- [callable-contract.md](../01-protocols/callable-contract.md) — what
  Mode 2 dispatches against
- [project-contract.md](../01-protocols/project-contract.md) — what
  Mode 3 coordinates against
- [return-schemas.md](../01-protocols/return-schemas.md) — tier 1/2/3
- [frontmatter-spec.md](../01-protocols/frontmatter-spec.md)
- [versioning-and-tags.md](../01-protocols/versioning-and-tags.md)

Modes may depend on the protocols layer. Modes may not depend on each
other. Substrate (root `skills/`, `instructions/`, `agents/`,
`schemas/`) may depend on the protocols layer.

## Consequences

**Positive**
- A consumer wanting only Mode 2 pulls `01-protocols/` plus
  `03-mode-orchestration/` and has a coherent product.
- Cross-mode interop (e.g., Mode 3 consuming Mode 2 results) works by
  shared protocol, not by hidden coupling.
- Drift detection is easy: a change in `01-protocols/` is a signal to
  audit every dependent.

**Negative**
- Protocols layer becomes a coordination point. Any change ripples
  downstream. Hence the requirement that protocol changes are rare and
  tag-versioned ([ADR 0003](0003-unified-semver-plus-contract-tags.md)).
- A new mode must justify any protocol extension before being added.

## Alternatives considered

- **No protocols layer; modes redefine shared concepts.** Rejected —
  guaranteed drift, hidden coupling.
- **Protocols inside each mode.** Rejected — three copies, no single
  source of truth.
- **Protocols inside substrate (root).** Rejected — couples protocols
  to the Mode 1 reference substrate; a Mode-2-only consumer would have
  to pull substrate they don't use.
