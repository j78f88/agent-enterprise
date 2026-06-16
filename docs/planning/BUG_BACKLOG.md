# Bug Backlog

Reproduction context for all logged bugs. Status is tracked in BACKLOG_LEDGER.md — not here.
Only @bug appends entries below the marker. Never edit existing entries.

---
<!-- BUG ENTRIES BELOW THIS LINE — do not edit above -->

## BUG-003 — Onboarding agent does not cover Claude Code slash-command setup

**Severity:** WARNING
**Reported:** 2026-05-29
**Reporter:** User (via chat — unable to use `/` commands or pull instructions)

### Description

A user who completes the onboarding flow ends up with `.github/agents/*.agent.md` and `.github/instructions/*.instructions.md` files deployed, but no Claude Code `/` commands registered. The onboarding agent (and its `SKILL.md`) makes no mention of `.claude/commands/` or the distinction between GitHub Copilot `@agent` mentions and Claude Code `/slash` commands. As a result, Claude Code users have no usable entry points to the 13 registered agents and must discover this gap themselves.

### Steps to Reproduce

1. Clone the repo and run `python init.py --config config/project.config.yml`
2. Open the project in Claude Code (CLI or VS Code extension)
3. Type `/` and observe — none of the 13 agents appear
4. Type `@` in GitHub Copilot Chat — agents do appear there
5. Observe that onboarding SKILL.md contains no guidance on `.claude/commands/`

### Expected Behavior

After onboarding:
- Claude Code users should have 13 `/command-name` shortcuts available
- The onboarding flow should explain the platform split: Copilot uses `@agent`, Claude Code uses `/command`
- `.claude/commands/` should be seeded automatically (or the user guided to do so)

### Actual Behavior

- No `.claude/commands/` directory is created or mentioned by onboarding
- No `/` commands are available in Claude Code after setup
- The only way to invoke agents is via Copilot `@` mentions

### Environment

- Claude Code CLI / VS Code extension (any version)
- Windows 11 / agent-enterprise main branch
- Repro confirmed: `.claude/commands/` was absent until manually created

### Notes

- The `.github/agents/*.agent.md` files are the source of truth — commands should mirror them
- A fix could be: add a "Claude Code setup" section to `skills/onboarding/onboarding.skill.md` that seeds `.claude/commands/` from the resolved agents, or add it as a step in `init.py`
- The `project.config.yml` and `project.config.example.yml` have no `paths.claude_commands` token — the path is currently hardcoded knowledge only
- Related: onboarding SKILL.md references "agent-enterprise" but the repo is "agent-enterprise" — name drift suggests the onboarding content was not updated at fork time

---

## BUG-004 — Planner-mode workflow bypassed (implementation executed before approved sprint draft)

**Severity:** WARNING
**Reported:** 2026-05-29
**Reporter:** User (via chat)

### Description

In planner mode, a rename request was implemented immediately across the repository before producing and getting approval on a sprint draft. This violated the expected planner sequence (draft in chat -> approval -> file writes / promotion) and required retroactive planning documentation.

### Steps to Reproduce

1. Run a non-trivial repo-wide change request while the assistant is in planner mode
2. Observe that implementation edits begin before a sprint draft is presented and approved
3. Ask for planning artifacts after the fact
4. Observe that draft planning is generated retroactively

### Expected Behavior

- Planner mode produces a sprint draft first
- User approval is obtained before repository edits begin
- Execution handoff occurs only after plan approval

### Actual Behavior

- Repository edits were executed first
- Sprint planning was generated after user escalation

### Environment

- Repository: agent-enterprise
- Branch: main
- Date observed: 2026-05-29

### Notes

- This is a process bug (workflow enforcement gap), not a code defect in runtime features
- Remediation should include an explicit planner-mode checkpoint before any edits on non-trivial tasks
- Linked ledger item: ITEM-007

---

## BUG-005 — init.py leaves unresolved {{paths.*}} tokens across deployed skills & docs

**Severity:** 🟡 Degraded
**Area:** init.py / build system / onboarding
**Reported:** 2026-05-30
**Ledger:** ITEM-008
**Screenshots:** None

### Description

After onboarding, skills and agent docs ship with raw `{{tokens}}`. Three distinct causes:

