# Validation: Cost & model governance (Cluster 8 — ADJACENT)

**Date:** 2026-06-15
**Owner:** `@pm`
**Source research:** `docs/planning/research/cost-model-governance-research.md`
**Framework:** `.github/instructions/validation-framework.instructions.md` (5-test echo-chamber filter)
**Cluster status:** ADJACENT (efficiency, not security/process-control core). Higher bar applied — adjacent efficiency features must clear the Complexity-cost and Causation tests strictly to compete with core work.

---

## Frame decision (per-cluster) and rationale

**Frame chosen: (a) controls the AU-gov compliance template should reference — NOT (b) substrate features to build.** One pattern is a partial exception (model right-sizing ladder) and lands as REFRAMED toward declared limits; the rest are REJECTED or DEFERRED as referenced controls.

Three facts drive this frame:

1. **agent-enterprise is a build-time resolver, not a runtime.** Per the vision doc (`safety-in-consumption-design-goals.md` §7 non-goals): *"Not a runtime sandbox. We do not execute or sandbox agents."* Every Cluster 8 lever is a **runtime** cost mechanism — routing decides per live request, caching discounts live API calls, reasoning-effort dials tune live inference, FinOps dashboards aggregate live spend. The resolver never sits in any of those loops. It cannot *operate* a router, a cache, or a spend meter; it can only **declare and compile** a limit into the artifact it emits. So none of these can be a "substrate feature to build" without inventing a runtime the project has explicitly disowned.

2. **The cost-governance hook already exists and is owned by core, not Cluster 8.** DG-4 (least-capability manifests) already carries **`maxUsd` / `timeoutMs` / kill-switch as first-class declared ceilings**, against threat **T8 (runaway cost / unbounded autonomy)**, slated for Sprint 4. The only Cluster-8 idea that the project's *core mission* actually wants is "an agent's cost must be bounded by a declared ceiling that the build compiles into a real gate." That is a **compliance control**, not an efficiency feature — it limits blast radius, it does not optimise spend.

3. **The repositioning (2026-06-01) killed "novel substrate" as a default frame.** Per MEMORY: the two original novel-substrate claims were disconfirmed; current direction is an **Australian-government compliance template, proposal-tier.** Efficiency levers map to that direction only as *controls the template references so an adopter's agent fleet meets a cost-accountability / spend-governance expectation* — i.e. point an adopter at FinOps-for-AI and routing as their problem to solve, with our manifest compiling the declared ceiling. They do not map to it as things we build and run.

Net: validate Cluster 8 as **template-referenced controls**, with the single load-bearing exception that the *declared cost ceiling* (already DG-4/T8 core work) is the one place a Cluster-8 idea becomes a real compiled gate.

---

## Pattern 1 — Model right-sizing ladder (strong-for-planning, cheap-for-execution)

The vault candidate `pattern-model-right-sizing-ladder`: assign tiered models to tiered work; strong model plans/orchestrates, cheap model executes.

| # | Test | Verdict | Reasoning |
|---|------|---------|-----------|
| 1 | Causation vs correlation | **FAIL (as efficiency); PASS (as declared limit)** | The research is blunt that the ladder is a *value-routing* decision that spends **~15× chat tokens**, not a cost-reduction one ("only worth it for high-value tasks"). It is not *why* anything succeeds for a build-time resolver — the resolver never picks a model at runtime. It only passes the causation test if reframed as "the artifact should *declare* which rung it assumes so a ceiling can be compiled," which is the DG-4 hook, not the ladder itself. |
| 2 | Frequency match | **FAIL** | The ladder pays off in high-frequency, high-token runtime fleets. agent-enterprise is invoked at **build/resolve time** (project-scoped, infrequent per artifact), not per-request. A per-request model-selection lever is cadence-mismatched to a resolver. |
| 3 | Survivorship bias | **PASS** | The research shows the *cheap-rung false economy* failure (5–10 self-correction cycles erase the saving), i.e. it surfaces the apps/configs where this lost. Not pattern-matching on winners only. |
| 4 | Anti-pattern / value | **PASS (as declared limit)** | A *declared* assumed-rung + cost ceiling drives real adopter value (blast-radius bound, T8). The ladder *as a runtime optimisation* drives token-spend, which is not our value axis. |
| 5 | Complexity cost | **FAIL (build the ladder); PASS (compile a declared field)** | Building or operating a model router/ladder is a runtime system we have disowned — enormous cost, zero fit. Adding a declared `model_tier:` / assumed-rung field that DG-4's ceiling references is near-free and rides existing Sprint-4 work. |

