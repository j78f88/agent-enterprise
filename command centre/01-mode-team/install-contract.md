# Mode 1: Team — Install Contract

Formal contract that `delivery-modes/team/install.py` must satisfy. Used as the basis for tests.

## CLI

```
install.py --target <path> --profile <path> [--editor vscode|claude|both] [--no-starters] [--dry-run]
```

| Flag | Required | Description |
|------|----------|-------------|
| `--target` | Yes | Absolute or relative path to the target project repo |
| `--profile` | Yes | Path to project profile YAML |
| `--editor` | No | Editor target. Default `vscode`. Affects file naming conventions |
| `--no-starters` | No | Skip seeding starter planning files |
| `--dry-run` | No | Print what would change; write nothing |

## Preconditions

| Check | Failure mode |
|-------|--------------|
| Target path exists and is a directory | Exit 2, message |
| Target path is a git repo (has `.git/`) | Warn, proceed |
| Profile file exists and is valid YAML | Exit 3, message |
| Profile schema validates | Exit 3, message with schema errors |
| Substrate (`skills/`, `instructions/`) exists | Exit 4, "homebase appears corrupt" |

## Postconditions

| Guarantee | Verified by |
|-----------|-------------|
| `<target>/.github/agents/<skill>/SKILL.md` exists for all 13 skills | File existence check per skill |
| `<target>/.github/instructions/*.md` exists for all 24 instructions | File existence check |
| `<target>/.github/agents/.homebase-mode` contains `mode: team` and current homebase git SHA | YAML parse check |
| Starter files seeded only where target file did not previously exist | Compare mtimes / hashes |
| All `{{tokens}}` in output are substituted (none remain) | Grep for `{{` in output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Generic error |
| 2 | Target path invalid |
| 3 | Profile invalid |
| 4 | Homebase substrate missing/corrupt |
| 5 | Write failure (permissions, disk) |

## Output Format

Stdout (human-readable summary):
```
Mode 1 (Team) install complete
  Target:   /path/to/project
  Profile:  profiles/react-web-app.config.yml
  Version:  homebase@abc1234
  Wrote:    13 skills, 24 instructions, 7 starters (3 skipped — already present)
```

With `--dry-run`, the same summary is printed but no files are written.

## Test Plan

| Test | Expected |
|------|----------|
| Install on empty target | All postconditions met |
| Install on target with existing starters | Starters not overwritten; skills/instructions overwritten |
| Install with missing profile | Exit 3 |
| Install with invalid YAML in profile | Exit 3 with schema errors |
| Install with `--dry-run` | No files modified; summary printed |
| Re-install (idempotency) | Same output; only marker version changes if homebase moved |
