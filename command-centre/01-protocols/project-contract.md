# Project contract

> **Contract tag:** `project-contract-v1`. Part of `protocol-v1`.
>
> Defines what Mode 3 coordinates against. A "project" is any unit of
> work registered in a program-of-works registry. Substrate- and
> runtime-agnostic.

## Purpose

Mode 3 (choreography) coordinates across multiple projects. It needs a
stable way to describe what each project is and what it expects, without
assuming uniformity in substrate, dispatcher, or implementation.

## Required fields

Every registry entry declares:

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique project identifier within the registry. |
| `name` | string | Human-readable name. |
| `repo` | string | URI of the project repository. May be `local:./path` for monorepo sub-projects. |
| `mode_level` | enum | One of `team`, `orchestration` (see below). |
| `substrate_version` | string | Pinned agent-enterprise semver. |
| `contract_pins` | array | List of contract tags this project relies on. |

Optional fields are listed in [registry-schema.md](../04-mode-choreography/registry-schema.md).

## Mode level declaration

`mode_level` declares which delivery modes this project consumes:

| Value | Meaning |
| --- | --- |
| `team` | Project runs Mode 1 only (substrate + interactive use). |
| `orchestration` | Project runs Mode 1 + Mode 2 (dispatcher present). |

There is deliberately no `choreography` mode level — a project does not
"run" Mode 3, it is *coordinated by* Mode 3.

Mixed fleets are valid by construction: a single registry may contain
`team` and `orchestration` projects in any combination. Meta-agents
([meta-agents.md](../04-mode-choreography/meta-agents.md)) adapt
behaviour based on this field.

## Substrate version pin

`substrate_version` is the agent-enterprise semver that this project was
last verified against. Mode 3 coordinators use this to:

- Detect drift between project pin and current substrate.
- Decide which contract version's expectations apply.
- Group projects by version for batched upgrade workflows.

## Contract tag pins

`contract_pins` lists every contract tag the project relies on:

```yaml
contract_pins:
  - protocol-v1
  - mode-1-contract-v1
  - callable-contract-v1
```

This is denormalised on purpose. A coordinator scanning the registry
can answer "who breaks if we bump `mode-1-contract-v1`?" without
opening any project.

## Registry entry shape

Full schema and required vs. optional fields:
[registry-schema.md](../04-mode-choreography/registry-schema.md).

Minimal valid entry:

```yaml
projects:
  - id: project-a
    name: "Project A"
    repo: "https://github.com/example/project-a"
    mode_level: team
    substrate_version: "2.3.0"
    contract_pins: [protocol-v1, mode-1-contract-v1]
```

## Non-enterprise project example

A project does not have to use agent-enterprise substrate to appear in a
registry. It must, however, declare the contracts it conforms to:

```yaml
projects:
  - id: legacy-service
    name: "Legacy Service"
    repo: "https://internal.example/legacy"
    mode_level: team
    substrate_version: "custom"
    custom_substrate:
      provider: "my-org-internal-skills"
      provider_version: "4.1.0"
    contract_pins: [protocol-v1, mode-1-contract-v1]
```

The project asserts conformance to `mode-1-contract-v1` even though
its substrate is not enterprise. The coordinator trusts that assertion
and verifies it at harvest time.

## Versioning

Breaking changes bump `project-contract-v1` → `project-contract-v2`.
N-1 coexistence required per [ADR 0003](../decisions/0003-unified-semver-plus-contract-tags.md).
