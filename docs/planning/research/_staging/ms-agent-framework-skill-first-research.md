---
title: "Research: MS Agent Framework + Foundry skill-first 'agents that build agents' blueprint"
status: untrusted
trust: untrusted
classification: OFFICIAL
date: 2026-06-16
---

# Research: MS Agent Framework + Foundry skill-first "agents that build agents" blueprint

**Date:** 2026-06-16
**Requested by:** user (via `/researcher`, with source URL)
**Scope:** Validate the techcommunity blog "Agents That Build Agents: A SKILL-first Blueprint
with MS Agent Framework & Foundry" (Dave Rendon, Microsoft Azure & AI MVP) and surface the
externally-evidenced patterns it describes: the build-time vs run-time agent split, the
SKILL.md unit, Foundry's versioned Skills API, and MCP-resource skill discovery. Includes
adoption scale, primary-source corroboration, and documented failure modes.

> Surfaces patterns + evidence + failure modes only. No recommendations and no 5-test
> validation — kill/keep is `@pm`'s call. **Trust = untrusted:** the seed is a single
> MVP-authored vendor-adjacent blog; every load-bearing claim below is re-grounded against
> Microsoft Learn / first-party docs or flagged as unverified.

## Validation verdict (the "validate" half of the request)

**The article is legitimate and technically accurate — it is not vendor fiction.** Every
load-bearing technical claim it makes is independently corroborated by first-party Microsoft
sources (Microsoft Learn, devblogs.microsoft.com, github.com/microsoft) and by the
Anthropic-originated open SKILL.md standard. Caveats:

- **It is an opinion/architecture piece by one MVP, not Microsoft product documentation.** Dave
  Rendon is a Microsoft Azure & AI MVP; the post ran on the Azure Dev Community blog (community
  hub) and is cross-posted to his Medium/ITNEXT. The "blueprint," the two-layer naming
  ("Coding Agent" / "Runtime Agent"), and the `ZavaShop` worked example are **his framing**, not
  an official Microsoft reference architecture. `Zava/ZavaShop` is Microsoft's recurring
  fictional-retailer demo brand, used here as an illustration.
- **The substrate is real and shipping.** Microsoft Agent Framework is GA (1.0, Apr 2026);
  Foundry Skills are real but **public preview**. So the *pattern* is buildable today; the
  *Skills* leg of it carries preview risk (API churn, no GA SLA).
- **Could not retrieve the article body directly.** techcommunity, ITNEXT, Medium, and
  learn.microsoft.com all returned **HTTP 403** to the fetch tool in this environment. Findings
  below are reconstructed from search-engine extracts of those same pages plus corroborating
  first-party sources. Treat verbatim field names as high-confidence (they recur across the
  official Learn page and the microsoft/skills repo) and treat the article's *narrative* claims
  as single-sourced.

## Apps / sources surveyed

- **Microsoft Agent Framework** — github.com/microsoft/agent-framework; open-source agent SDK
  (.NET + Python). The merged successor to Semantic Kernel + AutoGen. **GA 1.0 shipped ~Apr 2026**
  (public preview Oct 2025 → RC → 1.0).
- **Microsoft Foundry Agent Service + Foundry Skills (preview)** — learn.microsoft.com Foundry
  agents docs; devblogs.microsoft.com/foundry. Hosted-agent runtime + versioned Skills catalog.
- **github.com/microsoft/skills** — Microsoft's public skills/MCP/custom-agent repo for grounding
  coding agents. **~2.1k stars, ~242 forks, ~133 skills** under `.github/skills/`; ships `Agents.md`
  and ~11 Foundry-agent-platform skills. (Star/fork counts are a June-2026 snapshot; re-pull at use.)
- **Anthropic Agent Skills / SKILL.md open standard** — platform.claude.com docs;
  github.com/anthropics/skills; agentskills.io. The origin format MS adopted wholesale.
