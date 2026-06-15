# Validation: Process controls & human oversight (Cluster 6)

**Date:** 2026-06-15
**Validator:** `@pm` (subagent mode, `[WRITE:VALIDATION]`)
**Source research:** `docs/planning/research/process-controls-human-oversight-research.md`
**Framework:** `.github/instructions/validation-framework.instructions.md` (5-test echo-chamber filter)

---

## Chosen frame and rationale

**Frame: MIXED, dominated by "already-implemented capability."**

This is the critical call for this cluster, so it is stated up front. Per the
2026-06-01 reposition, agent-enterprise is **not** a novel safety substrate; it is
an Australian-government compliance template (proposal-tier). Cluster 6's six
patterns are therefore evaluated against two questions, never "is it novel?":

1. **Does agent-enterprise already implement this?** If yes, the validation
   output is "document the existing capability" — there is no feature to build
   and no analogy-driven recommendation to test. The 5-test framework still runs
   (it surfaces whether the existing mechanism is *load-bearing* or ceremonial),
   but the label reflects implementation reality.
2. **If not already built, should the AU-gov compliance template merely
   *reference/map* this as an external control, or genuinely *build* it?**

Grounding checked in-repo before labelling:

- **Three-tier returns** — fully implemented. `schemas/subagent-return-tier{1,2,3}.schema.json`,
  `.github/instructions/subagent-return-schemas.instructions.md`, and the Mode 2
  dispatcher's evidence check (`docs/ORCHESTRATION.md` "Verified results: no ghost-done",
  point 2) all enforce it. The research's `pattern-three-tier-returns` is literally this repo's design.
- **Thin / deterministic orchestration** — implemented. `src/mode2_dispatcher/`,
  `dispatch.py`, `docs/ORCHESTRATION.md`: deterministic queue, contract-frozen state
  machine (`queued → in-progress → done|rejected|failed`), control flow in code not
  model, crash recovery via journaled state. This *is* `pattern-thin-orchestration`.
- **Schema-gated build** — implemented, but a narrower form than the research describes.
  `init.py` validates frontmatter/callables against `schemas/*.json` and exits non-zero
  on violation (build-config gating). The research's pattern is *LLM constrained decoding*
  (token-masking at inference). These are the same *idea* (valid-by-construction gate)
  applied to two different layers — see Pattern 5.
- **Deterministic out-of-band hooks** — partial. The repo has build gates (`init.py`
  exit-non-zero), Mode 2 verifier hooks, and a `hooks/` VS Code session-freshness hook.
  It does **not** ship Claude Code-style PreToolUse/PostToolUse model-override hooks —
  those belong to the harness the template *runs on*, not the template itself.
- **Context-serialization handoff** — partial / adjacent. Tier-2/3 return summaries and
  `docs/archive/e1-fix-reconciliation-handoff.md` show the serialize-state-across-a-boundary
  posture, but compaction-vs-handoff is explicitly Cluster 7 territory (context management).
- **Human checkpoints / approval gates** — partial. The `flaggedDecisions` field and
  `status: needs-input` are the checkpoint primitive; the whole `@pm → @planner → human`
  gate ladder is a checkpoint regime. But Mode 2 is by design "without continuous human
  supervision," so a *runtime* approval-gate-on-sensitive-action is not built.

Net: this cluster is mostly a mirror of mechanisms the repo already has. The PM job
here is to prevent these from being re-scoped as "new substrate features" (which would
violate the reposition), and to route the genuinely-external ones (constrained decoding,
runtime approval gates) to the right home — a compliance-control *mapping*, not a build.

---

## Pattern 1 — Human checkpoints / approval gates (interrupt-and-resume)

