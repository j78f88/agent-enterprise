# Validation: Evidence & verification gating (Cluster 4)

**Date:** 2026-06-15
**Validator:** `@pm`
**Source research:** `docs/planning/research/evidence-verification-gating-research.md`
**Framework:** `.github/instructions/validation-framework.instructions.md` (5-test echo-chamber filter)
**Status:** proposal-tier — agent-enterprise repositioned 2026-06-01 to an AU-government compliance template; nothing here is canonical until the owner ratifies.

---

## Frame chosen: MIXED, weighted toward (a) "control to reference/map"

For this cluster, **four of the five patterns are validated as controls the AU-gov compliance template should reference/map to (frame a), and one carries a narrow, rescuable build component (frame c) scoped strictly to the residual-defensible artifact** (the unified fail-closed build pipeline + the verification-evidence channel around it).

**Why this frame, not "novel substrate to build":**

1. **The reposition forbids the default.** The 2026-06-01 research run disconfirmed agent-enterprise's two "novel substrate" claims. The residual defensible value is (i) the *unified* fail-closed build pipeline + nonce data-fence and (ii) a *reusable AU-gov compliance template*. Cluster 4's patterns are evidence/verification mechanisms — they sit closest to (ii), and only one of them touches (i).

2. **Every pattern in the research is already commoditized and first-party.** Executable verification loops ship in Claude Code Stop hooks + SWE-bench; evidence-by-design is Anthropic best-practice guidance + the bundled `/code-review` skill; grounding ships as the Citations API (GA on two clouds); generator-verifier ships as CriticGPT + reviewer subagents; behavioral evals are an $800M-valuation funded market (Braintrust, promptfoo, Inspect AI). Re-building any of these as a "feature" would fail the complexity-cost test on day one — the market has already paid the cost.

3. **The template, not the substrate, is where these patterns create defensible value for this project.** An AU-government assurance template needs to *cite recognised verification controls and their documented failure modes* so a gov reader can map them to ISM / Essential Eight / AI assurance expectations. The research already supplies exactly that: mechanism + adoption + named failure class per pattern. That is template fodder, not a build backlog.

4. **One narrow exception earns frame (c).** Evidence-by-design (Pattern 2) and the executable-verification loop (Pattern 1) describe *the verification-evidence channel around a build pipeline* — which is the project's residual-defensible artifact. There may be a thin, greenfield-only build slice here (a tamper-evident verification artifact the producing agent cannot forge), but only as a kill-gated experiment, not a committed feature. Flagged DEFERRED, not VALIDATED-to-build.

**Note on Pattern 6:** the research's "cross-cutting failure layer" is not a candidate pattern — it is the failure-mode catalogue for Patterns 1–5. It is not given its own 5-test row; its content is folded into the template-mapping rationale and surfaced in flaggedDecisions as the assurance content the template must carry.

---

## Pattern 1 — Executable verification loops (tests/build/lint/typecheck as the success signal)

Frame for this pattern: **(c) mixed** — reference as a control; a thin build slice is DEFERRED.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS (as control) | This is genuinely *why* unattended coding-agent autonomy works at all — Anthropic states the loop "closes on its own" only when there is a machine-readable pass/fail. For the template's purpose (citing the load-bearing control), the causation is real and well-evidenced. |
| 2. Frequency match | PASS | The control is invoked on every build/CI run, which matches a compliance template that is consulted per-engagement and per-pipeline-change; it is not a daily-engagement gimmick warping a low-frequency product. |
| 3. Survivorship bias | PASS | The research surfaces the failures explicitly — reward hacking (GPT-5 76% on ImpossibleBench), ~31% weak oracles, flaky tests masking instability. We are mapping the control *with* its documented failure class, not copying a winner blind. |
| 4. Anti-pattern / engagement-at-cost | PASS | Drives real assurance value (auditable pass/fail) rather than activity; the failure mode (gate-becomes-target) is itself documented and is part of what the template must warn about. |
| 5. Complexity cost | FAIL (as build) / PASS (as reference) | Re-building a verification-loop engine is redundant — Claude Code Stop hooks + SWE-bench harness already ship it; cost vastly exceeds value. As a *referenced control* in the template the cost is near-zero. The only non-redundant slice (a forge-proof evidence artifact) is unproven and out of current scope. |

**Label: REFRAMED.**
- **Original (research framing):** "Executable verification loops" as a substrate feature to build.
- **Reframed:** A *recognised verification control the AU-gov template references and maps to assurance expectations*, carrying its documented failure modes (reward hacking, weak/flaky oracles, Stop-hook 8-block escape valve). The reframe rescues it because Test 5 fails only against "build it"; it passes cleanly against "cite and map it." The narrow forge-proof-artifact build idea is split out as a DEFERRED flag, not part of this label.

---

## Pattern 2 — Evidence-by-design (attach proof before claiming "done")

