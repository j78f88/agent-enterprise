# Run sheet — `agent-homebase@2.0.0` release

> **SUPERSEDED (2026-05-16):** `agent-homebase@2.0.0` and `protocol-v1`
> shipped on commit `b943090`. This run sheet is preserved for historical
> record only. See [CHANGELOG.md](../../../CHANGELOG.md) for the released
> scope.

> **Audience:** the executing agent (Copilot / Claude Code / etc).
> **Mode:** agent-delivered. Time is not a constraint; correctness is.
> **Output target:** tagged release `agent-homebase@2.0.0` with
> `protocol-v1`, `mode-1-contract-v1`, `mode-2-contract-v1`,
> `mode-3-contract-v1` all backed by enforced schemas and ≥1
> reference implementation per mode.

---

## How to use this run sheet

1. Phases are **strictly ordered**. Each phase has a **gate** that
   must pass before the next phase starts.
2. Inside a phase, steps may run in any order unless marked
   `(blocks N)`.
3. Each step has: **deliverable**, **acceptance check**, **verify
   command**. Do not mark a step done until the verify command passes.
4. After every step, run the full test suite. The suite must stay
   green throughout.
5. Each phase ends with a **commit** using Conventional Commits.
   Pushing to `main` is allowed only after the phase gate passes.

## Repo state at start of run

- Branch: `main`
- Last commit: `6b56923 docs: close residual plan items (R8, R10, reference-impl wording)`
- Tests: 167 passed / 7 skipped
- All 16 items of the prior remediation plan complete.
- `command-centre/` v2 workbench finalised as contract design.
- v1 `command centre/` deleted.
- ADR-0007 explicitly defers schemas + reference impls "until a real
  P3 adopter signal materialises." This run sheet **withdraws that
  deferral** because the user is choosing to ship complete rather than
  ship preview.

## Scope

**In:** schemas, frontmatter validation, conformance tests, one
reference dispatcher (Mode 2), one reference coordinator (Mode 3),
substrate alignment with contracts, open contract decisions, docs
polish, README/help/onboarding, repo hygiene, release ritual.

**Out:** building schemas for runtimes we do not target (e.g., MCP
sidecar). Building more than one reference impl per mode. Cross-
platform CI (kept as-is). New profiles beyond the three existing.

---

## Phase 0 — Pre-flight

### 0.1 Snapshot baseline metrics

- **Deliverable:** baseline numbers recorded in
  `docs/sprints/v2-release/baseline.md`.
- **Capture:** test count, skip count, lint count (if any), file
  count under `command-centre/`, `skills/`, `instructions/`,
  `agents/`, `schemas/`, line count of `init.py`.
- **Verify:** file exists and contains all six numbers.

### 0.2 Re-affirm or update ADR-0007

> **Note:** ADR-0008 was never created. ADR-0007 remains in `Accepted` status. The references below are historical plan context only.

- **Deliverable:** edit
  [command-centre/decisions/0007-personas-scope-and-deferral.md](../../../command-centre/decisions/0007-personas-scope-and-deferral.md)
  status from `Accepted` to `Superseded by ADR-0008` and add
  ADR-0008 *"Ship `protocol-v1` complete: schemas and reference
  impls land at v2.0.0"* under
  `command-centre/decisions/0008-ship-protocol-v1-complete.md`.
- **Acceptance:** ADR-0008 states the rationale, names the deferral
  it reverses, lists the deliverables it commits to (Tier A + Tier B
  + Tier C below), cites the trigger (user direction, dated).
- **Verify:** both files exist; cross-links resolve.

### 0.3 Phase 0 gate

- Commit `chore(release): v2.0.0 run sheet + baseline + ADR-0008`.
- Tests green.
- No push yet.

---

## Phase 1 — Repo hygiene (no contract decisions)

Lowest-risk work that surfaces drift before contract work begins.

### 1.1 Untrack `resolved/` (already in `.gitignore`)

