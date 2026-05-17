# Best-Practice Alignment — Decisions Journal

> **Purpose.** Single canonical record of the *why* behind the best-practice-alignment sprint and its OPA Rego cleanup follow-through. Captures background, influences, alternatives considered, decisions made, things deliberately rejected, and the design choices that locked in. **If a future agent or owner is about to re-open a question, check here first.**
>
> **Status.** Living document. Append new rows; do not rewrite history. Date entries.
> **Sprint slug.** `best-practice-alignment`. The sprint scratch directory has been removed; this journal preserves the rationale.
> **Sprint dates.** Spec drafted 2026-05-16. Audit committed 2026-05-16. Run sheet hardened + Step 5b added 2026-05-16.

---

## 1. Context — what the repo looked like before the sprint

agent-homebase is a portable multi-agent OS: skills, instructions, and agents authored as Markdown with `{{tokens}}`, compiled by `init.py` into platform-ready artifacts under `resolved/`. It was architecturally well-differentiated (compilation step, tiered subagent contracts, write permits, OPA Rego policy layer), but two rounds of external research surfaced **5 concrete gaps vs. industry convention** that were hurting adoption surface and agent adherence.

### Locked baseline

Pre-sprint state captured in the sprint SPEC (since deleted with the sprint scratch):

| Metric | Pre-sprint |
|---|---|
| Tests | 120 passed, 14 skipped, 0 failed |
| Skills | 13 `.skill.md` (102–610 lines) |
| Resolved agents | 13 `.agent.md` (25–60 lines) |
| Resolved instructions | 24 files |
| `AGENTS.md` / `CLAUDE.md` / `references/` / `.cursor/rules/` | None existed |
| Anti-rationalization tables | 0 / 13 skills |
| Red Flags + Verification sections | 0 / 13 skills |
| Honesty contract | Did not exist |
| Path-scoped frontmatter in resolved output | Not emitted |

The 5 gaps that drove the sprint:

