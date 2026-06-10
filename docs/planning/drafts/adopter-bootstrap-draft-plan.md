# Adopter Bootstrap — One-Line Setup into External Projects

**Status:** DRAFT
**Type:** Feature (adopter experience / build-system)
**Sources:** session review 2026-06-10 (user-approved "close the gap upward" roadmap) · **Ledger:** ITEM-020
**Dependencies:** Sprint 2 (deploy + token-free guardrail) and Sprint 3 (CI profile matrix); platform work referenced by slug `platform-parity-draft-plan.md` (bootstrap should deploy whichever `editor.target` artifacts exist when it lands)

## Goals

- `init.py --target <path>` deploys the resolved tree into an
  **external** project directory, with containment checks replacing the
  blanket absolute-path refusal (`init.py:805-816`) — resolved deploy
  paths must stay inside the target, and the target must be a git repo
  unless `--force`.
- `init.py --bootstrap` composes the existing pieces into one command:
  `quick_setup` (`init.py:299`) → build → deploy → idempotent seeding of
  `starters/` content that today exists only as manual README steps.
- A new adopter goes from clone to working agent setup with one
  documented command; README Quick Start and `docs/ONBOARDING.md` are
  rewritten around it, and the `@onboarding` skill drives `--bootstrap`
  instead of narrating manual copies.
- The "separate template repo" alternative is consciously deferred and
  the tradeoff is recorded (ADR note or CHANGELOG): in-repo bootstrap
  now, template repo later as a thin wrapper over `--bootstrap`.

## Why This Sprint

Every prior roadmap rung made claims true for *this* repo; none made
adoption easy. Today the deploy guard hard-exits on any absolute path
(`init.py:805-816`), so deploying into another project requires manual
copying — the README's multi-step setup is the single biggest friction
for new adopters. This lands last among the roadmap drafts because it
packages everything the earlier rungs produce (hardened build from
Sprint 2, per-platform emission from `platform-parity-draft-plan.md`,
mode CLIs from the promotion drafts) into the front door. The
containment rework is deliberate security surface — the original
guardrail exists for a reason — so containment tests are non-negotiable
and `@security` gates the sprint.

## Technical Tasks

Execution order: **1 → 2** (guardrail rework, then external deploy) are
sequenced; **3** (bootstrap) after 2; **4** (starters seeding) with 3;
**5, 6** (tests, docs) after 3-4.

### Task Group 1: Containment-checked deploy guardrail
Files: `init.py`, `tests/test_init.py`

- [ ] Replace the blanket `Path(...).is_absolute()` refusal in
      `deploy_resolved` (`init.py:805-816`) with containment checks:
      every deploy destination, fully resolved (`Path.resolve()`,
      symlinks included), must be inside the deploy root (cwd today,
      `--target` after TG2). Use strict ancestor checks
      (`Path.is_relative_to`), not string prefixes.
- [ ] Reject path traversal (`..`), symlink escape, and absolute deploy
      tokens that resolve outside the root — same loud `sys.exit(1)`
      posture with an error naming the offending key.
- [ ] Keep current behaviour byte-identical for the in-repo (no
      `--target`) case.
- [ ] Containment tests are non-negotiable: traversal, symlink escape,
      absolute token, and happy-path cases on both CI OSes.

### Task Group 2: `init.py --target <path>` external deploy
Files: `init.py`, `tests/test_init.py`

- [ ] Add `--target <path>` to the CLI (argparse block,
      `init.py:884-906`): build into `resolved/` as today, then deploy
      into `<path>` with all `paths.*` deploy tokens interpreted
      relative to the target root.
- [ ] Target validation: must exist and be a git repository (`.git`
      present) unless `--force` is passed; never deploy into the
      substrate repo itself via `--target` (self-deploy stays the
      default no-flag path).
- [ ] Post-deploy verification runs against the target tree: token-free
      scan (`find_unresolved_tokens`) and deploy-count report, mirroring
      `deploy_resolved` (`init.py:782`).
- [ ] Deterministic: deploying twice into the same target is
      byte-identical.

### Task Group 3: `init.py --bootstrap` composition
Files: `init.py`, `tests/test_init.py`

- [ ] Add `--bootstrap [<path>]`: run `quick_setup` (`init.py:299`,
      reusing its create-from-example flow) → build → deploy (in-repo or
      `--target`) → seed starters (TG4), as one command with one
      summary.
- [ ] Non-interactive mode for CI/tests (`--bootstrap` honours an
      existing config without prompting; prompts only when config is
      missing and a TTY is present).
- [ ] Second run is a safe no-op: existing config untouched, deploy
      idempotent, seeding skips existing files with a report.
- [ ] Clear failure modes: any phase failing exits non-zero with the
      phase named; no partial silent success.

### Task Group 4: Idempotent `starters/` seeding
Files: `init.py`, `starters/` (new or consolidated), `tests/test_init.py`