- **Deliverable:** `resolved/` is no longer tracked. New builds do
  not produce status noise.
- **Steps:**
  ```powershell
  git rm -r --cached resolved/
  ```
- **Acceptance:** `git status --short` after a fresh
  `python init.py --config config/project.config.example.yml` shows
  zero `resolved/*` entries.
- **Verify:** above command in PowerShell.

### 1.2 Untrack `.agent-state/`

- **Deliverable:** `.agent-state/` ignored and untracked.
- **Steps:**
  ```powershell
  Add-Content .gitignore "`n# Local agent state (debug logs, violations)`n.agent-state/`n"
  git rm -r --cached .agent-state
  ```
- **Verify:** `git status .agent-state` shows nothing.

### 1.3 Stale-link audit

- **Deliverable:** zero broken Markdown links across the repo.
- **Steps:** write
  `scripts/check-links.py` (~80 LOC, walks `**/*.md`, parses links,
  verifies file targets resolve). Run it; fix every broken link.
- **Acceptance:** script exits 0.
- **Verify:** `python scripts/check-links.py`.

### 1.4 Stale-reference audit

- **Deliverable:** zero references to retired concepts (`policies/`,
  `OPA`, `Rego`, `command centre v2/`, `command centre/`) outside
  designated history files (POLICY_AUDIT.md, BPA journal §, ADRs).
- **Steps:** grep for each term; for each hit, either delete or move
  to the designated history allowlist (documented in audit comment).
- **Verify:**
  ```powershell
  Get-ChildItem -Recurse -File -Include *.md,*.py,*.yml | `
    Select-String -Pattern "policies/|\bRego\b|\bOPA\b|command centre v2|command centre/" | `
    Where-Object { $_.Path -notmatch "POLICY_AUDIT|BPA_|JOURNAL|decisions/0007" }
  ```
  Empty result is pass.

### 1.5 Resolved-path-drift check

- **Deliverable:** all three profiles produce byte-identical
  `resolved/` directories on two sequential runs (determinism gate).
- **Verify:**
  ```powershell
  foreach ($p in "python-api","react-web-app","monorepo-fullstack") {
    Remove-Item -Recurse -Force resolved
    python init.py --config profiles/$p.config.yml
    $h1 = (Get-ChildItem resolved -Recurse -File | Get-FileHash -Algorithm SHA256).Hash -join ""
    Remove-Item -Recurse -Force resolved
    python init.py --config profiles/$p.config.yml
    $h2 = (Get-ChildItem resolved -Recurse -File | Get-FileHash -Algorithm SHA256).Hash -join ""
    if ($h1 -ne $h2) { throw "$p non-deterministic" } else { Write-Host "$p OK" }
  }
  ```

### 1.6 Phase 1 gate

- All four steps above pass.
- Full pytest green.
- Commit `chore(hygiene): untrack build output, fix stale links and refs, verify determinism`.
- Push to `main`.

---

## Phase 2 — Contract decisions (Tier D)

These decisions block schema authoring. Resolve all six. Each
decision lands as a one-page ADR; each ADR amends the relevant
contract document.

### 2.1 Verifier-recursion base case

- **Decision:** a verifier callable MUST declare `verifier: null`.
  Verifier-of-verifier is not supported.
- **Land in:** ADR-0009; amend
  [callable-contract.md](../../../command-centre/01-protocols/callable-contract.md)
  "Verifier hook" section to state the rule.

### 2.2 Tier 3 telemetry shape

- **Decision:** move `token_usage` and `tool_calls` under
  `runtime_telemetry` sub-object on tier-3 return. Optional.
  Non-LLM callables omit the sub-object.
- **Land in:** ADR-0010; update
  [return-schemas.md](../../../command-centre/01-protocols/return-schemas.md)
  + `schemas/subagent-return-tier3.schema.json`.

### 2.3 Registry `mode_level` future-proofing

- **Decision:** keep enum `team | orchestration` but reserve
  forward-compatible parsing: unknown values cause a typed warning,
  not a hard error, in coordinators implementing v1.1+.
- **Land in:** ADR-0011; amend
  [registry-schema.md](../../../command-centre/04-mode-choreography/registry-schema.md)
  "`mode_level` enum" section.

### 2.4 `applies_to` vs `scope:` reconciliation

- **Decision:** the canonical field is `applies_to`. `scope:`
  remains supported as an alias on read for one minor version, then
  removed at `frontmatter-v2`.
- **Land in:** ADR-0012; amend
  [frontmatter-spec.md](../../../command-centre/01-protocols/frontmatter-spec.md)
  to document the alias + sunset.

### 2.5 Meta-agents — three or four?

- **Decision:** three (`@framework-dev`, `@harvest`, `@audit`).
  `@migration` is opt-in per coordinator, not required by
  `mode-3-contract-v1`. Adding `@migration` later is non-breaking
  (additive).
- **Land in:** ADR-0013; amend
  [meta-agents.md](../../../command-centre/04-mode-choreography/meta-agents.md).

### 2.6 `05-promotion-contract.md` placement

- **Decision:** move under
  `command-centre/04-mode-choreography/promotion-contract.md`.
  Redirect via stub at old path for one release.
- **Land in:** ADR-0014; `git mv` the file; update cross-links;
  leave a 5-line stub at old path linking to new with a deprecation
  note.

### 2.7 Phase 2 gate

- All six ADRs exist (0009–0014).
- All six contract docs updated.
- Full pytest green.
- Commit per ADR (six commits) — atomicity matters for future
  bisects.
- Push.

---

## Phase 3 — Schemas (Tier A part 1)

Author every schema referenced by a contract.

### 3.1 `frontmatter-v1.schema.json`

- **Location:** `schemas/frontmatter-v1.schema.json`.
- **Required fields:** per
  [frontmatter-spec.md](../../../command-centre/01-protocols/frontmatter-spec.md).
- **Style:** match existing
  `schemas/subagent-return-tier1.schema.json` (draft-07, `$id`
  under `https://agent-homebase/schemas/...`, `title`, `description`,
  `required`, `properties` with `description` + `examples`).
- **Acceptance:** `python -c "import jsonschema, json; jsonschema.Draft7Validator.check_schema(json.load(open('schemas/frontmatter-v1.schema.json')))"`
  succeeds.

### 3.2 `callable-v1.schema.json`

- Same shape, references
  [callable-contract.md](../../../command-centre/01-protocols/callable-contract.md).
- Must allow Form A (artifact paths) AND Form B (return tier) AND
  both. Use `oneOf` between the artifact and return-tier branches,
  then `allOf` for the combined case.

### 3.3 `project-v1.schema.json`

- References
  [project-contract.md](../../../command-centre/01-protocols/project-contract.md).
- Captures `id`, `name`, `repo`, `mode_level`, `substrate_version`,
  `contract_pins`, optional fields per the contract.

### 3.4 `registry-v1.schema.json`

- References
  [registry-schema.md](../../../command-centre/04-mode-choreography/registry-schema.md).
- Top-level `projects: array of project-v1`. Use `$ref` to
  `project-v1.schema.json`.

### 3.5 Schema cross-link pass

- Update each contract doc's "schema lives at" pointer from
  "(added when this contract ships)" to a concrete relative link.
- Update [README.md](../../../README.md) "Key directories" if it
  mentions `schemas/`.

### 3.6 Phase 3 gate

- All four new schemas exist and self-validate.
- Pytest still green.
- Commit `feat(schemas): add frontmatter, callable, project, registry v1 schemas`.
- Push.

---

## Phase 4 — Frontmatter validation in `init.py` (Tier A part 2)

### 4.1 Add `validate_frontmatter()` helper

- **Location:** new function in `init.py` near the existing token
  helpers.
- **Signature:** `validate_frontmatter(text: str, kind: str, path: Path) -> list[str]`
  returning list of error messages. Empty list = pass.
- **Behaviour:**
  1. Parse YAML frontmatter (between leading `---` fences).
  2. Load `schemas/frontmatter-v1.schema.json`.
  3. Validate against schema with `jsonschema`.
  4. Return formatted error messages with file path + jsonpath +
     reason.

### 4.2 Wire into build loop

- Call `validate_frontmatter()` for every `*.skill.md`,
  `*.instructions.md`, `*.body.md` processed by the build.
- **Strict mode (default):** validation failure raises and aborts
  build.
- **Lax mode:** flag `--allow-frontmatter-warnings` collects errors,
  prints them as warnings, continues.

### 4.3 Update `requirements.txt`

- Add `jsonschema>=4.0`.
- **Verify:** `pip install -r requirements.txt` from fresh venv.

### 4.4 Unit tests

- `tests/test_frontmatter_validation.py` — minimum coverage:
  - Valid skill passes.
  - Skill missing `id` fails with clear message.
  - Skill with unknown `kind` fails.
  - Lax mode collects but does not abort.
  - Schema-self check (the schema itself validates against draft-07).

### 4.5 Phase 4 gate

- All new tests pass.
- Existing tests still pass (will likely fail until Phase 5 — see
  below — that is expected; if Phase 4 work breaks tests, run with
  `--allow-frontmatter-warnings` to confirm the breakage is
  substrate-content, not validator bugs).
- Commit `feat(init): validate frontmatter against v1 schema`.
- Push.

---

## Phase 5 — Substrate alignment (Tier C)

Bring the existing 13 skills, 13 agents, and instruction files into
conformance with `frontmatter-v1` + `callable-v1`.

### 5.1 Inventory mismatches

- **Deliverable:** `docs/sprints/v2-release/frontmatter-gap-report.md`
  listing every file failing `validate_frontmatter()`.
- **Generate:**
  ```powershell
  python init.py --config config/project.config.example.yml --allow-frontmatter-warnings 2>&1 | `
    Out-File docs/sprints/v2-release/frontmatter-gap-report.md
  ```

### 5.2 Bulk fill: required fields

- For every file in the gap report, add the four required fields
  (`id`, `kind`, `version`, `applies_to`) preserving existing
  frontmatter.
- **`id`:** filename-derived (`skills/security/security.skill.md` →
  `id: skill.security`).
- **`kind`:** derived from file location/suffix (skill, instruction,
  agent).
- **`version`:** `1.0.0` initial.
- **`applies_to`:** `"**"` unless the file already declares `scope:`
  or `paths:` (in which case map to `applies_to`).

### 5.3 Add callable manifest to every skill

- Add `inputs`, `outputs`, `verifier` fields per
  [callable-contract.md](../../../command-centre/01-protocols/callable-contract.md).
- Minimum acceptable: `inputs: { type: object, required: [task],
  properties: { task: { type: string } } }`, `outputs: [{ return_tier: 2 }]`,
  `verifier: null`.
- For skills that produce documented artifacts (e.g., `architect`,
  `planner`), declare artifact paths in `outputs`.

### 5.4 Migrate `scope:` → `applies_to`

- Per ADR-0012 alias rule: keep `scope:` working but every file in
  this repo standardises on `applies_to`. Drop `scope:` from sources.

### 5.5 Phase 5 gate

- `python init.py --config config/project.config.example.yml`
  succeeds in strict mode (no `--allow-frontmatter-warnings` flag).
- All three profiles succeed in strict mode.
- Full pytest green.
- Commit `refactor(substrate): align all skills/agents/instructions with frontmatter-v1 and callable-v1`.
- Push.

---

## Phase 6 — Conformance tests (Tier A part 3)

### 6.1 `tests/test_callable_conformance.py`

- Loads every skill manifest from `skills/**/*.skill.md`.
- For each: validates against `callable-v1.schema.json`.
- Negative fixtures under
  `tests/fixtures/callable/invalid/` — each fixture asserts the
  expected validation error code.

### 6.2 `tests/test_frontmatter_conformance.py`

- Loads every substrate file under `skills/`, `instructions/`,
  `agents/`.
- Validates against `frontmatter-v1.schema.json`.
- Negative fixtures under `tests/fixtures/frontmatter/invalid/`.

### 6.3 `tests/test_project_conformance.py`

- Loads every file matching `**/project.yml` (none expected in
  agent-homebase itself, but the test exists and uses fixtures).
- Validates against `project-v1.schema.json`.
- Fixtures under `tests/fixtures/project/`.

### 6.4 `tests/test_registry_conformance.py`

- Same shape, against `registry-v1.schema.json`.
- Fixture under `tests/fixtures/registry/`.

### 6.5 Mode 1 reference-substrate conformance test

- `tests/test_mode1_conformance.py` — asserts the agent-homebase
  repo itself satisfies every checkbox in
  [`02-mode-team/contract.md`](../../../command-centre/02-mode-team/contract.md)
  "Conformance checklist".

### 6.6 Phase 6 gate

- All five new test files pass.
- Full pytest green (now expected ~180+ passing tests).
- Commit `test(conformance): add per-contract conformance tests`.
- Push.

---

## Phase 7 — Reference implementations (Tier B)

### 7.1 Mode 2 reference dispatcher

- **Location:**
  `command-centre/03-mode-orchestration/reference-impl/file-queue-dispatcher/`
- **Contents:**
  - `README.md` — what it is, how to run, what it demonstrates.
  - `dispatcher.py` (~150 LOC) — file-queue source
    (`queue/inbox/*.yml`), callable resolver (loads `skills/**`),
    invocation (subprocess to Python that imports the skill),
    artifact-existence verifier, state-machine in `queue/state.yml`.
  - `conformance_test.py` — runs the dispatcher against a 3-item
    fixture queue (one passes, one fails verification, one errors)
    and asserts the dispatcher honours every responsibility in
    [`03-mode-orchestration/contract.md`](../../../command-centre/03-mode-orchestration/contract.md).
  - Fixtures under `fixtures/`.
- **Acceptance:** `python conformance_test.py` exits 0.

### 7.2 Mode 3 reference coordinator

- **Location:**
  `command-centre/04-mode-choreography/reference-impl/registry-coordinator/`
- **Contents:**
  - `README.md`.
  - `coordinator.py` (~250 LOC) — loads `registry.yml`, drift
    detection (compares each project's `substrate_version` against
    the current homebase tag), impact report on contract bump,
    `@harvest` cycle that scans `projects[].repo` for promotion
    candidates per the promotion contract, audit-record writer.
  - `meta_agents/` — three minimal meta-agents
    (`framework-dev`, `harvest`, `audit`) as instruction files +
    callable manifests.
  - `conformance_test.py` — fixture registry with 2 projects
    (one `team`, one `orchestration`); asserts every checkbox in
    [`04-mode-choreography/contract.md`](../../../command-centre/04-mode-choreography/contract.md).
- **Acceptance:** `python conformance_test.py` exits 0.

### 7.3 Update stub READMEs

- The "intentionally empty" wording from the prior commit moves into
  a "Status: complete — one reference impl provided. See
  `file-queue-dispatcher/`" line, with the cite to ADR-0008
  superseding ADR-0007's deferral.

### 7.4 Phase 7 gate

- Both conformance tests pass.
- Full pytest green.
- Two commits (one per impl):
  - `feat(mode2): add file-queue reference dispatcher + conformance test`
  - `feat(mode3): add registry reference coordinator + conformance test`
- Push.

---

## Phase 8 — Documentation polish

### 8.1 Top-level README rewrite

- **File:** [README.md](../../../README.md).
- **Sections required (in this order):**
  1. Tagline (one sentence — "Portable, multi-agent OS for software
     projects.").
  2. Who this is for — links to [docs/PERSONAS.md](../../PERSONAS.md).
  3. Quickstart — 5-line copy-paste pointing at
     [docs/QUICKSTART.md](../../QUICKSTART.md).
  4. What you get — three-mode bullet list, each linking to its
     `command-centre/0N-...` folder.
  5. Status — single line per mode showing contract tag +
     reference-impl status (now both green).
  6. Architecture — small Mermaid or ASCII showing
     `skills/ + instructions/ + agents/ + profiles/ → init.py → resolved/`,
     with `command-centre/` annotated as "contracts that this
     reference impl satisfies".
  7. Key directories table (already exists; refresh).
  8. Contributing pointer.
  9. License pointer.
- **Length cap:** 250 lines. Detail belongs in `docs/`.

### 8.2 `docs/QUICKSTART.md` re-verify

- Walk every step on a fresh clone in a scratch directory; if any
  step needs a prerequisite not mentioned, add it.
- **Verify:**
  ```powershell
  $tmp = New-Item -ItemType Directory -Path (Join-Path $env:TEMP "ahq-$(Get-Random)")
  Push-Location $tmp
  git clone https://github.com/j78f88/agent-homebase.git .
  # Execute every code block in docs/QUICKSTART.md verbatim
  Pop-Location
  Remove-Item -Recurse -Force $tmp
  ```

### 8.3 `docs/ARCHITECTURE.md` refresh

- Update the "Current state" section to reflect: schemas exist,
  validation enforced, reference impls present, OPA removed.
- Verify all internal links resolve.

### 8.4 `docs/EXTENSION_GUIDE.md` refresh

- New section: "Authoring a new callable" — walks through
  declaring `inputs`, `outputs`, `verifier`. Cite the new schema.
- Keep the existing token-convention section added earlier.

### 8.5 `docs/CUSTOMIZATION.md` refresh

- New section: "Frontmatter migration cheat sheet" — minimal map
  from old shape to `frontmatter-v1`.

### 8.6 `docs/ONBOARDING.md` refresh

- Confirm the 30-min path still works post-validation. Add an FYI
  about strict frontmatter mode.

### 8.7 `docs/TROUBLESHOOTING.md` refresh

- Add entries for: "frontmatter validation failed", "callable
  manifest missing", "registry validation failed".

### 8.8 `AGENTS.md` and `CLAUDE.md` refresh

- Update "Key directories" tables to drop any stale entries.
- Add `command-centre/` row (didn't exist as a tracked location
  before). Add `schemas/` row mentioning the new schemas.

### 8.9 `docs/CHANGELOG.md` entry for 2.0.0

- New section under `## 2.0.0`:
  - **Added:** ADRs 0008–0014, four new schemas, frontmatter
    validation, callable manifests on every skill, Mode 2 + Mode 3
    reference impls, conformance test suite, personas (P1–P4),
    QUICKSTART, run sheet.
  - **Changed:** `applies_to` is canonical (alias `scope:`
    deprecated), promotion contract moved into
    `04-mode-choreography/`, telemetry sub-object on tier-3 return.
  - **Removed:** OPA Rego layer (BPA Step 5b), v1 `command centre/`
    workbench.
  - **Deprecated:** `scope:` field (alias only; removal at
    `frontmatter-v2`).
  - **Migration:** for adopters on a pre-2.0 build, run
    `python tools/migrate-frontmatter.py` (write this small helper
    in 8.10).

### 8.10 Migration helper `tools/migrate-frontmatter.py`

- ~80 LOC: walks the supplied substrate path, rewrites legacy
  frontmatter into `frontmatter-v1` shape, prints a diff per file.
- `--dry-run` default; `--apply` to write.
- Self-test: round-trip on this repo produces no diff (because
  Phase 5 already migrated).

### 8.11 Phase 8 gate

- Every doc cross-link resolves (`python scripts/check-links.py`).
- Migration helper round-trips clean on this repo.
- Full pytest green.
- Commit `docs: v2.0.0 release notes, README rewrite, migration helper`.
- Push.

---

## Phase 9 — Help and discoverability

### 9.1 `python init.py --help`

- Confirm the help text mentions: `--config`, strict vs lax
  validation flag, `--quick-setup`. Update if missing.

### 9.2 Top-level `--help` for each tool in `tools/`

- Every script in `tools/` accepts `-h/--help` and prints a one-line
  description plus argument list. Add `argparse` boilerplate where
  missing.

### 9.3 Skill index

- Generate `docs/SKILL_INDEX.md` from skill frontmatter (one row per
  skill: id, name, description, `applies_to`, link). Script lives
  at `scripts/generate-skill-index.py`. Wire into `init.py` so the
  index regenerates on every build.

### 9.4 Phase 9 gate

- `python init.py --help` and every tool's `--help` succeed.
- `docs/SKILL_INDEX.md` exists and matches current skills.
- Commit `feat(help): tool --help coverage + auto-generated skill index`.
- Push.

---

## Phase 10 — Final cleanup pass

### 10.1 Repo-wide grep for `TODO`, `FIXME`, `XXX`, `HACK`

- Triage each: fix, file as issue, or convert to a "DEFERRED" with
  explicit rationale and ADR link.
- Acceptable end state: zero raw `TODO` markers; every deferral
  cites an ADR or issue number.

### 10.2 Dead-file scan

- For every Markdown file: confirm at least one other file links to
  it (or it is a top-level entry point: README, AGENTS, QUICKSTART,
  LICENSE).
- Orphans: either delete or wire in.

### 10.3 Unused-import / dead-code scan

- Run `python -m pyflakes init.py src/ tools/ scripts/ tests/`.
- Fix every warning.

### 10.4 Determinism re-check

- Re-run the Phase 1.5 determinism gate after all the Phase 5–8
  changes. Must still produce byte-identical builds.

### 10.5 Phase 10 gate

- All four checks clean.
- Full pytest green.
- Commit `chore: final cleanup pass`.
- Push.

---

## Phase 11 — Release ritual

### 11.1 Update `docs/POLICIES.md` deletion residue

- The journal noted `docs/POLICIES.md` should be deleted post-OPA
  removal. Verify it is gone. If still present, delete and confirm
  no other doc links to it.

### 11.2 Bump version markers

- Anywhere a version literal lives in the repo (e.g.,
  `__version__` in `src/__init__.py`, `version` in
  `requirements.txt` if any package metadata exists), set to
  `2.0.0`.
- **Verify:**
  ```powershell
  Get-ChildItem -Recurse -File -Include *.py,*.md,*.yml | `
    Select-String -Pattern "agent-homebase@" | `
    Where-Object { $_.Line -notmatch "2\.0\.0" }
  ```
  Empty result is pass (modulo intentional historical references).

### 11.3 Tag candidates

- Tag the release commit with all five tags from PLAN.md Phase 5:
  ```powershell
  git tag -a agent-homebase@2.0.0      -m "v2.0.0 — protocol-v1 ships complete"
  git tag -a protocol-v1               -m "Protocols frozen at v1"
  git tag -a mode-1-contract-v1        -m "Mode 1 (team) contract v1"
  git tag -a mode-2-contract-v1        -m "Mode 2 (orchestration) contract v1"
  git tag -a mode-3-contract-v1        -m "Mode 3 (choreography) contract v1"
  ```

### 11.4 Fresh-clone smoke test

- ```powershell
  $tmp = New-Item -ItemType Directory -Path (Join-Path $env:TEMP "release-smoke-$(Get-Random)")
  Push-Location $tmp
  git clone --branch agent-homebase@2.0.0 https://github.com/j78f88/agent-homebase.git .
  pip install -r requirements.txt
  python init.py --config config/project.config.example.yml
  python -m pytest tests/ -q
  python command-centre/03-mode-orchestration/reference-impl/file-queue-dispatcher/conformance_test.py
  python command-centre/04-mode-choreography/reference-impl/registry-coordinator/conformance_test.py
  Pop-Location
  ```
- All commands must succeed.

### 11.5 Push tags

- `git push origin --tags`
- Verify on GitHub releases page.

### 11.6 Repo memory refresh

- Update `/memories/repo/agent-homebase-overview.md`:
  - Replace any pre-2.0 text.
  - Note v2.0.0 shipped, schemas + reference impls live.
  - Record the five tags.

### 11.7 Phase 11 gate

- All tags pushed.
- Fresh-clone smoke test passed.
- Repo memory current.
- Commit (if anything was changed in this phase)
  `chore(release): v2.0.0`.
- Final push.

---

## Verification matrix

After Phase 11, all of the following must be true:

| Check | Command | Expected |
| --- | --- | --- |
| Tests | `python -m pytest tests/ -q` | All pass, no skips except known platform skips |
| Build (example) | `python init.py --config config/project.config.example.yml` | "0 token warnings", 0 frontmatter errors |
| Build (3 profiles) | loop over profiles | Same for each |
| Determinism | Phase 1.5 script | Identical hashes |
| Link integrity | `python scripts/check-links.py` | exit 0 |
| Strict frontmatter | strict-mode build on every config | All pass |
| Mode 2 conformance | run impl conformance | exit 0 |
| Mode 3 conformance | run impl conformance | exit 0 |
| Fresh-clone install | Phase 11.4 script | All steps pass |
| Tags present | `git tag -l "*v1*"` and `git tag -l "agent-homebase@2.0.0"` | Five tags visible |

---

## Out of scope (deliberate)

- **Adopter template repo** — PLAN.md Phase 4 promise. Defer to
  v2.1 once a second adopter exists.
- **More than one reference impl per mode** — one suffices to
  validate the contract; more is post-release iteration.
- **CI workflow updates** — existing CI runs the test suite; no
  changes required to ship v2.0.0.
- **Schemas for non-contract artifacts** (e.g., profile config) —
  validated procedurally in `init.py`; promotion to JSON Schema is
  v2.1 work.
- **Hash-chain re-sign tooling** — BPA E8 placeholder; activated
  when the first real data row exists.
- **`@migration` meta-agent** — ADR-0013 declares it opt-in; not
  built here.

---

## Failure-mode playbook

If any phase gate fails:

1. **Do not advance.** Roll back the partial commits for the
   failing phase (`git reset --soft HEAD~N`) and re-plan that phase
   only.
2. **Record the failure** in
   `docs/sprints/v2-release/incidents.md` with: phase, step,
   symptom, root cause hypothesis, fix taken.
3. **Re-run the full Verification matrix** before re-attempting the
   failed phase to confirm no collateral damage.

If a discovered issue requires breaking a `protocol-v1` contract
decision already made:

1. Stop the run.
2. Write a `BREAKING` ADR explaining why the existing decision
   cannot stand.
3. Either: amend the contract and renumber to `protocol-v2`
   (expensive — re-do Phases 3–7), or accept the limitation and
   document it as a known issue in CHANGELOG `Known issues`.
4. Resume only when the contract layer is consistent again.

---

## Commit summary at end of run

Expected commit count: ~22 (six ADRs in Phase 2, four schema
files in Phase 3, validator + tests in Phases 4 + 6, substrate
alignment in Phase 5, two reference impls in Phase 7, docs +
migration helper in Phase 8, help in Phase 9, cleanup in Phase 10,
release in Phase 11, plus the run-sheet/baseline commit at start).

Branch policy: push at every phase gate, never inside a phase.
No force-pushes. No `--no-verify`.
