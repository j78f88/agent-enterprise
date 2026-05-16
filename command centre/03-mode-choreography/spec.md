# Mode 3: Choreography — Spec

## Purpose

Coordinate Mode 1 (and optionally Mode 2) deployments across N projects as a program of works. Lets one evolving framework propagate across a portfolio AND mature patterns harvest back into the substrate.

## Behavior

`delivery-modes/choreography/install.py` scaffolds a fresh **command-centre workspace** at a chosen path. The workspace is the runtime — choreography is not a dropped-in folder, it's a working environment.

### Install flow

1. Prompt for workspace path (default: `../<homebase-name>-control`)
2. Copy `delivery-modes/choreography/template/` to that path
3. Initialize as git repo
4. Add agent-homebase as a git submodule (or vendored copy) at `./agent-homebase/`
5. Generate empty `registry.yml` from `registry.yml.example`
6. Optionally prompt to register first project

### Workspace structure (post-install)

```
<workspace>/
├── README.md
├── registry.yml                 # Project registry
├── agent-homebase/              # Submodule or vendored
├── sync/                        # The sync CLI
│   ├── __init__.py
│   ├── deploy.py
│   ├── diff.py
│   ├── status.py
│   ├── harvest.py
│   └── registry.py              # Schema + IO
├── .github/
│   └── agents/                  # Meta-agents (framework-dev, harvest)
│       ├── framework-dev/SKILL.md
│       ├── harvest/SKILL.md
│       └── audit/SKILL.md
├── reports/                     # sync harvest output lives here
│   └── .gitkeep
└── docs/
    └── operating-model.md       # How to use the workspace
```

### sync CLI

See [sync-cli-spec.md](sync-cli-spec.md) for full command spec. Summary:

| Command | Purpose |
|---------|---------|
| `sync deploy <project>` | Install homebase into a registered project |
| `sync deploy --all` | Install into every registered project |
| `sync diff <project>` | Dry-run; show what would change |
| `sync status` | Show deployed-vs-current homebase version per project |
| `sync harvest <project>` | Diff project against substrate; generate back-port report |
| `sync register <name> --path <path> --profile <profile>` | Add a project to the registry |
| `sync unregister <name>` | Remove a project from the registry |

## Inputs

| Input | Required | Source |
|-------|----------|--------|
| Workspace path | Yes | CLI arg or prompt |
| Homebase reference | Yes | `submodule` (default), `vendor` (copy), or `path` (local) |
| First project to register | No | Prompted; can skip and add later |

## Composition with Modes 1 and 2

A choreography workspace doesn't replace Modes 1/2 — it **drives** them. When `sync deploy <project>` runs, it invokes Mode 1's installer (or Mode 2's, depending on the project's registry entry) under the hood.

Each project in the registry declares which mode it's deployed in:
```yaml
projects:
  verk-web:
    mode: team             # Mode 1
    profile: monorepo-fullstack
  verk-v2:
    mode: orchestration    # Mode 2
    tracker: linear
    workspace: verkv2
```

## Meta-agents

Distinct from the 13 delivery agents (which run inside target projects). Meta-agents run in the choreography workspace itself and improve the framework. See [meta-agents.md](meta-agents.md).

## Non-goals

- Not a CI/CD pipeline (though could be wrapped in one later)
- Not a multi-tenant SaaS (single-operator workspace)
- Not a replacement for project-local agents (those still run in each project)
- Not opinionated about hosting (workspace is a regular git repo; user decides where it lives)
