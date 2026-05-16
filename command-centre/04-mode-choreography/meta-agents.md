# Mode 3 — Meta-agents

> Choreography-level agents that operate across the program of works
> rather than inside a single project. Three are required by
> `mode-3-contract-v1`. Coordinators may add more.

## `@framework-dev`

**Role.** Designs and proposes changes to substrate (skills,
instructions, contracts) based on observed needs across projects.

**Inputs.**
- Registry snapshot.
- Audit records from recent cycles.
- Specific candidate area for change (e.g., "propose update to skill X"
  or "propose new contract field Y").

**Outputs (tier 3 return).**
- Proposed substrate diff.
- Impact list: which registered projects' `contract_pins` are
  affected.
- Migration note draft.
- Recommended target version bump (repo semver + which contract tags).

**State transitions caused.** None directly. Proposals enter the
substrate change-review workflow; merge is governed by repo PR rules.

## `@harvest`

**Role.** Runs a harvest cycle per [harvest-cadence.md](harvest-cadence.md).
Identifies project-local artifacts eligible for promotion and produces
the cycle's audit record.

**Inputs.**
- Registry snapshot.
- Previous cycle's audit record (for trend).
- Access to project repos listed in the registry.

**Outputs (tier 3 return).**
- List of promotion candidates with evidence.
- Audit record draft including metric movement vs previous cycle.
- Drift items to surface (projects with stale pins).

**State transitions caused.** Promotion-contract states
(`promoted` / `parked` / `rejected`) for each candidate after reviewer
response.

## `@audit`

**Role.** Read-only verification across the registry. Detects drift,
contract-pin staleness, project-contract violations, and skipped
cycles.

**Inputs.**
- Registry snapshot.
- Current substrate version and published contract tags.
- Audit-record history.

**Outputs (tier 3 return).**
- Drift report: projects behind current substrate or contract pins.
- Violation report: registered projects whose claims are no longer
  true.
- Skipped-cycle report: cadence violations.
- No mutations. `@audit` never writes to project repos or substrate.

**State transitions caused.** None. Audit is observation-only.

## Contracts each meta-agent satisfies

All three meta-agents are themselves callables conforming to
[callable-contract.md](../01-protocols/callable-contract.md). Their
outputs return at tier 3 per [return-schemas.md](../01-protocols/return-schemas.md).

This recursion is deliberate: meta-agents can be dispatched by a
Mode 2 dispatcher inside the coordinator repo just like any other
callable.

## Invocation patterns

- **Manual:** operator triggers from a chat or CLI.
- **Scheduled:** CI cron triggers `@harvest` and `@audit` per cadence.
- **Reactive:** substrate PR opens → CI triggers `@framework-dev` to
  compute impact list on the proposed diff.

All patterns are equivalent from the contract's standpoint. The
contract requires only that the meta-agents exist and produce the
required outputs.

## Outputs and where they land

| Meta-agent | Output destination |
| --- | --- |
| `@framework-dev` | Comment on substrate PR; impact-list artifact under `audit/proposals/` |
| `@harvest` | `audit/<cycle-id>.md` + promotion proposals under `harvest/candidates/` |
| `@audit` | `audit/drift-<timestamp>.md`; never mutates project repos |

Every output is a plain markdown or YAML file under version control.
No meta-agent writes to external systems by default — if a coordinator
adds integrations, they are an extension of the meta-agent, not a
requirement of the contract.