- **MicrosoftDocs/Agent-Skills**, **microsoft/skills-for-fabric**, **microsoft/GitHub-Copilot-for-Azure**,
  **CrowdStrike/foundry-skills** — independent adopters shipping the same SKILL.md unit.

## Patterns found

### Pattern 1 — Build-time "Coding Agent" vs run-time "Runtime Agent" (two-layer split)

- **What it is:** "Build an agent" is decomposed into two jobs with almost nothing in common.
  The **Coding Agent** (build-time) *authors* the artifact — code, agent definition, tools,
  tests, docs — from a one-sentence requirement, behind validation gates. The **Runtime Agent**
  (run-time) is the thing the business actually operates in production. Microsoft Agent Framework
  is positioned as the single SDK that makes both layers feel like one conceptual model;
  Microsoft Foundry is the platform both publish to and run on.
- **Source apps:** Article (Rendon). The underlying "an agent/coding-assistant scaffolds another
  agent from a skill" mechanic is corroborated by github.com/microsoft/skills, whose tagline is
  literally "Skills, MCP servers, Custom Agents, Agents.md **for SDKs to ground Coding Agents**."
- **Adoption scale:** Agent Framework GA (1.0, Apr 2026), .NET + Python. microsoft/skills ~2.1k
  stars. The generic "agents that build agents" framing is widespread across vendors in 2026;
  the *specific* MS-AF/Foundry instantiation is new (mid-2026) and single-author.
- **User complaints / failure mode:** The split is conceptual, not a product boundary — there is
  no Microsoft "Coding Agent" SKU; you assemble it from Agent Framework + a coding assistant +
  skills. Risk surfaced elsewhere in this repo's research: build-time agents that emit runtime
  agents amplify any error or injection in the skill into *every* generated agent (see Pattern 4).

### Pattern 2 — SKILL.md as the portable unit of "taste" (open standard, Anthropic-origin)

- **What it is:** A `SKILL.md` = a folder with one Markdown file carrying **YAML frontmatter**
  (`name`, `description` required) + Markdown instructions, plus optional bundled `scripts/`,
  `references/`, `assets/`. `name`: ≤64 chars, lowercase/digits/hyphens, no XML tags, no reserved
  words (`anthropic`, `claude`). `description` states *what it does and when to use it*. The skill
  encodes a team's conventions/fixtures/patterns once; every agent built afterward inherits them.
- **Source apps:** Origin = **Anthropic** (Claude Code, Oct 2025), now an open standard at
  agentskills.io. Cross-platform support claimed for **Claude Code, OpenAI Codex CLI, Google
  Gemini CLI, GitHub Copilot (VS Code agent skills), Cursor**. Microsoft adopted the *identical*
  format — microsoft/skills uses the same `SKILL.md` + frontmatter + bundled-resources layout.
- **Adoption scale:** anthropics/skills is a high-traffic public repo; microsoft/skills ~2.1k
  stars / ~133 skills; multiple independent MS-org repos (Fabric, Copilot-for-Azure, Agent-Skills)
  ship it; third parties (CrowdStrike) reuse the name for their own Foundry. This is the strongest
  signal in the survey: **the file format has converged across competing vendors.**
