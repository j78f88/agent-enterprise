# Knowledge Ops post-migration loop plan

Status: draft backlog detail
Date: 2026-06-22
Source: Knowledge Ops migration E0–E7, final repro, and Josh/Vex close-out.

## Purpose

This file turns the post-migration backlog from a list of cleanup ideas into an `agent-enterprise`-style operating plan.

The core lesson from the migration is that the valuable unit is not an ad-hoc task. It is:

1. a canonical backlog row;
2. an explicit mode target;
3. a callable or verifier contract;
4. a gate before commit/push;
5. accepted-deviation and restart state when reality diverges from the plan.

Use this file as the detail artifact for ITEM-033 through ITEM-040 and ITEM-031. `BACKLOG_LEDGER.md` remains the status owner.

## AE primitives to reuse

- **Mode 2 dispatcher:** queue item -> explicit callable id -> input validation -> invocation -> verifier -> state transition. No ghost-done.
- **Callable contract:** stable callable id, JSON-schema inputs, declared outputs, verifier hook, runtime hints.
- **Return tiers:** structured returns for machines first; prose summaries second.
- **Mode 3 choreography:** registry, drift detection, cross-project impact, harvest cycles, promotion contract, audit record.
- **Promotion contract:** evidence-first promotion from project/local artifact into substrate; rejected/parked decisions are recorded.
- **Accepted-deviation ledger:** deviations are allowed only with rationale, reversibility, tracking ref, and next condition.
- **Gate-before-commit:** V-n style verifier must pass before commit; push happens only after external verification when the worker is not the owner.
- **Plan-first mutation:** bulk vault/repo changes require a manifest and scoped rewrite map before mutation.

## Workstream order

### 0. Cockpit deploy substrate — ITEM-035

Why first: cockpit-side fixes are not shipped while `obsidian-publish` points at upstream Quartz.

Mode: Mode 3 project registration + deployment contract.

Callable candidate:

```yaml
id: knowledge-ops.cockpit.deploy-substrate
inputs:
  required: [repo_path, desired_remote, deploy_target]
outputs:
  - path: docs/planning/COCKPIT_DEPLOYMENT.md
  - return_tier: 2
verifier: knowledge-ops.verify-cockpit-deploy-substrate
runtime_hints:
  tools: [git, shell]
```

Verifier gate:

- `git remote -v` no longer has upstream Quartz as the push target, or push is explicitly disabled and deploy path is documented.
- local branch remains intact;
- no accidental push to `jackyzha0/quartz`;
- build/deploy command documented and smoke-tested.

Accepted deviation allowed: local-only cockpit remains acceptable only for read-only diagnostics, not for declaring cockpit fixes shipped.

### 1. Restore health trust — ITEM-034, ITEM-033, ITEM-037

This is one loop slice with three sub-gates. Tone does not become meaningful until all pass.

#### 1A. Fix daily sync hard abort — ITEM-034

Mode: Mode 2 callable + verifier.

Callable candidate:

```yaml
id: youtube-sync.deposit-contract.partition
inputs:
  required: [config_path, fixture_set]
outputs:
  - return_tier: 3
verifier: youtube-sync.verify-deposit-partition
runtime_hints:
  workdir: /home/azureuser/apps/youtube-sync
  command: .venv/bin/python -m pytest tests/test_vault_export.py tests/test_pipeline_contract.py -q
```

Required behavior:

- Replace aggregate `assert_deposit_link_contract` batch abort with per-note partition.
- `deposit_ok` notes are written normally.
- below-floor notes are `held_by_score`.
- above-floor but under-linked notes are `contract_rejected` and sent to a quarantine/review sink, not written as normal source notes.
- infrastructure/code errors still hard-fail.
- audit/return includes `{deposited, held_by_score, contract_rejected, failed}`.

Verifier gate:

- fixture with one bad note and one good note exits 0;
- good note deposits;
- bad note is quarantined/held with reasons;
- no orphan `_raw` transcript;
- audit return records partial success;
- live daily is not run until fixture passes.

#### 1B. Clear stale tone only after 1A

Mode: Mode 2 operational callable.

Precondition: ITEM-034 verifier passed.

Allowed actions:

- replace/annotate stale failed `youtube-sync-daily` audit row only if a current sandbox/no-push run proves the batch no longer hard-fails;
- regenerate `build_summary.json`;
- verify `run_risks` no longer marks the old failure as current.

Not allowed: clearing the audit row while current code still fails.

#### 1C. Fix duplicate cluster heuristic — ITEM-037

Mode: cockpit quality verifier + evidence map.

