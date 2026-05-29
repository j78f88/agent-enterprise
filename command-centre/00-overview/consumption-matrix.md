# Consumption matrix

> Which mode combinations are valid and how to take each one. Every
> non-empty subset of {Mode 1, Mode 2, Mode 3} is valid. For per-mode
> descriptions and the selection guide, see
> [three-modes.md](three-modes.md).

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

All seven are first-class. Pairs and triples are simply two or three
sequential standalone installs — no glue contract.

Per-mode install steps:
[Mode 1](../02-mode-team/install-contract.md),
[Mode 2](../03-mode-orchestration/install-contract.md),
[Mode 3](../04-mode-choreography/install-contract.md).

## Sparse-checkout recipes

A consumer wanting only one or two modes from the agent-enterprise repo
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

The protocols folder and schemas are required for every recipe.

Sparse-checkout is one mechanism, not the only one. A consumer may
equally vendor the relevant folders, write their own implementation
against the contracts, or use a release artifact pinned to specific
contract tags.
