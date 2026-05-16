# Command Centre

Workbench for restructuring agent-homebase into a three-mode delivery framework.

## Why this folder exists

1. **Containerize the restructure work** so it's easy to clean up later — nothing here ships to consumers of agent-homebase
2. **Seed Mode 3 (Choreography)** — stable contents will graduate into `delivery-modes/choreography/` once proven

## What's inside

| Folder | Purpose |
|--------|---------|
| `00-overview/` | The three-mode framing, architecture, glossary |
| `01-mode-team/` | Spec for Mode 1 (single-repo delivery team) |
| `02-mode-orchestration/` | Spec + absorption plan for Mode 2 (autonomous tracker dispatch) |
| `03-mode-choreography/` | Spec for Mode 3 (multi-project program of works) — the new build |
| `04-harvest/` | Audit reports from harvesting Verk Web's mature patterns |
| `05-onboarding/` | Per-project onboarding playbooks |
| `06-migration/` | Runbooks: absorption, graduation, rollback |
| `decisions/` | ADR-style records of structural choices |
| `PLAN.md` | The full plan (mirrors session memory) |

## Lifecycle

| Phase | State of this folder |
|-------|---------------------|
| **Now → Phase 3** | Active workbench; specs evolve here |
| **Phase 4–5** | Harvest reports + onboarding records accumulate |
| **Phase 6 (graduation)** | Stable specs move to `delivery-modes/choreography/template/`; planning artifacts move to `docs/`; this folder either deleted or kept as historical record (see [decisions/0003](decisions/0003-mode-3-scaffolds-workspace.md)) |

## Reading order

1. [PLAN.md](PLAN.md) — full plan
2. [00-overview/three-modes.md](00-overview/three-modes.md) — what each mode is
3. [00-overview/architecture.md](00-overview/architecture.md) — how they fit together
4. Mode-specific spec folders in numerical order
5. Migration runbooks when ready to execute
