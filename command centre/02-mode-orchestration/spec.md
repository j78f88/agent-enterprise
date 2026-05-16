# Mode 2: Orchestration — Spec

## Purpose

Mode 1 + autonomous tracker-driven dispatch. Issues in Linear (or another tracker) are picked up automatically, classified, routed to the right agent, and verified before being marked Done.

## Behavior

`delivery-modes/orchestration/install.py`:

1. Calls Mode 1's `install.py` first (Mode 2 is a superset of Mode 1)
2. Copies dispatch agents (`@dispatcher`, `@verifier`) to target's `.github/agents/`
3. Copies dispatch instructions (`dispatch-classification.md`, `completion-verification.md`, `tracker-adapter-*.md`, etc.) to `.github/instructions/`
4. Copies hooks (`afterCreate.sh`, `onComplete.sh`) to a configurable hooks location
5. Copies `WORKFLOW.md` and `hatice.env.example` to a configurable orchestration config location
6. Updates the marker file (`.github/agents/.homebase-mode`) to `mode: orchestration`

## Inputs (additional to Mode 1)

| Input | Required | Source |
|-------|----------|--------|
| Tracker type | Yes | `linear` / `github` / `gitlab` |
| Tracker workspace/repo | Yes | e.g. Linear workspace ID, GitHub `owner/repo` |
| Active states | No, has defaults | List of tracker states that trigger dispatch (default: `Todo`, `In Progress`) |
| Hooks install path | No, default `./hooks/` | Where to write `afterCreate.sh`, `onComplete.sh` |
| Orchestrator config path | No, default `./.orchestration/` | Where to write `WORKFLOW.md`, env example |

## Outputs (additional to Mode 1)

```
<target>/
├── .github/
│   ├── agents/
│   │   ├── .homebase-mode             # mode: "orchestration"
│   │   ├── dispatcher/SKILL.md        # NEW
│   │   └── verifier/SKILL.md          # NEW
│   └── instructions/
│       ├── dispatch-classification.md         # NEW
│       ├── completion-verification.md         # NEW
│       ├── retry-escalation.md                # NEW
│       ├── context-gathering.md               # NEW
│       └── tracker-adapter-*.md               # NEW (10 files)
├── hooks/
│   ├── afterCreate.sh                  # NEW
│   └── onComplete.sh                   # NEW
└── .orchestration/
    ├── WORKFLOW.md                     # NEW
    └── hatice.env.example              # NEW
```

## Runtime (post-install)

The user runs hatice (or another orchestrator) pointing at:
- The orchestration config (`./.orchestration/WORKFLOW.md`)
- Their tracker (via env from `hatice.env`)

hatice polls the tracker, calls `afterCreate.sh` to set up an isolated workspace, dispatches via `@dispatcher`, and verifies via `@verifier` on completion.

## Composition with Mode 1

Mode 2's installer is essentially:
```python
team_install(target, profile, ...)
copy_orchestration_assets(target, ...)
update_marker(target, mode="orchestration")
```

Re-running Mode 2's installer always re-runs Mode 1's installer first. A project at Mode 2 cannot drop back to Mode 1 without an explicit `uninstall-orchestration` operation.

## Migration from current state

The current `agent-orchestration` repo is cloned as a sibling of homebase and overlaid via `afterCreate.sh`. After absorption:

- `agent-orchestration/agents/*` → `delivery-modes/orchestration/agents/`
- `agent-orchestration/instructions/*` → `delivery-modes/orchestration/instructions/`
- `agent-orchestration/hooks/*` → `delivery-modes/orchestration/hooks/`
- `agent-orchestration/config/*` and `WORKFLOW.md` → `delivery-modes/orchestration/config/`
- `agent-orchestration/docs/*` → `delivery-modes/orchestration/docs/`

`afterCreate.sh` no longer clones a third repo — orchestration assets are inside homebase.

## Non-goals

- No multi-project coordination (that's Mode 3)
- No tracker-agnostic abstraction layer beyond what tracker-adapter-*.md already provides
- No replacing hatice — Mode 2 ships compatible config; users supply the runtime