**Label: REFRAMED**
- **Original:** Build a model right-sizing ladder (strong-for-planning / cheap-for-execution) into agent-enterprise.
- **Reframed:** *Do not build a runtime ladder.* Add an optional declared **assumed-model-tier field** to the capability manifest so the DG-4 cost ceiling (`maxUsd`, T8) can be reasoned about against the rung the skill assumes, and so the AU-gov template can reference "right-size the model to the task and declare the assumption" as an adopter control.
- **Why the reframe rescues it:** The failure was Tests 1/2/5 — the *runtime ladder* is mis-causal, cadence-mismatched, and a disowned runtime. Restating it as a **declared manifest assumption that an already-planned ceiling references** moves it onto the build-time/compliance axis the project actually owns, at near-zero added complexity.

---

## Pattern 2 — LLM routing (per-request strong-vs-cheap selection)

The vault candidate `concept-routing-planning-to-stronger-models`: a router picks cheap-vs-strong model per request.

| # | Test | Verdict | Reasoning |
|---|------|---------|-----------|
| 1 | Causation vs correlation | **FAIL** | Routing's headline savings (RouteLLM >85% on MT-Bench) are **benchmark-conditional and vendor/author-sourced**; "AI Agents That Matter" (2407.01502) shows cost-blind benchmarks overstate real savings. Even taken at face value, routing is a *runtime* inference-cost optimisation — it is not the cause of any build-time-resolver outcome. |
| 2 | Frequency match | **FAIL** | A per-request router is the definition of high-frequency runtime cadence; a resolver has no per-request loop to insert it into. |
| 3 | Survivorship bias | **PASS** | Research surfaces the structural losses: degenerate convergence (2602.03478), life-cycle routing vulnerabilities (2503.08704), "routing on vibes" silent regressions. Failure modes are documented, not hidden. |
| 4 | Anti-pattern / value | **FAIL** | The dominant failure is a **silent quality regression** — a hard task misrouted to a weak model fails quietly. For a *compliance* template that sells trustworthiness, shipping a control whose signature failure is undetectable quality loss is engagement-at-cost's cousin: it optimises spend while eroding the exact assurance the template promises. |
| 5 | Complexity cost | **FAIL** | Routing needs an eval-set / LLM-judge / A/B harness to be safe (the research names this as the missing prerequisite). Building that for a Markdown resolver is wildly out of proportion to a non-core efficiency lever. |

**Label: REJECTED** (fails Tests 1, 2, 4, 5; not rescuable)
- Not rescuable because the only salvage — "the AU-gov template could *mention* routing as an adopter cost option" — is too thin to be a control: it carries a silent-quality-regression failure mode (Test 4) that a compliance template should warn *against* unaccompanied by a regression-detection layer, not endorse. Routing is the adopter's runtime decision, outside our build-time boundary. Surfaced as a flagged decision below rather than a standing NON_GOAL (it is an adopter concern, not a project temptation to permanently foreclose).

---

## Pattern 3 — Prompt / context caching

The vault candidate `concept-prompt-caching`: discounted rate for repeated prompt prefixes.

