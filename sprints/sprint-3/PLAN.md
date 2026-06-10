# Sprint 3 — Claims Foundation: ADR, Debt, and Roadmap Seeding

**Status:** Active
**Type:** Mixed (feature-enabling / debt / hygiene)
**Sources:** session review 2026-06-10 (user-approved "close the gap upward" roadmap) · **Ledger:** ITEM-013, ITEM-014, ITEM-015, ITEM-016, ITEM-017, ITEM-018, ITEM-019, ITEM-020
**Dependencies:** None (Sprint 2 build hardening is the foundation this builds on)

## Goals

- The repo's own architecture record permits productionizing Modes 2/3: ADR
  0008 defines the "supported implementation" promotion contract and revises
  the `command-centre/PLAN.md` non-goal.
- The last open ledger item (ITEM-013, deprecated `jsonschema.RefResolver`)
  is closed before any Mode 3 production code is born on a deprecated API.
- `docs/planning/drafts/` contains only not-yet-done work; completed drafts
  are archived per the SPRINTS.md archive rule.
- CI builds every shipped profile, not just the example config, proving all
  profiles resolve token-free.
- README platform claims are honest in the interim: the OpenAI Codex "Ready"
  cell carries a footnote until the platform-parity sprint delivers it.
- The four roadmap themes are staged: one draft plan each in `docs/planning/drafts/` and
  ledger ITEMs, ready for promotion sprint-by-sprint.

## Why This Sprint

The 2026-06-10 review found the README's headline claims (3 delivery modes,
4 platforms Ready) outrun the implementation: Modes 2/3 are reference impls
only, and `init.py` gates agent generation to VS Code targets. The user chose
to close the gap upward — make the claims true. Nothing downstream can start
cleanly until (a) the PLAN.md non-goal that forbids owning a dispatcher is
revised by ADR, (b) the deprecated-API debt that Mode 3 code would inherit is
paid, and (c) the planning surface (drafts, ledger, CI matrix) is trustworthy.
All six task groups are low blast radius and unblock the four staged roadmap drafts.

## Technical Tasks

Execution order: **1 → 6** are sequenced only where noted; **2, 3, 4, 5** are
independent and can run in parallel after 1.

### Task Group 1: ADR 0008 — supported mode implementations (ITEM-014)
Files: `command-centre/decisions/0008-supported-mode-implementations.md`, `command-centre/PLAN.md`

- [ ] Write ADR 0008 (format of `0004-mode-2-contract-not-absorption.md`):
      revise the "Owning a specific Mode 2 dispatcher implementation"
      non-goal; define the 5-point supported-implementation contract
      (lives in `src/` with root CLI; contract checklist proven by pytest in
      CI on both OSes; crash-safety/idempotency beyond the reference impl;
      adopter doc in `docs/` + named in the mode's `install-contract.md`;
      reference impl stays frozen byte-unchanged).
- [ ] Update `command-centre/PLAN.md` Non-goals to reference ADR 0008.
- [ ] No contract/schema changes — `protocol-v1`, `mode-2-contract-v1`,
      `mode-3-contract-v1` remain frozen.

### Task Group 2: ITEM-013 — migrate RefResolver to `referencing`
Files: `command-centre/04-mode-choreography/reference-impls/registry-coordinator/coordinator.py`, `tests/test_protocol_v1_conformance.py`, `requirements.txt`

- [ ] Replace `jsonschema.RefResolver` usage (coordinator.py ~L42–53) with
      the `referencing` registry API.
- [ ] Migrate the same pattern in `tests/test_protocol_v1_conformance.py`
      (~L151–160).
- [ ] Add `referencing` to `requirements.txt`.
- [ ] Full suite green with zero jsonschema deprecation warnings.

### Task Group 3: Stale drafts cleanup (ITEM-015)
Files: `docs/planning/drafts/*`, `docs/archive/` (new), `docs/planning/BACKLOG_LEDGER.md`

- [ ] Create `docs/archive/`; move completed drafts there:
      `sprint-2-build-hardening-draft-plan.md` (Sprint 2 done),
      `onboarding-path-resolution-remediation-draft-plan.md` (Sprint 1 done),
      `repo-rename-agent-enterprise-draft-plan.md` (rename done 2026-05-29).
- [ ] `e1-fix-reconciliation-handoff.md` is a handoff, not a draft — relocate
      alongside `HANDOFF_REJECTIONS.md` context in `docs/planning/` (or a
      `_handoffs/` subdir) and leave a pointer.
- [ ] Triage `repo-structure-cleanup.md` and `command-centre-visual-v2-plan.md`:
      convert still-pending work to ledger ITEMs or archive if done.
