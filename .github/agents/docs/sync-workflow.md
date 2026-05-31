# Documentation Sync Workflow

Run this COMPLETE workflow every time you are asked to sync/update docs. Check each file; if it needs no changes, confirm it is current and move on.

## Step 1: Gather Context

- Read `SPRINTS.md` to identify recently completed sprints and their scope.
- Read the completed sprint's `PLAN.md` for task details and components.
- Run `git log --oneline -10` for recent commit messages.

## Step 2: Sprint & Status Docs

1. **`SPRINTS.md`** — Statuses correct? Commit hashes present? Archive table current? Phase boundary per `sprint-docs-format.instructions.md`.
2. **`.github/copilot-instructions.md`** — Current sprint pointer matches? Instruction file listing matches actual files on disk?
3. **`docs/planning/ROADMAP.md`** — Phase statuses match? No stale "IN PROGRESS"?
4. **`docs/planning/FEATURE_MATRIX.md`** — Update per `sprint-docs-format.instructions.md`.
5. **`docs/planning/BUG_BACKLOG.md`** — Update per `bug-backlog-format.instructions.md`.

## Step 3: User-Facing Docs

6. **`docs/USER_GUIDE.md`** — Check:
   - New features have dedicated sections with step-by-step instructions.
   - Table of Contents matches actual `##` headings.
   - "What's Coming Next" reflects current sprint/roadmap.
   - "Last Updated" footer is current.
   - **Coverage cross-check:** For every user-facing row in `docs/planning/FEATURE_MATRIX.md`, verify a corresponding section exists.
   - **Stale reference sweep:** Fix `Sprint \d+` with forward-looking language if that sprint completed; verify hardcoded version strings match `pyproject.toml`.

7. **`docs/RELEASES.md`** — Release notes for all recently completed sprints present?
8. **`docs/changelog.json`** — New entry prepended? Copied to `docs/changelog.json`? Schema matches `ChangelogEntry`?
9. **`pyproject.toml`** — `version` field matches the latest changelog entry?

## Step 4: Developer Docs

10. **`docs/TECHNICAL_DEBT.md`** — New resolved items added? New tech debt logged? Test counts current?
11. **`docs/ARCHITECTURE.md`** — New patterns or stores documented?
12. **`docs/decisions/DECISIONS.md`** — ADRs for sprint architectural decisions present?
13. **`docs/TESTING.md`** — Relative links resolve? Test commands still work?

## Step 5: README

14. **`README.md`** — Feature list current? Structure diagram matches actual directories? All internal links valid?

## Step 6: Link Validation

15. For every `[text](path)` link in files you touched, verify the target exists. Fix or remove broken links.

## Step 7: Commit

Commit per `.github/instructions/commit-conventions.instructions.md` (e.g., `docs: sync documentation for Sprint N completion`).
