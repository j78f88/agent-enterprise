# Plan: Three-Mode Delivery Framework for agent-homebase

## TL;DR

Restructure agent-homebase to formally support **three deployment modes**, each containerized in a new `delivery-modes/` folder. This makes homebase singularly deployable as (1) a project team, (2) an autonomous orchestration layer, or (3) a choreography layer across many projects (program-of-works). The choreography mode is the new "command centre" work — but housed inside homebase as a first-class delivery option rather than a separate repo. Existing `agent-orchestration` repo gets absorbed as Mode 2.

## The Three Modes

| Mode | Name | Deploys to | Today |
|------|------|-----------|-------|
| 1 | **Team** — structured delivery team | One project repo (`.github/agents/`) | Works via `init.py` + manual copy |
| 2 | **Orchestration** — autonomous tracker dispatch | One project + tracker (Linear/etc.) | Lives in separate `agent-orchestration` repo; absorb |
| 3 | **Choreography** — multi-project program of works | A workspace coordinating N projects | Doesn't exist; build it |

Mode 3 = Mode 2 applied to N instances of Mode 1. Modes share substrate (`skills/`, `instructions/`, `profiles/`, `init.py`).

## Phases

### Phase 0 — Populate `command centre/`
Specs, runbooks, and decisions written before any code changes. Establishes the contract Phases 1–6 execute against.

### Phase 1 — Create `delivery-modes/` container
New folder at homebase root with `team/`, `orchestration/`, `choreography/` subfolders. Each has its own `install.py`, README, and mode-specific assets. Shared substrate stays at root.

### Phase 2 — Absorb agent-orchestration as Mode 2
Migrate agents/instructions/hooks/config from the standalone `agent-orchestration` repo into `delivery-modes/orchestration/`. Adapt `afterCreate.sh` from cloning 3 repos to cloning 2. Archive standalone repo with redirect README.

### Phase 3 — Build Mode 3 (Choreography)
Build the `sync` CLI (`deploy`, `diff`, `status`, `harvest`). Define `registry.yml` schema. `delivery-modes/choreography/install.py` scaffolds a fresh command-centre workspace at a chosen path. Add meta-agents for framework dev + harvesting.

### Phase 4 — Harvest Verk Web's maturity
Audit Verk Web's 13 agents + 14 instructions vs homebase using `sync harvest` (dogfooding). Back-port improvements to homebase substrate; keep Verk-specific items project-local unless generalizable.

### Phase 5 — Onboard projects via Choreography
Verk Web → register, deploy, validate against existing 708 unit + 273 E2E suite. diy-project-helper → same with `react-web-app` profile. verk-v2 → already wired; just register and deploy.

### Phase 6 — Documentation + Graduation
Write `delivery-modes/README.md` selection guide. Update root README and `docs/EXTENSION_GUIDE.md`. Graduate stable contents from `command centre/` to `delivery-modes/choreography/template/`.

## Verification

1. Mode 1 install on a fresh repo produces identical output to today's manual `init.py` + copy flow
2. Mode 2 install replicates current agent-orchestration setup end-to-end (run a Linear issue through `@dispatcher` → `@verifier`)
3. Mode 3 install scaffolds a working command centre; `sync deploy verk-v2` matches manual init.py output
4. After harvest + back-port + Verk Web onboarding via Mode 3, Verk Web's existing test suite still passes
5. Round-trip: change a homebase skill → `sync deploy --all` → all registered projects updated correctly

## Decisions

See `decisions/` folder for ADR-style records. Key choices:

- [0001](decisions/0001-containerize-in-homebase.md) Containerize in `delivery-modes/` inside homebase, not a separate repo
- [0002](decisions/0002-absorb-agent-orchestration.md) Absorb agent-orchestration as Mode 2; archive standalone repo
- [0003](decisions/0003-mode-3-scaffolds-workspace.md) Mode 3 scaffolds a workspace (choreography is a working environment, not just config)
- [0004](decisions/0004-shared-substrate-at-root.md) Shared substrate stays at root (no duplication across modes)

## Open Questions

1. **Versioning** — Per-mode tags or unified semver with compatibility matrix? Current lean: unified semver.
2. **Mode interop** — Can a Mode 1 project be upgraded to Mode 2 in place? Current lean: yes, Mode 2 installer detects + upgrades.
3. **Verk Web's unique agents** (`@template-auditor`, `@delivery-lead`) — Promote to substrate, keep project-local, or add a `delivery-modes/extensions/` folder for opt-in extras? Decide during Phase 4.
4. **agent-orchestration repo fate** — Archive read-only with redirect README, or delete after deprecation period? Current lean: archive.
