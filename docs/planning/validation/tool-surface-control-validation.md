# Validation: Tool-surface control (Cluster 3)

**Date:** 2026-06-15
**Validator:** `@pm`
**Source research:** `docs/planning/research/tool-surface-control-research.md`
**Framework:** `.github/instructions/validation-framework.instructions.md` (5-test echo-chamber filter)
**Label scope:** one label per distinct pattern.

---

## Chosen frame and rationale

**Frame: (a) controls the AU-gov compliance template should reference/map to — with two narrow MIXED exceptions.**

Why this frame, not "novel substrate features":

- On **2026-06-01** agent-enterprise's two original "novel safety substrate" claims were disconfirmed as novel. The repositioned product is an **Australian-government compliance template, proposal-tier** — a build-time, consumption-side defensive artifact (mapping controls to AU-gov frameworks such as the ISM/Essential Eight and giving teams a vetted template for *how to consume* agent tooling safely). It is not a runtime tool-router, gateway, or sandbox.
- Every pattern in this research (tool-budget, staged retrieval, code-mode, gateways, namespacing/poisoning defenses) is a **runtime mechanism shipped by interested vendors** (Anthropic, Cloudflare, Docker, Kong, GitHub, OpenAI). Building any of them would be re-implementing a vendor substrate the repositioning explicitly walked away from. Re-deriving them as "our features" repeats the exact mistake the 2026-06-01 disconfirmation corrected.
- The template's real job here is to **convert these mechanisms into control objectives, configuration requirements, and vetting checklists** that an AU-gov team can map to its accreditation evidence. That is a documentation/compliance contribution, not an engineering one — and it is genuinely valuable because the failure modes (tool poisoning, rug pulls, name-collision shadowing, unverifiable benchmarks) are precisely the things a compliance reviewer must force a consuming team to address.
- **Two MIXED exceptions** exist where a *thin build-time check could plausibly live inside the template's own consumption pipeline* (which already does build-time defense against supply-chain injection per project memory): static scanning of tool/MCP descriptions, and checksum-pinning of tool definitions. These are consumption-time integrity gates, not runtime substrate, so they are frame-consistent if scoped as template-enforced build checks rather than a live gateway.

**Net:** treat Patterns 1–4 primarily as control-mappings the template references; treat the integrity defenses inside Pattern 5 as the one place where a build-time enforcement contribution is in-scope.

---

## Pattern inventory

| # | Pattern | Vault candidate | Label |
| --- | --- | --- | --- |
| 1 | Tool-budget limits & catalog curation | `[[tool surface budget]]` | REFRAMED |
| 2 | Tool search / dynamic discovery (staged retrieval) | `concept-staged-retrieval-and-tool-mediated-access` | REJECTED |
| 3 | Code-mode / filesystem-style interfaces | `concept-filesystem-style-interfaces` | REJECTED |
| 4 | MCP gateways / proxies / registries | `concept-mcp-open-standard` | REFRAMED |
| 5a | Namespacing discipline (collision avoidance) | cross-cuts | REFRAMED |
| 5b | Tool-description scanning + definition checksum-pinning (build-time integrity) | (failure-cluster defense) | DEFERRED |
| 6 | MCP-as-substrate (the standard itself) | `concept-mcp-open-standard` | REFRAMED |

---

## Pattern 1 — Tool-budget limits & catalog curation

