# Mode 3 — Install contract

> Standalone install. Coordinated projects do not need to run Mode 1
> or Mode 2; they only need to satisfy the project contract.

## Install shape: scaffold a fresh workspace

Mode 3 install **creates a fresh coordinator workspace** at a path
the operator chooses, rather than dropping files into an existing
repo. The workspace owns `registry.yml`, `harvest-cadence.yml`, the
three meta-agents, and the `audit/` records.

Why scaffold rather than drop-in:

- **Choreography is a working environment, not config.** Dropping a
  registry, meta-agents, and an audit log into a coordinated project
  pollutes that project with operator-only concerns.
- **Lifecycles differ.** Coordinated projects come and go; the
  workspace persists across them. A workspace deserves its own home.
- **Multiple workspaces are natural** (one per portfolio); each is
  self-contained.
- **Disposability.** Operators can delete and re-scaffold without
  surgery on any coordinated project.

The reference implementation pins agent-enterprise via submodule
(default) or vendored copy (`--vendor` flag) for version stability.

## Preconditions

- A coordinator-owning repo (the "program of works" repo).
- At least one candidate project satisfying the
  [project contract](../01-protocols/project-contract.md).
- A coordinator implementation satisfying [`contract.md`](contract.md).
- Cadence and owner decided per [harvest-cadence.md](harvest-cadence.md).
- Pins recorded: `mode-3-contract-vN + protocol-vN`.

## Steps

1. Create `registry.yml` conforming to
   [registry-schema.md](registry-schema.md); add at least one project
   entry per the project contract.
2. Create `harvest-cadence.yml` recording cycle interval, owner, and
   the steady-state metric.
3. Provision the three required meta-agents per
   [meta-agents.md](meta-agents.md).
4. Schedule the first harvest cycle (calendar, CI cron, or manual
   checklist) and produce the first audit record under
   `audit/<cycle-id>.md`.
5. Record pins in `.mode-3-pins`.

## Postconditions

- Registry validates against the schema.
- `@audit` reports drift.
- `@framework-dev` surfaces an impact list across projects for a
  proposed substrate change.
- `@harvest` produces audit records with metric-movement values.
- Pin file records the contract tags.

## Adding or removing a project

Add: confirm project conformance, append a registry entry, re-validate,
baseline with `@audit`. Remove: delete the entry and note it in the
next cycle's audit record. Removed projects are unaffected.

## Rollback

Stop scheduled cycles. Registry and audit records remain valuable as
plain files. Coordinated projects continue to satisfy their own
contracts independently.
