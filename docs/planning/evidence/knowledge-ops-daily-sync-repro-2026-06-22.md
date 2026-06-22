# Knowledge Ops daily sync repro evidence — 2026-06-22

Status: evidence artifact for ITEM-034 / ITEM-033
Source: non-mutating sandbox reproduction after Knowledge Ops migration close-out.

## Why this exists

The first ITEM-034 row captured the mechanism to stop `youtube-sync-daily` from hard-aborting a batch, but not the deeper correctness question: the repro showed every synthesized above-floor note failed the deposit link contract. A partition-only fix could make the job exit 0 while depositing nothing, silently starving the Learn surface.

This evidence must travel with ITEM-034 so future workers do not treat the issue as a one-off straggler.

## Original failed audited run

Audit ledger:

`/home/azureuser/.hermes/job-audit/youtube-sync-daily.jsonl`

Failed row:

- job: `youtube-sync-daily`
- command: `scripts/run_with_audit.py --job youtube-sync-daily -- .venv/bin/python -m engine.pipeline`
- cwd: `/home/azureuser/apps/youtube-sync`
- started: `2026-06-22T08:04:14Z`
- finished: `2026-06-22T08:06:03Z`
- exit_code: `1`
- repo_head: `2e875612b068`
- vault_head: `aaab3abfb3cd`
- repo_head_after: unchanged
- vault_head_after: unchanged

Journal error:

```text
RuntimeError: Deposit link contract failed:
  WJzsX32qMJY: needs_minimum_two_wikilinks, needs_semantic_concept_pattern_or_source_link;
  38qHuDGZOuA: needs_minimum_two_wikilinks, needs_semantic_concept_pattern_or_source_link
```

Pipeline trace summary:

- harvest: 41
- filter: 2 new
- transcripts: Supadata 429, Apify fallback succeeded
- synthesis: produced notes
- deposit: aborted before filesystem/git writes because contract check failed
- side effects: none; no deposit, no commit, no push

## Current-code sandbox repro

Sandbox shape:

- temp youtube-sync clone at current main `b2abcd0`
- temp vault clone at current main `644dbec`
- live `.env` symlinked into temp checkout for API access, then removed with sandbox
- `CONFIG_FILE` pointed at temp config
- `VAULT_ROOT` pointed at temp vault
- `expected_remote` cleared for temp vault
- git disabled in repro config
- repos block removed
- command used current code but did not touch live vault/state/git

Command class:

```bash
CONFIG_FILE="$RUNROOT/youtube-sync/config.repro.json" \
VAULT_ROOT="$RUNROOT/priv-obsidian" \
PYTHONPATH="$RUNROOT/youtube-sync" \
/home/azureuser/apps/youtube-sync/.venv/bin/python -m engine.pipeline \
  --no-push --no-commit --no-process --no-prune --no-verify \
  --limit 5
```

Result: exit 1.

Three new VS Code videos were synthesized and all failed the contract:

| video_id | score | capture floor | contract result |
| --- | ---: | --- | --- |
| `iHsjptWP2kM` | 92 | above 75 | failed: needs >=2 wikilinks + semantic link |
| `b-IhAbPUyIM` | 88 | above 75 | failed: needs >=2 wikilinks + semantic link |
| `0Gyax75_n0U` | 82 | above 75 | failed: needs >=2 wikilinks + semantic link |

Classification:

- data/synthesis-output issue + batch-level contract brittleness
- systemic, not a straggler
- E5 capture floor does not mitigate because failures are above-floor
- clearing the stale audit row alone is unsafe because the next live daily would re-fail

## Correctness question

The implementation must decide and verify one of these paths, not only partition the batch:

1. Fix synthesis so produced notes satisfy the existing contract.
2. Relax/redesign the contract so it matches useful generated notes.
3. Keep the contract but route rejected notes to an automated re-synthesis/quarantine drain with an owner and SLA.

A quarantine sink with no drain is not acceptable; it would recreate a human queue/graveyard.

## Required live/sandbox gate

A fixture-only verifier is insufficient.

Before ITEM-034 can close, a current-code no-live-mutation sandbox run must prove:

- `deposited > 0` when fresh above-floor videos exist;
- `contract_rejected_rate < 50%` on a daily-shaped sample, or a documented stricter threshold chosen by the implementer;
- rejected items have an automated drain path (e.g. re-synthesize with stronger link-injection, then retry; or write to a bounded review artifact that a Mode 2 callable processes);
- live audit is not cleared until this sandbox gate passes.

If the sandbox still rejects nearly all above-floor notes, ITEM-034 remains open even if partition fixtures pass.

## Secondary cost signal

Supadata returned 429 on every transcript in the repro and Apify paid fallback handled the transcripts. This is recurring-cost telemetry and should be tracked separately from ITEM-034.
