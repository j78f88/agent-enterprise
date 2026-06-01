---
from: "@planner (planning session)"
to: "new session — @architect + @planner"
date: 2026-06-01
feature: research-knowledge-base
artifact: docs/planning/vision/safety-in-consumption-design-goals.md
status: ready-for-build
notes: Ratified intent — build the sovereign, agency-owned, defensible research+decision knowledge base; researcher skill governs all research with deep-research as engine; codebase research approved. Build the container + contract first; no research content until it's conformed.
---

# Handoff — Research Knowledge Base (container + contract first)

A fresh session has **no memory of the planning conversation**. This manifest is the
full brief. Read the three artefact pointers below, then execute the in-scope tasks.

## Ratified intent (confirmed by the project owner)

Build agent-enterprise's research capability as a **sovereign, provenance-first,
agency-owned knowledge base inside this repo** — plain Markdown, git-versioned, no
external SaaS dependency, defensible by trace. It applies the project's own
"safety in consumption" thesis to *ideas*: every claim is sourced or it doesn't
become canonical.

Context that shapes every decision:
- **Consumer is an AU federal government agency**; the output must also be a
  **reusable template other gov orgs can consume**, and a **minimum-expectation
  baseline for vendors** in the coding delivery stream. → Three consumer profiles
  (own agency / other gov orgs / vendors); a design choice that's right for one can
  fail another. Tokenise everything portable.
- The owner has near-absolute tech authority and a highly capable team — **optimise
  for correctness and defensibility, not for adoption hand-holding.**
- **Compliance is the spine, not an add-on.** Goals trace to authoritative AU gov
  guidance, which is what makes them defensible (and not arbitrarily asserted).

## Approach decided

- The **`researcher` skill is the constitution** for ALL research. It owns the
  artefact home, citation/falsifiability rules, the approval gate, and the subagent
  return tiers. It **never recommends** (evidence only) — that is the built-in
  anti-echo guarantee. Keep it.
- **`deep-research` (global harness skill) is a breadth *engine*** the researcher
  drives for wide prior-art / landscape sweeps. It is NOT editable by us, so its raw
  output is never the artefact — it is **normalised into the researcher's home +
  template + provenance schema, then registered in INDEX**. Enforce at our boundary.
- **A fail-closed validator** (an `init.py`-style gate over the research home) is the
  real guarantee that "all research follows the contract regardless of slash command":
  unconformed research lands in `_staging/` as `untrusted` and cannot become canonical
  until it passes (citations + dates + provenance + INDEX entry).
- **Evidence vs decision separation stays intact:** research surfaces sourced
  source-notes/claims; the **adopt / build-on / greenfield** verdicts and ADRs are
  decisions made via `@architect`/`@pm` + owner ratification. The engine gathers;
  the owner decides. (This is the structural guard against overstepping — agent
  output is proposal-tier until ratified into `decisions/`.)
- **Codebase research is APPROVED** for this work (the researcher skill currently
  forbids it — see task 2). We are pioneering the next steps.

## In-scope build tasks (container + contract ONLY — no research content yet)

1. **Provenance homes as config tokens** (`config/project.config.yml` + profiles).
   Extend beyond the current flat `paths.research` (= `docs/planning/research/`) into a
   tokenised provenance substructure: `sources/`, `claims/`, `controls/` (the AU gov
   control register), `briefs/`, `_staging/`, `_imported/`. Tokenise for portability
   across consuming agencies. Default them under the research path.
2. **Extend the `researcher` skill** (`skills/researcher/researcher.skill.md` +
   `agents/researcher.body.md`):
   - Broaden remit to a new research type — "external validation, prior-art, and
     compliance evidence" — and **permit codebase research** for self-validation
     (owner-approved). Keep ALL citation/falsifiability/approval discipline.
   - Add the deep-research engine contract: how the skill invokes deep-research,
     crafts the scoped question (kill-questions baked in), and normalises output into
     the provenance home + INDEX.
3. **Schemas** (`schemas/`): `source-note.schema.json` and `claim.schema.json`
   (claim carries verdict `verified|plausible|overhyped|unverified` + evidence link +
   optional control anchor). Follow protocol-v1 conventions.
