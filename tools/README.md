# tools/

Developer CLI utilities for authoring and maintenance. Distinct from
`scripts/` which contains CI and verification scripts.

## Utilities

| Script | Purpose |
| --- | --- |
| `migrate-frontmatter.py` | Migrate skill/instruction YAML frontmatter between schema versions |
| `sprint_lint.py` | Validate sprint plan structure and completeness |

Run from the repository root:

```bash
python tools/migrate-frontmatter.py <path>
python tools/sprint_lint.py <plan-file>
```
