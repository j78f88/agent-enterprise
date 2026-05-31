# Sprint 2 — Build-System Hardening & Process Hygiene

**Status:** Draft · **Type:** Mixed (bug-fix / debt)
**Sources:** BUG-006, BUG-003, BUG-004, Sprint 1 retro/review · **Ledger:** ITEM-012, ITEM-006, ITEM-007, ITEM-011, ITEM-009, ITEM-010
**Dependencies:** None (Sprint 1 BUG-005 resolution is the foundation this builds on)

## Goals

- A single build command produces a token-free **deployed** tree (`.github/**`), or the build/CI fails loudly when it doesn't.
- Claude Code users get working `/` commands after onboarding, with the platform split documented.
- Planner-mode enforces a draft-approval checkpoint before any repo edits.
- Sprint 1 retro/review follow-ups (CI build-command check, `SOURCE_STYLE_REFS` derivation) are closed.
- Demo/template content is purged from the ledger and SPRINTS so future composition scoring is reliable.

## Why This Sprint

Sprint 1 fixed token *resolution* inside `init.py`. BUG-006 (🟡 Degraded) shows the *deploy + verification* gap remains — the tree agents actually load drifted back to raw tokens and the build still exits 0. Pairing that with the onboarding gap (BUG-003), the planner-process gap (BUG-004), and the small retro debt items forms one coherent "make the build and workflow self-verifying" theme. All same area, low blast radius, high adopter value.

## Technical Tasks

Execution order: **1 → 2 → 3** are the build/CI core (sequenced); **4, 5, 6, 7** are independent and can run in parallel.

### Task Group 1: Automated deploy-copy + fail-on-unresolved (ITEM-012 / BUG-006)
Files: `init.py`, `config/project.config.yml`, `tests/test_init.py`

- [ ] Add a deploy-copy step (or documented single command) that writes `resolved/` → `.github/` as part of the build, removing the manual copy.
- [ ] Add the missing config keys (`commands.container_scan`, `commands.iac_scan`, and the full `security:` block) so they resolve.
- [ ] Make missing config keys that leave unresolved real-reference tokens **fail the build** (non-zero exit), not warn-and-continue.
- [ ] Add test: build emits a token-free `.github/**`; a deliberately missing key fails the build.

### Task Group 2: Token-free guardrail for the deployed tree (ITEM-012 / BUG-006)
Files: `scripts/`, `tests/test_init.py`, CI config

- [ ] Add a guardrail (script + CI step) asserting `.github/instructions/**` and `.github/agents/**` contain no `{{namespace.key}}` real-reference tokens.
- [ ] Wire it so CI fails on drift.
- [ ] Add test covering the guardrail's pass/fail behaviour.

### Task Group 3: CI canonical-build-command check (ITEM-011)
Files: `scripts/`, CI config, `tests/`

- [ ] Add a CI/test check asserting all docs reference `config/project.config.example.yml` for the canonical build command.
- [ ] Flag any doc that drifts to a different config path.

### Task Group 4: Derive `SOURCE_STYLE_REFS` (ITEM-009)
Files: `tests/test_init.py`

- [ ] Replace the hardcoded 7-item allowlist at `tests/test_init.py` (~L894) with a derivation from the config/resolved tree.
- [ ] Verify the derived set matches the current intent (no silent coverage loss).

### Task Group 5: Claude Code `/command` seeding + onboarding docs (ITEM-006 / BUG-003)
Files: `skills/onboarding/onboarding.skill.md`, `init.py` (or onboarding step), `config/project.config.yml` (new `paths.claude_commands` token)

- [ ] Seed `.claude/commands/` from the resolved agents (mirror `.github/agents/*.agent.md`), or add a guided onboarding step.
- [ ] Add a "Claude Code setup" section to the onboarding skill explaining the platform split (Copilot `@agent` vs. Claude Code `/command`).
- [ ] Add a `paths.claude_commands` token so the path isn't hardcoded knowledge.

### Task Group 6: Planner-mode checkpoint enforcement (ITEM-007 / BUG-004)
Files: `agents/planner.body.md`, `skills/planner/*`

- [ ] Add an explicit planner-mode checkpoint: present a sprint draft and obtain approval before any repository edits on non-trivial tasks.
- [ ] Make the "no file writes without approval" rule load-bearing in the planner agent body, not just prose.

