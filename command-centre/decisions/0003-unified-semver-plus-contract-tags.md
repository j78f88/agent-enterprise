# ADR 0003 — Unified semver + per-mode contract tags

> **Status:** Accepted.

## Context

Three modes evolve at different rates. Different consumers care about
different parts. A Mode-2-only consumer should not have to track Mode 1
or Mode 3 churn. A consumer running long-lived agents must be able to
pin to a contract version while still receiving bug fixes within that
contract.

The Anthropic Multi-Agent Research System post identified the strongest
constraint here: *"We can't update every agent to the new version at
the same time; we use rainbow deployments."* Substrate must tolerate
N-1 (and ideally N-2) contract coexistence.

## Decision

Three independent version streams:

1. **Repo semver** — `agent-homebase@MAJOR.MINOR.PATCH`. Bumps on any
   change to any file in the repo. Used by consumers who want the whole
   framework at a known version.
2. **Protocol version** — single tag `protocol-vN`. Bumps only on a
   breaking change to anything under `01-protocols/`. Expected to bump
   very rarely.
3. **Per-mode contract tags** — `mode-1-contract-vN`,
   `mode-2-contract-vN`, `mode-3-contract-vN`. Bumps only on a breaking
   change to that mode's `contract.md` or related schemas. Expected to
   bump rarely.

**N-1 coexistence requirement:** substrate must continue to speak the
previous contract version for at least one minor release cycle after a
breaking bump. Consumers get a deprecation window, not a flag day.

## Consequences

**Positive**
- Mode-2-only consumer pins `protocol-v1 + mode-2-contract-v1` and
  tracks `agent-homebase@2.*.*` for fixes.
- A breaking change to Mode 3 does not invalidate Mode 1 or Mode 2
  consumers.
- Release notes can speak in two registers: repo-level (what changed at
  all) and contract-level (what consumers must react to).

**Negative**
- Tagging discipline becomes a release-time obligation. A release that
  forgets to bump a contract tag when the contract actually broke is
  worse than no contract tags at all.
- Two minor release cycles' worth of N-1 compatibility code may live in
  substrate at any time. Acceptable cost.

## Alternatives considered

- **Per-mode independent semver.** Rejected — three release pipelines,
  consumers must track three versions for any multi-mode consumption.
- **Single repo semver only.** Rejected — does not tell consumers what
  is safe to upgrade across vs. what is breaking.
- **Calendar-versioned tags (e.g., `2026.05`).** Rejected — doesn't
  carry break-vs-compat semantics.
