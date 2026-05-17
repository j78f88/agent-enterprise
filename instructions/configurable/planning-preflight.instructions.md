---
id: instruction.planning-preflight
kind: instruction
version: 1.0.0
applies_to: '**'
description: Use when running pre-flight checks on planning documents, scanning project docs before drafting sprint plans, or reviewing architecture constraints for feature planning.
applyTo: '{{paths.drafts}}**'
---

# Planning Pre-flight Checklists

Two scopes — use the one matching your current workflow.

## Full Pre-flight (Ideation / Feature Planning)

Read each document and note findings. **Do not** skip any row.

| Document                                     | Look for                                          |
| -------------------------------------------- | ------------------------------------------------- |
| `{{paths.technical_debt}}`         | Resolvable debt, constraining debt                |
| `{{paths.decisions}}`             | Applicable ADRs, need for new ADR                 |
| `{{paths.future_considerations}}` | Strategic notes                                   |
| `{{paths.sprints_doc}}` + `{{paths.roadmap}}`    | Phase alignment, dependencies                     |
| `{{paths.feature_matrix}}`            | Web/mobile parity                                 |
| `{{paths.copilot_instructions}}`            | Architecture rules                                |
| `{{paths.non_goals}}`                          | Conflicts — **flag, do not silently work around** |

## Focused Pre-flight (Bug Fixes)

| Item                                   | Look for                           |
| -------------------------------------- | ---------------------------------- |
| `{{paths.technical_debt}}`   | Is this a symptom of tracked debt? |
| `{{paths.copilot_instructions}}`      | Architecture constraints           |
| Test coverage search for affected area | Existing tests, gaps               |
