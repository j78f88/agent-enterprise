# ADR 0002: Absorb agent-orchestration as Mode 2

**Status:** Accepted  
**Date:** 2026-05-16

## Context

`agent-orchestration` currently exists as a standalone repo containing:
- `@dispatcher` and `@verifier` agents
- Tracker adapter instructions (Linear, GitHub, GitLab)
- Dispatch hooks (`afterCreate.sh`, `onComplete.sh`)
- WORKFLOW.md for hatice-style runtime
- Architectural docs

It's overlaid at deploy time via the "three-repo composition" model: homebase + agent-orchestration + project repo, all cloned and merged by `afterCreate.sh`.

When introducing the formal three-mode structure (Team / Orchestration / Choreography), Mode 2 IS what `agent-orchestration` provides. Three options:

1. **Absorb** — move all `agent-orchestration` contents into `delivery-modes/orchestration/`
2. **Mirror** — Mode 2 in homebase is a thin wrapper that clones `agent-orchestration` at install time
3. **Keep separate** — Mode 2 in homebase is just docs + a setup script pointing at `agent-orchestration`

## Decision

**Absorb.** Move all `agent-orchestration` contents into `delivery-modes/orchestration/` inside agent-homebase. Archive the standalone repo with a redirect README.

## Rationale

- **Content is genuinely generic** — `@dispatcher`, `@verifier`, tracker adapters, hatice config — none of it is project-specific. It belongs with the framework, not in a parallel repo.
- **Two-repo composition is simpler than three** — `afterCreate.sh` clones one fewer repo; one fewer thing to version-pin.
- **Mode 2 becomes a first-class deployment option** rather than "the orchestration repo you also need" — clearer mental model for users.
- **Versioning aligns** — homebase + orchestration evolve in lockstep, no skew possible.
- **Consistent with [ADR 0001](0001-containerize-in-homebase.md)** — "delivery patterns belong with the framework."

## Consequences

- **Positive:** Simpler deploy model (one fewer clone); clearer mental model; locked-step versioning.
- **Positive:** Mode 2's `install.py` can call Mode 1's `install.py` directly (in-process), instead of relying on filesystem overlay.
- **Negative:** Existing hatice deployments need migration when `afterCreate.sh` changes. Mitigated by: 7-day soak period, backward-compat shim if needed, clear migration runbook.
- **Negative:** Loss of clean separation if Mode 2 evolution becomes politically contentious (unlikely — single operator).

## Alternatives Considered

### Mirror

- Pro: agent-orchestration repo continues independent existence
- Con: Two repos to version, two release cycles, version skew risk
- Con: Mode 2's installer becomes a network operation (must clone)

Rejected.

### Keep separate

- Pro: Minimal change to existing structure
- Con: Doesn't solve the "Mode 2 is awkward" UX problem
- Con: Mode 3 still has to reason about three repos

Rejected.

## Migration Path

See [02-mode-orchestration/absorption-checklist.md](../02-mode-orchestration/absorption-checklist.md) and [06-migration/absorption-runbook.md](../06-migration/absorption-runbook.md).

## Related

- [ADR 0001: Containerize in Homebase](0001-containerize-in-homebase.md)
- [ADR 0003: Mode 3 Scaffolds Workspace](0003-mode-3-scaffolds-workspace.md) — Mode 3's pattern differs from Mode 2 because Mode 3 is a full workspace, not just files
