# Validation: Control plane & observability (Cluster 5)

**Date:** 2026-06-15
**Validator:** `@pm`
**Source research:** `docs/planning/research/control-plane-observability-research.md`
**Framework:** `.github/instructions/validation-framework.instructions.md` (5-test echo-chamber filter)

---

## Frame decision (per-cluster)

**Chosen frame: (a) controls the AU-gov compliance template should reference/map to — with two scoped (c) mixed exceptions.**

**Rationale.** agent-enterprise was repositioned on 2026-06-01 after research disconfirmed
both original "novel safety substrate" claims. The residual defensible value is a *reusable
AU-government compliance template* (proposal-tier; UK GDS has one, Australia does not). This
cluster surveys the enterprise agent **control plane** — and the evidence is unambiguous that
nearly every pattern here is a **mature, commoditised vendor capability**: three of four
hyperscalers ship a named control plane (AgentCore GA Oct 2025, Agent 365 Nov 2025, Agentforce),
an entire observability tooling layer has standardised on OTel GenAI conventions, and dedicated
guardrail/red-team/cost/audit products exist for every sub-layer. Building any of these as a
"substrate feature" would re-commit the exact mistake the reposition corrected: cloning a
crowded category on analogy.

The right move for a compliance template is to **map these patterns to the controls an
AU-government deployer must evidence** (ISM, PSPF, the forthcoming AU AI assurance expectations,
and the international anchors the research cites — EU AI Act Art. 9/12/14, NIST AI RMF, ISO/IEC
42001, SOC 2). The template's value is the *crosswalk and evidence checklist*, not a reimplementation
of LangSmith or AgentCore.

**Two exceptions are scoped as (c) mixed**, because they contain a thin, genuinely template-shaped
authoring artefact (not a product clone): the **audit-trail evidence schema** (Pattern 7) and the
**rollout/kill-switch change-control policy** (Pattern 5). In both, the template can ship a
*reference control definition and evidence requirement* that a deployer fills in — that is template
content, not substrate engineering.

**Important scope note on guardrail/red-team evidence (Patterns 3, 4).** The research's headline
finding is that every commercial guardrail is bypassable (emoji smuggling = 100% ASR) and that
red-team passing is a floor, not proof. For a *compliance template* this is a feature, not a
blocker: the template's job is to require the control AND require honest disclosure of its
residual-risk limits. We validate these as controls-to-reference with mandatory limitation
disclosure, never as a safety guarantee to build.

---

## Per-pattern validation

Verdict scale per test: PASS / FAIL / N/A, each with reasoning. One label per pattern.

> **Test re-interpretation for this frame.** The 5 tests were written for "should we *build* a
> feature." Under frame (a) the operative question becomes "should the AU-gov template *reference/map*
> this control." I apply each test against that question and note where a test is N/A because we are
> not building.

---

### Pattern 1 — OTel-shaped span tree as the observability substrate

| Test | Verdict | Reasoning |
|---|---|---|
| 1. Causation vs correlation | PASS | Structured trace/span observability is genuinely *why* a control plane can demonstrate "what the agent did" — it is the causal evidence base for audit and incident review, not incidental decoration. For a compliance template, traceability is a load-bearing control, not a vanity copy. |
| 2. Frequency match | PASS | A template is authored once and referenced per accreditation/assessment cycle. Observability is a continuous-operation control, which matches what an AU-gov deployer must evidence on an ongoing basis. Cadence aligns. |
| 3. Survivorship bias | PASS | The research explicitly surfaces the failure side: OTel GenAI conventions are *still experimental* (Mar 2026), so interoperability is partial. The template should reference the *capability* (structured tracing) while flagging the standard is unfrozen — survivorship checked, not ignored. |
| 4. Anti-pattern / engagement-at-cost | PASS | This drives real assurance value (reconstructable decision chains), not session counts. No engagement-farming risk for a compliance artefact. |
| 5. Complexity cost | PASS | Cost to the template is low: reference the OTel `gen_ai.*` span shape as a recommended (not mandated, given experimental status) evidence format. We are not building a tracer. |
| **Label** | **VALIDATED** | Reference as a control: require structured, hierarchical agent-action telemetry as the evidence base for traceability; cite OTel GenAI conventions as the leading (still-experimental) interoperability target. |

---

### Pattern 2 — Sampled tracing + online eval to control observability cost