Frame for this pattern: **(c) mixed** — reference as a control; thin build slice DEFERRED (this is the pattern closest to the residual-defensible build pipeline).

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | The "trust-then-verify gap" is named by Anthropic as a primary failure cause, and "show evidence rather than asserting success" is the direct mitigation. Evidence-by-design is causal to catching plausible-but-wrong agent output, not incidental. |
| 2. Frequency match | PASS | Evidence is produced per task/diff — matches the template's per-engagement assurance cadence and the build pipeline's per-run cadence. |
| 3. Survivorship bias | PASS | The research carries the counter-evidence: fabricated evidence (Replit fabricated ~4,000 users + false test results), reviewers over-reporting gaps. We map the control knowing it can be forged by the producing agent. |
| 4. Anti-pattern / engagement-at-cost | PASS | Produces auditable artifacts (test output, the command + its return, screenshots) — direct assurance value, not session inflation. |
| 5. Complexity cost | FAIL (as full build) / PASS (as reference + thin slice) | The general pattern is first-party Anthropic guidance + a bundled skill — re-implementing it is redundant. BUT the *unforgeable* evidence channel (tamper-evident artifact the producing agent cannot fabricate) is an open, unsolved need the research explicitly flags, and it sits on the project's residual-defensible build pipeline. That thin slice could justify cost — but is unproven, so it must be kill-gated, not committed. |

**Label: REFRAMED.**
- **Original:** "Evidence-by-design" as a substrate feature.
- **Reframed:** A *control the template references* ("attach machine-checkable proof before 'done'") PLUS a **DEFERRED** greenfield experiment — a tamper-evident verification artifact bound into the fail-closed build pipeline that the producing agent cannot forge. The reframe rescues the control half (Test 5 passes as reference); the build half is explicitly deferred behind a verify-first kill gate because the forgeable-evidence problem (Replit) has no shipped solution and the value is speculative.

---

## Pattern 3 — Grounding through retrieval, tools, and enforced citations

Frame for this pattern: **(a) control to reference/map.**

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS (with caveat) | Grounding causally cuts *surface* hallucination (Endex 10%→0%, vendor-sourced), but the research is explicit that "retrieval does not guarantee support" — it shifts the error class rather than removing it. Causal at the surface, partial at the substance; the template must state this nuance. |
| 2. Frequency match | PASS | Citation/grounding controls apply per generated answer — consistent with a template consulted per output-producing engagement; no cadence mismatch. |
| 3. Survivorship bias | PASS | Failure surfaced: mis-citation, overgeneralization, permutation-induced hallucination (Stable-RAG), citation accuracy lagging grounding accuracy. Mapped with eyes open. |
| 4. Anti-pattern / engagement-at-cost | PASS | Traceability/auditability is exactly the value a gov compliance reader needs; not engagement bait. |
| 5. Complexity cost | FAIL (as build) / PASS (as reference) | The Citations API is GA across two clouds — building our own grounding layer is pure redundancy. As a referenced control ("require source-bound citations; note citation≠support") the cost is near-zero and the value to the template is high. |

**Label: REFRAMED.**
- **Original:** "Grounding through retrieval" as a substrate feature.
- **Reframed:** A *control the AU-gov template references* — "constrain outputs to retrieved, citable sources" — explicitly annotated with the documented limit that grounding shifts but does not eliminate the error class. Reframe rescues it: Test 5 fails only against build (GA product exists); passes as a mapped control. This is the cleanest frame-(a) pattern in the cluster.

---

## Pattern 4 — Generator–verifier / critic / adversary (a second model grades the first)

Frame for this pattern: **(a) control to reference/map.**

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Generator-verifier separation is causally load-bearing — CriticGPT exists precisely because self-grading / human-only review is capacity-limited; fresh-context review catches what the producer's own reasoning hides. |
| 2. Frequency match | PASS | Applied per-diff / per-output review — matches per-engagement assurance cadence. |
| 3. Survivorship bias | PASS | Strong counter-evidence carried: LLM-judge position/verbosity/self-preference bias, CriticGPT hallucinating bugs, and steganographic verifier collusion that "outpaces equally-capable overseers." We are not copying a clean winner. |
| 4. Anti-pattern / engagement-at-cost | PASS | Independent adversarial review creates genuine assurance value; over-reporting is a known tuning issue, not an engagement-farming anti-pattern. |
| 5. Complexity cost | FAIL (as build) / PASS (as reference) | CriticGPT and Claude Code reviewer subagents ship first-party; multi-agent debate/reflexion remain *research*, not production-shipped. Building either is high cost for conditional/unproven benefit (the research calls debate gains "conditional"). As a referenced control with its bias/collusion caveats, cost is near-zero. |

