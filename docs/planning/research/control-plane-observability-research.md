---
title: "Research: Control plane & observability for enterprise agents (Cluster 5)"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-15
---

# Research: Control plane & observability for enterprise agents (Cluster 5)

**Date:** 2026-06-15
**Requested by:** user (via `vault-candidates-research-brief.md`, Cluster 5)
**Scope:** External survey of how enterprise agent control planes are structured — observability/tracing, guardrails, red-teaming, rollout/version controls, cost-quality governance, and audit trails — across the major vendor platforms (Microsoft Agent 365 / Azure AI Foundry, AWS Bedrock AgentCore, Salesforce Agentforce, Google Vertex/Agentspace, LangGraph Platform, CrewAI Enterprise) and the dedicated tooling layer (LangSmith, Langfuse, Arize Phoenix, Braintrust, Helicone, OpenTelemetry GenAI conventions, NeMo Guardrails, Llama Guard, Azure Prompt Shields, Lakera, PyRIT, garak). Surfaces the concrete mechanisms, adoption scale where findable, user complaints, and documented failure modes (guardrail bypass ASRs, trace sampling blind spots, alert fatigue, audit-log gaps, cost-control lag). One paragraph of scope by design — this is a feed for `@pm`, not a synthesis with recommendations.

> This document surfaces **patterns + adoption evidence + failure modes only**, with a citation for every concrete claim. It contains **no recommendations** and applies **no validation/5-test filter** — kill/keep is `@pm`'s call (the "research then triage" path). Vendor-published adoption numbers (deal counts, conversation volumes, ARR growth) are marketing-sourced and flagged as such; treat them as directional, not audited. Vault provenance for this cluster: `[[agent control plane]]`, `concept-enterprise-agent-control-planes-can-move-agents-from-prototypes`, `concept-production-agent-systems-require-trace-observability`.

---

## Synthesis

The "control plane" has become a real product category in 2025–2026, not a metaphor. Three of the four hyperscalers now ship an explicitly-named governance layer that sits *above* individual agents and treats them as a managed estate: AWS **Bedrock AgentCore** (GA 13 Oct 2025), Microsoft **Agent 365** (launched Nov 2025, governing agents from Salesforce, ServiceNow, Google and OSS frameworks), and Salesforce **Agent Fabric / Agentforce**. Below them sits a maturing observability/eval tooling layer (LangSmith, Langfuse, Arize Phoenix, Braintrust) that has standardised on **OpenTelemetry GenAI semantic conventions** for span shape. The load-bearing tension across the whole stack: every protective layer (guardrails, traces, audit logs, cost caps) has a documented, quantified failure mode, and the strongest failures are in the *guardrail* layer, where peer-reviewed evasion attacks hit up to **100% attack success rate**.

### Summary table

| Layer / mechanism | What it does | Who ships it | Adoption signal | Where it breaks |
|---|---|---|---|---|
| **Trace/span observability** | Captures `invoke_agent` → `chat` → `execute_tool` span trees, token usage, latency | LangSmith, Langfuse, Arize Phoenix, Braintrust, Datadog LLM Obs, Helicone, W&B Weave | Langfuse: 28.9k★, 50M+ SDK installs/mo, 2,300+ companies, "billions of observations/mo" (vendor) | Sampling blind spots (10–20% sampled at scale); single-call instrumentation misses agent reasoning chains |
| **OTel GenAI conventions** | Vendor-neutral span/metric schema (`gen_ai.*` attributes) | OTel GenAI SIG (formed Apr 2024); Datadog native in OTel v1.37; Grafana/Loki | Adopted by Datadog, Grafana, AgentCore (OTEL-compatible) | Most conventions still **experimental** as of Mar 2026 — schema not stabilised |
| **Input/output guardrails** | Classify+block jailbreaks, prompt injection, unsafe content | NeMo Guardrails, Guardrails AI, Llama Guard, Azure Prompt Shields, Lakera Guard | Widely deployed; Lakera analyses 100k+ attacks/day via Gandalf | **Evasion ASR up to 100%** (emoji smuggling); NeMo Guard 65–72% ASR; char injection drops Prompt Shield accuracy 78–100% |
| **Red-teaming tooling** | Automated adversarial probing pre-deploy | Microsoft PyRIT (70+ converters), NVIDIA garak (120+ probes), Promptfoo | PyRIT = "Metasploit for LLMs"; garak 0.14 adding agentic support | Limited agentic/RAG coverage; cannot match human creativity for novel attacks |
| **Prompt/version rollout** | Versioning, staged dev→staging→prod, canary, A/B, shadow, kill switch | LangSmith, LangWatch, Braintrust, Maxim | "Prompt updates drive most incidents" (Deepchecks) | LangSmith staged deployment "feels less developed"; true env-based staging needs custom build |
| **Cost/spend governance** | Per-key/per-team token cost dashboards, model routing, budget caps | Helicone, OpenRouter, Portkey, LiteLLM | OpenRouter routes across 350+ models; CrewAI 100k+ executions/day | OpenRouter/Helicone have **no budget enforcement at gateway** — cost-control lag |
| **Audit trail / compliance** | Immutable per-action logs for SOC2/ISO 42001/EU AI Act | TraceAgent, Knowlee, Agent Fabric, AgentCore | EU AI Act Art. 12 mandates statutory-term logging for high-risk AI | Logs must be immutable/tamper-evident; broken decision chains fail audit |
| **Vendor control planes** | Govern agent estate: identity, policy, observability, rollback | AgentCore, Agent 365, Agentforce, Vertex/Agentspace | Agentforce: 18,500+ deals, 330% ARR growth YoY (vendor) | Policy enforcement quality varies; rollback/governance often needs 3rd-party (Rubrik) bolt-ons |

