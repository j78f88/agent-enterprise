# Documentation Sync Workflow

Run this COMPLETE workflow every time you are asked to sync/update docs. Check each file; if it needs no changes, confirm it is current and move on.

## Step 1: Gather Context

- Read `{{paths.sprints_doc}}` to identify recently completed sprints and their scope.
- Read the completed sprint's `PLAN.md` for task details and components.
- Run `git log --oneline -10` for recent commit messages.

## Step 2: Sprint & Status Docs

1. **`{{paths.sprints_doc}}`** — Statuses correct? Commit hashes present? Archive table current? Phase boundary per `sprint-docs-format.instructions.md`.
2. **`{{paths.copilot_instructions}}`** — Current sprint pointer matches? Instruction file listing matches actual files on disk?
3. **`{{paths.roadmap}}`** — Phase statuses match? No stale "IN PROGRESS"?
4. **`{{paths.feature_matrix}}`** — Update per `sprint-docs-format.instructions.md`.
5. **`{{paths.bug_backlog}}`** — Update per `bug-backlog-format.instructions.md`.

## Step 3: User-Facing Docs

6. **`{{paths.user_guide}}`** — Check:
   - New features have dedicated sections with step-by-step instructions.
   - Table of Contents matches actual `##` headings.
   - "What's Coming Next" reflects current sprint/roadmap.
   - "Last Updated" footer is current.
   - **Coverage cross-check:** For every user-facing row in `{{paths.feature_matrix}}`, verify a corresponding section exists.
   - **Stale reference sweep:** Fix `Sprint \d+` with forward-looking language if that sprint completed; verify hardcoded version strings match `{{paths.package_json}}`.

7. **`{{paths.releases}}`** — Release notes for all recently completed sprints present?
8. **`{{paths.changelog}}`** — New entry prepended? Copied to `{{paths.changelog_deploy_copy}}`? Schema matches `ChangelogEntry`?
9. **`{{paths.package_json}}`** — `version` field matches the latest changelog entry?

## Step 4: Developer Docs

10. **`{{paths.technical_debt}}`** — New resolved items added? New tech debt logged? Test counts current?
11. **`{{paths.architecture_doc}}`** — New patterns or stores documented?
12. **`{{paths.decisions}}`** — ADRs for sprint architectural decisions present?
13. **`{{paths.testing_doc}}`** — Relative links resolve? Test commands still work?

## Step 5: README

14. **`README.md`** — Feature list current? Structure diagram matches actual directories? All internal links valid?

## Step 6: Link Validation

15. For every `[text](path)` link in files you touched, verify the target exists. Fix or remove broken links.

## Step 7: Commit

Commit per `{{paths.instructions_dir}}/commit-conventions.instructions.md` (e.g., `docs: sync documentation for Sprint N completion`).
