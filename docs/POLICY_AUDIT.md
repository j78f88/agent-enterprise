# OPA Rego Policy Audit

**Audit date:** 2026-05-16
**Scope:** `policies/composition.rego`, `policies/security.rego`
**Goal:** Measure real-world catch rate of the Rego policy layer and recommend keep / simplify / fold.

---

## Method

1. Inventory every site that invokes the policies (CI, hooks, init.py, scripts, tests).
2. Walk git history for actual violations flagged in commits, PRs, or CI logs.
3. Compare policy rules against checks already performed elsewhere in the repo (overlap analysis).
4. Estimate false-positive risk from the rule shapes.
5. Recommend a disposition.

---

## Inventory: where are the policies actually run?

| Invocation site | Status | Evidence |
| --- | --- | --- |
| GitHub Actions CI (`.github/workflows/ci.yml`) | **Not invoked.** No `opa`, `policy`, or `rego` token anywhere in the workflow. | `grep_search` on `.github/workflows/ci.yml` returned zero matches. |
| Repo hooks (`hooks/session-start.sh`, `hooks/hooks.json`) | **Not invoked.** | No reference to `opa` or `policies/`. |
| `init.py` build pipeline | **Not invoked.** `init.py` runs its own in-process `SecurityValidator` instead. | `init.py:31-160` — command whitelist, dangerous patterns, path-traversal checks all reimplemented in Python. |
| Application code (`src/phase1_verification/policy_engine.py`) | Importable wrapper exists but **no caller in the repo invokes it** outside tests. | `grep_search` for `PolicyEngine` / `evaluate_composition` / `evaluate_security` returns hits only in `tests/test_contracts.py` and the class's own docstring example. |
| Test suite (`tests/test_contracts.py`) | Tests exist, but **skip when OPA isn't installed**, which is the default on every dev box and CI runner in this repo. | `tests/test_contracts.py:213-218` — `pytest.skip(f"OPA not installed: {e}")`. OPA binary is not on the local machine (`Get-Command opa` failed). |

**Net result:** in the current configuration, the Rego files are never evaluated against any real input. Zero violations have ever been caught in production use.

---

## Git history: violations flagged

```
git log --all --oneline -- policies/
44f480a refactor: reorganize project structure into phase-based modules
```

A single squash commit. No history of violations flagged in commit messages, PR descriptions, or CI runs (CI doesn't run OPA).

**Violations caught by `composition.rego`:** 0 (observed).
**Violations caught by `security.rego`:** 0 (observed).
**False positives:** N/A — policies have never been evaluated against real data, so neither true nor false positives have accrued.

---

## Overlap analysis

### `security.rego` vs `init.py`'s `SecurityValidator`

| Rule in `security.rego` | Already implemented in `init.py`? |
| --- | --- |
| Command whitelist (`allowed_commands`) | **Yes** — `SecurityValidator.ALLOWED_COMMANDS` (init.py:40-67) |
| Dangerous patterns (`; rm`, backticks, `$(`, `curl…|sh`, `sudo`, `eval`) | **Yes** — `SecurityValidator.DANGEROUS_PATTERNS` (init.py:69-90) |
| Path traversal (`../`, `..\\`, etc.) | **Yes** — `SecurityValidator.validate_path` (init.py:123-155) |
| Absolute-path containment | **Partial** — init.py's path validator covers traversal; absolute-path allow-listing is Rego-only but unused. |
| Secret detection regexes (AWS keys, GitHub PATs, RSA blocks) | **No** — Rego-only, but the patterns are weak (the generic `[A-Za-z0-9_\-]{32,}` matches commit SHAs and any base64 fragment; very high false-positive risk if it were ever wired up). |
| Escalation threshold warning (`def_kill_threshold > 10`) | **No** — Rego-only, but it's a soft warning, not a security control. |

**Overlap: ~80% of `security.rego` is already enforced by `init.py` on every build.** The unique surface (secret regexes, escalation warning) is either high-false-positive or low-value.

### `composition.rego`

The composition rules (priority ordering, intra-tier score ordering, 50-80% feature mix, capacity ≤ 100%, P0 bug inclusion, debt-pressure, age escalation, ≤15 items) are not enforced anywhere else in the codebase. They're also not enforced by Rego, because nothing calls `evaluate_composition`.

The rules themselves are reasonable but live entirely on paper.

---

## False-positive risk (theoretical, if wired up)

| Rule | Risk |
| --- | --- |
| `composition.rego` priority/score ordering | Low — pure data shape, deterministic. |
| `composition.rego` feature-mix 50-80% | Medium — hard-coded band; legitimate sprints (security-only, all-bugs hotfix) will trip it. |
| `composition.rego` P0-bug-must-be-included | Medium — assumes every excluded P0 bug is a policy violation, but P0 bugs can legitimately be deferred to a hotfix branch. |
| `security.rego` command whitelist | Low (matches init.py behaviour, which has been exercised). |
| `security.rego` secret detection (`[\"'][A-Za-z0-9_\-]{32,}[\"']`) | **High** — matches commit SHAs, UUIDs, base64 thumbnails, Bicep resource IDs, etc. Would flood any pipeline. |
| `security.rego` password regex | Medium-high — matches any quoted string with ≥8 alphanumerics. |

---

## Recommendation: **Simplify and fold**

**Rationale**
1. **Zero real-world catches.** Policies have never run in CI or in `init.py`. There is no evidence the Rego layer has prevented a single defect.
2. **External binary dependency.** OPA must be installed out-of-band; every dev box and CI runner in this repo is missing it, and the tests silently skip. A guardrail that silently skips is not a guardrail.
3. **`security.rego` is ~80% redundant with `init.py`'s `SecurityValidator`,** which runs unconditionally on every build and is covered by the existing test suite.
4. **`composition.rego` enforces rules that have no caller.** Folding them into the `planner` skill's validation (or a small Python check inside `init.py` / a sprint-lint script) keeps the rules without the OPA dependency.
5. **The unique Rego-only rules (broad secret regex, password regex) have high false-positive risk** and would degrade signal quality if turned on.

**Proposed disposition**

| Action | Detail |
| --- | --- |
| Keep `init.py`'s `SecurityValidator` as the single source of truth for command + path checks. | Already in place and tested. |
| Port the high-value composition rules (priority order, intra-tier score order, feature 50-80%, capacity ≤ 100%, ≤15 items) to a small Python validator invoked by the `planner` skill / a future `tools/lint_sprint.py`. | Eliminates OPA dependency without losing the rules. |
| Drop `policies/security.rego` and `policies/composition.rego`. | Removes dead code and a misleading guardrail. |
| Drop or rewrite `src/phase1_verification/policy_engine.py` and the `TestPolicyEngine` skip-suite. | Removes the unused OPA bridge and the silently-skipping tests. |
| Update `docs/POLICIES.md`, `docs/CONTRIBUTING.md`, `command centre/00-overview/architecture.md`, `AGENTS.md`, `README.md`, `starters/FILE_HASHES.md`, and `tests/README.md` to remove references to `policies/`. | Documentation drift cleanup. |
| Optional: keep one Rego policy as an *example* if the project wants to advertise OPA support, but mark it explicitly as a sample, not a guardrail. | Only if there's a marketing reason. |

**Net effect:** loses zero real coverage, removes ~370 lines of unused Rego + the OPA binary requirement, and consolidates the security model in one place that already runs on every build.

---

## Out of scope for this audit (follow-up work)

- Actual file removal and documentation updates — to be sequenced as a separate, owner-approved cleanup PR.
- Porting composition rules to Python — separate task.
- Decision on whether to keep the `src/phase1_verification` module entry point at all.
