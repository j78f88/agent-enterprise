---
id: instruction.contract-change-checklist
kind: instruction
version: 1.0.0
applies_to: '**'
description: contract-change-checklist instruction
applyTo: .github/agents/**,.github/instructions/**,.github/prompts/**,docs/templates/**
---

# Contract-Change Checklist

When editing any agent, instruction, prompt, or template file, review this checklist **before committing**. Each item prevents a class of silent-break bugs discovered in dry-run testing.

## Checklist

- [ ] **Gate names match consumers.** If you added/renamed a quality gate (e.g., `migrations`, `a11y`), verify `sprint-lead.agent.md` Phase 3 handles it. Unknown gates cause a silent skip.
- [ ] **Handoff prompts still valid.** If you changed an agent's role boundary, update the YAML `initialPrompts` handoff buttons on the agents that hand off TO it. Verify the button text references `docs/planning/_handoffs/` if the receiving agent supports manifests.
- [ ] **Subagent invocation updated.** If you changed a specialist agent's expected input (e.g., `@reviewer` now needs `--commit-range`), update the calling agent's invocation (usually `sprint-lead.agent.md` Phase 4).
- [ ] **Template sections don't overlap agent phases.** If you added content to `SPRINT_PLAN_TEMPLATE.md`, ensure it doesn't duplicate `@sprint-lead` Phase 1–6 responsibilities. Execution guidelines belong in the agent, not the plan.
- [ ] **Instruction `applyTo` patterns tested.** If you created or changed an `applyTo` glob, verify it matches the intended files (test with `file_search` or glob expansion).
- [ ] **Schema changes propagated.** If you changed a return schema (e.g., subagent JSON return), update all consumers that parse that schema.
- [ ] **Severity levels consistent.** If you referenced severity levels (CRITICAL / WARNING / SUGGESTION), verify they match the definitions in `severity-levels.instructions.md`.
