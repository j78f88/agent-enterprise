# Mode 3 — Install contract

> Standalone install. Coordinated projects do not need to run Mode 1
> or Mode 2; they only need to satisfy the project contract.

## Preconditions

- Operator has a coordinator-owning repo (the "program of works" repo).
- At least one candidate project exists that satisfies the
  [project contract](../01-protocols/project-contract.md).
- A coordinator implementation is available, satisfying
  [`contract.md`](contract.md).
- Cadence and owner decided per [harvest-cadence.md](harvest-cadence.md).
- Pins recorded: `mode-3-contract-vN + protocol-vN`.

## Steps

1. Create `registry.yml` in the coordinator repo, conforming to
   [registry-schema.md](registry-schema.md).
2. Add at least one project entry per the project contract.
3. Create `harvest-cadence.yml` recording cycle interval, owner, and
   the steady-state metric being tracked.
4. Provision the three required meta-agents per [meta-agents.md](meta-agents.md)
   in whatever runtime the coordinator uses.
5. Schedule the first harvest cycle (calendar event, CI cron, or
   manual checklist — implementation choice).
6. Run the first cycle; produce the first audit record under
   `audit/<cycle-id>.md`.
7. Record pins in `.mode-3-pins`.

## Postconditions

- Registry exists and validates against the schema.
- `@audit` runs against the registry and reports drift.
- `@framework-dev` can propose a substrate change and the coordinator
  surfaces the impact list across projects.
- `@harvest` produces an audit record with metric-movement values.
- Pin file records the contract tags in use.

## Exit codes (coordinator CLI, if provided)

| Code | Meaning |
| --- | --- |
| 0 | Cycle succeeded; audit record produced |
| 1 | Registry validation failed |
| 2 | A registered project violated its declared project contract |
| 3 | Meta-agent invocation failed |
| 4 | Promotion-contract violation during cycle |
| 5 | Audit record write failed |

## Test plan

1. Add a deliberately drifted project (older `substrate_version` pin)
   and run `@audit`; confirm drift reported.
2. Propose a fake substrate change affecting one registered contract;
   run `@framework-dev`; confirm correct impact set.
3. Run a full harvest cycle on a registry containing one
   `mode_level: team` and one `mode_level: orchestration` project;
   confirm the audit record handles both correctly.
4. Attempt a promotion that violates the promotion contract; confirm
   coordinator blocks it.

## Rollback

- Stop scheduled cycles.
- The registry and audit records remain valuable artifacts even
  without an active coordinator (they are plain files).
- Coordinated projects are unaffected by coordinator rollback — they
  continue to satisfy their own contracts independently.

## Adding a project to an existing registry

1. Confirm the project conforms to the project contract.
2. Append a registry entry with the project's `id`, `repo`,
   `mode_level`, `substrate_version`, and `contract_pins`.
3. Re-run validation.
4. Run `@audit` on the new entry to baseline.
5. The project participates in the next harvest cycle.

## Removing a project from a registry

1. Delete the project's entry from `registry.yml`.
2. Note removal in the next cycle's audit record under "registry
   changes since last cycle".
3. The project itself is unaffected; only its coordination membership
   ends.
