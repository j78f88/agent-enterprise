# All-Agent Delivery Detailed Plan

## 1. Executive Context

This plan is designed for a fully agent-delivered delivery model where human and agent effort are not optimization constraints. The optimization targets are:

- Maximum output quality
- Maximum structural robustness
- Maximum determinism and reproducibility
- Maximum governance consistency and auditability
- Maximum autonomous throughput without orchestration stalls

The current repository already has strong governance and role specialization, but audit findings identified reliability gaps that can degrade autonomous operation quality if not hardened first.

## 2. Source Context and Inputs

This plan is based on the current operating model and contract surfaces in:

- [skills/sprint-lead/SKILL.md](skills/sprint-lead/SKILL.md)
- [skills/planner/SKILL.md](skills/planner/SKILL.md)
- [skills/qa/SKILL.md](skills/qa/SKILL.md)
- [skills/reviewer/SKILL.md](skills/reviewer/SKILL.md)
- [skills/docs/SKILL.md](skills/docs/SKILL.md)
- [skills/bug/SKILL.md](skills/bug/SKILL.md)
- [instructions/configurable/backlog-ledger.instructions.md](instructions/configurable/backlog-ledger.instructions.md)
- [instructions/configurable/composition-rules.instructions.md](instructions/configurable/composition-rules.instructions.md)
- [instructions/configurable/validation-framework.instructions.md](instructions/configurable/validation-framework.instructions.md)
- [instructions/configurable/severity-levels.instructions.md](instructions/configurable/severity-levels.instructions.md)
- [instructions/configurable/sprint-docs-format.instructions.md](instructions/configurable/sprint-docs-format.instructions.md)
- [instructions/configurable/engagement-gates.instructions.md](instructions/configurable/engagement-gates.instructions.md)
- [instructions/configurable/engagement-format.instructions.md](instructions/configurable/engagement-format.instructions.md)
- [instructions/generic/subagent-return-schemas.instructions.md](instructions/generic/subagent-return-schemas.instructions.md)
- [init.py](init.py)
- [project.config.example.yml](project.config.example.yml)
- [ONBOARDING.md](ONBOARDING.md)
- [README.md](README.md)

## 3. Key Findings Driving This Plan

The major plan drivers are:

- Determinism gaps in protocol fallback behavior and retry loops
- Cross-file policy inconsistencies in validation paths and severity semantics
- Missing bounded terminal behavior for some autonomous failure states
- Setup/compiler pipeline allows warning-only unresolved generation states
- Need to explicitly bind simplicity principles into enforceable quality gates

## 4. Strategic Outcome Objectives

The plan must satisfy all of the following:

- Every code-touching agent receives simplicity doctrine at invocation
- Every project can tune strictness via config without editing skills
- Every implementation subagent sees the active flags in its prompt
- Reviewer treats simplicity violations as gateable findings
- QA can flag structural overengineering alongside functional failures
- Retros capture simplicity metrics for trend analysis

Additional high-value objectives:

- Deterministic failure classes and terminal states
- Canonical policy precedence and conflict resolution
- Reproducible generated outputs across repeated runs
- Autonomous fallback behavior for interaction checkpoints
- Full traceability of decisions, overrides, and escalations

## 5. Delivery Architecture Model

### 5.1 Control Plane and Data Plane

Control plane:

- Configurable instructions define governance policy and constraints
- Generic instructions define shared protocol contracts
- Configuration and init pipeline compile final runtime contracts

Data plane:

- Skills execute role-specialized workflows and agent behavior
- Orchestrator skills delegate, collect returns, and enforce quality gates

### 5.2 Policy Precedence

When conflicts occur, policy precedence should be enforced as:

1. Protocol contracts in generic instructions
2. Governance contracts in configurable instructions
3. Skill-local constraints
4. Prompt-local workflow text

This precedence order should be codified and test-validated.

## 6. Phased Execution Plan

## Phase 0: Baseline and Traceability Foundation

Goal:

Establish stable before-state references and conflict resolution foundations.

