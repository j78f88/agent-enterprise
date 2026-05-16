# Mode 1: Team — Spec

## Purpose

Drop a structured 13-agent delivery team into a single project repo. Human-invoked. No tracker integration. The simplest deployment of agent-homebase.

## Behavior

`delivery-modes/team/install.py` is a thin wrapper around the existing `init.py` flow. It:

1. Reads a project profile (path to `.agent-config/profile.yml` or one of the bundled `profiles/*.config.yml`)
2. Runs `init.py` to substitute tokens, populating `resolved/`
3. Copies resolved output to the target project's `.github/agents/` and `.github/instructions/`
4. Optionally seeds starter planning files (`docs/planning/`, `SPRINTS.md`, etc.) from `starters/` if not already present
5. Writes a small marker file (`.github/agents/.homebase-mode`) recording the mode and homebase version installed

## Inputs

| Input | Required | Source |
|-------|----------|--------|
| Target project path | Yes | CLI arg or prompt |
| Project profile | Yes | Path to `.yml` file or selection from bundled profiles |
| Editor target | No, default `vscode` | `vscode` / `claude` / `both` |
| Seed starters | No, default `true` | Whether to copy `starters/` if missing |

## Outputs (in target project)

```
<target>/
├── .github/
│   ├── agents/
│   │   ├── .homebase-mode             # NEW — { mode: "team", version: "<sha>" }
│   │   ├── planner/SKILL.md
│   │   ├── pm/SKILL.md
│   │   └── ... (13 total)
│   └── instructions/
│       └── ... (24 total)
├── docs/
│   └── planning/
│       ├── BACKLOG_LEDGER.md          # Seeded from starters if missing
│       ├── BUG_BACKLOG.md
│       └── HANDOFF_REJECTIONS.md
├── SPRINTS.md                          # Seeded from starters if missing
└── docs/NON_GOALS.md                   # Seeded from starters if missing
```

## Idempotency

- Re-running `install.py` against the same project must be safe
- Existing planning files are NEVER overwritten (only created if missing)
- Resolved agents/instructions are always overwritten (they're generated)
- The marker file's `version` field updates on each run

## Non-goals

- No tracker setup (that's Mode 2)
- No multi-project coordination (that's Mode 3)
- No back-port / harvest tooling (that's Mode 3)
- No autonomous dispatch (Mode 1 agents are invoked by a human)

## Migration from current state

The current flow is:
```bash
python init.py --config profiles/react-web-app.config.yml
cp -r resolved/skills/* .github/agents/
cp -r resolved/instructions/* .github/instructions/
cp starters/* docs/planning/
```

Mode 1's `install.py` collapses this into:
```bash
python delivery-modes/team/install.py --target ../my-project --profile profiles/react-web-app.config.yml
```

Existing users continue to work unchanged — `init.py` stays at the root and is still callable directly.
