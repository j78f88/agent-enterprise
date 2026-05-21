# Onboarding Guide

Setup for a new project consuming agent-homebase. Pick the lane that fits how
hands-on you want to be — all three produce the same result.

> **Visual overview:** open [command-centre-visual.html](command-centre-visual.html) in a browser to see all agents, modes, and flows at a glance before diving in.

---

## Pick your lane

| Lane | First action | Best for |
|:-----|:-------------|:---------|
| **A — Chat** ⭐ | Open the repo in your agent and ask it to set you up | First-timers, "just do it for me" |
| **B — Guided CLI** | `python init.py --quick-setup` | Comfortable in a terminal, want prompts not YAML |
| **C — Manual** | Edit `project.config.yml`, then run `init.py` | Maximum control, reproducible/CI setups |

---

## Lane A — Chat-driven setup (recommended)

Clone the repo, open the folder in **GitHub Copilot Chat** or **Claude Code**,
and paste:

```text
Set up agent-homebase for my project. Ask me what you need, recommend a
profile, run init.py, deploy the resolved files, and verify it works.
```

The `@onboarding` agent drives the whole flow for you:

1. **Interviews you** — name, language/framework, repo, branch, team size, platform target (~5 questions).
2. **Recommends a profile** with rationale, and lets you override.
3. **Fills the config and runs the build** (`init.py`) — no YAML editing.
4. **Deploys the resolved files** into your project's directories.
5. **Seeds only the planning files you're missing** — never overwrites yours.
6. **Verifies** everything (files in place, no unresolved tokens) and reports a checklist.
7. **Self-removes** once setup is confirmed.

If anything is unclear it asks rather than guessing. When it finishes, jump
straight to a real task: `@planner scope my first feature`.

Want to drive it yourself instead? Lanes B and C are the manual paths below.

---

## Lanes B & C — Manual setup

The steps below are what Lane A does for you. Follow them directly if you
prefer the terminal (Lane B uses `--quick-setup` at Step 3; Lane C edits the
config by hand).

## Prerequisites

- Python 3.12+ with PyYAML (`pip install pyyaml`)
- A `.github/agents/` directory in your project (create it if absent)
- A `.github/instructions/` directory in your project (create it if absent)

---

## Step 1 — Choose your skills

Each skill is a specialized agent role (e.g., `@planner` drafts sprint plans, `@qa` runs tests, `@reviewer` checks code). You don't need all of them—pick the ones your team uses. Below, "minimum viable" = solo/small teams; optional = add as you grow.

**Minimum viable set (solo / small team):**
`planner`, `sprint-lead`, `qa`, `reviewer`, `bug`

**Add if doing research-driven features:**
`pm`, `researcher`

**Add if touching architecture regularly:**
`architect`

**Add if shipping UI:**
`a11y`

**Add if tracking bundle size / dependencies:**
`perf`

**Add for automated documentation:**
`docs`

**Add for vulnerability scanning and security audits:**
`security`

You can install all thirteen and let the skill descriptions handle routing — skills only load when relevant. The cost of unused skills is negligible.

---

## Step 2 — Install the library

### Option A — Git submodule (recommended)

Links the library as a separate repo. You get updates via `git submodule update --remote`. Keeps your repo clean and upgradeable.

```bash
git submodule add https://github.com/j78f88/agent-homebase.git skills-library
```

### Option B — One-time copy

Copies files once. No auto-updates, but simpler setup if you don't plan to upgrade.

```bash
git clone https://github.com/j78f88/agent-homebase.git skills-library
rm -rf skills-library/.git   # detach from library history
```

---

## Step 3 — Choose a profile and fill in config

Copy the closest profile to `project.config.yml`:

```bash
cd skills-library
cp profiles/react-web-app.config.yml project.config.yml
# or: cp profiles/python-api.config.yml project.config.yml
# or: cp profiles/monorepo-fullstack.config.yml project.config.yml
```

### Option A — Interactive setup (recommended for first-time)

```bash
python init.py --quick-setup
```

This prompts for the essential values (project name, repo, namespace, branch) and updates your config.

### Option B — Manual edit

Open `project.config.yml` and fill in every `FIXME` value. **If you skip this step, agents won't run correctly** - the system will show which values are missing (marked with ⚠) when you run `init.py`.

**Platform selection:** Set `editor.target` to control what gets generated:

| Value | Generates | Best For |
|:------|:----------|:---------|
| `"both"` (default) | Skills + agent wrappers + instructions | Teams on mixed platforms |
| `"vscode"` | Agent wrappers + instructions (skills set to non-invocable) | VS Code-only teams |
| `"claude-code"` | Skills + instructions (no agent wrappers) | Claude Code-only teams |

The key fields to get right:

