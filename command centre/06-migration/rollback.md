# Rollback Procedures

Per-phase rollback steps if any phase fails or causes regressions.

## General Principles

- Every phase commits to its own branch before merging to `main`
- Every commit is reversible via `git revert` (no force-pushes)
- Tags mark stable points: `pre-absorption-<date>`, `pre-graduation-<date>`
- Registered projects are read-only from homebase's perspective during rollback (their `.github/agents/` may need separate revert in the project repo)

## Phase 0 (Workbench Population)

**Risk:** Low — only adds files in `command centre/`; no production impact.

**Rollback:** `git -C D:\VS\agent-homebase rm -r "command centre/"` and commit.

## Phase 1 (Create `delivery-modes/` Container)

**Risk:** Low — only adds empty folders + READMEs.

**Rollback:** `git revert <phase-1-commit>` or manual `Remove-Item delivery-modes -Recurse`.

## Phase 2 (Absorb agent-orchestration)

**Risk:** Medium — changes how Mode 2 deployments find orchestration assets.

**Symptoms of failure:**
- hatice deployments fail with "file not found" errors
- `@dispatcher` doesn't load when triggered
- verk-v2 (or other Mode 2 projects) lose dispatch capability

**Rollback:**
1. `git -C D:\VS\agent-homebase revert <phase-2-merge-commit>` and push
2. Un-archive `agent-orchestration` repo on GitHub (Settings → Archive → Unarchive)
3. Restore old `afterCreate.sh` behavior (clones three repos)
4. Notify any active hatice operators to refresh their workspace
5. Update Verk-v2's `.agent-config/profile.yml` if it was changed to reference new paths

**Recovery time:** < 30 minutes if caught within first day; longer if stale paths have propagated.

## Phase 3 (Build Mode 3)

**Risk:** Low — Mode 3 is net-new; no existing flows depend on it.

**Rollback:** `git revert <phase-3-commits>`. Mode 3 simply doesn't exist; users continue with Modes 1 and 2.

## Phase 4 (Harvest + Back-port)

**Risk:** Medium — back-ports change substrate, which affects future deploys to all projects.

**Symptoms of failure:**
- After back-port merged, `sync diff` against a project shows unexpectedly large changes
- A project's behavior changes after re-deploy (regression)

**Rollback:**
1. `git -C D:\VS\agent-homebase revert <back-port-commit>`
2. `sync deploy --all --force` to reset all projects to pre-back-port substrate
3. Each affected project may need to revert its own `.github/agents/` via `git -C <project> checkout -- .github/`
4. Document the failed back-port in `04-harvest/` with rejection reason

**Mitigation:** back-port one item at a time, deploy + validate before next.

## Phase 5 (Onboard Projects)

**Risk:** Per-project medium-high — replacing a project's hand-rolled agents.

### Verk Web onboarding rollback

If validation fails after `sync deploy verk-web`:
1. `cd D:\VS\Verk Web`
2. `git checkout -- .github/`  # reverts agent + instruction changes
3. Update registry: set `verk-web.deployed_hash: null`
4. Run Verk Web's test suite to confirm baseline restored
5. Investigate root cause; re-attempt only after fix

### verk-v2 onboarding rollback

Trivial — verk-v2 has no production code:
1. `git -C D:\VS\verk-v2 checkout -- .github/` (or delete `.github/agents/` and `.github/instructions/`)
2. Update registry: `deployed_hash: null`

### diy-project-helper onboarding rollback

Same as Verk Web.

## Phase 6 (Graduation)

**Risk:** Low-medium — moves files but doesn't change runtime behavior of deployed projects.

**Symptoms of failure:**
- Broken links in docs
- Users can't find specs they previously read in `command centre/`

**Rollback:**
1. `git -C D:\VS\agent-homebase revert <graduation-merge-commit>`
2. `command centre/` returns; `delivery-modes/` reverts
3. Fix the issue (typically a missed file move or broken link), retry graduation

## Cross-Phase: Registry Corruption

If `registry.yml` becomes invalid:
1. `cp registry.yml registry.yml.bak`
2. Restore from git: `git checkout HEAD~1 -- registry.yml`
3. Hand-merge the latest changes back in

## Documentation of Failures

Every rollback should produce an entry in this file under a "Rollback History" section:

```markdown
## Rollback History

### YYYY-MM-DD: Phase 2 absorption rollback
- **Trigger:** afterCreate.sh path resolution broke for hatice
- **Detection time:** 2 hours after merge
- **Recovery time:** 45 minutes
- **Root cause:** stale env var $AGENT_ORCH_PATH in hatice config
- **Fix applied:** [link to PR]
- **Re-attempted:** YYYY-MM-DD
```

## Rollback History

(Empty — no rollbacks yet.)
