# Onboarding Guide

Setup for a new project consuming agent-enterprise. Pick the path that fits how
hands-on you want to be — all three produce the same result. The supported
embedded topology is:

```text
adopter-project/
└── skills-library/        # agent-enterprise checkout/submodule
```

Run `init.py` from `skills-library/`. Use `--deploy-root ..` so deploy artifacts
land in the adopter project root, while `resolved/` remains inside the library
checkout.

> **Visual overview:** open [command-centre-visual.html](command-centre-visual.html) in a browser to see all agents, modes, and flows at a glance before diving in.

---

## Three ways to set up

| Path | First action | Best for |
|:-----|:-------------|:---------|
| **Chat** ⭐ | Open the repo in your agent and ask it to set you up | First-timers, "just do it for me" |
| **Guided CLI** | `python init.py --config config/project.config.example.yml --quick-setup` | Comfortable in a terminal, want prompts not YAML |
| **Manual** | Edit `config/project.config.example.yml`, then run `init.py` | Maximum control, reproducible/CI setups |

## Choose the delivery modes you need

- **Mode 1 — Team:** install project-local agents/instructions with `init.py`; this is the normal onboarding path.
- **Mode 2 — Orchestration:** add non-interactive queue dispatch with `dispatch.py`; see [ORCHESTRATION.md](ORCHESTRATION.md).
- **Mode 3 — Choreography:** coordinate multiple projects from a separate registry workspace; see [CHOREOGRAPHY.md](CHOREOGRAPHY.md).

Mode 1 is the default first install. Add Mode 2 when you want queued, verified work execution. Add Mode 3 when you have multiple projects to coordinate and harvest learning from.

---

## Chat-driven setup (recommended)

Clone the repo, open the folder in **GitHub Copilot Chat** or **Claude Code**,
and paste:

```text
Set up agent-enterprise for my project. Ask me what you need, recommend a
profile, run init.py, deploy the resolved files, and verify it works.
```

The `@onboarding` agent drives the whole flow for you:

1. **Interviews you** — name, language/framework, repo, branch, team size, platform target (~5 questions).
2. **Recommends a profile** with rationale, and lets you override.
3. **Fills the config and runs the build** (`init.py`) — no YAML editing.
4. **Deploys the resolved files** into your project's directories.
5. **Seeds only the planning files you're missing** — never overwrites yours.
6. **Verifies** everything (files in place, no unresolved tokens) and reports a checklist.
7. **Self-removes after confirmation** — before `setup_complete: true`, the onboarding agent is present so it can finish setup; after `setup_complete: true` and the next `init.py --deploy --deploy-root ..`, setup-only onboarding artifacts are pruned.

If anything is unclear it asks rather than guessing. When it finishes, jump
straight to a real task: `@planner scope my first feature`.

Want to drive it yourself instead? The manual steps are below.

---

## Manual setup (Guided CLI or by hand)

The steps below are what the chat path does for you. Follow them directly if
you prefer the terminal — the Guided CLI uses `--quick-setup` at Step 3; the
fully manual path edits the config by hand.

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
git submodule add https://github.com/j78f88/agent-enterprise.git skills-library
```

### Option B — One-time copy

Copies files once. No auto-updates, but simpler setup if you don't plan to upgrade.

```bash
git clone https://github.com/j78f88/agent-enterprise.git skills-library
rm -rf skills-library/.git   # detach from library history
```

---

## Step 3 — Choose a profile and fill in config

For a clean adopter smoke or a first embedded setup, start with the canonical
config path used by the build/deploy examples: `config/project.config.example.yml`.
If you prefer one of the prebuilt profiles, copy it into that path (or pass your
own config path consistently in the commands below):

```bash
cd skills-library
cp profiles/react-web-app.config.yml config/project.config.example.yml
# or: cp profiles/python-api.config.yml config/project.config.example.yml
# or: cp profiles/monorepo-fullstack.config.yml config/project.config.example.yml
```

### Option A — Interactive setup (recommended for first-time)

```bash
python init.py --config config/project.config.example.yml --quick-setup
```

This prompts for the essential values (project name, repo, namespace, branch) and updates your config.

### Option B — Manual edit

Open `config/project.config.example.yml` and fill in every `FIXME` value. **If you skip this step, agents won't run correctly** - the system will show which values are missing (marked with ⚠) when you run `init.py`.

**Platform selection:** Set `editor.target` to control which platform-native artifacts are emitted. Every target gets the base set (skills, agent wrappers, instructions, Claude Code slash commands); the target adds the platform's own surface on top:

| Value | Adds on top of the base set | Best For |
|:------|:----------------------------|:---------|
| `"both"` (default) | Claude Code subagents (`.claude/agents/`) | Teams on Copilot + Claude Code |
| `"vscode"` | Skills set to non-invocable (use `@agent` instead) | VS Code-only teams |
| `"claude-code"` | Claude Code subagents (`.claude/agents/`) | Claude Code-only teams |
| `"cursor"` | Cursor rules (`.cursor/rules/`) + commands (`.cursor/commands/`) | Cursor-only teams |
| `"codex"` | Managed block merged into your `AGENTS.md` | Codex-only teams |
| `"all"` | Everything above (without the vscode skill suppression) | Mixed/every platform |

See [PLATFORMS.md](PLATFORMS.md) for the full per-platform artifact map and how each platform consumes its files.

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
python init.py --config config/project.config.example.yml
```

Watch for `⚠` warnings — each one is a token with no config value. Fix your config and re-run until the output shows `✓ All tokens resolved`. Missing required keys cause `init.py` to exit non-zero with an actionable error message indicating which key is absent.

---

## Step 5 — Deploy resolved files