| Test | Verdict | Reasoning |
|---|---|---|
| 1. Causation vs correlation | PASS | Sampling is the real operational mechanism teams use to make observability affordable at scale — it is causally why high-volume agents can be observed at all. It is a true control-design tradeoff, not analogy. |
| 2. Frequency match | PASS | The control is a standing operational-cost policy; matches the ongoing-operation cadence an AU-gov deployer must document. |
| 3. Survivorship bias | FAIL | The research is explicit that sampling creates a **structural blind spot**: the un-sampled 80–90% hides exactly the rare/novel failures that matter most for a security-sensitive gov deployment. Recommending sampling as a control without naming its blind spot would copy industry practice while ignoring the documented failure that bites government workloads hardest. |
| 4. Anti-pattern / engagement-at-cost | PASS | No engagement-farming concern; the risk is coverage, captured under Test 3. |
| 5. Complexity cost | PASS | Low template cost — it is a policy statement about sampling rate and exception handling. |
| **Label** | **REFRAMED** | **Original:** "reference sampled tracing + online eval as a cost-control observability pattern." Fails Test 3 — a blanket sampling recommendation imports the blind-spot risk into a government context where rare failures are the threat. **Reframed:** the template references sampling as an *acceptable cost-control technique only when paired with a mandated 100%-capture rule for high-risk action classes* (e.g., privileged tool calls, data egress, human-override events) and a documented sampling-exception policy. The reframe rescues it because it converts a coverage liability into a risk-tiered control — which is exactly the shape a compliance template should impose. |

---

### Pattern 3 — Input/output guardrail classifiers (the bypass-prone layer)

| Test | Verdict | Reasoning |
|---|---|---|
| 1. Causation vs correlation | PASS | Guardrails are a genuine, expected control in every assurance framework — their presence is causally required to claim injection/jailbreak mitigation. Referencing them is not analogy; it is table-stakes for an AI control catalogue. |
| 2. Frequency match | PASS | Standing runtime control; matches continuous-operation evidence cadence. |
| 3. Survivorship bias | PASS | The research provides peer-reviewed proof that guardrails *fail* (up to 100% ASR via emoji smuggling; NeMo 65–72%; Prompt Shield 60–72%). This is the strongest survivorship signal in the whole cluster, and the template can encode it as a mandatory residual-risk disclosure rather than ignoring it. |
| 4. Anti-pattern / engagement-at-cost | FAIL → recoverable | Treating "we deployed a guardrail" as a safety *guarantee* is a documented anti-pattern — it produces a false-assurance checkbox that drives compliance theatre rather than real protection. The control is valuable only if paired with mandatory limitation disclosure and defence-in-depth. |
| 5. Complexity cost | PASS | Template cost is low: define the control + required evidence + required limitation statement. No classifier is built. |
| **Label** | **REFRAMED** | **Original:** "reference guardrail classifiers as a prompt-injection/jailbreak control." Fails Test 4 — as written it invites false-assurance checkbox compliance. **Reframed:** the template references guardrails as a *required-but-insufficient* control that must be (i) deployed, (ii) accompanied by a documented residual-ASR/limitation statement citing the known bypass classes, and (iii) backed by defence-in-depth (deterministic policy enforcement outside the LLM loop, least-privilege tooling). The reframe rescues it by converting a checkbox into an honest, evidence-bearing control — the defining strength of a compliance template over a vendor datasheet. |

---

### Pattern 4 — Automated red-teaming pre-deployment

| Test | Verdict | Reasoning |
|---|---|---|
| 1. Causation vs correlation | PASS | Pre-deployment adversarial testing is a real, causally-motivated assurance gate (PyRIT/garak are the de-facto tools) — required to substantiate any "we tested for misuse" claim. Not analogy. |
| 2. Frequency match | PASS | Maps to a per-release / per-accreditation gate cadence, which a template can require at defined lifecycle points. Aligns with how gov assurance is evidenced. |
| 3. Survivorship bias | PASS | Research is explicit that automated red-teaming is a *floor not proof* — tools can't match human creativity for novel attacks, and garak has limited agentic coverage. The template should require red-teaming AND require human-expert testing for high-risk tiers; failure side acknowledged. |
| 4. Anti-pattern / engagement-at-cost | PASS | No engagement concern; drives real pre-deploy risk reduction. |
| 5. Complexity cost | PASS | Low template cost: reference automated red-team execution + evidence artefact + a "manual expert testing required for high-risk" clause. We do not build a scanner. |
| **Label** | **VALIDATED** | Reference as a control: require automated adversarial testing (cite PyRIT/garak/Promptfoo as exemplars) as a pre-deployment gate, with mandatory human-expert red-teaming for high-risk tiers and explicit acknowledgement that passing is a floor. |

---

### Pattern 5 — Prompt versioning + staged rollout + kill switch

