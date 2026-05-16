# Mode 3: sync CLI Spec

The `sync` CLI is the primary user interface for Mode 3. It operates on the workspace's `registry.yml` and the bundled agent-homebase submodule.

## Global Options

| Flag | Description |
|------|-------------|
| `--registry <path>` | Override registry path. Default: `./registry.yml` |
| `--homebase <path>` | Override homebase path. Default: `./agent-homebase` |
| `--verbose` | Verbose logging |
| `--json` | Machine-readable JSON output |

## Commands

### `sync register`

Add a project to the registry.

```
sync register <name> --path <path> --profile <name-or-path> [--mode team|orchestration] [--tracker <type>] [--workspace <id>]
```

| Flag | Required | Description |
|------|----------|-------------|
| `<name>` | Yes | Short identifier (e.g. `verk-web`) |
| `--path` | Yes | Local path or git URL of the project |
| `--profile` | Yes | Profile name (resolves in `agent-homebase/profiles/`) or path to YAML |
| `--mode` | No | `team` (default) or `orchestration` |
| `--tracker` | If mode=orchestration | Tracker type |
| `--workspace` | If mode=orchestration | Tracker workspace ID |

Effect: appends entry to `registry.yml` with `deployed_hash: null`.

### `sync deploy`

Install homebase into a registered project.

```
sync deploy <name> [--force] [--no-starters]
sync deploy --all [--force]
```

Behavior:
1. Looks up project in `registry.yml`
2. Resolves mode → calls Mode 1 or Mode 2 installer with project's profile + path
3. On success, updates `deployed_hash` to current homebase git SHA
4. Writes a deploy log entry to `reports/deploy-log.md`

| Flag | Description |
|------|-------------|
| `--force` | Deploy even if `deployed_hash` matches current homebase SHA |
| `--no-starters` | Skip starter file seeding |

### `sync diff`

Dry-run deploy. Show what would change without writing.

```
sync diff <name>
sync diff --all
```

Output: per-file additions, modifications, deletions. Highlights any project-local files that would be overwritten.

### `sync status`

Show deployed-vs-current homebase version per project.

```
sync status
```

Output:
```
Project              Mode             Deployed       Current        Drift
verk-web             team             abc1234 (5d)   def5678        2 commits behind
verk-v2              orchestration    def5678 (now)  def5678        up to date
diy-project-helper   team             —              def5678        not deployed
```

### `sync harvest`

Diff a project's `.github/agents/` and `.github/instructions/` against homebase substrate. Generate a back-port candidates report.

```
sync harvest <name> [--output <path>]
```

Behavior:
1. Reads project's `.github/agents/` and `.github/instructions/`
2. For each file, locates the corresponding substrate source (skill, instruction, or "no match" = project-original)
3. Diffs and classifies:
   - **Identical**: ignored
   - **Substituted-only**: differences explainable by token substitution; ignored
   - **Genuine divergence**: project has modified the resolved output post-deploy
   - **Project-original**: project file with no substrate counterpart
4. Writes report to `reports/harvest-<name>-<date>.md` with sections:
   - Genuine divergences (candidates for back-port)
   - Project-originals (candidates for promotion to substrate or `delivery-modes/extensions/`)
   - Identical / token-substituted (info only)

### `sync unregister`

Remove a project from the registry. Does NOT touch the project's filesystem.

```
sync unregister <name>
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Generic error |
| 2 | Project not in registry |
| 3 | Project path missing or unreadable |
| 4 | Homebase substrate missing/corrupt |
| 5 | Write failure |
| 6 | Drift detected and `--force` not supplied (deploy only) |

## Output Format

All commands support `--json` for machine consumption. Default is human-readable tables/summaries.

## Idempotency Guarantees

- `sync deploy` is safe to re-run; updates marker version, leaves project-local files alone
- `sync register` errors if name already exists
- `sync harvest` is read-only on the project; only writes to `reports/`
- `sync diff` writes nothing
