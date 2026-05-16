# Mode 2: Orchestration — Install Contract

Formal contract that `delivery-modes/orchestration/install.py` must satisfy.

## CLI

```
install.py --target <path> --profile <path> --tracker <type> --workspace <id>
           [--editor vscode|claude|both]
           [--active-states <list>]
           [--hooks-path <path>]
           [--config-path <path>]
           [--no-starters] [--dry-run]
```

| Flag | Required | Description |
|------|----------|-------------|
| `--target` | Yes | Target project repo path |
| `--profile` | Yes | Project profile YAML |
| `--tracker` | Yes | `linear` / `github` / `gitlab` |
| `--workspace` | Yes | Tracker workspace/repo identifier |
| `--active-states` | No | Comma-separated tracker states that trigger dispatch. Default: `Todo,In Progress` |
| `--hooks-path` | No | Where to write hooks. Default `<target>/hooks/` |
| `--config-path` | No | Where to write orchestration config. Default `<target>/.orchestration/` |

(Inherits Mode 1 flags.)

## Preconditions

All Mode 1 preconditions, plus:

| Check | Failure mode |
|-------|--------------|
| `delivery-modes/orchestration/` exists in homebase | Exit 4 |
| Tracker type is supported | Exit 6, list valid types |
| Hooks path is writable | Exit 5 |

## Postconditions

All Mode 1 postconditions, plus:

| Guarantee | Verified by |
|-----------|-------------|
| `@dispatcher` and `@verifier` agents exist in `<target>/.github/agents/` | File check |
| All dispatch + tracker-adapter instructions exist in `<target>/.github/instructions/` | File check (count must be ≥ 14) |
| Marker file `.homebase-mode` shows `mode: orchestration` | YAML parse |
| `<hooks-path>/afterCreate.sh` and `onComplete.sh` exist and are executable | File + perms check |
| `<config-path>/WORKFLOW.md` and `hatice.env.example` exist | File check |
| `WORKFLOW.md` has tracker type and workspace substituted from inputs | Grep for `{{tracker}}` etc. (none should remain) |

## Exit Codes

Same as Mode 1, plus:

| Code | Meaning |
|------|---------|
| 6 | Unsupported tracker type |

## Output Format

```
Mode 2 (Orchestration) install complete
  Target:    /path/to/project
  Profile:   profiles/monorepo-fullstack.config.yml
  Tracker:   linear (workspace: verkv2)
  Version:   homebase@abc1234
  
  Mode 1 substrate:    13 skills, 24 instructions
  Orchestration:       2 agents (dispatcher, verifier), 14 instructions
  Hooks:               ./hooks/afterCreate.sh, ./hooks/onComplete.sh
  Config:              ./.orchestration/WORKFLOW.md, ./.orchestration/hatice.env.example
  
  Next steps:
    1. Copy hatice.env.example to hatice.env, fill in tracker credentials
    2. Point hatice at ./.orchestration/WORKFLOW.md
    3. Run hatice; @dispatcher will pick up active issues
```

## Test Plan

| Test | Expected |
|------|----------|
| Install on Mode-1-already-installed target | Upgrades in place; marker becomes `orchestration` |
| Install on fresh target | Mode 1 + Mode 2 assets both present |
| Install with unsupported tracker | Exit 6 |
| Install with `--dry-run` | No files modified |
| Re-install (idempotency) | Same output; marker version updates if homebase moved |
| End-to-end: install + run dummy Linear issue | `@dispatcher` classifies, dispatches, `@verifier` reports |
