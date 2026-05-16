# Command Centre v2

> **Status:** design workbench. Not yet released. v1 at [command centre/](../command%20centre/)
> remains in place as historical reference until v2 is reviewed and
> accepted.

Workbench for designing agent-homebase as three **standalone,
independently consumable delivery modes** (team / orchestration /
choreography) on top of a small shared protocol layer.

> **Start here:** [00-overview/design-history.md](00-overview/design-history.md)
> captures the full reasoning trail — origin, research consulted,
> errors found in v1, alternatives eliminated, and influences behind
> every v2 decision. Read it before any contract document.

## Purpose

Deliver the three outcomes stated by the user:

1. **Singularly deployable as an effective project team.** → Mode 1.
2. **Singularly deployable as an orchestration layer.** → Mode 2.
3. **Multi-deployable as a choreography layer across multiple
   projects in a program-of-works approach.** → Mode 3.

Under two anchoring constraints:

- **agent-homebase is totally generic.** No information about any
  specific project.
- **Someone could consume one mode and have their own in-project
  agents and skills alongside it.** Modes are standalone, not
  additive layers.

## How v2 differs from v1

| Aspect | v1 (`command centre/`) | v2 (this workbench) |
| --- | --- | --- |
| Mode shape | Additive layers on shared substrate | Standalone products sharing only protocols |
| Project content | Mixed with framework content | Removed entirely — framework is 100% generic |
| Mode 2 | Absorbs agent-orchestration runtime | Contract; runtimes are reference impls |
| Harvest | A phase | Steady-state cadence with owner + metric |
| Sync CLI | Proposed six commands | None — registry file + harvest script |
| Versioning | Repo semver only | Repo semver + protocol tag + per-mode contract tags |

Full reasoning in [design-history.md](00-overview/design-history.md).

## Folder map

```
command centre v2/
  README.md                    ← this file
  PLAN.md                      ← phases and success criteria
  00-overview/                 ← design-history, three-modes, architecture, glossary
  01-protocols/                ← shared contracts (callable, project, returns, frontmatter, versioning)
  02-mode-team/                ← Mode 1 contract + install + reference substrate mapping
  03-mode-orchestration/       ← Mode 2 contract + install + non-homebase example + reference-impl/
  04-mode-choreography/        ← Mode 3 contract + install + registry-schema + meta-agents + harvest + mixed-fleet + reference-impl/
  05-promotion-contract.md     ← shared, used only by Mode 3
  decisions/                   ← ADRs 0001-0006
```

## Lifecycle

1. **Skeleton** — all stub files in place (done).
2. **Population** — each stub filled with normative content (done).
3. **Review** — user accepts shape and content; identifies gaps.
4. **Reference impl scaffolding** — directories under `reference-impl/`
   populated with worked examples.
5. **Conformance tests** — added to [`tests/`](../tests/) covering
   contract assertions.
6. **Release** — first `protocol-v1` + `mode-N-contract-v1` tags cut.
7. **v1 retirement** — `command centre/` removed in a separate commit.

See [PLAN.md](PLAN.md) for phase-by-phase detail.

## Cross-references

- **For "why":** [00-overview/design-history.md](00-overview/design-history.md)
  and the ADRs under [decisions/](decisions/).
- **For "what":** [00-overview/three-modes.md](00-overview/three-modes.md)
  and the contract.md files under each mode folder.
- **For "how":** the install-contract.md files under each mode folder.
- **For "which combinations":** [00-overview/consumption-matrix.md](00-overview/consumption-matrix.md).
- **For "how the pieces fit":** [00-overview/architecture.md](00-overview/architecture.md).
- **For terminology:** [00-overview/glossary.md](00-overview/glossary.md).
