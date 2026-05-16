# Absorption Runbook

Step-by-step execution: migrate `agent-orchestration` repo into `delivery-modes/orchestration/`.

## Pre-execution Checklist

- [ ] Phase 1 complete: `delivery-modes/` skeleton exists in homebase
- [ ] Backup: `agent-orchestration` repo cloned and tagged with `pre-absorption-<date>`
- [ ] No active hatice/orchestration runs in flight against verk-v2 or any other project
- [ ] Operator approval to proceed

## Execution Steps

### Step 1: Stage the move

```powershell
cd D:\VS\agent-homebase
git checkout -b absorb-agent-orchestration
mkdir -p "delivery-modes/orchestration/agents"
mkdir -p "delivery-modes/orchestration/skills"
mkdir -p "delivery-modes/orchestration/instructions"
mkdir -p "delivery-modes/orchestration/hooks"
mkdir -p "delivery-modes/orchestration/config"
mkdir -p "delivery-modes/orchestration/docs"
```

### Step 2: Copy files (preserve via copy, not move — keep source intact for verification)

Per [absorption-checklist.md](../02-mode-orchestration/absorption-checklist.md):

```powershell
$src = "D:\VS\agent-orchestration"
$dst = "D:\VS\agent-homebase\delivery-modes\orchestration"

Copy-Item "$src\agents\*"          "$dst\agents\"          -Recurse
Copy-Item "$src\skills\*"          "$dst\skills\"          -Recurse
Copy-Item "$src\instructions\*"    "$dst\instructions\"    -Recurse
Copy-Item "$src\hooks\*"           "$dst\hooks\"           -Recurse
Copy-Item "$src\config\*"          "$dst\config\"          -Recurse
Copy-Item "$src\WORKFLOW.md"       "$dst\config\WORKFLOW.md"
Copy-Item "$src\docs\*"            "$dst\docs\"            -Recurse
Copy-Item "$src\CLAUDE.md"         "$dst\docs\CLAUDE.md"
```

### Step 3: Verify copy integrity

For each copied file, confirm SHA256 match with source:

```powershell
$pairs = @(
  @("$src\hooks\onComplete.sh",       "$dst\hooks\onComplete.sh"),
  @("$src\instructions\dispatch-classification.md", "$dst\instructions\dispatch-classification.md"),
  # ... add all
)
foreach ($p in $pairs) {
  $a = (Get-FileHash $p[0] -Algorithm SHA256).Hash
  $b = (Get-FileHash $p[1] -Algorithm SHA256).Hash
  if ($a -ne $b) { Write-Error "MISMATCH: $($p[0])" }
}
```

### Step 4: Modify `afterCreate.sh` (the one breaking change)

Edit `delivery-modes/orchestration/hooks/afterCreate.sh` per the diff in [absorption-checklist.md](../02-mode-orchestration/absorption-checklist.md). Remove the `agent-orchestration` clone; source orchestration assets from `<homebase>/delivery-modes/orchestration/` instead.

### Step 5: Rewrite `delivery-modes/orchestration/docs/ARCHITECTURE.md`

Update from "three-repo composition" to "two-repo composition (homebase + project)".

### Step 6: Audit for stale path references

```powershell
cd "$dst"
Select-String -Pattern "agent-orchestration" -Path .\**\*.md, .\**\*.sh, .\**\*.yml, .\**\*.env*
```

Update each reference to point to `delivery-modes/orchestration/` (or remove if no longer relevant).

### Step 7: Smoke test before committing

Run a Linear test issue through the new layout:
1. Set up an isolated workspace (mimic what `afterCreate.sh` does, manually)
2. Confirm `@dispatcher` agent loads from `delivery-modes/orchestration/agents/`
3. Confirm tracker-adapter instructions load from `delivery-modes/orchestration/instructions/`
4. Run a dummy classification + dispatch + verify cycle

### Step 8: Commit and PR

```powershell
cd D:\VS\agent-homebase
git add delivery-modes/orchestration/
git commit -m "Absorb agent-orchestration as Mode 2

Migrates contents of standalone agent-orchestration repo into
delivery-modes/orchestration/. Updates afterCreate.sh from
three-repo to two-repo composition.

Per command centre/06-migration/absorption-runbook.md"
git push origin absorb-agent-orchestration
# Open PR; merge after review
```

### Step 9: Archive standalone repo

After PR merged and validated for ≥7 days with no issues:

1. In `agent-orchestration` repo, replace README with redirect (per absorption-checklist.md)
2. Tag final state: `git tag v-final-pre-absorption && git push --tags`
3. On GitHub: Settings → Archive this repository

### Step 10: Update downstream consumers

If any active hatice deployments reference `agent-orchestration` directly (env vars, paths), update them to point at the new location. Verk-v2's `.agent-config/profile.yml` may need a path update.

## Rollback

If Step 7 smoke test fails:
1. `git -C D:\VS\agent-homebase checkout main`
2. `git -C D:\VS\agent-homebase branch -D absorb-agent-orchestration`
3. Source repo `agent-orchestration` is unchanged (we copied, not moved); resume using it as before
4. Document failure in [rollback.md](rollback.md) with root cause

If issues surface AFTER PR merged:
1. `git revert <merge-commit>` on homebase main
2. Restore `agent-orchestration` repo from archive (un-archive on GitHub)
3. Notify any downstream consumers

## Success Criteria

- [ ] All files from `agent-orchestration` present in `delivery-modes/orchestration/`
- [ ] SHA256 matches for files copied as-is
- [ ] `afterCreate.sh` updated and functional
- [ ] No stale `agent-orchestration` path references
- [ ] Smoke test passes
- [ ] PR merged
- [ ] 7-day soak with no regressions
- [ ] Standalone repo archived with redirect