**Implementation status:** Partially implemented. `flaggedDecisions` + `status:needs-input`
in the return schemas, and the `@pm`/`@planner`/human handoff ladder, are checkpoint
mechanisms. Runtime interrupt-and-resume on a *sensitive action mid-run* is not (Mode 2
runs unsupervised by design).

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | The checkpoint is genuinely *why* the supervised-handoff model works — `flaggedDecisions` is the load-bearing gate that stops a subagent from acting on an unconfirmed decision, not incidental ceremony. For an AU-gov compliance posture, a human decision point on sensitive actions is the substantive control, not a proxy for one. |
| 2. Frequency match | PASS | agent-enterprise is project/sprint-scoped (low cadence), which is the *correct* cadence for human checkpoints — the failure mode (approval fatigue) is a high-frequency problem. Low-frequency use is exactly where this pattern is safe. |
| 3. Survivorship bias | FAIL | The research documents the dominant failure of shipped approval gates: 93% blind-approval, "73 prompts in a morning → #68 incident." Apps that bolted on per-action runtime approval gates produced rubber-stamping, not safety. Importing a *runtime* approval gate would import the failure. |
| 4. Anti-pattern / engagement-at-cost | PASS (for the built form) | The repo's checkpoint drives real value (a human actually decides at handoff) rather than manufacturing approval clicks. A *runtime* per-action gate would fail this test — it generates approvals without proportional value. |
| 5. Complexity cost | PASS (for the built form) | The existing `flaggedDecisions`/handoff checkpoint is near-zero added cost. A durable interrupt-and-resume runtime (checkpointers, persistent state) is high cost for a proposal-tier template and unjustified. |

**Label: REFRAMED**

- **Original (from research):** "Add runtime interrupt-and-resume human approval gates on sensitive actions (LangGraph `interrupt()` / OpenAI `needs_approval` style)."
- **Reframe that rescues it:** "Validate as an *already-implemented documented capability*: agent-enterprise's batch-level, decision-point checkpoints (`flaggedDecisions`, `needs-input`, the `@pm→@planner→human` handoff ladder) are the AU-gov-appropriate form of human oversight. Map them to the relevant oversight control; do **not** build a per-action runtime gate."
- **Why the reframe rescues it:** Test 3 fails only for the *runtime per-action* version. Restating the feature as the batch/decision-point form the repo already has — which the research itself endorses as the fatigue mitigation ("batching to PR-level review") — passes all five.

---

## Pattern 2 — Deterministic out-of-band hooks that enforce workflow constraints

