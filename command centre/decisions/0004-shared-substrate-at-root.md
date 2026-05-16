# ADR 0004: Shared Substrate Stays at Root

**Status:** Accepted  
**Date:** 2026-05-16

## Context

When introducing `delivery-modes/{team,orchestration,choreography}/`, a question arises: do skills, instructions, profiles, and `init.py` belong:

1. **At the root**, shared by all modes? OR
2. **Duplicated** (or symlinked) into each mode's folder?

## Decision

Shared substrate stays at the root of agent-homebase, used by all three modes. No duplication.

```
agent-homebase/
├── skills/             ← shared substrate
├── instructions/       ← shared substrate
├── profiles/           ← shared substrate
├── starters/           ← shared substrate
├── schemas/            ← shared substrate
├── policies/           ← shared substrate
├── init.py             ← shared substrate
└── delivery-modes/
    ├── team/           ← reads substrate via relative paths
    ├── orchestration/  ← reads substrate via relative paths
    └── choreography/   ← workspace template references substrate
```

## Rationale

- **DRY:** one source of truth for the 13 skills and 24 instructions; bugs fixed once
- **Modes are thin:** each mode is mostly install logic + mode-specific assets; doesn't need to ship its own copy of the substrate
- **Easier evolution:** adding a 14th skill means one new file at `skills/<name>/`, automatically available to all modes
- **Smaller footprint:** no duplication; smaller diffs; faster clones
- **Existing structure preserved:** today's `init.py` already reads from root paths; no rewiring needed

## Consequences

- **Positive:** Substrate changes propagate to all modes immediately.
- **Positive:** No drift between modes' versions of the same skill.
- **Negative:** Modes have implicit dependency on root structure — moving `skills/` would break all modes. Mitigated by: documented contract in [00-overview/architecture.md](../00-overview/architecture.md); structure is stable.
- **Negative:** Mode-specific overrides of substrate require explicit override mechanism (currently planned: project-local `custom_instructions` in `registry.yml`, NOT mode-level overrides).

## What "Mode-Specific Assets" Means

A mode owns content that doesn't make sense outside it:

- **Mode 1 owns:** install.py wrapper, mode-specific README/docs
- **Mode 2 owns:** dispatcher/verifier agents, dispatch + tracker-adapter instructions, hooks, hatice config
- **Mode 3 owns:** workspace template (sync CLI, meta-agents, registry schema)

A mode does NOT own:
- The 13 delivery agents (substrate)
- Generic instructions (substrate)
- Profiles (substrate)
- Token substitution engine `init.py` (substrate)

## Alternatives Considered

### Duplicate substrate per mode

- Pro: Each mode is fully self-contained; can be extracted
- Con: 3x maintenance burden; drift inevitable
- Con: Bug fixes require 3 PRs

Rejected.

### Symlinks from each mode to substrate

- Pro: DRY at the file system level
- Con: Symlinks don't work uniformly across Windows/Unix
- Con: Adds indirection without value (relative paths work fine)

Rejected.

## Related

- [00-overview/architecture.md](../00-overview/architecture.md) — diagrams the layering
- [ADR 0001: Containerize in Homebase](0001-containerize-in-homebase.md)
