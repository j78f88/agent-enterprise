# Quickstart

The fastest path is to let the `@onboarding` agent do it. Prefer the terminal?
The three-command CLI path is right below. Both produce the same build.

## Fastest path — let the agent set it up

Clone the repo, open it in GitHub Copilot Chat or Claude Code, and paste:

```text
Set up agent-enterprise for my project. Ask me what you need, recommend a
profile, run init.py, deploy the resolved files, and verify it works.
```

The agent interviews you (~5 questions), picks a profile, fills the config,
runs the build, deploys the files, and verifies — no YAML editing, no copy
commands. It self-removes once setup is confirmed.

## CLI path

Designed for the **Pro Dev with AI** persona — see [PERSONAS.md](PERSONAS.md).
Get a working build into your project in three commands.

### Prerequisites

Python 3.12+ and `pip install pyyaml`.

### Steps

1. **Clone and pick a profile** that matches your stack:
   ```powershell
   git clone https://github.com/<owner>/agent-enterprise.git
   cd agent-enterprise
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
