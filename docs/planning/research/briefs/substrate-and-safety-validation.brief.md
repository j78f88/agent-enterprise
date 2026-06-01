---
title: "Brief: substrate commoditisation + build-time safety-layer validation"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-01
---

# Brief — Substrate & Safety-Layer Validation (disconfirmation-first)

**Status:** PROPOSAL — evidence for owner ratification. Not canonical until promoted.

This brief drove the first research run against the conformed knowledge base. Evidence is
in [`../sources/`](../sources/README.md) and [`../claims/`](../claims/README.md); the
registry is [`../INDEX.md`](../INDEX.md). The verdicts below are **evidence**, not
decisions — adopt / build-on / greenfield calls belong to `@pm`/`@architect` + owner.

## Questions under test (and kill-questions)

- **Claim A (substrate):** "author once → resolve to multi-platform agent artefacts" is a
  novel, defensible capability.
  - *Kill-question:* is multi-target emit already commoditised by existing tools?
- **Claim B (safety layer):** "build-time, fail-closed validation of agent artefacts vs
  injection + supply-chain" is a novel, defensible niche.
  - *Kill-question:* does a shipped tool already gate markdown agent artefacts pre-deploy?
- **Compliance anchor map:** verify current AU/intl framework versions; **top redundancy
  risk** — does a reusable government AI-coding template already exist?
- **Adversarial:** steelman that the project is redundant and/or non-compliant.

## Scope

- Consumer profiles: own-agency, other-gov-orgs, vendor-baseline.
- Source-tier floor for `verified`: ≥2 independent sources (per trust-policy).
- Retrieval date: 2026-06-01. Engine: deep-research (4 parallel sweeps), normalised via
  `scripts/conform_research.py`.

## Headline findings (evidence verdicts — see claims for full sourcing)

- **Claim A — disconfirmed as novel.** Author-once → multi-target emit is commoditised by
  `ruler`, `rulesync`, `ai-rulez` (+ corporate `block/ai-rules`), and undercut by the
  AGENTS.md standard and Anthropic Agent Skills (open standard, OpenAI-adopted). Residual
  differentiation: build-time `{{token}}` templating + build-time security validation of
  inputs. [`CLM-multitarget-is-commoditised`, `CLM-agententerprise-residual-novelty`]
- **Claim B — largely disconfirmed as novel.** Snyk Agent Scan + Vercel already ship
  submission-time fail-closed gating of `SKILL.md` (engine: Invariant mcp-scan); CSA
  prescribes CI Unicode linting; Microsoft Agent Governance Toolkit (MIT) covers much of
  the supply-chain posture. Residual: the *unified* build-time resolution pipeline + nonce
  data-fence over multi-platform artefacts. [`CLM-buildtime-skill-gating-already-exists`,
  `CLM-residual-novelty-is-orchestration-not-primitives`,
  `CLM-nonce-data-fence-not-found-in-competitors`]
- **Compliance — partial redundancy, real AU gap.** A reusable *government* AI-coding
  baseline exists (UK GDS "AI Coding Assistants for HMG", Sept 2025); CISA/ACSC shipped
  agentic-AI adoption guidance (Dec 2025). No *Australian* deployable template exists.
  Framework versions verified (ISM Mar 2026; PSPF 2025; DTA AI Policy v2.0; E8MM Nov 2023;
  NIST SSDF 1.1; AI RMF 1.0 + GenAI Profile; SFIA 9). SLSA minor version unconfirmed.
  [`CLM-uk-gds-overlap`, `CLM-no-reusable-gov-template-exists`]
- **Adversarial — strong, partly self-defeating.** The kill-case (distribution solved,
  safety commoditised, "fail-closed is rented", provenance self-admittedly weak, runtime
  gap vs DTA standard, no IRAP, bus-factor) is well-sourced; each carries a falsifier that
  points to the survivable repositioning. [`CLM-adv-*`]

## What would change these verdicts

If `ai-rulez`'s "security auditor" proves to be a real build-time gate, or a single shipped
tool already bundles artefact injection-lint + quarantine + checksum + SBOM + dep-scan for
multi-platform agent artefacts, the residual novelty collapses — re-run before any build.
