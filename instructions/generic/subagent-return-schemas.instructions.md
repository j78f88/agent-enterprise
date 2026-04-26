# Subagent Return Schemas

Centralized return schemas for subagent mode invocations. Referenced declaratively by agent files — no `applyTo` pattern.

> **Protocol:** When `@delivery-lead` invokes a specialist agent in `[SUBAGENT-MODE]`, the specialist skips session lifecycle and returns structured data per the tier matching the write permit token.

## Write Permit Tokens

Write permits control what a subagent may create on disk. The invoking agent includes exactly one token in the subagent prompt.

| Token                  | Permitted Output                                    | Used By        |
| ---------------------- | --------------------------------------------------- | -------------- |
| `[WRITE:BRAINSTORM]`  | `docs/planning/drafts/*-brainstorm.md`              | `@planner`     |
| `[WRITE:DRAFT-PLAN]`  | `docs/planning/drafts/*-draft-plan.md`              | `@planner`     |
| `[WRITE:ANALYSIS-ONLY]` | No file writes — return JSON only                 | `@planner`, `@pm` |
| `[WRITE:VALIDATION]`  | `docs/planning/validation/*-validation.md`          | `@pm`          |
| `[WRITE:RESEARCH]`    | `docs/research/*` and `docs/planning/research/*`    | `@researcher`  |
| `[WRITE:ARCHITECTURE]` | `docs/architecture/*` (ADR drafts, analysis docs)  | `@architect`   |

A subagent that writes to a path not covered by its write permit is in violation. The invoking agent must reject the return and flag the violation.

## Tier 1 — Analysis Returns

Used for quick assessments that produce no artifacts. Write permit: `[WRITE:ANALYSIS-ONLY]`.

### Schema

```json
{
  "tier": 1,
  "agent": "<agent-name>",
  "status": "complete" | "blocked" | "needs-input",
  "summary": "<1-2 sentence result>",
  "findings": [
    {
      "severity": "CRITICAL" | "WARNING" | "SUGGESTION",
      "description": "<finding description>",
      "recommendation": "<recommended action>"
    }
  ],
  "flaggedDecisions": [
    "<decision requiring human checkpoint>"
  ],
  "blockerReason": "<why blocked, if status=blocked>"
}
```

### Fields

| Field             | Required | Description                                                    |
| ----------------- | -------- | -------------------------------------------------------------- |
| `tier`            | Yes      | Always `1`                                                     |
| `agent`           | Yes      | Agent name (e.g., `planner`, `pm`)                             |
| `status`          | Yes      | `complete`, `blocked`, or `needs-input`                        |
| `summary`         | Yes      | Brief result summary                                           |
| `findings`        | Yes      | Array of findings (may be empty)                               |
| `flaggedDecisions`| No       | Decisions that require human confirmation before proceeding    |
| `blockerReason`   | No       | Required if `status` = `blocked`                               |

## Tier 2 — Artifact Returns

Used when the subagent creates a file artifact. Write permits: `[WRITE:BRAINSTORM]`, `[WRITE:DRAFT-PLAN]`, `[WRITE:VALIDATION]`, `[WRITE:RESEARCH]`, `[WRITE:ARCHITECTURE]`.

### Schema

```json
{
  "tier": 2,
  "agent": "<agent-name>",
  "status": "complete" | "blocked" | "needs-input",
  "summary": "<1-2 sentence result>",
  "artifactPath": "<relative path to created file>",
  "artifactType": "brainstorm" | "draft-plan" | "validation" | "research" | "architecture",
  "findings": [
    {
      "severity": "CRITICAL" | "WARNING" | "SUGGESTION",
      "description": "<finding description>",
      "recommendation": "<recommended action>"
    }
  ],
  "flaggedDecisions": [
    "<decision requiring human checkpoint>"
  ],
  "blockerReason": "<why blocked, if status=blocked>"
}
```

### Additional Fields (over Tier 1)

| Field           | Required | Description                                            |
| --------------- | -------- | ------------------------------------------------------ |
| `artifactPath`  | Yes      | Relative path to the created artifact                  |
| `artifactType`  | Yes      | Category of the artifact matching the write permit     |

## Tier 3 — Composition Returns

Used by `/compose-sprint` for sprint composition recommendations. No write permit — composition draft is managed by the prompt workflow.

### Schema

```json
{
  "tier": 3,
  "agent": "planner",
  "status": "complete" | "blocked" | "needs-input",
  "summary": "<1-2 sentence composition summary>",
  "sprintNumber": "<recommended sprint number>",
  "composition": [
    {
      "itemId": "ITEM-NNN",
      "type": "<ledger type>",
      "tier": "P0" | "P1" | "P2" | "P3" | "P4" | "P5" | "P6",
      "score": "<intra-tier score>",
      "rationale": "<why included>"
    }
  ],
  "excluded": [
    {
      "itemId": "ITEM-NNN",
      "reason": "<why excluded from this sprint>"
    }
  ],
  "constraints": {
    "featurePercent": "<% of capacity allocated to features>",
    "bugCount": "<number of bug items included>",
    "debtPressure": "<current debt pressure score>",
    "capacityUsed": "<% of estimated capacity used>"
  },
  "flaggedDecisions": [
    "<decision requiring human checkpoint>"
  ],
  "blockerReason": "<why blocked, if status=blocked>"
}
```

### Additional Fields (over Tier 1)

| Field         | Required | Description                                                    |
| ------------- | -------- | -------------------------------------------------------------- |
| `sprintNumber`| Yes      | Target sprint number for the composition                       |
| `composition` | Yes      | Ordered list of items recommended for inclusion                |
| `excluded`    | No       | Items considered but excluded, with reasons                    |
| `constraints` | Yes      | Composition constraint metrics for the recommendation          |

## Return Validation Protocol

When the invoking agent receives a subagent return:

1. **Parse check:** Attempt to parse the return as JSON matching the expected tier schema.
2. **Field validation:** Verify all required fields are present and values are valid enums.
3. **Write permit check:** If Tier 2, verify `artifactPath` is within the permitted path for the write token.
4. **On failure — 1 retry:** Re-invoke the subagent with: `[SUBAGENT-MODE] Your previous return failed validation: <reason>. Return valid JSON per Tier <N> schema.`
5. **On second failure — raw output fallback:** Accept the subagent's raw text output, log a WARNING finding, and present the raw output to the user for manual interpretation.
