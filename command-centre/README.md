# Command Centre

> **Status:** contract design. Reference impls and conformance tests
> are deferred until a real adopter signal materialises (see ADR
> 0007). v1 (`command centre/`) has been retired — personal
> harvest/onboarding notes were relocated outside the repo, and
> the substance of v1 ADRs 0003/0004 is preserved in v2's Mode 3
> install-contract and v2 ADR 0002. See `00-overview/design-history.md`
> for the full reasoning trail.

Workbench for designing agent-enterprise as three **standalone,
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

Under two anchoring constraints: agent-enterprise ships **zero
project-specific content**, and any mode can be consumed alone
alongside the consumer's own substrate.

## Folder map

```
command-centre/
  README.md                    ← this file
  PLAN.md                      ← phases and success criteria
  00-overview/                 ← design-history, three-modes, architecture, glossary, consumption-matrix
  01-protocols/                ← shared contracts (callable, project, returns, frontmatter, versioning)
  02-mode-team/                ← Mode 1 contract + install + reference substrate
  03-mode-orchestration/       ← Mode 2 contract + install + example + reference-impls/
  04-mode-choreography/        ← Mode 3 contract + install + registry/meta-agents/harvest + example + reference-impls/
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
- **Visual overview:** [command-centre-visual.html](../docs/command-centre-visual.html) — interactive cheat sheet, process flows, and architecture reference.
