# Research: Git hooks for worktree-based, multi-target build processes

**Date:** 2026-06-16
**Requested by:** maintainer (ad-hoc investigation into worktree build tooling)
**Scope:** External best practices for git hooks supporting a worktree-based, multi-target build/codegen pipeline. This repo is a build-time generator (`python init.py` → generated artifacts under `resolved/` and platform dirs); `resolved/` is never committed or hand-edited; primary dev is Windows/PowerShell. Five research clusters, cross-checked against primary sources.

> Surfaces patterns + adoption evidence + failure modes only. No recommendation — kill/keep is the maintainer's call. **Outcome of this investigation:** git hooks were investigated and deliberately NOT adopted for the build (see [CHANGELOG](../../../CHANGELOG.md) "Sprint 6 — worktree bootstrap"). CI already enforces multi-target build health and `resolved/` is gitignored, so there is nothing committed to diff against. A worktree bootstrap script (`scripts/setup-worktree.{sh,ps1}`) was added instead.

---

## Cluster 1 — Git worktree + hooks mechanics & gotchas

**Hooks are shared, not per-worktree.** The hooks dir defaults to `$GIT_DIR/hooks`, but in a *linked* worktree `git rev-parse --git-path hooks` resolves via `$GIT_COMMON_DIR` (the main `.git`). So the same hook scripts run in every worktree. `core.hooksPath` is read from the shared `.git/config`, so it too is identical across all worktrees by default. (git-scm [githooks](https://git-scm.com/docs/githooks), [git-worktree CONFIGURATION FILE](https://git-scm.com/docs/git-worktree).) Note: Git's own docs never state "hooks are shared" in one sentence — it's inferred from path-resolution rules plus corroborating blogs.

**Per-worktree config exists but is heavyweight.** `git config extensions.worktreeConfig true` enables a per-worktree config file (`.git/worktrees/<id>/config.worktree`), written via `git config --worktree`. This lets you set a per-worktree `core.hooksPath`. Introduced in git/git commit [58b284a](https://github.com/git/git/commit/58b284a2e9123588eedc8c5ee17e8b069d9454f8) (~Git 2.20, Dec 2018 — version is moderate-confidence). Caveats, all official: older Git "will refuse to access repositories with this extension" (repo-wide lockout, not graceful skip); default writes still go to shared `config`; once enabled you must manually relocate `core.bare`/`core.worktree` into the main worktree's `config.worktree` or risk corruption. Non-canonical Git implementations choke on it ([libgit2#5442](https://github.com/libgit2/libgit2/issues/5442); [Antigravity agent breakage report](https://discuss.ai.google.dev/t/antigravity-agent-breaks-on-git-worktree-repos-with-extensions-worktreeconfig/137246)).

**`git worktree add` fires `post-checkout`** (unless `--no-checkout`), with args: arg1 = null-ref (`0000…`), arg2 = new HEAD SHA, arg3 = 1 (branch flag). Post-2018 fix ([Sunshine patch](https://public-inbox.org/git/20180215191841.40848-1-sunshine@sunshineco.com/)) chdirs into the new worktree and strips `GIT_DIR`/`GIT_WORK_TREE` from the hook env. Before that, hooks ran in the wrong cwd with a misleading `GIT_DIR`.

---

## Cluster 2 — Which hooks for build/codegen pipelines

| Hook | Fires on | Can abort? | Codegen use |
|---|---|---|---|
| **pre-commit** | `git commit` (skip `--no-verify`) | Yes | Block staged generated/stale output; quick generate-and-check |
| **pre-push** | `git push` | Yes | Heavier "is generated code in sync?" before code leaves machine |
| **post-checkout** | checkout/switch, **clone, `worktree add`** | No | Regenerate on branch/worktree switch; arg3 flag=1 branch / 0 file |
| **post-merge** | `merge`/`pull` (**not on conflict**) | No | Regenerate after pulling source changes |
| **post-rewrite** | `amend`, `rebase` (**not** filter-repo/fast-import) | No | Rarely used for codegen |

Source: [githooks(5)](https://git-scm.com/docs/githooks).

- **(a) Prevent committing generated/stale output:** pre-commit check that fails if generated-output globs are staged, or runs the generator and fails on diff.
- **(b) Regenerate on switch:** post-checkout / post-merge. But post-checkout **also fires on single-file checkout (flag=0), clone, and `worktree add`** — must gate on flag=1.
- **(c) "Did you run the generator?" check:** the dominant idiom is `<run generator> && git diff --exit-code` ([git-diff docs](https://git-scm.com/docs/git-diff)). **Cross-tool consensus: this belongs in CI, not (only) a local hook**, because hooks are bypassable and not distributed. sqlc states it directly: "New developers… may forget to run `sqlc generate`… we suggest running sqlc as part of your CI/CD" ([sqlc CI/CD docs](https://github.com/sqlc-dev/sqlc/blob/main/docs/howto/ci-cd.md)).

**Real codegen repos:** sqlc (~17.9k★) ships a native `sqlc diff`/`vet`/`verify`. buf (~9–11k★) pins `buf.gen.yaml` so "every developer and CI run produces the same output" but has **no `buf generate --check`** — projects roll their own `buf generate && git diff --exit-code`. gqlgen/graphql-codegen (~10.7k★) — no `--check` flag; users requested one ([#2872](https://github.com/dotansimha/graphql-code-generator/issues/2872)). Bazel Gazelle has `-mode=diff`. Kubernetes `make verify` → `verify-codegen` copies tree, regenerates, diffs, tells you to run `hack/update-codegen.sh` — the canonical local-generate / CI-verify split.

---

## Cluster 3 — Hook managers comparison

| Tool | Lang | Install → location | Windows | Monorepo / per-path | Sets `core.hooksPath`? | Stars | Key failure mode |
|---|---|---|---|---|---|---|---|
| **pre-commit** | Python | `.git/hooks/` | Tested; needs Python | Strong file/type globs, staged-only; weak for multi-lang monorepos | **No** | ~15.3k | Stashes unstaged changes (edge-case data loss); slow first-run env builds |
| **Husky** | JS | `.husky/` | Yes; Yarn+GitBash needs `common.sh` | None built-in; relies on **lint-staged** | **Yes** (local→`.husky/_`) | ~35.2k | v9 migration breakage (no auto-shebang); GUI clients miss hooks |
| **Lefthook** | Go binary | `.git/hooks/` | Yes (winget/scoop), no runtime dep | **Strongest**: parallel, `root:`, glob filters, partial-stage | **No** — conflicts when one exists | ~8.4k | **Worktree `install` exit-128 ([#901](https://github.com/evilmartians/lefthook/issues/901))**; conflicts w/ existing hooksPath ([#1248](https://github.com/evilmartians/lefthook/issues/1248)) |
| **simple-git-hooks** | JS | `.git/hooks/` | Unspecified | None (1 cmd/hook) | **No** | ~1.7k | Manual re-run → stale hooks; 1-command limit |
| **Plain `core.hooksPath`** | Any | `git config core.hooksPath .githooks` (Git ≥2.9) | DIY; exec-bit/CRLF snags | DIY | **Yes** (by definition) | N/A | Each dev must opt in; breaks some GUI hook toggles; only one wins |

Sources: [pre-commit.com](https://pre-commit.com/), [typicode/husky](https://github.com/typicode/husky), [evilmartians/lefthook](https://github.com/evilmartians/lefthook), [simple-git-hooks](https://github.com/toplenboren/simple-git-hooks). All managers expose `--no-verify` bypass plus tool-specific skips (`SKIP=hookid`, `HUSKY=0`, `LEFTHOOK=0`, `SKIP_SIMPLE_GIT_HOOKS=1`).

**Windows/PowerShell note (relevant to this repo):** none of these use PowerShell as the hook interpreter — Git invokes hooks via its bundled sh. To run PowerShell logic you shell out to `pwsh` from an sh hook. Lefthook (static Go binary, winget-installable, no runtime dependency) has the lightest Windows footprint; pre-commit needs Python present; Husky needs Node + has the exec-bit issue (fixed in v9) and CRLF snags.

> **Repo note:** this project already uses the plain checked-in `core.hooksPath` pattern for a `.githooks/commit-msg` hook (UTF-8 BOM rejection on Windows authoring). It is opt-in per clone (`git config core.hooksPath .githooks`).

---

## Cluster 4 — Multi-target fan-out kept in sync

**Dominant pattern: a declarative manifest lists every target; one generator pass produces all of them.** The config file *is* the fan-out contract — adding a consumer = adding a target entry.
- **Style Dictionary** (~4.7k★, Amazon-origin) — one config's `platforms[]` fan tokens to CSS/Android/iOS/JS in one `build`. De-facto design-token standard; W3C DTCG format emerging.
- **buf generate** (~11.2k★) — one `buf.gen.yaml` → N language stubs; remote plugins avoid per-machine installs.
- **OpenAPI Generator** (~26.4k★, 50+ langs, 200+ named adopters incl. AWS/IBM/Kubernetes) — one spec → N SDKs.

**"Verify-not-generate in CI, generate locally" split** (same pattern as Cluster 2c): generate locally (hook), CI re-runs generator + `git diff --exit-code` as the enforcement backstop. Kubernetes `verify-codegen` is the flagship; buf and sqlc build for it.

**Selective/incremental regeneration** (only rebuild affected targets), three tiers:
- **Turborepo** (~3.8M weekly dl) — content-hash caching; `--affected` (v2.1, Aug 2024) builds changed packages + dependents (package-level granularity).
- **Nx** (~3.6M weekly dl) — `nx affected` from real TS import-graph analysis (finer granularity, fewer false positives).
- **Bazel** — hermetic action graph + content-addressed keys; affected set via `bazel query 'rdeps(//..., set(<changed files>))'` (caveat: operates on BUILD graph, not source contents).

**Determinism is the linchpin** for both the CI verify step and cache correctness — pin generator + plugin/toolchain versions so identical input yields byte-identical output everywhere.

---

## Cluster 5 — Worktree build workflows & how hooks fit

**The 2025–2026 adoption driver is AI agents running in parallel** — one worktree per agent isolates file edits. Worktree support is now built-in and default-on in Claude Code (desktop creates one per session; `--worktree` flag, `EnterWorktree` tool, `isolation: worktree` subagent frontmatter) and OpenAI Codex ("Worktree mode," ~15 managed worktrees). A third-party env-setup ecosystem exists (`claude-worktree`, `git-worktree-runner`, `worktrunk`).

**Default isolation already prevents artifact clobbering** — `dist/`, `target/`, `node_modules/`, `.venv/` live inside each worktree. Cost: disk + per-worktree dependency install (30–120s for Python venvs). Mitigations disagree: pnpm `enableGlobalVirtualStore` / CoW clone / symlinked deps (fast, but pnpm warns "do not use one writable store for mutually untrusted agents").

**Ephemeral CI loop:** `git worktree prune` → `add` → build/test → `git worktree remove`. `remove` needs `-f` for unclean, `--force` twice for locked; main worktree can't be removed. `git worktree lock`/`--lock` prevents auto-prune. Claude Code calls `git worktree lock` while an agent runs.

**How hooks break in worktrees:**
- **Relative `core.hooksPath` breaks** — resolved relative to `GIT_WORK_TREE`, which differs per worktree, so it points at a nonexistent dir in each linked worktree. Common recipe uses an absolute path: `git config core.hooksPath "$(pwd)/_hooks"` ([tnez blog](https://blog.tnez.dev/posts/supercharge-workflow-with-git-worktrees/)).
- **`.git` is a *file*, not a dir** in linked worktrees — hooks that reference `.git/` as a directory break.
- **No "post-create" worktree hook in git** — biggest real-world gap. A fresh worktree has no `.venv`/`node_modules`/`.env`, so tooling can't run. Documented cluster of ≥7 linked issues on [Claude Code #27744](https://github.com/anthropics/claude-code/issues/27744) requesting `PostWorktreeCreate`. Vendor responses: Claude Code's `.worktreeinclude` + `WorktreeCreate`/`WorktreeRemove` hooks (non-git VCS); Codex per-worktree setup scripts. Setup contexts also **lack a worktree-path env var**, making root references hard.

---

## Failure modes / gotchas (deduplicated, cross-cluster)

1. **Shared hooks run wrong-branch/wrong-dir logic.** One hook script runs in all worktrees; hardcoded paths or branch assumptions misbehave from linked worktrees. Mitigation cited: use `git rev-parse --show-toplevel` / `--git-path`, not absolute paths. (Clusters 1, 5)
2. **`post-checkout` fires far more than expected** — on file checkout (flag=0), clone, *and* `worktree add`. Heavy hooks here caused `git worktree add` to **hang indefinitely** with git-lfs 2.3.4 + Git ≥2.16.1 ([git-lfs#2848](https://github.com/git-lfs/git-lfs/issues/2848)); Microsoft's Git fork added `postCommand.strategy=worktree-change` to skip when the worktree is unchanged ([microsoft/git#813](https://github.com/microsoft/git/pull/813)). (Clusters 1, 2, 5)
3. **Non-deterministic generators → false-positive CI diffs.** The headline risk for the diff-after-generate check. Documented: OpenAPI embedded timestamps + unstable map ordering; gqlgen "almost randomly" picks `interface{}` vs `any` ([gqlgen#3414](https://github.com/99designs/gqlgen/issues/3414)). The "everyone produces same output" guarantee holds only if tool/plugin versions are pinned. (Clusters 2, 4)
4. **Hooks are bypassable (`--no-verify`) and not distributed** — not cloned with the repo, so new contributors silently lack them. This is the universal reason the sync check lives in CI. (Clusters 2, 3, 4)
5. **`git diff --exit-code` only sees tracked files** — newly generated *untracked* files won't fail the check; use `git status --porcelain` or `git add -N`. (Cluster 2)
6. **post-merge skipped on conflicts; post-rewrite skipped for filter-repo/fast-import** — regen gaps. (Cluster 2)
7. **`core.hooksPath` is mutually exclusive / manager conflicts.** Only one value wins. Husky sets it (local); lefthook conflicts when one is already set and its `install` **fails exit-128 in a worktree** ([lefthook#901](https://github.com/evilmartians/lefthook/issues/901)). pre-commit/simple-git-hooks/lefthook write to `.git/hooks/`. (Clusters 1, 3, 5)
8. **`extensions.worktreeConfig` is repo-wide and locks out old/non-canonical Git.** (Cluster 1)
9. **Manager partial-stage stash dance** (pre-commit, lint-staged) is a known edge-case data-loss source. (Cluster 3)
10. **Some Git GUIs ignore `core.hooksPath` or hide the run-hooks toggle** when it's set (JetBrains, GitKraken). (Clusters 3, 5)
11. **Partial/incomplete regeneration leaves inconsistent multi-target state** — non-atomic; a subset-only "affected" build can mask cross-target drift unless CI regenerates *all* targets. (Cluster 4)

---

## Where sources disagree

- **Commit generated artifacts vs generate-at-build-time** — genuinely contested. Check-in (Kubernetes verify model; tonic#1052) avoids forcing the toolchain on consumers and is reviewable; generate-on-build (Bazel/Nx culture; buf/gqlgen discussions) avoids staleness. No convergence. *(Note: this repo's hard rule — `resolved/` never committed — places it firmly on the generate-side, which makes the CI verify-diff pattern of Cluster 2c/4 awkward: there's nothing committed to diff against.)*
- **Affected-graph fidelity** — Nx (import-level) vs Turborepo (package/hash-level) superiority claims are opinion/benchmark blogs, not vendor-neutral.
- **Per-worktree dependency stores** — shared/symlinked (fast, disk-cheap) vs full per-worktree install (safe, slow); pnpm's "no shared writable store for untrusted agents" warning directly conflicts with the multi-agent isolation rationale.
- **Native sync-check command** — sqlc/gazelle provide one; buf/gqlgen/go-generate punt to `git diff`.
- **venv location** — inside-worktree (simple, breaks on move) vs pyenv-decoupled (robust, more setup).

---

## Open questions surfaced (and how this repo resolved them)

1. **What is being diffed, given `resolved/` is never committed?** → Nothing — the diff-after-generate pattern does not apply. The existing `session-start.sh` mtime/hash freshness check is the correct family; CI asserts the build succeeds + tokens resolve rather than diffing committed output.
2. **Per-worktree vs shared hook behavior** → No per-worktree hook divergence needed; `extensions.worktreeConfig` was removed (it was dangling).
3. **Enforcement point** → CI (`.github/workflows/ci.yml`) is the enforcement gate (builds all profiles + all editor targets + canonical tree, runs token/build-command checks + tests). No build-driving local hook added.
4. **Cross-platform interpreter** → Bootstrap shipped as paired `setup-worktree.sh` (auto-detects `python3`/`python`, forces UTF-8) and `setup-worktree.ps1`.
5. **Determinism of `init.py`** → Asserted by `scripts/smoke-test.{sh,ps1}` (builds twice, compares byte hashes).
6. **Worktree env bootstrap** → Closed by `scripts/setup-worktree.{sh,ps1}` (run after `git worktree add`), since git has no native post-worktree-create hook.

---

**Sources:** all inline above. Primary authorities: git-scm.com (githooks, git-worktree, git-config, git-diff man pages); git/git + microsoft/git + libgit2 + git-lfs issue trackers; pre-commit.com, typicode/husky, evilmartians/lefthook, toplenboren/simple-git-hooks repos; buf.build, docs.sqlc.dev, gqlgen, Bazel/Gazelle docs; Style Dictionary, OpenAPI Generator, Turborepo, Nx docs; Kubernetes `make verify`; Claude Code & OpenAI Codex worktree docs; engineering blogs (tnez.dev, Simon Willison, pnpm, Huon Wilson) and JetBrains/GitKraken issue trackers.
