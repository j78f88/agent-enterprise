---
description: "Use when writing or seeding RETRO.md files, defining complexity assessments, or assembling sprint retrospectives. Defines the schema, complexity scale, forecast format, and finalized structure for sprint retrospectives."
applyTo: "sprints/**/RETRO.md"
---

# Retrospective Report Format

Schema, templates, and lifecycle rules for `RETRO.md` — the sprint retrospective artifact.

## § Complexity Scale

| Level           | Definition                                                                 |
| --------------- | -------------------------------------------------------------------------- |
| trivial         | Config change, copy update, single-line fix. No tests affected.            |
| straightforward | Isolated change in 1-2 files. Clear path, minimal risk.                    |
| moderate        | Touches 3-5 files or crosses one boundary (store↔component). Some risk.    |
| complex         | Crosses multiple boundaries, new patterns, 6+ files. Requires design.      |
| gnarly          | Architectural change, multi-store coordination, unknown unknowns. High risk.|

## § Forecast Format

The `@planner` generates a `## Sprint Forecast` section containing these subsections:

1. **Sprint Type** — one of: `feature` | `fix` | `debt` | `restructure` | `coverage` | `mixed`
2. **Per-Task Complexity Forecast** — table:

   | Task | Expected Complexity | Reasoning |
   | ---- | ------------------- | --------- |
   | …    | moderate            | …         |

3. **Risk Areas** — 1-3 tasks most likely to surprise, with reasoning
4. **Assumptions** — explicit statements the plan depends on (e.g., "existing store migration chain is intact")
5. **Expected Gate Outcomes** — per gate: PASS or RISK + reasoning
6. **Scope Estimate** — files to touch, estimated lines changed, subagents expected
7. **Watch Items** — cross-task interactions, hidden dependencies, sequencing concerns

## § Seeded RETRO.md Structure

Written by `@planner` at promotion (via `/promote-draft`). This is the initial file placed in `sprints/sprint-N/RETRO.md`:

```markdown
# Sprint N Retrospective — [title]

<!-- FORECAST — seeded by @planner at promotion -->

## Sprint Forecast

[Sprint Forecast section copied verbatim from the draft plan]

<!-- /FORECAST -->

<!-- ACTUALS — to be completed by @sprint-lead at sprint completion -->

## Section 0: Forecast vs. Actual
_To be completed by @sprint-lead_

## Section 1: Sprint Summary
_To be completed by @sprint-lead_

## Section 2: Execution Timeline
_To be completed by @sprint-lead_

## Section 3: Complexity Profile
_To be completed by @sprint-lead_

## Section 4: Process Health
_To be completed by @sprint-lead_

## Section 5: Quality Results
_To be completed by @sprint-lead_

## Section 6: Code Review
_To be completed by @sprint-lead_

## Section 7: Retrospective
_To be completed by @sprint-lead_

## Section 8: Commits
_To be completed by @sprint-lead_

## Section 9: Carry-Over
_To be completed by @sprint-lead_

## Section 10: Sprint Trends
_To be completed by @sprint-lead_

## Section 11: Owner Notes
_Reserved for project owner — no agent writes here._

<!-- /ACTUALS -->
```

## § RETRO.md Finalized Structure

The 12 sections `@sprint-lead` fills in at Phase 6. Each section uses data from subagent returns, the process ledger, and prior RETRO.md files.

### Section 0: Forecast vs. Actual

- **Previous Action Items: Status** — table from the prior sprint's Section 7 action items:

  | Action Item | Target | Status |
  | ----------- | ------ | ------ |
  | …           | Sprint N | ✅ Done / ⏳ In Progress / ❌ Not Started |

  If no prior RETRO.md exists, write: "No prior retrospective — skipping action item review."

- **Complexity Comparison** — table:

  | Task | Forecast | Actual | Δ | Accurate? |
  | ---- | -------- | ------ | - | --------- |
  | …    | moderate | complex | +1 | ❌ |

- **Assumptions Check** — table:

  | Assumption | Held? | Notes |
  | ---------- | ----- | ----- |
  | …          | ✅ / ❌ | … |

- **Risk Area Accuracy** — which predicted risks materialized, which didn't, any missed risks
- **Forecast Calibration Score**:
  - Assumptions accuracy: X/Y (Z%)
  - Complexity accuracy: X/Y (Z%)
  - Combined: (assumptions% + complexity%) / 2

### Section 1: Sprint Summary

- Tasks planned / completed / blocked / partial
- Files created / modified (totals)
- Sprint type (from forecast)

