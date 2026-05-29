# Bug Backlog

Reproduction context for all logged bugs. Status is tracked in BACKLOG_LEDGER.md — not here.
Only @bug appends entries below the marker. Never edit existing entries.

---
<!-- BUG ENTRIES BELOW THIS LINE — do not edit above -->

## BUG-001 — Login redirect fails on Safari

**Severity:** WARNING  
**Reported:** 2026-04-20  
**Reporter:** QA team  

### Description

After successful OAuth login, Safari users are redirected to a blank page instead of the dashboard.

### Steps to Reproduce

1. Open app in Safari 17.x
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Observe blank page instead of dashboard

### Expected Behavior

User should land on `/dashboard` after successful authentication.

### Actual Behavior

User sees blank white page. URL shows `/callback?code=...` — redirect never completes.

### Environment

- Browser: Safari 17.4
- OS: macOS Sonoma 14.4
- Device: MacBook Pro M3

### Screenshots

See `bugs/screenshots/BUG-001-safari-blank.png`

### Notes

- Works correctly in Chrome, Firefox, Edge
- Likely related to Safari's stricter cookie handling
- Possibly a SameSite cookie issue

---

## BUG-002 — Dashboard charts don't render on slow connections

**Severity:** SUGGESTION  
**Reported:** 2026-04-25  
**Reporter:** User feedback  

### Description

On slow 3G connections, dashboard charts show loading spinner indefinitely.

### Steps to Reproduce

1. Enable network throttling (Slow 3G preset)
2. Navigate to dashboard
3. Wait 30+ seconds

### Expected Behavior

Charts should render within 10 seconds or show error state.

### Actual Behavior

Loading spinner persists indefinitely. No error shown.

### Environment

- Any browser with network throttling
- Simulated Slow 3G (400ms RTT, 400kbps down)

### Notes

- Timeout appears to be missing
- Consider adding skeleton loading state
- Lower priority — affects edge case users only

---

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
- Remediation draft: `docs/planning/drafts/onboarding-path-resolution-remediation-draft-plan.md`
- Linked ledger item: ITEM-008
