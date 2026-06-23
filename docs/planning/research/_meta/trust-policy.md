---
title: "Research knowledge base — trust policy"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-01
---

# Research Knowledge Base — Trust Policy

> **Status: PROPOSAL — awaiting owner ratification. Not canonical.**
> The source hierarchy and classification handling below are candidate defaults. The
> owner ratifies, amends, or replaces them.

## 1. Source hierarchy (tiers)

Higher tiers carry more weight. A `verified` verdict needs **≥2 independent** sources of
sufficient tier; a single source caps a claim at `plausible`.

| Tier | `source_tier` | Examples | Weight |
| --- | --- | --- | --- |
| 1 | `authoritative-standard` | ACSC ISM, PSPF, Essential Eight, NIST SSDF/AI RMF, SLSA, IRAP/HCF | Highest — defensible by itself for compliance anchoring. |
| 2 | `official-guidance` | DTA AI policy/assurance, ACSC/CISA/NCSC secure-AI guidelines, first-party vendor docs | Strong. |
| 3 | `primary` | First-party spec/RFC/repo/commit, official changelogs | Strong for technical fact. |
| 4 | `practitioner-signal` | Conference talks, practitioner blogs, **the YouTube corpus** | **Down-ranked** — corroborating signal only. |
| 5 | `community` | Forums, Q&A, social posts | Lowest — a starting hint, never a citation on its own. |

## 2. Trust labels (untrusted-wins)

- **`trusted`** — first-party authored / reviewed and promoted into `sources/`, `claims/`,
  `controls/`, `briefs/`.
- **`untrusted`** — imported, fetched, third-party, or engine-raw. Lives in `_staging/`
  or `_imported/`. A claim **inherits the most restrictive** trust label of its evidence;
  any untrusted input ⇒ the claim is untrusted and cannot be canonical.

## 3. Classification handling (PSPF: OFFICIAL → PROTECTED)

Every source-note and claim carries a `classification`. Ordered least → most restrictive:

```
OFFICIAL  <  OFFICIAL:Sensitive  <  PROTECTED
```

- **Default** is `OFFICIAL`. Escalate when the content warrants it.
- A claim inherits the **most restrictive** classification among its evidence.
- This is a **markdown + git** knowledge base. Do **not** place material above the
  repository's approved handling level here. If research would require **PROTECTED**
  handling, record only an `OFFICIAL`/`OFFICIAL:Sensitive` reference plus a pointer to the
  controlled store — never the protected content itself.
- The validator asserts a valid classification is **present**; it does not enforce the
  storage boundary — that remains human accountability.

## 4. The gate (fail-closed)

`scripts/check_research.py` hard-fails when, in the canonical tree:

- a source-note or claim fails its schema or omits provenance (URL/locator, date, hash);
- a claim's `evidence[].source_id` does not resolve to an existing source-note;
- a `verified`/`contested` claim has fewer than 2 independent sources;
- a canonical document is labelled `untrusted`, or cites a `_staging/`/`_imported/` path;
- a document is missing a valid `classification`;
- `INDEX.md` is missing, or a canonical record is unregistered.

It **degrades gracefully** (warn, record "not run") when optional external scanners
(`semgrep`, `grype`, `syft`, `detect-secrets`) are absent — the owner's decision — so the
contract is runnable everywhere without the full toolchain. Core contract checks always
hard-fail; only the supplementary scanners degrade.

## 5. Honest scope (anti-hype)

A content hash proves **what was recorded at retrieval time**, not that any downstream
agent behaved correctly (corpus guardrail: *recorded ≠ executed*). Provenance here gives
tamper-evidence of the **record**, paired with the build's determinism — never market it
as runtime assurance.