### Section 2: Execution Timeline

Per-phase wall-clock durations:

| Phase | Duration | Notes |
| ----- | -------- | ----- |
| Phase 1: Kickoff | Xm | … |
| Phase 2: Implementation | Xm | … |
| Phase 2.5: Safety-Net | Xm | … |
| Phase 3: Quality Gates | Xm | … |
| Phase 4: Code Review | Xm | … |
| Phase 5: Documentation | Xm | … |
| Phase 6: Retrospective | Xm | … |
| **Total** | **Xm** | |

### Section 3: Complexity Profile

Per-task detail:

| Task | Complexity | Lines +/- | Files | Fix Iterations | Duration |
| ---- | ---------- | --------- | ----- | -------------- | -------- |
| …    | moderate   | +120 / -30 | 4    | 0              | ~8m      |

- Duration is best-effort from commit timestamp gaps
- Totals row + complexity distribution (e.g., "2 moderate, 1 complex, 1 straightforward")

### Section 4: Process Health

- Subagent counts: implementation / fix / specialist
- Gate reruns (count and reason)
- Blocked/partial tasks
- Fix loop detail:

  | Fix # | Trigger | Root Cause | Files |
  | ----- | ------- | ---------- | ----- |
  | 1     | lint    | unused import | app.tsx |

- Gate pass rate: X/Y first-pass

### Section 5: Quality Results

From specialist JSON summaries (@qa, @a11y, @perf):

- TypeScript: PASS/FAIL
- Lint: PASS/FAIL (warning count)
- Unit Tests: X passed / Y failed / Z skipped
- Coverage: store X%, web X%
- E2E: X passed / Y failed
- A11y: X violations (if gate ran)
- Perf: bundle X KB, build Xs (if gate ran)

### Section 6: Code Review

From @reviewer JSON summary:

| Severity | Count | All Resolved? |
| -------- | ----- | ------------- |
| CRITICAL | X     | ✅ / ❌ |
| WARNING  | X     | — |
| SUGGESTION | X   | — |

### Section 7: Retrospective

- **What went well** — 2-4 bullets
- **What didn't go well** — 2-4 bullets. If forecast Watch Items flagged task ordering concerns, assess whether the chosen ordering worked or caused problems.
- **Surprises & Lessons** — unexpected findings
- **Start / Stop / Continue**:
  - Start: practices to adopt
  - Stop: practices to drop
  - Continue: practices working well
- **Action Items** — 1-3 concrete items:

  | Action Item | Target |
  | ----------- | ------ |
  | …           | Sprint N+1 |

### Section 8: Commits

| Hash | Message |
| ---- | ------- |
| abc1234 | feat: Sprint N — description |

### Section 9: Carry-Over

Items not completed this sprint. Each entry annotated:

- **First logged: Sprint N** — when this item first appeared
- Items carried 3+ sprints: flagged with ⚠ (e.g., "⚠ First logged: Sprint N-4 — consider escalating or dropping")

### Section 10: Sprint Trends

N-2 comparison table (oldest available if fewer than 3 sprints have RETRO.md):

| Metric | Sprint N-2 | Sprint N-1 | Sprint N | Signal |
| ------ | ---------- | ---------- | -------- | ------ |
| Sprint type | — | feature | debt | — |
| Tasks planned | — | 8 | 5 | — |
| Tasks completed | — | 8 | 5 | — |
| Completion rate | — | 100% | 100% | ● |
| Total duration | — | 45m | 32m | ▲ |
| Files changed | — | 24 | 12 | — |
| Lines added | — | 580 | 210 | — |
| Lines removed | — | 120 | 85 | — |
| Fix iterations | — | 3 | 1 | ▲ |
| Gate reruns | — | 1 | 0 | ▲ |
| Gate first-pass rate | — | 75% | 100% | ▲ |
| Review CRITICALs | — | 2 | 0 | ▲ |
| Carry-over items | — | 1 | 0 | ▲ |
| Forecast calibration | — | 62% | 85% | ▲ |
| Test count delta | — | +15 | +8 | — |
| Coverage delta | — | +2.1% | +0.5% | — |

**Signal key:** ● stable, ▲ improving, ▼ declining, ⚠ needs attention

**Drift Analysis** — 2-5 interpretive bullets. Note sprint type when comparing ("debt sprint expected fewer lines than feature sprint"). Flag ⚠ signals.

### Section 11: Owner Notes

Empty section. Reserved for the project owner to annotate after reading. No agent writes here.
