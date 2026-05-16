# Skills Library — Implementation Plan

> **[ARCHIVED — historical planning document]**
>
> This document captures the original plan for extracting the agent skills library from a parent monorepo (where it lived under `skills-library/` alongside `apps/` and `packages/`). That extraction is complete: agent-homebase is now its own standalone repository, and the directory layout described below no longer matches reality.
>
> For current architecture, see [ARCHITECTURE.md](ARCHITECTURE.md) and [DUAL_PLATFORM_PLAN.md](DUAL_PLATFORM_PLAN.md). Kept for historical reference only.

---

This document is the working guide for building and extracting the reusable agent skills library from the DIY project. It lives inside `skills-library/` — a top-level directory that is explicitly separate from the web app delivery pipeline (`apps/`, `packages/`).

---

## Separation Strategy

The `skills-library/` directory is treated as a project-within-a-project. It shares the same git repository for now so work can happen alongside normal sprints without a context switch. When the library is ready to publish, it gets extracted into its own standalone repo using `git subtree split`. Nothing in `apps/` or `packages/` references anything in `skills-library/`, and the web app build pipeline ignores it entirely.

Add the following to `.gitignore` at the repo root to keep the library's working files out of web app tooling:

```
# Skills library — not part of web app build
skills-library/resolved/
skills-library/__pycache__/
```

No changes to `pnpm-workspace.yaml`, `vite.config.ts`, or any build config are needed — the directory is plain markdown and Python, invisible to the JS toolchain.

---

## Target Folder Structure

```
skills-library/
├── IMPLEMENTATION_PLAN.md        # This file
├── README.md                     # Library overview and quick-start
├── ONBOARDING.md                 # Step-by-step guide for new projects
├── CHANGELOG.md                  # Library version history
│
├── plugin.json                   # Plugin manifest (cross-compatible: VS Code + Claude Code)
├── project.config.example.yml    # Config template — consuming projects fill this in
├── init.py                       # Token substitution script
│
├── skills/                       # One folder per skill — {name}.skill.md format
│   ├── pm/
│   │   └── pm.skill.md
│   ├── planner/
│   │   └── planner.skill.md
│   ├── sprint-lead/
│   │   └── sprint-lead.skill.md
│   ├── qa/
│   │   └── qa.skill.md
│   ├── reviewer/
│   │   └── reviewer.skill.md
│   ├── architect/
│   │   └── architect.skill.md
│   ├── researcher/
│   │   └── researcher.skill.md
│   ├── bug/
│   │   └── bug.skill.md
│   ├── docs/
│   │   └── docs.skill.md
│   ├── a11y/
│   │   └── a11y.skill.md
│   ├── perf/
│   │   └── perf.skill.md
│   └── security/
│       └── security.skill.md
│
├── agents/                       # Hand-crafted agent bodies for VS Code wrappers
│   ├── a11y.body.md
│   ├── architect.body.md
│   ├── bug.body.md
│   ├── docs.body.md
│   ├── perf.body.md
│   ├── planner.body.md
│   ├── pm.body.md
│   ├── qa.body.md
│   ├── researcher.body.md
│   ├── reviewer.body.md
│   ├── security.body.md
│   └── sprint-lead.body.md
│
├── instructions/                 # Supporting instruction files
│   ├── generic/                  # Copy as-is — no substitution needed
│   │   ├── askquestions-contract.instructions.md
│   │   ├── batch-report.instructions.md
│   │   ├── commit-conventions.instructions.md
│   │   ├── contract-change-checklist.instructions.md
│   │   ├── determinism-guarantees.instructions.md
│   │   ├── fsm-orchestration.instructions.md
│   │   ├── observability.instructions.md
│   │   ├── security-model.instructions.md
│   │   ├── state-management.instructions.md
│   │   └── subagent-return-schemas.instructions.md
│   └── configurable/             # Require token substitution before use
│       ├── backlog-ledger.instructions.md
│       ├── bug-backlog-format.instructions.md
│       ├── composition-rules.instructions.md
│       ├── engagement-format.instructions.md
│       ├── engagement-gates.instructions.md
│       ├── handoff-rejection-format.instructions.md
│       ├── non-goals-governance.instructions.md
│       ├── planning-compliance.instructions.md
│       ├── planning-preflight.instructions.md
│       ├── retro-report.instructions.md
│       ├── security-audit.instructions.md
│       ├── severity-levels.instructions.md
│       ├── sprint-docs-format.instructions.md
│       └── validation-framework.instructions.md
│
├── starters/                     # Seed files for new projects
│   ├── BACKLOG_LEDGER.md
│   ├── BUG_BACKLOG.md
│   ├── FILE_HASHES.md
│   ├── HANDOFF_REJECTIONS.md
│   ├── memory-architecture.md    # Starter .claude/memory/architecture.md
│   ├── memory-conventions.md     # Starter .claude/memory/conventions.md
│   ├── NON_GOALS.md
│   ├── SECURITY_CHANGELOG.md
│   └── SPRINTS.md
│
├── profiles/                     # Pre-filled configs for common project types
│   ├── react-web-app.config.yml
│   ├── python-api.config.yml
│   └── monorepo-fullstack.config.yml  # Mirrors this project — reference implementation
│
└── resolved/                     # Git-ignored — init.py writes output here
    ├── skills/
    ├── agents/                   # VS Code agent wrappers (when editor.target includes vscode)
    └── instructions/
```