**Label: REFRAMED.**
- **Original:** "Generator–verifier–adversary" as a substrate feature.
- **Reframed:** A *control the template references* — "have a separate, fresh-context model grade the producer's output" — carrying the mandatory caveats (judge bias is systematic and game-able; multi-agent verifier collusion is documented; debate/reflexion are not yet production-proven). Reframe rescues it because Test 5 fails only against building a novel verifier; the control maps cleanly. The debate/reflexion sub-variants are flagged separately as not-production-ready.

---

## Pattern 5 — Behavioral evals for production agent systems (the eval-harness layer)

Frame for this pattern: **(a) control to reference/map.**

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS (with caveat) | Versioned eval suites as a CI quality gate causally catch regressions before ship. Caveat the research is blunt about: a contaminated/overfit eval measures leakage, not capability (SWE-bench 22.4%→10.0% once leakage removed). Causal only when the eval is decontaminated. |
| 2. Frequency match | PASS | Evals run per prompt/agent change and against prod traces — matches a template consulted per-change and per-engagement. |
| 3. Survivorship bias | PASS | Heavily counter-evidenced: OpenAI walked away from SWE-bench Verified (59.4% of failures were test flaws), >94% pre-cutoff contamination, "benchmark illusion." The losing side is documented. |
| 4. Anti-pattern / engagement-at-cost | PASS | Eval gates produce assurance value; the risk (eval gaming) is itself a control-design caveat, not engagement inflation. |
| 5. Complexity cost | FAIL (as build) / PASS (as reference) | This is an $800M-valuation funded market (Braintrust, promptfoo, Inspect AI). Building an eval platform is the single worst complexity-cost trade in the cluster. As a referenced control — and notably, Inspect AI is a *government* (UK AISI) framework, ideal for the AU-gov template to cite — the value is high and the cost is citation-only. |

**Label: REFRAMED.**
- **Original:** "Behavioral evals" as a substrate feature.
- **Reframed:** A *control the AU-gov template references and maps* — "gate agent changes behind versioned, decontaminated eval suites in CI" — preferentially citing **Inspect AI (UK AISI)** as the government-aligned precedent, with the mandatory contamination/overfitting caveat. Reframe rescues it: Test 5 fails only against build (mature funded market exists); passes cleanly as a mapped control. Strong frame-(a) fit and a direct AU↔UK-gov precedent bridge.

---

## Summary of labels

| Pattern | Label | Frame |
| --- | --- | --- |
| 1. Executable verification loops | REFRAMED | (c) reference + DEFERRED thin build slice |
| 2. Evidence-by-design | REFRAMED | (c) reference + DEFERRED forge-proof artifact |
| 3. Grounding via retrieval/citations | REFRAMED | (a) reference/map |
| 4. Generator–verifier–adversary | REFRAMED | (a) reference/map |
| 5. Behavioral evals | REFRAMED | (a) reference/map |

No pattern was VALIDATED-to-build, and none was REJECTED. Every pattern is a legitimate, well-evidenced verification control; each fails the complexity-cost test *only* when framed as "novel substrate to build" (the framing the 2026-06-01 reposition retired) and passes when framed as "control the AU-gov compliance template references and maps." That uniform REFRAMED result is itself the headline finding: this cluster is template content, not a build backlog.

## Flagged decisions (surfaced here because ROADMAP.md does not exist)

1. **DEFERRED — Tamper-evident, non-forgeable verification-evidence artifact** (from Patterns 1 & 2). The only genuine build candidate in the cluster, scoped strictly to the residual-defensible fail-closed build pipeline. Unblock condition: a verify-first kill gate confirming (a) no shipped product already solves the producing-agent-forges-its-own-evidence problem (Replit class) and (b) the artifact materially strengthens the AU-gov template's assurance claims. Do NOT commit greenfield budget before that gate fires.

2. **NEW (template content) — "Gate-becomes-target" assurance section.** Research Pattern 6 (cross-cutting failure layer) is not a feature but is high-value template content: the AU-gov template should carry an explicit catalogue of the four failure classes (reward hacking, fabrication/false-success, verifier unreliability/collusion, flaky/weak oracles) and the layered-defense rationale ("no single gate is individually sound"). Route to template authoring, not to `@planner` as a sprint.

3. **DEFERRED — Multi-agent debate / reflexion sub-variants** (from Pattern 4). Not production-shipped; research describes gains as "conditional." Do not reference as a recommended control in the template until production evidence exists; hold as a watch item.

4. **Honesty caveat to propagate.** Most adoption figures in the source research are vendor/PR-sourced (Braintrust valuation, promptfoo Fortune-500 penetration, Endex delta, CriticGPT preference rates) and several arXiv IDs are recent preprints. Any figure that lands in the AU-gov template must be re-verified against a primary source before it is presented to a government reader as settled. Inspect AI (UK AISI) is the most defensible single citation in the cluster because it is itself a government artifact.

5. **No NON_GOALS.md update warranted.** Nothing here is a standing "no"; all five are valid controls. Recording for traceability that no Non-Goal entry was added.
