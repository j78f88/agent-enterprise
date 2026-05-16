# Architecture

> How [`01-protocols/`](../01-protocols/) and the three delivery-mode
> folders compose into the v2 design.

## Layer diagram

```
┌─────────────────────────────────────────────────┐
│  02-mode-team/     03-mode-orchestration/   04-mode-choreography/  │
│  (Mode 1)          (Mode 2)                  (Mode 3)               │
│    │                   │                          │                │
│    └─────────────┴────────────────────────────┴───────────────┐    │
│                       ▼                                       │    │
│  ╔══════════════════════════════════════════╗                  │    │
│  ║          01-protocols/  (shared, stable)    ║                  │    │
│  ║  callable-contract, project-contract,       ║                  │    │
│  ║  return-schemas, frontmatter, versioning    ║                  │    │
│  ╚═══════════════════════════════════════════╝                  │    │
│                                                                  │    │
│  05-promotion-contract.md  (shared, used only by Mode 3)         │    │
└──────────────────────────────────────────────────────────────────┘
```

## Protocols layer

Five files under [`01-protocols/`](../01-protocols/):

| File | Defines |
| --- | --- |
| [callable-contract.md](../01-protocols/callable-contract.md) | What Mode 2 dispatches against |
| [project-contract.md](../01-protocols/project-contract.md) | What Mode 3 coordinates against |
| [return-schemas.md](../01-protocols/return-schemas.md) | Tier 1/2/3 return shapes used cross-mode |
| [frontmatter-spec.md](../01-protocols/frontmatter-spec.md) | Required/optional frontmatter fields |
| [versioning-and-tags.md](../01-protocols/versioning-and-tags.md) | Repo semver + protocol tag + mode contract tags |

The protocols layer is small on purpose. Every file added here
increases the coordination cost for every mode. See [ADR 0002](../decisions/0002-protocols-as-shared-root.md).

## Delivery modes layer

Three sibling folders, identical shape:

```
NN-mode-<name>/
  contract.md              ← what conformance means
  install-contract.md      ← how a consumer installs
  reference-impl/          ← worked implementation(s)
  <mode-specific files>    ← e.g., registry-schema, meta-agents
```

A mode folder has zero imports from sibling mode folders. It may
reference protocols and (for Mode 3) the promotion contract.

## Reference substrate

The agent-homebase root ([`skills/`](../../skills/),
[`instructions/`](../../instructions/), [`agents/`](../../agents/),
[`profiles/`](../../profiles/), [`init.py`](../../init.py)) is the
reference Mode 1 substrate. See [02-mode-team/reference-substrate.md](../02-mode-team/reference-substrate.md).

Reference implementations for Mode 2 and Mode 3 live under each
mode's `reference-impl/` subfolder.

Reference implementations exist to prove the contract is satisfiable.
Consumers may use them, fork them, or write their own.

## Dependency direction

- Protocols depend on nothing.
- Promotion contract depends on protocols.
- Each mode depends only on protocols (and Mode 3 also on promotion
  contract).
- Reference impls depend on their mode's contract + protocols.

No cycles. No mode-to-mode dependency. This is the structural
guarantee that makes the modes individually consumable.
