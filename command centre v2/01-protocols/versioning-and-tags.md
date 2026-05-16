# Versioning and tags

> **Decision:** [ADR 0003](../decisions/0003-unified-semver-plus-contract-tags.md).
>
> Three independent version streams: repo semver + protocol version +
> per-mode contract tags. This file is the operational reference.

## Repo semver

Format: `agent-homebase@MAJOR.MINOR.PATCH` plus pre-release suffix.

- **MAJOR** — reserved for restructure or large policy change.
- **MINOR** — new substrate content, new reference impl, new skill, new
  instruction.
- **PATCH** — bug fix, typo, small clarification.

Applied as a git tag at the repo root: `v2.3.0`.

Used by consumers who want "all of agent-homebase at a known version."

## Protocol version tag

Format: `protocol-vN`.

Applied as a separate git tag (lightweight, points at the same commit
as the corresponding repo tag).

Bumps only when **any** file under
[`01-protocols/`](../01-protocols/) changes in a breaking way:

- Removing a required field from a contract.
- Changing semantics of an existing field.
- Removing a return tier.
- Changing the meaning of a `mode_level` enum value.

Non-breaking additions (new optional fields, new tiers, new enum
values that don't change existing meanings) do not bump.

## Mode 1 contract tag

Format: `mode-1-contract-vN`.

Bumps when [`02-mode-team/contract.md`](../02-mode-team/contract.md) or
any conformance-affecting file under `02-mode-team/` changes in a
breaking way.

Used by consumers who only want Mode 1 — they pin this tag and the
protocol tag, and track `agent-homebase@N.*.*` within them.

## Mode 2 contract tag

Format: `mode-2-contract-vN`.

Bumps on breaking change to
[`03-mode-orchestration/contract.md`](../03-mode-orchestration/contract.md)
or the [callable contract](callable-contract.md) (the latter also
bumps `protocol-vN`).

## Mode 3 contract tag

Format: `mode-3-contract-vN`.

Bumps on breaking change to
[`04-mode-choreography/contract.md`](../04-mode-choreography/contract.md),
[registry-schema.md](../04-mode-choreography/registry-schema.md), the
[project contract](project-contract.md), or
[`05-promotion-contract.md`](../05-promotion-contract.md).

## N-1 coexistence requirement

When any contract tag bumps, substrate MUST continue to honour the
previous version for at least one minor repo release cycle.

Mechanism:

- Schemas under [`schemas/`](../../schemas/) keep the previous version
  alongside the new one (e.g., `mode-2-contract-v1.schema.json` and
  `mode-2-contract-v2.schema.json` both present).
- Build pipeline (`init.py`) supports building artifacts against
  either version, selected by consumer pin.
- Deprecation notice is added to the previous version's docs at bump
  time. Removal happens one cycle later.

Rationale: Anthropic Multi-Agent Research — rainbow deployments. See
[design-history §4](../00-overview/design-history.md#anthropic-how-we-built-our-multi-agent-research-system-jun-2025).

## Consumer pin strategies

### "I want the whole framework, fast updates"

Pin: `agent-homebase@^2.0.0`. Get all minor and patch updates.

### "I want the whole framework, conservative"

Pin: `agent-homebase@~2.3.0`. Only patch updates.

### "I only use Mode 2"

Pin: `protocol-v1 + mode-2-contract-v1`. Track
`agent-homebase@2.*.*` for fixes within those contract versions.

### "I only use Mode 3 and coordinate Mode 1 projects"

Pin: `protocol-v1 + mode-1-contract-v1 + mode-3-contract-v1`. Mode 2
can bump under you without breaking your coordination.

## Release process

For each release the release notes MUST declare:

1. Repo semver bump.
2. Whether `protocol-vN` bumped (and to what).
3. Whether any `mode-X-contract-vN` bumped (and to what).
4. Deprecation notices for any contracts now in N-1 grace period.
5. Removal notices for any contracts whose grace period has ended.

A release that bumps any contract tag MUST include a migration note.