4. **`INDEX.md`** seed in the research home (currently missing) + a `_meta/charter.md`
   and `_meta/trust-policy.md` (source hierarchy; **down-rank the YouTube corpus** to
   practitioner-signal tier; classification handling for OFFICIAL→PROTECTED).
5. **Fail-closed validator** — a gate (script + test, `init.py` philosophy) over the
   research home: every claim has source+date; every decision cites claim IDs; no
   canonical doc references `_staging`; classification present. Stub is acceptable for
   v1, but the contract must be expressed.
6. **Retro-conform the two existing artefacts** produced out-of-contract this session:
   move `docs/planning/research/youtube-synthesis-digest.md` into `_staging/` (or
   conform it) and treat `tools/distill_synthesis.py` as the corpus ingestor (note its
   hard-coded external path).

## Artefact pointers (read these, do not duplicate)

- `docs/planning/vision/safety-in-consumption-design-goals.md` — the design goals +
  phased roadmap (DG-1…DG-10), re-baselined against the corpus. **Owner flagged this
  was authored with an overstep — treat its goals as candidate proposals, not settled
  fact.** §8 holds open decisions.
- `docs/planning/research/youtube-synthesis-digest.md` — distilled 241-note corpus
  (caveat frequencies + anti-hype guardrails). Secondary source; down-ranked.
- `tools/distill_synthesis.py` — deterministic corpus distiller.

## The research to run AFTER the container exists

Two claims, validated separately, disconfirmation-first:
- **Claim A (substrate):** "author once → resolve to multi-platform artefacts." Likely
  partly commoditised — triage `ruler`, `rulesync`, AGENTS.md standard, Anthropic Agent
  Skills, Claude Code plugins. Verdict: adopt / build-on / greenfield.
- **Claim B (safety layer):** build-time fail-closed validation vs injection +
  supply-chain. Triage garak, promptfoo, NeMo Guardrails, Llama Guard, Lakera, Invariant
  mcp-scan, Socket.dev, OSV-Scanner, Semgrep, Sigstore/SLSA, OWASP LLM/Agentic Top 10,
  MS agent-governance-toolkit.
- **Compliance anchor map (the spine):** ACSC ISM, Essential Eight, PSPF + data
  classification, DTA Policy for Responsible Use of AI in Government + AI assurance
  framework, ACSC/CISA/NCSC Guidelines for Secure AI System Development, NIST SSDF/AI
  RMF/SLSA, IRAP + Hosting Certification Framework, SFIA (vendor baseline). Verify
  current versions/dates. **Surface honestly if a reusable gov AI-coding template
  already exists** (US GSA/CISA, UK GDS/NCSC, ACSC/DTA) — that's the top redundancy risk.
- A dedicated **adversarial agent** argues the project is redundant/non-compliant.

## Constraints & guardrails

- Agent/Claude output is **proposal-tier**, lands in `_staging/`, never canonical until
  the owner promotes. Do not assert the owner's goals as fact.
- Every external claim: URL + retrieval date + verdict; ≥2 independent sources for
  contested claims; unsourced = `unverified`, never smuggled in.
- Tokenise homes — the template must port to other agencies.
- Honour `CLAUDE.md`: never edit `resolved/`; change source; keep `init.py` + tests green.

## Open decisions (owner to resolve; do not assume)

1. Supply-chain depth (design-goals §8): checksums+provenance JSON / + Cosign / full SLSA.
2. Validator toolchain: bundle scanners as deps vs degrade-gracefully when absent.
3. Research-home location: nest under `docs/planning/research/` vs new top-level
   `knowledge/`.
4. Scope of first research run: own agency only, or all three consumer profiles.

## Success criteria for the new session

- The provenance container exists, schema-enforced, with INDEX + charter + trust-policy.
- The `researcher` skill governs deep-research and the new research type; codebase
  research permitted; `python init.py` and tests stay green.
- A deep-research run started *bare* would land in `_staging/` and fail the gate until
  conformed — demonstrably "process followed regardless of slash command."
- No research conclusions written as canonical; goals remain the owner's to ratify.