| Test | Verdict | Reasoning |
|---|---|---|
| 1. Causation vs correlation | PASS | "Prompt updates drive most production incidents" (Deepchecks) — change-control over prompts is causally tied to incident rate. A change-control + kill-switch control is genuinely load-bearing, not copied. |
| 2. Frequency match | PASS | Change-control is a standing governance policy referenced per change; matches a template's authored-once, applied-per-change model well. |
| 3. Survivorship bias | PASS | Research notes the failure side (LangSmith staged deployment "feels less developed"; true env-based staging needs custom build) — i.e. the *product tooling* is immature, which is precisely why the template should specify the *control requirement* (review, staging, canary, kill switch) rather than endorse a tool. |
| 4. Anti-pattern / engagement-at-cost | PASS | Drives real operational safety (reversibility), no engagement-farming. |
| 5. Complexity cost | PASS (mixed) | As a *referenced control* the cost is low. As the scoped (c)-mixed exception, the template can additionally ship a thin reference **change-control + kill-switch policy artefact** (define required stages, gate criteria, rollback SLA) — that is authoring, not engineering, and the cost is justified by being uniquely template-shaped. |
| **Label** | **VALIDATED** | Reference as a control AND ship a reference change-control/kill-switch policy artefact in the template. Require: version control + review for prompts/policies, staged promotion with quality gates, canary or shadow before full rollout, and a documented one-click reversion/kill-switch with a rollback SLA. |

---

### Pattern 6 — Cost-quality governance at the gateway

| Test | Verdict | Reasoning |
|---|---|---|
| 1. Causation vs correlation | PASS | Spend governance is a real fiscal/operational control; for gov it ties to budget accountability. Per-team cost attribution is causally useful, not decorative. |
| 2. Frequency match | PASS | Standing operational control; matches ongoing-operation evidence cadence. |
| 3. Survivorship bias | FAIL | The research's central finding here is that the popular gateways (OpenRouter, Helicone) **track and alert but do not enforce** — there is no inline hard budget cap, leaving cost control reactive. Referencing "gateway cost governance" as a control without this caveat copies the market's gap; a runaway agent loop can overspend before a human reacts. |
| 4. Anti-pattern / engagement-at-cost | PASS | No engagement concern. |
| 5. Complexity cost | PASS | Low template cost as a referenced control. |
| **Label** | **REFRAMED** | **Original:** "reference gateway cost-quality governance (dashboards, routing, budgets) as a control." Fails Test 3 — most gateways lack *enforcement*, so the control as commonly implemented is reactive. **Reframed:** the template references cost governance as a control that must distinguish **tracking/alerting (necessary)** from **inline hard-cap enforcement (required for high-risk/autonomous agents)**, and requires the deployer to document which they have and the residual overspend exposure if enforcement is absent. The reframe rescues it by turning a market gap into an explicit risk-disclosure control. |

---

### Pattern 7 — Immutable audit trail for compliance evidence

| Test | Verdict | Reasoning |
|---|---|---|
| 1. Causation vs correlation | PASS | This is the *most directly load-bearing* pattern for the reposition: immutable, tamper-evident, attributable audit logs are exactly what EU AI Act Art. 12, ISO 42001, SOC 2 — and AU PSPF/ISM record-keeping — require. It is the causal core of a compliance template, not analogy. |
| 2. Frequency match | PASS | Audit-evidence requirements are referenced at every assessment and continuously enforced in operation; perfect fit for a template's cadence. |
| 3. Survivorship bias | PASS | Research surfaces the failure modes (broken decision chains fail audit; multi-agent attribution is hard; mutable app logs are insufficient) — these become *requirements* the template encodes, not pitfalls it ignores. |
| 4. Anti-pattern / engagement-at-cost | PASS | Pure assurance value; no engagement concern. |
| 5. Complexity cost | PASS (mixed) | As the scoped (c)-mixed exception, the template can ship a reference **audit-evidence schema** (required fields: actor, timestamp, tool invoked, data retrieved, reasoning link, authorisation, outcome, system-state link; immutability/tamper-evidence requirement; multi-agent attribution requirement). This is high-value, uniquely template-shaped authoring — the cost is justified and the artefact is the template's differentiator. |
| **Label** | **VALIDATED** | Reference as the anchor control AND ship a reference audit-evidence schema + crosswalk to EU AI Act Art. 12/14, NIST AI RMF, ISO 42001, SOC 2, and AU PSPF/ISM record-keeping. This is the cluster's strongest fit with the repositioned value proposition. |

---

### Pattern 8 — The vendor control plane (estate governance above individual agents)

