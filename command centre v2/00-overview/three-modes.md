# Three modes

> Mode 1 (team), Mode 2 (orchestration), Mode 3 (choreography) are
> standalone products that share only the root protocol layer. Read
> [design-history.md](design-history.md) for why this shape emerged.

## Mode 1 — Team

**Outcome:** singularly deployable as an effective project team.

**What it is.** A substrate of skills, instructions, agents, and
profiles a single project consumes to work with a coding-agent
runtime in an organised way.

**What it requires.** A consumer project, a profile selecting
substrate elements, a build, and a coding-agent runtime.

**What it does not require.** No dispatcher. No registry. No
meta-agents.

**Contract.** [02-mode-team/contract.md](../02-mode-team/contract.md).

## Mode 2 — Orchestration

**Outcome:** singularly deployable as an orchestration layer.

**What it is.** A dispatcher + verifier that pulls work from a queue,
resolves each item to a [callable](../01-protocols/callable-contract.md),
invokes it, verifies the result, and transitions state. Runtime- and
substrate-agnostic.

**What it requires.** At least one callable (from anywhere) and a
queue source.

**What it does not require.** No Mode 1 substrate — callables can be
consumer-authored. No Mode 3 registry.

**Contract.** [03-mode-orchestration/contract.md](../03-mode-orchestration/contract.md).

## Mode 3 — Choreography

**Outcome:** multi-deployable as a choreography layer across multiple
projects in a program-of-works approach.

**What it is.** A coordinator that maintains a registry of projects,
detects drift, runs harvest cycles on cadence, and applies a promotion
contract to flow learnings into substrate.

**What it requires.** A registry file, at least one registered project
conforming to the [project contract](../01-protocols/project-contract.md),
a cadence and owner, and the three required meta-agents.

**What it does not require.** No registered project needs to run
Mode 2. Registered projects may use custom (non-homebase) substrate.

**Contract.** [04-mode-choreography/contract.md](../04-mode-choreography/contract.md).

## Independence guarantees

The three modes share only [`01-protocols/`](../01-protocols/). They
do not import from each other's source trees.

- A Mode 1 install never produces a dispatcher or registry.
- A Mode 2 install never requires Mode 1 substrate.
- A Mode 3 install never requires registered projects to run Mode 2.

This enables all 7 non-empty subsets of {Mode 1, Mode 2, Mode 3} as
valid consumption profiles. See [consumption-matrix.md](consumption-matrix.md).

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

Nothing about the modes forces a particular order of adoption. A
consumer may start with any single mode and add others later — each
additional mode is a standalone install that does not modify existing
ones.