- [ ] Grep check: no doc links break (ledger Draft column updated).

### Task Group 4: CI profile build matrix (ITEM-016)
Files: `.github/workflows/ci.yml`

- [ ] Build all three `profiles/*.config.yml` in CI in addition to
      `config/project.config.example.yml` (loop or matrix); rely on the
      existing fail-on-unresolved guardrail.
- [ ] Keep the canonical-build-command doc check (ITEM-011) intact — profiles
      are additional builds, not a new canonical command.

### Task Group 5: Interim README honesty footnote
Files: `README.md`

- [ ] Add a footnote to the OpenAI Codex "✅ Ready" cell (README ~L321):
      Codex consumes the deployed Markdown + AGENTS.md convention today;
      native target emission lands with the platform-parity draft.
- [ ] No badge changes; the Works Everywhere table stays.

### Task Group 6: Seed the four roadmap draft plans + ledger (ITEM-017..020)
Files: `docs/planning/drafts/platform-parity-draft-plan.md`, `docs/planning/drafts/mode2-dispatcher-promotion-draft-plan.md`, `docs/planning/drafts/mode3-coordinator-promotion-draft-plan.md`, `docs/planning/drafts/adopter-bootstrap-draft-plan.md`, `docs/planning/BACKLOG_LEDGER.md`

- [ ] Author the four roadmap draft plans (same template as this one), each
      scoped to 5–8 task groups, with Files:, gates, risks.
- [ ] Ledger rows ITEM-017 (platform parity), ITEM-018 (Mode 2 promotion),
      ITEM-019 (Mode 3 promotion), ITEM-020 (adopter bootstrap) point at
      their drafts.
- [ ] No sprint numbers assigned to future work (slug references only).

## Files to Create/Modify

- `command-centre/decisions/0008-supported-mode-implementations.md` (new) + `command-centre/PLAN.md` (TG1)
- `registry-coordinator/coordinator.py`, `tests/test_protocol_v1_conformance.py`, `requirements.txt` (TG2)
- `docs/archive/` (new) + `docs/planning/drafts/*` moves + ledger Draft column (TG3)
- `.github/workflows/ci.yml` (TG4)
- `README.md` footnote (TG5)
- 4 new draft plans + `docs/planning/BACKLOG_LEDGER.md` rows (TG6)

## Quality Gates

- [ ] standard — `python -m pytest tests/ -v` stays green (401+), zero new warnings
- [ ] Determinism — re-run `init.py` twice, output identical
- [ ] guardrail — token-free `.github/**` check passes
- [ ] docs — voice/heading tests green for the ADR and new drafts

## Success Criteria

- [ ] ADR 0008 accepted; PLAN.md non-goal revised; no frozen contract touched.
- [ ] ITEM-013 closed; suite green with zero jsonschema deprecation warnings.
- [ ] `docs/planning/drafts/` contains only pending work; archive rule applied.
- [ ] CI builds 4 configs (example + 3 profiles) token-free.
- [ ] README Codex cell footnoted.
- [ ] Four roadmap drafts staged + ledger ITEMs.

## Risks

- ADR 0008 revises a recorded non-goal — mitigation: the ADR documents the
  rationale (user-approved roadmap, claims/implementation gap) and keeps
  reference impls frozen so the original concern (runtime lock-in) holds.
- `referencing` migration could change validation behaviour — mitigation:
  conformance tests pin the checklist before/after; zero-warning assertion.
- Draft moves can break links — mitigation: repo-wide grep for each moved
  filename before commit.
- CI matrix lengthens build time — mitigation: profiles build in one job
  loop; each build is seconds.

## Pre-flight Findings

- `command-centre/decisions/` ends at 0007 — 0008 is the next number.
- ITEM-013 is the only open ledger row; no P0 carry-over (Def ≥ 3) exists.
- No NON_GOALS.md conflict: the non-goal lives in `command-centre/PLAN.md`,
  which is governed by ADRs, not the NON_GOALS registry.
- `docs/archive/` does not exist yet; SPRINTS.md footer's archive rule names
  it as the destination — TG3 creates it.

## Compliance Notes

- Protocol-v1 and both mode contracts remain frozen; this sprint changes no
  schema or contract text.
- Planner contract: this draft was authored under [SUBAGENT-MODE]
  [WRITE:DRAFT-PLAN]; the roadmap it stages was user-approved 2026-06-10.

## Sprint Execution Guidelines

_(left for @sprint-lead)_

## Commit Plan

_(left for @sprint-lead)_
