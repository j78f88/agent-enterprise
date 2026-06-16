---
title: "Research: Tool-surface control for agent systems (Cluster 3)"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-15
---

# Research: Tool-surface control for agent systems (Cluster 3)

**Date:** 2026-06-15
**Requested by:** user (via `vault-candidates-research-brief.md`, Cluster 3)
**Scope:** How agent systems bound and gate large tool surfaces — tool-search / dynamic discovery, MCP gateways and registries, filesystem-style ("code mode") interfaces over API/MCP dumps, staged/progressive retrieval, tool-budget limits, and namespacing. For each: the concrete mechanism, MCP's role, who ships it, adoption scale where findable, and the documented failure modes (selection-accuracy collapse past N tools, context bloat, tool-name collisions, tool poisoning / rug pulls, abandoned approaches).

> Surfaces patterns + evidence + failure modes only. No recommendations and no 5-test validation — kill/keep is `@pm`'s call. **Vault provenance:** `[[tool surface budget]]`, `concept-large-mcp-tool-surfaces-degrade`, `concept-filesystem-style-interfaces`, `concept-staged-retrieval-and-tool-mediated-access`, `concept-mcp-open-standard`.

## Synthesis — the mechanisms, who ships what, and where it breaks

The "too many tools" problem became real the moment MCP made it trivial to bolt dozens of servers onto one agent. The default MCP wire pattern injects **every tool definition from every connected server into context on every request**, so tool surface scales linearly with context cost and *inversely* with selection accuracy. The industry response has converged into **five stacked control mechanisms**, each a distinct vault candidate, each with its own adoption curve and its own documented failure class:

| Mechanism | Vault candidate | What it does | Who ships it | Adoption signal | Where it breaks |
| --- | --- | --- | --- | --- | --- |
| **Tool-budget / curation** | `[[tool surface budget]]` | Hard-cap or hand-prune the tool list; "default toolsets"; one-agent-one-job | GitHub MCP (default toolsets), OpenAI `allowed_tools`, OpenAI Agents SDK static filter | GitHub cut default surface after 101 tools = 64.6k tokens | Manual; doesn't scale to thousands; still degrades past ~5–20 tools |
| **Tool search / dynamic discovery** | `concept-staged-retrieval-and-tool-mediated-access` | Load only a search tool upfront; `defer_loading`; BM25/regex/embedding retrieval expands defs on demand | Anthropic Tool Search Tool (+ Claude Code), RAG-MCP, GitHub dynamic toolsets | Anthropic: 85% token cut; Opus 4 49%→74% MCP eval | Retrieval precision degrades past ~100 tools (RAG-MCP); recall misses → silent capability loss |
| **Code-mode / filesystem interface** | `concept-filesystem-style-interfaces` | Present tools as a typed code API / `./servers/*.ts` filesystem; agent writes code that calls them | Cloudflare Code Mode, Anthropic "Code execution with MCP", CodeAct lineage | Cloudflare: whole API in ~1k tokens; Anthropic: 150k→2k (98.7%) | Requires a code sandbox; expands injection / RCE surface; closed-beta runtimes |
| **MCP gateway / proxy / registry** | `concept-mcp-open-standard` | Aggregate many servers behind one endpoint; filter, namespace, RBAC, audit, scan | Docker MCP Gateway/Toolkit, Kong, Azure APIM/API Center, Stacklok ToolHive vMCP | Docker catalog 300+ servers; official registry ~9,652 servers | Gateway is a new trust chokepoint; aggregation re-creates the overload it solves |
| **Namespacing / naming discipline** | (cross-cuts all) | Prefix tools `server.tool` / `mcp_<server>_<tool>` to avoid collisions | Cursor, OpenAI Agents SDK, ToolHive vMCP | Client-dependent; not in base spec | Collisions = "last registered wins" → malicious override / tool shadowing |

