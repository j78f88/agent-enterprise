# ADR 0005 — Harvest as steady-state cadence

> **Status:** Accepted.

## Context

v1 PLAN.md treated harvest as Phase 4 — a one-shot audit of a mature
project's patterns, with results back-ported into substrate. The
implicit assumption was that Phase 4 ends and the system moves on.

Anthropic Enterprise: *"Compounding returns assume sustained expert
feedback investment. Organisations that encode knowledge once and do
not maintain it will see the flywheel stall."* Harness Engineering
reaches the same conclusion: garbage-collection agents and continuous
doc-gardening keep the substrate current.

Harvest as a phase bakes in flywheel stall by construction.

## Decision

Harvest is a **steady-state recurring obligation** owned by Mode 3, not
a phase of any plan.

The Mode 3 contract
([`04-mode-choreography/contract.md`](../04-mode-choreography/contract.md))
requires:

- A declared **cadence** (per-sprint, monthly, or ad hoc with maximum
  interval).
- A declared **owner role** (which agent or human role runs each cycle).
- A required **metric movement** per cycle — at least one measurable
  substrate property must improve, even marginally.
- An **audit trail** of cycles run (date, owner, inputs, outputs,
  metric movement).

Detailed cadence semantics in
[`harvest-cadence.md`](../04-mode-choreography/harvest-cadence.md).

## Consequences

**Positive**
- Substrate stays current with observed reality.
- Flywheel stall has a named owner and a forcing function (the metric
  requirement).
- Skipped cycles are visible (the audit trail shows gaps).

**Negative**
- Operating cost in perpetuity. A program of works that adopts Mode 3
  accepts ongoing harvest work as a baseline tax.
- Owner role required. If unowned, the cadence will stop. The contract
  makes ownership explicit so this failure is detectable.

## Alternatives considered

- **Harvest as a milestone (v1 design).** Rejected for reasons above.
- **Harvest on-demand, no cadence.** Rejected — no forcing function;
  predictably skipped under pressure.
- **Automated harvest with no owner.** Rejected — meta-agents need a
  human or named role to escalate to when a cycle finds something
  ambiguous.
