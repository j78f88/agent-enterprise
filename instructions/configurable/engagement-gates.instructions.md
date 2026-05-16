---
id: instruction.engagement-gates
kind: instruction
version: 1.0.0
applies_to: '**'
description: Use when running engagement gates, checking scope upgrade thresholds, building subagent prompts for validation or planning, or determining deployment workflow details. Defines Gate 1-4 criteria, scope upgrade rules, and platform configuration.
applyTo: .github/agents/delivery-lead.agent.md
---

# Engagement Gates

Gate definitions, subagent prompt templates, scope upgrade thresholds, and platform configuration for the @delivery-lead engagement lifecycle.

## Gate Definitions

### Gate 1 — Requirements Validation

**Trigger:** After validation subagent completes (M/L size). Skipped for S-size.

**What to check:**
- Validation subagent verdict (PASS / CONDITIONAL / FAIL)
- Conflicts with {{paths.non_goals}}, {{paths.roadmap}}, {{paths.decisions}}
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

**Trigger:** After merge to {{git.main_branch}} and production deployment workflow finishes.

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

These thresholds trigger a scope upgrade prompt when an S-size engagement's planning subagent returns values exceeding them. @delivery-lead reads these values at runtime — tune by editing this section, zero agent changes needed.

```
taskCount > {{scope_upgrade.task_count}}
filesAffected > {{scope_upgrade.files_affected}}
multiStore: true    # touches >1 store factory
multiArea: true     # touches >2 top-level directories (apps/, packages/, docs/)
```

When triggered, @delivery-lead presents: "This looks bigger than S-size. Upgrade to M (adds requirements validation) or continue as S?"

- Upgrade to M: run Phase 2 (validation) before continuing. Log in gate-log.
- Continue as S: CTO override, logged as `SIZE-OVERRIDE` in gate-log.

**Calibration:** Review SIZE-OVERRIDE entries in gate-logs after 5-10 engagements. If overrides are frequent, raise thresholds. If scope creep is common, lower them.

---

## Subagent Prompt Templates

### Validation Subagent (Phase 2)

```
Read `{{paths.engagements}}{engagement}/brief.md` and
`{{paths.instructions_dir}}/validation-framework.instructions.md`.

Apply the 5-test validation framework against the brief.

Also read:
- {{paths.non_goals}} — check for scope conflicts
- {{paths.roadmap}} — check for roadmap alignment
- {{paths.decisions}} — check for ADR conflicts

Write a validation record to `{{paths.engagements}}{engagement}/validation.md`.

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
Read `{{paths.engagements}}{engagement}/brief.md` and the validation
record at `{{paths.engagements}}{engagement}/validation.md` (if it exists).

Read:
- {{paths.instructions_dir}}/planning-compliance.instructions.md
- {{paths.instructions_dir}}/planning-preflight.instructions.md

Explore the codebase for patterns to reuse relevant to the brief's scope.
Run pre-flight checks ({{paths.technical_debt}}, {{paths.decisions}}, {{paths.future_considerations}}, {{paths.non_goals}}).

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

- **Test deploy workflow:** `{{platform.test_workflow}}`
- **Production deploy workflow:** `deploy-azure-swa.yml` ({{platform.ci_workflow_display_name}})
- **Automated test suite:** Playwright E2E (chromium + iPhone 14 viewport)
- **Test environment URL:** Azure SWA test instance URL from workflow output
- **Production URL:** `https://gray-glacier-029377c00.7.azurestaticapps.net`
- **CI workflow:** `ci.yml`
- **Deploy check commands:**
  ```bash
  # Test deployment
  gh run list --branch {{git.develop_branch}} --workflow {{platform.test_workflow}} --limit 3 --json databaseId,status,conclusion
  # Production deployment
  gh run list --branch {{git.main_branch}} --workflow "{{platform.ci_workflow_display_name}}" --limit 2 --json databaseId,status,conclusion
  # Failure details
  gh run view <run-id> --log-failed | tail -50
  ```

### Mobile (future)

- TBD — add when mobile enters engagement model
- Same gate structure, different workflow names and test runner
