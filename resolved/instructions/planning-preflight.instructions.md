---
description: "Use when running pre-flight checks on planning documents, scanning project docs before drafting sprint plans, or reviewing architecture constraints for feature planning."
applyTo: "docs/planning/drafts/**"
---

# Planning Pre-flight Checklists

Two scopes — use the one matching your current workflow.

## Full Pre-flight (Ideation / Feature Planning)

Read each document and note findings. Do NOT skip any row.

| Document                                     | Look for                                          |
| -------------------------------------------- | ------------------------------------------------- |
| `docs/development/TECHNICAL_DEBT.md`         | Resolvable debt, constraining debt                |
| `docs/architecture/DECISIONS.md`             | Applicable ADRs, need for new ADR                 |
| `docs/architecture/FUTURE_CONSIDERATIONS.md` | Strategic notes                                   |
| `SPRINTS.md` + `docs/planning/ROADMAP.md`    | Phase alignment, dependencies                     |
| `docs/planning/FEATURE_MATRIX.md`            | Web/mobile parity                                 |
| `.github/copilot-instructions.md`            | Architecture rules                                |
| `docs/NON_GOALS.md`                          | Conflicts — **flag, do not silently work around** |

## Focused Pre-flight (Bug Fixes)

| Item                                   | Look for                           |
| -------------------------------------- | ---------------------------------- |
| `docs/development/TECHNICAL_DEBT.md`   | Is this a symptom of tracked debt? |
| `.github/copilot-instructions.md`      | Architecture constraints           |
| Test coverage search for affected area | Existing tests, gaps               |
