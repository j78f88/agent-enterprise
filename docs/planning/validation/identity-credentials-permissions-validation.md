# Validation: Identity, credentials & permissions (Cluster 2)

**Date:** 2026-06-15
**Validator:** `@pm`
**Source research:** `docs/planning/research/identity-credentials-permissions-research.md`
**Framework:** `.github/instructions/validation-framework.instructions.md` (5-test echo-chamber filter)
**Reposition context:** agent-enterprise was repositioned 2026-06-01. The two original "novel safety substrate" claims were disconfirmed as novel. Current direction = an **Australian-government compliance template, proposal-tier**.

---

## Chosen frame for this cluster: **(a) controls the AU-gov compliance template should reference/map to** — with two narrow exceptions

**Frame: predominantly (a), reference-and-map; not (b) build-a-substrate-feature.** Rationale:

1. **What agent-enterprise actually is.** This repo produces build-time prompt/skill/agent artifacts via `init.py`. It is not a running control plane: there is no live IdP, no credential broker process, no policy decision point at a tool boundary. Every Cluster 2 pattern (Entra Agent ID, Vault dynamic secrets, Cedar/OPA at a gateway, ID-JAG, SPIFFE/SPIRE, ReBAC) is a **runtime infrastructure product** owned by a cloud/IdP/secret-manager vendor. agent-enterprise cannot *build* these; it can at most **require, reference, and provide a conformance mapping to** them. That is exactly the compliance-template job.
2. **The reposition forbids the default.** Pre-2026-06-01, the temptation was to read this research as "novel identity substrate to build." That framing was disconfirmed for the project's two original claims and is doubly wrong here, where the patterns are explicitly *already shipped by named vendors* (Entra GA, Okta GA, Vault EA, OPA 100M+ downloads). Re-shipping a worse version of Entra Agent ID is not novel and not in scope.
3. **The AU-gov angle has real pull-through.** The research surfaces controls that map cleanly onto Australian government frameworks an agent-deployment template would need to satisfy: ISM (Information Security Manual) identity/credential controls, the Essential Eight (restrict admin privileges, MFA, application control), PSPF (Protective Security Policy Framework) accountability, and DTA / emerging AU agentic-AI guidance. A template's value is *telling an AU-gov team which of these vendor controls they must adopt and how to evidence it* — not building the control.
4. **Two narrow build-exceptions (mixed).** A small number of patterns have a thin, genuinely buildable artifact *inside* a prompt-artifact template: (i) **the plaintext-secrets anti-pattern guardrail** — build-time linting / `.gitignore` enforcement / a NON_GOAL that no secret is ever written to a resolved artifact or `.mcp.json`; and (ii) **a human-sponsor/accountability requirement baked into agent definitions** — the template *can* mandate a named accountable human per agent in its own schema. These are flagged as REFRAMED-to-template-control or NEW, not as substrate rebuilds.

**Net:** Patterns are validated as **compliance-template reference controls (map-to)**, with the secrets-hygiene guardrail and the accountability field as the only thin in-repo builds. Each pattern carries one label below.

---

## How to read the labels

Per the framework, exactly one label per pattern. Because the frame is "compliance template," PASS on the 5 tests means **"this control belongs in the template's control catalogue / conformance map"**, not "build a runtime feature." A pattern that is real and important but cannot be expressed even as a template control without an external dependency is **DEFERRED**. A pattern that is a pure vendor product with no template hook is **REJECTED for build** but may still be cited as background (noted inline).

> Note: the framework's standard tests (causation, frequency, survivorship, anti-pattern, complexity) were designed for consumer-app feature copying. I apply their *intent* to the compliance-template context: Causation = "is this control load-bearing for the security outcome, or incidental?"; Frequency = "does an AU-gov agent deployment actually hit this control on its cadence?"; Survivorship = "did anyone ship this and still get breached / abandon it?"; Anti-pattern = "does mandating it create real assurance or just paperwork?"; Complexity = "does template-mapping cost match the assurance gained?"

---

