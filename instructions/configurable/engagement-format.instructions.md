---
id: instruction.engagement-format
kind: instruction
version: 1.0.0
applies_to: '**'
description: Use when creating, updating, or reading engagement tracking files (brief.md, gate-log.md, deployment-log.md). Defines the ENG-NNN numbering scheme, engagement folder structure, file formats, and status lifecycle.
applyTo: '{{paths.engagements}}**'
---

# Engagement Tracking Format

Single schema and lifecycle specification for engagement tracking under `{{paths.engagements}}`.

## Engagement Folder Structure

Each engagement lives at: `{{paths.engagements}}{{ids.engagement_prefix}}-NNN-{slug}/`

```
{{ids.engagement_prefix}}-001-export-pdf/
  brief.md          — What, why, acceptance criteria, size, constraints
  gate-log.md       — Gate decisions (sprint-scoped, multi-sprint ready)
  deployment-log.md — Test URL, E2E results, prod URL, smoke results
  validation.md     — Validation subagent output (M/L size only)
```

## ID Assignment

`{{ids.engagement_prefix}}-NNN`, zero-padded to 3 digits, sequential. Scan `{{paths.engagements}}` for the highest existing N; assign N+1. If no engagements exist, start at {{ids.engagement_prefix}}-001.

## Status Lifecycle

```
INTAKE → VALIDATING → PLANNING → EXECUTING → TESTING → DEPLOYING → COMPLETE
                                                                   → CANCELLED
```

Status is tracked in `gate-log.md` via the most recent entry's gate/decision combination:
- INTAKE: brief.md exists, no gate-log entries
- VALIDATING: Gate 1 pending
- PLANNING: Gate 1 approved, Gate 2 pending
- EXECUTING: Gate 2 approved, @sprint-lead in progress
- TESTING: Sprint complete, test deployment pending/in-progress
- DEPLOYING: Gate 3 approved, production deployment pending
- COMPLETE: Gate 4 confirmed
- CANCELLED: Any gate rejected or CTO abort

## Brief Format (`brief.md`)

Use template from `docs/templates/engagement-brief.md`. Required fields:

```markdown
# {{ids.engagement_prefix}}-NNN — {Title}

## Summary
{One-paragraph description of what and why}

## Size Classification
{S | M | L} — {Rationale for classification}

## Acceptance Criteria
- [ ] {Criterion 1}
- [ ] {Criterion 2}

## Scope Boundaries
**In scope:** {What's included}
**Out of scope:** {What's excluded}

## Constraints
{Dependencies, deadlines, technical constraints}

## Priority
{Relative priority and rationale}
```

## Gate Log Format (`gate-log.md`)

Use template from `docs/templates/gate-log.md`. Sprint-scoped, multi-sprint ready from day 1:

```markdown
# {{ids.engagement_prefix}}-NNN — Gate Log

| Date | Sprint | Gate | Decision | Detail |
|------|--------|------|----------|--------|
```

**Gate values:** Requirements, Plan, Test Deploy, Production
**Decision values:** APPROVED, REJECTED, OVERRIDE, SIZE-OVERRIDE, FAILED, CONFIRMED, CANCELLED, FIX-REQUESTED

## Deployment Log Format (`deployment-log.md`)

```markdown
# {{ids.engagement_prefix}}-NNN — Deployment Log

## Test Deployment
- **Environment URL:** {URL}
- **Deployment Target:** {e.g., Azure SWA test instance}
- **Workflow Run:** {run ID or link}
- **Automated Test Results:** {pass/fail count}
- **Date:** {ISO date}

## Production Deployment
- **Environment URL:** {URL}
- **Deployment Target:** {e.g., Azure SWA production}
- **Workflow Run:** {run ID or link}
- **Automated Test Results:** {pass/fail count}
- **Date:** {ISO date}
```

Fields are platform-agnostic: "Environment URL", "Automated Test Results", "Deployment Target" — not web-specific.
