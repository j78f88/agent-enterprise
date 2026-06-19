# Quickstart

The fastest path is to let the `@onboarding` agent do it. Prefer the terminal?
The CLI path below uses the same deploy-oriented topology: keep this repo under
your project as `skills-library/`, run `init.py` there, and deploy into the
adopter root with `--deploy-root ..`.

## Fastest path — let the agent set it up

Clone the repo, open it in GitHub Copilot Chat or Claude Code, and paste:

```text
Set up agent-enterprise for my project. Ask me what you need, recommend a
profile, run init.py, deploy the resolved files, and verify it works.
```

The agent interviews you (~5 questions), picks a profile, fills the config,
runs the build, deploys the files, and verifies — no YAML editing, no copy
commands. After `setup_complete: true` and a final deploy, the setup-only
onboarding agent removes itself from generated/deployed surfaces.

## CLI path

Designed for the **Pro Dev with AI** persona — see [PERSONAS.md](PERSONAS.md).
Get working agent surfaces deployed into your project.

### Prerequisites

Python 3.12+ and `pip install pyyaml`.

### Steps

1. **Add the library under your project** and pick a profile that matches your stack:
   ```powershell
   cd your-project
   git clone https://github.com/j78f88/agent-enterprise.git skills-library
   cd skills-library
   # Pick one of: python-api, react-web-app, monorepo-fullstack
   Copy-Item profiles\python-api.config.yml config\my-project.config.yml
   ```

2. **Fill the FIXMEs** in `config\my-project.config.yml` — repo name,
   coverage targets, tracker, etc. Comments mark every required value.

3. **Build and deploy** into the adopter project root:
   ```powershell
   python init.py --config config\my-project.config.yml --deploy --deploy-root ..
   ```

## What you got

- `skills-library\resolved\skills\`, `resolved\instructions\`, and `resolved\agents\` — deterministic build output; do not edit by hand.
- `..\.github\agents\` and `..\.github\instructions\` — deployed skills, wrappers, and shared instructions in your project root.
- `..\.claude\commands\` — slash-command files for every agent.
- Target-specific surfaces from `editor.target`: `..\.claude\agents\`, `..\.cursor\commands\` + `..\.cursor\rules\`, or a managed block in `..\AGENTS.md`.

For the full before/after smoke checklist, including `setup_complete: true`
self-removal of the onboarding agent, see [ONBOARDING.md](ONBOARDING.md#step-9--verify-your-setup).

## Next

Re-run `python init.py --config config\my-project.config.yml --deploy --deploy-root ..`
any time you change the config or the source under `skills\`, `instructions\`,
or `agents\`. Never hand-edit anything in `resolved\` — it is regenerated every
build.