---

## Skill File Format

Every skill lives in its own folder inside `skills/`. The source file is named `{name}.skill.md` (e.g., `skills/architect/architect.skill.md`) for easy identification in editors. At build time, `init.py` resolves these to `SKILL.md` in the output directory — the folder name must exactly match the `name` field in the frontmatter, as required by the VS Code SKILL.md spec. The description field is what the agent uses to decide when to load the skill, so write it to describe both what it does and when to invoke it, not as a tagline.

```markdown
---
name: pm
description: Validates whether features are worth building using a 5-test
  echo-chamber filter. Use when you have a feature idea, competitive research
  finding, or brainstorm output that needs pressure-testing before sprint
  planning begins. Also use for roadmap prioritisation decisions.
---

[full instruction body here — identical to the current agent file content
 minus hardcoded project paths, which become {{config.tokens}}]
```

Optional frontmatter fields worth using for this library: `when_to_use` (concrete trigger phrases to improve discovery), `user-invocable: true` (makes the skill appear as a slash command the user can call directly). The `user-invocable` flag is particularly useful for skills like `@bug` and `@researcher` where the user initiates them directly rather than an orchestrator invoking them.

---

## plugin.json

The plugin manifest bundles all skills into a single installable package. There is a known cross-compatibility constraint: Claude Code rejects `plugin.json` with a validation error if a `skills` field is present, but VS Code requires it. The workaround is to omit the `skills` field — both tools then work correctly because they discover skills by scanning the directory.

```json
{
  "name": "agent-homebase",
  "version": "1.0.0",
  "description": "Reusable agent skills for software delivery: product validation, sprint planning, execution, quality gates, and documentation.",
  "author": {
    "name": "Your Name",
    "url": "https://github.com/j78f88"
  },
  "repository": "https://github.com/j78f88/agent-homebase",
  "agents": "skills/",
  "instructions": "instructions/"
}
```

Naming rules: lowercase letters, numbers, and hyphens only. No slashes, colons, or special characters — these cause silent load failures.

---

## project.config.example.yml

The full config file drives all token substitution. Consuming projects copy this, rename it to `project.config.yml`, fill in their values, and run `init.py`. Every `{{placeholder}}` token in the configurable skills and instructions maps to a key in this file.

