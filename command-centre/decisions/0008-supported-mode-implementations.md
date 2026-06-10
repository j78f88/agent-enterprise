# ADR 0008 — Supported mode implementations

> **Status:** Accepted (2026-06-10). Refines the PLAN.md dispatcher
> non-goal; complements ADR 0004 (contract, not absorption).

## Context

The repo claims three delivery modes, but Modes 2 and 3 ship as frozen
contracts plus reference implementations only. The reference impls
under [`03-mode-orchestration/reference-impls/`](../03-mode-orchestration/reference-impls/)
and [`04-mode-choreography/reference-impls/`](../04-mode-choreography/reference-impls/)
exist to prove the contracts, not to run in production. Adopters who
want a production-grade runtime must build one themselves.

The maintainer approved (2026-06-10) productionizing supported
implementations. The existing PLAN.md non-goal — "Owning a specific
Mode 2 dispatcher implementation. Reference impls only; runtimes are
interchangeable." — blocks this. The non-goal conflates two distinct
concerns: mandating a runtime (lock-in, the real risk ADR 0004 guards
against) and offering one (a convenience that leaves the contract as
the interface).

## Decision

The repo **may** ship one *supported implementation* per mode. A
supported implementation is promoted under this five-point contract:

1. **Packaged.** Lives in `src/` as an importable package with a
   root-level CLI entry point mirroring `init.py`'s UX.
2. **Conformant.** Conformance against the frozen mode contract
   (`mode-2-contract-v1` / `mode-3-contract-v1`) is proven by pytest
   tests in `tests/`, run in CI on both OSes.
3. **Crash-safe.** Provides crash-safety and idempotency beyond the
   reference impl: atomic state writes and resume semantics per the
   install-contract rollback sections
   ([Mode 2](../03-mode-orchestration/install-contract.md#rollback),
   [Mode 3](../04-mode-choreography/install-contract.md#rollback)).
4. **Documented.** Has an adopter-facing doc in `docs/` and is named
   in the mode's `install-contract.md` as the supported implementation.
5. **Non-displacing.** The reference implementation stays frozen
   byte-unchanged as contract pedagogy. PLAN.md success criterion 2
   (each mode has at least one reference implementation) still holds.

An implementation that fails any of the five points is not promoted —
it stays a reference impl or lives outside the repo.

## Consequences

**Positive**
- Adopters get a production-grade runtime without building one, while
  runtimes remain interchangeable: the contract, not the
  implementation, is the interface.
- The original non-goal's concern (runtime lock-in) is preserved —
  adopters may still bring their own runtime, and conformance is
  checked against the contract alone.
- Frozen contracts are unchanged. If a supported implementation needs
  a breaking contract change, that is a `-v2` tag with N-1 coexistence
  per [ADR 0003](0003-unified-semver-plus-contract-tags.md), never an
  in-place edit.

**Negative**
- A supported implementation is a maintenance obligation: CI on both
  OSes, crash-safety guarantees, and adopter docs must be kept current.
- Two implementations per mode (frozen reference plus supported) can
  confuse newcomers. The install-contract naming requirement (point 4)
  exists to keep the recommendation unambiguous.

## Alternatives considered

- **Keep reference impls only (status quo).** Rejected — adopters
  repeatedly rebuild the same production hardening; the maintainer has
  approved closing that gap.
- **Promote a reference impl in place.** Rejected — reference impls
  are contract pedagogy and stay frozen; productionizing them would
  blur the contract-first pattern of ADR 0004.
- **Ship the supported implementation as a separate repo.** Rejected —
  splits CI, versioning, and conformance testing away from the
  contract it must track; ADR 0003's tag streams already give
  consumers the pinning granularity they need.