```bash
# Recommended: build + copy in one step
python init.py --config config/project.config.example.yml --deploy --deploy-root ..
```

`--deploy` copies `resolved/` into the configured target directories (`.github/agents/`, `.github/instructions/`) under `--deploy-root` and additionally seeds `.claude/commands/` with one `.md` file per agent for Claude Code slash-command support. Depending on `editor.target`, it also seeds `.claude/agents/` (Claude Code subagents), `.cursor/rules/` + `.cursor/commands/` (Cursor), or merges a managed block into your `AGENTS.md` (Codex) — see [PLATFORMS.md](PLATFORMS.md). Keep `paths.*` values relative and traversal-free; do not put `../` in config paths to target the adopter root.

If you prefer manual control:

```bash
cp -r resolved/skills/*        ../.github/agents/
cp -r resolved/instructions/*  ../.github/instructions/
cp -r resolved/agents/*        ../.github/agents/
```

> **Note:** `init.py` generates thin `.agent.md` wrappers in `resolved/agents/` for every `editor.target` — they carry native tool restrictions and subagent delegation, and the per-platform emitters (Claude Code subagents, Cursor commands, the Codex `AGENTS.md` block) are rendered from them. They go alongside skills in `.github/agents/`. Manual copying covers only the `.github/` tree; prefer `--deploy` so the platform directories for your target are seeded too.

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

Run these checks from `skills-library/` after `python init.py --config config/project.config.example.yml --deploy --deploy-root ..`.

### 9.1 Before marking setup complete

The onboarding skill is still present at this point because it is the setup assistant.

```bash
# Core Mode 1 files should be deployed into the adopter root
test -d ../.github/agents
test -d ../.github/instructions
test -f ../.github/agents/planner.agent.md
test -d ../.github/agents/planner

# Onboarding should still exist before setup_complete flips
test -f ../.github/agents/onboarding.agent.md
test -d ../.github/agents/onboarding
```

Check platform surfaces for your `editor.target`:

| `editor.target` | Smoke check |
| --- | --- |
| `both` / `claude-code` / `all` | `test -f ../.claude/commands/planner.md` and `test -f ../.claude/agents/planner.md` |
| `vscode` | `test -f ../.claude/commands/planner.md` and `test ! -f ../.claude/agents/planner.md` |
| `cursor` / `all` | `test -f ../.cursor/commands/planner.md` and `test -d ../.cursor/rules` |
| `codex` / `all` | `grep -q "agent-enterprise:begin" ../AGENTS.md` |

Verify no real unresolved config tokens remain in deployed files. This intentionally checks only dotted build tokens like `{{project.name}}`; documentation literals such as `{{tokens}}` and GitHub Actions syntax such as `${{ secrets.TOKEN }}` are allowed.

```bash
python - <<'PY'
import re
import sys
from pathlib import Path

root = Path('..')
scan_roots = [
    root / '.github' / 'agents',
    root / '.github' / 'instructions',
    root / '.claude',
    root / '.cursor',
    root / 'AGENTS.md',
]
token_re = re.compile(r'(?<!\$)(\\?)\{\{([a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)+)\}\}')
findings = []
for scan_root in scan_roots:
    if not scan_root.exists():
        continue
    files = [scan_root] if scan_root.is_file() else sorted(scan_root.rglob('*.md'))
    for file_path in files:
        try:
            lines = file_path.read_text(encoding='utf-8').splitlines()
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(lines, start=1):
            for match in token_re.finditer(line):
                if match.group(1) != '\\':
                    findings.append(f'{file_path}:{line_no}: {{{{{match.group(2)}}}}}')
if findings:
    print('⚠ Unresolved config tokens found:')
    print('\n'.join(findings))
    sys.exit(1)
print('✓ No unresolved config tokens in deployed surfaces')
PY
```

### 9.2 Mark setup complete and verify self-removal

After the onboarding checklist passes, set `setup_complete: true` in `config/project.config.example.yml`, then rerun deploy:

```bash
python init.py --config config/project.config.example.yml --deploy --deploy-root ..
```

Expected after this second deploy:

```bash
# Setup-only onboarding artifacts are pruned from generated and deployed surfaces
test ! -e resolved/skills/onboarding
test ! -e resolved/agents/onboarding.agent.md
test ! -e ../.github/agents/onboarding
test ! -e ../.github/agents/onboarding.agent.md
test ! -e ../.claude/commands/onboarding.md
test ! -e ../.claude/agents/onboarding.md
test ! -e ../.cursor/commands/onboarding.md

# If editor.target includes codex, onboarding should also be absent from the managed roster
! grep -Fq "**onboarding**" ../AGENTS.md 2>/dev/null || echo "⚠ onboarding still appears in AGENTS.md"
```

This before/after state is intentional: onboarding exists while setup is in progress, then disappears once setup is complete so future agent rosters contain only day-to-day roles.

### 9.3 Test the library (optional but recommended)

```bash
cd skills-library
pytest tests/ -v
# Expected: all tests pass
```

### 9.4 Quick interactive smoke test

In VS Code with Copilot Chat:
1. Open your project root (not the `skills-library` checkout).
2. Type `@planner` and hit Enter.
3. If the agent responds, your setup is working.

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
python init.py --config config/project.config.example.yml --deploy --deploy-root ..
```

Your config file is not overwritten — keep it under `skills-library/config/` (or pass its explicit path) and keep `paths.*` relative to the adopter root. `--deploy-root ..` sends refreshed platform artifacts back into the project root.

---

## Adding a project-specific orchestration layer

If you want a custom orchestrator agent that sequences these skills in your own workflow, write it in `.github/agents/` alongside the resolved skills. It stays in your project and is not part of the library. The library ships the role agents; you build the coordination layer on top.
