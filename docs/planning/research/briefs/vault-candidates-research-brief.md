---
title: "Research Brief: Vault candidate sweep for agent-enterprise"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-14
---

# Research Brief: Vault candidate sweep for agent-enterprise

**Date:** 2026-06-14
**Requested by:** user (sourced from personal R&D Obsidian vault)
**Type:** Research brief / feed — INPUT to `@researcher`, not a research output
**Scope:** External research on the enterprise-lensed patterns/concepts captured in the vault as candidates for implementation into agent-enterprise (security + process controls). One research doc per cluster.

> This is a feed, not a synthesis. Each cluster below is a self-contained `@researcher` task — copy one at a time. Researcher surfaces patterns + adoption + failure modes with citations; it does **not** recommend or validate. Kill/keep is `@pm`'s call. Provenance slugs in `[[...]]` and `concept-*` refer to notes in the source vault.

## How to use

1. Run clusters **1–6** first — they map directly to agent-enterprise's mission (security + process controls). Clusters 7–8 are adjacent (context/cost efficiency); run only if wanted.
2. Paste one cluster's task into `@researcher`. Each produces one research doc in `docs/planning/research/`.
3. After research lands, hand off to `@pm` for validation/prioritisation (the "research then triage" path).

---

## ★ Cluster 1 — Sandboxing & runtime isolation

Research how production agent frameworks and coding agents implement runtime sandboxing and isolation for tool-using agents — process/container sandboxes, isolated worktrees, OS-level confinement, and execution-mode separation. For each pattern give concrete mechanism, which tools ship it, adoption scale, and failure modes (sandbox escapes, prompt-injection bypass, abandoned approaches).

**Vault candidates:** `[[agent runtime safety boundary]]`, `concept-sandboxed-agent-actions` / `concept-tool-using-agents-need-sandboxing`, `concept-running-multiple-coding-agents-in-isolated-worktrees`, `pattern-mode-separation`.

## ★ Cluster 2 — Identity, credentials & permissions

Research how enterprise agent platforms handle agent identity, centralised credential/secret storage for tool servers, and permission/RBAC models. Concrete data models, where secrets live, how scopes are granted, adoption scale, and failure modes (leaked secrets, over-broad scopes, retired schemes).

**Vault candidates:** `concept-agent-credential-storage`, `concept-scaled-enterprise-agent-deployments-require-centralized-identity`.

## ★ Cluster 3 — Tool-surface control

Research how agent systems bound and gate large tool surfaces — tool-search/gateways, dynamic discovery, filesystem-style interfaces over API/MCP dumps, staged retrieval, and tool-budget limits. Concrete mechanisms, MCP's role, adoption, and failure modes.

**Vault candidates:** `[[tool surface budget]]`, `concept-large-mcp-tool-surfaces-degrade`, `concept-filesystem-style-interfaces`, `concept-staged-retrieval-and-tool-mediated-access`, `concept-mcp-open-standard`.

## ★ Cluster 4 — Evidence & verification gating

Research how production agent systems gate autonomy behind evidence and verification — executable verification loops, evidence-by-design, grounding via retrieval/tools, generator-verifier-adversary multi-agent review, and behavioral evals. Concrete designs, adoption, and failure modes (false success claims, eval gaming).

**Vault candidates:** `[[evidence gate]]`, `pattern-evidence-by-design`, `concept-agentic-coding-requires-executable-verification-loops`, `concept-grounding-through-retrieval`, `concept-generator-verifier-adversary`, `concept-production-agent-systems-require-behavioral-evals`.

## ★ Cluster 5 — Control plane & observability

Research enterprise agent control planes — tracing, guardrails, red-teaming, rollout controls, cost-quality management, audit trails. How vendors structure the control plane, adoption scale, and failure modes.

**Vault candidates:** `[[agent control plane]]`, `concept-enterprise-agent-control-planes-can-move-agents-from-prototypes`, `concept-production-agent-systems-require-trace-observability`.

## ★ Cluster 6 — Process controls & human oversight

Research process-control patterns for long-horizon coding agents — human checkpoints/approval gates, deterministic hooks enforcing workflow constraints, context-serialization handoffs, tiered returns, and schema-gated builds. Concrete mechanisms, adoption, and failure modes (goal drift, error accumulation).

**Vault candidates:** `pattern-human-checkpoints-for-long-horizon-agents`, `concept-deterministic-hooks-enforce`, `[[context serialization handoff]]`, `pattern-three-tier-returns`, `pattern-schema-gated-build`, `pattern-thin-orchestration`, `concept-long-horizon-agents-fail-three-ways`.

## Cluster 7 — Context management *(adjacent)*

Research agent context-management techniques — context graphs with decision traces vs flat memory, compaction/handoff for window decay, isolated-context subagents, distilled episodic memory. Adoption and failure modes.

**Vault candidates:** `concept-context-graphs-vs-flat-memory`, `concept-large-context-windows-degrade`, `concept-subagents-with-isolated-context`, `concept-agent-memory-is-more-useful-when-distilled`.

## Cluster 8 — Cost & model governance *(adjacent)*

Research cost/model governance for agent fleets — model right-sizing ladders, routing planning-to-strong / execution-to-cheap, prompt caching, deliberate token-spend budgeting. Adoption and failure modes.

**Vault candidates:** `pattern-model-right-sizing-ladder`, `concept-routing-planning-to-stronger-models`, `concept-prompt-caching`, `concept-token-spend-has-four-quadrants`.

---

## Provenance

Candidate pool extracted 2026-06-14 from the source vault's enterprise-lensed patterns (`20_patterns/`) and concepts (`30_concepts/`), cross-referenced against `50_projects/project-agent-enterprise.md` and `60_mocs/Enterprise-ready & robust MOC.md`. Clusters 1–6 are the security/process-control core; 7–8 are efficiency-adjacent. This brief carries no recommendations by design.