```yaml
project:
  name: "My Project"
  language: "TypeScript"
  framework: "React + Vite"
  locale: "en-AU"               # Used by @docs for spelling conventions

paths:
  sprints: "sprints/"
  drafts: "docs/planning/drafts/"
  archive: "docs/archive/"
  validation: "docs/planning/validation/"
  research: "docs/planning/research/"
  handoffs: "docs/planning/_handoffs/"
  engagements: "docs/planning/engagements/"
  vision: "docs/planning/vision/"
  # Backlog files
  backlog_ledger: "docs/planning/BACKLOG_LEDGER.md"
  bug_backlog: "docs/planning/BUG_BACKLOG.md"
  bugs_screenshots: "docs/planning/bugs/screenshots/"
  rejections: "docs/planning/HANDOFF_REJECTIONS.md"
  non_goals: "docs/NON_GOALS.md"
  # Planning docs
  roadmap: "docs/planning/ROADMAP.md"
  feature_matrix: "docs/planning/FEATURE_MATRIX.md"
  # Architecture docs
  decisions: "docs/architecture/DECISIONS.md"
  future_considerations: "docs/architecture/FUTURE_CONSIDERATIONS.md"
  design_reviews: "docs/architecture/design-reviews/"
  architecture_doc: "docs/development/ARCHITECTURE.md"
  # Development docs
  technical_debt: "docs/development/TECHNICAL_DEBT.md"
  testing_doc: "docs/development/TESTING.md"
  # User-facing docs
  user_guide: "docs/user/USER_GUIDE.md"
  releases: "docs/user/RELEASES.md"
  changelog: "docs/user/changelog.json"
  changelog_deploy_copy: "apps/web/public/changelog.json"
  package_json: "apps/web/package.json"
  # Agent tooling
  copilot_instructions: ".github/copilot-instructions.md"
  instructions_dir: ".github/instructions"    # Used by @reviewer to reference instruction files
  memory_architecture: ".claude/memory/architecture.md"
  memory_conventions: ".claude/memory/conventions.md"

quality:
  # Coverage thresholds are split — store packages and web components differ
  coverage_store_threshold: 80      # Store packages (e.g. packages/store) — gate blocks below this
  coverage_web_threshold: 60        # Web/app components — gate blocks below this
  e2e_regression_threshold: 5       # % E2E failure rate that triggers CRITICAL
  bundle_warning_kb: 200
  bundle_critical_kb: 500
  build_warning_seconds: 60

platform:
  type: "azure-swa"
  test_workflow: "deploy-test.yml"           # Filename used in gh run list --workflow
  prod_workflow: "deploy-prod.yml"
  ci_workflow_display_name: "Azure Static Web Apps CI/CD"  # Display name in GitHub Actions UI
  test_url: "https://your-app-test.azurestaticapps.net"
  prod_url: "https://your-app.azurestaticapps.net"
  e2e_runner: "playwright"

git:
  main_branch: "master"
  develop_branch: "develop"

ids:
  bug_prefix: "BUG"
  item_prefix: "ITEM"
  rejection_prefix: "REJ"
  engagement_prefix: "ENG"
  adr_prefix: "ADR"

escalation:
  # Item deferral thresholds
  def_p0_threshold: 3               # Def >= this → P0 mandatory inclusion
  def_kill_threshold: 5             # Def >= this → must resolve or kill
  age_stale_sprints: 10             # Age >= this → stale warning
  # Debt health by sprint count
  debt_warning_sprints: 3
  debt_escalate_sprints: 5
  # Debt health by item count
  debt_warning_items: 20            # Debt item count that triggers warning
  debt_escalate_items: 40           # Debt item count that triggers escalation
  debt_min_allocation_percent: 30   # Minimum % of sprint capacity reserved for debt
  # Sprint composition
  sprint_size_min: 5
  sprint_size_max: 8
  feature_cap_percent: 70           # Max % of sprint that can be features
  p0_overflow_percent: 50           # If P0 items exceed this % of capacity, offer overflow relief

scope_upgrade:
  task_count: 3
  files_affected: 8

commands:
  install: "pnpm install"
  dev: "pnpm dev"
  test: "pnpm test"
  typecheck: "pnpm typecheck"
  lint: "pnpm lint"
  build: "pnpm build"
  e2e: "pnpm test:e2e"
  coverage: "pnpm test:coverage"
  depcheck: "npx depcheck --json"   # Used by @perf for dependency audit
  # Cross-platform ISO timestamp — used by @sprint-lead for phase timing
  # Do NOT use Get-Date (PowerShell/Windows only). Use the value below on bash/zsh,
  # or replace with your CI environment's equivalent.
  timestamp: "date -u +\"%Y-%m-%dT%H:%M:%SZ\""

team:
  cto_name: "Your Name"  # FIXME
```

