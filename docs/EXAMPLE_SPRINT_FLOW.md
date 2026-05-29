# Example Sprint Flow

A complete walkthrough of running a sprint using agent-enterprise skills.

---

## Scenario

**Project:** Task Manager Pro (React + TypeScript monorepo)  
**Sprint:** Sprint 12 — "Add recurring tasks feature"  
**Mode:** Interactive (with EXIT POINTs)

---

## Phase 1: Planning

### User initiates planning

```
User: @planner I want to add recurring tasks - users should be able to set tasks to repeat daily, weekly, or monthly
```

### @planner response

```
I'll scope this feature. Let me research patterns first.

[Invokes @researcher for recurrence patterns]

Based on research, here's the scope:

**Feature: Recurring Tasks**

Tasks:
1. Add recurrence field to Task model (daily | weekly | monthly | custom)
2. Create RecurrenceService to spawn task instances
3. Add UI picker for recurrence in TaskEditModal
4. Add "next occurrence" display to TaskCard
5. Write tests for recurrence logic

Estimated complexity: Medium (5 tasks, ~12 files)

Files affected:
- apps/web/src/types/Task.ts
- apps/web/src/services/RecurrenceService.ts
- apps/web/src/components/TaskEditModal.tsx
- apps/web/src/components/TaskCard.tsx
- packages/store/src/taskStore.ts
- tests/recurrence.test.ts

Shall I draft PLAN.md?
```

### PLAN.md created

```markdown
# Sprint 12 — Recurring Tasks

**Status:** Planning  
**Type:** Feature  
**Started:** 2026-04-27

## Goals

- [x] Users can set tasks to repeat on a schedule
- [x] System automatically creates next occurrence when task completes

## Tasks

### Task 1: Data Model
**Files:** `apps/web/src/types/Task.ts`, `packages/store/src/taskStore.ts`
- Add `recurrence` field: `{ type: 'none' | 'daily' | 'weekly' | 'monthly', interval?: number }`
- Add `parentTaskId` for linking instances

### Task 2: Recurrence Service  
**Files:** `apps/web/src/services/RecurrenceService.ts`
- `createNextOccurrence(task: Task): Task`
- `calculateNextDate(task: Task): Date`
- Handle edge cases (month overflow, etc.)

### Task 3: UI - Edit Modal
**Files:** `apps/web/src/components/TaskEditModal.tsx`
- Add recurrence picker dropdown
- Show interval input for custom recurrence

### Task 4: UI - Task Card
**Files:** `apps/web/src/components/TaskCard.tsx`
- Show "Repeats: weekly" badge
- Show next occurrence date

### Task 5: Tests
**Files:** `tests/recurrence.test.ts`
- Unit tests for RecurrenceService
- Edge case tests (leap year, month end)

## Quality Gates

- [x] Typecheck
- [x] Lint  
- [x] Unit Tests (coverage >= 85%)
- [x] E2E Tests
- [x] Accessibility audit
```

---

## Phase 2: Sprint Execution

### User kicks off sprint

```
User: @sprint-lead run Sprint 12
```

### @sprint-lead Phase 1 (Kickoff)

```
📋 Sprint 12 — Recurring Tasks

Reading PLAN.md... ✓
Building task list... ✓

Task breakdown:
1. [Data Model] Task.ts, taskStore.ts
2. [Recurrence Service] RecurrenceService.ts  
3. [UI - Edit Modal] TaskEditModal.tsx
4. [UI - Task Card] TaskCard.tsx
5. [Tests] recurrence.test.ts

Dependencies: Task 1 → Task 2 → Tasks 3,4 → Task 5

⏸ EXIT POINT: Which task should I start with?
○ Task 1: Data Model (recommended - no dependencies)
○ Task 2: Recurrence Service
○ Let me review first
```

### User selects Task 1

```
User: Start with Task 1
```

### @sprint-lead delegates to subagent

```
Starting Task 1: Data Model

[Spawns unnamed subagent with task context]

Subagent return:
{
  "tier": 2,
  "status": "complete", 
  "summary": "Added recurrence field to Task type and updated store",
  "artifactPath": "apps/web/src/types/Task.ts",
  "filesChanged": ["apps/web/src/types/Task.ts", "packages/store/src/taskStore.ts"]
}

Committing: feat: add recurrence field to Task model

Moving to Task 2...
```

### Task 2-4 implementation (abbreviated)

