# diy-project-helper Onboarding Playbook

Onboarding `D:\VS\DIY project\diy-project-helper` (original "DIY Project Helper" / pre-Verk-rebrand) to agent-homebase via Mode 3.

## Context

This is the predecessor to Verk Web — same project, older naming. Decision needed early: is this still actively maintained, or archive-only?

**Decision gate:** Before onboarding, confirm with operator:
- [ ] Active development continues here? (If no → skip onboarding, archive instead)
- [ ] Or is Verk Web the canonical successor? (If yes → consider archiving this and deleting registry entry)

If operator confirms continued activity, proceed.

## Pre-conditions

- [ ] Phase 3 complete: choreography workspace + sync CLI exist
- [ ] Phase 4 complete (if Verk Web patterns also apply here)
- [ ] Operator confirmation that this project is active

## Profile

If single-package React app (not monorepo): use `react-web-app` profile.
If monorepo (similar to Verk Web): use `monorepo-fullstack`.

Create `D:\VS\DIY project\diy-project-helper\.agent-config\profile.yml` based on actual project structure (verify before generating).

## Registry Entry

```bash
python -m sync register diy-project-helper \
  --path "D:\VS\DIY project\diy-project-helper" \
  --profile react-web-app \
  --mode team
```

Notes in registry:
```yaml
projects:
  diy-project-helper:
    notes: "Predecessor to Verk Web. Confirm active before maintaining."
    tags: [legacy, verk]
```

## Deploy + Validate

Same flow as [verk-web.md](verk-web.md):
1. `sync diff diy-project-helper`
2. `sync deploy diy-project-helper`
3. Run existing test suite
4. Smoke-test agents

## Risks

| Risk | Mitigation |
|------|-----------|
| Project is dormant; deploying just adds noise | Confirm active status first |
| Patterns harvested from Verk Web don't fit older codebase | Treat as separate harvest target if needed |
| Confusion between this and Verk Web | Clear naming + tags in registry |