---

## init.py

The substitution script reads `project.config.yml`, flattens all keys to dot-notation (`paths.backlog_ledger`, `quality.coverage_store_threshold`, etc.), then walks all `.md` files in `skills/` and `instructions/configurable/`, replacing `{{token}}` occurrences and writing resolved files to `resolved/`.

```python
#!/usr/bin/env python3
"""
init.py — Token substitution for skills-library.
Usage: python3 init.py --config project.config.yml
Output: resolved/ directory ready to copy into .github/
"""

import argparse
import os
import re
import shutil
import yaml
from pathlib import Path


def flatten(d, prefix=""):
    """Flatten nested dict to dot-notation keys."""
    result = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.update(flatten(v, key))
        else:
            result[key] = str(v)
    return result


def substitute(text, tokens):
    """Replace {{token}} occurrences with config values."""
    def replace(match):
        key = match.group(1).strip()
        if key not in tokens:
            print(f"  WARNING: no config value for {{{{ {key} }}}}")
            return match.group(0)   # leave unreplaced so it's visible
        return tokens[key]
    return re.sub(r"\{\{([^}]+)\}\}", replace, text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="project.config.yml")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)
    tokens = flatten(config)

    output = Path("resolved")
    if output.exists():
        shutil.rmtree(output)

    # Skills ({name}.skill.md files) — substitute and output as SKILL.md
    for skill_md in sorted(Path("skills").rglob("*.skill.md")):
        dest = output / skill_md
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(substitute(skill_md.read_text(), tokens))
        print(f"  resolved: {dest}")

    # Configurable instructions
    for instr in Path("instructions/configurable").glob("*.md"):
        dest = output / "instructions" / instr.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(substitute(instr.read_text(), tokens))
        print(f"  resolved: {dest}")

    # Generic instructions — copy as-is
    for instr in Path("instructions/generic").glob("*.md"):
        dest = output / "instructions" / instr.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(instr, dest)
        print(f"  copied:   {dest}")

    # Final check — flag any remaining unresolved tokens
    unresolved = []
    for md in output.rglob("*.md"):
        matches = re.findall(r"\{\{[^}]+\}\}", md.read_text())
        if matches:
            unresolved.append((md, matches))

    if unresolved:
        print("\n⚠  Unresolved tokens found — check project.config.yml:")
        for path, tokens_found in unresolved:
            print(f"  {path}: {tokens_found}")
    else:
        print("\n✓ All tokens resolved.")
        print("  Copy resolved/skills/     → .github/agents/  (or your skills path)")
        print("  Copy resolved/instructions/ → .github/instructions/")


if __name__ == "__main__":
    main()
```

---

## Extraction Phases

### Phase 1 — Scaffold (Day 1)

Create the `skills-library/` directory structure. No content yet — just the skeleton. Commit as `chore: scaffold skills-library directory`. This establishes the separation before any content moves.

Create `plugin.json` with the manifest stub. Create `project.config.example.yml` with all fields (use the template above). Copy `init.py` across. Add `skills-library/resolved/` to `.gitignore`.

Verify nothing in the web app build references the new directory. Run `pnpm build` to confirm it's clean.

### Phase 2 — Generic Instructions (Day 1-2)

Copy the six generic instruction files from `.github/instructions/` into `skills-library/instructions/generic/`. These files need no changes — they are already project-agnostic. Commit as `chore: skills-library — add generic instructions`.

Files: `askquestions-contract`, `batch-report`, `subagent-return-schemas`, `severity-levels`, `commit-conventions`, `contract-change-checklist`.

Apply token changes to `severity-levels` before copying: replace the store coverage threshold (80%) with `{{quality.coverage_store_threshold}}` and the web coverage threshold (60%) with `{{quality.coverage_web_threshold}}`, then move it to `instructions/configurable/` instead of `generic/`.

### Phase 3 — Configurable Instructions (Day 2-3)

