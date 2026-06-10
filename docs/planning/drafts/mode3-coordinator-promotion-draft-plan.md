# Mode 3 Coordinator Promotion — Supported Implementation in `src/`

**Status:** DRAFT
**Type:** Feature (mode promotion per ADR 0008)
**Sources:** session review 2026-06-10 (user-approved "close the gap upward" roadmap), ADR-0008 (supported mode implementations) · **Ledger:** ITEM-019
**Dependencies:** ADR-0008 and the `referencing` migration (both Sprint 3, ITEM-013 closed); promotion patterns established by `mode2-dispatcher-promotion-draft-plan.md` (src/ package + root CLI + shared conformance + byte-freeze test)

## Goals

- Mode 3 (Choreography) graduates to a **supported implementation**:
  `src/mode3_coordinator/` satisfying all five ADR 0008 criteria, built
  on the modern `referencing` registry API (never the deprecated
  `jsonschema.RefResolver` — debt paid in Sprint 3).
- The toy harvest (`registry-coordinator/coordinator.py:127-144`) is
  replaced by a real harvest pipeline implementing
  `command-centre/05-promotion-contract.md`: eligibility assessment,
  required evidence files, append-only audit records, and
  `promoted` / `parked` / `rejected` decisions with written reasons.
- A root CLI `coordinate.py` mirrors the `init.py` UX, including an
  `init` subcommand that seeds a registry skeleton and the coordinator
  meta-agents — which stay coordinator-scoped and are **not** added to
  `skills/` (the 13-agent claim and count tests must hold).
- The `command-centre/PLAN.md` Phase 3 exit criterion — "a dry-run
  harvest cycle completes against a fake registry of three projects and
  produces a valid audit record" — is encoded as a pytest test against
  a committed fleet fixture.
- Conformance parity: reference impl and production package pass the
  same `mode-3-contract-v1` checklist; reference impl byte-unchanged.

## Why This Sprint

Mode 3 is the last unproven delivery-mode claim. The reference
coordinator
(`command-centre/04-mode-choreography/reference-impls/registry-coordinator/coordinator.py`)
validates a registry and detects drift, but its `harvest()` is
explicitly a toy (writes a stub audit record, ~L127-144) — the
promotion contract that gives Mode 3 its value is not executed by any
code. This sprint follows the Mode 2 promotion
(`mode2-dispatcher-promotion-draft-plan.md`) deliberately: the src/
package + root CLI + shared-conformance + byte-freeze pattern is
proven there first, and the Sprint 3 `referencing` migration ensures no
production Mode 3 code is born on a deprecated API
(registry validation pattern now at
`tests/test_protocol_v1_conformance.py:150-159`).

## Technical Tasks

Execution order: **1** (fixture) and **2** (core port) in parallel;
**3** (harvest) after 2; **4** (CLI) after 2-3; **5, 6** (tests) after
4; **7** (docs) last.

### Task Group 1: `tests/fixtures/fleet/` — 3-project mixed-mode fixture
Files: `tests/fixtures/fleet/` (new: 3 fabricated project dirs + `registry.yml`)

- [ ] Fabricate three projects with mixed mode levels (per the
      consumption matrix in
      `command-centre/04-mode-choreography/mixed-fleet-example.md`):
      e.g. one Mode 1 consumer, one Mode 2 (orchestration pins), one
      Mode 3 participant with promotion candidates.
- [ ] A fleet `registry.yml` valid against
      `schemas/registry-v1.schema.json`, with contract pins and
      substrate versions arranged so drift/impact have non-trivial
      results.
- [ ] Include at least one harvest candidate with complete evidence and
      one with incomplete evidence (must park, not reject, per
      `05-promotion-contract.md` ~L56-57).

### Task Group 2: `src/mode3_coordinator/` core port on `referencing`
Files: `src/mode3_coordinator/__init__.py` (new), `src/mode3_coordinator/coordinator.py` (new)

- [ ] Package mirrors `src/phase1_verification/` layout; port registry
      load + schema validation from
      `registry-coordinator/coordinator.py` (`_schema_registry`, ~L43)
      using the `referencing.Registry` API exclusively.
- [ ] Port `detect_drift` (~L97), `impact_of_contract_bump` (~L112),
      `list_by_mode_level` (~L120) with the same semantics.
- [ ] Crash-safety/idempotency beyond the reference impl (ADR 0008
      criterion 3): atomic writes for every registry/audit mutation;
      re-running any read-only command is side-effect-free.
- [ ] Reference impl not modified; byte-freeze test added in TG6.

### Task Group 3: Real `harvest.py` per the promotion contract
Files: `src/mode3_coordinator/harvest.py` (new)

- [ ] Implement the harvest cycle from
      `command-centre/05-promotion-contract.md`: identify candidates →
      assess eligibility (each criterion cited on failure) → gather
      required evidence files → stage for review → record decision.
- [ ] Decisions limited to `promoted` / `parked` / `rejected`;
      `parked` and `rejected` require a written reason; incomplete
      evidence ⇒ parked, never rejected.
- [ ] Audit records are **append-only** (never rewrite history) and
      validate as harvest-audit documents; parked candidates land under
      `harvest/parked/` per the contract.
- [ ] `--dry-run` mode: full cycle, decisions computed, no filesystem
      mutation outside the audit/dry-run report.

### Task Group 4: Root CLI `coordinate.py`
Files: `coordinate.py` (new, repo root)

- [ ] Subcommands: `validate` (registry vs `registry-v1`), `drift`,
      `impact <contract-tag>`, `harvest --dry-run`, `decide <candidate>
      --decision promoted|parked|rejected --reason …`, `init`.
