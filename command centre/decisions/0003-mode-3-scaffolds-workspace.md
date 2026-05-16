# ADR 0003: Mode 3 Scaffolds a Workspace

**Status:** Accepted  
**Date:** 2026-05-16

## Context

Mode 3 (Choreography) coordinates multi-project deployments. Two shapes are possible:

1. **Drop-in folder** — Mode 3 installs files into an existing repo (like Modes 1 and 2 do for projects)
2. **Scaffold a workspace** — Mode 3 creates a fresh workspace at a chosen path, with its own git repo, registry, sync CLI, and meta-agents

## Decision

**Scaffold a workspace.** `delivery-modes/choreography/install.py` creates a new directory at a user-chosen path, populated from `delivery-modes/choreography/template/`, initialized as a git repo, and ready to register projects.

## Rationale

- **Choreography is a working environment, not config** — it has a registry, a CLI, a reports folder, meta-agents. Dropping these into an existing repo would pollute that repo.
- **Single-purpose space:** the operator's choreography workspace IS for managing the program of works; mixing it with other concerns dilutes that purpose.
- **Submodule pattern fits naturally:** the workspace pulls in agent-homebase as a submodule for version pinning.
- **Lifecycle is different:** projects come and go; the workspace persists across them. A workspace deserves its own home.
- **Disposability:** if the operator wants to start over, they can delete the workspace and scaffold fresh. No surgery on existing repos.

## Consequences

- **Positive:** Clear separation: workspace is the control plane; projects are the data plane.
- **Positive:** Easy to maintain multiple workspaces (e.g. one per portfolio) — each is self-contained.
- **Positive:** Meta-agents have a natural home (`<workspace>/.github/agents/`) without colliding with delivery agents in target projects.
- **Negative:** One more directory for the operator to remember (acceptable — they live in it anyway).
- **Negative:** Submodule semantics expose users to git submodule literacy. Mitigated by: `vendor` mode option (no submodule, just a copy) and clear docs.

## Disposition of `command centre/` folder after graduation

Open sub-question: when `command centre/` graduates (Phase 6), what happens to the folder itself?

Options:
- **A. Delete entirely** (history preserved in git)
- **B. Keep as a stub README** pointing to graduated locations
- **C. Rename to `archive/command-centre/`**

**Provisional decision: A (delete).** Reasoning:
- `command centre/` is workbench infrastructure, not a feature
- Stale folders confuse future readers
- `git log -- "command centre/"` retrieves history if needed
- A redirect README is unnecessary noise

To be confirmed at graduation time per [graduation-runbook.md](../06-migration/graduation-runbook.md).

## Alternatives Considered

### Drop-in folder mode

- Pro: Consistent with Modes 1 and 2 install pattern
- Con: Pollutes the host repo with operator-only concerns
- Con: Where would meta-agents live?
- Con: How would `registry.yml` not conflict with existing configs?

Rejected.

### Hybrid: ship workspace contents but let operator place them

- Pro: Maximum flexibility
- Con: Too many places things could go; harder to document; harder to support

Rejected.

## Related

- [03-mode-choreography/spec.md](../03-mode-choreography/spec.md)
- [03-mode-choreography/workspace-template.md](../03-mode-choreography/workspace-template.md)