Copy the remaining twelve instruction files into `skills-library/instructions/configurable/` and work through each one applying the token substitutions documented in `docs/planning/AGENT_SKILLS_EXTRACTION_PLAN.md`. The substitution map is already defined there — this phase is mechanical execution.

After each file, run a quick grep to confirm no hardcoded paths or thresholds survive: `grep -n "docs/planning\|pnpm\|80%\|60%\|70%\|BUG-\|ITEM-\|REJ-\|ENG-\|master\|develop" instructions/configurable/filename.md`

Commit when all twelve are done: `chore: skills-library — add configurable instructions`.

### Phase 4 — Tier 1 Skills (Day 3-4)

Convert the six lowest-complexity agents into SKILL.md format. For each:

1. Create the folder: `skills-library/skills/<name>/`
2. Create `<name>.skill.md` with the correct frontmatter (`name` must match folder name)
3. Paste the current agent file body as the instruction content
4. Replace all hardcoded values with `{{config.tokens}}`
5. Write a description that covers both what it does and concrete trigger conditions
6. Add `user-invocable: true` where the user initiates the skill directly

Agents in this tier: `bug`, `a11y`, `perf`, `researcher`, `architect`, `reviewer`.

**Special handling for `reviewer`:** The current agent hardcodes six `.github/instructions/` paths in its shared rules section (e.g. `.github/instructions/severity-levels.instructions.md`). Replace all of these with `{{paths.instructions_dir}}/severity-levels.instructions.md` etc., using the `paths.instructions_dir` token. This makes the reviewer portable to any project that places instructions in a different directory.

Commit: `chore: skills-library — tier 1 skills (bug, a11y, perf, researcher, architect, reviewer)`.

### Phase 5 — Tier 2 and 3 Skills (Day 4-6)

Tier 2 agents (`qa`, `pm`, `docs`) follow the same process with moderately more token substitution.

Tier 3 agents (`planner`, `sprint-lead`) are the most path-heavy. Take these one at a time. After converting each, run `init.py` against the example config and manually review the resolved output — verify no `{{` tokens survive and no project-specific paths appear.

**Special handling for `sprint-lead`:** The current agent uses `Get-Date -Format o` for phase boundary timestamps. This is PowerShell-only and fails on Linux and Mac. Replace it with `{{commands.timestamp}}`, which the config maps to the portable bash equivalent `date -u +"%Y-%m-%dT%H:%M:%SZ"`. Document this in the skill's frontmatter under `when_to_use` so consuming projects on Windows know to override the token with a PowerShell equivalent if needed.

Do not extract `delivery-lead`. That agent is a personal orchestration layer that references these skills from the outside. It stays in `.github/agents/` as a consuming project's example of how to build on top of the library.

Commit after Tier 2: `chore: skills-library — tier 2 skills (qa, pm, docs)`.
Commit after Tier 3: `chore: skills-library — tier 3 skills (planner, sprint-lead)`.

### Phase 6 — Starters, Profiles, and Docs (Day 6-7)

Write the starter template files in `skills-library/starters/`. These are minimal seed files for new projects — blank `BACKLOG_LEDGER.md` with headers only, empty `BUG_BACKLOG.md`, empty `HANDOFF_REJECTIONS.md`, stub `SPRINTS.md`, blank `NON_GOALS.md`, and the two memory files with instructional comments explaining what to fill in.

