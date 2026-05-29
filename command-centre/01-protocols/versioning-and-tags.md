# Versioning and tags

> **Decision:** [ADR 0003](../decisions/0003-unified-semver-plus-contract-tags.md).
>
> Three independent version streams: repo semver + protocol version +
> per-mode contract tags.

## Mechanism

### Repo semver

`agent-enterprise@MAJOR.MINOR.PATCH` (plus optional pre-release suffix),
applied as a git tag (e.g., `v2.3.0`).

- **MAJOR** — restructure or large policy change.
- **MINOR** — new substrate content, new reference impl, new skill,
  new instruction.
- **PATCH** — bug fix, typo, small clarification.

### Protocol tag

`protocol-vN`. Bumps only when any file under
[`01-protocols/`](../01-protocols/) changes in a breaking way:
removing a required field, changing semantics of an existing field,
removing a return tier, changing an enum's meaning. Non-breaking
additions (new optional fields, new tiers, new enum values that don't
change existing meanings) do not bump.

### Per-mode contract tags

- `mode-1-contract-vN` — bumps on breaking changes to
  [`02-mode-team/contract.md`](../02-mode-team/contract.md) or any
  conformance-affecting file under `02-mode-team/`.
- `mode-2-contract-vN` — bumps on breaking changes to
  [`03-mode-orchestration/contract.md`](../03-mode-orchestration/contract.md)
  or the [callable contract](callable-contract.md) (the latter also
  bumps `protocol-vN`).
- `mode-3-contract-vN` — bumps on breaking changes to
  [`04-mode-choreography/contract.md`](../04-mode-choreography/contract.md),
  [registry-schema.md](../04-mode-choreography/registry-schema.md),
  the [project contract](project-contract.md), or
  [`05-promotion-contract.md`](../05-promotion-contract.md).

### N-1 coexistence

When any contract tag bumps, substrate MUST continue to honour the
previous version for at least one minor repo release cycle. Schemas
under [`schemas/`](../../schemas/) keep both versions; `init.py`
builds against either, selected by consumer pin; a deprecation notice
goes in at bump time and removal happens one cycle later.

Rationale: rainbow deployments — see
[design-history](../00-overview/design-history.md).

### Release notes

Every release MUST declare the repo bump, whether `protocol-vN`
bumped, whether any `mode-X-contract-vN` bumped, and any deprecation
or removal notices. A release that bumps any contract tag MUST
include a migration note.

## Consumer pin strategies

- **Whole framework, fast updates:** `agent-enterprise@^2.0.0`.
- **Whole framework, conservative:** `agent-enterprise@~2.3.0`.
- **Single-mode pin:** `protocol-v1 + mode-N-contract-v1`, tracking
  `agent-enterprise@2.*.*` for fixes within those contract versions.
  Other modes can bump under you without breaking conformance.
