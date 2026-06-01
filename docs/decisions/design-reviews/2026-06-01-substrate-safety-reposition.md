# Design Review — Substrate & Safety-Layer Reposition (ADRs)

**Status:** PROPOSED — architecture decisions for owner ratification. Not canonical.
**Author:** @architect · **Date:** 2026-06-01
**Handoff in:** [`../../planning/_handoffs/2026-06-01-pm-to-architect-substrate-safety.md`](../../planning/_handoffs/2026-06-01-pm-to-architect-substrate-safety.md)
**Evidence:** [`../../planning/research/INDEX.md`](../../planning/research/INDEX.md) · **Validation:** [`../../planning/validation/substrate-safety-validation.md`](../../planning/validation/substrate-safety-validation.md)

> ADRs are PROPOSED. They cite claim IDs as evidence; the verdicts are the researcher's,
> the design choices are mine, the ratification is the owner's.

---

## ADR-101 — Emitter: build-on, don't rebuild (retain `init.py`, emit to open standards)

- **Context:** multi-target emit is commoditised (`CLM-multitarget-is-commoditised`,
  `CLM-ruler-covers-multitarget`); `init.py`'s edge is `{{token}}` templating + validation
  (`CLM-ruler-no-templating`), which is thin (`CLM-tokentemplating-not-confirmed-elsewhere`).
- **Decision (proposed):** keep `init.py` as the **token-resolving, security-validating**
  authoring path, but stop expanding bespoke per-agent emitters. Emit to the **AGENTS.md**
  and **Anthropic Agent Skills** open standards (`CLM-skills-open-standard-portable`), and
  treat `ruler`/`rulesync` as interop/reference targets. A later spike evaluates delegating
  raw fan-out to `ruler`/`rulesync` behind our gate.
- **Consequences:** less surface to maintain; portability rides the open standards; our
  value moves up-stack to validation + compliance. Risk: coupling to external emitters
  (mitigated by emitting standard formats, not tool-specific ones).
- **Alternatives rejected:** (a) keep building emitters — duplicates mature tooling;
  (b) adopt `ruler` wholesale now — premature; loses token templating + our gate.

## ADR-102 — Safety layer is an orchestrator over best-of-breed (not new scanners)

- **Context:** build-time skill gating already ships (`CLM-buildtime-skill-gating-already-exists`),
  CI unicode lint is a published recommendation (`CLM-ci-unicode-linting-recommended-standard`),
  dep/SBOM/provenance are commodity (`CLM-dep-and-provenance-layer-commoditised`). Residual
  value is orchestration (`CLM-residual-novelty-is-orchestration-not-primitives`).
- **Decision (proposed):** implement design-goal **DG-6** as the spine — an ASH-style
  orchestrator that fans out to **external** validators and normalises to SARIF:
  Snyk Agent Scan / Invariant `mcp-scan` (artefact injection + tool-poisoning),
  `semgrep`/`detect-secrets` (embedded code), `osv-scanner`/`syft`/`grype` (deps/SBOM),
  plus our **own** unicode/bidi + injection-marker linter (the one genuinely-thin in-house
  control). We integrate; we do not reimplement scanners.
- **Consequences:** fast to credible coverage; swap-able as tools mature (the project's core
  premise). Risk: integration breadth.
- **Alternatives rejected:** in-house scanners — redundant with `CLM-adv-safety-redundant-msgov`.

## ADR-103 — Fail-closed posture is profile-driven (gov = hard-fail; bundle + pin toolchain)

- **Context:** the "rented guarantee" critique (`CLM-adv-scanners-not-bundled`) is valid;
  design-goals §8.2 is open.
- **Decision (proposed):** split the posture by **profile**. A `strict` (government) profile
  **hard-fails** the build when a *required* scanner is absent and **pins+isolates** the
  toolchain; a `standard` profile degrades gracefully. Record every scanner's run/skip
  state in `PROVENANCE.json` (DG-9). *Note:* the **research-KB** validator
  (`check_research.py`) intentionally degrades gracefully (owner decision for the knowledge
  base); the **build** safety gate is the stricter sibling — the two are deliberately
  distinct and must not be conflated.
- **Consequences:** closes the adversarial gap for gov; heavier setup for `strict`.
- **Alternatives rejected:** single global posture — fails one consumer profile or another.

## ADR-104 — Explicit runtime-scope boundary + Operate-phase hand-off

- **Context:** the DTA AI technical standard spans Discover/Operate/Retire; we are "not a
  runtime sandbox" (`CLM-adv-not-runtime-operate-gap`).
- **Decision (proposed):** declare scope = **Discover + build-time + supply-chain** only,
  and ship a documented hand-off to runtime guardrails (NeMo/Llama Guard/Lakera/MS toolkit —
  `CLM-most-named-guardrails-are-runtime`) for Operate. Position outputs to **feed** an
  agency's existing IRAP-assessed runtime, not replace it (`CLM-adv-no-irap` falsifier).
- **Consequences:** honest, defensible scope; converts two kill-claims into design clarity.

## ADR-105 — Nonce data-fence as the lead structural differentiator (verify-first)

- **Context:** build-time data/instruction separation via a nonce fence was not found in any
  surveyed competitor (`CLM-nonce-data-fence-not-found-in-competitors`, contested/plausible).
- **Decision (proposed):** design DG-3's nonce-`<DATA>` fence into resolved artefacts as the
  flagship differentiator — **gated on a confirmation pass** that no shipped tool already
  emits it (the claim's falsifier). If falsified, fall back to ADR-102 orchestration value.
- **Consequences:** a concrete, ownable primitive; low redundancy risk if verified.

## ADR-106 — Compliance-control register is the spine (bind to ISM/PSPF/DTA + map UK GDS)

- **Context:** no AU reusable gov AI-coding template exists; the UK GDS one does
  (`CLM-no-reusable-gov-template-exists`, `CLM-uk-gds-overlap`); PSPF classification is the
  marking scheme (`CLM-pspf-classifications`); ISM-1730 mandates SBOM (`CLM-adv-ism1730`).
- **Decision (proposed):** populate `research/controls/` and a build-time control register
  that binds each gate/control to **ISM / PSPF / DTA AI Policy v2.0 / NIST SSDF+AI RMF /
  SLSA**, and publish an explicit **crosswalk to the UK GDS ten principles** (adopt-and-
  localise, don't reinvent). This is the template's defensible spine.
- **Consequences:** turns "compliance is the spine" into a shippable artefact; differentiates
  on the AU gap. Risk: framework version drift — mitigated by the source-notes' retrieval
  dates + re-run cadence.

---

## Decisions for the owner

Ratify ADR-101…106 (or amend). The load-bearing ones are **ADR-102** (orchestrate, don't
rebuild), **ADR-103** (gov hard-fail), and **ADR-106** (compliance spine). **Handoff:** to
`@sprint-lead` to sequence these into a sprint.
