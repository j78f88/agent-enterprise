# Example Skill Outputs

Sample return values for each subagent tier. Use these as reference when building integrations or debugging unexpected returns.

---

## Tier 1: Analysis Only

Returns that produce no artifacts. Used for validation, analysis, and recommendations.

### @pm — Feature Validation (5-Test Echo Chamber)

```json
{
  "tier": 1,
  "agent": "pm",
  "status": "complete",
  "summary": "Feature passes 4/5 validation tests. Recommend proceeding with minor scope adjustment.",
  "findings": [
    {
      "severity": "WARNING",
      "description": "Test 3 (Competitor Parity): Feature exceeds competitor scope — risk of over-engineering",
      "recommendation": "Consider phasing: v1 with core recurrence, v2 with custom intervals"
    },
    {
      "severity": "SUGGESTION",
      "description": "Test 5 (Maintenance Burden): Date math is historically error-prone",
      "recommendation": "Add comprehensive edge case tests for month boundaries and leap years"
    }
  ],
  "flaggedDecisions": [
    "Should custom intervals be included in v1 or deferred to v2?"
  ]
}
```

### @qa — Quality Pipeline Results

```json
{
  "tier": 1,
  "agent": "qa",
  "status": "complete",
  "summary": "5/5 quality gates passed. Coverage at 87%, all tests green.",
  "findings": []
}
```

### @qa — Quality Pipeline with Failures

```json
{
  "tier": 1,
  "agent": "qa",
  "status": "blocked",
  "summary": "2/5 quality gates failed. Typecheck errors and coverage below threshold.",
  "blockerReason": "Typecheck found 3 errors in RecurrenceService.ts; coverage at 72% (threshold: 85%)",
  "findings": [
    {
      "severity": "CRITICAL",
      "description": "Typecheck failed: 3 errors in RecurrenceService.ts",
      "recommendation": "Fix type errors before proceeding"
    },
    {
      "severity": "CRITICAL", 
      "description": "Coverage at 72%, below 85% threshold",
      "recommendation": "Add tests for calculateNextDate edge cases"
    }
  ]
}
```

### @reviewer — Code Review

```json
{
  "tier": 1,
  "agent": "reviewer",
  "status": "complete",
  "summary": "Code review complete. 1 WARNING, 2 SUGGESTIONS.",
  "findings": [
    {
      "severity": "WARNING",
      "description": "RecurrenceService has no error handling for invalid dates",
      "recommendation": "Add try-catch and return Result<Date, Error> instead of throwing"
    },
    {
      "severity": "SUGGESTION",
      "description": "TaskCard recurrence badge could use shared Badge component",
      "recommendation": "Refactor to use <Badge variant='info'> for consistency"
    },
    {
      "severity": "SUGGESTION",
      "description": "Consider extracting date formatting to a utility function",
      "recommendation": "Create formatRecurrenceDate() in utils/date.ts"
    }
  ]
}
```

### @a11y — Accessibility Audit

```json
{
  "tier": 1,
  "agent": "a11y",
  "status": "complete",
  "summary": "WCAG 2.1 AA audit passed. Minor suggestion for screen reader experience.",
  "findings": [
    {
      "severity": "SUGGESTION",
      "description": "Recurrence dropdown announces 'combobox' but not current selection",
      "recommendation": "Add aria-live region to announce selected recurrence type"
    }
  ]
}
```

### @perf — Performance Audit

```json
{
  "tier": 1,
  "agent": "perf",
  "status": "complete", 
  "summary": "Bundle size within limits. Build time acceptable.",
  "findings": [
    {
      "severity": "WARNING",
      "description": "date-fns import adds 12KB to bundle",
      "recommendation": "Use selective imports: import { addDays } from 'date-fns/addDays'"
    }
  ]
}
```

---

## Tier 2: With Artifacts

Returns that produce a single artifact (draft, document, code file).

### @planner — Feature Draft

```json
{
  "tier": 2,
  "agent": "planner",
  "status": "complete",
  "summary": "Feature scope complete. Draft saved to drafts/recurring-tasks-draft.md",
  "artifactPath": "docs/planning/drafts/recurring-tasks-draft.md",
  "artifactType": "draft",
  "findings": [
    {
      "severity": "SUGGESTION",
      "description": "Consider splitting into 2 sprints if timeline is tight",
      "recommendation": "Sprint A: core recurrence, Sprint B: custom intervals + UI polish"
    }
  ]
}
```

### @researcher — Research Summary

