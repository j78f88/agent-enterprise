---
id: instruction.engagement-gates
kind: instruction
version: 1.0.0
applies_to: '**'
description: Use when running engagement gates, checking scope upgrade thresholds,
  building subagent prompts for validation or planning, or determining deployment
  workflow details. Defines Gate 1-4 criteria, scope upgrade rules, and platform configuration.
applyTo: '**'
paths:
- '**'
---

# Engagement Gates

Gate definitions, subagent prompt templates, scope upgrade thresholds, and platform configuration for the @sprint-lead engagement lifecycle.

## Gate Definitions

### Gate 1 — Requirements Validation

**Trigger:** After validation subagent completes (M/L size). Skipped for S-size.

**What to check:**
- Validation subagent verdict (PASS / CONDITIONAL / FAIL)
- Conflicts with docs/NON_GOALS.md, docs/planning/ROADMAP.md, docs/decisions/DECISIONS.md
- Risk assessment

**Present to CTO:**
- Verdict with rationale
- Identified risks and conflicts
- Recommendation

**Decision options:** Approve / Revise brief / Reject / Override

### Gate 2 — Plan Approval

**Trigger:** After planning subagent produces draft PLAN.md.

**What to check:**
- Task list completeness and clarity
- Quality gates defined
- Acceptance criteria mapped to brief
- Compliance with planning-preflight checks

**Present to CTO:**
- Full draft plan in conversation
- Planning subagent's risk assessment
- Compliance issues (if any)

**Decision options:** Approve / Revise / Reject / Split into smaller sprints

### Gate 3 — Test Deployment

**Trigger:** After @sprint-lead completes and test deployment workflow finishes.

**What to check:**
- Test deployment workflow status (via `gh` CLI)
- Automated test results from workflow summary
- Test environment URL accessibility

**Present to CTO:**
- Deployment status (success/failure)
- Automated test pass/fail count
- Test environment URL for manual verification

**Decision options:** Approve for production / Request fixes / Abort

### Gate 4 — Production

**Trigger:** After merge to main and production deployment workflow finishes.

**What to check:**
- Production deployment workflow status
- Automated smoke test results
- Production URL accessibility

**Present to CTO:**
- Deployment status
- Smoke test results
- Production URL

**Decision options:** Confirm / Rollback / Hold

---

## Scope Upgrade Thresholds

These thresholds trigger a scope upgrade prompt when an S-size engagement's planning subagent returns values exceeding them. @sprint-lead reads these values at runtime — tune by editing this section, zero agent changes needed.

```
taskCount > 3
filesAffected > 8
multiStore: true    # touches >1 store factory
multiArea: true     # touches >2 top-level directories (apps/, packages/, docs/)
```

When triggered, @sprint-lead presents: "This looks bigger than S-size. Upgrade to M (adds requirements validation) or continue as S?"

- Upgrade to M: run Phase 2 (validation) before continuing. Log in gate-log.
- Continue as S: CTO override, logged as `SIZE-OVERRIDE` in gate-log.

**Calibration:** Review SIZE-OVERRIDE entries in gate-logs after 5-10 engagements. If overrides are frequent, raise thresholds. If scope creep is common, lower them.

---

## Subagent Prompt Templates

### Validation Subagent (Phase 2)

```
Read `docs/planning/engagements/{engagement}/brief.md` and
`.github/instructions/validation-framework.instructions.md`.

Apply the 5-test validation framework against the brief.

Also read:
- docs/NON_GOALS.md — check for scope conflicts
- docs/planning/ROADMAP.md — check for roadmap alignment
- docs/decisions/DECISIONS.md — check for ADR conflicts

Write a validation record to `docs/planning/engagements/{engagement}/validation.md`.

Return a JSON summary:
{
  "verdict": "PASS|CONDITIONAL|FAIL",
  "risks": ["..."],
  "conflicts": ["..."],
  "recommendation": "..."
}
```

### Planning Subagent (Phase 3)

```
Read `docs/planning/engagements/{engagement}/brief.md` and the validation
record at `docs/planning/engagements/{engagement}/validation.md` (if it exists).

Read:
- .github/instructions/planning-compliance.instructions.md
- .github/instructions/planning-preflight.instructions.md

Explore the codebase for patterns to reuse relevant to the brief's scope.
Run pre-flight checks (docs/TECHNICAL_DEBT.md, docs/decisions/DECISIONS.md, docs/decisions/FUTURE_CONSIDERATIONS.md, docs/NON_GOALS.md).

Write a draft PLAN.md with tasks, files to modify, quality gates, and
acceptance criteria. Follow the format in docs/templates/SPRINT_PLAN_TEMPLATE.md.

Return a JSON summary:
{
  "sprintNumber": N,
  "taskCount": N,
  "filesAffected": N,
  "risks": ["..."],
  "complianceIssues": ["..."]
}
```

---

## Platform Configuration

Gate definitions above reference "the platform's deployment workflow" and "automated test suite" generically. This section maps to concrete values per platform.

### Web

- **Test deploy workflow:** `ci.yml`
- **Production deploy workflow:** `deploy-azure-swa.yml` (Python CI)
- **Automated test suite:** Playwright E2E (chromium + iPhone 14 viewport)
- **Test environment URL:** Azure SWA test instance URL from workflow output
- **Production URL:** `https://gray-glacier-029377c00.7.azurestaticapps.net`
- **CI workflow:** `ci.yml`
- **Deploy check commands:**
  ```bash
  # Test deployment
  gh run list --branch develop --workflow ci.yml --limit 3 --json databaseId,status,conclusion
  # Production deployment
  gh run list --branch main --workflow "Python CI" --limit 2 --json databaseId,status,conclusion
  # Failure details
  gh run view <run-id> --log-failed | tail -50
  ```

### Mobile (future)

- TBD — add when mobile enters engagement model
- Same gate structure, different workflow names and test runner
