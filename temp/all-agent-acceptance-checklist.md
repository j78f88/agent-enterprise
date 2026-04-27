## Acceptance Checklist (Markdown)

Use this as a pass/fail gate for your all-agent delivery model.

### 1) Core Objectives

- [ ] Objective 1: Every code-touching agent receives simplicity doctrine at invocation  
  Pass criteria:
  - [ ] Each code-touching workflow includes a required doctrine reference in its invocation template
  - [ ] Invocation payloads include doctrine metadata or inherited policy block
  Evidence:
  - [ ] Invocation samples from all relevant agents
  - [ ] One negative test showing invocation fails if doctrine is missing

- [ ] Objective 2: Every project can tune strictness via config without editing skills  
  Pass criteria:
  - [ ] Strictness controls exist in config schema
  - [ ] Skill behavior changes when config values change, with no skill file edits
  Evidence:
  - [ ] Two config profiles (strict and relaxed)
  - [ ] Diff showing behavior change only from config swap

- [ ] Objective 3: Every implementation subagent sees active flags in prompt  
  Pass criteria:
  - [ ] Subagent prompt templates inject active strictness flags
  - [ ] Runtime logs/returns confirm flags were received
  Evidence:
  - [ ] Prompt render snapshots for at least 3 implementation tasks
  - [ ] One test proving stale or absent flags are rejected

- [ ] Objective 4: Reviewer treats simplicity violations as gateable findings  
  Pass criteria:
  - [ ] Reviewer taxonomy includes simplicity/surgical-edit violations
  - [ ] Violations map to severity with blocking semantics where defined
  Evidence:
  - [ ] Reviewer output with at least one simplicity violation
  - [ ] Gate decision trace showing block/defer behavior

- [ ] Objective 5: QA flags structural overengineering alongside functional failures  
  Pass criteria:
  - [ ] QA report has structural checks and functional checks as separate sections
  - [ ] Structural failures can fail or warn per policy
  Evidence:
  - [ ] QA report containing one structural and one functional finding
  - [ ] Policy mapping proving structural checks are enforceable

- [ ] Objective 6: Retros capture simplicity metrics for trend analysis  
  Pass criteria:
  - [ ] Retro schema includes structural quality metrics
  - [ ] Metrics are recorded across multiple runs and trendable
  Evidence:
  - [ ] At least 3 retro entries with the same metric set
  - [ ] Trend summary showing direction over time

---

### 2) Additional High-Value Objectives

- [ ] Objective 7: Deterministic failure classes  
  Pass criteria:
  - [ ] Every critical failure maps to a named class and terminal action
  - [ ] No raw fallback path bypasses contract enforcement in production mode

- [ ] Objective 8: Contract compatibility guarantees  
  Pass criteria:
  - [ ] Schema/version compatibility rules are defined
  - [ ] Upgrade path exists for older returns/prompts

- [ ] Objective 9: Autonomous checkpoint fallback policy  
  Pass criteria:
  - [ ] Interactive checkpoints have no-human defaults
  - [ ] Default decisions require rationale logging

- [ ] Objective 10: Drift detection and certification gates  
  Pass criteria:
  - [ ] Drift checks run on policy/schema/config surfaces
  - [ ] Certification gate blocks release on critical drift

- [ ] Objective 11: Policy precedence enforcement  
  Pass criteria:
  - [ ] One precedence order is documented and testable
  - [ ] Conflict cases resolve consistently to the same winner

- [ ] Objective 12: Traceability completeness  
  Pass criteria:
  - [ ] Each decision, override, and fallback links to policy + artifact
  - [ ] Audit trail is reconstructable end-to-end for a pilot run

---

### 3) Failure-Injection Validation Matrix

- [ ] Malformed subagent return triggers bounded retry then deterministic fail
- [ ] Unknown gate name triggers deterministic halt path
- [ ] Missing validation artifact triggers deterministic composition/planning outcome
- [ ] Unresolved token in generation triggers fail-fast behavior
- [ ] Ledger invariant violation is caught at write time
- [ ] Resume after interruption restores state without ambiguity

---

### 4) Exit Criteria (Go/No-Go)

- [ ] All Core Objectives (1-6) are passed
- [ ] At least 5 of 6 Additional Objectives (7-12) are passed
- [ ] All failure-injection tests passed
- [ ] One full-chain pilot completed with no manual rescue steps
- [ ] Audit package complete (invocations, reports, retros, decision traces)

Decision:
- [ ] GO (certified for maximum all-agent delivery)
- [ ] NO-GO (remediate failed checks and rerun)
