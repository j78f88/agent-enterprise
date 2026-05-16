# The Three Modes

agent-homebase ships as one library that can be deployed in three modes. Each mode wraps the same shared substrate (skills, instructions, profiles) but with different installation and runtime behavior.

## Mode 1 — Team

**What it is:** A structured 13-agent delivery team dropped into a single project repo.

**Use when:**
- You have one project and want a consistent agent team in it
- A human (you) drives invocations (`@planner`, `@sprint-lead`, etc.)
- No tracker integration needed

**What gets installed:**
- Resolved skills → `.github/agents/`
- Resolved instructions → `.github/instructions/`
- Starter planning files → `docs/planning/`, `SPRINTS.md`, etc.

**Today's status:** Works via `init.py` + manual copy. Mode 1 formalizes this as `delivery-modes/team/install.py`.

---

## Mode 2 — Orchestration

**What it is:** Mode 1 + an autonomous dispatch layer driven by an issue tracker (Linear, GitHub Issues, etc.).

**Use when:**
- You have one project and want agents to run autonomously without human invocation
- Tracker is the source of truth for work state
- You need completion verification (no "ghost-done" issues)

**What gets installed:**
- Everything from Mode 1, plus:
- `@dispatcher` and `@verifier` agents
- Dispatch classification + completion verification instructions
- Tracker adapter instructions (Linear/GitHub/etc.)
- `afterCreate.sh` / `onComplete.sh` hooks
- `WORKFLOW.md` for hatice-style runtime
- Env template (`hatice.env.example`)

**Today's status:** Lives in separate `agent-orchestration` repo. Phase 2 absorbs it into `delivery-modes/orchestration/`.

---

## Mode 3 — Choreography

**What it is:** A command-centre workspace that coordinates Mode 1 (and optionally Mode 2) deployments across N projects as a program of works.

**Use when:**
- You have multiple projects and want them to share one evolving framework
- Improvements should propagate (homebase update → all registered projects)
- Mature patterns from one project should be harvestable back into the substrate
- You're running a portfolio, not a single project

**What gets installed:**
- A fresh workspace at a chosen path containing:
  - `registry.yml` listing all target projects
  - `sync` CLI (`deploy`, `diff`, `status`, `harvest`)
  - Meta-agents for framework dev + harvest work (distinct from the 13 delivery agents)
  - Submodule references to homebase (and optionally per-project repos)

**Today's status:** Doesn't exist. The `command centre/` folder is the staging ground; Phase 3 builds it; Phase 6 graduates it.

---

## Mode Composition

Mode 3 = Mode 2 applied to N instances of Mode 1.

A typical Mode 3 deployment:
1. Choreography workspace registers 5 projects
2. `sync deploy --all` installs Mode 1 in 4 of them, Mode 2 in 1 (the high-throughput one)
3. Improvements made in the workspace flow out to all 5 via `sync deploy`
4. Mature patterns flow back via `sync harvest`

## Selection Guide

```
How many projects do you have?
├── 1 project
│   ├── Need autonomous tracker-driven dispatch? → Mode 2
│   └── Human-driven invocations? → Mode 1
└── 2+ projects
    └── Want propagation + harvest across them? → Mode 3
```
