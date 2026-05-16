# Registry schema

> **Contract tag:** part of `mode-3-contract-v1`.
>
> Schema for the choreography registry file. Each entry describes one
> project in the program of works.

## File location and format

- One file per coordinator instance.
- Default location: `<coordinator-repo>/registry.yml`.
- Format: YAML 1.2.
- Canonical JSON Schema lives at
  [`schemas/registry-v1.schema.json`](../../schemas/) (added when this
  contract ships).

A coordinator MUST NOT split the registry across multiple files. This
is the single source of truth.

## Required fields per project

Each entry under `projects[]`:

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Unique within the registry. `^[a-z0-9][a-z0-9-]*$`. |
| `name` | string | Human-readable. |
| `repo` | string | URI. `https://`, `ssh://`, `git@`, or `local:./path`. |
| `mode_level` | enum | `team` \| `orchestration`. See below. |
| `substrate_version` | string | Semver, or `"custom"` if not homebase. |
| `contract_pins` | array | Contract tags this project claims to conform to. |

## Optional fields per project

| Field | Type | Notes |
| --- | --- | --- |
| `description` | string | One-sentence summary. |
| `owner` | string | Role or identity responsible. |
| `tags` | array | Free-form labels. |
| `last_harvested_at` | ISO date | Set by `@harvest`. Read by drift detection. |
| `custom_substrate` | object | If `substrate_version` is `"custom"`, declare provider + version. |
| `dispatcher` | object | If `mode_level` is `orchestration`, declare impl. See below. |
| `notes` | string | Free-form context for human readers. |

## `mode_level` enum

| Value | Meaning |
| --- | --- |
| `team` | Project runs Mode 1 only (substrate + interactive use). |
| `orchestration` | Project runs Mode 1 + Mode 2 (dispatcher present). |

No `choreography` value: a project does not run Mode 3, it is
coordinated by Mode 3.

## Substrate version pin

- For homebase substrate: semver matching a published
  `agent-homebase@N.M.P`.
- For custom substrate: literal string `"custom"`, with a
  `custom_substrate` block declaring `provider` and `provider_version`.

Drift detection uses this field to flag projects behind the current
substrate version (or behind their declared custom provider's current
version, if the coordinator can resolve that).

## Contract tag pins

`contract_pins` is denormalised on purpose. Each project lists every
contract tag it relies on so the coordinator can answer impact
questions without opening any project repo.

Minimum required pins:
- A `mode-1-contract-vN` if `mode_level: team`.
- A `mode-1-contract-vN` + `mode-2-contract-vN` if `mode_level: orchestration`.
- A `protocol-vN` always.
- Any other contract the project relies on (e.g., `callable-contract-vN`).

## Dispatcher impl declaration (Mode 2 projects)

For `mode_level: orchestration` projects, the `dispatcher` block:

```yaml
dispatcher:
  impl: "my-org-dispatcher"
  impl_version: "3.1.0"
  queue_source: "github-issues"
```

The coordinator does not validate the dispatcher impl itself — it
trusts the project's claim. Verification is the project's
responsibility.

## Validation rules

1. `id` must be unique within the registry.
2. `mode_level` must be one of the enum values.
3. If `substrate_version` is `"custom"`, `custom_substrate` must be
   present.
4. If `mode_level` is `orchestration`, `dispatcher` must be present.
5. `contract_pins` must include the minimum required pins for the
   declared `mode_level`.
6. Every contract tag in `contract_pins` must be a known tag (the
   coordinator maintains a list of valid tags per substrate version).

Validation failure aborts coordinator operations on the affected
entry until corrected.

## Versioning of the schema itself

The registry schema is versioned with the Mode 3 contract
(`mode-3-contract-vN`). Breaking changes to required fields bump the
Mode 3 contract tag. N-1 coexistence per
[ADR 0003](../decisions/0003-unified-semver-plus-contract-tags.md).
