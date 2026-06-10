# Mode 2 Dispatcher Promotion — Supported Implementation in `src/`

**Status:** Active
**Type:** Feature (mode promotion per ADR 0008)
**Sources:** session review 2026-06-10 (user-approved "close the gap upward" roadmap), ADR-0008 (supported mode implementations) · **Ledger:** ITEM-018
**Dependencies:** ADR-0008 (Sprint 3); platform parity work referenced by slug `platform-parity-draft-plan.md` is independent — no hard dependency

## Goals

- Mode 2 (Orchestration) graduates from "frozen contract + reference
  impl" to a **supported implementation**: `src/mode2_dispatcher/`
  satisfying all five ADR 0008 promotion criteria.
- A root-level CLI `dispatch.py` mirrors the `init.py` UX so adopters
  run Mode 2 without installing Mode 1.
- Crash-safety and idempotency exceed the reference impl: atomic state
  writes, a journal, and crash-resume — the reference impl's plain
  `state.yml` rewrite (`dispatcher.py:104-107`) is the baseline to beat.
- Both the reference impl and the production package pass the same
  `mode-2-contract-v1` checklist via shared parametrized conformance
  tests; the reference impl stays byte-unchanged.
- Adopters have `docs/ORCHESTRATION.md` and the Mode 2
  `install-contract.md` names the supported implementation.

## Why This Sprint

The README claims three delivery modes; today Mode 2 exists only as
`command-centre/03-mode-orchestration/reference-impls/file-queue-dispatcher/`
— explicitly didactic, not production. Sprint 3's ADR 0008 revised the
`command-centre/PLAN.md` non-goal and defined the 5-point promotion
contract precisely so this work could start. Mode 2 goes before Mode 3
(`mode3-coordinator-promotion-draft-plan.md`) because the dispatcher is
self-contained (file queue, no fleet registry), its contract checklist
is already executed in CI
(`tests/test_protocol_v1_conformance.py:167-182`), and the promotion
pattern established here (src/ package + root CLI + shared conformance)
is the template the Mode 3 sprint reuses.

## Technical Tasks

Execution order: **1 → 2 → 3** build the package core (sequenced);
**4** (CLI) after 1-3; **5, 6** (tests) after 4; **7** (docs) last.

### Task Group 1: `src/mode2_dispatcher/` core port
Files: `src/mode2_dispatcher/__init__.py` (new), `src/mode2_dispatcher/dispatcher.py` (new)

- [ ] Create the package mirroring the `src/phase1_verification/` layout
      (`__init__.py` + focused modules).
- [ ] Port the dispatcher core from
      `command-centre/03-mode-orchestration/reference-impls/file-queue-dispatcher/dispatcher.py`:
      state machine (`_ALLOWED_TRANSITIONS`, ~L75-78, `TransitionError`),
      `dispatch_one`/`run` flow (~L169-229), tier-3 summary emission.
- [ ] Port the ghost-done verifier (`dispatcher.py:135-167`): never mark
      done solely because the session ended; verifier outputs +
      return-tier validation decide.
- [ ] Reference impl files are **not modified** — port by copy +
      adaptation; ADR 0008 criterion 5 (byte-unchanged) verified by test.

### Task Group 2: Callable discovery (`discovery.py`)
Files: `src/mode2_dispatcher/discovery.py` (new)

- [ ] Discover `*.callable.yml` sidecar manifests per the non-enterprise
      example in
      `command-centre/01-protocols/callable-contract.md` (~L93-116).
- [ ] Discover `callable-v1` frontmatter in skill files (the enterprise
      path), reusing the frontmatter parsing already proven in `init.py`.
- [ ] Validate every discovered callable against
      `schemas/callable-v1.schema.json`; invalid callables are reported
      with path + violation, never silently skipped.
- [ ] Deterministic discovery order (sorted paths) so runs are
      reproducible.

### Task Group 3: Durable queue (`queue_file.py`) + return validation (`returns.py`)
Files: `src/mode2_dispatcher/queue_file.py` (new), `src/mode2_dispatcher/returns.py` (new)

