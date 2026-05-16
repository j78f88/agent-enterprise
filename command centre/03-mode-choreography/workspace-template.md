# Mode 3: Workspace Template

What gets scaffolded when `delivery-modes/choreography/install.py` runs.

## Source

`delivery-modes/choreography/template/` (in homebase)

## Target

User-chosen workspace path (default: `<parent>/<homebase-name>-control`)

## Template Contents

```
template/
├── README.md.template               # Workspace README; tokens substituted at install
├── registry.yml.example             # Renamed to registry.yml on install
├── .gitignore                       # Standard Python + workspace exclusions
├── sync/                            # The sync CLI
│   ├── __init__.py
│   ├── __main__.py                  # `python -m sync ...`
│   ├── cli.py                       # argparse / click entry
│   ├── deploy.py
│   ├── diff.py
│   ├── status.py
│   ├── harvest.py
│   ├── register.py
│   ├── registry.py                  # Schema validation + IO
│   ├── homebase.py                  # Wraps Mode 1 / Mode 2 installers
│   └── reporting.py                 # Markdown report generation
├── .github/
│   └── agents/
│       ├── framework-dev/SKILL.md
│       ├── harvest/SKILL.md
│       └── audit/SKILL.md
├── reports/
│   └── .gitkeep
├── docs/
│   ├── operating-model.md
│   ├── first-project.md
│   └── harvest-workflow.md
└── pyproject.toml                   # Python deps for sync CLI
```

## Token Substitution at Install

| Token | Source | Used in |
|-------|--------|---------|
| `{{workspace.name}}` | Install prompt | README, registry, docs |
| `{{workspace.owner}}` | Install prompt or git config | README, registry |
| `{{homebase.ref}}` | Install option (`main`, tag, SHA) | registry |
| `{{homebase.location}}` | `submodule` / `vendor` / `path` | README, sync code |

## Homebase Reference Strategies

The workspace needs to find homebase at runtime. Three options selected at install:

### `submodule` (default, recommended)

```
git submodule add <homebase-url> agent-homebase
```

Pros: explicit version pinning, clean updates via `git submodule update --remote`
Cons: requires git submodule literacy

### `vendor`

Copy homebase contents into `<workspace>/agent-homebase/` as plain files (no submodule).

Pros: no submodule complexity
Cons: updates require manual re-copy; no version tracking

### `path`

Reference an existing local homebase clone via path in `registry.yml`:

```yaml
workspace:
  homebase_path: D:\VS\agent-homebase
```

Pros: dev-friendly when iterating on homebase + workspace together
Cons: not portable; breaks if path changes

## Post-Install Operator Steps

The installer prints these next steps:

```
Workspace installed at <path>

Next steps:
  1. cd <path>
  2. python -m venv .venv && .venv/Scripts/Activate.ps1
  3. pip install -e .
  4. python -m sync register <project-name> --path <project-path> --profile <profile>
  5. python -m sync deploy <project-name>
  6. Review reports/ folder for any harvest output

Read docs/first-project.md for a guided walkthrough.
```

## Template Maintenance

The template lives in homebase, so improvements to the workspace are versioned with homebase. When operators update homebase, they can re-run the workspace installer with `--upgrade-template` (future feature) to pull template improvements without losing their registry.