Write the three profile configs: `react-web-app`, `python-api`, and `monorepo-fullstack` (this project's values, as the reference implementation).

Write `README.md` (library overview), `ONBOARDING.md` (step-by-step new project guide), and `CHANGELOG.md` (initial version 1.0.0 entry).

Commit: `chore: skills-library — starters, profiles, docs`.

---

## Validation Checklist

Before calling the library ready, run through this:

**Token resolution.** Run `python3 init.py --config profiles/monorepo-fullstack.config.yml` from inside `skills-library/`. The resolved output for this profile should produce files that are functionally equivalent to the current `.github/agents/` and `.github/instructions/` files. Diff them manually.

**No surviving tokens.** After resolution, `grep -r "{{" resolved/` should return nothing.

**No web app bleed.** Confirm `pnpm build`, `pnpm test`, and `pnpm typecheck` still pass — the skills-library directory should be completely invisible to the JS toolchain.

**VS Code skill discovery.** If the Copilot agent skills feature is active, install the plugin locally and confirm VS Code lists the skills correctly and matches them to appropriate prompts.

**Cross-tool check.** Confirm `plugin.json` loads in both Claude Code (Cowork) and GitHub Copilot without validation errors. The absence of a `skills` field in `plugin.json` is the critical cross-compatibility fix — do not add it.

**React web app profile.** Run `init.py` against `profiles/react-web-app.config.yml` and verify the resolved output makes sense for a plain React + Vite project with no monorepo structure.

---

## Git Extraction (When Ready to Publish)

When the library is stable and you want to publish it as a standalone repo:

```bash
# From the repo root — extract skills-library/ commit history into its own branch
git subtree split --prefix=skills-library --branch skills-library-standalone

# Push directly to agent-homebase (empty repo, no initial commit)
git push https://github.com/j78f88/agent-homebase.git skills-library-standalone:main
```

That's it — two commands. The `skills-library/` folder's full commit history lands in `agent-homebase` as the `main` branch. The original DIY project repo is unaffected.

To wire up the upgrade flow after publishing, replace the local `skills-library/` folder with a git submodule:

```bash
# From the repo root
rm -rf skills-library/
git submodule add https://github.com/j78f88/agent-homebase.git skills-library
git commit -m "chore: convert skills-library to submodule (agent-homebase)"
```

From that point, `git submodule update --remote skills-library` pulls any updates from `agent-homebase` into this project. Any other project consuming the library does the same.

---

## What Stays in the DIY Project

After extraction, the DIY project retains:

- `.github/agents/delivery-lead.agent.md` — personal orchestration layer, not in the library
- `.github/agents/*.agent.md` — the resolved/installed versions of library skills (these are what Copilot actually loads; the library is the source of truth)
- `.github/instructions/*.instructions.md` — resolved versions
- `.github/copilot-instructions.md` — project-specific Copilot instructions
- `.github/prompts/` — prompt files reference agents by name; they stay project-side
- All planning and architecture docs — project state, not methodology

---

---

## Dry Run Findings (2026-04-26)

A pre-implementation audit was run against all 12 agent files and 18 instruction files before any extraction began. Seven issues were found and fixed in this document. Recorded here for traceability.

**Fixed — Coverage thresholds split.** `qa.agent.md` uses 80% for store packages and 60% for web components separately. The config previously had a single `coverage_critical_threshold`. Resolved by splitting into `quality.coverage_store_threshold` and `quality.coverage_web_threshold`.

**Fixed — Four composition constants missing from config.** `composition-rules.instructions.md` contained hardcoded P0 overflow percent (50%), debt warning item count (20), debt escalate item count (40), and debt minimum allocation percent (30%). All four added to the `escalation` block.

**Fixed — `reviewer.agent.md` hardcodes `.github/instructions/` paths.** Six instruction file paths are referenced by full `.github/instructions/` path. Added `paths.instructions_dir` token and noted the fix in Phase 4 instructions.

**Fixed — `"Azure Static Web Apps CI/CD"` hardcoded in `engagement-gates`.** The gh CLI command used this literal string. Added `platform.ci_workflow_display_name` token to config.

**Fixed — `Get-Date -Format o` is PowerShell-only.** `sprint-lead.agent.md` uses this Windows-only command for phase timestamps. Added `commands.timestamp` token mapped to a portable bash equivalent, with a note in Phase 5 instructions.

**Fixed — `commands.depcheck` missing.** `perf.agent.md` calls `npx depcheck --json` with no corresponding config key. Added to `commands` block.

**Fixed — Ten path tokens missing from config.** Paths for `validation`, `user_guide`, `releases`, `vision`, `design_reviews`, `testing_doc`, `architecture_doc`, `copilot_instructions`, `instructions_dir`, `memory_architecture`, and `memory_conventions` were absent. All added. Also renamed `paths.ledger` → `paths.backlog_ledger` and `paths.bugs` → `paths.bug_backlog` for naming consistency with the actual files they reference.

*Plan last updated: 2026-04-26*