- **(A) Companion files never resolved or deployed.** `init.py` only processes the main `*.skill.md` file per directory. These companion files keep raw tokens and are never copied to `resolved/` or `.github/agents/`: `skills/planner/session-lifecycle.md`, `skills/planner/session-end-menu.md`, `skills/sprint-lead/phase-details.md`, `skills/sprint-lead/subagent-templates.md`, `skills/security/report-format.md`, `skills/security/audit-checks.md`, `skills/docs/sync-workflow.md`.
- **(B) Code-span tokens skipped.** `substitute()` deliberately skips `{{tokens}}` inside backtick code spans. Agent/skill bodies wrap real path references in backticks for formatting, so they ship unresolved (e.g. `.github/agents/docs.agent.md` "Key Documents" section).
- **(C) Cross-references use source paths.** References point at `skills/<name>/...` source paths that do not exist in an adopter deployment that only ships `.github/agents/`.

### Steps to Reproduce

1. Run `python init.py --config config/project.config.yml`
2. Grep for `{{` under `resolved/` and `.github/agents/`
3. Observe unresolved `{{paths.*}}` / `{{commands.*}}` / `{{git.*}}` tokens
4. Note that companion files (e.g. `phase-details.md`) are absent from `.github/agents/sprint-lead/`

### Expected Behavior

Deployed artifacts contain no unresolved real-reference tokens; companion files are resolved and deployed; cross-references resolve to paths that exist in the deployment.

### Actual Behavior

Raw `{{tokens}}` appear across deployed skills and agent docs; companion files are missing entirely.

### Environment

- Repository: agent-enterprise
- Branch: main
- Date observed: 2026-05-30

### Notes

- Build-system gap in `init.py`, affects every adopter (not a config error from onboarding)
- Remediation draft: `docs/archive/onboarding-path-resolution-remediation-draft-plan.md`
- Linked ledger item: ITEM-008

---

## BUG-006 — init.py has no automated deploy-copy or token-free guardrail for the .github tree

**Severity:** 🟡 Degraded
**Area:** init.py / build system / deployment
**Reported:** 2026-05-30
**Ledger:** ITEM-012
**Screenshots:** None

### Description

BUG-005 fixed token *resolution* (companion files, code spans, cross-refs) so `init.py` now emits a clean `resolved/`. But the deployed tree that agents actually load — `.github/instructions/` and `.github/agents/` — drifted back to containing raw `{{namespace.key}}` tokens. Three distinct root causes, none covered by BUG-005:

- **(A) No automated deploy-copy.** `init.py` only writes to `resolved/`. Copying `resolved/` → `.github/` is a manual step documented only in the "Next steps" output. A prior cleanup sprint regenerated `resolved/` but skipped the copy, so the deployed tree silently went stale. This recurs for every adopter and every rebuild.
- **(B) No guardrail asserting the deployed tree is token-free.** Nothing fails the build (or CI) when `.github/instructions/**` or `.github/agents/**` contains an unresolved `{{namespace.key}}` token. Drift is invisible until a human notices broken references at runtime.
- **(C) Missing config keys produce unresolved tokens with only a non-blocking warning.** `config/project.config.yml` was missing `commands.container_scan`, `commands.iac_scan`, and the entire `security:` block (`sbom_format`, `tracked_files`, `license_gate`, `license_denylist`, `license_allowlist`). `init.py` printed "token warnings" but exited 0, so the broken output shipped.

### Steps to Reproduce

1. Run `python init.py --config config/project.config.yml`
2. Manually edit/regenerate `resolved/` without copying into `.github/` (or omit a config key)
3. Grep `.github/instructions` and `.github/agents` for `\{\{[a-zA-Z_]+\.[a-zA-Z_]+`
4. Observe stale `{{paths.*}}` / `{{commands.*}}` / `{{security.*}}` tokens in the files agents load
5. Note the build still exited 0 — nothing flagged the drift

### Expected Behavior

A single build command produces a token-free deployed tree, OR the build/CI fails loudly when `.github/**` contains unresolved real-reference tokens. Missing config keys that leave unresolved tokens should fail the build, not warn-and-continue.

### Actual Behavior

Deployed `.github/` files contain raw `{{tokens}}`; the build exits 0 regardless; the deploy-copy is a manual step that is easy to skip.

### Environment

- Repository: agent-enterprise
- Branch: main
- Date observed: 2026-05-30

### Notes

- Distinct from BUG-005: that was token *resolution* inside `init.py`; this is the *deploy + verification* gap around it
- Affects every adopter — agent-enterprise is consumed this way downstream
- Immediate symptom was hand-fixed this session (config keys added, resolved/ rebuilt clean, copied into .github/, verified zero tokens); this entry tracks the durable guardrail so it cannot recur