```
Task 2: Recurrence Service ✓
  Commit: feat: add RecurrenceService with date calculation

Task 3: UI - Edit Modal ✓
  Commit: feat: add recurrence picker to TaskEditModal

Task 4: UI - Task Card ✓
  Commit: feat: show recurrence badge on TaskCard
```

---

## Phase 3: Quality Gates

```
📊 Running quality gates...

[Invokes @qa]

@qa return:
{
  "tier": 1,
  "status": "complete",
  "summary": "4/5 gates passed, coverage at 82%",
  "findings": [
    {
      "severity": "WARNING",
      "description": "Coverage at 82%, below 85% threshold",
      "recommendation": "Add tests for edge cases in RecurrenceService"
    }
  ]
}

⚠️ Coverage gate: 82% (threshold: 85%)

Spawning fix subagent for coverage...

[Subagent adds edge case tests]

Re-running @qa...

@qa return:
{
  "tier": 1,
  "status": "complete",
  "summary": "5/5 gates passed, coverage at 87%",
  "findings": []
}

✓ All quality gates passed
```

---

## Phase 4: Code Review

```
📝 Running code review...

[Invokes @reviewer]

@reviewer return:
{
  "tier": 1,
  "status": "complete",
  "summary": "Code review complete with 1 suggestion",
  "findings": [
    {
      "severity": "SUGGESTION",
      "description": "RecurrenceService.calculateNextDate could use date-fns for cleaner month handling",
      "recommendation": "Consider refactoring to use date-fns addMonths()"
    }
  ]
}

1 SUGGESTION (non-blocking)
✓ No CRITICAL or WARNING findings

Proceeding to documentation...
```

---

## Phase 5: Documentation & Ship

```
📚 Updating documentation...

[Invokes @docs]
- Updated SPRINTS.md status
- Added feature to USER_GUIDE.md

[Invokes @a11y]
@a11y: ✓ Recurrence picker is keyboard accessible, proper ARIA labels

[Invokes @perf]  
@perf: ✓ No bundle size regression (+2.1KB, within threshold)

Pushing to remote...
git push origin main ✓

Verifying CI...
gh run list --limit 1
✓ Vercel Preview: Success
```

---

## Phase 6: Retrospective

```
📊 Writing retrospective...

## Sprint 12 Retrospective

### Summary
- **Duration:** 2h 34m
- **Tasks:** 5/5 completed
- **Quality gates:** Passed (1 rerun for coverage)
- **Review findings:** 1 SUGGESTION

### Phase Timing
| Phase | Duration |
|-------|----------|
| Kickoff | 3m |
| Implementation | 1h 45m |
| Quality Gates | 28m (includes fix loop) |
| Code Review | 12m |
| Documentation | 6m |

### Metrics
- Lines added: 487
- Lines removed: 12
- Files changed: 8
- Test coverage delta: +5%

### Process Notes
- Coverage fix loop added 15 minutes
- @a11y found no issues (good pattern reuse)
- SUGGESTION logged for future refactor (date-fns)

### Forecast vs Actual
| Metric | Forecast | Actual |
|--------|----------|--------|
| Complexity | Medium | Medium |
| Duration | 2-3h | 2h 34m |
| Risk areas | Date math | ✓ Mitigated with tests |

Committing: docs: Sprint 12 — retrospective
```

---

## Final Output

```
✅ Sprint 12 Complete

Commits (6):
1. docs: Sprint 12 — kick off
2. feat: add recurrence field to Task model
3. feat: add RecurrenceService with date calculation  
4. feat: add recurrence picker to TaskEditModal
5. feat: show recurrence badge on TaskCard
6. docs: Sprint 12 — retrospective

Quality: All gates passed
Review: 1 SUGGESTION (logged)
CI/CD: Vercel Preview deployed

📁 Artifacts:
- sprints/sprint-12/PLAN.md
- sprints/sprint-12/RETRO.md
- SPRINTS.md (updated)
```

---

## Autopilot Mode Variation

For hands-free execution:

```
User: @sprint-lead autopilot Sprint 12
```

Differences:
- No EXIT POINT pauses
- Auto-selects recommended options
- Commits stay local (no push)
- Ends with: "All commits are local. Run `git push origin main` when ready."

---

## Cross-References

- [SKILL_FLOW.md](SKILL_FLOW.md) — Detailed skill execution diagrams
- [INSTRUCTION_INDEX.md](INSTRUCTION_INDEX.md) — Instructions governing this flow
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues during sprint execution
