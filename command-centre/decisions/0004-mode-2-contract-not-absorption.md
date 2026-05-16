# ADR 0004 — Mode 2 is a contract, not an absorption

> **Status:** Accepted. Supersedes v1 ADR 0002 (absorb-agent-orchestration).

## Context

v1 planned to absorb an existing orchestration runtime wholesale into
`delivery-modes/orchestration/` and treat that runtime as Mode 2 itself.
This violates Anti-Fragility Pattern 7 (vendor coupling drift): if the
absorbed runtime ages or breaks, Mode 2 ages or breaks with it. A
consumer who prefers a different runtime cannot use Mode 2.

Symphony's pattern (a `SPEC.md` plus a reference implementation) shows
the correct shape: the contract is the artifact; the implementation is
one of N possible.

## Decision

Mode 2 is defined by
[`03-mode-orchestration/contract.md`](../03-mode-orchestration/contract.md).

Reference implementations live under
[`03-mode-orchestration/reference-impl/<name>/`](../03-mode-orchestration/reference-impl/),
each with its own README and a conformance test against the contract.

No single implementation is privileged. Consumers may use a reference
implementation as-is, fork it, or write their own — provided the
conformance test passes.

Mode 3 (choreography) is bound by [ADR 0001](0001-modes-as-standalone-products.md)
to the same pattern: contract first, reference impls second.

## Consequences

**Positive**
- Mode 2 outlives any single runtime.
- Consumers may import existing dispatcher runtimes as reference impls
  without restructuring them as Mode 2.
- Symphony, hatice-style runtimes, custom dispatchers, and future
  orchestrators are interchangeable.

**Negative**
- Every reference impl must include a conformance test. Adds maintenance
  overhead per impl.
- A consumer must read the contract, not just copy the reference impl,
  to use Mode 2 correctly. Documentation discipline matters more.

## Alternatives considered

- **Wholesale absorption of one runtime (v1 design).** Rejected for
  reasons above.
- **Multiple equally-canonical impls with no contract.** Rejected —
  drift between impls would be immediate and silent.
- **Single reference impl marked "recommended".** Acceptable as a soft
  signal but does not change the decision; the contract remains the
  artifact.