A hard cap / hand-prune of the tool surface (allow-block lists, default toolsets, "one agent one job"). Strong adoption signal: GitHub cut its default surface after 101 tools = 64.6k tokens.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | The token/accuracy degradation is causally tied to surface size (GitHub's own before/after, multiple chance-corrected papers); curation directly attacks the cause for small surfaces. |
| 2. Frequency match | PASS | Build-time/config concern, not engagement-cadence-dependent; matches a template that is consulted per-deployment rather than daily. |
| 3. Survivorship bias | PASS | The research itself flags the failure side (manual curation doesn't scale, silent capability gaps), so we are not only seeing the winners. |
| 4. Anti-pattern / engagement-at-cost | PASS | No engagement-farming dimension; pure cost/correctness control. |
| 5. Complexity cost | FAIL | As a *substrate feature* the cost is wrong — it is a vendor-owned runtime concern (OpenAI `allowed_tools`, GitHub toolsets). Re-building it ourselves is unjustified; the value is in *requiring* it, not coding it. |

**Label: REFRAMED.**
- **Original:** "Build a tool-budget / curation mechanism."
- **Reframed:** "The AU-gov template references a **tool-surface-budget control objective**: a consuming team must declare a bounded, least-privilege tool allow-list per agent role and cite the vendor mechanism enforcing it (e.g. `allowed_tools`, GitHub default toolsets)." The reframe rescues it by moving from build-it to require-and-map-it, which fixes Test 5 while preserving the validated causal value (Tests 1–4).

---

## Pattern 2 — Tool search / dynamic discovery (staged retrieval)

Keep one search tool in context; `defer_loading` the rest; BM25/embedding retrieval expands defs on demand (Anthropic Tool Search, RAG-MCP, GitHub dynamic toolsets).

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Retrieval demonstrably triples selection accuracy and cuts tokens >50% (RAG-MCP), so it causally addresses overload — within its range. |
| 2. Frequency match | PASS | Runtime-cadence concern but not engagement-driven; n/a to template frequency mismatch. |
| 3. Survivorship bias | FAIL | RAG-MCP's own stress test shows retrieval precision collapses past ~100 tools and recall misses are *silent capability loss*; the cure inherits the disease's ceiling. We would be copying a partially-failing approach. |
| 4. Anti-pattern / engagement-at-cost | PASS | No engagement-farming; legitimate efficiency mechanism. |
| 5. Complexity cost | FAIL | This is a live ranking/retrieval system owned by model vendors; building a retrieval index is squarely the runtime substrate the 2026-06-01 repositioning abandoned, and it is unreproducible-benchmark territory. |

**Label: REJECTED.**
Two non-rescuable failures for *us*: Test 3 (the mechanism has a documented hard ceiling and silent-failure mode) and Test 5 (it is a vendor runtime, not a compliance template's job). It is not even rescuable as a *required* control, because mandating retrieval would force consuming teams into an immature, ceiling-bound mechanism. The template should instead *note* staged retrieval as an optional vendor mitigation without requiring it. (No NON_GOALS entry — it is a "not for us to build," not a standing product no.)

---

## Pattern 3 — Code-mode / filesystem-style interfaces

Expose tools as a typed code API / `./servers/*.ts` filesystem; agent writes code in a sandbox to call them (Cloudflare Code Mode, Anthropic Code execution with MCP). Largest token wins (98.7%) but needs a sandbox and widens injection/RCE surface.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Token reduction is causally real (corpus-fit argument + multiple vendor numbers), even if vendor-reported. |
| 2. Frequency match | N/A | Not an engagement-cadence question; the pattern is architectural. |
| 3. Survivorship bias | FAIL | Months-old, not years-proven; key runtime (Cloudflare Worker Loader) is closed beta and Cloudflare's own post gives no benchmark — we'd be adopting an unsettled approach. |
| 4. Anti-pattern / engagement-at-cost | PASS | No engagement dimension. |
| 5. Complexity cost | FAIL | The largest token win comes with the largest *new attack surface* (Anthropic concedes injection/RCE exposure) and a mandatory sandbox runtime — exactly the runtime-substrate burden the repositioning rejected, and it pushes the security cost onto Cluster 1. |

**Label: REJECTED.**
Tests 3 and 5 fail non-rescuably. Adopting code-mode would re-make agent-enterprise into a sandboxed runtime substrate, contradicting the proposal-tier compliance-template positioning, and it imports an RCE blast-radius the template exists to *warn against*, not own. The template should reference it as a high-risk advanced option whose adoption triggers Cluster 1 sandboxing controls.

---

## Pattern 4 — MCP gateways / proxies / registries

An intermediary aggregating N servers behind one endpoint with filtering, namespacing, RBAC, audit, scanning (Docker MCP Gateway, Kong, Azure APIM/API Center, Stacklok ToolHive vMCP). Registry ~9,652 servers.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Gateways causally provide the RBAC/audit/isolation chokepoint enterprises need; the control value (governance, credential brokering, call-tracing) is real and the thing AU-gov accreditation cares about. |
| 2. Frequency match | PASS | Governance/audit cadence aligns with a compliance template's per-deployment review model. |
| 3. Survivorship bias | PASS | Research flags the downside honestly (gateway = single trust chokepoint, aggregation can re-create overload), so we see both sides. |
| 4. Anti-pattern / engagement-at-cost | PASS | Pure governance value, no engagement-farming. |
| 5. Complexity cost | FAIL | Building a gateway is a major runtime substrate (Kong/Docker/Azure are full products); wrong cost for a proposal-tier template. The value to us is *mandating and mapping* a gateway's controls, not coding one. |

**Label: REFRAMED.**
- **Original:** "Provide an MCP gateway/registry capability."
- **Reframed:** "The template references a **mediated-tool-access control objective**: AU-gov agent deployments must route third-party MCP servers through a governed gateway providing RBAC, audit logging, credential brokering, isolation, and an approved-server catalog — mapped to ISM/Essential Eight controls — and must treat the gateway as a single point of failure requiring its own hardening evidence." Reframe rescues Test 5 by requiring/mapping rather than building, while preserving the validated governance value.

---

## Pattern 5a — Namespacing discipline (collision avoidance)

Prefix tools `server.tool` / `mcp_<server>_<tool>` to prevent "last-registered-wins" shadowing. Client-dependent; not in base MCP spec.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Collisions causally enable tool-shadowing/override attacks (documented: GitHub & Linear both expose `create_issue`); namespacing directly removes the cause. |
| 2. Frequency match | N/A | Configuration-time concern, no cadence dimension. |
| 3. Survivorship bias | PASS | The failure (collisions, cross-service call breakage, OpenAI SDK #464) is the very evidence motivating it. |
| 4. Anti-pattern / engagement-at-cost | PASS | No engagement dimension; security hygiene. |
| 5. Complexity cost | PASS (as control) / FAIL (as build) | As a *required configuration control* it is near-zero cost and high value; as a substrate feature there is nothing for us to build since it is host/client behavior. |

**Label: REFRAMED.**
- **Original:** "Implement namespacing."
- **Reframed:** "The template mandates a **unique-tool-namespace control**: any AU-gov deployment wiring more than one MCP server must enforce host-side tool-name prefixing and document the resolution rule, to prevent shadowing/override." Reframe is trivial and high-leverage: it is the cheapest control in the cluster and closes a real attack class.

---

## Pattern 5b — Tool-description scanning + tool-definition checksum-pinning (build-time integrity)

Static scan of MCP tool descriptions for poisoned/`<IMPORTANT>` injection payloads (mcp-scan lineage), plus checksum-pinning of tool definitions to detect rug-pulls (definition changes silently after approval). MCP ships no integrity, no description-trust boundary.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Directly addresses documented attack chains (Invariant Labs tool poisoning reading `~/.ssh/id_rsa`; rug-pulls against WhatsApp/GitHub MCP); scanning + pinning causally close them. |
| 2. Frequency match | PASS | Build/consumption-time integrity check fits agent-enterprise's existing build-time defensive model (per project memory: build-time defense vs supply-chain injection). |
| 3. Survivorship bias | PASS | The vulnerability classes are well-documented with multiple academic taxonomies; not a hype-only signal. |
| 4. Anti-pattern / engagement-at-cost | PASS | Pure safety; no engagement dimension. |
| 5. Complexity cost | PASS (in principle) | A build-time scan + checksum-pin is bounded and aligns with the template's consumption pipeline — but it depends on the vault/consumption-pipeline scope being defined, which is not yet settled. |

**Label: DEFERRED.**
This is the one genuinely in-scope build-time contribution (MIXED frame): it lives in consumption/build defense, not runtime substrate, and matches the project's stated design core. It is **deferred, not validated**, because the unblock conditions are unmet: (1) the consumption-pipeline / vault scope that would host the check is not yet defined, and (2) it overlaps Cluster 1 (sandboxing) and the identity/credentials cluster — sequencing must be resolved before scoping. **Unblock condition:** consumption-pipeline scope confirmed AND cross-cluster ownership (vs Cluster 1) resolved. *(Note: framework says DEFERRED items go to ROADMAP "Parked"; ROADMAP.md does not exist, so this is surfaced in flaggedDecisions instead.)*

---

## Pattern 6 — MCP-as-substrate (the standard itself)

MCP is the open protocol the whole cluster sits on; now a Linux Foundation standard (~97M monthly SDK downloads, 9,400–10,000+ servers, adopted by OpenAI/Google/Microsoft).

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | MCP is causally why large heterogeneous tool surfaces (and their failure modes) exist; it is the substrate, not a copyable feature. |
| 2. Frequency match | N/A | A protocol standard, not a feature with a usage cadence. |
| 3. Survivorship bias | PASS | It is the dominant standard, but the research documents its gaps (no namespacing, no integrity, no trust boundary), so we are not blind to its weaknesses. |
| 4. Anti-pattern / engagement-at-cost | N/A | Not a feature; no engagement dimension. |
| 5. Complexity cost | FAIL (as build) | "Building MCP" is nonsensical; it is an external standard we consume, not implement. |

**Label: REFRAMED.**
- **Original:** "MCP as a substrate feature."
- **Reframed:** "The template treats MCP as the **assumed integration substrate** and names its three documented spec-level gaps — no mandatory namespacing, no tool-definition integrity, no description-trust boundary — as **explicit residual risks the consuming team must mitigate out-of-band** (covered by Patterns 5a/5b controls)." Reframe rescues it by converting "feature" into "documented substrate assumption + residual-risk register," which is exactly a compliance template's job.

---

## Summary

Of six distinct patterns, **none validate as substrate features to build** — consistent with the 2026-06-01 repositioning. Four (Patterns 1, 4, 5a, 6) **REFRAME cleanly into control objectives / required configurations / residual-risk entries** the AU-gov compliance template should reference and map to its accreditation frameworks. Two (Patterns 2, 3) are **REJECTED for us**: staged retrieval has a documented hard ceiling and silent-failure mode (and is a vendor runtime), and code-mode imports an RCE blast radius plus a closed-beta runtime that contradicts proposal-tier positioning — both should be *mentioned* by the template as optional/high-risk vendor mitigations, not required or built. One (Pattern 5b — build-time description-scanning + checksum-pinning) is the single in-scope **DEFERRED** build contribution, matching the project's build-time-defense core, blocked on consumption-pipeline scope and Cluster 1 ownership.

The strongest near-term, lowest-cost wins are **Patterns 5a (namespacing) and 1 (tool-budget)** as required controls. The strongest eventual build candidate is **5b**, pending scope resolution.