| Test | Verdict | Reasoning |
|---|---|---|
| 1. Causation vs correlation | N/A (build) / PASS (reference) | We are not building a control plane — that would directly re-commit the disconfirmed "novel substrate" mistake (three hyperscalers already ship this). As a *reference*, naming the estate-governance capabilities a deployer needs (identity brokering, deterministic policy enforcement outside the LLM loop, observability, rollback) is causally sound for a template's environment-mapping section. |
| 2. Frequency match | PASS | The template can reference these as platform-selection / environment criteria, authored once and applied per deployment. Cadence fits. |
| 3. Survivorship bias | PASS | Research is explicit the native primitives are *incomplete* — AgentCore needed Rubrik for rollback, Straiker for runtime visibility; Agentforce adoption is contested. The template must therefore NOT assume a vendor control plane = compliance; it must require the deployer to evidence the specific controls regardless of platform. Failure side strongly informs the framing. |
| 4. Anti-pattern / engagement-at-cost | PASS | No engagement concern; the anti-pattern risk (vendor-control-plane-as-compliance-proxy) is captured in Test 3. |
| 5. Complexity cost | PASS | As a reference/environment-mapping section the cost is low. As anything to *build* the cost is prohibitive and off-strategy. |
| **Label** | **REFRAMED** | **Original (implicit build reading):** "vendor control plane as a substrate feature to build." This fails the reposition test outright (commoditised, hyperscaler-owned). **Reframed:** the template references vendor control planes as *platform-environment options* whose native primitives must be independently verified against the template's control catalogue — explicitly warning that "we run on AgentCore/Agent 365/Agentforce" is **not** itself compliance evidence given documented native gaps. The reframe rescues it by repositioning the pattern from a thing-to-build into an environment-mapping caution, which is genuine template value. |

---

## Summary of labels

| # | Pattern | Frame | Label |
|---|---|---|---|
| 1 | OTel-shaped span tree (observability substrate) | (a) reference | VALIDATED |
| 2 | Sampled tracing + online eval | (a) reference | REFRAMED |
| 3 | Input/output guardrail classifiers | (a) reference | REFRAMED |
| 4 | Automated red-teaming pre-deployment | (a) reference | VALIDATED |
| 5 | Prompt versioning + staged rollout + kill switch | (c) reference + reference artefact | VALIDATED |
| 6 | Cost-quality governance at the gateway | (a) reference | REFRAMED |
| 7 | Immutable audit trail | (c) reference + reference schema | VALIDATED |
| 8 | Vendor control plane (estate governance) | (a) reference | REFRAMED |

No REJECTED patterns: every pattern is legitimate *as a control to map* under the AU-gov template
frame. No pattern survives as a "novel substrate feature to build" — consistent with the 2026-06-01
reposition. The four REFRAMED labels all share one shape: the control is real but its *market
implementation has a documented gap*, and the template's job is to convert that gap into an explicit,
risk-tiered, evidence-bearing requirement.

---

## Flagged decisions (for owner — ROADMAP.md does not exist)

1. **[FRAME RATIFICATION]** This record commits the whole cluster to frame (a)/(c) — controls to
   *reference/map*, never substrate to build. This is downstream of the proposal-tier reposition,
   which is itself **not yet owner-ratified**. If the owner reverses the reposition, Patterns 5 and 7
   (the two mixed artefacts) are the only build candidates worth re-validating. **What do you think —
   ratify the reposition before any of this is treated as canonical?**

2. **[NEW — strongest template artefact]** Pattern 7's audit-evidence schema + multi-framework
   crosswalk (incl. AU PSPF/ISM, which the research did not cover) is the highest-value, most
   defensible deliverable in this cluster and the closest fit to "the UK-GDS-equivalent Australia
   lacks." Recommend it be the **anchor artefact** of the compliance template. Not handed to
   `@planner` yet — needs the frame ratified first.

3. **[NEW — AU-specific gap in the research]** The research anchors on EU AI Act / NIST / ISO 42001 /
   SOC 2 but contains **no AU-specific controls** (PSPF, ISM, the DTA/AI assurance framework,
   forthcoming AU AI guardrails). Before any handoff, commission a follow-up `@researcher` pass on
   the *Australian* control set so the template crosswalks to AU primary sources, not just
   international analogues. This is a dependency for the template's core claim.

4. **[DEFERRED — Pattern 2 high-risk-class capture rule]** The reframed "100% capture for high-risk
   action classes" rule depends on first defining the *taxonomy of high-risk agent actions* for AU
   gov (privileged tool calls, data egress, override events). That taxonomy is a prerequisite and
   doesn't exist yet. Unblock condition: high-risk-action taxonomy authored (likely from Cluster
   on tool-surface/process-controls).

5. **[CAVEAT — adoption numbers]** All vendor adoption figures in the research (Agentforce 18,500
   deals / 330% ARR; CrewAI 100k exec/day; Langfuse "billions of observations") are marketing-sourced
   and unaudited per the research's own honesty caveat. None of this validation relies on them; the
   load-bearing evidence is the peer-reviewed guardrail-bypass paper (arXiv:2504.11168) and the
   statutory frameworks. Do not cite vendor numbers as fact in the template.

6. **[CROSS-CLUSTER]** Patterns 3, 4, and 8 overlap heavily with the identity/credentials,
   tool-surface, and process-controls research clusters (deterministic policy enforcement, least
   privilege, human oversight). Recommend de-duplicating control definitions across cluster
   validations before `@planner` assembles the template, to avoid a fragmented control catalogue.
