# agent-enterprise — Roadmap

> **Living roadmap.** Phases + rationale, not sprint-level tasks. `@planner` turns
> a phase item into a scoped sprint; `@pm` owns this file and the *why/when*.
> Last updated: 2026-06-15.

## Thesis

agent-enterprise is a **build-time** assurance toolset for AI-agent
consumption — it resolves, scans, and gates skills/instructions/agents
*before* they are deployed (see `docs/planning/vision/safety-in-consumption-design-goals.md`).

Two corrections shape this roadmap, both confirmed 2026-06-15:

1. **Novelty is not the goal — proven-and-evergreen is.** The 2026-06-01
   re-baseline disconfirmed the original "novel safety substrate" claims. That
   is not a retreat. Australia has no frontier-model development and minimal
   internal model R&D, so the right ambition for this context is to **curate
   robust, proven controls into an evergreen toolset** — not to chase frontier
   usage patterns. The maturity of a control is a *feature*, not a reason to
   skip it.

2. **AU compliance is a design lens, not a hard gate.** The toolset must be
   *able to operate within* Australian government compliance (PSPF, ISM,
   Essential Eight), which broadly inherit international frameworks (NIST AI
   RMF, ISO/IEC 42001, OWASP ASI, EU AI Act). We map to those and note AU
   alignment; we do **not** block delivery on an AU-native control corpus that
   barely exists. Specific government bans (e.g. DeepSeek-class vendor bans) are
   handled as **explicit exclusions** in config, not as a reason to stall.

## Evidence base

This roadmap is built from the 2026-06-15 validation sweep of the vault-candidate
research (`docs/planning/research/briefs/vault-candidates-research-brief.md`).
Eight clusters → eight validation records in `docs/planning/validation/`,
covering **59 distinct patterns**. Every cluster, validated independently,
converged on the same frame: **curate/map mature controls; do not re-build
vendor runtime.** Tally: 15 VALIDATED (as controls/already-built capability),
24 REFRAMED (→ control objectives), 9 DEFERRED, 8 REJECTED, 3 NEW (genuine
in-scope builds).

| Cluster | Record |
| --- | --- |
| 1 — Sandboxing & runtime isolation | `validation/sandboxing-runtime-isolation-validation.md` |
| 2 — Identity, credentials & permissions | `validation/identity-credentials-permissions-validation.md` |
| 3 — Tool-surface control | `validation/tool-surface-control-validation.md` |
| 4 — Evidence & verification gating | `validation/evidence-verification-gating-validation.md` |
| 5 — Control plane & observability | `validation/control-plane-observability-validation.md` |
| 6 — Process controls & human oversight | `validation/process-controls-human-oversight-validation.md` |
| 7 — Context management *(adjacent)* | `validation/context-management-validation.md` |
| 8 — Cost & model governance *(adjacent)* | `validation/cost-model-governance-validation.md` |

## Current state (shipped, as of Sprint 5)

These are **done** — the roadmap below builds on them, and Phase B *maps* them
to compliance frameworks rather than re-planning them:

- Deterministic build + hash-chain (DG-10); post-deploy token-free guardrail.
- `SecurityValidator` (T1): config whitelist / secrets / paths; `license_denylist`.
- Mode 2 file-queue dispatcher — deterministic, journaled, crash-recoverable
  (validates Cluster 6 "thin orchestration" as already-built).
- Tiered/structured subagent returns + schemas (validates Cluster 6
  "tiered returns" as already-built).
- Platform-parity emit (Claude Code subagents, Cursor commands, Codex AGENTS.md).

---

## Phase A — Build-time assurance core *(the evergreen toolset)*

The genuinely buildable, in-scope increments. Each extends an existing design
goal and is a proven control, not a novel mechanism. **Highest priority** — this
is the product's spine.

