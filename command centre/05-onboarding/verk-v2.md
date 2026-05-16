# verk-v2 Onboarding Playbook

Onboarding [verk-v2](D:\VS\verk-v2) to agent-homebase via Mode 3.

## Context

verk-v2 is **already wired** for the three-repo composition model:
- Has `.agent-config/profile.yml` with all token definitions
- Has 5 project-specific instructions in `instructions/`
- Has `CLAUDE.md` configured for agent dispatch
- Designed from day one to consume agent-homebase

This makes verk-v2 the **simplest onboarding target** and a good first project to register.

## Pre-conditions

- [ ] Phase 3 complete: choreography workspace + sync CLI exist
- [ ] Operator confirms verk-v2 is the right first onboarding (low risk: skeleton, no production code yet)

Phase 4 (harvest from Verk Web) is **not required** before onboarding verk-v2 — but improvements from Phase 4 will flow into verk-v2 on subsequent deploys.

## Profile

Already exists at `D:\VS\verk-v2\.agent-config\profile.yml`. Spot-check fields against current `monorepo-fullstack` profile schema; update any drift.

## Registry Entry

verk-v2 uses Linear for tracker integration. Register as Mode 2 (orchestration):

```bash
python -m sync register verk-v2 \
  --path D:\VS\verk-v2 \
  --profile D:\VS\verk-v2\.agent-config\profile.yml \
  --mode orchestration \
  --tracker linear \
  --workspace verkv2
```

Update registry with notes:
```yaml
projects:
  verk-v2:
    custom_instructions:
      - instructions/commercial-validation.md
      - instructions/spec-pipeline.md
      - instructions/voice-budget.md
      - instructions/rls-policy.md
      - instructions/payment-state.md
    tags: [active-development, verk, first-onboarding]
    notes: "Reference implementation for Mode 3. Skeleton; no app code yet."
```

## Deploy + Validate

```bash
python -m sync diff verk-v2
python -m sync deploy verk-v2
```

Validation:
1. `.github/agents/` populated with 13 substrate agents + `@dispatcher` + `@verifier` (Mode 2 includes these)
2. `.github/instructions/` populated with substrate + dispatch instructions
3. Project-local instructions (`instructions/commercial-validation.md`, etc.) untouched
4. `.homebase-mode` shows `mode: orchestration`, current homebase SHA
5. Hooks present (`hooks/afterCreate.sh`, `hooks/onComplete.sh`) — verify they reference homebase paths, not the old `agent-orchestration` repo

## Smoke Test (Orchestration)

Since verk-v2 has no app code, the smoke test focuses on the dispatch loop:

1. Create a test issue in Linear workspace `verkv2`: "TEST: write a haiku about woodworking to a file"
2. Move issue to Active state
3. Confirm `@dispatcher` picks it up (manual or via hatice)
4. Confirm classification is sensible
5. Confirm `@verifier` checks for the artifact
6. Resolve test issue

If end-to-end works, Mode 3 + Mode 2 are validated together.

## Why verk-v2 First?

- **Lowest risk:** no production code, no users
- **Reference implementation:** profile.yml is already correctly structured
- **Validates Mode 2 + Mode 3 together:** orchestration deployment via choreography
- **Validates the absorption:** confirms `delivery-modes/orchestration/` works end-to-end

## Rollback

Trivial since project is a skeleton:
1. `git -C D:\VS\verk-v2 checkout -- .github/` (if files were under git)
2. Or `Remove-Item -Recurse D:\VS\verk-v2\.github\agents` and re-clone state
3. Update registry: `deployed_hash: null`
