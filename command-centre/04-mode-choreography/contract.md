# Mode 3 — Choreography contract

> **Contract tag:** `mode-3-contract-v1`.
>
> Defines what a program-of-works coordinator must do to satisfy Mode 3.
> Coordinates across multiple projects, including mixed fleets where
> some projects run Mode 1 only and others run Mode 1 + Mode 2.

## Purpose

Mode 3 is for organisations running multiple projects that share
substrate. It provides the program-of-works view: which projects exist,
what versions they pin, when substrate changes affect them, and how
learnings from one project flow back to substrate.

Mode 3 does not run inside projects. It runs *above* them.

## Coordinator responsibilities

A conforming coordinator MUST:

1. **Maintain a registry.** Per
   [registry-schema.md](registry-schema.md). Single source of truth
   for the program of works.
2. **Honour project contracts.** Treat every registry entry as a
   project conforming to [project-contract.md](../01-protocols/project-contract.md).
3. **Detect drift.** For each project, identify when its
   `substrate_version` or `contract_pins` are behind current.
4. **Surface impact.** When a substrate change occurs (e.g., contract
   tag bump), report which projects are affected.
5. **Run harvest cycles.** On the declared cadence
   ([harvest-cadence.md](harvest-cadence.md)), execute the harvest
   workflow and produce an audit record.
6. **Apply the promotion contract.** Every promotion of a project-local
   artifact into substrate follows
   [`05-promotion-contract.md`](../05-promotion-contract.md).
7. **Provide meta-agents.** Minimum required:
   [`@framework-dev`, `@harvest`, `@audit`](meta-agents.md). Coordinator
   may add more.

## Registry shape

The registry is a single YAML file per coordinator instance. Schema
and validation rules in [registry-schema.md](registry-schema.md).

The coordinator MUST NOT split the registry across multiple files —
this defeats the single-source-of-truth guarantee.

## Mixed-fleet support

A program of works MAY contain projects at different `mode_level`
values (`team` and `orchestration`). The coordinator MUST handle this
by construction:

- Meta-agents adapt behaviour based on `mode_level` per project.
- Harvest cycles consider what each project actually runs, not a
  uniform assumption.
- Drift detection works for any `mode_level`.

See [mixed-fleet-example.md](mixed-fleet-example.md) for a worked
scenario.

## Harvest workflow

Each harvest cycle:

1. **Inputs:** registry snapshot, last cycle's audit record, list of
   project repos accessible.
2. **Scan:** identify project-local artifacts that might be promotable
   per the promotion contract.
3. **Evaluate:** apply promotion-contract eligibility criteria.
4. **Propose:** generate a list of promotion candidates with evidence.
5. **Review:** reviewer (per promotion contract) accepts/parks/rejects
   each candidate.
6. **Apply:** accepted candidates are merged into substrate; rejected
   are logged with reasons; parked are deferred to a later cycle.
7. **Audit:** record the cycle with date, owner, inputs, outputs,
   metric movement, decisions.

Detailed cadence semantics in [harvest-cadence.md](harvest-cadence.md).

## Conformance checklist

A coordinator claims `mode-3-contract-v1` conformance if and only if:

- [ ] Maintains a registry per the registry schema.
- [ ] Validates every registry entry against the project contract.
- [ ] Detects substrate-version and contract-pin drift per project.
- [ ] Surfaces impact of substrate changes to registered projects.
- [ ] Implements at least the three required meta-agents.
- [ ] Runs harvest on a declared cadence with required-metric movement.
- [ ] Applies the promotion contract on every promotion.
- [ ] Handles mixed-fleet registries by construction.
- [ ] Includes a worked example of coordinating a non-enterprise project
      (see [mixed-fleet-example.md](mixed-fleet-example.md)).

## Independence guarantees

- Mode 3 depends only on [`01-protocols/`](../01-protocols/).
- Mode 3 does NOT require any project to run Mode 2. A program of works
  entirely composed of `mode_level: team` projects is valid.
- Mode 3 does NOT require projects to use agent-enterprise substrate.
  Projects may declare custom substrate per the project contract.
- Mode 3 coordinator reference impls do not import from Mode 1 or
  Mode 2 source trees.

## Versioning

Breaking changes bump `mode-3-contract-v1` → `mode-3-contract-v2`.
Examples of breaking: removing a required coordinator responsibility,
changing the harvest workflow steps, changing required meta-agent set.

N-1 coexistence per [ADR 0003](../decisions/0003-unified-semver-plus-contract-tags.md).