Required behavior:

- remove transitive union chaining;
- treat E3 archive map as ground truth: `_archive/2026-06-22-knowledge-ops/E3/*.orig` are known duplicates, E3 survivors are known-distinct unless future evidence says otherwise;
- move domain stopwords into config;
- until fixed, duplicate-cluster signal is warn-only, not health-critical.

Verifier gate:

- the 14 distinct E3 canonical notes no longer become one cluster;
- the known archived duplicates still map to their canonical targets;
- cockpit health tone is not driven by the old false-positive heuristic.

### 2. Freshness/provenance badges — ITEM-036

Mode: Mode 3 drift detection applied to generated cockpit artifacts.

Callable candidate:

```yaml
id: knowledge-ops.cockpit.provenance-badges
inputs:
  required: [summary_path, repo_roots]
outputs:
  - return_tier: 2
verifier: knowledge-ops.verify-provenance-drift
```

Required behavior:

- generated cards expose `generated_at` and source git heads;
- compare summary heads to live `git rev-parse HEAD`;
- if drift exists, card says stale and how many commits behind;
- stale cards cannot present as authoritative.

Verifier gate:

- fixture with stale head renders a stale badge;
- fixture with matching heads renders fresh;
- no network or live sync required.

### 3. Edge-based route matcher — ITEM-038

Mode: Mode 3 harvest/promotion + project registry graph.

Required behavior:

- stop routing raw `pattern-candidate-*` titles directly to broad project briefs;
- route via curated edges: `20_patterns` and canonical `30_concepts` wikilinks to `50_projects` notes;
- use lexical matching only as a weak fallback;
- create rows only for high-confidence graph-backed matches;
- unmatched validated ideas remain parked until pattern promotion.

Verifier gate:

- fixture project with `related: [[concept-x]]` receives a high-confidence route from a pattern linked to `concept-x`;
- unrelated lexical overlap does not route;
- idempotent by `source-ref`.

### 4. Governance path coupling — ITEM-031

Mode: Mode 3 pre-move impact scanner + config resolver.

Immediate fix:

- patch the two stale string references found in `_meta/review-queue.md` generator and `_meta/hermes-handoff-learning.md` source/generator.

Structural fix:

- generators resolve governance docs by basename/stable id or config, not hardcoded `_meta/docs/...` paths;
- any future doc move runs a literal path scan across generators, queues, scripts, configs, cron prompts, and job outputs before mutation.

Verifier gate:

- grep for old `_meta/docs/POLICY.md` and `_meta/docs/LEARNING-MAINTENANCE.md` path strings returns only historical archive/explicit migration notes;
- generated review queue points at `_meta/docs/_governance/POLICY.md` or uses resolver;
- pre-move checker has a fixture with path strings in config and generated markdown.

### 5. Decay coverage interlock — ITEM-039

Mode: promotion-contract safety guard.

Required behavior:

- `python -m engine.prune --concepts --apply` refuses to run unless configured verdict coverage threshold is met;
- absence of verdict is never negative evidence;
- only explicit `overhyped`/`refuted` with current coverage can archive;
- hand-authored notes require explicit override.

Verifier gate:

- low-coverage fixture aborts before any archive move;
- high-coverage fixture archives only positive-negative evidence;
- dry-run reports coverage percentage and would-archive list.

### 6. Multi-phase runbook controller spike — ITEM-040

Mode: research spike into Mode 2 + Galactic Council escalation.

Timebox: one spike, not a full feature build.

Spike output:

- controller architecture note;
- schemas for `phase_result`, `phase_verdict`, `decision_packet`, and `resume_packet`;
- executable gate interface for V-n checks;
- sticky-question classifier with four classes: `auto_resolve`, `council_resolve`, `defer_with_handoff`, `ask_josh`;
- accepted-deviation ledger contract;
- one toy runbook fixture proving restart after a council-resolved blocker.

Verifier gate:

- a failing phase cannot transition done;
- an accepted deviation requires rationale + reversibility + tracking ref;
- an `ask_josh` decision blocks instead of guessing;
- a `council_resolve` decision yields a resume packet without new human transport.

## Ledger update rules

When working these items:

- Status remains in `BACKLOG_LEDGER.md` only.
- This file holds detail; do not duplicate status here.
- Each implementation must write a verifier-backed closeout note or commit message with evidence.
- If a task discovers another follow-up, add a new ledger row or update the appropriate existing row in the same rollback unit.
- Do not close ITEM-033 until ITEM-034 and ITEM-037 have landed and a fresh build summary proves the tone signal is meaningful.
