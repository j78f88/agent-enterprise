# Architecture

How the three modes sit on top of shared substrate inside agent-homebase.

## Repo Layout (Target State, post-restructure)

```
agent-homebase/
├── skills/                         # Shared substrate: 13 agent skills
├── agents/                         # Shared substrate: VS Code agent wrappers
├── instructions/
│   ├── generic/                    # Shared substrate: 9 generic instructions
│   └── configurable/               # Shared substrate: 15 configurable instructions
├── profiles/                       # Shared substrate: 3 base profiles
├── starters/                       # Shared substrate: bootstrap templates
├── schemas/                        # Shared substrate: subagent return schemas
├── policies/                       # Shared substrate: Rego policies
├── init.py                         # Shared substrate: token substitution engine
├── resolved/                       # Shared substrate: generated output
│
├── delivery-modes/                 # NEW — three deployment modes
│   ├── README.md                   # Selection guide
│   ├── team/                       # Mode 1
│   │   ├── install.py
│   │   ├── README.md
│   │   └── docs/
│   ├── orchestration/              # Mode 2 (absorbed from agent-orchestration repo)
│   │   ├── install.py
│   │   ├── agents/                 # @dispatcher, @verifier
│   │   ├── instructions/           # dispatch-classification, tracker-adapter-*, etc.
│   │   ├── hooks/                  # afterCreate.sh, onComplete.sh
│   │   ├── config/                 # hatice.env.example, WORKFLOW.md
│   │   └── docs/                   # ARCHITECTURE.md, RUNBOOK.md
│   └── choreography/               # Mode 3 (NEW)
│       ├── install.py              # Scaffolds a workspace
│       ├── template/               # Workspace template
│       │   ├── registry.yml.example
│       │   ├── sync/               # The sync CLI
│       │   ├── agents/             # Meta-agents
│       │   └── README.md
│       └── docs/
│
├── command centre/                 # TEMPORARY workbench (this folder)
└── docs/                           # Existing user-facing docs
```

## Layering

```
┌─────────────────────────────────────────────────────────┐
│ Mode 3: Choreography                                    │
│  - registry.yml + sync CLI + meta-agents                │
│  - Coordinates N deployments of Mode 1/2                │
└────────────┬────────────────────────────────────────────┘
             │ deploys
             ▼
┌─────────────────────────────────────────────────────────┐
│ Mode 2: Orchestration                                   │
│  - @dispatcher + @verifier + tracker adapters + hooks   │
│  - Wraps Mode 1 with autonomous dispatch                │
└────────────┬────────────────────────────────────────────┘
             │ wraps
             ▼
┌─────────────────────────────────────────────────────────┐
│ Mode 1: Team                                            │
│  - Resolved skills + instructions in .github/agents/    │
│  - Human-invoked agents in a single project repo        │
└────────────┬────────────────────────────────────────────┘
             │ resolves
             ▼
┌─────────────────────────────────────────────────────────┐
│ Shared Substrate (root)                                 │
│  skills/ instructions/ profiles/ starters/              │
│  schemas/ policies/ init.py                             │
└─────────────────────────────────────────────────────────┘
```

**Key principle:** Each mode is a layer on top of substrate, not a fork. Substrate is loaded once and used by all modes.

## Dependencies

| Mode | Depends on |
|------|-----------|
| Mode 1 | Substrate only |
| Mode 2 | Substrate + Mode 1 (Mode 2's installer calls Mode 1's installer first) |
| Mode 3 | Substrate (workspace template references substrate via submodule or vendoring) |

## Runtime Topology Per Mode

### Mode 1 runtime
```
Developer's IDE (VS Code / Claude Code)
        │
        ▼
Project repo with .github/agents/ + .github/instructions/
        │
        ▼
Agents read instructions, write artifacts to project
```

### Mode 2 runtime
```
Tracker (Linear) ◄──── @verifier writes status
        │                      ▲
        │ polled                │
        ▼                      │
hatice (orchestrator)         │
        │                      │
        ▼                      │
afterCreate.sh ── clones homebase + project to isolated workspace
        │                      │
        ▼                      │
@dispatcher classifies issue ──┘
        │
        ▼
Mode 1 agents do the work
        │
        ▼
onComplete.sh ── triggers @verifier
```

### Mode 3 runtime
```
Command centre workspace
        │
        ▼
registry.yml lists projects (path, profile, deployed_hash)
        │
        ▼
sync deploy <project>
        ├──► init.py with project's profile
        ├──► copies resolved/ to project's .github/agents/
        └──► updates deployed_hash in registry
        
sync harvest <project>
        ├──► reads project's .github/agents/
        ├──► diffs against substrate
        └──► writes report to command centre/04-harvest/
```
