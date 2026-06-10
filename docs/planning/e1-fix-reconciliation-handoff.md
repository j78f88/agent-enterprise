# Handoff: Reconcile agent-homebase-e1 fixes into agent-enterprise

**Created:** 2026-06-02
**Reason for handoff:** The reconciliation needs read access to the
`agent-homebase-e1` repo, which is **not reachable from a Claude Code on the
web session** (isolated cloud container, single repo cloned, no local-disk
access, e1 is private so WebFetch 404s, GitHub MCP scoped to `agent-enterprise`
only). Continue in a session that can see **both** repos — see "Where to run"
below.

---

## Goal

Confirm that the fixes made in **agent-homebase-e1** (its ~2 sprints) have
equivalents in **agent-enterprise**, and apply any that are genuinely missing
and portable. Produce a landed / missing / different / not-applicable table.

## Repo lineage (so nobody gets confused again)

- **agent-homebase → renamed → agent-enterprise.** Same repo. This repo's own
  release history is tagged `agent-homebase@3.0.x`; the rename to
  `agent-enterprise` happened ~2026-05-29 (see
  `docs/planning/drafts/repo-rename-agent-enterprise-draft-plan.md`). So
  "agent-homebase fixes" are already in this history by definition.
- **agent-homebase-e1 is a SEPARATE fork** that pivoted to a **TypeScript /
  Ports & Adapters** rewrite (ADR-003, accepted 2026-05-27). It is *not* this
  repo. Its sprints were: Sprint 1 = GitHub issue-tracker adapter, Sprint 2 =
  Azure DevOps + Linear adapters.
- **Key consequence:** e1's *adapter code* is TypeScript and does **not** port
  into this Python + Jinja2 generator. Only the **process / prompt / governance**
  fixes are portable. Expect most adapter work to be "N/A — TS-only," not
  "missing."

## Which git repos you need connected

| Role | Repo | GitHub | Local path | Notes |
|------|------|--------|------------|-------|
| **Source of fixes** | `agent-homebase-e1` | `j78f88/agent-homebase-e1` (private) | `C:\VS\agent-homebase-e1` | Read-only for this task |
| **Target (this repo)** | `agent-enterprise` | `j78f88/agent-enterprise` | wherever you cloned it (suggest `C:\VS\agent-enterprise`) | Branch: `claude/docs-skill-progress-6bJOt` |

You need **both checked out locally, side by side** (e.g. both under `C:\VS\`).

## Where to run this

Pick one — both give a session that can see e1 and this repo together:

1. **Claude Code CLI (recommended)** — `cd C:\VS` (the common parent of both
   repos) and run `claude` there, so both directories are in the workspace.
2. **VS Code / JetBrains extension** — open `C:\VS` (or a multi-root workspace
   containing both `agent-homebase-e1` and `agent-enterprise`).

Do **not** retry this in a Claude Code on the web session — it cannot reach
`C:\` or a private second repo. That's a fixed property of the web sandbox, not
a configuration to change.

## What to gather from e1 (the reconciliation inputs)

From `C:\VS\agent-homebase-e1`, the authoritative "what we fixed" record:

1. `sprints/sprint-1/RETRO.md` + `PLAN.md`
2. `sprints/sprint-2/RETRO.md` + `PLAN.md`
3. e1's backlog (its equivalent of `docs/planning/BACKLOG_LEDGER.md` /
   `BUG_BACKLOG.md`), plus `docs/sop/skill-layer-requirements.md` (R1/R2)
4. e1's ADRs (`docs/decisions/` — ADR-003…006 referenced in research)
5. For any *process/prompt/governance* fix: the diffs/files (hooks, skill
   bodies, instruction docs, validators, scripts) — skip TS adapter source

## Method

For each fix in e1's RETROs/backlog, classify against `agent-enterprise`:

- ✅ **Landed** — equivalent already exists here (cite the file path)
- ❌ **Missing** — portable fix with no equivalent here → apply it
- ⚠️ **Different** — exists here but diverges → decide which is correct
- 🚫 **N/A** — TS adapter / architecture-specific, does not port

## Already-verified equivalents (cross-checked against the research, 2026-06-02)

These e1 requirements (per the research docs in
`docs/planning/research/`) already have working equivalents here — confirm the
e1 RETROs don't add anything beyond them:

| e1 requirement | Equivalent in agent-enterprise | Status |
|---|---|---|
| R1 — no dangling references | `scripts/check_tokens.py` + `init.py` unresolved-token hard-exit | ✅ (Sprint 2 / ITEM-012) |
| R2 — researcher honesty-guard | `instructions/generic/honesty-contract.instructions.md` + falsification section in `skills/researcher/researcher.skill.md` | ✅ |
| ADR-006 — process gates | `.githooks/commit-msg` + planner draft-approval checkpoint in `agents/planner.body.md` | ✅ (Sprint 2 / ITEM-007) |

## State of this repo (target)

- All backlog items `done` **except ITEM-013** (`jsonschema.RefResolver`
  deprecation, open, unscheduled) — see `docs/planning/BACKLOG_LEDGER.md`.
- Version `3.0.2`; Sprint 2 complete. Note: CHANGELOG has **no `3.0.3` /
  Sprint 2 entry** and version files (`src/__init__.py`, `config/plugin.json`)
  are not bumped for Sprint 2 — a separate `@docs` follow-up if you want it.

## Definition of done

- A reconciliation table (landed/missing/different/N/A) covering every e1 fix.
- Any ❌ missing-and-portable fix applied on a branch off
  `claude/docs-skill-progress-6bJOt` (or a fresh branch), committed per
  `instructions/.../commit-conventions`, with a PR for the review gate.
- Anything ⚠️ different flagged for your decision before changing.