| # | Test | Verdict | Reasoning |
|---|------|---------|-----------|
| 1 | Causation vs correlation | **FAIL** | Caching is the most universally shipped lever with real bill cuts (Anthropic 90% off reads, OpenAI automatic 50%), but the discount is realised **at API call time by the model vendor**, entirely outside the resolver. It cannot be a cause of any build-time outcome; the resolver emits Markdown, it does not make cached API calls. |
| 2 | Frequency match | **FAIL** | Caching pays off across many repeated runtime calls within a TTL window (5-min default). A resolver's cadence is project-scoped builds, not bursty repeated inference. |
| 3 | Survivorship bias | **PASS** | Research documents the precise failure surface: cache miss from non-deterministic prefixes, invalidation cascades (`tools→system→messages`), 20-block lookback, silent non-caching with no error. The losing configs are named. |
| 4 | Anti-pattern / value | **N/A** | Caching is value-neutral cost reduction with no session-gaming dynamic; the test does not bind. It simply is not *our* value to capture. |
| 5 | Complexity cost | **FAIL** | Any benefit (e.g. emitting cache-friendly stable prefixes / breakpoint hints into artifacts) is a speculative micro-optimisation for a downstream consumer's runtime, at real authoring/maintenance cost, on a non-core axis — wrong trade. |

**Label: REJECTED** (fails Tests 1, 2, 5; not rescuable)
- Interesting adjacency: caching *rewards prefix determinism*, and **determinism is already a core safety property (DG-10)**. But that is a coincidental alignment, not a reason to build a caching feature — DG-10 already delivers byte-identical builds for tamper-evidence; we do not need caching as a second justification. No salvage that is both in-boundary and load-bearing. Adopter-side runtime concern; surfaced as a flagged decision.

---

## Pattern 4 — Deliberate token-spend budgeting (reasoning-effort, thinking budgets, spend caps, four-quadrant value)

The vault candidate `concept-token-spend-has-four-quadrants` plus the shipped dials (reasoning-effort, per-task caps, spend guardrails). **This is the pattern that touches core work (DG-4 / T8).**

| # | Test | Verdict | Reasoning |
|---|------|---------|-----------|
| 1 | Causation vs correlation | **PASS (for the spend-cap sub-pattern only)** | The *declared spend/time ceiling* sub-pattern is genuinely causal for the project's value: bounding runaway autonomy (T8) is *why* an adopter can trust an AFK agent. The reasoning-effort/thinking-budget *dials* and the "four-quadrant value" frame are runtime/conceptual and fail this test (no shipped product even implements the quadrant frame — research calls it an unmet need). |
| 2 | Frequency match | **PASS (for declared ceilings)** | A declared ceiling is set once at author/resolve time and compiled into the artifact — that matches the build-time cadence exactly. (The runtime dials again fail; they are per-request.) |
| 3 | Survivorship bias | **PASS** | Research documents the failure: hard caps **truncate mid-task** (re-paying for lost work); the GPT-5 auto-router "got dumber" complaint shows the loss-of-predictability failure of *automatic* spend decisions. This argues directly for *declared, not automatic* ceilings — the DG-4 design choice. |
| 4 | Anti-pattern / value | **PASS** | A declared `maxUsd`/`timeoutMs`/kill-switch is real adopter value (predictable blast radius, audit-able limit) with no session-gaming dynamic. |
| 5 | Complexity cost | **PASS (declared ceiling); FAIL (graceful-degradation engine)** | The declared-ceiling field is already in the Sprint-4 plan (DG-4) — incremental, in-boundary, low cost. The research's "soft cap → downshift / compress / checkpoint-resume" unmet need is a *runtime* engine and is out of bounds; do not build it. |

**Label: REFRAMED**
- **Original:** Build deliberate token-spend budgeting (reasoning-effort dials, four-quadrant spend classification, soft-cap graceful degradation) into agent-enterprise.
- **Reframed:** *Scope down to the declared cost/time ceiling only* — which is **already core work (DG-4, threat T8, Sprint 4):** `maxUsd` / `timeoutMs` / kill-switch as first-class declared manifest fields the resolver compiles into a real gate. Drop the reasoning-effort dials, the four-quadrant frame, and the soft-cap engine as runtime/out-of-boundary. The AU-gov template references "every autonomous agent must carry a declared spend/time ceiling" as a compliance control.
- **Why the reframe rescues it:** The full pattern failed Tests 1/2/5 on its runtime-dial and degradation-engine parts. Restricting to the **declared ceiling** sub-pattern passes all five and — crucially — does not invent new work: it confirms and reinforces an existing core threat (T8) and sprint (4). This is the one place a Cluster-8 idea becomes a genuine compiled gate rather than a referenced adopter concern.