**Finding 1 — The degradation is measured, not folklore, but the headline numbers come from interested parties.** Multiple independent threads converge on the same shape: accuracy holds at small tool counts and falls as the surface grows, while token cost grows linearly. The **RAG-MCP paper (arXiv 2505.03275)** is the strongest peer-style evidence — retrieval-based selection more than **tripled tool-selection accuracy (43.13% vs 13.62% baseline)** and cut prompt tokens >50%, but the authors themselves show **sharp degradation once the candidate pool exceeds ~100 tools**, calling retrieval "mandatory rather than optional beyond that scale." Anthropic's own MCP-eval numbers (Opus 4 **49%→74%**, Opus 4.5 **79.5%→88.1%** with Tool Search on) point the same way. The widely-cited **"MCP uses 35× more tokens than CLI tools, reliability drops to 72% on hard tasks"** figure is real and repeated everywhere, but the originating benchmark is **unnamed, unlinked, and unreproducible by the author's own admission** — treat as directional only.

**Finding 2 — Two architecturally different cures, both MCP-native.** The first cure keeps tool-calling but **stages the catalog** (Anthropic Tool Search Tool's `defer_loading`, RAG-MCP's vector index, GitHub's dynamic toolsets): only a search tool sits in context; full definitions are pulled on demand. The second cure **abandons direct tool-calling** and hands the model a code interface (Cloudflare Code Mode's `search()`/`execute()`; Anthropic's `./servers/*.ts` filesystem) on the premise — stated explicitly by Cloudflare — that "**LLMs are better at writing code to call MCP than at calling MCP directly**," because their training corpus is full of real code and starved of tool-call examples. Both report order-of-magnitude token cuts; the code-mode path reports the largest (Anthropic **98.7%**, 150k→2k), at the cost of needing a sandboxed runtime.

**Finding 3 — The control layer is also a new attack surface.** Tool descriptions are model-visible free text the agent reads every turn, which makes the tool surface itself an injection channel. **Invariant Labs' "tool poisoning" (Apr 2025)** showed hidden `<IMPORTANT>` instructions in a benign-looking `add()` tool's docstring directing the agent to read `~/.ssh/id_rsa` and `~/.cursor/mcp.json` and exfiltrate them — invisible to users who see only a summarized UI. **"Rug pulls"** exploit MCP's lack of content-addressing/integrity: a tool approved on day 1 silently changes definition on day 30. **Tool-name collisions** across servers (both GitHub and Linear expose `create_issue`) resolve to undefined, client-dependent "last-registered-wins" behavior, enabling **tool shadowing** where a malicious server hijacks a trusted tool's name. Gateways and registries that aggregate servers concentrate this risk into one chokepoint.

**Finding 4 — MCP is the substrate the whole cluster sits on, and it is now an industry standard.** Released by Anthropic Nov 2024; OpenAI adopted Mar 2025, Google DeepMind Apr 2025, Microsoft/GitHub joined the steering committee at Build 2025; donated to a Linux Foundation directed fund (AAIF) Dec 2025. Reported scale: **~97M monthly SDK downloads, 9,400–10,000+ public servers**. Every mechanism in this doc exists *because* MCP made large, heterogeneous tool surfaces cheap to assemble.

**Standing honesty caveat for `@pm`:** a large share of the token-saving and accuracy numbers below come from **vendor blogs marketing their own fix** (Anthropic, Cloudflare, Docker, Kong, Maxim, StackOne) — they are directionally consistent across vendors but each is an interested party. The **35× / 72% benchmark is explicitly unattributed**. The **$377-per-query / 1.15M-token at 508 tools** figure is from a Medium walkthrough, not a vendor or paper. Adoption counts (SDK downloads, registry server counts, catalog sizes) are vendor/registry self-reported snapshots. **Verify any number before quoting it as authoritative**, and re-pull registry/star/download counts at use time — they move weekly. This note also satisfies the researcher honesty-guard.

## Method

Parallel WebSearch/WebFetch sweeps on 2026-06-15 across six facets: (1) degradation studies/benchmarks; (2) tool-search & dynamic discovery; (3) code-mode/filesystem interfaces; (4) MCP gateways/registries/proxies; (5) namespacing & collisions; (6) tool-poisoning / rug-pull failure modes. Primary sources preferred and fetched in full where load-bearing: Anthropic engineering blog (advanced tool use, code execution with MCP), Cloudflare blog (Code Mode), the MCP registry blog/site, GitHub MCP-server issues/discussions, the RAG-MCP arXiv paper, and Invariant Labs' tool-poisoning write-up. Secondary/aggregator sources (Medium, DEV, vendor comparison blogs) used only for corroboration and flagged inline. Findings synthesized here; no recommendations added.

## Apps / sources surveyed

| System | Category | Mechanism | Scale signal |
| --- | --- | --- | --- |
| Anthropic Tool Search Tool | Dynamic discovery (API + Claude Code) | `defer_loading: true`; BM25/regex/embedding search; on-demand def expansion | 85% token cut; Opus 4.5 79.5%→88.1% MCP eval; in Claude Code (issue #12836) |
| Anthropic Programmatic Tool Calling | Code-mediated tool use | Claude writes Python in a code-exec env; tool results bypass context; `allowed_callers` | 43,588→27,297 tokens (37%); GAIA 46.5%→51.2% |
| Anthropic "Code execution with MCP" | Filesystem interface | MCP servers as `./servers/<srv>/<tool>.ts`; progressive disclosure; `./skills/` | 150k→2k tokens (98.7%) on the worked example |
| Cloudflare Code Mode | Filesystem/code interface | Two tools `search()`/`execute()`; MCP→TypeScript API; V8 isolate sandbox | Entire Cloudflare API in ~1,000 tokens; `@cloudflare/codemode` on npm; MCP-portal code mode (2026-03-26) |
| RAG-MCP (arXiv 2505.03275) | Staged retrieval (research) | Vector index of MCP metadata; retrieve top-k before prompting LLM | Accuracy 13.62%→43.13%; >50% token cut; degrades past ~100 tools |
| GitHub MCP server | Tool-budget + dynamic toolsets | 5 default + 17+ optional toolsets; runtime toolset enable; tool-specific config | 162+ tools; 101 enabled = 64.6k tokens; 3–10 tools = 60–90% context cut |
| OpenAI Agents SDK / Responses API | Tool filtering | `allowed_tools`; `create_static_tool_filter` allow/block; dynamic per-run filter | Native across Agents SDK + Responses API |
| Docker MCP Gateway / Toolkit | Gateway + catalog | Isolated containers; dot-notation enable/disable (`github.create_issue`); custom catalogs; call-tracing | Catalog 300+ servers; `docker/mcp-gateway` CLI plugin |
| Official MCP Registry | Registry | Community discovery API for servers/versions | ~9,652 latest / 28,959 version records (24 May 2026); preview Sep 2025 |
| Kong Enterprise MCP Gateway | Enterprise gateway | Plugin/policy engine auto-applies security+observability per server | GA enterprise product (2026) |
| Azure API Management / API Center | Enterprise gateway/governance | Register MCP tools for governance + discovery into Foundry inventory | Microsoft-first teams |
| Stacklok ToolHive (vMCP) | K8s-native gateway | Virtual MCP aggregation; tool prefixing by workload id; SSO/RBAC/audit | Okta/Entra integrations; K8s operator |
| Invariant Labs mcp-scan | Security scanner | Static scan of MCP configs for poisoned descriptions | `invariantlabs-ai/mcp-injection-experiments` |
| MCP (the standard) | Substrate | Open protocol for tool/resource exposure | ~97M monthly SDK downloads; 9,400–10,000+ public servers |

## Patterns found

### Pattern 1 — Tool-budget limits & catalog curation (the blunt instrument)

- **What it is:** Cap or hand-curate the tool list rather than discover it. Concrete forms: (a) **hard allow/block lists** — OpenAI's `allowed_tools` parameter filters which MCP tools the model sees per call, and the OpenAI Agents SDK ships `create_static_tool_filter(allowed_tool_names=…)` plus dynamic per-run filtering; (b) **default toolsets** — GitHub MCP ships 5 default toolsets for common operations and 17+ optional ones, so the out-of-box surface is a fraction of the 162+ available tools; (c) **design heuristics** — "one agent, one tool / one job," and informal budgets ("keep it under ~10–20 tools").
- **Source apps:** OpenAI Responses API + Agents SDK (`allowed_tools`, static/dynamic filters); GitHub MCP server (default toolsets, tool-specific config shipped 2025-12-10); general practitioner guidance (Medium, DEV, Lunar.dev, Jenova).
- **Adoption scale:** GitHub's move is the load-bearing data point — they cut the default surface *specifically because* "all tools enabled" meant **101 tools consuming 64.6k tokens by default**, causing "tool confusion," higher cost, and "out of the box" complaints (Discussion #1182, Issue #275). Loading 3–10 of the most-used tools yields a **~60–90% reduction in context-window usage** vs all default toolsets.
- **User complaints:** Manual curation doesn't scale to thousands of tools and pushes the selection burden onto the integrator. OpenAI users report `allowed_tools` "breaks my MCP call" (OpenAI community #1369470) — filtering has its own rough edges. Practitioners report performance problems emerging "once an agent has access to 5+ tools."
- **Failure mode:** Budgets fight the symptom, not the cause — even a curated list degrades as it grows. The chance-corrected study **"How Many Tools Should an LLM Agent See?" (arXiv 2605.24660)** and the **"Less is More: On the Selection of Tools for LLMs"** paper both show a negative correlation between tool count and accuracy; reported high-accuracy bands are narrow (≈2–6 unique tool calls for GPT-5/DeepSeek/Kimi-K2 in one analysis). Hard caps also create **silent capability gaps**: a needed tool that was pruned simply isn't available, with no signal to the model.

### Pattern 2 — Tool search & dynamic discovery (staged retrieval over the catalog)

- **What it is:** Keep tool-calling, but don't load the catalog. A single **search tool** sits in context (~500 tokens for Anthropic's); the full tool definitions are marked `defer_loading: true` and pulled in only when the model searches for them. Anthropic's Tool Search Tool offers **regex- and BM25-based search out of the box** plus a hook for custom embedding search; matched tools' references expand into full definitions on use. RAG-MCP generalizes this as **retrieval-augmented tool selection**: an external vector index of MCP metadata returns top-k candidates before the LLM is prompted. GitHub's **dynamic toolset discovery** lets the host list and enable toolsets at runtime in response to the prompt.
- **Source apps:** Anthropic **Tool Search Tool** (Claude Developer Platform; rolled into **Claude Code** for MCP, issue #12836); **RAG-MCP** (arXiv 2505.03275 + `fintools-ai/rag-mcp`); **GitHub MCP** dynamic toolsets (Issue #275). Third-party proxies (`toolception`, Lunar.dev) implement similar staged exposure.
- **Adoption scale:** Anthropic reports **85% token reduction** (a worked example drops 77K→8.7K tokens of tool overhead) and **accuracy gains on its internal MCP eval: Opus 4 49%→74%, Opus 4.5 79.5%→88.1%**, tested across 50+ tools spanning GitHub/Slack/Sentry/Grafana/Splunk and claimed to scale to "hundreds or thousands." Recommended threshold: enable when tool defs exceed ~10K tokens or 10+ tools. RAG-MCP reports **accuracy 13.62%→43.13%** and >50% token cut.
- **User complaints:** Third-party reviews flag it as **"not ready for production"** in some workflows (Growth Method on marketing workflows). The feature is new (late-2025/2026) and depends on the search returning the right tool — a non-obvious tuning problem. Community SDKs raced to add it (pydantic-ai #3590, Arcade, Tessl coverage), signaling it isn't yet universal.
- **Failure mode:** **Retrieval is itself a ranking problem that decays at scale.** RAG-MCP's own stress test shows retrieval precision and throughput **degrade sharply past ~100 candidate MCPs** — the cure has the same ceiling, just higher. A **recall miss is a silent failure**: if search doesn't surface the right tool, the agent behaves as if the capability doesn't exist. And the search index/descriptions are still attacker-influenceable (see Pattern 5).

### Pattern 3 — Code-mode / filesystem-style interfaces (skip tool-calling entirely)

- **What it is:** Stop exposing tools as JSON function schemas; expose them as a **typed code API** or a **filesystem of code modules**, and give the model a code-execution sandbox to *write a program* that calls them. Two concrete shapes: (a) **Cloudflare Code Mode** — exposes exactly two tools, `search()` and `execute()`, backed by an auto-generated TypeScript API (MCP schemas → TS interfaces with JSDoc); generated JS runs in a **V8 isolate** (Workers) with **zero internet by default**, reaching MCP servers only through `env` bindings that hide credentials. (b) **Anthropic "Code execution with MCP"** — presents servers as a `./servers/<server>/<tool>.ts` filesystem; the agent **explores the directory and reads only the tool files it needs**, can persist reusable helpers to `./skills/`, and PII is **"untokenized" via a client-side lookup** so real emails/phones flow service-to-service without entering the model context. Lineage: the **CodeAct** research pattern ("LLMs better at writing code than emitting tool calls").
- **Source apps:** Cloudflare **Code Mode** (`@cloudflare/codemode` on npm; `cloudflare/agents` repo; MCP-portal code mode shipped 2026-03-26); Anthropic **Code execution with MCP** (Nov 2025 engineering post) and the related **Programmatic Tool Calling** beta (`allowed_callers: ["code_execution_*"]`, Python in a code-exec env, tool results bypass context). Community reimplementations: `p2c2e/pydantic_mcp_code_execution`, `vrsen/mcp-code-exec-agent`, `ArtemisAI/code-execution-with-MCP`.
- **Adoption scale:** Token claims are the headline: Cloudflare exposes **the entire Cloudflare API in ~1,000 tokens** with two tools; Anthropic reports a workflow dropping **150,000→2,000 tokens (98.7%)**, and Programmatic Tool Calling cutting complex-research usage **43,588→27,297 (37%)** while lifting GAIA 46.5%→51.2%. Backed by major vendors (Cloudflare ships it in Workers; Anthropic in the Developer Platform), so this is not fringe — but it is months-old, not years-proven.
- **User complaints:** Both vendors concede the **operational tax**: code mode "requires a sandboxed runtime, resource limits, and monitoring" (Anthropic) and Cloudflare's **Dynamic Worker Loader API remains in closed beta**, "production-ready only for local dev via Wrangler" at time of writing. Cloudflare's own post provides **no token-count or benchmark for the converted API beyond qualitative "striking results"** — flag as marketing.
- **Failure mode:** **Letting the agent write and run code widens the blast radius.** Anthropic explicitly notes allowing agents to run code "increases exposure to injection risks and filesystem misuse." A prompt-injected agent in code mode can compose novel multi-tool exfiltration that no single tool-call guard anticipated; the sandbox (V8 isolate / container) becomes the only line of defense, which ties this pattern's safety directly to Cluster 1 (sandboxing). Token wins are real but **shift the catalog from context into a runtime the operator must now secure and pay for**.

### Pattern 4 — MCP gateways, proxies & registries (aggregate, filter, govern)

- **What it is:** Put an intermediary between the agent and N servers. A **gateway/proxy** aggregates many MCP servers behind one endpoint and adds filtering, namespacing, RBAC, audit logging, and isolation; a **registry** is the discovery directory of available servers. Docker's **MCP Gateway** runs each server in an isolated container with restricted privileges/network and built-in call-tracing, and lets you **enable/disable individual tools by dot-notation** (`github.create_issue`) or whole servers, with **custom catalogs** that expose only an approved subset instead of the full 300+ catalog. **Stacklok ToolHive's vMCP** aggregates servers and **prefixes every tool with the workload identifier** to guarantee unique names. Enterprise gateways (**Kong**, **Azure API Management / API Center**) auto-apply security/observability policy and surface tools into a governed inventory.
- **Source apps:** **Docker MCP Gateway + Toolkit + Catalog** (`docker/mcp-gateway`); **official MCP Registry** (`registry.modelcontextprotocol.io`, `modelcontextprotocol/registry`); **Kong Enterprise MCP Gateway**; **Azure API Management AI gateway + API Center**; **Stacklok ToolHive / vMCP**; plus the spec discussion on "servers that act as proxy clients to many servers" (modelcontextprotocol Discussion #94).
- **Adoption scale:** Docker catalog **300+ servers**, gateway shipped as a `docker mcp` CLI plugin and integrated into Docker Desktop. Official registry: **~9,652 latest server records / 28,959 server-version records as of 24 May 2026** (preview launched 8 Sep 2025); Anthropic's Dec 2025 ecosystem note cited **>10,000 active public servers**. The broader MCP standard reports **~97M monthly SDK downloads**. Enterprise gateways (Kong, Microsoft, Stacklok) are GA 2026 products targeting exactly this control problem.
- **User complaints:** The **"MCP composability trap"** (TianPan) — "just add another server" becomes dependency sprawl and version hell. Aggregation can **re-create the overload it was meant to solve**: a gateway fronting 20 servers still presents a huge surface unless it *also* filters/stages. Registry quality/trust is uneven (no universal vetting of the 10k servers).
- **Failure mode:** The gateway is a **single trust chokepoint and a single point of failure** — compromise or misconfiguration affects every downstream agent, and it sees every credential it brokers (SSO/RBAC features exist precisely because of this). Registries amplify **supply-chain risk**: a poisoned or rug-pulled server discovered via the registry inherits the registry's implied trust. Aggregation without integrity checking propagates tool poisoning/shadowing across the whole fleet (Pattern 5).

### Pattern 5 — Namespacing, tool-name collisions & tool poisoning (the failure cluster)

- **What it is:** Not a control mechanism but the failure surface the others must defend. **(a) Name collisions:** independent servers expose identically-named tools (both GitHub and Linear expose `create_issue`); the base MCP spec has no mandatory namespace, so resolution is **client-dependent — often "last registered wins,"** which lets a malicious or later server **shadow/override** a trusted tool. Clients patch this ad hoc: Cursor uses `mcp_<server>_<tool>`, others use `<server>/<tool>`, ToolHive prefixes by workload id. **(b) Tool poisoning:** because tool descriptions are model-visible free text read every turn, hidden instructions in a description are an injection channel. **(c) Rug pull:** definitions can change after first approval, and clients don't alert on the change — MCP has no content-addressing/integrity for tool defs.
- **Source apps / documented chains:** **Invariant Labs tool-poisoning notification (Apr 2025)** — a benign `add(a,b)` tool whose docstring hides `<IMPORTANT>` tags telling the agent to read `~/.ssh/id_rsa` and `~/.cursor/mcp.json` and exfiltrate them via tool args, with **Cursor** the demonstrated victim (UI shows only a summarized tool name; full description hidden); released `mcp-scan` + `mcp-injection-experiments`. **Shadowing attacks** inject instructions affecting *other* servers' tools (silent email redirection). **Collision bugs:** Cursor forum thread #70946 (cross-service call failures), OpenAI Agents SDK **Issue #464** (duplicate tool names cause errors), `vulnerablemcp.info` tool-name-collisions entry. **CyberArk "Poison everywhere: no output from your MCP server is safe."** **Rug pulls** demonstrated against WhatsApp and GitHub MCP servers within months of the coinage; an **npm supply-chain "meltdown"** hit the MCP package ecosystem (2026, per Glasp/security roundups — verify specifics).
- **Adoption scale:** N/A — vulnerability classes, broadly applicable to any agent wiring untrusted/third-party MCP servers. The relevant scale is exposure: 9,400–10,000+ public servers, most unvetted.
- **User complaints:** Integrators report that **the consumer has no control over a third-party server's tool names**, making two servers unusable together without host-side namespacing. Reviewers note confirmation dialogs are **security theater** when they hide the actual tool arguments/description from the user.
- **Failure mode:** The recurring fix is **out-of-band**, not in the protocol: scan descriptions (mcp-scan), pin versions by checksum, prefix names, and broker credentials at a gateway — because the base MCP spec ships **no integrity verification, no mandatory namespacing, and no description-trust boundary**. Academic taxonomies (arXiv 2603.18063 "MCP-38," 2509.06572 "Parasitic Toolchain Attacks," 2604.05969 formal framework) formalize the same gaps. Every aggregation/discovery mechanism in Patterns 2–4 inherits this unless it adds its own integrity layer.

## Unmet needs observed

- **No standard, in-protocol tool-budget or staged-retrieval primitive.** Tool search (Anthropic), dynamic toolsets (GitHub), and RAG (RAG-MCP) are vendor- or integrator-specific; the base MCP wire format still defaults to "ship every definition every turn."
- **Retrieval-based selection has its own ceiling (~100 tools).** Past it, both the disease (overload) and the cure (RAG/search) degrade — no robust answer yet for the thousands-of-tools regime the registry now enables.
- **Code-mode trades context cost for runtime/security cost.** It needs a sandbox (Cluster 1) and widens injection/RCE surface; the largest token wins come with the largest new attack surface, and key runtimes (Cloudflare Worker Loader) are still closed beta.
- **No mandatory namespacing in the MCP spec** — collisions resolve client-dependently ("last wins"), enabling shadowing/override; every host reinvents prefixing.
- **No integrity/content-addressing for tool definitions** — rug pulls are undetectable by default; mitigation means out-of-band scanning + checksum pinning that no client enforces natively.
- **Tool descriptions are an un-sandboxed injection channel** read every turn; UIs hide them from users, defeating human review.
- **Gateways centralize both control and risk** — they solve discovery/governance but become a credential-bearing single point of failure, and aggregation can re-create the overload it was meant to cure.
- **The headline degradation benchmarks are partly unverifiable** — the most-quoted "35× / 72%" figure has no published methodology; `@pm` should not weight it heavily without a reproduction.

## Sources

**Degradation studies / benchmarks** *(flag: 35×/72% benchmark is unattributed; 508-tool/$377 figure is a Medium walkthrough — verify before quoting)*
- RAG-MCP paper (arXiv 2505.03275) — https://arxiv.org/abs/2505.03275 ; PDF https://arxiv.org/pdf/2505.03275
- "How Many Tools Should an LLM Agent See? A Chance-Corrected Answer" (arXiv 2605.24660) — https://arxiv.org/html/2605.24660v2
- "MCP Servers Use 35x More Tokens Than CLI Tools…72% on Hard Tasks" (MindStudio) — https://www.mindstudio.ai/blog/mcp-servers-35x-more-tokens-cli-tools-reliability-benchmark
- "Cutting MCP Token Costs by 92% at 500+ Tools" (Maxim / Medium) — https://www.getmaxim.ai/articles/cutting-mcp-token-costs-by-92-at-500-tools/ ; https://medium.com/@hi.debmckinney/cutting-mcp-token-costs-by-92-at-500-tools-a-benchmark-walkthrough-b7d976c7e2c8
- "MCP Tool Overload: Why More Tools Make Your Agent Worse" (DEV) — https://dev.to/thedailyagent/mcp-tool-overload-why-more-tools-make-your-agent-worse-5a49
- MCP token optimization comparison (StackOne) — https://www.stackone.com/blog/mcp-token-optimization/
- "AI Tool Overload" / MCP scalability (Jenova) — https://www.jenova.ai/en/resources/mcp-tool-scalability-problem
- "Less is More: On the Selection of Tools for LLMs" (referenced) — see arXiv listing via the above

**Tool search / dynamic discovery (primary)**
- Anthropic, "Introducing advanced tool use" (Tool Search + Programmatic Tool Calling) — https://www.anthropic.com/engineering/advanced-tool-use
- Tool search tool — Claude API docs — https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool
- Claude Code issue #12836 (Tool Search / Programmatic Tool Use betas) — https://github.com/anthropics/claude-code/issues/12836
- Arcade analysis — https://blog.arcade.dev/anthropic-tool-search-claude-mcp-runtime ; Tessl — https://tessl.io/blog/anthropic-brings-mcp-tool-search-to-claude-code/ ; "not ready for production" (Growth Method) — https://growthmethod.com/anthropic-tool-search/
- pydantic-ai tool search issue #3590 — https://github.com/pydantic/pydantic-ai/issues/3590

**Code-mode / filesystem interfaces (primary)**
- Anthropic, "Code execution with MCP" — https://www.anthropic.com/engineering/code-execution-with-mcp ; coverage: https://www.marktechpost.com/2025/11/08/anthropic-turns-mcp-agents-into-code-first-systems-with-code-execution-with-mcp-approach/
- Cloudflare, "Code Mode: the better way to use MCP" — https://blog.cloudflare.com/code-mode/ ; "give agents an entire API in 1,000 tokens" — https://blog.cloudflare.com/code-mode-mcp/
- Cloudflare Agents codemode docs — https://developers.cloudflare.com/agents/model-context-protocol/protocol/codemode/ ; repo https://github.com/cloudflare/agents/tree/main/packages/codemode ; npm https://www.npmjs.com/package/@cloudflare/codemode ; MCP-portal code mode changelog — https://developers.cloudflare.com/changelog/post/2026-03-26-mcp-portal-code-mode/
- InfoQ on Code Mode — https://www.infoq.com/news/2026/04/cloudflare-code-mode-mcp-server/

**Tool-budget / filtering**
- GitHub MCP toolsets (DeepWiki) — https://deepwiki.com/github/github-mcp-server/3-github-toolsets ; default toolsets Discussion #1182 — https://github.com/github/github-mcp-server/discussions/1182 ; dynamic tool selection Issue #275 — https://github.com/github/github-mcp-server/issues/275 ; tool-specific config changelog — https://github.blog/changelog/2025-12-10-the-github-mcp-server-adds-support-for-tool-specific-configuration-and-more/
- OpenAI Agents SDK MCP filtering (DeepWiki) — https://deepwiki.com/openai/openai-agents-python/11.3-mcp-tool-discovery-and-filtering ; docs https://openai.github.io/openai-agents-python/mcp/ ; `allowed_tools` bug — https://community.openai.com/t/allowed-tools-breaks-my-mcp-call/1369470
- OpenAI MCP/connectors guide — https://developers.openai.com/api/docs/guides/tools-connectors-mcp

**Gateways / registries / proxies**
- Docker MCP Gateway — https://docs.docker.com/ai/mcp-catalog-and-toolkit/mcp-gateway/ ; Toolkit/Gateway explained — https://www.docker.com/blog/mcp-toolkit-gateway-explained/ ; repo https://github.com/docker/mcp-gateway ; catalog https://docs.docker.com/ai/mcp-catalog-and-toolkit/catalog/
- Official MCP Registry — https://registry.modelcontextprotocol.io/ ; preview blog https://blog.modelcontextprotocol.io/posts/2025-09-08-mcp-registry-preview/ ; repo https://github.com/modelcontextprotocol/registry ; adoption stats https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol
- Kong Enterprise MCP Gateway — https://konghq.com/blog/product-releases/enterprise-mcp-gateway
- Azure API Management AI gateway — https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities
- Stacklok ToolHive / vMCP tool aggregation — https://docs.stacklok.com/toolhive/ ; https://docs.stacklok.com/toolhive/guides-vmcp/tool-aggregation ; platform https://stacklok.com/platform/
- MCP proxy-of-many-servers spec discussion #94 — https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/94

**Namespacing & collisions**
- Cursor collision bug — https://forum.cursor.com/t/mcp-tools-name-collision-causing-cross-service-tool-call-failures/70946
- OpenAI Agents SDK duplicate tool names Issue #464 — https://github.com/openai/openai-agents-python/issues/464
- Vulnerable MCP — tool name collisions — https://vulnerablemcp.info/vuln/tool-name-collisions.html
- "Fixing MCP Tool Name Collisions" — https://www.letsdodevops.com/p/fixing-mcp-tool-name-collisions-when ; "MCP Composability Trap" — https://tianpan.co/blog/2026-04-13-mcp-composability-trap-dependency-sprawl

**Failure modes / security** *(verify CVE/incident specifics and the "npm meltdown" against primary advisories before quoting)*
- Invariant Labs tool poisoning — https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks ; experiments repo https://github.com/invariantlabs-ai/mcp-injection-experiments
- CyberArk "Poison everywhere: no output from your MCP server is safe" — https://www.cyberark.com/resources/threat-research-blog/poison-everywhere-no-output-from-your-mcp-server-is-safe
- MCP security / tool poisoning / rug pulls / npm supply chain (Glasp roundup) — https://glasp.co/articles/mcp-security-tool-poisoning-supply-chain
- Threat taxonomies — MCP-38 (arXiv 2603.18063) https://arxiv.org/pdf/2603.18063 ; Parasitic Toolchain Attacks (arXiv 2509.06572) https://arxiv.org/pdf/2509.06572 ; formal framework (arXiv 2604.05969) https://arxiv.org/pdf/2604.05969
- CSA Agentic MCP Security Best Practices — https://labs.cloudsecurityalliance.org/agentic/agentic-mcp-security-best-practices-v1/

**MCP standard / adoption provenance**
- OpenAI adopts MCP (TechCrunch, Mar 2025) — https://techcrunch.com/2025/03/26/openai-adopts-rival-anthropics-standard-for-connecting-ai-models-to-data/
- "A Year of MCP" (Pento) — https://www.pento.ai/blog/a-year-of-mcp-2025-review
- MCP on Wikipedia — https://en.wikipedia.org/wiki/Model_Context_Protocol
- MCP 2026 roadmap / enterprise adoption (Toloka) — https://toloka.ai/blog/the-future-of-mcp-enterprise-adoption/ ; WorkOS MCP-in-2026 — https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026

*No recommendations section by design — hand off to `@pm` for validation/prioritisation (the "research then triage" path).*