- **User complaints / failure mode:** The reserved-word + naming constraints trip authors; the
  "description triggers loading" contract means a vague `description` → the agent never loads the
  skill (silent capability loss) or loads the wrong one. (This matches degradation patterns in the
  repo's existing tool-surface research.)
- **Note for this repo:** agent-enterprise is *itself* a skill-first system (`skills/*.skill.md`
  source → `resolved/SKILL.md` build output via `init.py`; "never edit `resolved/` directly").
  The external pattern is **convergent with the architecture already in this codebase** — surfaced
  as an observation for `@pm`/`@planner`, not a recommendation.

### Pattern 3 — Foundry's versioned Skills API + MCP-resource discovery (the novel/valuable bit)

- **What it is:** The piece that is genuinely new vs the open SKILL.md standard. A skill is authored
  once and stored centrally in **Foundry through a versioned Skills API**, project-scoped:
  - **Immutable versioning:** every update creates a **new immutable version**; the parent skill
    tracks a **`default_version`**. To ship a change you create a new version, test it, then
    **promote to default — without touching any agent code.** (This is the decoupling payoff:
    behavioral guidelines version independently of agent code.)
  - **Discovery via MCP Resources, not a proprietary SDK:** attach skills to a **toolbox**; any MCP
    client calls **`resources/list`** once at startup to discover attached skills, then
    **`resources/read`** to download content into the session context. **Any MCP client — GitHub
    Copilot, Claude Code, or your own harness — can consume skills without the Foundry SDK.**
    Alternatively skills can be downloaded directly into a hosted or local agent project.
- **Source apps:** learn.microsoft.com "Use skills with Microsoft Foundry agents (preview)" and
  "Use skills with the Responses API." Corroborated verbatim across multiple independent extracts.
- **Adoption scale:** **Public preview** (mid-2026). No GA, no published customer counts. Foundry
  Agent Service itself is GA and was a headline at Build 2026; Skills rode in as a preview tool.
- **User complaints / failure mode:** Preview-stage → unstable API, no SLA, likely breaking changes
  before GA. The MCP-resources path inherits MCP's known weaknesses (resource discovery is
  client-dependent; not every "MCP client" implements the Resources sub-protocol, so the
  "any client" claim is aspirational for clients that only do tools, not resources).

### Pattern 4 — "Treat skills as privileged, untrusted code" (the load-bearing security caveat)

- **What it is:** Microsoft's *own* Foundry skills documentation explicitly warns that skills are an
  attack surface: **prompt-injection-driven data exfiltration** and **unauthorized command
  execution**. Guidance: "Treat skills as privileged code and instructions… treat any skill as
  potentially untrusted input until you validate it." Skill content can influence planning, tool
  selection, and command execution. A companion authoring rule: *don't call a workflow's MCP tools
  without first reading its skill doc* (the skill carries required pre-checks/validation).
- **Source apps:** learn.microsoft.com Foundry skills (preview) security section; matches
  Anthropic's own skill-security guidance.
- **Adoption scale:** First-party warning shipped with the preview docs — i.e., Microsoft is
  flagging this *before* GA.
- **Failure mode:** This is the central failure mode of the whole "agents that build agents"
  pattern: a poisoned/compromised SKILL.md at build-time is inherited by every Runtime Agent the
  Coding Agent generates. A skill is read every turn as model-visible text → a tool-poisoning /
  hidden-instruction vector (consistent with `tool-surface-control-research.md` Finding 3 in this
  repo). Versioning helps provenance but does **not** content-address against rug-pulls unless the
  consumer pins a version.

## Adoption & timeline (corroborated, first-party)

| Fact | Detail | Source class |
| --- | --- | --- |
| MS Agent Framework = SK + AutoGen merge | Same teams; next gen of both | first-party + trade press |
| Public preview | Oct 2025 | devblogs / VS Magazine |
| Release Candidate (.NET + Python) | late 2025 | devblogs.microsoft.com/agent-framework |
| GA 1.0 | ~Apr 6 2026 | Visual Studio Magazine |
| SK + AutoGen status | **maintenance mode** — bug/security fixes only, no new features | first-party |
| Foundry Skills | **public preview** (mid-2026) | learn.microsoft.com |
| microsoft/skills repo | ~2.1k★ / ~242 forks / ~133 skills | github (snapshot, re-pull) |
| SKILL.md origin | Anthropic, open standard at agentskills.io | platform.claude.com |

## Documented failure modes / complaints (the framework substrate)