**Implementation status:** Partial. Build-time gates (`init.py` exit-non-zero), Mode 2
verifier hooks, and a `hooks/` session-freshness hook exist. Claude Code-style
PreToolUse/PostToolUse model-override hooks are a property of the *host harness*, not the template.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Deterministic enforcement (code, not model, decides) is the actual mechanism the reposition rests on — "build-time defense" per project memory. It is causally why a gate cannot be talked around by the model. |
| 2. Frequency match | PASS | Build/commit-time gates fire at the project's natural cadence (per build, per sprint), matching agent-enterprise's frequency rather than warping it. |
| 3. Survivorship bias | FAIL | The research is blunt: client-side hooks are bypassed in the wild (`--no-verify`, `disableAllHooks` overriding *managed org* hooks, "six consecutive commits" bypassing deny rules). Shipping client-side hooks as the safety claim is the survivorship trap — the bypassed ones are invisible until the incident. |
| 4. Anti-pattern / engagement-at-cost | PASS | Deterministic gates create real value (blocked unsafe action), not vanity activity. N/A risk of engagement-gaming. |
| 5. Complexity cost | PASS | The repo already pays this cost via `init.py` validation and Mode 2 verifiers; documenting/mapping it is cheap. Adding harness-level model-override hooks would be out of scope (not the template's layer). |

**Label: REFRAMED**

- **Original (from research):** "Adopt deterministic out-of-band hooks (Claude Code PreToolUse/PostToolUse/Stop, OPA/Rego PEP) as the enforcement layer."
- **Reframe that rescues it:** "Validate the *server-side / CI re-run* form as the documented control, and map client-side hooks as *advisory only*. The repo's own posture already matches the research's consensus mitigation: 'client-side enforcement is fundamentally insufficient; re-run the same checks server-side/in CI — the agent cannot pass `--no-verify` to CI.' For AU-gov mapping, the enforceable control is the CI/build gate (`init.py`, conformance tests), not the client hook."
- **Why the reframe rescues it:** Test 3 fails only for *client-side* hooks taken as enforcement. Restating the control as CI/build-time enforcement (which the repo has and which is unbypassable by the agent) passes all five. This mirrors Cluster 1's "instructed vs. enforced" finding.

---

## Pattern 3 — Context-serialization handoff (vs. in-place compaction)

**Implementation status:** Partial / adjacent. Return-summary serialization and
`e1-fix-reconciliation-handoff.md` show the posture; compaction-vs-handoff mechanics
are Cluster 7 (context management) territory.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Explicit state serialization at boundaries is causally why handoffs don't silently lose context — the research shows lossy compaction directly degrades accuracy ("recursive summaries distort earlier reasoning"). |
| 2. Frequency match | N/A | This is a within-run mechanism whose cadence is set by context-window pressure, not by product usage frequency; the frequency-match test does not apply to a sub-run infrastructure concern. |
| 3. Survivorship bias | PASS | The research surfaces the failed alternative (compaction) and the survivor (handoff: "Amp retired compaction"), so the evidence is not survivorship-blind — the losing approach is named. |
| 4. Anti-pattern / engagement-at-cost | N/A | No engagement dimension — this is plumbing, not a user-facing feature that could game sessions. |
| 5. Complexity cost | FAIL | Building a full handoff/serialization subsystem (curated carry-forward, checkpointers) is meaningful infrastructure cost for a proposal-tier compliance template, and the research itself flags it as Cluster 7's unresolved territory (no technique is both automatic and lossless). Scope/dependency-blocked, not value-justified here. |

**Label: DEFERRED**

- **Unblock condition:** Resolve as part of the **Cluster 7 (context management)** validation, where compaction-vs-handoff is the primary subject. Re-validate only if/when context-loss is identified as a concrete failure in agent-enterprise's own runs, *and* a host-harness mechanism isn't already covering it. Until then, the repo's existing return-summary serialization is sufficient and needs no new build.

---

## Pattern 4 — Tiered / structured returns to an orchestrator

**Implementation status:** **FULLY IMPLEMENTED.** This pattern *is* agent-enterprise's
return protocol: `schemas/subagent-return-tier{1,2,3}.schema.json`,
`.github/instructions/subagent-return-schemas.instructions.md` (summary + artifactPath +
status + `flaggedDecisions`/`blockerReason` escalation + 1-retry-then-fallback validation),
and the Mode 2 dispatcher's tier-validation evidence check.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | The structured return is causally why the orchestrator can act on a subagent result deterministically (parse → validate → permit-check) instead of guessing — it is the load-bearing interface, not decoration. The research's escalation-not-hallucinate point maps directly to the repo's `status:blocked`/`blockerReason`/`needs-input`. |
| 2. Frequency match | PASS | Fires once per subagent invocation at the sprint/handoff cadence — matches the project-scoped frequency exactly. |
| 3. Survivorship bias | PASS | The research names the failure modes the repo already guards against — over-tight schemas (the repo keeps returns small and human-readable) and over-wide fan-out (the repo's hierarchy is shallow). No invisible failed cohort being copied. |
| 4. Anti-pattern / engagement-at-cost | PASS | Drives real value (verifiable handoff, no ghost-done) with no engagement-gaming surface. |
| 5. Complexity cost | PASS | Already built and tested (`tests/test_mode2_dispatcher.py`, `tests/test_protocol_v1_conformance.py`); marginal cost to document/map is near zero. |

**Label: VALIDATED** (as already-implemented capability)

> This is the clearest "already built — validate as documented capability" case in the
> cluster. No build. Action is to ensure the AU-gov compliance mapping *references* the
> existing three-tier return protocol as the project's structured-handoff control. The
> research's `pattern-three-tier-returns` and Anthropic "90.2%" eval are external
> corroboration, not a new feature.

---

## Pattern 5 — Schema-gated build (constrained / structured output as a gate)

**Implementation status:** Split. The *build-config* form is implemented (`init.py`
validates frontmatter/callable manifests against `schemas/*.json`, exits non-zero —
valid-by-construction config gate). The *LLM constrained-decoding* form (token-masking at
inference, JSON-schema grammars) is **not** in the repo and is a host-model concern.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS (build form) | The schema gate in `init.py` is causally why malformed substrate config cannot ship — it is the actual enforcement, not a correlate of quality. |
| 2. Frequency match | PASS (build form) | Runs every build; matches project cadence. |
| 3. Survivorship bias | FAIL (decoding form) | The research documents the failed cohort for *constrained decoding*: 10–30% reasoning degradation, Hermes-4-405B 92.5%→35.0% under constrained JSON. Importing constrained-decoding-as-a-gate would import a documented quality regression — the "constrain the wire format, never the thinking" caveat exists precisely because naive adopters were burned. |
| 4. Anti-pattern / engagement-at-cost | N/A | No engagement dimension. |
| 5. Complexity cost | FAIL (decoding form) | Constrained-decoding infrastructure (grammar compilation, token masking) is squarely a model-inference-layer concern, not something a proposal-tier compliance template should build or own. High cost, wrong layer. |

**Label: REFRAMED**

- **Original (from research):** "Adopt schema-gated build via LLM constrained decoding (Structured Outputs / Outlines / XGrammar) as a gate between steps."
- **Reframe that rescues it:** "Validate the *build-time schema-validation* form as an already-implemented capability — `init.py`'s JSON-schema gate on frontmatter and callables is the project's valid-by-construction gate and is the right layer for a compliance template. Treat LLM constrained decoding as an *external/host-model control to map, with the reasoning-degradation caveat noted*, not a feature to build."
- **Why the reframe rescues it:** Tests 3 and 5 fail only for the inference-layer decoding form. The repo's build-config schema gate (same valid-by-construction *idea*, different layer) passes all applicable tests and already exists.

---

## Pattern 6 — Thin / deterministic orchestration ("code not model for control flow")

**Implementation status:** **FULLY IMPLEMENTED.** `src/mode2_dispatcher/` + `dispatch.py` +
`docs/ORCHESTRATION.md`: deterministic queue, contract-frozen state machine, control flow
in code (zero-LLM for routing), journaled crash recovery, no-ghost-done evidence gate.
This is `pattern-thin-orchestration` realised.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Deterministic, code-driven control flow is causally why Mode 2 is auditable and crash-recoverable — exactly the property an AU-gov compliance posture needs (predictable, replayable, no model in the control path). |
| 2. Frequency match | PASS | Dispatcher runs per work-queue drain at project cadence; no frequency mismatch. |
| 3. Survivorship bias | PASS | The research names the failure of *over-rigid* orchestration (can't handle open-ended tasks). The repo's design already concedes this by being explicitly batch/queue-scoped (Mode 2) rather than claiming to orchestrate open-ended autonomy — it is not over-fitting to the winning-app surface. |
| 4. Anti-pattern / engagement-at-cost | PASS | Drives real value (durable, verified execution); no engagement surface. |
| 5. Complexity cost | PASS | Already built, contract-frozen, and dual-implementation-tested. Documenting/mapping is cheap; the over-rigidity risk is bounded because the repo scopes this to divisible work, not open-ended tasks. |

**Label: VALIDATED** (as already-implemented capability)

> Second clear "already built" case. No build. Action: ensure the AU-gov compliance
> mapping references Mode 2 deterministic orchestration as the project's control-flow
> assurance control. Anthropic *Building Effective Agents* and Temporal/Conductor are
> external corroboration of the design choice, not new candidates.

---

## Summary of labels

| Pattern | Implementation status | Label |
| --- | --- | --- |
| 1. Human checkpoints / approval gates | Partial (batch checkpoints yes; runtime per-action no) | REFRAMED |
| 2. Deterministic out-of-band hooks | Partial (CI/build gates yes; client hooks advisory) | REFRAMED |
| 3. Context-serialization handoff | Partial / Cluster-7 adjacent | DEFERRED |
| 4. Tiered / structured returns | Fully implemented | VALIDATED (documented capability) |
| 5. Schema-gated build | Build form yes; decoding form no | REFRAMED |
| 6. Thin / deterministic orchestration | Fully implemented | VALIDATED (documented capability) |

**Bottom line:** No pattern in this cluster is a new substrate feature to build. Four are
already realised in the repo (Patterns 4 and 6 fully; the build-config halves of 2 and 5);
the reframes route the externally-failing forms (runtime approval gates, client-side hooks,
constrained decoding) to *compliance-control mapping with caveats* rather than implementation;
one (handoff) is deferred to the Cluster 7 context-management validation. This is consistent
with the 2026-06-01 reposition: agent-enterprise references/maps these as controls; it does
not re-claim them as novel mechanisms.