- [ ] `queue_file.py`: atomic `state.yml` writes (write-temp + `os.replace`),
      an append-only journal of transitions, and crash-resume — on
      startup, reconcile journal vs. state and resume in-flight items
      safely (in-progress items without a terminal record re-queue per
      the contract's `failed → queued` / `rejected → queued` transitions).
- [ ] Honour `.mode-2-pins` (contract pin file) when loading queue
      config.
- [ ] `returns.py`: validate subagent returns by **reusing**
      `SubagentReturnValidator` from `src/phase1_verification/validator.py:67`
      against `schemas/subagent-return-tier{1,2,3}.schema.json` — no
      duplicated validation logic.
- [ ] No schema or contract text changes: `mode-2-contract-v1` and
      `protocol-v1` remain frozen.

### Task Group 4: Root CLI `dispatch.py`
Files: `dispatch.py` (new, repo root)

- [ ] Subcommands: `run` (drain inbox, emit tier-3 summary), `status`
      (queue state report), `requeue <item-id>` (contract-legal
      transitions only), `validate-callables` (discovery + schema check,
      non-zero exit on violations).
- [ ] Mirror `init.py` CLI conventions (argparse, clear errors, non-zero
      exit on failure) but stay a **separate entry point**: `init.py` is
      the Mode 1 build tool; `dispatch.py` is Mode 2 runtime and must
      work in a repo that never ran `init.py`.
- [ ] `--queue-root` argument with the same relative-path containment
      posture as the deploy guard (`init.py:805-816`).

### Task Group 5: `tests/test_mode2_dispatcher.py`
Files: `tests/test_mode2_dispatcher.py` (new)

- [ ] State-machine tests: every allowed transition, every illegal
      transition raises `TransitionError`.
- [ ] Ghost-done tests: session end without verifier evidence never
      yields `done`.
- [ ] Crash-resume tests: kill mid-dispatch (simulated partial
      state/journal), restart, queue reconciles without loss or
      duplicate dispatch; state writes are atomic (no torn `state.yml`).
- [ ] Non-enterprise callable end-to-end: a `*.callable.yml` sidecar
      (per `callable-contract.md` ~L98-116) is discovered, dispatched,
      and verified with zero enterprise-substrate coupling.
- [ ] CLI tests: `validate-callables` exit codes; `requeue` rejects
      illegal transitions.

### Task Group 6: Shared conformance parametrization
Files: `tests/test_protocol_v1_conformance.py`, `tests/test_mode2_dispatcher.py`

- [ ] Extend the Mode 2 conformance hook
      (`tests/test_protocol_v1_conformance.py:167-182`) into a
      parametrized run over **both** implementations: the frozen
      reference impl and `src/mode2_dispatcher/` — same
      `mode-2-contract-v1` checklist, same fixtures.
- [ ] Add a byte-freeze test: hash the reference-impl files
      (`dispatcher.py`, `conformance_test.py`, `README.md`) and assert
      unchanged (ADR 0008 criterion 5).

### Task Group 7: Adopter docs + install contract
Files: `docs/ORCHESTRATION.md` (new), `command-centre/03-mode-orchestration/install-contract.md`, `README.md`, `CHANGELOG.md`

- [ ] Write `docs/ORCHESTRATION.md`: install, queue layout, callable
      authoring (sidecar + frontmatter), `dispatch.py` usage,
      crash-recovery semantics.
- [ ] Update `command-centre/03-mode-orchestration/install-contract.md`
      to name `src/mode2_dispatcher/` + `dispatch.py` as the supported
      implementation (per ADR 0008 criterion 4), keeping the contract
      text itself frozen.
- [ ] README: Mode 2 row/claims updated to "supported implementation";
      CHANGELOG entry.

## Files to Create/Modify

- `src/mode2_dispatcher/{__init__.py,dispatcher.py,discovery.py,queue_file.py,returns.py}` (new) (TG1-3)
- `dispatch.py` (new, root) (TG4)
- `tests/test_mode2_dispatcher.py` (new), `tests/test_protocol_v1_conformance.py` (TG5, TG6)
- `docs/ORCHESTRATION.md` (new), `command-centre/03-mode-orchestration/install-contract.md`, `README.md`, `CHANGELOG.md` (TG7)
- **Not modified:** `command-centre/03-mode-orchestration/reference-impls/file-queue-dispatcher/**` (frozen, asserted by test), `schemas/**`, contract texts

## Quality Gates

- [ ] standard — `python -m pytest tests/ -v` stays green (401+ plus new module), zero new warnings, both CI OSes
- [ ] Determinism — re-run `init.py` twice, output identical; dispatcher discovery order deterministic
- [ ] guardrail — token-free `.github/**` check passes (sprint adds no tokens there)
- [ ] docs — voice/heading tests green for `docs/ORCHESTRATION.md`
- [ ] conformance — reference impl **and** `src/mode2_dispatcher/` both pass `mode-2-contract-v1`; reference impl byte-unchanged

## Success Criteria

- [ ] `src/mode2_dispatcher/` meets all five ADR 0008 criteria (src/ + root CLI; pytest contract checklist on both OSes; crash-safety beyond reference; adopter doc + named in install-contract; reference impl frozen).
- [ ] `python dispatch.py run` drains a fixture queue and emits a valid tier-3 summary; crash-resume proven by test.
- [ ] A non-enterprise `*.callable.yml` callable round-trips end-to-end.
- [ ] Shared conformance parametrization covers both implementations.
- [ ] `docs/ORCHESTRATION.md` published; install-contract names the supported impl; README/CHANGELOG updated.

## Risks

- Porting could drift from the contract semantics the reference impl
  encodes — mitigation: shared parametrized conformance (TG6) runs the
  identical checklist against both; any divergence fails CI.
- Crash-resume logic is the highest-complexity new code — mitigation:
  journal + atomic-replace design kept minimal; dedicated
  partial-failure tests in TG5; `@qa` gate on this task group.
- Temptation to "improve" the frozen contract while productionizing —
  mitigation: zero contract/schema diffs is an explicit checklist item;
  any breaking need escalates to `-v2` per ADR 0003 and back to
  `@planner`.
- Reuse of `SubagentReturnValidator` couples Mode 2 to
  `src/phase1_verification/` — mitigation: this is intentional reuse of
  a stable in-repo module (no Mode 1 build artifacts required at
  runtime); the e2e test runs without a prior `init.py` build to prove
  independence.
- Windows CI path/atomic-rename semantics differ — mitigation:
  `os.replace` (atomic on both OSes), `encoding="utf-8"` everywhere,
  conformance on both CI OSes per ADR 0008 criterion 2.

## Sprint Execution Guidelines

- One subagent per task-group batch; subagents edit files only — the
  sprint lead commits each batch with explicit pathspecs.
- Deploy-capable subagents are told exactly which config to use
  (Sprint 4 retro lesson); this sprint should not need `--deploy` at all.
- Tests include a stale-state dimension where applicable (Sprint 4
  retro lesson): crash-resume IS that dimension here.
- CI on the PR branch is part of the sprint contract: any failing check
  observed during the sprint is diagnosed and fixed before close.
- Batch order: TG1-4 (package + CLI) → TG5+TG6 (tests) ∥ TG7 (docs).

## Commit Plan

_(left for @sprint-lead)_
