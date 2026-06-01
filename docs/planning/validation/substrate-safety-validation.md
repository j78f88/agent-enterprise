# PM Validation — Substrate & Safety-Layer Positioning

**Status:** PROPOSAL — decision-support for owner ratification. Not canonical.
**Author:** @pm · **Date:** 2026-06-01 · **Evidence:** [`research/INDEX.md`](research/INDEX.md) (54 source-notes, 46 claims, gate green)
**Handoff in:** [`_handoffs/2026-06-01-researcher-to-pm-substrate-safety.md`](_handoffs/2026-06-01-researcher-to-pm-substrate-safety.md)

> @pm surfaces validated recommendations; the **adopt / build-on / greenfield** decision
> and any ADR are the owner's (via `@architect` + ratification). Evidence verdicts are the
> researcher's; the product judgement below is mine.

## 1. The question that actually matters

Not "is any part novel?" but: **given an AU federal agency running heterogeneous coding
agents (Claude Code / Copilot / Cursor / Codex), is there a defensible, fundable product
here — and if so, what is it?** The evidence forces a reposition, not a retreat.

## 2. Evidence → recommendation (per layer)

| Layer | Evidence (claim IDs) | Verdict | Recommendation |
| --- | --- | --- | --- |
| **Raw multi-target emit** | commoditised: `CLM-multitarget-is-commoditised`, `CLM-ruler-covers-multitarget`, `CLM-rulesync-covers-multitarget`, `CLM-skills-open-standard-portable` | Redundant | **ADOPT** — stop investing in a bespoke emitter; consume/standardise on ruler or rulesync + AGENTS.md/Agent Skills. |
| **Build-time `{{token}}` templating** | `CLM-ruler-no-templating`, `CLM-tokentemplating-not-confirmed-elsewhere` (plausible, contested) | Thin edge | **BUILD-ON** — keep `init.py` token resolution as a convenience, but do not market it as the moat. |
| **Build-time safety gate (injection + supply-chain)** | already ships: `CLM-buildtime-skill-gating-already-exists`, `CLM-ci-unicode-linting-recommended-standard`, `CLM-dep-and-provenance-layer-commoditised`, `CLM-adv-safety-redundant-msgov` | Largely redundant as "novel" | **BUILD-ON** — orchestrate best-of-breed (Snyk Agent Scan/Invariant mcp-scan, OSV/Socket/Semgrep, CSA unicode guidance, MS toolkit patterns); do not reinvent scanners. |
| **Unified fail-closed pipeline + nonce data-fence over *multi-platform* artefacts** | `CLM-residual-novelty-is-orchestration-not-primitives`, `CLM-nonce-data-fence-not-found-in-competitors` (plausible, contested) | Genuinely thin-but-open | **GREENFIELD (narrow)** — the only build-it-ourselves slice, and only if the contested falsifiers don't fire. |
| **AU-government compliance-bound template** | `CLM-uk-gds-overlap`, `CLM-no-reusable-gov-template-exists`, `CLM-cisa-agentic-overlap` | Real gap (UK has one, AU doesn't) | **GREENFIELD** — the strongest defensible value: an ISM/PSPF/DTA-AI-Policy-bound, vendor-neutral baseline. |

## 3. Repositioned value proposition (recommended)

> **From:** "a novel author-once substrate with a novel build-time safety layer."
> **To:** "an **opinionated, AU-government-grade, vendor-neutral integration + template**
> that binds best-of-breed agent-artefact security tools into a **single fail-closed build
> gate** and maps every control to **ISM / PSPF / DTA AI Policy** — for agencies that run
> *multiple* coding agents and cannot depend on any one vendor's native governance."

Why this survives the adversarial case (`CLM-adv-*`): every kill-claim's own falsifier
points here — reposition as a **Discover/build-time + supply-chain** control that *feeds*
an agency's existing IRAP-assessed runtime, explicitly hands off the Operate phase to
runtime tooling, and differentiates on **cross-vendor + compliance binding**, not on
primitives.

## 4. Consumer-profile read (the three lenses)

- **own-agency:** value = defensible, compliance-traced control over a heterogeneous agent
  fleet. Strong fit.
- **other-gov-orgs:** value = the missing *Australian* reusable template. Strongest
  differentiator; UK GDS proves demand, AU gap proves whitespace.
- **vendor-baseline:** value = an SFIA-anchored minimum expectation for delivery vendors.
  Viable, secondary.

## 5. Risks & kill criteria (PM lens)

- **Absorption risk** (`CLM-adv-strategic-absorption`, plausible): vendors fold portability
  into standards. *Mitigation:* compete on cross-vendor + AU-compliance, not portability.
- **"Rented" guarantee** (`CLM-adv-scanners-not-bundled`): fail-closed depends on unbundled
  scanners. *Mitigation:* pin/version the toolchain; resolve the degrade-gracefully open
  decision toward hard-fail in gov contexts (architect call).
- **Bus-factor / no IRAP** (`CLM-adv-bus-factor`, `CLM-adv-no-irap`): *Mitigation:* scope as
  a build-time developer tool feeding an assessed system; add governance evidence.
- **KILL if:** ai-rulez's "security auditor" proves to be a real build-time multi-artefact
  gate, OR any single shipped tool already bundles injection-lint + quarantine + checksum +
  SBOM + dep-scan for multi-platform agent artefacts (`CLM-agententerprise-residual-novelty`
  falsifier). Re-run before committing build budget.

## 6. Decisions flagged for the owner (do not assume)

1. Accept the reposition (integration + AU-compliance template) over "novel substrate"?
2. Adopt an existing emitter (ruler/rulesync) vs keep `init.py` as the emitter?
3. Greenlight the narrow greenfield (nonce data-fence + compliance template) only?

**Handoff:** to `@architect` for the technical design decisions / ADRs implied by §2 and §5.
