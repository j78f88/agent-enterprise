# Mode 3 — Mixed-fleet example

> A worked example proving Mode 3 coordinates a program containing
> both `mode_level: team` and `mode_level: orchestration` projects,
> with one project on custom (non-enterprise) substrate.

## Scenario

A platform organisation runs three internal product teams. Each team
owns one project. The program-of-works coordinator wants visibility,
drift control, and shared learnings across all three.

- **Project Alpha:** uses agent-enterprise substrate; runs Mode 1 only
  (interactive use by a small team, no dispatcher).
- **Project Bravo:** uses agent-enterprise substrate; runs Mode 1 + Mode 2
  (issue-driven dispatcher operating on a queue).
- **Project Gamma:** uses a custom internal substrate that conforms to
  Mode 1 contract; runs Mode 1 only.

All three are valid. None of the three knows or cares about the
others' configuration.

## Registry contents

```yaml
projects:
  - id: alpha
    name: "Project Alpha"
    repo: "https://internal.example/alpha"
    mode_level: team
    substrate_version: "2.3.0"
    contract_pins: [protocol-v1, mode-1-contract-v1]
    owner: "@team-alpha-lead"

  - id: bravo
    name: "Project Bravo"
    repo: "https://internal.example/bravo"
    mode_level: orchestration
    substrate_version: "2.3.0"
    contract_pins:
      - protocol-v1
      - mode-1-contract-v1
      - mode-2-contract-v1
      - callable-contract-v1
    dispatcher:
      impl: "my-org-dispatcher"
      impl_version: "3.1.0"
      queue_source: "github-issues"
    owner: "@team-bravo-lead"

  - id: gamma
    name: "Project Gamma"
    repo: "https://internal.example/gamma"
    mode_level: team
    substrate_version: "custom"
    custom_substrate:
      provider: "my-org-internal-skills"
      provider_version: "4.1.0"
    contract_pins: [protocol-v1, mode-1-contract-v1]
    owner: "@team-gamma-lead"
```

## Per-project mode_level

| Project | mode_level | Substrate | Dispatcher? |
| --- | --- | --- | --- |
| Alpha | team | enterprise 2.3.0 | No |
| Bravo | orchestration | enterprise 2.3.0 | Yes |
| Gamma | team | custom 4.1.0 | No |

The coordinator handles all three uniformly through the project
contract. It does not need separate logic for enterprise vs custom
substrate, nor for `team` vs `orchestration` projects — the meta-agents
branch on `mode_level` internally.

## How meta-agents adapt behaviour per project

**`@audit`:**
- All three: check `substrate_version` against current. Alpha and Bravo
  share enterprise — same current-version reference. Gamma uses custom —
  the coordinator resolves `my-org-internal-skills` current version
  separately (or skips, with a note in the audit record).
- Bravo only: also check `dispatcher.impl_version` for drift if the
  coordinator tracks dispatcher releases.

**`@framework-dev`:**
- When proposing a enterprise substrate change: impact list includes
  Alpha and Bravo, excludes Gamma.
- When proposing a Mode 2 contract change: impact list includes Bravo
  only.
- When proposing a protocol change: impact list includes all three.

**`@harvest`:**
- Scans all three project repos for promotable artifacts.
- For Gamma (custom substrate), promotions go to `my-org-internal-skills`
  not agent-enterprise — the coordinator may decline to propose them, or
  may route them to a sibling harvest workflow if one exists.
- Audit record covers all three uniformly.

## Harvest cycle across mixed fleet

One `harvest-cadence.yml` covers all three. Example cycle output:

```markdown
# Audit cycle 2026-05-15

Cadence: monthly. Owner: @platform-lead.
Metric (candidates_per_cycle): 3 (floor 1, PASS).

## Registry summary
- alpha: substrate 2.3.0 (current). No drift.
- bravo: substrate 2.3.0 (current). Dispatcher 3.1.0 (current). No drift.
- gamma: custom 4.1.0 (current per provider). No drift.

## Promotion candidates
- alpha/skills/onboarding-tweaks/   → PARKED (insufficient evidence)
- bravo/instructions/queue-naming/  → PROMOTED to substrate
- gamma/skills/internal-auth/       → ROUTED to my-org-internal-skills harvest

## Skipped cycles since last
None.
```

The registry, the meta-agents, and the cadence contract are unchanged
by fleet composition. Adding a fourth project of any `mode_level` and
substrate type follows the same install steps and does not require
coordinator changes.
