# Researcher — Research Contract & Deep-Research Engine

Reference material for the `@researcher` skill. The skill is the **constitution** for
ALL research in {{project.name}}; this file holds the operational contract that keeps
every research run — **regardless of which slash command launched it** — provenance-first
and fail-closed.

The governing documents live in the research knowledge base:

- `{{paths.research_charter}}` — charter (purpose, principles, homes, ratification path).
- `{{paths.research_trust_policy}}` — source hierarchy, trust labels, classification.
- Schemas: `schemas/source-note.schema.json`, `schemas/claim.schema.json`.
- Gate: `scripts/check_research.py` (fail-closed validator).

---

## Provenance homes (where research lands)

| Home | Token | Holds |
| --- | --- | --- |
| Source-notes | `{{paths.research_sources}}` | One record per cited source. |
| Claims | `{{paths.research_claims}}` | Verdict-tagged claims with evidence links. |
| Controls | `{{paths.research_controls}}` | AU gov control register / anchors. |
| Briefs | `{{paths.research_briefs}}` | Scoped questions + kill-questions. |
| Staging | `{{paths.research_staging}}` | Quarantine — untrusted, unconformed. |
| Imported | `{{paths.research_imported}}` | Ingested external corpora. |
| Index | `{{paths.research_index}}` | Registry of canonical artefacts. |

Anything not yet conformed lands in `{{paths.research_staging}}` as `untrusted` and
**cannot become canonical** until it passes the gate.

---

## Research types in remit

1. **Pattern / competitive research** — how other apps and segments solve a problem.
2. **External validation, prior-art & compliance evidence** — triage existing tools and
   standards to test whether a capability is already commoditised or compliant.
3. **Codebase research for self-validation** (owner-approved) — validate a claim against
   this repository's own code. Record it as a source-note with `locator.kind = codebase`
   and a `path@gitsha` ref. The same citation, dating, and provenance discipline applies —
   a codebase finding is evidence, not a recommendation.

Across all three: surface evidence, **never** recommend. The adopt / build-on / greenfield
verdicts and ADRs are decisions made by `@architect`/`@pm` plus owner ratification.

---

## Driving the deep-research engine

`deep-research` is a breadth **engine**, not the artefact. It is not editable here, so its
raw output is normalised at our boundary before anything is registered.

1. **Author a brief** in `{{paths.research_briefs}}` first: the precise claim under test,
   the **kill-questions** (what evidence would disconfirm it), the consumer profile(s)
   (own-agency / other-gov-orgs / vendor-baseline), and the source-tier floor for a
   `verified` verdict.
2. **Craft the scoped question** for `deep-research` with the kill-questions baked in —
   run disconfirmation-first, so a redundant or non-compliant result fails fast.
3. **Capture raw output into `{{paths.research_staging}}`** as `untrusted`. Never treat
   engine output as canonical.
4. **Normalise** each retained finding into the schema:
   - one **source-note** per source (URL or codebase locator, retrieval date, publisher,
     `source_tier`, `classification`, SHA-256 `content_hash`);
   - one **claim** per proposition (verdict, evidence links to source-note ids, optional
     `control_anchor`, a `falsifier`).
5. **Register** every promoted record in `{{paths.research_index}}` and move it from
   staging into `{{paths.research_sources}}` / `{{paths.research_claims}}`.
6. **Run the gate** — `python scripts/check_research.py`. Promotion is complete only when
   it is green.

---

## Verdict discipline

- `verified` — corroborated by **≥2 independent** sources of sufficient tier.
- `plausible` — supported but not fully corroborated; a single source caps here.
- `overhyped` — a claim the evidence does **not** support; record it as an anti-hype
  guardrail (what not to design around).
- `unverified` — no adequate source found. Never smuggled in as fact.

Contested claims require ≥2 independent sources. Every `verified`/`plausible` claim states
its **falsifier**. The YouTube corpus is tier-4 `practitioner-signal` (down-ranked) — it
corroborates direction but cannot lift a claim above `plausible` or anchor compliance.

---

## Classification (PSPF: OFFICIAL → PROTECTED)

Every record carries a `classification`; default `OFFICIAL`. A claim inherits the most
restrictive classification of its evidence. This is a Markdown + git store — keep material
above the repository's approved handling level out; record an `OFFICIAL` reference plus a
pointer to the controlled store instead.

---

## Pattern / competitive research — prose template

For pattern and competitive sweeps (not prior-art/compliance, which normalise into
source-notes + claims), use this shape:

```markdown
# Research: <topic>

**Date:** YYYY-MM-DD
**Requested by:** <user | @pm>
**Scope:** <specific question or segment>

## Apps / sources surveyed
- App name — URL, category, scale (users/years)

## Patterns found
For each pattern:
- **Name:** short title
- **What it is:** concrete UX / data model / workflow (not abstract)
- **Source apps:** which apps implement it
- **Adoption scale:** users, years, success indicators
- **User complaints:** what users actually complain about (reddit, app store, forums)
- **Failure mode:** apps that shipped this and abandoned it, or features retired

## Unmet needs observed
Patterns that users are asking for but no app delivers well.

## Sources
Full citation list with URLs and retrieval dates.
```

Never add a "recommendations" section — that is `@pm`'s job.