- [ ] Collect the manual README "next steps" content (planning ledger
      skeleton, SPRINTS skeleton, config starter, etc.) into a
      `starters/` source tree with a small manifest of
      destination paths.
- [ ] Seeding copies each starter only if the destination is absent —
      never overwrites adopter files; reports seeded vs. skipped.
- [ ] Starters pass the same containment checks (TG1) and token-free
      verification as the deploy.
- [ ] Determinism: seeding output is sorted/stable.

### Task Group 5: Bootstrap end-to-end tests
Files: `tests/test_bootstrap.py` (new), `tests/test_init.py`

- [ ] End-to-end: bootstrap into a scratch git repo (tmp dir) →
      assert full artifact tree, token-free, starters seeded.
- [ ] Idempotency: second `--bootstrap` run is a no-op (byte-identical
      tree, "skipped" report).
- [ ] Guard rails: non-git target without `--force` refused; traversal
      and symlink-escape targets refused (overlaps TG1 but exercised
      through the CLI).
- [ ] Windows + Linux CI coverage for the path semantics.

### Task Group 6: Docs rewrite around the one-liner
Files: `README.md`, `docs/ONBOARDING.md`, `skills/onboarding/onboarding.skill.md`, `docs/QUICKSTART.md`, `CHANGELOG.md`

- [ ] README Quick Start: lead with the one-liner
      (`python init.py --bootstrap --target <your-project>`); demote the
      manual copy steps to an appendix or remove where superseded.
- [ ] Rewrite `docs/ONBOARDING.md` around bootstrap; align
      `docs/QUICKSTART.md`.
- [ ] `@onboarding` skill drives `--bootstrap` (runs/guides the command
      and verifies its report) instead of narrating manual steps; keep
      the per-platform split (see `docs/PLATFORMS.md` from the platform
      parity work).
- [ ] Record the template-repo tradeoff in the CHANGELOG (and ADR
      addendum if `@architect` prefers): separate template repo is out
      of scope now; `--bootstrap` is the supported path; a future
      template repo would be a thin wrapper over it.

## Files to Create/Modify

- `init.py` — containment guardrail rework, `--target`, `--bootstrap`, starters seeding (TG1-4)
- `starters/**` (new/consolidated) + seeding manifest (TG4)
- `tests/test_bootstrap.py` (new), `tests/test_init.py` (TG1-5)
- `README.md`, `docs/ONBOARDING.md`, `docs/QUICKSTART.md`, `skills/onboarding/onboarding.skill.md`, `CHANGELOG.md` (TG6)

## Quality Gates

- [ ] standard — `python -m pytest tests/ -v` stays green, zero new warnings, both CI OSes
- [ ] Determinism — re-run `init.py` twice, output identical; second bootstrap into the same target is a byte-identical no-op
- [ ] guardrail — token-free `.github/**` check passes; token-free scan also runs against the external target tree
- [ ] docs — voice/heading tests green for rewritten `docs/ONBOARDING.md` / `docs/QUICKSTART.md`
- [ ] security — `@security` review of the containment rework (it replaces an existing safety guard)

## Success Criteria

- [ ] `--target` deploys into an external git repo; containment violations (traversal, symlink escape, absolute tokens) are refused with named-key errors.
- [ ] `--bootstrap` takes a fresh adopter from zero to deployed artifacts + seeded starters in one command; second run is a no-op.
- [ ] The previous absolute-path protection level is preserved or strengthened — proven by tests, on both OSes.
- [ ] README Quick Start and onboarding docs/skill lead with the one-liner; manual copy steps no longer the primary path.
- [ ] Template-repo deferral recorded with rationale.

## Risks

- Relaxing the absolute-path guard is a real security-surface change —
  mitigation: containment via resolved-path ancestor checks (not string
  matching), symlink/traversal tests are non-negotiable, `@security`
  gate required, and the no-flag in-repo path keeps its exact current
  behaviour.
- `--bootstrap` interactivity (`quick_setup` prompts) breaks CI and
  agent-driven runs — mitigation: non-interactive contract defined in
  TG3 and tested; prompts only on missing config + TTY.
- Seeding could overwrite adopter files on name collision — mitigation:
  absent-only copy semantics with a skipped report; covered by the
  idempotency e2e test.
- Docs rewrite can desync from the canonical-build-command CI check
  (ITEM-011) — mitigation: the one-liner still references
  `config/project.config.example.yml`; the doc check runs in CI and
  fails on drift.
- Scope creep toward packaging (PyPI/console scripts) — mitigation:
  explicitly out of scope here; packaging remains a separate optional
  roadmap item gated on `@pm` demand validation.

## Sprint Execution Guidelines

_(left for @sprint-lead)_

## Commit Plan

_(left for @sprint-lead)_
