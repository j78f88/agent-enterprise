# Consumption matrix

> Which mode combinations are valid and how a consumer takes each one.
> Every non-empty subset of {Mode 1, Mode 2, Mode 3} is valid.

## Valid combinations

| # | Mode 1 | Mode 2 | Mode 3 | Use case |
| --- | :---: | :---: | :---: | --- |
| 1 | ✓ |   |   | Single-project agent team library |
| 2 |   | ✓ |   | Dispatch consumer's own callables |
| 3 |   |   | ✓ | Coordinate projects with custom substrates |
| 4 | ✓ | ✓ |   | Team library + non-interactive dispatch |
| 5 | ✓ |   | ✓ | Program-of-works over Mode 1 teams |
| 6 |   | ✓ | ✓ | Coordinated dispatched projects |
| 7 | ✓ | ✓ | ✓ | Everything |

All seven are first-class. None require modifying or wrapping the
others.

## How to consume Mode 1 alone

Follow [02-mode-team/install-contract.md](../02-mode-team/install-contract.md).

Footprint in consumer repo: profile file, built artifacts, pin file.
No runtime processes. No registry membership.

## How to consume Mode 2 alone

Follow [03-mode-orchestration/install-contract.md](../03-mode-orchestration/install-contract.md).

Footprint: callable manifests, dispatcher configuration, dispatcher
process (CI / scheduled / service), pin file. Substrate not required.
See [non-homebase-example.md](../03-mode-orchestration/non-homebase-example.md).

## How to consume Mode 3 alone

Follow [04-mode-choreography/install-contract.md](../04-mode-choreography/install-contract.md).

Footprint in coordinator repo: registry, cadence config, audit
records, three meta-agents, pin file. Registered projects may use
any substrate including custom ones.

## How to consume any pair

Each mode installs against its own contract. Pairs are simply two
sequential standalone installs. No additional contract glues them.

- **Mode 1 + Mode 2:** Install Mode 1 (substrate available
  interactively). Install Mode 2 (dispatcher resolves to substrate
  skills as callables). Both work simultaneously.
- **Mode 1 + Mode 3:** Install Mode 1 in each project. Set up Mode 3
  coordinator repo. Each project's profile is its own; the registry
  observes them.
- **Mode 2 + Mode 3:** Install Mode 2 in each project that needs
  dispatch. Set up Mode 3 coordinator that tracks them as
  `mode_level: orchestration`.

## How to consume all three

The sum of the three install contracts. Order does not matter —
adding any mode later is purely additive.

This combination represents the in-house reference scenario:
agent-homebase itself uses Mode 1 substrate, may add Mode 2 dispatch
for its own backlog, and could be coordinated under a Mode 3 registry
if part of a larger program.

## Sparse-checkout recipes

A consumer wanting only one or two modes from the agent-homebase repo
can sparse-checkout the needed folders:

```bash
# Mode 2 only:
git sparse-checkout set \
  command\ centre\ v2/01-protocols \
  command\ centre\ v2/03-mode-orchestration \
  schemas

# Mode 3 only:
git sparse-checkout set \
  command\ centre\ v2/01-protocols \
  command\ centre\ v2/04-mode-choreography \
  command\ centre\ v2/05-promotion-contract.md \
  schemas
```

The protocols folder and schemas are required for every mode and
therefore every recipe.

This is one mechanism, not the only one. A consumer can equally
vendor the relevant folders, write their own implementation against
the contracts, or use a release artifact pinned to specific contract
tags.