1. No `AGENTS.md` at repo root (industry convention across Claude Code, Copilot, Codex).
2. No `CLAUDE.md` (Claude Code's auto-loaded entry point).
3. No honesty / anti-sycophancy / anti-hallucination contract.
4. No anti-rationalization tables on skills (addyosmani/agent-skills pattern, 41.9k★).
5. No Red Flags + Verification gates on skills (same source).

---

## 2. Influences — what was read and what each contributed

| Source | Stars / type | Contributed |
|---|---|---|
| addyosmani/agent-skills | 41.9k★ repo | Anti-rationalization tables, Red Flags + Verification sections, progressive-disclosure `references/` folder, lifecycle slash commands, session-start hook |
| agentsmd/agents.md | 21.4k★ doc | `AGENTS.md` shape + conventions |
| awesome-cursorrules | 39.5k★ repo | Anti-sycophancy / honesty contract pattern; Cursor `.mdc` ecosystem footprint |
| multica | 28.7k★ repo | General agent-OS patterns |
| iterate | 169★ repo | Sprint-loop patterns |
| evlog | 1.3k★ repo | Structured rejection fields (`Fix`, `Link`); hash-chain signing pattern |
| Claude Code docs | Official | `CLAUDE.md` auto-load, `paths:` frontmatter, native hooks |
| GitHub Copilot docs | Official | `applyTo:` frontmatter, `.github/copilot-instructions.md` |
| OpenAI Codex `AGENTS.md` | Official | `AGENTS.md` precedence model |
| cursor.directory | Catalog | Cursor `.mdc` + `globs:` frontmatter |

All citations were also captured in the sprint's ADOPTION_PLAN under "Sources" (sprint scratch since deleted).

---

## 3. Goals (locked)

1. Close the 5 gaps above.
2. Add progressive-disclosure infrastructure (`references/`) to reduce skill token weight.
3. Strengthen handoff-rejection actionability via structured-error fields (evlog).
4. Enable multi-platform reach (Cursor `.mdc`, path-scoped frontmatter, lifecycle commands).
5. Validate the OPA Rego investment with concrete data.

Non-goal: application-code changes. The sprint touches Markdown skills/instructions and `init.py` only.

---

## 4. Decisions — settled (do not re-open without a written reason)

### 4.1 Open decisions from the spec — final resolutions

| # | Question | Options considered | **Chosen** | Why | Status |
|---|---|---|---|---|---|
| D1 | Policy audit timing | A: before Phase 1 / B: parallel / C: defer | **B** | Read-only, doesn't block other work. | Done — audit landed alongside other phases. |
| D2 | Lifecycle slash commands | A: ship as sugar over `@agent` invocations / B: skip | **A** | Low cost, familiar UX. Agents remain canonical; prompts are thin wrappers. | Done — 5 prompts under `prompts/`. |
| D3 | Audit signing strategy | A: HMAC / B: hash-chain / C: defer to git | **B** | Fits existing `FILE_HASHES.md` model; no shared-secret management. | Done — `scripts/verify-hash-chain.py` ships. |
| D4 | Cursor editor target naming | A: add `cursor` + `all` / B: only `all` / C: defer | **A** | Explicit is better; `all` for fan-out, `cursor` for surgical. | Done — added to `VALID_EDITOR_TARGETS`. |
| D5 | `when_to_use` vs `description` consolidation | A: merge into `description` / B: keep both | **B** | Keep both — superset is fine. Revisit only if a platform forces the choice. | Deferred — not re-opening this sprint. |

### 4.2 Decisions added during execution

| # | Question | **Chosen** | Why |
|---|---|---|---|
| D6 | Where does the OPA Rego layer end up? | **Drop it. Port the high-value composition rules to a small Python validator (`tools/sprint_lint.py`).** | The audit found zero real-world catches, ~80% overlap with `init.py`'s `SecurityValidator`, silently-skipping tests, and high false-positive risk in the unique Rego-only rules. |
| D7 | Sequence the OPA cleanup as part of the sprint or as a follow-on PR? | **Follow-on PR (Step 5b), owner-choice ordering vs Step 6.** | The audit explicitly scoped the file-removal as out-of-scope; mixing it into the sprint branch would have made the green-build gate ambiguous. |
| D8 | `applyTo` scope on the run sheet itself | **`docs/sprints/best-practice-alignment/**`** | I1 Option B during the run-sheet hardening review. Narrow scope avoids the run sheet auto-attaching to unrelated work. |
| D9 | Do we re-sign `FILE_HASHES.md` when removing the `policies/*.rego` reference? | **No.** | The file is currently a template with zero data rows; the reference lives in an HTML comment about *categories*, not in the chain. No re-sign procedure exists in `verify-hash-chain.py` either — verify-only by design. |
| D10 | Allow-list shape for the cleanup leak grep | **Exclude `.git/`, `resolved/`, `docs/POLICY_AUDIT.md`, and `docs/sprints/best-practice-alignment/**`.** | The sprint scratch dir is protected by the no-delete rule and references OPA Rego extensively; without the exclusion, the leak grep `throw`s and blocks the commit. |
| D11 | Run-sheet verify blocks — fail-fast strictness | **`$ErrorActionPreference='Stop'` + `$LASTEXITCODE` check after every `python` call, plus `throw` on regression.** | Earlier draft only ran the commands; failures were silent. O1 from the review. |
| D12 | Approval gates between steps | **Explicit ⛔ blocks after every step (1→2, 2→3, 3→4, 4→5, 5→5b/6, 5b→6).** | Forces the owner-in-the-loop pattern declared in the spec. I2 from the review. |

### 4.3 Decisions reaffirmed (not changed by the sprint)

| # | Question | Standing answer | Why we did not revisit |
|---|---|---|---|
| R1 | Should `resolved/` be source-controlled? | **No — it is build output, regenerated by `init.py`.** | Already enforced by [AGENTS.md](../../AGENTS.md) and [CLAUDE.md](../../CLAUDE.md). |
| R2 | Where do `policies/`, `skills/`, `schemas/` etc. live in three-mode topology? | **At repo root as "shared substrate".** | Settled in [command-centre/decisions/0002-protocols-as-shared-root.md](../../command-centre/decisions/0002-protocols-as-shared-root.md) (substrate-at-root rule). |
| R3 | Are skills loaded into context unconditionally? | **No — on-demand.** | Why ~35-line growth per skill (rationalizations + red flags + verification) is acceptable. |

---

## 5. Eliminations — things we considered and deliberately rejected

> **Do not re-propose any of these without a written reason that addresses the cited rationale.**

| # | Rejected option | Reason for rejection |
|---|---|---|
| E1 | Keep the OPA Rego layer and wire it into CI | Zero real-world catches over the life of the repo; OPA binary not installed on any dev box or CI runner; tests silently skip when OPA is absent, which is *worse than no guardrail*. |
| E2 | Keep `security.rego` even after dropping `composition.rego` | ~80% overlap with `init.py`'s `SecurityValidator`; the unique Rego-only rules (broad secret regex, password regex) are high false-positive. |
| E3 | Replace OPA Rego with another policy engine (Cedar, etc.) | Adds back the external-binary dependency that was the core problem; no evidence the existing rules needed an engine at all. |
| E4 | Stub out `docs/POLICIES.md` to a one-liner instead of deleting it | A stub would mislead — the doc describes an entire workflow that no longer exists. The audit (since deleted with this cleanup) superseded it. |
| E5 | Merge `when_to_use` into `description` on every skill (D5 option A) | No platform forces this today; consolidating now means a forced re-author later if either field drifts. Defer until a platform forces the choice. |
| E6 | Apply the run sheet `applyTo` to the whole workspace (`**/*`) | Would auto-attach the run sheet's verify blocks to unrelated edits; high noise. Chose narrow scope (D8). |
| E7 | Use `git stash` in the cleanup pre-flight to hide unrelated dirty files | Real risk of conflicts on `git stash pop` given other ongoing edits in the tree; cleaner to require a clean tree and stop-and-ask if it isn't. (S1 from review.) |
| E8 | Add `--re-sign` to `scripts/verify-hash-chain.py` as part of the cleanup | `FILE_HASHES.md` has no chained data rows yet; re-signing is a no-op. The audit's removal target is in an HTML comment outside the chain. Build the re-sign tool when the first real data row exists. |
| E9 | Squash the three OPA-cleanup commits into one | Each commit has a distinct semantic (port → delete → docs); separate commits keep `git bisect` useful and the leak grep auditable. |
| E10 | Delete the sprint scratch directory automatically when QA goes green | Explicit owner rule — manual deletion only. Codified at the top of the run sheet and in QA.md (sprint scratch since deleted). |
| E11 | Use `Select-String -Path . -Pattern … -Recurse` for the cleanup leak grep | `Select-String -Recurse` against `.` is unreliable in PowerShell — `-Recurse` wants a directory but `-Path` with patterns is ambiguous. Switched to `Get-ChildItem -Recurse -File -Include … \| Select-String`. |
| E12 | Roll the OPA cleanup into the sprint branch | Mixes two narratives (best-practice alignment vs. dead-code removal) and makes Step 6's pass/fail signal ambiguous. Separate PR (D7). |

---

## 6. Architecture / design choices that shaped the outcome

1. **All new sections are additive on skills.** Common Rationalizations + Red Flags + Verification append at the bottom of each `.skill.md`. Nothing existing was removed → zero breakage risk on the existing skill body.
2. **Honesty contract is a *generic* instruction, not configurable.** Identical text for every adopter; no `{{tokens}}` to resolve; auto-discovered by the existing `generic_src` glob in `init.py`. No code change required to deploy it.
3. **`references/` are pulled by link, not inlined.** Skills reference them with a path; the content stays in one place and skills stay light. Progressive disclosure.
4. **Path-scoped frontmatter is emitted per-platform from a single `scope:` field.** One source of truth in the instruction file; `init.py` translates to `paths:`, `applyTo:`, or `globs:` based on `editor.target`.
5. **`cursor` and `all` are explicit editor targets.** Not implicit "do-everything"; the spec required `SecurityValidator.validate_config()` to accept them without false positives.
6. **Hash-chain signing for `FILE_HASHES.md` was preferred over HMAC.** No shared-secret management, fits an evlog-style append-only model, validation is pure-Python (`scripts/verify-hash-chain.py`).
7. **The run sheet enforces owner-in-the-loop after every step.** Approval gates are blocking, not advisory. Re-run cleanup (`Remove-Item -Recurse -Force resolved/*`) is gated to *retries only*.
8. **Step 5b (OPA cleanup) is optional and the owner picks the ordering.** Three viable orderings — 5 → 5b → 6, 5 → 6 → 5b, or 5 → 6 and defer 5b — are explicitly enumerated in the run sheet.
9. **Composition rules survive in Python, not Rego.** All 9 rules (PRIORITY_ORDER, SCORE_ORDER, FEATURE_BALANCE×2, CAPACITY_EXCEEDED, CAPACITY_HIGH, BUG_POLICY, DEBT_PRESSURE, AGE_ESCALATION, ITEM_COUNT) port to `tools/sprint_lint.py` with identical message prefixes so existing references stay valid.

---

## 7. Work-package summary (what was done, where it lives now)

| WP | Focus | Survives sprint cleanup as |
|---|---|---|
| 01-scaffolding | `AGENTS.md`, `CLAUDE.md`, `references/`, `EXTENSION_GUIDE.md` skill template, honesty contract | Root `AGENTS.md` + `CLAUDE.md`; `references/*.md`; `instructions/generic/honesty-contract.instructions.md`; appended section in `docs/EXTENSION_GUIDE.md` |
| 02-skills | Common Rationalizations + Red Flags + Verification on all 13 skills | The 13 `.skill.md` files |
| 03-formats | Structured rejection fields (Fix, Link) + hash-chain signing | `instructions/configurable/handoff-rejection-format.instructions.md`; `starters/FILE_HASHES.md`; `scripts/verify-hash-chain.py`; `tests/test_hash_chain.py` |
| 04-platform | `cursor`/`all` targets, path-scoped frontmatter, lifecycle prompts, session-start hook | `init.py` changes + tests; `config/project.config.example.yml`; `config/plugin.json`; `prompts/*.prompt.md`; `hooks/session-start.sh` + `hooks/hooks.json` |
| 05-audit | OPA Rego pressure-test → recommendation | (audit doc since deleted; findings summarised in §8 below) |
| 05b-cleanup (optional) | Execute the audit recommendation | `tools/sprint_lint.py` + `tests/test_sprint_lint.py`; deletions of `policies/`, `src/phase1_verification/policy_engine.py`, `docs/POLICIES.md`; documentation prunes across ~10 files |

The deliverables above remain permanently in the repo. The sprint scratch directory and its manual cleanup checklist (QA.md) have been removed.

---

## 8. OPA Rego audit — the decision in one place

**Question.** Is the OPA Rego policy layer (`policies/composition.rego`, `policies/security.rego`, `src/phase1_verification/policy_engine.py`) earning its keep?

**Method.** Inventoried every invocation site, walked git history for caught violations, ran overlap analysis against `init.py`'s `SecurityValidator`, estimated false-positive risk on the unique rules. The full audit document (`docs/POLICY_AUDIT.md`) has since been deleted; its findings are summarised below.

**Findings.**
- **Invocations:** 0 in CI, 0 in hooks, 0 in `init.py`, 0 in app code outside tests. Tests *skip* unless OPA is installed — and OPA is on no dev box or CI runner in this repo.
- **Violations caught:** 0 observed, ever.
- **Overlap:** ~80% of `security.rego` is already enforced unconditionally by `init.py`'s `SecurityValidator` (command whitelist, dangerous patterns, path traversal).
- **Unique Rego-only rules:** broad secret regex (`[A-Za-z0-9_\-]{32,}`) matches commit SHAs / UUIDs / base64 fragments → high false-positive; password regex similarly weak; escalation warning is soft.
- **Composition rules** (priority/score order, 50–80% feature mix, capacity ≤100%, P0 bug inclusion, debt pressure, age, item count) are reasonable but **have no caller**.

**Decision (D6 + D7).** Drop the OPA layer. Port the 9 composition rules to `tools/sprint_lint.py` with identical message prefixes. Executed as a separate, owner-approved PR (Step 5b work package, sprint scratch since deleted).

**What gets deleted.** `policies/composition.rego`, `policies/security.rego`, `policies/` (empty after), `src/phase1_verification/policy_engine.py`, `docs/POLICIES.md`. Plus the `TestPolicyEngine` class and one import line in `tests/test_contracts.py`, and one re-export line in `src/phase1_verification/__init__.py`.

**What changes in docs.** Ten files pruned: `AGENTS.md`, `README.md`, `tests/README.md`, `docs/CONTRIBUTING.md`, three v1 files under the (now retired) `command centre/` workbench, `docs/DUAL_PLATFORM_PLAN.md`, `starters/FILE_HASHES.md` (comment-block bullet only — no chain re-sign needed), `instructions/configurable/security-audit.instructions.md`.

**Expected test-count delta.** Removing the silently-skipping `TestPolicyEngine` suite reduces the *skipped* count. The pre-/post-cleanup `X passed, Y skipped` lines must be recorded in commit 3's message; if `QA.md` hard-codes a criterion-9 baseline, it gets updated in the same commit.

**Stop-and-ask triggers.** Any `PolicyEngine` reference surfacing outside the allow-list during commit 2's leak grep; any unrelated dirty file in the working tree at pre-flight; hash-chain validation failing (would indicate someone has chained data rows since this journal was written).

---

## 9. Run-sheet design choices (and what got rejected during review)

Two review passes hardened the sprint run sheet (sprint scratch since deleted):

| Code | Issue | Resolution |
|---|---|---|
| E1 | Step 1 listed Creates but not Edits | Added explicit Edits list (4 skill files + EXTENSION_GUIDE) |
| E2 | Verify checks used `=` not `≥`, baseline blank | Switched to `≥` bounds; baseline pre-filled placeholders |
| E3 | Step 4 didn't verify the `VALID_EDITOR_TARGETS` / `.cursor/rules/` / prompt-filename details it claimed | Added concrete checks |
| E4 | Step 1 didn't confirm `resolved/` output | Added `Test-Path resolved/...` assertions |
| O1 | Verify blocks not fail-fast | `$ErrorActionPreference='Stop'` + `$LASTEXITCODE` checks after every `python` call (D11) |
| O2 | No re-run cleanup guidance | Added top-of-file rule: `Remove-Item -Recurse -Force resolved/*` on retries only |
| O3 | Step 4 precondition gap | Added explicit "tests before init.py changes" rule |
| O4 | Step 6 referenced QA.md without inlining the 10 criteria | Inlined criteria so the orchestrator doesn't have to context-switch |
| I1 | `applyTo` was workspace-wide | Narrowed to `docs/sprints/best-practice-alignment/**` (D8) + scope note added |
| I2 | No approval gates | Added ⛔ gates between every step (D12) |
| I3 | No audit trail | Added `git log --oneline -1` after each step |
| I4 | Step 1.7 looked like drift (skill template references sections that don't exist yet) | Added forward-looking note explaining the template lands before the sections do |

Second pass added Step 5b. Two of the seven cleanup-prompt defects that drove Step 5b's shape:

- **B1.** Earlier draft of the cleanup handoff cited a nonexistent `scripts/verify-hash-chain.py --help` re-sign procedure. Step 5b instead documents D9 (no re-sign needed, file is template-only) and points at the actual verify command.
- **B4.** Earlier draft's leak grep would have caught the sprint scratch dir (protected from deletion) and `throw`n. Step 5b uses the D10 allow-list.

---

## 10. Risks tracked (and how they were mitigated)

| Risk | Mitigation in place |
|---|---|
| Anti-rationalization tables age into noise | Documented in spec — quarterly review, rotate examples |
| Path-scoped frontmatter breaks `init.py` | Tests-before-code rule on Step 4; existing tests gate regression |
| `.cursor/rules/` adds maintenance | Fully auto-generated; no manual upkeep |
| Lifecycle commands overlap with `@agent` invocations | Prompts are thin wrappers; agents remain canonical (D2) |
| Hash-chain workflow complexity | `verify-hash-chain.py` automates; chain is empty until first data row, so cost is zero today |
| Cleanup PR regresses test count | Pre/post pytest numbers required in commit 3 message; QA.md baseline updated in the same commit |
| Cleanup PR leaves stale `policies/` references | D10 allow-list leak grep + `throw` on commit 3 |
| Re-running a failed step picks up stale `resolved/` | Top-of-run-sheet rule: `Remove-Item -Recurse -Force resolved/*` on retry only |

---

## 11. Pointers (for the next person)

- **Sprint scratch, run sheet, audit, spec, adoption plan, QA, and 05b cleanup work package**: deleted with the sprint scratch directory. This journal is the surviving record.
- **Standing repo conventions referenced here**: [AGENTS.md](../../AGENTS.md), [CLAUDE.md](../../CLAUDE.md), [command-centre/decisions/0002-protocols-as-shared-root.md](../../command-centre/decisions/0002-protocols-as-shared-root.md)
- **Three-mode architecture rationale** (origin, errors, alternatives eliminated): [command-centre/00-overview/design-history.md](../../command-centre/00-overview/design-history.md) — BPA assumes the substrate-at-root shape settled there; read it for the *why* behind the directory layout this journal patches.

---

## 12. Change log for this journal

| Date | Change | By |
|---|---|---|
| 2026-05-16 | Initial consolidation after Step 5 (audit) committed and Step 5b inserted into the run sheet. | sprint owner via assistant |