---

## Pattern 5 — FinOps for LLMs (dashboards, per-team budgets, showback/chargeback)

Not a named vault candidate, but a distinct pattern the research isolates: apply cloud-FinOps discipline (visibility, attribution, optimization, accountability) to token spend.

| # | Test | Verdict | Reasoning |
|---|------|---------|-----------|
| 1 | Causation vs correlation | **FAIL (as a build) / PASS (as a referenced control)** | FinOps-for-AI is a *runtime cost-observability* discipline (dashboards over live spend, chargeback off billing data). It cannot be a build-time-resolver feature. But it *is* a legitimate **compliance/accountability control** an AU-gov template should point an adopter toward — which is the frame we chose. |
| 2 | Frequency match | **FAIL (build) / N/A (reference)** | Continuous spend monitoring is a runtime/ops cadence, not a resolver cadence. As a referenced control the cadence test does not bind to us. |
| 3 | Survivorship bias | **PASS** | Research surfaces the core unsolved pain ("an LLM API call is a transaction, not an asset" — no resource to tag), showback-weak-accountability vs chargeback-needs-infra, and the "cloud cost playbook breaks down." Failure modes are named, not hidden. |
| 4 | Anti-pattern / value | **PASS** | Spend attribution / accountability is real governance value and aligns with a compliance template's accountability axis (cf. DG-9 audit/provenance posture). No engagement-at-cost dynamic. |
| 5 | Complexity cost | **FAIL (build) / PASS (reference)** | Building FinOps tooling is enormous and squarely out of bounds. *Referencing* it in the AU-gov template (e.g. "adopters must attribute and govern agent-fleet token spend; see FinOps Foundation 'FinOps for AI'") is near-zero cost. |

**Label: DEFERRED**
- **Why DEFERRED not REJECTED:** Valid in principle as an AU-gov-template *referenced control* (passes Tests 3/4 and the reference-framing of 1/5), but **blocked by a missing dependency**: the AU-gov compliance template itself does not yet exist as an artifact to attach a control to. There is nothing to write the reference *into* today.
- **Unblock condition:** When the AU-gov compliance template / control catalogue is created, add a referenced control: "Agent-fleet token spend must be attributed and governed (showback/chargeback); the build's declared cost ceiling (DG-4) supplies the per-artifact bound." Do **not** build FinOps tooling.
- Note: ROADMAP.md does not exist, so this is surfaced in flaggedDecisions rather than parked there.

---

## Summary

| Pattern | Label | One-line reason |
|---------|-------|-----------------|
| 1 — Model right-sizing ladder | REFRAMED | Runtime ladder fails causation/frequency/complexity; rescued as a declared assumed-tier field the DG-4 ceiling references. |
| 2 — LLM routing | REJECTED | Per-request runtime optimisation outside our build-time boundary; signature failure is a silent quality regression a compliance template can't endorse. |
| 3 — Prompt caching | REJECTED | Vendor-side runtime discount the resolver never touches; cadence- and boundary-mismatched, no load-bearing salvage. |
| 4 — Token-spend budgeting | REFRAMED | Scoped down to the declared cost/time ceiling — already core work (DG-4 / T8 / Sprint 4); runtime dials and soft-cap engine dropped. |
| 5 — FinOps for LLMs | DEFERRED | Valid as an AU-gov-template referenced control, but blocked until that template exists; never build FinOps tooling. |

**Headline:** Only **one** Cluster-8 idea survives as buildable, and it is not new — the declared **cost/time ceiling** is already core work (DG-4, threat T8, Sprint 4). The remaining four levers are runtime cost optimisations that fall outside agent-enterprise's build-time boundary; they belong in the AU-gov compliance template as *adopter controls to reference*, not substrate to build. This is the expected result for an ADJACENT efficiency cluster held to the strict Causation and Complexity-cost bar.
