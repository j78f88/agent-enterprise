# Sprint Lead — Phase Details

## Phase 1: Sprint Kickoff

1. Check `docs/planning/_handoffs/` for manifests addressed to `@sprint-lead`. If found, use the manifest's feature slug and sprint reference. If it contains `engagement: ENG-NNN`, store as the engagement reference (used for push target in Phase 5). Archive to `docs/planning/_handoffs/archive/`.
2. Read `SPRINTS.md` to identify the target sprint.
3. Read the sprint's `PLAN.md` from `sprints/`.
4. Read the **Quality Gates** section to determine which optional gates apply.
5. Load forecast: read `sprints/sprint-N/RETRO.md` if present. Store forecast data for Phase 6.
6. Validate every task group has a `Files:` annotation — flag missing ones.
7. Update `SPRINTS.md` status to "IN PROGRESS" with today's date.
8. Break down the plan into an ordered task list with dependencies using `#tool:todo`.
9. Commit: `docs: Sprint N — kick off`

**EXIT POINT (interactive):** Present task breakdown via `#tool:askQuestions`: "Which task should I start with?" with each task as a selectable option. In autopilot: start with first independent task.

---

## Resume Protocol (for `continue Sprint N`)

When the sprint is already in progress, reconstruct state:

1. Read `SPRINTS.md` — if "IN PROGRESS", skip Phase 1.
2. Read PLAN.md checkboxes to identify completed vs remaining tasks.
3. Read `sprints/sprint-N/RETRO.md` to reload forecast.
4. Parse `git log --grep='Sprint N' --oneline` for commit history.
5. Present reconstructed state via `#tool:askQuestions`.
6. On confirmation, resume Phase 2 from first unchecked task.

---

## Phase 2: Implementation (Subagent-per-Task)

For each task, run an unnamed subagent using `#tool:agent`. Use the Implementation Subagent Prompt Template from `.github/agents/sprint-lead/subagent-templates.md`.

### Processing Subagent Returns

1. Parse the return value.
2. Update `#tool:todo` — mark based on `status`.
3. Update PLAN.md checkbox for completed tasks.
4. Record commit hashes and summary for Sprint Report.

### Status Handling

- **`"done"`** — Record commits, move to next task.
- **`"blocked"`** — Interactive: EXIT POINT. Autopilot: log blocker, move to next independent task.
- **`"partial"`** — Log to Sprint Report notes. Move to next task. Appears in carry-over at Phase 6.

### What Sprint-Lead Does NOT Do in Phase 2

- Does not read source files in the main conversation.
- Does not edit code or run build commands in the main conversation.
- Does not run terminal commands other than `git` operations for PLAN.md updates.

---

## Phase 2.5: Safety-Net Verification

After all Phase 2 subagents complete, run in main conversation:

```bash
 && 
```

- Pass → proceed to Phase 3.
- Fail → diagnose which commit broke it, spawn fix subagent (using Fix template), repeat until clean.

---

## Phase 3: Quality Gates (Subagent Delegation)

### Standard Gates (always run)

1. Run **@qa** — full quality pipeline. Verify coverage thresholds.
2. Verify all PLAN.md tasks checked off.

### Optional Gates (per PLAN.md Quality Gates section)

- **a11y** — Run **@a11y** on changed pages/components.
- **perf** — Run **@perf** for bundle size, build time, dependencies.
- **security** — Run **@security** for CVE scan, secrets, OWASP, integrity hashes.
- **migrations** — Run unnamed subagent for store migration verification.

Unknown gate names: flag CRITICAL and halt.

### Handling Gate Results

- CRITICAL findings → spawn fix subagent, re-run failing gate.
- Record all gate results for Sprint Report.

---

## Phase 4: Code Review (Subagent Delegation)

Run **@reviewer** with `--commit-range {kickoff_commit_sha}..HEAD`.

- CRITICAL findings → fix subagents, then re-run @reviewer on fixed files.
- WARNING findings → record as tech debt for @docs.

---

## Phase 5: Documentation (Subagent Delegation)

1. Run **@docs** for full Documentation Sync Workflow for Sprint N.
2. Update memory files if needed (lightweight, main context).
3. Do not commit yet — Phase 6 commits.
4. Determine push target: engagement → `develop`; else → `main`.
5. Interactive: push and verify CI. Autopilot: do not push.

---

## Phase 6: Sprint Retrospective

1. Read prior RETRO.md files (N-1, N-2) for trend comparison.
2. Update Backlog Ledger: mark completed items done, increment Def for carried-over items, add new items from sprint output.
3. Assemble full RETRO.md per `retro-report.instructions.md`.
4. Spawn subagent to write RETRO.md.
5. Display in chat.
6. Commit: `docs: Sprint N — complete`

**EXIT POINT (interactive):** "Push and verify CI" (recommended), "Kick off next sprint", "Done for now".

Autopilot: present Sprint Report and stop with push instructions.
