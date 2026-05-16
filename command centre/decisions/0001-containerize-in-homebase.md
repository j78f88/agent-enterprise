# ADR 0001: Containerize Restructure Work Inside agent-homebase

**Status:** Accepted  
**Date:** 2026-05-16

## Context

agent-homebase is being restructured to support three deployment modes (Team / Orchestration / Choreography). The new "Choreography" mode requires a command-centre concept — a workspace that coordinates multiple project deployments.

Two options for housing the development work and Mode 3 specs:

1. **Separate repo** (`agent-command-centre`) — a workbench parallel to agent-homebase
2. **Containerized folder inside agent-homebase** (`command centre/`)

## Decision

Containerize the restructure work inside agent-homebase in a dedicated `command centre/` folder. Mode 3 itself ships as `delivery-modes/choreography/` once stable, also inside agent-homebase.

## Rationale

- **Pollution rule reframed:** "pollution" = project-specific work (Verk's templates, client branding); generic delivery patterns belong WITH the framework
- **Single source of truth:** one repo, one version, one history — easier to keep modes consistent as homebase evolves
- **Mirrors existing pattern:** `profiles/` already ships deployment-shaped content; `delivery-modes/` is the same pattern on a different axis
- **Easy cleanup:** containerized in a single folder; can be deleted or graduated cleanly
- **No submodule complexity** for daily framework work (submodules are still used at Mode 3 deploy time, but operators don't deal with them while developing the framework itself)

## Consequences

- **Positive:** Single repo to clone, build, test. No version skew between workbench and framework. Modes evolve together.
- **Positive:** "Containerization" provides clean cleanup path: `command centre/` graduates in Phase 6, then either deletes or stays as historical pointer.
- **Negative:** agent-homebase repo gets larger (acceptable; specs are small).
- **Negative:** Risk of in-progress workbench content leaking into deploys if delivery modes accidentally reference `command centre/`. Mitigated by: clear separation in folder structure, lifecycle documented in [README](../README.md), `.gitignore` rules if needed.

## Alternatives Considered

### Separate `agent-command-centre` repo

- Pro: Strict isolation between framework and workbench
- Pro: Easy to archive or delete the workbench without affecting homebase
- Con: Submodule complexity for everyday framework dev
- Con: Version skew risk
- Con: Two repos for one logical concern

Rejected because the isolation benefit doesn't justify the operational overhead, and "containerization in a folder" achieves the cleanup benefit without the multi-repo cost.

## Related

- [ADR 0002: Absorb agent-orchestration](0002-absorb-agent-orchestration.md) — same logic applied to Mode 2
- [ADR 0004: Shared Substrate at Root](0004-shared-substrate-at-root.md)