- **Secrets-hygiene guard** *(NEW, Cluster 2)* — CI/build-time validator that
  resolved + emitted MCP/agent config carry no inline secrets; `.gitignore` +
  external-manager requirement. *Extends DG-6 (scanner chain), DG-1; closes the
  cluster's single largest documented harm source. Threats T1/T5.* **Top pick.**
- **Deny-by-default tool allow-list + capability schema fields** *(NEW, Cluster 2;
  overlaps Cluster 3 tool-budget)* — require explicit per-agent tool allow-lists,
  forbid wildcards. *Extends DG-4 (least-capability manifests). Deconflict the
  allow-list scope with Cluster 3 before planning.*
- **Tool-surface budget + namespacing discipline** *(REFRAMED, Cluster 3)* —
  required config: bounded tool count; unique namespaces to close last-registered-wins
  shadowing. *Extends DG-4/DG-6. Cheapest, highest-leverage controls in Cluster 3.*
- **Accountable-human / agent-sponsor schema field** *(REFRAMED, Cluster 2)* —
  mandatory "named accountable human" field on every agent definition. *Extends
  DG-2 (provenance) / DG-4.*
- **Banned-vendor/model exclusion list** *(NEW from the AU-lens correction)* —
  config denylist for government-banned models/vendors (DeepSeek-class), mirroring
  `license_denylist`. *Extends DG-5; makes "operates within AU compliance" concrete.*
  **Scope note for `@planner`:** this item is **thesis-derived (thesis #2, the
  AU-lens correction), NOT backed by any of the 59 validated patterns.** It has no
  validation verdict behind it — it traces to the roadmap thesis, not to the
  vault-candidate sweep. Acceptable as a derived in-scope build, but plan it on
  the strength of the AU-compliance rationale, not on a pattern validation record.
- **Thin policy stubs** *(Cluster 1 P2/P4, mixed-frame)* — two-phase-network
  profile (setup-online → agent-offline, secrets wiped); default permission-mode
  + protected-path policy. *Extends DG-4/DG-8. Policy artifacts, NOT isolation
  engines — must not drift into re-implementing vendor primitives.*

## Phase B — Compliance-mapping layer *(the evergreen product surface)*

Converts the curated controls into the deliverable that makes the toolset
*demonstrably* compliance-ready. This is where REFRAMED controls live.

- **Audit-evidence schema + multi-framework crosswalk** *(VALIDATED anchor,
  Cluster 5)* — reference schema for tamper-evident audit evidence; crosswalk
  DG-1…DG-10 + controls → NIST AI RMF / ISO 42001 / OWASP ASI / EU AI Act, with
  the **AU lens** (PSPF/ISM/Essential Eight) as an alignment column. *Extends
  DG-9. Flagged by validation as the single most defensible deliverable.*
- **Control catalogue** — the 24 REFRAMED controls organised by domain (identity,
  tool-surface, evidence-gating, control-plane), each as a control objective with
  documented caveats and its framework mappings.
