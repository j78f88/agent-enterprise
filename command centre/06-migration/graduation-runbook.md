# Graduation Runbook

Step-by-step execution: graduate stable contents from `command centre/` into `delivery-modes/choreography/template/`.

This runs in **Phase 6**, after Mode 3 has been used in production against at least one registered project (proof it works).

## Pre-execution Checklist

- [ ] Phase 5 complete: at least verk-v2 successfully onboarded via Mode 3
- [ ] `sync` CLI has been used for: `register`, `deploy`, `diff`, `status`, `harvest` against real project(s)
- [ ] No outstanding spec changes (the contracts in `command centre/` reflect actual behavior)
- [ ] Operator approval to graduate

## What Graduates Where

| `command centre/` content | Destination | Rationale |
|---------------------------|-------------|-----------|
| `00-overview/three-modes.md` | `delivery-modes/README.md` (rewritten as selection guide) | User-facing now, not internal spec |
| `00-overview/architecture.md` | `docs/ARCHITECTURE.md` (replace existing) | Definitive architecture doc |
| `00-overview/glossary.md` | `docs/GLOSSARY.md` | Useful long-term |
| `01-mode-team/spec.md` | `delivery-modes/team/README.md` | Mode-specific user docs |
| `01-mode-team/install-contract.md` | `delivery-modes/team/CONTRACT.md` (or as test spec) | Test reference |
| `02-mode-orchestration/spec.md` | `delivery-modes/orchestration/README.md` | Mode-specific user docs |
| `02-mode-orchestration/install-contract.md` | `delivery-modes/orchestration/CONTRACT.md` | Test reference |
| `02-mode-orchestration/absorption-checklist.md` | `docs/CHANGELOG.md` (historical entry) | Historical record |
| `03-mode-choreography/spec.md` | `delivery-modes/choreography/README.md` | Mode-specific user docs |
| `03-mode-choreography/sync-cli-spec.md` | `delivery-modes/choreography/template/sync/README.md` | CLI docs |
| `03-mode-choreography/registry-schema.md` | `delivery-modes/choreography/template/docs/registry-schema.md` | Reference for operators |
| `03-mode-choreography/meta-agents.md` | `delivery-modes/choreography/template/.github/agents/README.md` | Co-located with agents |
| `03-mode-choreography/workspace-template.md` | `delivery-modes/choreography/docs/workspace-template.md` | Maintainer reference |
| `04-harvest/*` | `docs/harvest/<project>/` | Historical harvest records |
| `05-onboarding/*` | `docs/onboarding/<project>/` | Historical onboarding records |
| `06-migration/*` | `docs/migration/` | Historical runbooks |
| `decisions/*` | `docs/decisions/` (or `docs/adr/`) | ADR archive |

## Execution Steps

### Step 1: Branch and prep

```powershell
cd D:\VS\agent-homebase
git checkout -b graduate-command-centre
mkdir -p docs/decisions docs/migration docs/harvest docs/onboarding
```

### Step 2: Move file-by-file per the table above

Use `git mv` to preserve history:

```powershell
git mv "command centre/00-overview/glossary.md" docs/GLOSSARY.md
git mv "command centre/decisions/*" docs/decisions/
# ...etc per the table
```

For files that are rewritten (not moved as-is), copy + edit + delete original:
```powershell
Copy-Item "command centre/00-overview/three-modes.md" delivery-modes/README.md
# Edit delivery-modes/README.md to be a user-facing selection guide
git rm "command centre/00-overview/three-modes.md"
```

### Step 3: Update cross-references

Many files in `command centre/` link to each other with relative paths. After moving, those break.

```powershell
# Audit
Select-String -Pattern "command centre" -Path docs/**/*.md, delivery-modes/**/*.md
```

Update each reference to the new location.

### Step 4: Decide fate of `command centre/` folder

Options (choose one):

**A. Delete entirely.** Clean. History preserved in git.
```powershell
git rm -r "command centre/"
```

**B. Keep as historical pointer.** Leave a single README explaining the folder's lifecycle is complete.
```powershell
git rm -r "command centre/"
@"
# Command Centre (graduated)

This folder previously held the workbench for Mode 3 development.
Contents graduated to:
- delivery-modes/choreography/  (specs, template)
- docs/decisions/               (ADRs)
- docs/onboarding/              (per-project records)
- docs/migration/               (runbooks)
- docs/harvest/                 (audit reports)

See git history for the original workbench contents.
"@ | Out-File "command centre/README.md"
git add "command centre/README.md"
```

**C. Rename to `archive/command-centre/`.** Compromise.

Recommendation: **A (delete)** — history is in git, and a stale folder confuses future readers.

### Step 5: Update root README

Add the three modes prominently:

```markdown
## Three Deployment Modes

agent-homebase deploys in three modes — pick the one that matches your scale:

- **[Mode 1: Team](delivery-modes/team/)** — Drop a structured 13-agent team into one project.
- **[Mode 2: Orchestration](delivery-modes/orchestration/)** — Mode 1 + autonomous tracker-driven dispatch.
- **[Mode 3: Choreography](delivery-modes/choreography/)** — Coordinate multiple projects as a program of works.
```

### Step 6: Update existing docs

- `docs/EXTENSION_GUIDE.md` → rewrite three-repo section to reflect single-repo composition
- `docs/ADOPTION_PLAN.md` → add Mode 3 path
- `docs/MIGRATION_GUIDE.md` → add migration steps for users coming from old three-repo setup

### Step 7: Commit and PR

```powershell
git add -A
git commit -m "Graduate command centre contents to delivery-modes/ and docs/

Mode 3 is now production-ready. Specs, runbooks, and decisions
move from the workbench into permanent locations:

- delivery-modes/{team,orchestration,choreography}/  user-facing docs
- docs/decisions/                                    ADR archive
- docs/onboarding/                                   project-specific records
- docs/migration/                                    historical runbooks

Per command centre/06-migration/graduation-runbook.md"
git push origin graduate-command-centre
```

### Step 8: Tag a release

After PR merged, tag a major homebase release reflecting the new structure:

```powershell
git tag v2.0.0 -m "Three-mode delivery framework"
git push --tags
```

## Success Criteria

- [ ] All files from `command centre/` either moved (with `git mv`) or deleted with content reflected elsewhere
- [ ] No broken links in any `.md` file (run a link checker)
- [ ] Root README features the three modes prominently
- [ ] `docs/EXTENSION_GUIDE.md` reflects new model
- [ ] PR merged
- [ ] Release tagged
- [ ] No regression in any registered project (run `sync deploy --all` against test workspace)

## Rollback

If post-graduation issues surface:
1. `git revert <graduation-merge-commit>` 
2. `command centre/` returns; `delivery-modes/` reverts to pre-graduation state
3. Investigate; re-attempt graduation after fix
