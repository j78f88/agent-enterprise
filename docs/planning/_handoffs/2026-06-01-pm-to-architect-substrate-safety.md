---
from: "@pm"
to: "@architect"
date: 2026-06-01
feature: substrate-safety-validation
artifact: docs/planning/validation/substrate-safety-validation.md
status: complete
notes: Reposition validated — adopt emit, build-on safety (orchestrate), greenfield only the nonce data-fence + AU-compliance template. Needs ADRs for emitter, scanner-bundling/fail-closed posture, runtime-scope boundary, and compliance-control mapping. Owner ratifies.
---

# Handoff — @pm → @architect

## Validated position (proposal-tier; owner ratifies)

Reposition agent-enterprise from "novel substrate + novel safety" to an
**AU-government-grade, vendor-neutral integration + compliance-bound template** with a
single fail-closed build gate. Full reasoning + evidence:
[`validation/substrate-safety-validation.md`](../validation/substrate-safety-validation.md).

## Technical decisions needed from @architect (ADRs)

1. **Emitter strategy** — adopt `ruler`/`rulesync` for multi-target emit vs retain `init.py`
   as the emitter. Evidence: `CLM-multitarget-is-commoditised`, `CLM-ruler-no-templating`.
   Trade-off: dependency + portability vs control + token templating.
2. **Safety-layer architecture** — orchestrate best-of-breed (Snyk Agent Scan/Invariant
   mcp-scan, OSV/Socket/Semgrep, CSA unicode lint) behind the fail-closed gate vs build
   in-house. Evidence: `CLM-buildtime-skill-gating-already-exists`,
   `CLM-residual-novelty-is-orchestration-not-primitives`.
3. **Scanner-dependency / fail-closed posture** — pin+bundle vs degrade-gracefully. Resolve
   the design-goals §8.2 open decision for the gov context. Evidence:
   `CLM-adv-scanners-not-bundled`.
4. **Runtime-scope boundary** — make the "not a runtime sandbox" boundary explicit and
   document the Operate-phase hand-off to runtime tooling (DTA AI technical standard).
   Evidence: `CLM-adv-not-runtime-operate-gap`.
5. **Differentiator design** — the nonce data-fence in resolved artefacts; confirm it is not
   present in competitors before building. Evidence:
   `CLM-nonce-data-fence-not-found-in-competitors`.
6. **Compliance-control mapping** — bind controls to ISM/PSPF/DTA-AI-Policy and map against
   the UK GDS baseline. Evidence: `CLM-uk-gds-overlap`, `CLM-no-reusable-gov-template-exists`,
   `CLM-pspf-classifications`, `CLM-adv-ism1730`.

## Constraint

Output is proposal-tier. ADRs are PROPOSED until owner ratifies. Honour the kill criteria
in the validation doc §5 (re-run research if a falsifier fires).
