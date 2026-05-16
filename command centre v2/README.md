# Command Centre v2

> **Status:** design workbench. Not yet released. v1 at
> [command centre/](../command%20centre/) remains as historical
> reference until v2 is accepted.

Workbench for designing agent-homebase as three **standalone,
independently consumable delivery modes** (team / orchestration /
choreography) on top of a small shared protocol layer.

> **Start here:** [00-overview/design-history.md](00-overview/design-history.md)
> — the full reasoning trail (origin, research consulted, v1 errors,
> alternatives eliminated). Read it before any contract document.

## Three outcomes

1. **Singularly deployable as an effective project team.** → Mode 1.
2. **Singularly deployable as an orchestration layer.** → Mode 2.
3. **Multi-deployable as a choreography layer across multiple
   projects in a program-of-works approach.** → Mode 3.

Under two anchoring constraints: agent-homebase ships **zero
project-specific content**, and any mode can be consumed alone
alongside the consumer's own substrate.

## Folder map

```
command centre v2/
  README.md                    ← this file
  PLAN.md                      ← phases and success criteria
  00-overview/                 ← design-history, three-modes, architecture, glossary, consumption-matrix
  01-protocols/                ← shared contracts (callable, project, returns, frontmatter, versioning)
  02-mode-team/                ← Mode 1 contract + install + reference substrate
  03-mode-orchestration/       ← Mode 2 contract + install + example + reference-impl/
  04-mode-choreography/        ← Mode 3 contract + install + registry/meta-agents/harvest + example + reference-impl/
  05-promotion-contract.md     ← shared, used only by Mode 3
  decisions/                   ← ADRs 0001-0006
```

## Cross-references

- **For "why":** [design-history.md](00-overview/design-history.md)
  and the ADRs under [decisions/](decisions/).
- **For "what":** [three-modes.md](00-overview/three-modes.md) and the
  per-mode `contract.md` files.
- **For "how":** the `install-contract.md` files under each mode folder.
- **For "which combinations":** [consumption-matrix.md](00-overview/consumption-matrix.md).
- **For "how the pieces fit":** [architecture.md](00-overview/architecture.md).
- **For terminology:** [glossary.md](00-overview/glossary.md).
