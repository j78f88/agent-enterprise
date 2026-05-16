# Mode 2: Orchestration — Absorption Checklist

Step-by-step: migrate the standalone `agent-orchestration` repo into `delivery-modes/orchestration/`.

## Source: `D:\VS\agent-orchestration`

## Target: `D:\VS\agent-homebase\delivery-modes\orchestration`

## File-by-File Migration

| Source path | Target path | Notes |
|-------------|-------------|-------|
| `agents/dispatcher.body.md` | `delivery-modes/orchestration/agents/dispatcher.body.md` | Move as-is |
| `agents/verifier.body.md` | `delivery-modes/orchestration/agents/verifier.body.md` | Move as-is |
| `skills/dispatcher/dispatcher.skill.md` | `delivery-modes/orchestration/skills/dispatcher/dispatcher.skill.md` | Move as-is |
| `skills/verifier/verifier.skill.md` | `delivery-modes/orchestration/skills/verifier/verifier.skill.md` | Move as-is |
| `instructions/dispatch-classification.md` | `delivery-modes/orchestration/instructions/dispatch-classification.md` | Move as-is |
| `instructions/context-gathering.md` | `delivery-modes/orchestration/instructions/context-gathering.md` | Move as-is |
| `instructions/completion-verification.md` | `delivery-modes/orchestration/instructions/completion-verification.md` | Move as-is |
| `instructions/retry-escalation.md` | `delivery-modes/orchestration/instructions/retry-escalation.md` | Move as-is |
| `instructions/tracker-adapter-*.md` (10 files) | `delivery-modes/orchestration/instructions/` | Move as-is |
| `hooks/afterCreate.sh` | `delivery-modes/orchestration/hooks/afterCreate.sh` | **MODIFY** — see below |
| `hooks/onComplete.sh` | `delivery-modes/orchestration/hooks/onComplete.sh` | Move as-is |
| `config/hatice.env.example` | `delivery-modes/orchestration/config/hatice.env.example` | Move as-is |
| `WORKFLOW.md` | `delivery-modes/orchestration/config/WORKFLOW.md` | Move as-is |
| `docs/ARCHITECTURE.md` | `delivery-modes/orchestration/docs/ARCHITECTURE.md` | **REWRITE** — three-repo → two-repo |
| `docs/RUNBOOK.md` | `delivery-modes/orchestration/docs/RUNBOOK.md` | Update paths |
| `CLAUDE.md` | `delivery-modes/orchestration/docs/CLAUDE.md` | Move as-is |

## `afterCreate.sh` Changes

Current behavior: clones THREE repos (agent-homebase, agent-orchestration, project) into an isolated workspace and overlays them.

New behavior: clones TWO repos (agent-homebase, project). Orchestration assets are at `<homebase>/delivery-modes/orchestration/` and overlaid from there.

```diff
- git clone <agent-homebase-url>     $WORKSPACE/agent-homebase
- git clone <agent-orchestration-url> $WORKSPACE/agent-orchestration
- git clone <project-url>             $WORKSPACE/project
+ git clone <agent-homebase-url>     $WORKSPACE/agent-homebase
+ git clone <project-url>             $WORKSPACE/project

- cp -r $WORKSPACE/agent-homebase/skills/*           $WORKSPACE/.claude/agents/
- cp -r $WORKSPACE/agent-orchestration/agents/*     $WORKSPACE/.claude/agents/
- cp -r $WORKSPACE/agent-orchestration/instructions/* $WORKSPACE/.claude/instructions/
+ cp -r $WORKSPACE/agent-homebase/skills/*                                $WORKSPACE/.claude/agents/
+ cp -r $WORKSPACE/agent-homebase/delivery-modes/orchestration/agents/*  $WORKSPACE/.claude/agents/
+ cp -r $WORKSPACE/agent-homebase/delivery-modes/orchestration/instructions/* $WORKSPACE/.claude/instructions/
```

## Validation Steps

1. **Source-target hash compare** — for files moved as-is, `sha256` of source must match `sha256` of target. Script:
   ```powershell
   Compare-Object (Get-FileHash <source> SHA256) (Get-FileHash <target> SHA256)
   ```
2. **WORKFLOW.md path references** — grep for any references to `agent-orchestration` repo paths; update to `delivery-modes/orchestration` paths.
3. **End-to-end smoke test** — run a Linear issue through `@dispatcher` → `@verifier` against verk-v2 using the new layout. Compare behavior to pre-absorption baseline.
4. **Documentation sync** — confirm `delivery-modes/orchestration/docs/ARCHITECTURE.md` no longer references "three-repo composition"; updates to "two-repo composition" or just "homebase + project".

## Standalone Repo Disposition

After absorption is validated:

1. Tag final commit of `agent-orchestration` with `v-final-pre-absorption`
2. Replace README with redirect:
   ```markdown
   # agent-orchestration (archived)
   
   This repo's contents have been absorbed into agent-homebase as Mode 2 (Orchestration).
   See: https://github.com/j78f88/agent-homebase/tree/main/delivery-modes/orchestration
   
   This repo is archived for historical reference. Do not modify.
   ```
3. Archive the GitHub repo (read-only)

## Risks

| Risk | Mitigation |
|------|-----------|
| Existing deployments break when `afterCreate.sh` changes | Keep old script working until all known users migrate; tag old hash for rollback |
| Hatice config has hardcoded paths to `agent-orchestration` | Audit and update before declaring absorption complete |
| Lost git history for orchestration files | History preserved in archived repo; new commits attribute via commit message |
