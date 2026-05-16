# Quickstart

Get a working agent-homebase build into your project in three commands.
Designed for the **Pro Dev with AI** persona — see [PERSONAS.md](PERSONAS.md).

## Prerequisites

Python 3.12+ and `pip install pyyaml`.

## Steps

1. **Clone and pick a profile** that matches your stack:
   ```powershell
   git clone https://github.com/<owner>/agent-homebase.git
   cd agent-homebase
   # Pick one of: python-api, react-web-app, monorepo-fullstack
   Copy-Item profiles\python-api.config.yml config\my-project.config.yml
   ```

2. **Fill the FIXMEs** in `config\my-project.config.yml` — repo name,
   coverage targets, tracker, etc. Comments mark every required value.

3. **Build** the resolved artifacts:
   ```powershell
   python init.py --config config\my-project.config.yml
   ```

## What you got

- `resolved\skills\` — copy into your project's `.github\agents\`
- `resolved\instructions\` — copy into `.github\instructions\`
- `resolved\agents\` — copy into `.github\agents\`

## Next

Re-run `python init.py` any time you change the config or the source
under `skills\`, `instructions\`, or `agents\`. Never hand-edit
anything in `resolved\` — it is regenerated every build.