### Cross-cutting findings

- **The guardrail layer is the weakest link, and it is quantified.** A peer-reviewed empirical study (Hackett et al., arXiv:2504.11168, Apr 2025) found character-injection attacks like "emoji smuggling" achieve **100% attack success rate (ASR)** against multiple commercial guardrails for both prompt injection and jailbreaks. NeMo Guard Jailbreak Detect recorded **72.54% ASR** under character injection and was **most vulnerable to adversarial-ML jailbreak evasion at 65.22% average ASR**. Azure Prompt Shield hit **71.98% (injection) / 60.15% (jailbreak)** ASR. Meta Prompt Guard was the most robust (2.76% injection ASR) but separate work shows character injection still degraded Prompt Guard/Prompt Shield accuracy by **78.24%–100%**. ([arxiv.org/html/2504.11168v1](https://arxiv.org/html/2504.11168v1), [mindgard.ai](https://mindgard.ai/blog/bypassing-azure-ai-content-safety-guardrails))

- **The control plane consolidated into a named vendor product in late 2025.** AWS Bedrock AgentCore went GA 13 Oct 2025 as a composable set of services (Runtime, Gateway, Memory, Browser, Code Interpreter, Identity, Observability) covering "execution environment, session isolation, memory, tool connectivity, identity brokering, observability, policy enforcement, quality evaluation." Microsoft split build (Azure AI Foundry Agent Service, GA May 2025) from govern (**Agent 365**, Nov 2025), where Agent 365 explicitly governs *third-party and OSS agents*, not just Microsoft's own. ([aws.amazon.com](https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-agentcore-available), [nexustek.com](https://www.nexustek.com/insights/microsoft-agent-365-the-new-control-plane-for-enterprise-ai-governance))

- **Observability standardised on OTel, but the standard is still experimental.** The OTel GenAI SIG (formed Apr 2024) defines `invoke_agent` → `chat` → `execute_tool` span trees with `gen_ai.request.model`, `gen_ai.usage.input_tokens/output_tokens`, `gen_ai.response.finish_reasons`. Datadog ships native support since OTel v1.37; AgentCore Observability is OTEL-compatible and exports to Datadog/Arize/LangSmith/Langfuse. But **most GenAI conventions remain in experimental status as of March 2026** — the schema is not frozen, so "standard" interoperability is partial. ([opentelemetry.io](https://opentelemetry.io/blog/2026/genai-observability/), [datadoghq.com](https://www.datadoghq.com/blog/llm-otel-semantic-convention/))

- **Sampling and cost trade against coverage; this is structural, not fixable by tooling.** At scale teams sample 10–20% of requests for detailed traces, and run online evals on a sampled subset, explicitly to control logging cost — which means the un-sampled 80–90% is a blind spot for the rare/novel failure. Single-call instrumentation (the common starting point) misses the multi-step agent reasoning chain entirely. ([braintrust.dev](https://www.braintrust.dev/articles/best-llm-monitoring-tools-2026), [langchain.com](https://www.langchain.com/articles/llm-monitoring-observability))

---

## Method

Real WebSearch/WebFetch sweeps run 2026-06-15. Search axes: (1) observability/tracing platforms + adoption; (2) OTel GenAI semantic conventions + agent span structure; (3) guardrail frameworks + arXiv evasion evaluations; (4) red-teaming tools (PyRIT/garak) + coverage limits; (5) prompt versioning/rollout/canary/kill-switch; (6) cost/spend governance gateways; (7) audit trail + SOC2/ISO 42001/EU AI Act; (8) per-vendor control-plane structure and adoption numbers (AgentCore, Agent 365, Agentforce, LangGraph, CrewAI). Primary sources preferred where reachable: AWS What's New, Microsoft Azure Blog / Microsoft Learn, OpenTelemetry.io, arXiv (full-text fetch of the key bypass paper), and vendor GitHub/blog. The arXiv guardrail-evasion paper (2504.11168) was fetched full-text for exact ASR figures.

**Honesty caveat:** adoption figures published by Salesforce, AWS, CrewAI, and Langfuse are vendor/marketing-sourced (deal counts, conversation volume, ARR growth %, "billions of observations") and are **not independently audited**. They are reported here as directional adoption signals and flagged inline. GitHub-star and PyPI-download counts are third-party-verifiable but fluctuate. Guardrail ASR figures come from a peer-reviewed paper and are the most reliable hard numbers in this doc.

---

## Apps / sources surveyed

| System | Category | Mechanism | Scale signal |
|---|---|---|---|
| **LangSmith** | Observability + eval + prompt mgmt | Tracing, eval, prompt versioning, deployment, secure code exec | "Full agent engineering platform" 2026; tightly coupled to LangChain ([digitalapplied.com](https://www.digitalapplied.com/blog/agent-observability-platforms-langsmith-langfuse-arize-2026)) |
| **Langfuse** | OSS observability + eval | OTel-native tracing, prompt mgmt, evals, datasets | 28.9k★, 50M+ SDK installs/mo, 6M+ Docker pulls, 2,300+ companies; acquired by ClickHouse Jan 2026 ([github.com/langfuse](https://github.com/langfuse/langfuse)) |
| **Arize Phoenix** | OSS observability + eval | 50+ research-backed metrics (faithfulness, toxicity, hallucination), drift detection | Leading OSS/self-host option ([arize.com](https://arize.com/llm-evaluation-platforms-top-frameworks/)) |
| **Braintrust** | Eval + prompt + observability | Eval-first, prompt versioning, generous free tier (1M spans/mo) | Targets experimentation teams ([braintrust.dev](https://www.braintrust.dev/articles/langfuse-alternatives-2026)) |
| **Datadog LLM Observability** | Enterprise observability | Native OTel GenAI conventions since v1.37 | First major vendor to natively support OTel GenAI ([datadoghq.com](https://www.datadoghq.com/blog/llm-otel-semantic-convention/)) |
| **Helicone** | Proxy observability + cost | Request logging, cost analytics dashboard | Proxy-based; budget enforcement *not* its focus ([braintrust.dev](https://www.braintrust.dev/articles/best-llm-gateways-2026)) |
| **OpenTelemetry GenAI** | Span/metric standard | `gen_ai.*` span attributes, agent/tool/MCP spans | GenAI SIG since Apr 2024; mostly experimental Mar 2026 ([opentelemetry.io](https://opentelemetry.io/blog/2026/genai-observability/)) |
| **NeMo Guardrails** | Guardrail framework | Customizable "rails" + random-forest jailbreak classifier | 65–72% ASR under evasion (arXiv:2504.11168) |
| **Guardrails AI / Llama Guard** | Guardrail / safety classifier | Output validators; Llama Guard content classifier | Llama Guard 3 has documented false negatives ([arxiv.org/pdf/2506.21972](https://arxiv.org/pdf/2506.21972)) |
| **Azure Prompt Shields / AI Content Safety** | Guardrail (cloud) | Jailbreak + indirect-injection detection; Spotlighting (Build 2025) | Integrated into Foundry control plane; 60–72% ASR under evasion ([azure.microsoft.com](https://azure.microsoft.com/en-us/blog/enhance-ai-security-with-azure-prompt-shields-and-azure-ai-content-safety/)) |
| **Lakera Guard** | Guardrail (commercial) | Adaptive threat intel from 100k+ attacks/day (Gandalf) | 100k+ new attacks analysed daily ([lakera.ai](https://www.lakera.ai/risk/prompt-injection-attacks)) |
| **Microsoft PyRIT** | Red-team framework | 70+ prompt converters, adaptive iteration, multi-modal | "Metasploit for LLMs"; Microsoft AI Red Team ([appsecsanta.com](https://appsecsanta.com/pyrit)) |
| **NVIDIA garak** | Red-team scanner | 120+ probes; "Nmap for LLMs" | v0.14 adding agentic support; limited RAG coverage ([ringsafe.in](https://ringsafe.in/ai-red-teaming-pyrit-garak/)) |
| **AWS Bedrock AgentCore** | Control plane | Runtime/Gateway/Memory/Identity/Observability composable services | GA 13 Oct 2025; OTEL-compatible ([aws.amazon.com](https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-agentcore-available)) |
| **Microsoft Agent 365 / Azure AI Foundry** | Control plane | Govern agent estate across vendors; Foundry = build/run | Foundry GA May 2025; Agent 365 launched Nov 2025 ([nexustek.com](https://www.nexustek.com/insights/microsoft-agent-365-the-new-control-plane-for-enterprise-ai-governance)) |
| **Salesforce Agentforce / Agent Fabric** | Control plane | Agent+MCP dashboard, visual authoring canvas, human checkpoints | 18,500+ deals, 1M+ conversations, 330% ARR growth (vendor) ([salesforce.com](https://www.salesforce.com/news/stories/agentic-enterprise-index-insights-h1-2025/)) |
| **LangGraph Platform** | Agent framework + platform | Graph state mgmt mapping to audit trails/rollback points | 24.8k★, ~34.5M monthly PyPI downloads; LinkedIn/Replit/Elastic ([medium](https://medium.com/@atnoforgenai/10-ai-agent-frameworks-you-should-know-in-2026-langgraph-crewai-autogen-more-2e0be4055556)) |
| **CrewAI Enterprise** | Agent framework + platform | Multi-agent orchestration; enterprise tier | 44–46k★, 100k+ executions/day, 150+ enterprise customers, $18M Series A (vendor) ([medium](https://medium.com/@atnoforgenai/10-ai-agent-frameworks-you-should-know-in-2026-langgraph-crewai-autogen-more-2e0be4055556)) |
| **TraceAgent / Knowlee** | Audit/compliance | Immutable audit trail; EU AI Act Art. 12/14 alignment | Compliance-ready for EU AI Act, NIST, ISO 42001 ([traceagent.dev](https://www.traceagent.dev/)) |

---

## Patterns found

### Pattern 1 — OTel-shaped span tree as the observability substrate

- **What it is:** A standardised hierarchical trace where a top-level `invoke_agent` span has child `chat` spans for each LLM call and `execute_tool` spans for each tool invocation. Spans carry GenAI semantic-convention attributes: `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons`. The OTel GenAI SIG (formed under the Semantic Conventions SIG in April 2024) defines six layers: Client Spans, Agent Spans, MCP conventions, Events (prompt/completion content), Metrics, and Provider conventions.
- **Source apps:** OpenTelemetry GenAI conventions; Datadog LLM Observability (native since OTel v1.37); Grafana/Loki; Langfuse (OTel-native); AWS AgentCore Observability (OTEL-compatible, exports to Datadog/Arize/LangSmith/Langfuse).
- **Adoption scale:** Langfuse reports 50M+ SDK installs/month and "billions of observations per month" across 2,300+ companies (vendor-sourced). Datadog and Grafana are major-vendor adopters of the OTel convention. ([opentelemetry.io/blog/2026/genai-observability](https://opentelemetry.io/blog/2026/genai-observability/), [datadoghq.com](https://www.datadoghq.com/blog/llm-otel-semantic-convention/), [github.com/langfuse](https://github.com/langfuse/langfuse))
- **User complaints:** Single-call instrumentation is "a common starting point and a significant blind spot" — teams instrument the LLM call but not the agent reasoning chain or tool execution. A complete strategy "requires covering six areas — missing any one creates a blind spot." ([langchain.com](https://www.langchain.com/articles/llm-monitoring-observability))
- **Failure mode:** **The conventions are still experimental as of March 2026** — the API/schema is not stabilised, so cross-vendor interoperability is partial and attributes can shift between versions. ([greptime.com](https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions))

### Pattern 2 — Sampled tracing + online eval to control observability cost

- **What it is:** For high-volume agents, only 10–20% of requests get detailed traces; online evaluations run on a sampled subset of live traffic rather than every request, because evaluating every request "would be expensive and slow." Quality-aware alerting fires (PagerDuty/Slack) when eval scores, safety signals, or drift move — e.g. a non-urgent alert if quality drops >10% below the rolling 7-day baseline.
- **Source apps:** Standard practice across Braintrust, LangChain/LangSmith, Confident AI, Elastic LLM observability guides.
- **Adoption scale:** Described as standard production practice for "high-volume applications"; no single hard adoption number — it is a configuration norm rather than a product. ([braintrust.dev/articles/best-llm-monitoring-tools-2026](https://www.braintrust.dev/articles/best-llm-monitoring-tools-2026))
- **User complaints:** Inherent tension — "tracing multi-step agentic workflows without sampling can help avoid missing critical failure points," directly conflicting with the cost pressure to sample. Teams cannot have both full coverage and low cost.
- **Failure mode:** **Sampling blind spots.** The 80–90% un-sampled traffic is invisible; rare/novel failures (the ones that matter most for a security-focused control plane) are statistically likely to land in the un-sampled bucket and go undetected. ([inference.net](https://inference.net/content/llm-observability-monitoring-production-deployments/))

### Pattern 3 — Input/output guardrail classifiers (the bypass-prone layer)

- **What it is:** A classifier or rule-set sits in front of (and behind) the model to detect/block prompt injection, jailbreaks, and unsafe content. NeMo Guardrails offers customizable "rails" plus a lightweight random-forest jailbreak classifier using pre-trained embedding pairs. Azure Prompt Shields detects direct and indirect (cross-prompt) injection, with "Spotlighting" added at Build 2025 to improve indirect-injection detection. Llama Guard is a content-safety classifier. Lakera Guard learns continuously from 100k+ adversarial attacks/day via its Gandalf game.
- **Source apps:** NVIDIA NeMo Guardrails, Guardrails AI, Meta Llama Guard / Prompt Guard, Azure AI Content Safety / Prompt Shields, Lakera Guard, ProtectAI, Vijil.
- **Adoption scale:** NeMo Guardrails and Llama Guard cited as the two "promising solutions" for regulated (healthcare) deployments; Lakera processes 100k+ attacks/day; Azure Prompt Shields integrated into the Foundry control plane and Defender for Cloud AI alerts. ([azure.microsoft.com/blog/enhance-ai-security-with-azure-prompt-shields](https://azure.microsoft.com/en-us/blog/enhance-ai-security-with-azure-prompt-shields-and-azure-ai-content-safety/), [arxiv.org/html/2409.17190v1](https://arxiv.org/html/2409.17190v1))
- **User complaints:** Llama Guard 3 produces both false positives (over-blocking benign content) and **false negatives** (passing genuinely harmful content) — "Llama Guard had a lot of false negatives, which the Mistral judge was able to catch." Agentic setups are *more* vulnerable than the base LLM: "base LLMs are consistently more robust than their agentic counterparts." ([arxiv.org/pdf/2506.21972](https://arxiv.org/pdf/2506.21972), [arxiv.org/pdf/2510.01359](https://arxiv.org/pdf/2510.01359))
- **Failure mode — quantified guardrail bypass (the headline finding):** Hackett, Birch, Trawicki, Suri & Garraghan, *"Bypassing Prompt Injection and Jailbreak Detection in LLM Guardrails"* (arXiv:2504.11168, Apr 2025) empirically evaluated Azure Prompt Shield, Meta Prompt Guard, ProtectAI v1/v2, NeMo Guard Jailbreak Detect, and Vijil:
  - **Emoji smuggling: 100% ASR** for both prompt injection and jailbreaks.
  - **Vijil:** 87.95% (injection) / 91.67% (jailbreak) ASR — most vulnerable overall.
  - **Azure Prompt Shield:** 71.98% (injection) / 60.15% (jailbreak) ASR.
  - **NeMo Guard:** 72.54% ASR under character injection; **65.22% average ASR** under adversarial-ML jailbreak evasion — the most vulnerable to that class.
  - **ProtectAI v1:** 95.18% ASR (injection) under adversarial-ML evasion.
  - **Meta Prompt Guard:** most robust at 2.76% ASR (injection) — but separate Mindgard work shows character injection still reduced Prompt Guard / Prompt Shield detection accuracy by **78.24%–100%**.
  - Conclusion: both evasion families "can be used to evade detection while maintaining adversarial utility achieving in some instances up to 100% evasion success." ([arxiv.org/html/2504.11168v1](https://arxiv.org/html/2504.11168v1), [mindgard.ai/blog/bypassing-azure-ai-content-safety-guardrails](https://mindgard.ai/blog/bypassing-azure-ai-content-safety-guardrails))

### Pattern 4 — Automated red-teaming pre-deployment

- **What it is:** Adversarial probing harnesses run a battery of attacks against an agent before/after deploy. Microsoft PyRIT (Python Risk Identification Tool, from the Microsoft AI Red Team) automates adversarial testing across text/image/audio/video with 70+ prompt converters (Base64, ROT13, Leetspeak, Unicode confusables) that *stack* (translate → Base64 → embed in image) and can adaptively iterate on attacks. NVIDIA garak is a broad-spectrum vulnerability scanner ("Nmap for LLMs") with 120+ probes. Promptfoo is the third common tool.
- **Source apps:** Microsoft PyRIT, NVIDIA garak, Promptfoo; commercial AI red-team services (Mindgard, Lakera).
- **Adoption scale:** PyRIT positioned as the de-facto open framework ("Metasploit for LLMs"); garak v0.14.0 in development with "enhanced support for agentic AI systems." No hard install/user counts surfaced. ([appsecsanta.com/pyrit](https://appsecsanta.com/pyrit), [beyondscale.tech/blog/ai-red-teaming-tools-comparison-2026](https://beyondscale.tech/blog/ai-red-teaming-tools-comparison-2026))
- **User complaints:** garak "provides limited agentic and RAG coverage"; tools excel at systematic/regression coverage but produce many findings to triage.
- **Failure mode — coverage limits:** "Manual expert testing remains essential for discovering novel vulnerabilities, as automated tools excel at systematic coverage and regression testing but cannot match human creativity in developing new attack techniques." Red-team passing is therefore a floor, not proof of safety — the un-probed novel attack surface is unbounded. ([vectra.ai/topics/ai-red-teaming](https://www.vectra.ai/topics/ai-red-teaming), [ringsafe.in/ai-red-teaming-pyrit-garak](https://ringsafe.in/ai-red-teaming-pyrit-garak/))

### Pattern 5 — Prompt versioning + staged rollout + kill switch

- **What it is:** Prompts treated as deployable software. Mechanisms: version control + review; staged dev → staging → prod with quality gates at each stage; **canary** (small % of real traffic first, auto-stop on degradation); **A/B** (variants on live traffic side-by-side); **shadow mode** (new version runs in parallel on identical inputs, outputs discarded, to characterise behaviour); **one-click reversion / kill switch** (pin versions to affected cohorts).
- **Source apps:** LangWatch (explicit staged dev→staging→prod with gates), LangSmith (dataset mgmt + automated evaluators), Braintrust, Maxim.
- **Adoption scale:** Treated as "critical infrastructure" for production LLM apps; LangWatch and Braintrust market dedicated prompt-management products. No hard user counts surfaced. ([langwatch.ai/blog/what-is-prompt-management](https://langwatch.ai/blog/what-is-prompt-management-and-how-to-version-control-deploy-prompts-in-productions), [braintrust.dev/articles/best-prompt-versioning-tools-2025](https://www.braintrust.dev/articles/best-prompt-versioning-tools-2025))
- **User complaints:** LangSmith "prioritizes tracing and debugging over dedicated prompt development workflows"; environment-based deployment "feels less developed than pure prompt-management platforms," and "true environment-based staged deployment requires custom implementation."
- **Failure mode — prompt-change incidents:** Deepchecks reports **prompt updates drive most production incidents** — a one-line prompt edit ships behaviour change with none of the guardrails of a code deploy, and many teams "update prompts without reliable version control, review, or documentation… you're flying blind." ([deepchecks.com/llm-production-challenges-prompt-update-incidents](https://deepchecks.com/llm-production-challenges-prompt-update-incidents/), [tianpan.co/blog/2026-04-09-cicd-llm-applications-prompt-deployment-pipeline](https://tianpan.co/blog/2026-04-09-cicd-llm-applications-prompt-deployment-pipeline))

### Pattern 6 — Cost-quality governance at the gateway

- **What it is:** An LLM gateway/proxy sits between agents and providers, providing per-key/per-team token cost dashboards, model routing (cheap model for easy calls, strong model for hard), and (sometimes) budget caps. OpenRouter unifies 350+ models behind one API/bill with per-key spend tracking and trace broadcast to Datadog/Langfuse. Helicone is a proxy that logs requests + cost analytics. Portkey adds PII redaction, HIPAA coverage, and audit trails at the routing layer for enterprise governance.
- **Source apps:** OpenRouter, Helicone, Portkey, LiteLLM, Inworld/Eden AI routers.
- **Adoption scale:** OpenRouter routes across 350+ models; gateways are typically run *alongside* (not instead of) each other — "most teams run [Helicone] alongside OpenRouter, LiteLLM, or Portkey." CrewAI cites 100k+ agent executions/day (vendor). ([openrouter.ai/blog/insights/llm-gateway](https://openrouter.ai/blog/insights/llm-gateway/), [braintrust.dev/articles/best-llm-gateways-2026](https://www.braintrust.dev/articles/best-llm-gateways-2026))
- **User complaints:** "Budget enforcement and cache-aware cost calculations are not [Helicone's] focus"; OpenRouter has "no budget enforcement at the gateway level, and no per-customer or per-team spend hierarchy."
- **Failure mode — cost-control lag:** Most gateways *track and alert* on spend but do not *enforce* a hard cap inline, so a runaway agent loop can overspend before a human reacts to the alert. Governance "starts at the first endpoint" and "budget alerts should be set before you need them" — i.e. the failure is reactive-by-default. ([dev.to/pranay_batta/llm-cost-tracking-and-spend-management-for-engineering-teams](https://dev.to/pranay_batta/llm-cost-tracking-and-spend-management-for-engineering-teams-233a))

### Pattern 7 — Immutable audit trail for compliance evidence

- **What it is:** Every agent action is logged with enough detail to reconstruct the decision chain post-hoc: which tools were invoked, what data was retrieved, what reasoning produced the action, the outcome, plus actor, timestamp, and system-state link. Auditors ask three questions — who/what decided, what authorised it, and what happened. EU AI Act Art. 12 (logging), Art. 14 (human oversight), Art. 9 (risk management) impose statutory-term retention for high-risk AI.
- **Source apps:** TraceAgent ("immutable audit trail… compliance-ready for EU AI Act, NIST, ISO 42001"), Knowlee (architected for EU AI Act Art. 9/12/14), Salesforce Agent Fabric governance tools, AgentCore policy enforcement.
- **Adoption scale:** Positioned as mandatory for regulated deployers under five frameworks — EU AI Act (Reg. 2024/1689), NIST AI RMF 1.0, ISO/IEC 42001:2023, SOC 2 (AICPA TSP 100), GDPR. ISO 42001 lets the deployer reason about "suitable" log depth; the EU AI Act "resets that bar" with mandatory logging of every vital input, model change, override, and human action. ([digitalapplied.com/blog/ai-agent-governance-policy-compliance-2026](https://www.digitalapplied.com/blog/ai-agent-governance-policy-compliance-2026), [isms.online/frameworks/iso-42001](https://www.isms.online/frameworks/iso-42001/iso-42001-logging-lifecycle-traceability-vs-eu-ai-act/))
- **User complaints:** Multi-agent outputs are hard to make "attributable and reversible" enough to pass audit — establishing *which* agent in a crew made a decision and *what authorised it* is non-trivial. ([augmentcode.com/guides/multi-agent-outputs-n-pass-enterprise-audit](https://www.augmentcode.com/guides/multi-agent-outputs-n-pass-enterprise-audit))
- **Failure mode — log incompleteness / tamper-evidence:** Audits "demand unbroken proof" — a single missing link (an unlogged override, retraining, or deletion) breaks the chain and fails the audit. Logs must be *immutable* (hence dedicated products marketing "immutable audit trail"), implying the default mutable application log is insufficient and tamper-vulnerable. ([traceagent.dev](https://www.traceagent.dev/), [augmentcode.com](https://www.augmentcode.com/guides/multi-agent-outputs-n-pass-enterprise-audit))

### Pattern 8 — The vendor control plane (estate governance above individual agents)

- **What it is:** A platform layer that governs a *fleet/estate* of agents — identity brokering, deterministic policy enforcement outside the LLM loop, observability, rollback, and quality eval — independent of which framework/model built each agent.
  - **AWS Bedrock AgentCore** (GA 13 Oct 2025): composable Runtime, Gateway (turns APIs/Lambda/MCP into agent tools), Memory, Browser, Code Interpreter, Identity (secure vault for refresh tokens, identity-aware authz), Observability (CloudWatch-powered, OTEL-compatible). AgentCore Evaluations went GA Mar 2026. Policies defined in natural language but **executed deterministically outside the LLM reasoning loop** via the Gateway.
  - **Microsoft Agent 365** (Nov 2025): the control plane governing the agent estate across Salesforce, ServiceNow, Google and OSS frameworks, layered over Azure AI Foundry Agent Service (build/run, GA May 2025).
  - **Salesforce Agent Fabric / Agentforce**: agent + MCP dashboard tracking agents across Salesforce and third parties (Amazon, GoDaddy), a visual authoring canvas mapping agentic *and human* checkpoints, and governance tools for higher-risk processes.
- **Source apps:** AWS Bedrock AgentCore, Microsoft Agent 365 / Azure AI Foundry, Salesforce Agentforce, Google Vertex AI / Agentspace, LangGraph Platform, CrewAI Enterprise.
- **Adoption scale (vendor-sourced, flagged):**
  - Agentforce: 18,500+ deals closed since launch (9,500+ paid, +50% QoQ); customers in production +70% QoQ; 1M+ conversations on help.salesforce.com by Jul 2025; 330% ARR growth YoY; Williams-Sonoma's "Olive" agent handles ~60% of website conversations.
  - LangGraph: ~24.8k★, ~34.5M monthly PyPI downloads, 1.0 stable Oct 2025, deployments at LinkedIn/Replit/Elastic.
  - CrewAI: 44–46k★, 100k+ agent executions/day, 150+ enterprise customers, "60% of Fortune 500," $18M Series A, $3.2M revenue by Jul 2025.
  ([salesforce.com/news/stories/agentic-enterprise-index-insights-h1-2025](https://www.salesforce.com/news/stories/agentic-enterprise-index-insights-h1-2025/), [salesforcedevops.net](https://salesforcedevops.net/index.php/2025/07/14/salesforce-crosses-1-million-agentforce-conversations/), [aws.amazon.com](https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-agentcore-available))
- **User complaints / gaps:** Rollback and governance for AgentCore were notably *not native at GA* — Rubrik announced add-on "agent governance and rollback" for AgentCore at re:Invent (Dec 2025), and startups (Straiker, Rubrik) are filling runtime-protection/visibility gaps the platforms left open. Agentforce real-world adoption is contested — practitioner coverage asks "where are we really at with Agentforce adoption?" against the headline deal numbers. ([virtualizationreview.com](https://virtualizationreview.com/articles/2025/12/02/rubrik-adds-agent-governance-and-rollback-to-amazon-bedrock-agentcore-at-aws-re-invent.aspx), [salesforceben.com/where-are-we-really-at-with-agentforce-adoption](https://www.salesforceben.com/where-are-we-really-at-with-agentforce-adoption/))
- **Failure mode:** The control planes are new (all GA/launched in 2025) and lean on **third-party bolt-ons for governance/rollback/runtime protection**, indicating the native control-plane primitives are incomplete; deterministic policy enforcement quality varies and the "govern any vendor's agent" promise depends on integrations that are still maturing. ([helpnetsecurity.com/2026/03/23/straiker-discover-ai](https://www.helpnetsecurity.com/2026/03/23/straiker-discover-ai/))

---

## Unmet needs observed

- **No guardrail withstands character-injection/emoji-smuggling at production-grade ASR.** Every commercial guardrail evaluated in arXiv:2504.11168 was bypassable; emoji smuggling hit 100%. There is no surveyed product that closes this — it is an open research gap, not a feature anyone ships. ([arxiv.org/html/2504.11168v1](https://arxiv.org/html/2504.11168v1))
- **Inline budget *enforcement* (hard cap that stops a runaway agent) is missing from the popular gateways.** OpenRouter and Helicone track and alert but do not enforce; this leaves cost-control reactive. ([braintrust.dev/articles/best-llm-gateways-2026](https://www.braintrust.dev/articles/best-llm-gateways-2026))
- **Full-coverage tracing without prohibitive cost** — sampling is the universal compromise; nobody surfaces a way to get 100% coverage of rare failures cheaply. ([inference.net](https://inference.net/content/llm-observability-monitoring-production-deployments/))
- **Attribution + reversibility for multi-agent crews** is hard to make audit-passing; "which agent decided, what authorised it" is an open operational problem. ([augmentcode.com](https://www.augmentcode.com/guides/multi-agent-outputs-n-pass-enterprise-audit))
- **Native rollback/governance in the hyperscaler control planes** — AgentCore needed Rubrik for rollback; runtime visibility needed Straiker. The estate-governance promise outran the shipped primitives. ([virtualizationreview.com](https://virtualizationreview.com/articles/2025/12/02/rubrik-adds-agent-governance-and-rollback-to-amazon-bedrock-agentcore-at-aws-re-invent.aspx))
- **A stable, non-experimental observability standard** — OTel GenAI conventions are still experimental (Mar 2026), so the interoperability story has a moving floor. ([greptime.com](https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions))
- **Alert signal-to-noise for quality drift** — quality-aware alerting (>10% drop vs 7-day baseline) is emerging but thresholds are hand-tuned; no surveyed source claims a solved alert-fatigue story for eval-score alerts.

---

## Sources

**Observability / tracing platforms**
- Arize — Comparing LLM Evaluation Platforms: https://arize.com/llm-evaluation-platforms-top-frameworks/
- digitalapplied — Agent Observability (LangSmith/Langfuse/Arize) 2026: https://www.digitalapplied.com/blog/agent-observability-platforms-langsmith-langfuse-arize-2026
- Braintrust — Langfuse alternatives 2026: https://www.braintrust.dev/articles/langfuse-alternatives-2026
- Braintrust — Best LLM monitoring tools 2026: https://www.braintrust.dev/articles/best-llm-monitoring-tools-2026
- LangChain — Why LLM observability needs evaluations: https://www.langchain.com/articles/llm-monitoring-observability
- Inference.net — LLM Observability complete guide: https://inference.net/content/llm-observability-monitoring-production-deployments/
- Langfuse GitHub (stars/installs/Docker pulls): https://github.com/langfuse/langfuse

**OpenTelemetry GenAI conventions**
- OpenTelemetry — Inside the LLM Call: GenAI Observability: https://opentelemetry.io/blog/2026/genai-observability/
- Datadog — native OTel GenAI Semantic Conventions: https://www.datadoghq.com/blog/llm-otel-semantic-convention/
- Greptime — How OTel traces LLM/agent/MCP (experimental status): https://greptime.com/blogs/2026-05-09-opentelemetry-genai-semantic-conventions

**Guardrails + evasion (hard ASR numbers)**
- arXiv:2504.11168 — Hackett et al., *Bypassing Prompt Injection and Jailbreak Detection in LLM Guardrails* (full-text fetched): https://arxiv.org/html/2504.11168v1
- Mindgard — Bypassing Azure AI Content Safety Guardrails (78–100% accuracy drop): https://mindgard.ai/blog/bypassing-azure-ai-content-safety-guardrails
- Microsoft Azure Blog — Prompt Shields + Content Safety (Spotlighting): https://azure.microsoft.com/en-us/blog/enhance-ai-security-with-azure-prompt-shields-and-azure-ai-content-safety/
- Microsoft Learn — Prompt Shields / jailbreak detection: https://learn.microsoft.com/en-us/azure/ai-services/content-safety/concepts/jailbreak-detection
- Lakera — Prompt Injection Attacks (100k attacks/day via Gandalf): https://www.lakera.ai/risk/prompt-injection-attacks
- arXiv:2409.17190 — Enhancing Guardrails for Healthcare AI (NeMo + Llama Guard): https://arxiv.org/html/2409.17190v1
- arXiv:2506.21972 — Llama Guard false negatives / hybrid jailbreak: https://arxiv.org/pdf/2506.21972
- arXiv:2510.01359 — agentic counterparts less robust than base LLMs: https://arxiv.org/pdf/2510.01359

**Red-teaming**
- AppSecSanta — PyRIT 2026 (70+ converters): https://appsecsanta.com/pyrit
- RingSafe — AI Red Teaming: PyRIT, garak (garak 0.14 agentic): https://ringsafe.in/ai-red-teaming-pyrit-garak/
- BeyondScale — PyRIT vs Garak vs Promptfoo 2026: https://beyondscale.tech/blog/ai-red-teaming-tools-comparison-2026
- Vectra — AI red teaming tools/frameworks (manual still essential): https://www.vectra.ai/topics/ai-red-teaming

**Prompt versioning / rollout**
- LangWatch — What is prompt management (staged/canary/A-B/shadow): https://langwatch.ai/blog/what-is-prompt-management-and-how-to-version-control-deploy-prompts-in-productions
- Braintrust — Best prompt versioning tools: https://www.braintrust.dev/articles/best-prompt-versioning-tools-2025
- Deepchecks — prompt updates drive most incidents: https://deepchecks.com/llm-production-challenges-prompt-update-incidents/
- TianPan — CI/CD for LLM apps / prompt deployment: https://tianpan.co/blog/2026-04-09-cicd-llm-applications-prompt-deployment-pipeline

**Cost / spend governance**
- OpenRouter — What is an LLM Gateway: https://openrouter.ai/blog/insights/llm-gateway/
- Braintrust — 6 best LLM gateways 2026 (no gateway budget enforcement): https://www.braintrust.dev/articles/best-llm-gateways-2026
- dev.to — LLM cost tracking & spend management: https://dev.to/pranay_batta/llm-cost-tracking-and-spend-management-for-engineering-teams-233a

**Audit trail / compliance**
- digitalapplied — AI Agent Governance Policy & Compliance 2026: https://www.digitalapplied.com/blog/ai-agent-governance-policy-compliance-2026
- ISMS.online — ISO 42001 logging vs EU AI Act: https://www.isms.online/frameworks/iso-42001/iso-42001-logging-lifecycle-traceability-vs-eu-ai-act/
- Augment Code — Multi-agent outputs passing enterprise audit (attributability/reversibility): https://www.augmentcode.com/guides/multi-agent-outputs-n-pass-enterprise-audit
- TraceAgent — immutable audit logging for AI agents: https://www.traceagent.dev/
- Knowlee — ISO 42001 vs SOC2 vs ISO 27001: https://www.knowlee.ai/blog/iso-42001-vs-soc2-vs-iso-27001-comparison

**Vendor control planes + adoption**
- AWS — Bedrock AgentCore now generally available (What's New): https://aws.amazon.com/about-aws/whats-new/2025/10/amazon-bedrock-agentcore-available
- AWS — AgentCore Evaluations GA (Mar 2026): https://aws.amazon.com/about-aws/whats-new/2026/03/agentcore-evaluations-generally-available
- NexusTek — Microsoft Agent 365 control plane: https://www.nexustek.com/insights/microsoft-agent-365-the-new-control-plane-for-enterprise-ai-governance
- linesNcircles — Enterprise Agent Platforms 2026 (Gemini/Agentforce/Bedrock/Foundry): https://linesncircles.com/Blog/Enterprise/Enterprise_Agent_Platforms_2026
- Salesforce — Agentic Enterprise Index H1 2025 (deal/adoption numbers, vendor): https://www.salesforce.com/news/stories/agentic-enterprise-index-insights-h1-2025/
- SalesforceDevops — 1M Agentforce conversations: https://salesforcedevops.net/index.php/2025/07/14/salesforce-crosses-1-million-agentforce-conversations/
- Salesforce Ben — "Where are we really at with Agentforce adoption?" (skeptical): https://www.salesforceben.com/where-are-we-really-at-with-agentforce-adoption/
- Medium/ATNO — 10 AI Agent Frameworks 2026 (LangGraph/CrewAI stars+downloads): https://medium.com/@atnoforgenai/10-ai-agent-frameworks-you-should-know-in-2026-langgraph-crewai-autogen-more-2e0be4055556
- VirtualizationReview — Rubrik adds governance + rollback to AgentCore: https://virtualizationreview.com/articles/2025/12/02/rubrik-adds-agent-governance-and-rollback-to-amazon-bedrock-agentcore-at-aws-re-invent.aspx
- Help Net Security — Straiker runtime protection for agents: https://www.helpnetsecurity.com/2026/03/23/straiker-discover-ai/

**Verification flags:** All vendor adoption numbers (Salesforce 18,500 deals / 330% ARR / 1M conversations; CrewAI 100k executions/day / 150+ enterprise / "60% of Fortune 500"; Langfuse "billions of observations/mo" / 2,300+ companies) are **marketing-sourced and not independently audited** — verify before citing as fact. GitHub-star and PyPI-download counts vary by source date and should be re-checked at use time. The arXiv:2504.11168 ASR figures are peer-reviewed and the most reliable quantitative claims here. Microsoft Agent 365 launch framing comes from a partner (NexusTek) blog, not Microsoft Learn directly — confirm against primary Microsoft docs before load-bearing use.

---

*No recommendations section by design — hand off to `@pm` for validation/prioritisation (the "research then triage" path).*