### Task Group 7: Purge demo / template content (ITEM-010)
Files: `SPRINTS.md`, `docs/planning/BACKLOG_LEDGER.md`, `docs/planning/BUG_BACKLOG.md`

- [ ] Remove demo ledger rows ITEM-001 through ITEM-005 (OAuth/auth/dashboard/rate-limiting template content).
- [ ] Remove demo bug entries BUG-001 and BUG-002 from `BUG_BACKLOG.md`.
- [ ] Remove the demo "Sprint 2 — Authentication Improvements" and "Sprint 1 — Initial Setup (template)" content from `SPRINTS.md`; reflect the real Sprint 1 (Onboarding Path Resolution) and this Sprint 2.
- [ ] Recompute ledger summary counts to match the purged table.
- [ ] Verify no remaining doc links point at the purged demo items.

## Files to Create/Modify

- `init.py` — deploy-copy step, missing-key fail-on-unresolved, `.claude/commands/` seeding (5)
- `config/project.config.yml` + profiles — missing `commands.*` / `security:` keys (1), `paths.claude_commands` token (5)
- `scripts/` + CI config — token-free guardrail (2), canonical-build-command check (3)
- `tests/test_init.py` — tests for 1, 2; `SOURCE_STYLE_REFS` derivation (4)
- `skills/onboarding/onboarding.skill.md` — Claude Code setup section (5)
- `agents/planner.body.md` + `skills/planner/*` — checkpoint enforcement (6)
- `SPRINTS.md`, `docs/planning/BACKLOG_LEDGER.md`, `docs/planning/BUG_BACKLOG.md` — demo purge (7)

## Quality Gates

- [x] standard — `python -m pytest tests/ -v` stays green (393+)
- [x] Determinism — re-run `init.py` twice, output identical
- [x] guardrail — new token-free `.github/**` check passes

## Success Criteria

- [ ] One build command yields token-free `.github/**`; CI fails on drift or missing keys.
- [ ] `.claude/commands/` seeded; onboarding doc covers the platform split.
- [ ] Planner agent body enforces draft-approval before edits.
- [ ] `SOURCE_STYLE_REFS` derived; CI build-command check live.
- [ ] Demo content purged; ledger summary counts recomputed.
- [ ] Full test suite green.

## Risks

- Task Group 1's fail-on-unresolved change could break the build for adopters with incomplete configs — needs a clear error message pointing at the missing key.
- Task Group 5 touches onboarding flow; verify `.claude/commands/` seeding is deterministic and doesn't collide with existing files.
- Task Group 7 is a one-way data decision (purge) — confirmed by user 2026-05-30. Verify no in-flight drafts reference the purged demo items before deletion.

## Pre-flight Findings

- NON_GOALS: no conflict (placeholders only).
- No TECHNICAL_DEBT / DECISIONS / FUTURE_CONSIDERATIONS files exist — no constraints to honor.
- Ledger: no item escalated (all Age ≤ 2, Def ≤ 1). ITEM-012 leads as highest severity (🟡 Degraded).
- ITEM-009 location verified at `tests/test_init.py` ~L894.
- Purge safety (Task Group 7): grepped in-flight drafts (`repo-rename`, `repo-structure-cleanup`, `command-centre-visual-v2`) for demo references (ITEM-001–005, BUG-001/002, OAuth/Safari/rate-limit/auth terms) — zero matches. No draft depends on purged demo content; purge is safe.

## Compliance Notes

- Determinism gate required (`init.py` is the deterministic build core).
- No store/migration/a11y gates apply — Python build-system + Markdown changes only.
- Task Group 7 (demo purge): user-approved one-way data change (approved by user 2026-05-30).

## Decisions (resolved at draft time)

- **Sprint number:** Sprint 2 (Sprint 1 = Onboarding Path Resolution, real).
- **ITEM-010:** Purge demo content entirely (not keep as scaffolding) — user decision 2026-05-30.
- **Scope:** All 7 task groups in a single sprint — user decision 2026-05-30.

<!-- Sprint Execution Guidelines + Commit Plan — left for @sprint-lead -->
<!-- Sprint Forecast — to be seeded by @planner at promotion -->
