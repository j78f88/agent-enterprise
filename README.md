<div align="center">

<h1>🏠 agent-enterprise</h1>

<h3>The operating system your AI coding assistant is missing</h3>

<p><strong>13 agents · 3 delivery modes · 7 enforced schemas · 4 platforms</strong></p>

<p><em>Set up by chatting — open the repo in your agent, say one sentence, and it configures everything for you.</em></p>

[![CI](https://github.com/j78f88/agent-enterprise/actions/workflows/ci.yml/badge.svg)](https://github.com/j78f88/agent-enterprise/actions/workflows/ci.yml)
[![GitHub stars](https://img.shields.io/github/stars/j78f88/agent-enterprise?style=social)](https://github.com/j78f88/agent-enterprise/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Copilot](https://img.shields.io/badge/GitHub%20Copilot-Ready-blue?logo=github)](https://github.com/features/copilot)
[![Claude](https://img.shields.io/badge/Claude%20Code-Ready-orange)](https://claude.ai)
[![Cursor](https://img.shields.io/badge/Cursor-Ready-purple)](https://cursor.sh)

<br />

**[Quick Start](#-quick-start)** · **[What You Get](#-what-you-get)** · **[Three Modes](#-three-delivery-modes)** · **[Why It Works](#-why-it-works)** · **[Full Docs](docs/ONBOARDING.md)**

<br />

---

*Copilot, Claude, and Cursor are powerful. But without structure, they're chaos machines.*
*agent-enterprise turns your AI assistant into a professional delivery team.*

---

</div>

## 🔥 The Problem Everyone Ignores

You're using GitHub Copilot or Claude Code. They're fast. They're capable.

**They also:**
- Forget your project conventions after every session
- Ship code without tests, reviews, or documentation
- Require you to manually coordinate planning → coding → QA
- Lose all learned patterns when context resets
- Make inconsistent decisions across identical problems

You have a **powerful tool** with **no process**. That's not engineering — that's gambling.

---

## 💡 The Solution: A Professional Delivery Team in Your Config

**agent-enterprise** is a portable, multi-agent operating system for software projects.

Skills, instructions, and agents are authored once in plain Markdown, resolved with your project-specific tokens, and emitted as copy-ready artifacts for **any** compatible coding agent — GitHub Copilot, Claude Code, Cursor, or OpenAI Codex.

One config file transforms chaotic AI assistance into a structured software pipeline:

```
Your feature request
        ↓
   @planner      → Scopes requirements, estimates complexity
        ↓
   @pm           → Validates against project goals (prevents scope creep)
        ↓
   @sprint-lead  → Orchestrates full implementation cycle
        ↓
   @qa           → Enforces tests, coverage, linting (blocks failures)
        ↓
   @reviewer     → Catches security issues, anti-patterns, code smells
        ↓
   @docs         → Updates documentation automatically
        ↓
   Deployed code — tested, reviewed, documented
```

---

## 📈 Before & After

<table>
<tr>
<th width="50%">❌ Without agent-enterprise</th>
<th width="50%">✅ With agent-enterprise</th>
</tr>
<tr>
<td>

```
You: "Add user authentication"

Agent: [writes 200 lines immediately]
       • No tests
       • Hardcodes API keys
       • Uses deprecated patterns
       • Forgets your Auth0 setup

You: "Wait, we use Auth0..."

Agent: [rewrites everything]
       • Still no tests
       • Documentation? What docs?
```

</td>
<td>

```
You: "@planner add user auth"

@planner: Scoped 4 tasks (~8 files)
          Using Auth0 per config
          Complexity: Medium

You: "@sprint-lead run Sprint 12"

@sprint-lead:
  ✔ Implementation complete
  ✔ Tests passing (91% coverage)
  ✔ 14 security checks passed, 0 CVEs
  ✔ Docs updated
  ✔ Pushed to feature branch
```

</td>
</tr>
</table>

---

## 🎯 What You Get

### 13 Specialized Agent Roles

| Agent | What It Does |
|:------|:-------------|
| 🎯 **@pm** | Validates features through 5 structured tests — prevents scope creep before code is written |
| 📋 **@planner** | Scopes requirements, drafts sprint plans, estimates complexity |
| 🎬 **@sprint-lead** | Orchestrates complete sprint execution with zero manual coordination |
| ✅ **@qa** | Runs typecheck, lint, tests, coverage — blocks deploys on failures |
| 🔍 **@reviewer** | Reviews for patterns, security, performance — flags issues by severity |
| 🏗️ **@architect** | Designs approaches, writes ADRs, makes structural decisions |
| 📚 **@researcher** | Surfaces prior art with citations, identifies failure modes |
| 🐛 **@bug** | Captures bugs into structured, prioritized backlog |
| 📖 **@docs** | Keeps documentation in sync after every sprint |
| 🔐 **@security** | 14 automated security checks — see [details below](#-security-built-in-not-bolted-on) |
| ♿ **@a11y** | WCAG 2.1 AA accessibility audits |
| ⚡ **@perf** | Bundle size, build time, dependency analysis |
| 🚀 **@onboarding** | Sets up agent-enterprise from one chat prompt — interviews you, builds, deploys, verifies, then self-removes. Also ramps up new team members. |

### 🔐 Security: Built In, Not Bolted On

`@security` runs **14 automated checks** as a sprint gate or on demand:

| Check | What It Catches |
|:------|:----------------|
| Dependency CVE scan | Known vulnerabilities in your packages |
| Active exploit research | CISA KEV catalog, proof-of-concept detection |
| Secret detection | API keys, tokens, passwords in source |
| OWASP pattern matching | Injection, XSS, auth failures |
| File integrity hashes | Unauthorized changes to tracked files |
| SBOM generation | Full software bill of materials |
| SAST scanning | Static analysis security findings |
| Git history secret scan | Secrets in old commits |
| License compliance | Denylist/allowlist enforcement |
| HTTP security headers | Missing CSP, HSTS, X-Frame-Options |
| Container image scan | Vulnerabilities in Docker images |
| IaC scanning | Misconfigurations in infrastructure code |
| Supply chain audit | Dependency provenance verification |
| Security changelog | Append-only finding log (SEC-NNN entries) |

Every finding gets an **OWASP remediation classification**: patched, delayed, no-fix, or zero-day — with timelines and effort tags.

### 7 Enforced Schemas

Every artifact is validated at build time — no more silent drift:

| Schema | Validates |
|:-------|:----------|
| `frontmatter-v1` | YAML frontmatter on every skill, instruction, and agent |
| `callable-v1` | Callable manifest on every skill |
| `project-v1` | A single project entry in a Mode 3 registry |
| `registry-v1` | A full Mode 3 choreography registry |
| `subagent-return-tier1` | Lightweight subagent return contracts |
| `subagent-return-tier2` | Standard subagent return contracts |
| `subagent-return-tier3` | Full subagent return contracts |

### 3 Ready-to-Use Profiles

| Profile | For |
|:--------|:----|
| **[react-web-app](profiles/react-web-app.config.yml)** | React + Vite single-page apps |
| **[monorepo-fullstack](profiles/monorepo-fullstack.config.yml)** | TypeScript monorepo (pnpm + Vite + Expo) |
| **[python-api](profiles/python-api.config.yml)** | FastAPI / Flask / Django backends |

---

## 🔀 Three Delivery Modes

agent-enterprise ships as three **standalone, independently consumable** modes on top of a shared protocol layer. Use one, two, or all three:

| Mode | What It Is | When You Need It |
|:-----|:-----------|:-----------------|
| **Mode 1 — Team** | A substrate of skills, instructions, and agents for interactive use | You want `@planner`, `@qa`, `@security`, etc. in your project |
| **Mode 2 — Orchestration** | A dispatcher that pulls work from a queue, invokes callables, and verifies results | You want non-interactive, issue-driven dispatch |
| **Mode 3 — Choreography** | Coordinates a program of works across many projects with drift control | You manage multiple projects and need cross-repo visibility |

Each mode is a standalone install. Adoption order is free. Adding a new mode doesn't modify existing ones.

> **Visual reference:** open [docs/command-centre-visual.html](docs/command-centre-visual.html) in a browser for an interactive cheat sheet covering all three modes.

---

## 🚀 Quick Start

### Get set up in one sentence

Clone the repo, open it in **GitHub Copilot Chat** or **Claude Code**, and paste this:

```text
Set up agent-enterprise for my project. Ask me what you need, recommend a
profile, run init.py, deploy the resolved files, and verify it works.
```

The `@onboarding` agent takes it from there — it interviews you (about five
questions), recommends a profile, fills the config, runs the build, deploys
the files, and checks everything works. **No YAML editing. No copy commands.**
When setup is verified, it removes itself.

First time in the repo? Clone it, open the folder in your agent, and paste the sentence above.

```powershell
git clone https://github.com/j78f88/agent-enterprise.git
```

**Rather drive it yourself?** Two terminal paths produce the same build.

*Guided CLI* — interactive prompts, no agent:

```powershell
cd agent-enterprise
pip install -r requirements.txt
python init.py --quick-setup          # prompts for name, repo, branch, namespace
```

*Full manual* — edit the config yourself, most control:

```powershell
cd agent-enterprise
pip install -r requirements.txt

# Choose a profile and generate + deploy resolved files
python init.py --config profiles/python-api.config.yml --deploy
# → resolved/skills, resolved/instructions, resolved/agents
# → copies automatically into .github/ and seeds .claude/commands/

# Initialize planning files (first time only)
cp starters/SPRINTS.md ../
cp starters/BACKLOG_LEDGER.md ../docs/planning/
```

**Then use naturally:**
```
@planner scope the dark mode feature
@sprint-lead run Sprint 3
@qa check coverage for auth module
@reviewer look at the last 3 commits
```

📖 **[Complete setup guide →](docs/ONBOARDING.md)** · **[Quickstart →](docs/QUICKSTART.md)**

---

## 🧠 Why It Works

### Thin Orchestration Architecture

```
@sprint-lead (coordinator)
    │
    ├── Reads plans
    ├── Tracks state
    ├── Manages workflow
    │
    └── Delegates ALL implementation to:
            ├── Unnamed subagents → write code
            ├── @qa → validate quality
            ├── @reviewer → check patterns
            └── @docs → update documentation
```

**The secret:** `@sprint-lead` never reads source code. It coordinates. This keeps context windows clear for what actually matters.

### Contract-First Design

Every agent returns **structured data** following JSON schemas:

```json
{
  "tier": 1,
  "agent": "qa",
  "status": "blocked",
  "summary": "2/5 quality gates failed",
  "blockerReason": "Coverage at 72% (threshold: 85%)",
  "findings": [...]
}
```

When `@qa` returns `status: blocked`, `@sprint-lead` knows exactly what to do. No guessing. No hallucinating.

### Protocol-v1: Frozen Contracts

`protocol-v1` is frozen at `2.0.0`. Every skill, instruction, and agent gets validated against JSON Schemas at build time. Frontmatter validation is strict by default. No more drift — if it builds, it conforms.

### Works Everywhere

author once → resolve with tokens → deploy to any platform:

| Platform | Status |
|:---------|:-------|
| **GitHub Copilot** | ✅ Ready |
| **Claude Code** | ✅ Ready |
| **Cursor** | ✅ Ready |
| **OpenAI Codex** | ✅ Ready |

---

## 🗂️ Architecture (1 minute)

```
skills/           author once, token-templated, callable-v1 manifests
instructions/     shared rules, generic + configurable
agents/           per-agent body that wraps a skill
schemas/          7 JSON Schemas that gate the build
config/           project-specific token values
profiles/         pre-built configs (python-api, react-web-app, monorepo-fullstack)
command-centre/   contracts (protocol-v1, mode contracts, ADRs, ref impls)
        │
        ▼  python init.py --config <profile>
resolved/         deploy artifacts (skills/, instructions/, agents/)
```

`init.py` is the single source of truth for the build. It runs security validation, frontmatter validation (strict by default), resolves `{{tokens}}`, and writes deterministic output.

`resolved/` is build output — never edit it directly, never commit it.

---

## 🤔 Is This For You?

<table>
<tr>
<th>✅ Perfect fit</th>
<th>❌ Not for you</th>
</tr>
<tr>
<td>

- You use Copilot/Claude/Cursor for real development
- You're tired of re-explaining context every session
- You want consistent quality without babysitting
- You value process but don't want to build from scratch
- You manage multiple projects and need cross-repo consistency

</td>
<td>

- You only use AI for quick code snippets
- You prefer building your own agent framework from scratch
- You don't use any AI coding assistants

</td>
</tr>
</table>

---

## 📚 Documentation

| Guide | What You'll Learn |
|:------|:------------------|
| **[Onboarding](docs/ONBOARDING.md)** | Setup (start here) — chat-driven, guided CLI, or full manual |
| **[Quickstart](docs/QUICKSTART.md)** | Fastest path to running |
| **[Architecture](docs/ARCHITECTURE.md)** | Design decisions & rationale |
| **[Personas](docs/PERSONAS.md)** | Who this is for (evidence-tagged) |
| **[Skill Flow](docs/SKILL_FLOW.md)** | How agents orchestrate work |
| **[Example Sprint](docs/EXAMPLE_SPRINT_FLOW.md)** | Complete sprint walkthrough |
| **[Three Modes](command-centre/00-overview/three-modes.md)** | Team, Orchestration, Choreography explained |
| **[Customization](docs/CUSTOMIZATION.md)** | Adapting skills for your needs |
| **[Extension Guide](docs/EXTENSION_GUIDE.md)** | Authoring new skills |
| **[Troubleshooting](docs/TROUBLESHOOTING.md)** | Common issues & fixes |

---

## 🤝 Contributing

Contributions welcome. See **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** and **[AGENTS.md](AGENTS.md)**.

- Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:` …).
- Every PR must keep `python init.py` green and the test suite passing.
- New skills must include a `callable-v1` manifest and follow [EXTENSION_GUIDE.md](docs/EXTENSION_GUIDE.md).

---

## 📄 License

MIT © 2026

---

<div align="center">

<br />

### Your AI assistant has the power.

### Give it the process.

<br />

**[⭐ Star on GitHub](https://github.com/j78f88/agent-enterprise)** · **[📖 Get Started](docs/ONBOARDING.md)** · **[🐛 Report Issue](https://github.com/j78f88/agent-enterprise/issues)**

<br />

---

<sub>Extracted from real production teams. Battle-tested on TypeScript, Python, React, and monorepo projects.<br/>
protocol-v1 frozen at 2.0.0 — contracts enforced by 7 JSON Schemas.</sub>

</div>