Actions:

- Capture a baseline manifest of critical contract files and their hashes
- Define canonical policy precedence in governance instructions
- Establish a change classification matrix for contract updates

Outputs:

- Baseline contract inventory
- Conflict precedence section in policy layer
- Change impact rubric for future modifications

Acceptance:

- All critical policy files mapped and hash-tracked
- Precedence rule documented and reference-linked in dependent surfaces

## Phase 1: Protocol Determinism Hardening

Goal:

Eliminate ambiguous protocol outcomes and unbounded loop behavior.

Actions:

- Replace permissive raw-output fallback in subagent schema handling with bounded retries and deterministic fail states
- Add explicit bounded retry cap and terminal failure behavior in sprint orchestration repair loops
- Define unknown input behavior for unknown gates, malformed references, and missing artifacts

Outputs:

- Deterministic protocol fallback policy
- Bounded loop policy for orchestration safety nets
- Unknown input error-class policy table

Acceptance:

- No protocol pathway returns unstructured fallback in strict mode
- All retry loops terminate via success or explicit failure class

## Phase 2: Governance Normalization

Goal:

Unify governance semantics across planning, triage, composition, and execution.

Actions:

- Build canonical severity mapping matrix across bug triage axis, gate severity axis, and composition tiers
- Canonicalize validation record location and lookup behavior
- Normalize escalation state-machine behavior across planner, composition, and ledger contracts

Outputs:

- Severity conversion matrix
- Single validation path contract
- Canonical escalation state machine

Acceptance:

- No contradictory path or severity logic across configurable instructions
- Planner and composition behavior align with normalized rules

## Phase 3: Ledger and Policy Integrity Enforcement

Goal:

Prevent silent governance drift and preserve high-trust audit history.

Actions:

- Add write-time invariant checks for ledger operations
- Enforce atomic update rules for detail-store plus ledger pair operations
- Add stale-state and immutable section validation for seeded forecast artifacts

Outputs:

- Invariant validation checkpoints
- Atomic update policy
- Immutable forecast enforcement rules

Acceptance:

- Every ledger-affecting write validates invariants before completion
- No partially applied state transitions in coupled artifacts

## Phase 4: Setup and Generation Pipeline Hardening

Goal:

Make contract compilation strict, reproducible, and safe by default.

Actions:

- Make unresolved placeholder generation fail by default
- Add preflight validator for required directories, required keys, and command topology
- Add deterministic output validation with checksum and run equivalence checks
- Clarify bootstrap/operator model in onboarding docs

Outputs:

- Strict generation behavior
- Preflight validation report
- Reproducibility verification artifact

Acceptance:

- Identical input yields byte-identical resolved output
- Missing required config causes fail-fast with actionable diagnostics

## Phase 5: Full-Autonomy Orchestration Optimization

Goal:

Ensure all-agent operation can run end-to-end without stall-prone interaction dependencies.

Actions:

- Add policy-driven autonomous fallback for checkpoint decisions
- Add durable state persistence for resume-safe orchestration
- Define deterministic optional-gate branch policy from plan signals

Outputs:

- Autonomous checkpoint policy
- Orchestration state persistence contract
- Gate branch determinism rules

Acceptance:

- No workflow hard-stalls due to unavailable human input
- Resume behavior restores prior state without ambiguity

## Phase 6: Simplicity Doctrine and Structural Excellence Overlay

Goal:

Enforce high-quality code shape without reducing governance rigor.

Actions:

- Add shared simplicity/surgical-edit doctrine as cross-cutting instruction
- Add config-driven strictness flags in configuration schema
- Inject active strictness flags into implementation subagent prompts
- Add reviewer gateable findings for simplicity doctrine violations
- Add QA structural overengineering checks alongside functional checks
- Add retro metrics for structural trend analysis

Outputs:

- Simplicity doctrine contract
- Config strictness controls
- Prompt flag injection behavior
- Reviewer and QA enforcement extensions
- Retro structural metrics schema

Acceptance:

