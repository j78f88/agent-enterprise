---
id: instruction.sprint-docs-format
kind: instruction
version: 1.0.0
applies_to: '**'
description: sprint-docs-format instruction
applyTo: '**'
---

# Sprint Documentation Format

Schema and rules for sprint-adjacent files: `{{paths.sprints_doc}}`, `PLAN.md`, `{{paths.feature_matrix}}`, and phase archives.

## SPRINTS.md Archiving

- Archive Sprint N-2 when Sprint N completes.
- **Phase boundary rule:** If Sprint N is the last in a phase, create or update `docs/archive/SPRINTS_PHASE_X.md` and update the Archive table — every completed phase must have a `[View]` link, never `—`.
- **Archive writer:** `@docs` is the sole writer. `@sprint-lead` Phase 5 **invokes** `@docs` rather than writing archives directly.

## PLAN.md Directory Archiving

When Sprint N completes, move the Sprint N-2 plan directory to the archive:

```powershell
Move-Item -Path "sprints/sprint-(N-2)" -Destination "docs/archive/sprint-plans/sprint-(N-2)" -Force
```

- **Source:** `{{paths.sprints}}sprint-(N-2)/` (contains PLAN.md and any companion files)
- **Destination:** `docs/archive/sprint-plans/sprint-(N-2)/`
- **Update links:** If any archive docs (`SPRINTS_PHASE_*.md`, `SPRINTS_STANDALONE.md`) link to the moved sprint, rewrite `../../{{paths.sprints}}sprint-(N-2)/PLAN.md` → `sprint-plans/sprint-(N-2)/PLAN.md`.
- Active sprint plans (current and next) always remain in `{{paths.sprints}}`.

## RETRO.md Lifecycle

- **Seeded at promotion:** `@planner` writes `{{paths.sprints}}sprint-N/RETRO.md` with the forecast and placeholder sections (via `/promote-draft`).
- **Loaded at kickoff:** `@sprint-lead` Phase 1 reads the seeded RETRO.md to capture the forecast.
- **Finalized at completion:** `@sprint-lead` Phase 6 assembles the full RETRO.md from forecast + actuals + prior trends.
- **Committed:** Included in the `docs: Sprint N — complete` commit.
- **Archived at N-2:** Moves with the sprint directory to `docs/archive/sprint-plans/sprint-N/`.
- **Full format reference:** `{{paths.instructions_dir}}/retro-report.instructions.md`

## PLAN.md Per-Task File Annotations

Every task group in `## Technical Tasks` **must** include a `Files:` line listing the files that task touches. This is load-bearing for subagent delegation — sprint-lead passes these paths to implementation subagents so they can self-orient without reading the entire codebase.

```markdown
### Task Group 1: Feature Name

Files: `path/to/file.ts`, `path/to/other.tsx`

- [ ] Task 1
- [ ] Task 2
```

- @planner populates `Files:` when writing PLAN.md (derive from global `Files to Create/Modify` section + task description).
- Sprint-lead validates per-task `Files:` annotations exist at kickoff; flags missing ones as a blocker.
- If a task discovers it needs additional files not listed, the subagent may access them but **must** note them in its return.

## PLAN.md Quality Gates Section

```markdown
## Quality Gates

- [x] standard (typecheck, lint, test, coverage, e2e)
- [x] a11y (accessibility audit)
- [ ] perf (bundle size, dependencies)
- [ ] migrations (store schema migration verification)
```

- `standard` is always checked.
- `a11y` is recommended-default when the sprint touches `{{paths.web_app_dir}}/src/components/**`.
- `migrations` is recommended-default when the sprint adds or modifies persisted store fields in `packages/store/src/`.
- Unknown gate names are flagged CRITICAL by `@sprint-lead` Phase 3.

### Migrations Gate Verification

When `migrations` is checked:

1. Verify `version` was bumped in every modified store factory.
2. Verify `migrate()` function handles upgrade from `version - 1` to `version`.
3. Run store test suite: `{{commands.test}}` — all migration tests must pass.
4. Spot-check: seed a store at the previous version and verify `migrate()` produces the correct current-version shape without data loss.

## FEATURE_MATRIX.md Update Rule

- "Last Updated" date at top must be set to today's date on every update.
- Parity percentages must be recomputed, not estimated.
- **Test counts:** Copy unit test count and E2E test count from the latest completed sprint's Quality Results in `{{paths.sprints_doc}}` (the `@qa` report numbers). Update the "Quality & Testing" table rows to match. Also update the footer "Last Updated" + "Tracked By" line to reflect the current sprint.
- **Feature completeness:** If a sprint ships a new user-facing feature, verify it has a row in docs/planning/FEATURE_MATRIX.md. Missing rows are added during the same docs sync.

## changelog.json & Version Bump Rule

When a sprint ships user-facing features, bug fixes, or improvements:

1. **Prepend** a new `ChangelogEntry` to `{{paths.changelog}}` with the next incremented version, today's date, and a user-friendly title + highlights.
2. **Copy** the updated file to `{{paths.changelog_deploy_copy}}` (the web app fetches from `public/`).
3. **Bump** the `version` field in `{{paths.package_json}}` to match the new entry. This version drives the `UpdateNotification` banner — a mismatch causes the notification to either never show or show on every reload.
4. **Verify** JSON validity: `Get-Content {{paths.changelog}} -Raw | ConvertFrom-Json` must succeed.

Sprints with no user-facing changes (documentation-only, audit-only) do not require a changelog entry or version bump.

## NON_GOALS.md Approval Marker

See `{{paths.instructions_dir}}/non-goals-governance.instructions.md` for the full protocol.

## Review File Archival

Point-in-time review files (`docs/planning/REVIEW_*.md` and `.html`) should be moved to `{{paths.archive}}` after all action items from the review have been executed. Keep only the current/active review in `docs/planning/`.

## Sprint Output Artifacts

When a sprint plan specifies non-code output files (reports, roadmaps, audits):

- **During planning:** `@planner` may use `{{paths.drafts}}` as the initial output location in the plan — this is correct for the planning phase.
- **At sprint completion:** `@sprint-lead` (via `@docs`) must move these artifacts from `{{paths.drafts}}` to their permanent location:
  - Architecture reports/audits → `docs/architecture/`
  - Development guides/strategies → `docs/development/`
  - Research outputs → `docs/research/`
- **Cleanup verification:** `/plan-cleanup` flags any non-plan files remaining in `{{paths.drafts}}` after their source sprint completes.

## Ledger Updates

At sprint completion, `@sprint-lead` updates the Backlog Ledger (`{{paths.backlog_ledger}}`) at **Phase 6 step 2** — before the `docs: Sprint N — complete` commit.

### Required Operations

1. **Done:** Set Status → `done` for all ledger items completed in this sprint.
2. **Defer:** Increment `Def` by 1 for all items that were `assigned` to this sprint but not completed.
3. **Carry-overs:** Append new ITEM entries (Type: `carry-over`) for any unplanned follow-ups discovered during the sprint.
4. **Scan output artifacts:** Check RETRO.md §9 and any sprint output files for follow-up actions; dedup-check against existing ledger entries before appending.
5. **Update summary counts:** Recalculate the summary section to match actual table contents.

### Timing

Ledger updates happen **after** all task commits and **before** the `docs: Sprint N — complete` commit. The ledger changes are included in that final commit.