- **"Gate-becomes-target" assurance catalogue** *(NEW template content, Cluster 4)*
  — the four Cluster-4 failure classes (reward hacking, fabrication/false-success,
  verifier unreliability/collusion, flaky/weak oracles) + layered-defense
  rationale. *Extends DG-1 ("gates are the control, prose is not"). Source:
  `validation/evidence-verification-gating-validation.md` (flagged decision #2).
  Note: approval-fatigue (process-controls, Cluster 6) and guardrail-bypass
  (control-plane, Cluster 5) are related failure modes owned by other clusters —
  the template may cross-reference them, but they are not part of this Cluster-4
  catalogue.*
- **Residual-risk register** — the controls that are real but have **no shipped
  default-on implementation**: egress / lethal-trifecta (Cluster 1 P5 — the
  cluster's primary unsolved risk), guardrail-bypass ASR (Cluster 5 P3), memory
  poisoning / OWASP ASI06 (re-homed from Cluster 7). Document honestly as residual.

## Phase C — Hardening & already-built mapping

Lower-urgency. Mostly documentation of shipped capability + opt-in hardening.

- **Map already-shipped capability** into the Phase-B catalogue: Mode 2 thin
  orchestration, tiered returns (Cluster 6); determinism (DG-10). Documentation,
  not build.
- **Declared cost/time ceiling** (Cluster 8 / DG-4 / T8) — `maxUsd`/`timeoutMs`/
  kill-switch as declared manifest fields. This is **planned scope, not yet
  shipped**: it lives in the design-goals doc's capability-manifest plan but no
  `maxUsd` code exists in `src/` (the executed Sprint 4 was Platform Parity,
  Sprint 5 the Mode 2 Dispatcher). Therefore this is a **real build** for
  `@planner`, not a documentation-only mapping — do not file it under
  already-shipped. Low-cost and in-boundary, but unbuilt.
- **Risk-scoped human step-up** *(REFRAMED, Cluster 2)* — HITL only for a defined
  high-risk/irreversible action class (avoids approval fatigue). *Extends DG-8.*
- **Dynamic/leased-credential guidance** *(REFRAMED, Cluster 2)* — require short
  governed TTL + documented Secret-Zero bootstrap, not bare "use Vault."

---

## Parked *(DEFERRED — valid, blocked on a dependency)*

Each carries its unblock condition. Revisit when the condition is met.

| Item | Cluster | Unblock condition |
| --- | --- | --- |
| Federated delegation token (ID-JAG) | 2 | MCP enterprise-auth / OAuth-for-AI-agents spec stabilises (~2027–28) |
| SPIFFE/SPIRE workload identity | 2 | WIMSE agent extension finalised; long-lived service agents only |
| Cedar/OPA policy engine, ReBAC, SCIM/AuthZEN | 2 | Runtime enforcement enters scope / specs converge |
| Forge-proof verification-evidence artifact | 4 | Behind a verify-first kill gate; build pipeline residual-defensible |
| Build-time tool-description scan + checksum-pin | 3 | Consumption-pipeline scope confirmed; reconcile with Cluster 1 ownership |
| Context-serialization handoff | 6→7 | An observed context-loss failure justifies the cost |
| FinOps showback/chargeback control | 8 | Phase-B control catalogue exists to reference it |
| 100%-capture rule for high-risk actions | 5 | High-risk-agent-action taxonomy authored |

## Non-goals *(REJECTED — candidate `NON_GOALS.md` additions)*

These are out-of-boundary for a build-time toolset (vendor runtime / dev-ergonomics).
`@planner` owns `NON_GOALS.md` and must sign off before they are added there.

- Worktree-based isolation **as a compliance control** (dev-ergonomics; market
  retreating — Crystal/vibe-kanban sunsetting). *Cluster 1.*
- Building a tool-retrieval router, code-mode runtime, or MCP gateway. *Cluster 3.*
- Building a graph-memory store, subagent orchestrator, or distilled-memory
  runtime. *Cluster 7.*
- LLM request-routing or prompt-caching **as our features** (runtime, out of
  build-time boundary). *Cluster 8.*
- Permitting "dynamic user" inheritance for privileged agents *(prohibition
  control — candidate standing no). Cluster 2.*

---

## Cross-cutting notes

- **Evidence honesty.** Adoption/scale figures in the source research are
  vendor-sourced; CVE IDs/CVSS are unverified against NVD. Any figure or CVE that
  reaches a government-facing control document must be verified against the
  primary source first. No roadmap verdict relies on a vendor statistic.
- **Cross-cluster overlaps to deconflict before planning:** egress controls
  (Clusters 1/3/5), the tool allow-list (Clusters 2/3), and memory-integrity
  (Cluster 7 → security clusters).
- **AU-specific mapping is an enhancement, not a blocker** (per thesis #2). A
  follow-up `@researcher` pass on PSPF/ISM/Essential Eight specifics would
  sharpen the Phase-B crosswalk but is not on the critical path.
