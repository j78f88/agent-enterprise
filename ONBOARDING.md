# Onboarding Guide

Step-by-step setup for a new project consuming agent-homebase.

---

## Prerequisites

- Python 3.8+ with PyYAML (`pip install pyyaml`)
- A `.github/agents/` directory in your project (create it if absent)
- A `.github/instructions/` directory in your project (create it if absent)

---

## Step 1 — Choose your skills

Not every project needs all eleven skills. Pick the ones that match your workflow:

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

You can install all eleven and let the skill descriptions handle routing — skills only load when relevant. The cost of unused skills is negligible.

---

## Step 2 — Install the library

**Option A — Git submodule (recommended, gives you upgrade path):**

```bash
git submodule add https://github.com/j78f88/agent-homebase.git skills-library
```

**Option B — One-time copy:**

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

Open `project.config.yml` and fill in every `FIXME` value. The key fields to get right:

- `paths.*` — where your planning docs live
- `commands.*` — your actual test/build/lint commands
- `quality.coverage_store_threshold` and `quality.coverage_web_threshold` — your coverage targets
- `platform.ci_workflow_display_name` — the exact name shown in GitHub Actions UI
- `git.main_branch` — `main` or `master`
- `team.cto_name` — your name (used in approval markers)

---

## Step 4 — Run substitution

```bash
cd skills-library
python3 init.py --config project.config.yml
```

Watch for `⚠` warnings — each one is a token with no config value. Fix them in `project.config.yml` and re-run until the output shows `✓ All tokens resolved`.

---

## Step 5 — Copy resolved files

```bash
cp -r resolved/skills/*        ../.github/agents/
cp -r resolved/instructions/*  ../.github/instructions/
```

---

## Step 6 — Seed planning files (first time only)

If your project doesn't already have planning infrastructure:

```bash
mkdir -p ../docs/planning ../docs/architecture ../docs/development ../docs/user
mkdir -p ../.claude/memory

cp starters/BACKLOG_LEDGER.md    ../docs/planning/
cp starters/BUG_BACKLOG.md       ../docs/planning/
cp starters/HANDOFF_REJECTIONS.md ../docs/planning/
cp starters/SPRINTS.md           ../
cp starters/NON_GOALS.md         ../docs/
cp starters/memory-architecture.md ../.claude/memory/architecture.md
cp starters/memory-conventions.md  ../.claude/memory/conventions.md
```

---

## Step 7 — Write your conventions and architecture files

The agents `@reviewer` and `@architect` read `.claude/memory/architecture.md` and `.claude/memory/conventions.md` to understand project-specific patterns. The starters ship with instructional comments — fill them in with your actual stack, patterns, and decisions.

The more specific these files are, the more useful the agents become. A blank conventions file produces generic advice; a detailed one produces project-aware advice.

---

## Step 8 — Write a copilot-instructions.md

Create `.github/copilot-instructions.md` with project-level context: what the project is, its key directories, and any agent routing notes. This is the file Copilot loads before every session.

---

## Upgrading

When the library is updated:

```bash
cd skills-library
git pull                                  # if submodule: git submodule update --remote skills-library
python3 init.py --config project.config.yml
cp -r resolved/skills/*        ../.github/agents/
cp -r resolved/instructions/*  ../.github/instructions/
```

Your `project.config.yml` is not overwritten — config is yours to keep.

---

## Adding a project-specific orchestration layer

If you want a `@delivery-lead` style agent that sequences these skills in your own workflow, write it in `.github/agents/` alongside the resolved skills. It stays in your project and is not part of the library. The library ships the role agents; you build the coordination layer on top.