## Pattern 1 — Dedicated agent-identity principal (Entra Agent ID class)

A first-class directory object distinct from human users and app service principals, with a mandatory accountable human (`sponsor`) in the schema.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | The accountability + lifecycle attributes (sponsor, owner, lifecycle state) are *the* mechanism that makes "which agent acted, on whose behalf" answerable — a load-bearing PSPF/ISM accountability requirement, not incidental dressing. |
| Frequency | PASS | Any AU-gov agent deployment provisions identities continuously; this control is hit on every agent create/retire, matching the template's audience cadence exactly. |
| Survivorship | PASS (with scar) | The pattern shipped and was breached twice in this research (Entra "Agent ID Administrator" role overreach; EchoLeak abusing well-modelled identity's broad grants). The survivorship lesson is *not* "drop identity" — it's "identity alone is insufficient without scope-narrowing," which strengthens the case to mandate it **plus** least-privilege, not weaken it. |
| Anti-pattern | PASS | Mandating a named human sponsor per agent produces real assurance (traceability) rather than box-ticking — it is exactly the gap the research quantifies (only 28% can trace agent actions to a sponsor). |
| Complexity | PASS | As a *template control* (require an agent-identity object + named sponsor, map to ISM/PSPF), cost is documentation, not infrastructure. The buildable sub-part — a mandatory accountable-human field in agent-enterprise's own agent schema — is a thin addition. |

**Label: REFRAMED**
- **Original (as research implies):** Build an Entra-style agent-identity directory.
- **Reframed:** (a) Template control: *require* a dedicated agent-identity principal with a named human sponsor and map it to ISM/PSPF accountability + Essential Eight "restrict admin privileges." (b) Thin build: add a mandatory `sponsor`/accountable-human field to agent-enterprise's agent definition schema so the template eats its own dog food. The reframe rescues it because the substrate (an IdP) is out of scope, but the *requirement* and a *schema field* are squarely in scope.

---

## Pattern 2 — Federated delegation token (Okta Cross App Access / ID-JAG)

Short-lived, admin-governed delegation credential encoding {user, agent, scopes, target app}.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | Admin-governed delegation (no end-user consent dialog) is the control that prevents broad standing consent — directly load-bearing for the "authorized to call ≠ intended" gap. |
| Frequency | N/A→PASS | Hit on every cross-app agent action, but only relevant to deployments that span multiple SaaS apps; for single-app AU-gov pilots it may not fire. Passes as a *conditional* template control. |
| Survivorship | PASS | The thing it replaced (per-server DCR) was abandoned as "a massive barrier"; ID-JAG is the surviving design and is in the Nov-2025 MCP spec. No abandonment signal against ID-JAG itself. |
| Anti-pattern | PASS | Replaces standing broad consent with scoped short-lived delegation — real assurance, not paperwork. |
| Complexity | FAIL (for build) | ID-JAG is Okta-proprietary, format unpublished, single-IdP, no multi-cloud portability. agent-enterprise cannot build or even reliably reference it without locking a customer to Okta. |

**Label: DEFERRED**
**Unblock condition:** The MCP "Enterprise-Managed Authorization" capability / `draft-oauth-ai-agents-on-behalf-of-user` reaches a stable, vendor-neutral form (research projects full RFC stack ~2027-2028). Until then the template can cite "use federated short-lived delegation where your IdP supports it" as guidance, but cannot make it a mandatory mapped control without picking a proprietary winner. Surface in flaggedDecisions.

---

## Pattern 3 — Cryptographic workload identity (SPIFFE/SPIRE + cloud variants)

Short-lived attested SVIDs; identity from infrastructure facts; no shared secret.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | Secret-less, auto-rotated identity removes the static-credential root cause that drives the cluster's largest harm class. Genuinely load-bearing where it fits. |
| Frequency | FAIL | Research is explicit: SVID issuance latency and re-attestation are "incompatible with creating/destroying agents thousands of times/day," and SPIFFE encodes no intent/owner/task. The AU-gov agent cadence (ephemeral, high-frequency) is the exact mismatch the framework's frequency test exists to catch. |
| Survivorship | PASS | Mature, prod at Uber/Stripe/Netflix; not abandoned. The pattern survives — for *workloads*, not high-frequency *agents*. |
| Anti-pattern | PASS | Real assurance (no shared secret) when applicable. |
| Complexity | FAIL (for build/mandate) | "Years not months," dedicated HA attestation infra, SPOF without HA, no native owner/sponsor. Cost vastly exceeds what a proposal-tier compliance template can mandate of an AU-gov adopter. |

**Label: DEFERRED**
**Unblock condition:** WIMSE dual-identity agent extension finishes (its security-considerations section is currently literally "TODO") and SVID issuance becomes viable for ephemeral agents. Template can reference SPIFFE as the *recommended* workload-identity substrate for long-lived service agents, but cannot mandate it for the general case. Surface in flaggedDecisions.

---

## Pattern 4 — Cloud IAM service-role pattern (AWS / Google)

Reuse existing cloud IAM (execution role + trust policy; SPIFFE principal as IAM principal).

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | Constraining the trust policy (`aws:SourceArn`) and per-session attribution (`SourceIdentity`) are the controls that prevent confused-deputy lateral movement — load-bearing. |
| Frequency | PASS | Any AU-gov deployment on AWS/GCP (the common case) hits IAM on every agent action. |
| Survivorship | PASS (with scar) | Confused-deputy in Roles Anywhere (Unit 42) and AgentCore "God Mode" default roles are real failures — but they are *misconfiguration* failures, which is precisely what a compliance template exists to prevent. Strengthens the map-to case. |
| Anti-pattern | PASS | Mandating least-privilege roles + source conditions + SourceIdentity produces audited, real least-privilege; directly maps to Essential Eight "restrict admin privileges." |
| Complexity | PASS | As a template control (here are the IAM conditions an AU-gov agent role MUST set, mapped to ISM), cost is documentation against an IAM substrate the customer already runs. |

**Label: VALIDATED**
Cleared as a template reference control: a conformance checklist for agent IAM roles (constrain trust policy, set SourceIdentity, no `Resource:"*"`, no default starter roles) mapped to ISM/Essential Eight. No build required.

---

## Pattern 5 — NHI-governance overlay (discover / attribute / flag)

A layer above the substrate that discovers all non-human identities, maps to owners, flags hygiene.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | Discovery + ownership attribution is what closes the "shadow agent" gap the research names as the top unsolved problem. |
| Frequency | PASS | Continuous control; an AU-gov estate needs an agent registry on an ongoing basis (research: only 21% keep a real-time registry). |
| Survivorship | N/A | No abandonment data; category is young and entirely vendor-driven. |
| Anti-pattern | FAIL (caution) | This is the category that *produces nearly every sprawl statistic in the doc and sells the fix*. Mandating a commercial NHI-governance product risks paperwork-and-vendor-capture rather than assurance. The *requirement* (maintain an agent registry mapped to sponsors) is real; the *product* is not something to endorse. |
| Complexity | PASS (for the requirement, not the product) | Requiring "maintain a current agent registry with named owners" is a low-cost template control; mandating a specific overlay product is not. |

**Label: REFRAMED**
- **Original:** Adopt an NHI-governance overlay product.
- **Reframed:** Template control: *require an agent registry mapping every agent identity to a named human sponsor and recording lifecycle state*, mapped to PSPF accountability. Be product-neutral; do not endorse a vendor overlay. The reframe rescues it by keeping the assurance outcome (the registry/ownership requirement) and dropping the vendor-capture risk the anti-pattern test flagged.

---

## Pattern 6 — Plaintext secrets in config/env (the dominant anti-pattern)

Raw keys in `.mcp.json` / `claude_desktop_config.json` env blocks; no encryption, no rotation.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | The research's single largest concrete harm source (24,008 MCP-config secrets on GitHub, 90k+ creds harvested from `.env`). Preventing it is the highest-leverage control in the cluster. |
| Frequency | PASS | Every MCP-using deployment touches config files; agent-enterprise *itself* emits `.mcp.json`-style and resolved artifacts, so the project hits this risk on its own build path. |
| Survivorship | PASS | The anti-pattern is the de-facto default *and* the most-breached; the lesson is unambiguous — eliminate it. |
| Anti-pattern | PASS | A build-time guard that blocks secrets from entering resolved artifacts is pure assurance. |
| Complexity | PASS | Low cost and genuinely buildable *in this repo*: lint/CI check + `.gitignore` enforcement + a NON_GOAL that no secret is written to any resolved/`.mcp.json` artifact + template guidance to reference an external secret manager. |

**Label: NEW**
Origin: not copied as a feature — it is a *guardrail against an anti-pattern*, and it is the one place the project can build something real and load-bearing within prompt-artifact scope. Build: (i) build-time/CI check that resolved artifacts and emitted MCP config contain no inline secrets; (ii) `.gitignore` + docs/NON_GOALS entry; (iii) template control "secrets MUST come from an external manager (Vault/cloud KMS/keychain), never inline," mapped to ISM credential-management controls. Treat as VALIDATED per the framework's NEW definition.

---

## Pattern 7 — OS-native keychain / encrypted local storage

Tokens in macOS Keychain / Windows Credential Manager / libsecret instead of config.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | A direct, mature remediation of Pattern 6 — moves secrets out of plaintext config. |
| Frequency | PASS | Relevant to every local-MCP deployment, including dev workstations in an AU-gov team. |
| Survivorship | PASS | Multiple shipping backends (IBM mcp-cli, 1Password, Doppler); not abandoned. |
| Anti-pattern | PASS | Real hygiene improvement; the only caveat (OS-session compromise exposes all tokens at once) is a known limit, not a falsification. |
| Complexity | PASS | As a template *recommendation* (prefer keychain over env), zero build cost. agent-enterprise can't operate a keychain but can require/reference it. |

**Label: VALIDATED**
Cleared as a template reference control bundled with Pattern 6: "prefer OS keychain / encrypted store for local agent tokens." No build; documentation/mapping only.

---

## Pattern 8 — Secret-manager dynamic/leased credentials (Vault class)

Generate ephemeral TTL'd credentials on demand via a machine identity.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | Short-lived dynamic secrets attack the "long-lived static credential" root cause directly — the cluster's structural failure shape. |
| Frequency | PASS | Hit on every credential acquisition in a deployment that adopts it. |
| Survivorship | PASS | Vault is mature and widely deployed; not abandoned. |
| Anti-pattern | FAIL→reframe | The research's sharp caveat: Vault's AWS-engine **default lease is 768h (32 days)** — "effectively static unless explicitly overridden," plus the unsolved "Secret Zero" bootstrap. Mandating "use a secret manager" without mandating *short TTLs + bootstrap identity* is paperwork that yields static-equivalent secrets. |
| Complexity | PASS (for the control) | Referencing a secret manager the customer runs is low cost; the assurance only materialises if the template also mandates TTL governance. |

**Label: REFRAMED**
- **Original:** Require a secret manager (Vault/cloud).
- **Reframed:** Template control: *require dynamic/leased credentials from an external secret manager **with an explicitly governed short TTL** (call out the 768h default trap) and a documented bootstrap-identity (Secret Zero) story*, mapped to ISM credential lifecycle controls. The reframe rescues the anti-pattern failure by binding the requirement to TTL governance, without which "use Vault" is hollow. No build (external substrate).

---

## Pattern 9 — Gateway token vaulting & credential brokering (agent never sees the secret)

Per-user OAuth vaulting at a gateway, or placeholder-injection broker (CB4A).

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | "Agent never holds the real credential" structurally neutralises prompt-injection exfiltration — strongly load-bearing. |
| Frequency | PASS | Hit on every outbound tool call in a deployment that routes through a gateway. |
| Survivorship | PASS (with scar) | Shipping (TrueFoundry, Docker MCP Gateway, Aembit); the scar (mcp-remote CVE RCE; broker = high-value SPOF) is a deployment-hardening lesson, not abandonment. |
| Anti-pattern | PASS | Real assurance; the broker-SPOF caveat is a known design tension to document, not a reason to reject. |
| Complexity | FAIL (for build) | A live gateway/broker is exactly the runtime control plane agent-enterprise is *not* and the reposition says not to build. It is a vendor/infra product. |

**Label: DEFERRED**
**Unblock condition:** Only relevant if agent-enterprise ever ships a runtime gateway component (not in current proposal-tier scope) OR a vendor-neutral broker standard matures. Until then the template can *recommend* credential brokering as a hardening pattern but cannot mandate or build it. Surface in flaggedDecisions.

---

## Pattern 10 — MCP tool allow-list (deny-by-default virtual keys / tool groups)

Bind each consumer to an explicit per-server tool allow-list; non-listed tools invisible + blocked.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | Least-tool-surface is load-bearing: the GitHub MCP injection happened precisely because no allow-list was present. |
| Frequency | PASS | Every agent-tool binding hits this; agent-enterprise *defines agent tool access in its own configs*, so it touches this directly. |
| Survivorship | PASS | Shipping in MCP spec v2025-11-05, ServiceNow, Maxim; wildcard `["*"]` documented as the anti-pattern. |
| Anti-pattern | PASS | Real attack-surface reduction; not box-ticking. |
| Complexity | PASS | Buildable in-repo as a template convention: agent-enterprise can require explicit per-agent tool allow-lists in its agent definitions and forbid wildcards — and map it to Essential Eight "application control." |

**Label: NEW**
Origin: a template convention agent-enterprise can adopt for its own agent definitions (deny-by-default tool allow-lists, no wildcards) plus a mapped control for downstream AU-gov deployments. This overlaps Cluster 8 (tool-surface control) — note the boundary; the *identity* angle here is "allow-list bound to the agent principal." Treat as VALIDATED per NEW.

---

## Pattern 11 — Declarative policy engine at the agent-tool boundary (Cedar / OPA / Cerbos)

Intercept every tool call; evaluate principal + action + input params against policy before execution.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | Per-call evaluation is the emerging answer to "authorized to call ≠ this call was intended" — the cluster's deepest unmet need. |
| Frequency | PASS | Fires on every tool call where deployed. |
| Survivorship | PASS | OPA 100M+ downloads, Cedar GA; CNCF 2026 recommended stack. Not abandoned. |
| Anti-pattern | PASS | Real assurance (call-level authz), with documented fail-open risk to call out. |
| Complexity | FAIL (for build) | A live PDP at a tool boundary is a runtime control plane — out of scope per reposition. Rego is "30-40h learning"; this is infra the customer runs, not something a prompt-artifact template builds. |

**Label: DEFERRED**
**Unblock condition:** Relevant only if a runtime enforcement component enters scope, OR as an *advanced* template recommendation for high-assurance AU-gov deployments (reference Cedar/OPA + AuthZEN, flag fail-closed requirement). Currently document as recommended hardening, not a mandated/built control. Surface in flaggedDecisions.

---

## Pattern 12 — OAuth 2.1 scoped-token architecture + downscoping (RFC 8693 / 9396)

Per-tool scopes (`tool:resource:action`), no wildcards; token exchange for sub-agent downscoping.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | Narrow short-lived scoped tokens attack over-permissioning directly (Zylos: 74% of agents over-permissioned). Load-bearing. |
| Frequency | PASS | Every authenticated agent action; OAuth 2.1 is mandated by MCP for remote servers. |
| Survivorship | PASS (with scar) | OAuth underpins enterprise auth; the scar (EchoLeak exploiting too-broad-but-legitimate grants) reinforces "scope tighter," not "abandon." |
| Anti-pattern | FAIL→reframe | The research flags **scope-format fragmentation** (`access_mcp` vs `mcp:tools:*` vs `tool:calendar:read`, no interop) and **no standardized delegation-depth limit**. Mandating "use scoped tokens" without picking/standardising a vocabulary risks an opaque single-scope cop-out that defeats the granularity — paperwork over assurance. |
| Complexity | PASS (for the control) | Referencing OAuth 2.1 + least-scope is low cost; the assurance depends on the template specifying *least-privilege scope + bounded delegation depth*. |

**Label: REFRAMED**
- **Original:** Require OAuth 2.1 scoped tokens.
- **Reframed:** Template control: *require OAuth 2.1 + PKCE, least-privilege per-tool scopes (no wildcards), and a bounded delegation-chain depth* — and pick a single internal scope convention for agent-enterprise's own examples so the template isn't hollow. Mapped to ISM authentication controls. The reframe rescues the fragmentation failure by mandating bounded scope/depth rather than "use OAuth." No runtime build.

---

## Pattern 13 — Relationship-based authorization (ReBAC / Zanzibar)

Authz from graph traversal over (subject, relation, object) tuples; prevents lateral movement.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | Graph isolation genuinely prevents sibling-node lateral movement (the Asana MCP cross-tenant flaw is the negative case). |
| Frequency | N/A | Only relevant to deployments with rich relationship/resource graphs; many AU-gov agent pilots won't have this shape. |
| Survivorship | PASS | Google/Slack/Airbnb scale; commercial FGA exists. Not abandoned. |
| Anti-pattern | PASS | Real assurance where the data model warrants it. |
| Complexity | FAIL (for build/mandate) | Needs careful upfront schema; RBAC→graph is "a real migration"; tuple-sync latency causes stale decisions. Far beyond proposal-tier template scope to mandate. |

**Label: DEFERRED**
**Unblock condition:** Reference as an *optional advanced* authz model for AU-gov deployments with complex resource graphs; do not mandate. Re-evaluate if a deployment with that data shape becomes a concrete target. Surface in flaggedDecisions.

---

## Pattern 14 — Vendor permission sets & the "dynamic user" trap

Reuse platform RBAC; Salesforce/ServiceNow "Dynamic user" inherits the invoking human's permissions.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS (inverted) | The research is clear this is a **structural confused-deputy** shipped as a default by two major platforms — the load-bearing insight is what to *prohibit*, not adopt. |
| Frequency | PASS | Any AU-gov deployment on Salesforce/ServiceNow could hit the dynamic-user default. |
| Survivorship | PASS (cautionary) | Shipping and in use — and named as a built-in confused deputy. Survivorship lesson: avoid the dynamic-user mode. |
| Anti-pattern | PASS | Prohibiting dynamic-user inheritance produces real assurance against privilege escalation. |
| Complexity | PASS | Low cost as a template *prohibition* + guidance (prefer fixed permission sets, forbid dynamic-user inheritance for privileged agents). |

**Label: REFRAMED**
- **Original (research framing):** A pattern to adopt.
- **Reframed:** Template control as a **prohibition/caution**: *for AU-gov deployments, forbid "dynamic user" permission inheritance for privileged agents; require fixed, least-privilege permission sets*, mapped to PSPF/Essential Eight restrict-admin-privileges. The reframe flips an adopt-pattern into a guardrail, which is where its value sits. Candidate NON_GOAL entry.

---

## Pattern 15 — Human-in-the-loop step-up authorization (CIBA / tool-approval)

PDP risk-scores actions; high-risk triggers out-of-band human approval before resume.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | Human gating on high-risk actions is endorsed in NIST AI RMF 1.1 + EU AI Act for high-risk systems — directly load-bearing for AU-gov high-assurance contexts. |
| Frequency | PASS | Relevant whenever an agent performs irreversible/high-risk actions, common in gov workflows. |
| Survivorship | PASS | Shipping (Copilot Studio, Agent Framework ToolApproval, LangGraph). Not abandoned. |
| Anti-pattern | FAIL→reframe | The research's exact warning: **approval fatigue → rubber-stamping** ("93% of prompts approved," same as Cluster 1). A blanket "require human approval" mandate degrades into theatre. Assurance requires *risk-scoped* gating, not gate-everything. |
| Complexity | PASS (for the control) | As a template control (require HITL for a defined high-risk action class) cost is policy definition, not infra. |

**Label: REFRAMED**
- **Original:** Require human-in-the-loop approval.
- **Reframed:** Template control: *require HITL step-up only for a defined high-risk/irreversible action class (financial, deletion, privilege change), explicitly to avoid approval fatigue*, mapped to NIST AI RMF / EU AI Act / emerging AU agentic guidance. The reframe rescues the anti-pattern failure by scoping the gate to high-risk actions rather than all actions. No runtime build (the substrate is the deployment platform's approval mechanism).

---

## Pattern 16 — Interop/provisioning standards (SCIM-for-agents, AuthZEN)

`/Agents` SCIM extension for lifecycle provisioning; AuthZEN standard PEP↔PDP API.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| Causation | PASS | Standard provisioning/deprovisioning + engine-neutral authz would close real portability and lock-in gaps. |
| Frequency | N/A | Pre-adoption — enterprises are evaluating, not deploying. |
| Survivorship | N/A | Too early; "no production impls yet" for SCIM agent ext. |
| Anti-pattern | PASS | Right-direction standards, real assurance if adopted. |
| Complexity | FAIL (timing) | Drafts only; full RFC stack ~2027-2028. Mandating a draft standard in a proposal-tier template is premature and risks betting on a non-converging spec ("early-2000s SSO-style lock-in" warned). |

**Label: DEFERRED**
**Unblock condition:** SCIM agent extension reaches production implementations / AuthZEN 1.0 sees broad adoption (research: consolidation at IETF 125 Mar 2026, no prod impls yet). Until convergence, the template should *watch* these and avoid betting on one. Surface in flaggedDecisions.

---

## Summary table

| # | Pattern | Label |
| --- | --- | --- |
| 1 | Dedicated agent-identity principal (Entra Agent ID class) | REFRAMED |
| 2 | Federated delegation token (Okta XAA / ID-JAG) | DEFERRED |
| 3 | Cryptographic workload identity (SPIFFE/SPIRE) | DEFERRED |
| 4 | Cloud IAM service-role pattern (AWS/Google) | VALIDATED |
| 5 | NHI-governance overlay | REFRAMED |
| 6 | Plaintext secrets in config/env (anti-pattern guardrail) | NEW |
| 7 | OS-native keychain / encrypted local storage | VALIDATED |
| 8 | Secret-manager dynamic/leased credentials (Vault) | REFRAMED |
| 9 | Gateway token vaulting & credential brokering | DEFERRED |
| 10 | MCP tool allow-list (deny-by-default) | NEW |
| 11 | Declarative policy engine at tool boundary (Cedar/OPA) | DEFERRED |
| 12 | OAuth 2.1 scoped tokens + downscoping | REFRAMED |
| 13 | Relationship-based authorization (ReBAC/Zanzibar) | DEFERRED |
| 14 | Vendor permission sets / "dynamic user" trap | REFRAMED |
| 15 | Human-in-the-loop step-up authorization | REFRAMED |
| 16 | Interop/provisioning standards (SCIM-for-agents, AuthZEN) | DEFERRED |

**Cleared to hand off to `@planner` now (template-control catalogue + thin in-repo builds):** Patterns 4, 6, 7, 10, plus the reframed controls 1, 5, 8, 12, 14, 15. The two genuine in-repo builds are Pattern 6 (secrets-hygiene build-time guard) and the schema/convention additions in Patterns 1 and 10. Everything else is reference/map or deferred.

**Open question for the user (do not let me decide this):** the highest-leverage *buildable* item is the Pattern 6 secrets-hygiene guard, because it is the one control that (a) attacks the cluster's largest documented harm source and (b) fits prompt-artifact scope. The rest of the cluster is a compliance-mapping exercise against ISM/Essential Eight/PSPF. Do you want the first sprint to be "build the secrets guard," or "write the AU-gov control-mapping catalogue," or both in parallel — what do you think?
