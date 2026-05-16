# Verk Web Onboarding Playbook

Onboarding [Verk Web](D:\VS\Verk%20Web) to agent-homebase via Mode 3.

## Pre-conditions

- [ ] Phase 3 complete: choreography workspace + sync CLI exist
- [ ] Phase 4 complete: Verk Web's mature patterns harvested and back-ported into substrate
- [ ] Verk Web test suite green (708 unit + 273 E2E) before onboarding starts (baseline)
- [ ] Operator approval to replace Verk Web's hand-rolled agents with homebase-resolved ones

## Profile Generation

Verk Web is a TypeScript monorepo (Turborepo + pnpm + React 19 + Vite). Use `monorepo-fullstack` profile as base.

Create `D:\VS\Verk Web\.agent-config\profile.yml`:

```yaml
profile_base: monorepo-fullstack

editor:
  target: vscode

project:
  name: Verk Web
  language: typescript
  framework: react
  namespace: verk

team:
  cto_name: Joshua Pope

git:
  repo: <github-url>
  default_branch: main

paths:
  planning: docs/planning
  architecture: docs/architecture
  sprints: sprints
  backlog_ledger: docs/planning/BACKLOG_LEDGER.md
  bug_backlog: docs/planning/BUG_BACKLOG.md
  handoff_rejections: docs/planning/HANDOFF_REJECTIONS.md
  non_goals: docs/NON_GOALS.md
  sprints_root: SPRINTS.md
  feature_matrix: docs/FEATURE_MATRIX.md          # Verk-specific

quality:
  store_coverage_pct: 80
  web_coverage_pct: 60
  bundle_kb_max: <verk-current-budget>
  lighthouse_perf_min: 90
  lighthouse_a11y_min: 95
  wcag_level: AA

commands:
  test: pnpm test
  test_coverage: pnpm test:coverage
  lint: pnpm lint
  build: pnpm build
  e2e: pnpm e2e
  typecheck: pnpm typecheck

platform:
  hosting: azure-static-web-apps
  monitoring: application-insights

escalation:
  def_p0_threshold: 3
  def_kill_threshold: 5
  e2e_concurrent_max: 5
```

## Registry Entry

```bash
cd <command-centre-workspace>
python -m sync register verk-web \
  --path "D:\VS\Verk Web" \
  --profile monorepo-fullstack \
  --mode team
```

After registration, hand-edit `registry.yml` to add Verk Web's project-locals:

```yaml
projects:
  verk-web:
    custom_instructions:
      - .github/instructions/template-validation.md
      - .github/instructions/release-governance.md
    custom_agents:
      - .github/agents/template-auditor/SKILL.md
      - .github/agents/delivery-lead/SKILL.md      # Until/unless promoted to substrate in Phase 4
    tags: [production, verk]
    notes: "Sprint 90+. Audited and back-ported in Phase 4. Project-local agents preserved."
```

## Pre-deploy Audit

Run dry-run to see what changes:

```bash
python -m sync diff verk-web
```

**Critical checks before proceeding:**
- [ ] No project-local files (Verk-specific agents/instructions) appear in deletion list
- [ ] Diff size is reasonable (no surprise mass-rewrite)
- [ ] Substrate-resolved agents conceptually match Verk Web's current ones (post-harvest, they should)

If anything looks wrong, STOP and re-audit Phase 4 back-ports.

## Deploy

```bash
python -m sync deploy verk-web
```

## Post-deploy Validation

1. **Test suite must pass unchanged:**
   ```bash
   cd D:\VS\Verk Web
   pnpm install
   pnpm test          # Expect 708 passing
   pnpm e2e           # Expect 273 passing
   ```

2. **Agent behavior smoke test:**
   - Invoke `@qa` on a known sprint; confirm it produces equivalent output to pre-onboarding
   - Invoke `@reviewer` on a recent PR; confirm findings are equivalent
   - Invoke `@planner` and confirm it reads `BACKLOG_LEDGER.md` correctly

3. **File integrity:**
   - Confirm `.github/agents/.homebase-mode` shows `mode: team` and current homebase SHA
   - Confirm Verk-specific files (`@template-auditor`, `@delivery-lead`) still exist
   - Confirm planning files (`SPRINTS.md`, `BACKLOG_LEDGER.md`) untouched

## Rollback

If validation fails:

1. `git -C "D:\VS\Verk Web" status` — confirm changes are tracked
2. `git -C "D:\VS\Verk Web" checkout -- .github/` — revert all agent + instruction changes
3. Update registry: `deployed_hash: null` (manually)
4. Open issue against homebase substrate; do NOT retry deploy until root cause fixed

## Risks

| Risk | Mitigation |
|------|-----------|
| Substrate agents subtly differ from Verk Web's; agent behavior changes | Phase 4 harvest must be thorough; smoke tests required |
| Verk-specific instructions overridden by substrate | Custom-instructions list in registry; dry-run audit |
| Test suite regression caused by .github/ changes | Tests should not depend on .github/; if they do, fix tests not skip onboarding |