- [ ] `init`: seed a registry skeleton (`registry.yml` + dirs) and copy
      the meta-agents (`audit.agent.md`, `framework-dev.agent.md`,
      `harvest.agent.md` from
      `registry-coordinator/meta_agents/`) into the coordinator
      workspace — coordinator-scoped only, **never** into `skills/`
      (would break the 13-agent claim and count tests).
- [ ] Mirror `init.py` CLI conventions; separate entry point — Mode 3
      installs without Mode 1 or Mode 2.
- [ ] Idempotent `init`: re-running against an existing workspace is a
      no-op (or explicit refusal), never a clobber.

### Task Group 5: `tests/test_mode3_coordinator.py` + Phase 3 exit criterion
Files: `tests/test_mode3_coordinator.py` (new)

- [ ] Encode the `command-centre/PLAN.md` Phase 3 exit criterion as a
      test: `harvest --dry-run` against `tests/fixtures/fleet/`
      (3 projects) completes and produces a valid audit record.
- [ ] Eligibility tests: each criterion failure cites the criterion;
      incomplete evidence parks; written reasons enforced for
      parked/rejected.
- [ ] Append-only audit test: a second harvest cycle appends, never
      rewrites.
- [ ] Drift/impact tests against the fixture registry; `init` seeding
      idempotency; meta-agents are absent from `skills/` and the agent
      count stays 13.
- [ ] Zero deprecation warnings (no `RefResolver` anywhere in `src/`).

### Task Group 6: Conformance parity + reference freeze
Files: `tests/test_protocol_v1_conformance.py`

- [ ] Parametrize the Mode 3 conformance run
      (`tests/test_protocol_v1_conformance.py:185` onward) over both
      implementations: frozen reference impl and
      `src/mode3_coordinator/`, same `mode-3-contract-v1` checklist and
      fixtures.
- [ ] Byte-freeze test for
      `command-centre/04-mode-choreography/reference-impls/registry-coordinator/**`
      (mirror the Mode 2 pattern).

### Task Group 7: Adopter docs
Files: `docs/CHOREOGRAPHY.md` (new), `command-centre/04-mode-choreography/install-contract.md`, `README.md`, `CHANGELOG.md`

- [ ] Write `docs/CHOREOGRAPHY.md`: fleet registry setup,
      `coordinate.py` usage, harvest cadence pointers
      (`harvest-cadence.md`), meta-agent roles, evidence requirements.
- [ ] Update `command-centre/04-mode-choreography/install-contract.md`
      to name `src/mode3_coordinator/` + `coordinate.py` as the
      supported implementation (ADR 0008 criterion 4); contract text
      stays frozen.
- [ ] README Mode 3 claims updated; CHANGELOG entry.

## Files to Create/Modify

- `src/mode3_coordinator/{__init__.py,coordinator.py,harvest.py}` (new) (TG2, TG3)
- `coordinate.py` (new, root) (TG4)
- `tests/fixtures/fleet/**` (new), `tests/test_mode3_coordinator.py` (new), `tests/test_protocol_v1_conformance.py` (TG1, TG5, TG6)
- `docs/CHOREOGRAPHY.md` (new), `command-centre/04-mode-choreography/install-contract.md`, `README.md`, `CHANGELOG.md` (TG7)
- **Not modified:** `command-centre/04-mode-choreography/reference-impls/registry-coordinator/**` (frozen, asserted by test), `schemas/**`, contract texts, `skills/**` (no meta-agents added)

## Quality Gates

- [ ] standard — `python -m pytest tests/ -v` stays green, zero new warnings (incl. zero jsonschema deprecation warnings), both CI OSes
- [ ] Determinism — re-run `init.py` twice, output identical; `coordinate.py init` idempotent; dry-run harvest reproducible against the fixture
- [ ] guardrail — token-free `.github/**` check passes
- [ ] docs — voice/heading tests green for `docs/CHOREOGRAPHY.md`
- [ ] conformance — reference impl **and** `src/mode3_coordinator/` both pass `mode-3-contract-v1`; reference impl byte-unchanged; agent count stays 13

## Success Criteria

- [ ] `src/mode3_coordinator/` meets all five ADR 0008 criteria.
- [ ] `python coordinate.py harvest --dry-run` against `tests/fixtures/fleet/` completes with a valid audit record — the PLAN.md Phase 3 exit criterion holds as a test, permanently.
- [ ] Harvest implements the full promotion contract: eligibility, evidence, append-only audit, promoted/parked/rejected with reasons.
- [ ] Meta-agents seeded coordinator-scoped only; `skills/` untouched; 13-agent claim intact.
- [ ] `docs/CHOREOGRAPHY.md` published; install-contract names the supported impl.

## Risks

- The promotion contract is the most judgement-heavy contract in the
  repo; code could encode a stricter or looser reading than the text —
  mitigation: every eligibility criterion and evidence row in
  `05-promotion-contract.md` maps 1:1 to a named test in TG5; `@qa`
  reviews the mapping table.
- Meta-agents leaking into `skills/` would silently break the 13-agent
  claim — mitigation: explicit negative test (TG5) pins the skill/agent
  count.
- Fabricated fleet fixture may not represent real adopter fleets —
  mitigation: fixture mirrors the documented `mixed-fleet-example.md`
  shapes; documented as a fixture, not a benchmark; extendable later.
- Append-only audit + atomic writes on Windows CI — mitigation: same
  `os.replace` + utf-8 discipline as the Mode 2 promotion; both-OS CI
  per ADR 0008 criterion 2.
- Scope creep into harvest *automation* (cadence, CI wiring) —
  mitigation: cadence stays documentation
  (`harvest-cadence.md`); this sprint ships the cycle as a CLI run,
  nothing scheduled.

## Sprint Execution Guidelines

_(left for @sprint-lead)_

## Commit Plan

_(left for @sprint-lead)_