- `project.name` — your project name (e.g., "My App") — used in all agent identity prompts
- `team.cto_name` — your name (e.g., "Alex") — used in approval markers and skill personalization
- `git.repo` — your GitHub repository (e.g., "owner/repo") — used for CI status checks
- `paths.*` — where your planning docs live
- `commands.*` — your actual test/build/lint commands
- `quality.coverage_store_threshold` and `quality.coverage_web_threshold` — your coverage targets
- `platform.ci_workflow_display_name` — the exact name shown in GitHub Actions UI
- `git.main_branch` — `main` or `master`

---

## Step 4 — Run substitution

```bash
cd skills-library
python init.py --config project.config.yml
```

Watch for `⚠` warnings — each one is a token with no config value. Fix them in `project.config.yml` and re-run until the output shows `✓ All tokens resolved`.

---

## Step 5 — Copy resolved files

```bash
cp -r resolved/skills/*        ../.github/agents/
cp -r resolved/instructions/*  ../.github/instructions/

# If using VS Code agents (editor.target: "vscode" or "both"):
cp -r resolved/agents/*        ../.github/agents/
```

> **Note:** When `editor.target` includes `"vscode"`, `init.py` generates thin `.agent.md` wrappers in `resolved/agents/` with native tool restrictions and subagent delegation. These go alongside skills in `.github/agents/`.

---

## Step 6 — Seed planning files (first time only)

If your project doesn't already have planning infrastructure:

```bash
mkdir -p ../docs/planning ../docs/architecture ../docs/development ../docs/user
mkdir -p ../docs/security ../docs/security/reports
mkdir -p ../.claude/memory

cp starters/BACKLOG_LEDGER.md    ../docs/planning/
cp starters/BUG_BACKLOG.md       ../docs/planning/
cp starters/HANDOFF_REJECTIONS.md ../docs/planning/
cp starters/SPRINTS.md           ../
cp starters/NON_GOALS.md         ../docs/
cp starters/SECURITY_CHANGELOG.md ../docs/security/
cp starters/FILE_HASHES.md       ../docs/security/
cp starters/memory-architecture.md ../.claude/memory/architecture.md
cp starters/memory-conventions.md  ../.claude/memory/conventions.md
```

---

## Step 7 — Write your conventions and architecture files

The agents `@reviewer` and `@architect` read `.claude/memory/architecture.md` and `.claude/memory/conventions.md` to understand project-specific patterns. The starters ship with instructional comments — fill them in with your actual stack, patterns, and decisions.

The more specific these files are, the more useful the agents become. A blank conventions file produces generic advice; a detailed one produces project-aware advice.

---

## Step 8 — Write a copilot-instructions.md

Create `.github/copilot-instructions.md` with project-level context: what the project is, its key directories, and any agent routing notes. This is the file Copilot loads before every session. Copy `starters/copilot-instructions.md` to `.github/copilot-instructions.md` and fill in your project-specific details.

---

## Step 9 — Verify your setup

Run these checks to confirm everything is working:

### 9.1 Check resolved files exist

```bash
# Skills should be in place
ls ../.github/agents/
# Expected: architect/ bug/ docs/ a11y/ onboarding/ perf/ planner/ pm/ qa/ reviewer/ researcher/ security/ sprint-lead/

# Agent wrappers (if editor.target includes "vscode")
ls ../.github/agents/*.agent.md
# Expected: 13 .agent.md files (one per skill)

# Instructions should be in place
ls ../.github/instructions/
# Expected: Multiple .instructions.md files
```

### 9.2 Verify no unresolved tokens

```bash
# Search for leftover {{tokens}} — should return nothing
grep -r "{{" ../.github/agents/ ../.github/instructions/ || echo "✓ No unresolved tokens"
```

### 9.3 Test the library (optional but recommended)

```bash
cd skills-library
pytest tests/ -v
# Expected: All tests pass (69+ tests)
```

### 9.4 Quick smoke test

In VS Code with Copilot Chat:
1. Open your project (not the skills-library)
2. Type `@planner` and hit Enter
3. If the agent responds, your setup is working

**Troubleshooting:** If the agent isn't found:
- Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"
- Check files are in the correct location (`.github/agents/`, not `.github/skills/`)
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

---

## Upgrading

When the library is updated:

```bash
cd skills-library
git pull                                  # if submodule: git submodule update --remote skills-library
python init.py --config project.config.yml
cp -r resolved/skills/*        ../.github/agents/
cp -r resolved/instructions/*  ../.github/instructions/
```

Your `project.config.yml` is not overwritten — config is yours to keep.

---

## Adding a project-specific orchestration layer

If you want a custom orchestrator agent that sequences these skills in your own workflow, write it in `.github/agents/` alongside the resolved skills. It stays in your project and is not part of the library. The library ships the role agents; you build the coordination layer on top.