```json
{
  "tier": 2,
  "agent": "researcher",
  "status": "complete",
  "summary": "Research complete. Found 3 relevant patterns from industry leaders.",
  "artifactPath": "docs/planning/research/recurrence-patterns.md",
  "artifactType": "research",
  "findings": [
    {
      "severity": "SUGGESTION",
      "description": "Todoist uses RRULE spec for complex recurrence",
      "recommendation": "Consider RRULE for future extensibility, but overkill for v1"
    }
  ],
  "citations": [
    {
      "source": "Todoist Engineering Blog",
      "url": "https://todoist.com/engineering/recurring-tasks",
      "relevance": "Direct competitor implementation"
    },
    {
      "source": "RFC 5545 (iCalendar)",
      "url": "https://tools.ietf.org/html/rfc5545",
      "relevance": "RRULE specification for recurrence"
    }
  ]
}
```

### @architect — Design Document

```json
{
  "tier": 2,
  "agent": "architect",
  "status": "complete",
  "summary": "Architecture decision recorded. Recommending service-based approach.",
  "artifactPath": "docs/architecture/design-reviews/ADR-015-recurrence-service.md",
  "artifactType": "adr",
  "findings": []
}
```

### @docs — Documentation Update

```json
{
  "tier": 2,
  "agent": "docs",
  "status": "complete",
  "summary": "User guide updated with recurring tasks documentation.",
  "artifactPath": "docs/user/USER_GUIDE.md",
  "artifactType": "documentation",
  "findings": []
}
```

### @bug — Bug Report

```json
{
  "tier": 2,
  "agent": "bug",
  "status": "complete",
  "summary": "Bug logged to backlog with reproduction steps.",
  "artifactPath": "docs/planning/BUG_BACKLOG.md",
  "artifactType": "bug-entry",
  "bugId": "BUG-047",
  "findings": [
    {
      "severity": "WARNING",
      "description": "Similar bug BUG-032 was fixed but may have regressed",
      "recommendation": "Check if BUG-032 fix was reverted or bypassed"
    }
  ]
}
```

---

## Tier 3: Composition

Returns with multiple artifacts, metadata, and provenance. Used by orchestrators.

### @sprint-lead — Sprint Completion

```json
{
  "tier": 3,
  "agent": "sprint-lead",
  "status": "complete",
  "summary": "Sprint 12 complete. 5 tasks delivered, all gates passed.",
  "artifacts": [
    {
      "path": "sprints/sprint-12/PLAN.md",
      "type": "plan",
      "action": "created"
    },
    {
      "path": "sprints/sprint-12/RETRO.md", 
      "type": "retrospective",
      "action": "created"
    },
    {
      "path": "SPRINTS.md",
      "type": "tracking",
      "action": "updated"
    },
    {
      "path": "docs/user/USER_GUIDE.md",
      "type": "documentation",
      "action": "updated"
    }
  ],
  "metadata": {
    "sprintId": "012",
    "duration": "2h 34m",
    "tasksCompleted": 5,
    "tasksTotal": 5,
    "commits": 6,
    "linesAdded": 487,
    "linesRemoved": 12,
    "coverageDelta": "+5%"
  },
  "provenance": {
    "subagentCalls": [
      {"agent": "qa", "invocations": 2, "status": "passed"},
      {"agent": "reviewer", "invocations": 1, "status": "passed"},
      {"agent": "a11y", "invocations": 1, "status": "passed"},
      {"agent": "perf", "invocations": 1, "status": "passed"},
      {"agent": "docs", "invocations": 1, "status": "passed"}
    ],
    "fixLoops": 1,
    "gateReruns": 1
  },
  "findings": [
    {
      "severity": "SUGGESTION",
      "description": "1 code review suggestion logged for future refactor",
      "recommendation": "See RETRO.md Process Notes"
    }
  ]
}
```

---

## Status Values

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `complete` | Task finished successfully | Proceed to next step |
| `blocked` | Cannot proceed without intervention | Check `blockerReason`, fix issue |
| `needs-input` | Requires user decision | Present options via askQuestions |

---

## Severity Levels

| Severity | Blocks Progress | Action Required |
|----------|-----------------|-----------------|
| `CRITICAL` | Yes | Must fix before proceeding |
| `WARNING` | Configurable | Should fix, may proceed with flag |
| `SUGGESTION` | No | Log for future improvement |

---

## Schema References

Full JSON Schema definitions:
- [subagent-return-tier1.schema.json](../schemas/subagent-return-tier1.schema.json)
- [subagent-return-tier2.schema.json](../schemas/subagent-return-tier2.schema.json)
- [subagent-return-tier3.schema.json](../schemas/subagent-return-tier3.schema.json)

---

## Cross-References

- [SKILL_FLOW.md](SKILL_FLOW.md) — When each skill returns which tier
- [INSTRUCTION_INDEX.md](INSTRUCTION_INDEX.md) — `subagent-return-schemas.instructions.md` for full contract
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Debugging unexpected returns