- **Convergence-story whiplash:** Microsoft first told developers SK and AutoGen *would merge*,
  then shipped a **third, new framework that replaces both** — a widely-voiced developer
  frustration (`microsoft/semantic-kernel` Discussion #13209; trade press).
- **AutoGen migration is heavy:** AutoGen's conversation-centric multi-agent model has **no direct
  equivalent** — it moves to a **graph-based** orchestration model, so production AutoGen users
  rebuild collaboration logic as explicit graph transitions. An `autogen_compat` shim emulates
  GroupChat on the graph engine but is a compat layer, not parity.
- **Semantic Kernel migration is gentler** (most plugins/connectors port directly) **but** the
  experimental `AgentGroupChat` agent features were replaced by graph orchestration.
- **Skills security (above)** is the pattern-specific failure mode and is acknowledged first-party.

## Unmet needs observed

- **No first-party "Coding Agent" product** — the build-time layer is a do-it-yourself assembly;
  the blueprint names a role Microsoft doesn't ship as a unit.
- **Skill integrity / supply-chain** — versioning exists, but no surfaced content-addressing,
  signing, or rug-pull protection for skills consumed over MCP resources.
- **"Any MCP client" is overstated** — depends on the client implementing MCP *Resources*
  (`resources/list`/`read`), which tool-only clients don't.
- **Preview-stage Skills API** — no GA SLA, breaking-change risk for anyone building on it now.

## Sources

- Rendon, D. "Agents That Build Agents: A SKILL-first Blueprint with MS Agent Framework & Foundry."
  Microsoft Community Hub / Azure Dev Community blog —
  https://techcommunity.microsoft.com/blog/azuredevcommunityblog/agents-that-build-agents-a-skill-first-blueprint-with-ms-agent-framework--foundr/4523631
  (body returned HTTP 403; reconstructed from search extracts)
- Rendon, D. (mirror). ITNEXT —
  https://itnext.io/a-build-time-and-run-time-architecture-for-ai-agents-skill-first-construction-on-microsoft-agent-d143bc375f44
- "Use skills with Microsoft Foundry agents (preview)" — https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/skills
- "Use skills with the Responses API" — https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/skills
- "What is Microsoft Foundry Agent Service?" — https://learn.microsoft.com/en-us/azure/foundry/agents/overview
- "Build and run agents at scale with Microsoft Foundry at Build 2026" — https://devblogs.microsoft.com/foundry/agent-service-build2026/
- Microsoft Agent Framework overview / docs — https://learn.microsoft.com/en-us/agent-framework/overview/
- "Migrate your Semantic Kernel and AutoGen projects to Microsoft Agent Framework RC" — https://devblogs.microsoft.com/agent-framework/migrate-your-semantic-kernel-and-autogen-projects-to-microsoft-agent-framework-release-candidate/
- "Microsoft Ships Production-Ready Agent Framework 1.0 for .NET and Python" — Visual Studio Magazine, 2026-04-06 — https://visualstudiomagazine.com/articles/2026/04/06/microsoft-ships-production-ready-agent-framework-1-0-for-net-and-python.aspx
- "Microsoft Agent Framework. So what's next?" — github.com/microsoft/semantic-kernel Discussion #13209 — https://github.com/microsoft/semantic-kernel/discussions/13209
- github.com/microsoft/agent-framework — https://github.com/microsoft/agent-framework
- github.com/microsoft/skills — https://github.com/microsoft/skills
- Agent Skills (Microsoft Open Source) — https://microsoft.github.io/skills/
- Anthropic Agent Skills overview — https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- github.com/anthropics/skills — https://github.com/anthropics/skills
- "SKILL.md: The Open Standard for AI Agent Skills" (agensi.io) — https://www.agensi.io/learn/agent-skills-open-standard

> **Honesty-guard:** The seed source body was unreachable (403) and is single-author MVP content;
> classified **untrusted**. First-party Microsoft claims (versioning, `default_version`,
> `resources/list`/`resources/read`, preview status, GA dates, security warnings) are
> corroborated across ≥2 independent extracts of official pages. GitHub star/fork/skill counts are
> June-2026 snapshots — re-pull before quoting. No recommendation or 5-test applied; that is `@pm`'s call.
