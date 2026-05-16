# Three modes

> Mode 1 (team), Mode 2 (orchestration), Mode 3 (choreography) are
> standalone products that share only the root protocol layer. See
> [design-history.md](design-history.md) for why this shape emerged.

## Selection guide

| If you want… | Use |
| --- | --- |
| A single-project agent team library | Mode 1 alone |
| Issue-driven dispatch on your existing prompts | Mode 2 alone |
| Visibility + drift control across many projects | Mode 3 alone |
| Team library + non-interactive dispatch on one project | Mode 1 + Mode 2 |
| Program-of-works over multiple Mode 1 teams | Mode 1 + Mode 3 |
| Centrally-coordinated dispatched projects | Mode 2 + Mode 3 |
| Everything | All three |

Adoption order is free. Each additional mode is a standalone install
that does not modify existing ones.

## Mode summaries

- **Mode 1 — Team.** A substrate of skills, instructions, agents, and
  profiles a single project consumes interactively. Contract:
  [02-mode-team/contract.md](../02-mode-team/contract.md).
- **Mode 2 — Orchestration.** A dispatcher + verifier that pulls work
  from a queue, resolves each item to a
  [callable](../01-protocols/callable-contract.md), invokes it, and
  transitions state. Substrate-agnostic. Contract:
  [03-mode-orchestration/contract.md](../03-mode-orchestration/contract.md).
- **Mode 3 — Choreography.** A coordinator that maintains a project
  registry, detects drift, runs harvest cycles on cadence, and applies
  a promotion contract. Contract:
  [04-mode-choreography/contract.md](../04-mode-choreography/contract.md).

## Independence guarantees

- A Mode 1 install never produces a dispatcher or registry.
- A Mode 2 install never requires Mode 1 substrate.
- A Mode 3 install never requires registered projects to run Mode 2.

This enables all 7 non-empty subsets of {Mode 1, Mode 2, Mode 3} as
valid consumption profiles. See
[consumption-matrix.md](consumption-matrix.md).
