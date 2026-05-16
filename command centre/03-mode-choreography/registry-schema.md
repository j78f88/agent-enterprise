# Mode 3: registry.yml Schema

The registry is the single source of truth for which projects a choreography workspace coordinates.

## Location

`<workspace-root>/registry.yml`

## Schema

```yaml
# Schema version for forward-compat
schema: 1

# Workspace metadata
workspace:
  name: string                    # Display name for this workspace
  owner: string                   # Operator (your name or team)
  homebase_ref: string            # Git ref of homebase to track (e.g. "main", "v1.2.0")

# Project registry
projects:
  <name>:                         # Short identifier, used in CLI commands
    path: string                  # Local path or git URL
    profile: string               # Profile name (resolves in homebase/profiles/) or path to YAML
    mode: enum                    # "team" | "orchestration"
    
    # Required if mode == orchestration
    tracker: enum                 # "linear" | "github" | "gitlab"
    workspace: string             # Tracker workspace/repo identifier
    active_states: list[string]   # Optional override of dispatch trigger states
    
    # Deployment state (managed by sync, do not edit by hand)
    deployed_hash: string|null    # Homebase git SHA of last successful deploy
    deployed_at: timestamp|null   # ISO 8601 of last successful deploy
    deployed_by: string|null      # Operator who last deployed
    
    # Optional project-local overlays
    custom_instructions: list[string]   # Paths (relative to project) to project-specific instructions
    custom_agents: list[string]         # Paths to project-specific agents
    
    # Optional metadata
    notes: string                 # Freeform notes
    tags: list[string]            # For filtering: e.g. ["production", "verk-portfolio"]
```

## Example

```yaml
schema: 1

workspace:
  name: Joshua's Portfolio
  owner: joshua
  homebase_ref: main

projects:
  verk-web:
    path: D:\VS\Verk Web
    profile: monorepo-fullstack
    mode: team
    deployed_hash: null            # not yet deployed
    custom_instructions:
      - .github/instructions/template-validation.md
      - .github/instructions/release-governance.md
    custom_agents:
      - .github/agents/template-auditor/SKILL.md
      - .github/agents/delivery-lead/SKILL.md
    tags: [production, verk]
    notes: "Sprint 90+; mature. Audit before deploy via sync harvest."

  verk-v2:
    path: D:\VS\verk-v2
    profile: monorepo-fullstack
    mode: orchestration
    tracker: linear
    workspace: verkv2
    active_states: [Todo, In Progress]
    deployed_hash: null
    tags: [active-development, verk]
    notes: "Skeleton; first to onboard via Mode 3."

  diy-project-helper:
    path: D:\VS\DIY project\diy-project-helper
    profile: react-web-app
    mode: team
    deployed_hash: null
    tags: [legacy, verk]
    notes: "Original Verk; consider archiving after Verk Web migration."
```

## Validation Rules

| Rule | Error |
|------|-------|
| `schema` is `1` | Unsupported schema version |
| `projects.<name>` keys are unique | Duplicate project name |
| `<name>` matches `^[a-z0-9-]+$` | Invalid project name |
| `path` exists OR is a valid git URL | Project path unreachable |
| `profile` resolves (in homebase/profiles or as path) | Profile not found |
| `mode` is `team` or `orchestration` | Invalid mode |
| If `mode == orchestration`, `tracker` and `workspace` required | Missing required fields |
| `tracker` is supported value | Unsupported tracker |
| `custom_instructions` / `custom_agents` paths exist (relative to project) | Custom file missing (warn only) |

## Field Lifecycle

| Field | Set by | Updated by |
|-------|--------|-----------|
| `path`, `profile`, `mode`, `tracker`, `workspace`, `custom_*`, `notes`, `tags` | Operator (via `sync register` or hand edit) | Operator |
| `deployed_hash`, `deployed_at`, `deployed_by` | `sync deploy` | `sync deploy` |
| `active_states` | Operator (optional) | Operator |

## Migration

Schema version `1` is the initial release. Future versions document migrations in this file.