- All six strategic outcome objectives pass objective-level checks
- Doctrine is enforceable, not advisory

## Phase 7: Pilot, Failure Injection, and Certification

Goal:

Certify readiness under real autonomous execution and synthetic failure stress.

Actions:

- Run one full-chain pilot with all role agents
- Execute failure injection matrix: malformed return, unresolved token, unknown gate, missing validation artifact, ledger mismatch, interrupted resume
- Validate deterministic outcomes and traceability completeness

Outputs:

- Pilot run report
- Failure injection result matrix
- Certification decision package

Acceptance:

- All mandatory objective checks pass
- All critical failure classes terminate deterministically
- Certification marked GO

## 7. Agent Utilization Model (Maximum Best Use)

## 7.1 Role Allocation by Lifecycle Stage

Shaping and decision quality:

- pm validates feature value and risk assumptions
- researcher provides evidence-backed external pattern synthesis
- architect formalizes design choices and tradeoffs

Planning and governance:

- planner composes execution plans and governs backlog integration
- bug captures and normalizes issue intake

Execution and quality enforcement:

- sprint-lead orchestrates sequencing, delegation, and gate handling
- qa executes functional and structural quality validation
- reviewer enforces code quality and doctrine compliance
- a11y and perf enforce specialized quality axes

Documentation and audit closure:

- docs synchronizes lifecycle and operational artifacts

## 7.2 Why This Is Maximum Utilization

- Every specialized agent is used only for its highest-value domain
- Coordination complexity is offloaded to deterministic protocol contracts
- Quality control is multi-layered, independent, and auditable
- Human interaction becomes optional policy input, not runtime dependency

## 8. Detailed Benefits Map

## 8.1 Quality Benefits

- Higher implementation quality through doctrine-enforced minimalism
- Lower defect escape through strict protocol boundaries
- Better structural consistency through reviewer and QA doctrine checks

## 8.2 Robustness Benefits

- Reduced orchestration deadlocks through bounded retries
- Predictable behavior under failure through deterministic terminal states
- Stable cross-agent semantics through policy normalization

## 8.3 Audit and Governance Benefits

- Trustworthy history through invariant-checked ledger operations
- Clear escalation rationale through normalized state-machine behavior
- Better compliance evidence through explicit traceability contracts

## 8.4 Autonomous Throughput Benefits

- Fewer pauses from unavailable human approvals
- Resume-safe long-running execution
- More reliable multi-agent parallelism due to strict contracts

## 9. Risks and Mitigations

Risk: Increased strictness may reject outputs more often initially.
Mitigation: Use staged rollout with certification profile and diagnostics-first feedback.

Risk: Policy normalization may require refactoring across multiple instructions.
Mitigation: Implement with explicit compatibility windows and mapping adapters.

Risk: Strict generation could block teams with incomplete configs.
Mitigation: Provide preflight diagnostics and clear required/optional key classes.

## 10. Dependency and Sequencing Summary

Critical dependency chain:

- Phase 1 must complete before Phase 5
- Phase 2 must complete before Phase 3 finalization
- Phase 4 must complete before certification
- Phase 6 overlays should be activated after core determinism controls are stable

Recommended order:

- Phase 0 to Phase 4 first
- Phase 5 and Phase 6 next
- Phase 7 certification last

## 11. Verification and Certification Matrix

Mandatory checks:

- Protocol determinism checks
- Retry termination checks
- Governance consistency checks
- Validation path coherence checks
- Ledger invariant checks
- Setup strictness and reproducibility checks
- Objective checks for simplicity doctrine integration
- End-to-end pilot and failure injection checks

Certification rule:

- GO only if all core objective checks and all critical failure-class tests pass

## 12. Definition of Done

This plan is complete only when:

- All lifecycle stages run in agent-only mode under strict policy
- Deterministic behavior is validated for nominal and failure scenarios
- Governance semantics are normalized and contradiction-free
- Simplicity doctrine is enforced in reviewer and QA, with retro trend metrics
- Certification package supports clear GO decision for default all-agent rollout
