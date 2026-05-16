# Mode 3: Meta-Agents

Meta-agents run **inside the choreography workspace** to improve the framework itself. They are distinct from the 13 delivery agents, which run inside target projects.

## Why separate?

Delivery agents (`@planner`, `@qa`, `@reviewer`, etc.) operate on application code. Meta-agents operate on agent-homebase content (skills, instructions, profiles). Mixing concerns would pollute both.

## Initial Meta-Agent Roster

### `@framework-dev`

**Role:** Improves homebase substrate (skills, instructions, profiles) based on operator direction.

**Inputs:**
- A specific improvement target (skill name, instruction file, etc.)
- Optional: harvest report identifying the gap

**Outputs:**
- Edits to homebase files (skills, instructions, profiles)
- Updated tests in `tests/`
- Commit-ready changes with rationale

**When to invoke:**
- "Improve `@reviewer` skill to handle TypeScript-specific patterns"
- "Add a new instruction for monorepo composition rules"
- "Refactor `planning-compliance.instructions.md` for clarity"

### `@harvest`

**Role:** Extracts mature patterns from a deployed project, diffs against substrate, and proposes back-port candidates.

**Inputs:**
- A project name from the registry

**Outputs:**
- Harvest report at `reports/harvest-<name>-<date>.md`
- For each candidate, classification: back-port to substrate / promote to extensions / leave project-local
- Suggested PR diff against homebase substrate

**When to invoke:**
- "Harvest verk-web — find what should flow back to homebase"
- After major sprints in any registered project
- Before declaring substrate stable for a release

**Powered by:** wraps `sync harvest` and adds reasoning over the raw diff.

### `@audit`

**Role:** Reviews proposed substrate changes for quality, consistency, and breaking-change risk.

**Inputs:**
- A diff or PR against homebase substrate

**Outputs:**
- Audit report: lint issues, schema violations, downstream impact analysis (which registered projects would be affected and how)
- Pass/fail recommendation

**When to invoke:**
- Before merging any change to homebase from `@framework-dev` or harvest
- Periodic: weekly audit of all substrate

## Optional Future Meta-Agents

| Agent | Role |
|-------|------|
| `@release` | Cuts a homebase semver release; tags, generates changelog from commits |
| `@migrate` | Generates migration guides when substrate has breaking changes |
| `@telemetry` | Aggregates usage telemetry from registered projects (if/when telemetry exists) |

## Location

```
<workspace>/.github/agents/
├── framework-dev/
│   └── SKILL.md
├── harvest/
│   └── SKILL.md
└── audit/
    └── SKILL.md
```

These are vendored from `delivery-modes/choreography/template/agents/` at workspace install time.

## Boundaries

Meta-agents **must not**:
- Edit registered projects directly (that's what `sync deploy` is for)
- Edit `registry.yml` (operator's responsibility, or via `sync register/unregister`)
- Edit `.git/` of any repo
- Push to remotes without operator confirmation

Meta-agents **may**:
- Edit homebase substrate (skills, instructions, profiles)
- Read any registered project (read-only)
- Write reports to `<workspace>/reports/`
- Propose changes (PRs, diffs) for operator review
