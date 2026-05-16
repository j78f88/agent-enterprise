# Frontmatter spec

> **Contract tag:** `frontmatter-v1`. Part of `protocol-v1`.
>
> Required and optional YAML frontmatter fields for callables, skill
> sources, instructions, agents, and registry entries.

## Required fields

Every substrate file MUST declare:

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Globally unique within substrate. Stable. |
| `kind` | enum | `skill` \| `instruction` \| `agent` \| `profile` \| `callable` \| `policy` \| `schema` |
| `version` | semver | File-level version. Independent of repo semver. |
| `applies_to` | string or array | Path glob(s) where this file is active. Use `"**"` for global. |

## Optional fields

| Field | Type | Notes |
| --- | --- | --- |
| `description` | string | One-sentence purpose. |
| `tags` | array | Free-form labels for search/filter. |
| `replaces` | string | `id` of a deprecated file this supersedes. |
| `depends_on` | array | List of other file `id`s required to be present. |
| `runtime` | array | Platforms this file is verified on (`copilot`, `claude-code`, `cursor`, `codex`). |
| `owner` | string | Role or identity responsible for upkeep. |
| `last_reviewed` | ISO date | Used by `@audit` to detect staleness. |

## Mode-specific fields

### Callable (Mode 2 target)

In addition to required fields, a callable adds:

| Field | Type | Notes |
| --- | --- | --- |
| `inputs` | JSON schema | See [callable-contract.md](callable-contract.md). |
| `outputs` | array | See callable contract. |
| `verifier` | string \| null | See callable contract. |
| `runtime_hints` | object | Optional. |

### Registry entry (Mode 3)

Registry entries use their own schema; see
[registry-schema.md](../04-mode-choreography/registry-schema.md).
Frontmatter rules do not apply because the registry is a single file
with multiple entries, not one file per project.

## Path-scoped frontmatter rules

`applies_to` controls where a file is active. Rules:

- A file with `applies_to: "**"` is global. Use sparingly.
- A file with `applies_to: "src/api/**"` is only loaded when the active
  context is under `src/api/`.
- An array applies if any glob matches.
- More specific paths override less specific ones when files conflict
  (longest-glob-wins semantics).

The substrate build (`init.py`) enforces these rules and flags
conflicts.

## Validation

Frontmatter is validated at build time by `init.py` against the
relevant JSON Schema in [`schemas/`](../../schemas/). Validation
failure is a build error.

A file missing required frontmatter is rejected. A file with unknown
fields under a strict-mode profile is rejected; under lax mode
(default), unknown fields are preserved and warned about.

## Versioning

This spec is `frontmatter-v1`. Adding new optional fields is non-
breaking. Removing a field or changing semantics of an existing field
is breaking and bumps to `frontmatter-v2` with N-1 coexistence.
