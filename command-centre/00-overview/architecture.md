# Architecture

> Layer diagram and dependency direction. For what each mode *is*, see
> [three-modes.md](three-modes.md). For consumption combinations, see
> [consumption-matrix.md](consumption-matrix.md).

## Layer diagram

```
┌──────────────────────────────────────────────────────────────────┐
│  02-mode-team/     03-mode-orchestration/   04-mode-choreography/ │
│  (Mode 1)          (Mode 2)                  (Mode 3)             │
│       │                  │                          │             │
│       └──────────────────┴──────────────────────────┘             │
│                          ▼                                        │
│  ╔════════════════════════════════════════════╗                   │
│  ║       01-protocols/  (shared, stable)       ║                   │
│  ║  callable-contract, project-contract,        ║                   │
│  ║  return-schemas, frontmatter, versioning     ║                   │
│  ╚════════════════════════════════════════════╝                   │
│                                                                   │
│  05-promotion-contract.md  (shared, used only by Mode 3)          │
└──────────────────────────────────────────────────────────────────┘
```

## Protocols layer

| File | Defines |
| --- | --- |
| [callable-contract.md](../01-protocols/callable-contract.md) | What Mode 2 dispatches against |
| [project-contract.md](../01-protocols/project-contract.md) | What Mode 3 coordinates against |
| [return-schemas.md](../01-protocols/return-schemas.md) | Tier 1/2/3 return shapes used cross-mode |
| [frontmatter-spec.md](../01-protocols/frontmatter-spec.md) | Required/optional frontmatter fields |
| [versioning-and-tags.md](../01-protocols/versioning-and-tags.md) | Repo semver + protocol tag + mode contract tags |

The protocols layer is small on purpose — every addition raises
coordination cost for every mode. See
[ADR 0002](../decisions/0002-protocols-as-shared-root.md).

## Delivery-mode folders

Each mode folder has the same shape (`contract.md`,
`install-contract.md`, `reference-impls/`, plus mode-specific files)
and has zero imports from sibling mode folders.

## Dependency direction

- Protocols depend on nothing.
- Promotion contract depends on protocols.
- Each mode depends only on protocols (Mode 3 also on the promotion
  contract).
- Reference impls depend on their mode's contract + protocols.

No cycles. No mode-to-mode dependency. This is the structural
guarantee that makes the modes individually consumable.
