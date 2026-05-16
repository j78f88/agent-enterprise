<div align="center">

<h1>🏠 agent-homebase</h1>

<h3>The operating system your AI coding assistant is missing</h3>

<p><strong>12 agents · 14 security checks · dual-platform · 5 minutes to production-grade AI</strong></p>

[![CI](https://github.com/j78f88/agent-homebase/actions/workflows/ci.yml/badge.svg)](https://github.com/j78f88/agent-homebase/actions/workflows/ci.yml)
[![GitHub stars](https://img.shields.io/github/stars/j78f88/agent-homebase?style=social)](https://github.com/j78f88/agent-homebase/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Copilot](https://img.shields.io/badge/GitHub%20Copilot-Ready-blue?logo=github)](https://github.com/features/copilot)
[![Claude](https://img.shields.io/badge/Claude%20Code-Ready-orange)](https://claude.ai)

<br />

**[Quick Start](#-quick-start)** · **[What You Get](#-what-you-get)** · **[Why This Works](#-why-it-works)** · **[Full Docs](docs/ONBOARDING.md)**

<br />

---

*Copilot and Claude are powerful. But without structure, they're chaos machines.*  
*agent-homebase turns your AI assistant into a professional delivery team.*

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

You have a **powerful tool** with **no process**. That's not engineering—that's gambling.

---

## 💡 The Solution: A Professional Delivery Team in Your Config

**agent-homebase** is a battle-tested skills library extracted from real production teams.

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

## 🎯 What You Get

### 12 Specialized Agent Roles

| Agent | What It Does |
|:------|:-------------|
| 🎯 **@pm** | Validates features through 5 structured tests—prevents scope creep before code is written |
| 📋 **@planner** | Scopes requirements, drafts sprint plans, estimates complexity |
| 🎬 **@sprint-lead** | Orchestrates complete sprint execution with zero manual coordination |
| ✅ **@qa** | Runs typecheck, lint, tests, coverage—blocks deploys on failures |
| 🔍 **@reviewer** | Reviews for patterns, security, performance—flags issues by severity |
| 🏗️ **@architect** | Designs approaches, writes ADRs, makes structural decisions |
| 📚 **@researcher** | Surfaces prior art with citations, identifies failure modes |
| 🐛 **@bug** | Captures bugs into structured, prioritized backlog |
| 📖 **@docs** | Keeps documentation in sync after every sprint |
| 🔐 **@security** | 14 automated security checks — see [details below](#-security-built-in-not-bolted-on) |
| ♿ **@a11y** | WCAG 2.1 AA accessibility audits |
| ⚡ **@perf** | Bundle size, build time, dependency analysis |

> A 13th agent, `@onboarding`, ships with the library but is **setup-only** — it guides first-time configuration and removes itself after the initial run, so it doesn't appear in your day-to-day agent roster.

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

### 24 Governance Rules

- Commit message conventions  
- Severity classification (CRITICAL / WARNING / SUGGESTION)  
- Escalation paths for blocked work  
- Quality gate thresholds  
- Sprint retrospective format  
- Handoff contracts between agents  
- Security policies & validation  
- *...and 16 more*

### 3 Ready-to-Use Profiles

| Profile | For |
|:--------|:----|
| **[react-web-app](profiles/react-web-app.config.yml)** | React + Vite single-page apps |
| **[monorepo-fullstack](profiles/monorepo-fullstack.config.yml)** | TypeScript monorepo (pnpm + Vite + Expo) |
| **[python-api](profiles/python-api.config.yml)** | FastAPI / Flask / Django backends |

---

## 📊 Before & After

<table>
<tr>
<th width="50%">❌ Without agent-homebase</th>
<th width="50%">✅ With agent-homebase</th>
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
  ✓ Implementation complete
  ✓ Tests passing (91% coverage)
  ✓ 14 security checks passed, 0 CVEs
  ✓ Docs updated
  ✓ Pushed to feature branch
```

</td>
</tr>
</table>

---

## 🚀 Quick Start

**Setup in 5 minutes:**

```bash
# 1. Add to your project
git submodule add https://github.com/j78f88/agent-homebase.git skills-library
cd skills-library

# 2. Choose your profile
cp profiles/react-web-app.config.yml project.config.yml
# Edit project.config.yml — at minimum set project.name and git.repo
# Or use: python init.py --quick-setup  (interactive)

# 3. Generate resolved files
python init.py --config project.config.yml

# 4. Copy to your project
cp -r resolved/skills/* ../.github/agents/
cp -r resolved/instructions/* ../.github/instructions/
# If using VS Code agents (editor.target: "vscode" or "both"):
cp -r resolved/agents/* ../.github/agents/

# 5. Initialize planning files (first time only)
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

📖 **[Complete setup guide →](docs/ONBOARDING.md)**

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

### Progressive Reliability (Optional)

| Phase | Adds | When to Enable |
|:------|:-----|:---------------|
| **0-1** | Security validation, JSON Schema contracts | Always (default) |
| **2** | SQLite checkpoints, resume from any point | Long sprints, unstable networks |
| **3** | Docker sandboxing, resource limits | CI/CD, untrusted code |
| **4** | Deterministic replay, Lamport timestamps | Compliance, debugging |

Most projects only need Phase 0-1. Add phases as reliability requirements grow.

### Tested & CI-Verified

The library ships with a test suite covering contract validation, init.py generation, checkpoint durability, sandbox capabilities, and determinism guarantees — verified on every push across Python 3.10 and 3.12.

📖 **[Architecture deep-dive →](docs/ARCHITECTURE.md)**

---

## 🤔 Is This For You?

<table>
<tr>
<th>✅ Perfect fit</th>
<th>❌ Not for you</th>
</tr>
<tr>
<td>

- You use Copilot/Claude for real development
- You're tired of re-explaining context every session
- You want consistent quality without babysitting
- You value process but don't want to build from scratch

</td>
<td>

- You only use AI for quick code snippets
- You prefer completely unstructured exploration
- Your project changes too fast for conventions

</td>
</tr>
</table>

---

## 🌍 Compatibility

| Platform | Status | What You Get |
|:---------|:-------|:-------------|
| GitHub Copilot (VS Code agent mode) | ✅ Full support | Agent wrappers with tool restrictions + skills |
| Claude Code / Cowork | ✅ Full support | Skills with progressive context loading |
| Any `.instructions.md` system | ✅ Compatible | Instructions work everywhere |

### Platform Selection

Set `editor.target` in your config to control what gets generated:

| Value | Generates | Best For |
|:------|:----------|:---------|
| `"both"` (default) | Skills + agents + instructions | Teams on mixed platforms |
| `"vscode"` | Agents + instructions (skills set to non-invocable) | VS Code-only teams |
| `"claude-code"` | Skills + instructions (no agents) | Claude Code-only teams |

When `editor.target` includes VS Code, `init.py` generates thin `.agent.md` wrappers in `resolved/agents/` with native tool restrictions, subagent delegation, and model selection. Skills remain the single source of truth.

---

## 📁 Project Structure

```
agent-homebase/
├── skills/           # 12 agent definitions (canonical source of truth)
├── instructions/     # 24 governance rules
│   ├── configurable/ # Project-specific (paths, thresholds)
│   └── generic/      # Universal (contracts, severity)
├── profiles/         # Ready-to-use configs
├── starters/         # 9 starter templates (sprints, backlog, security changelog, file hashes)
├── schemas/          # JSON return validation
├── resolved/         # Generated output
│   ├── skills/       # Token-resolved skills (both platforms)
│   ├── agents/       # VS Code agent wrappers (when editor.target includes vscode)
│   └── instructions/ # Token-resolved instructions
├── docs/             # Complete documentation
└── src/              # Phase implementations (Python)
```

---

## 📚 Documentation

| Guide | What You'll Learn |
|:------|:------------------|
| **[Onboarding](docs/ONBOARDING.md)** | Step-by-step setup (start here) |
| **[Architecture](docs/ARCHITECTURE.md)** | Design decisions & rationale |
| **[Skill Flow](docs/SKILL_FLOW.md)** | How agents orchestrate work |
| **[Example Sprint](docs/EXAMPLE_SPRINT_FLOW.md)** | Complete sprint walkthrough |
| **[Customization](docs/CUSTOMIZATION.md)** | Adapting skills for your needs |
| **[Troubleshooting](docs/TROUBLESHOOTING.md)** | Common issues & fixes |

---

## 🤝 Contributing

Contributions welcome. See **[CONTRIBUTING.md](docs/CONTRIBUTING.md)**.

---

## 📄 License

MIT © 2026

---

<div align="center">

<br />

### Your AI assistant has the power.

### Give it the process.

<br />

**[⭐ Star on GitHub](https://github.com/j78f88/agent-homebase)** · **[📖 Get Started](docs/ONBOARDING.md)** · **[🐛 Report Issue](https://github.com/j78f88/agent-homebase/issues)**

<br />

---

<sub>Extracted from real production teams. Battle-tested on TypeScript, Python, React, and monorepo projects.</sub>

</div>
