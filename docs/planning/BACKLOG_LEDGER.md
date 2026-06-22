# Backlog Ledger

Single source of truth for all backlog item status. Detail and context live in BUG_BACKLOG.md and HANDOFF_REJECTIONS.md — this file tracks status only.

> **Phased feature work** from the 2026-06-15 vault-candidate validation sweep is tracked at the phase level in `ROADMAP.md` (`@pm` owns the why/when). Items are added here as discrete backlog entries when they are concrete and ready to enter planning — not bulk-imported, to avoid duplicating the roadmap.

| ID | Type | Source | Age | Def | Sprint | Status | Blocked | Draft | Notes |
|----|------|--------|-----|-----|--------|--------|---------|-------|-------|
| ITEM-006 | bug | BUG-003 | 0 | 0 | 2 | done | | | Onboarding missing Claude Code /command setup |
| ITEM-007 | bug | BUG-004 | 0 | 0 | 2 | done | | | Planner-mode workflow bypassed before approved sprint draft |
| ITEM-008 | bug | BUG-005 | 0 | 0 | 1 | done | | ../archive/onboarding-path-resolution-remediation-draft-plan.md | RESOLVED Sprint 1 — companion-file resolution, skills_deploy_dir cross-refs, inline code-span resolution + escape; all 3 BUG-005 mechanisms closed |
| ITEM-009 | audit-finding | Sprint 1 review SUGGESTION #2 | 1 | 0 | 2 | done | | | `SOURCE_STYLE_REFS` in tests/test_init.py is a hardcoded 7-item allowlist; consider deriving it from config/resolved tree instead of maintaining by hand |
| ITEM-010 | debt | Sprint 1 retro | 1 | 0 | 2 | done | | | Decide whether SPRINTS.md and BACKLOG_LEDGER.md hold real repo history or stay as template demo content |
| ITEM-011 | debt | Sprint 1 retro | 1 | 0 | 2 | done | | | Consider a CI check asserting all docs use config/project.config.example.yml for the canonical build command |
| ITEM-012 | bug | BUG-006 | 0 | 0 | 2 | done | | | init.py has no automated deploy-copy or token-free guardrail for the .github tree (distinct from BUG-005) |
| ITEM-013 | debt | Sprint 2 retro (@security/@reviewer SUGGESTION) | 2 | 0 | 3 | done | | | jsonschema.RefResolver deprecated in jsonschema ≥4.18; pre-existing warning, no immediate failure, migrate to jsonschema.validators API before upgrading jsonschema |
| ITEM-014 | feature | session review 2026-06-10 | 0 | 0 | 3 | done | | ../archive/claims-foundation-draft-plan.md | ADR 0008: define supported-mode-implementation promotion contract; revise command-centre/PLAN.md non-goal |
| ITEM-015 | debt | session review 2026-06-10 | 0 | 0 | 3 | done | | ../archive/claims-foundation-draft-plan.md | Stale drafts cleanup: archive completed draft plans, relocate handoff, triage remaining |
| ITEM-016 | debt | session review 2026-06-10 | 0 | 0 | 3 | done | | ../archive/claims-foundation-draft-plan.md | CI builds all profiles/*.config.yml, not just the example config |
| ITEM-017 | feature | session review 2026-06-10 | 0 | 0 | 3 | done | | ../archive/platform-parity-draft-plan.md | Platform parity: ungate agent generation; native Claude Code subagents, Cursor commands, Codex AGENTS.md target |
| ITEM-018 | feature | session review 2026-06-10 | 0 | 0 | 3 | done | | ../archive/mode2-dispatcher-promotion-draft-plan.md | Promote Mode 2 file-queue dispatcher to supported implementation in src/ per ADR 0008 |
| ITEM-019 | feature | session review 2026-06-10 | 2 | 2 | 3 | open | | drafts/mode3-coordinator-promotion-draft-plan.md | Promote Mode 3 registry coordinator to supported implementation in src/ per ADR 0008 |
| ITEM-020 | feature | session review 2026-06-10 | 2 | 2 | 3 | open | | drafts/adopter-bootstrap-draft-plan.md | Adopter bootstrap: init.py --target/--bootstrap one-line setup into external projects |
| ITEM-021 | debt | Sprint 3 review SUGGESTION | 0 | 0 | 3 | done | | | CI: run canonical example-config build last so post-build guardrail steps validate the canonical tree, not the last profile build |
| ITEM-022 | debt | Sprint 3 review SUGGESTION | 2 | 2 | 3 | open | | | ADR 0008 wording: disambiguate "promotion contract" vs 05-promotion-contract.md; add explicit ADR 0004 cross-reference |
| ITEM-023 | debt | Sprint 4 review SUGGESTION | 1 | 1 | 4 | open | | | Onboarding skill walks adopters through project.config.yml but build/deploy examples must use the canonical example config to satisfy the guardrail — decouple (exemption or placeholder phrasing) |
| ITEM-024 | debt | Sprint 5 review (test-author finding a) | 0 | 0 | 5 | open | | | callable-contract.md non-enterprise example invalid against callable-v1 schema (missing kind/version/applies_to) — frozen surface; fix as additive informative note or at -v2 |
| ITEM-025 | debt | Sprint 5 review SUGGESTIONs S3/S4/d/e | 0 | 0 | 5 | open | | | dispatch.py hardening: containment for --summary-out/--callables; distinct exit when all callables invalid; scope _resolve_python_entry sys.path insertion; requeue/recover UX |
| ITEM-026 | debt | Sprint 5 review SUGGESTIONs S5/S6 | 0 | 0 | 5 | open | | | queue journal robustness: document tail-tolerance assumption, wrap bad seq in QueueStateError, journal compaction, directory fsync |
| ITEM-027 | feature | ROADMAP Phase A · validation 2026-06-15 (Cluster 2 P6) | 0 | 0 | — | open | | | Secrets-hygiene guard (NEW, roadmap top pick): build-time validator that resolved + emitted MCP/agent config carry no inline secrets — extend `SecurityValidator.detect_secrets` from input-only to the output/emit path + `.gitignore`/external-manager requirement. Extends DG-6/DG-1; threats T1/T5 |
| ITEM-028 | feature | KNOWLEDGE-OPS-MIGRATION-RUNBOOK · 2026-06-22 | 0 | 0 | — | open | | | EPIC tracking row: Knowledge Ops migration E0–E7 (plan in priv-obsidian _meta/docs/KNOWLEDGE-OPS-MIGRATION-RUNBOOK.md). Bounded agent-enterprise worker execution; Vex/Hermes owns reconciliation. E0 complete: ko-snapshot-2026-06-22 tag on vault+cockpit, archive root created, KO-002 contained (plaintext dup quarantined outside git, .hermes/.env chmod 600) — key rotation deferred by Josh as accepted-risk override, no 401 claim. Per-phase status lives in the runbook checklist. |
| ITEM-029 | feature | KNOWLEDGE-OPS-MIGRATION-RUNBOOK E4 · 2026-06-22 | 0 | 0 | — | open | | | KO-E4 Mode 2 rails wiring (handoff for dispatch host; no second scheduler). Engine behavior shipped in youtube-sync 89722bc: `python -m engine.promote --apply` = verdict-gated source promotion (00_import→10_sources); `python -m engine.process` = corroboration-gated + dedup-aware concept writer; `python -m engine.prune --concepts --apply` = decay→archive (conservative, block-only, non-destructive). These CLIs are the rails-dispatchable units; floor + statuses live in youtube-sync config.json `promotion`. TODO rails: register as Mode 2 callable(s) via queue/inbox dispatch + schedule. galactic-council escalation feature-flagged OFF (config promotion.council_escalation_enabled=false) until council ready. CAUTION: do NOT run `prune --concepts --apply` live until verdicts.json has full current coverage — read-only dry-run flags curated concepts when coverage is incomplete. |
| ITEM-030 | research | KNOWLEDGE-OPS-MIGRATION-RUNBOOK E6 KO-E6-3 · 2026-06-22 | 0 | 0 | — | open | | | KO-E6-3 tag-collapse PROPOSAL (policy/governance — human-applied; agent does NOT self-edit tags.md). Proposed: collapse vault tag namespaces to stage/, lens/, topic/; retire format/, backfill, and redundant meta/ content tags. Source: design §5 + runbook E6. Surfaced as a steer row per runbook ("tag changes touch policy → BACKLOG_LEDGER type=research row, human applies") + Vex E6 guardrail #6 (no taxonomy change without explicit Josh approval). E6 commit ko(e6): slim shipped only the mechanical parts (4 dashboard stubs + 5 process docs → _meta/docs/_governance/); this tag change is intentionally deferred to a human decision. |
| ITEM-031 | research | KNOWLEDGE-OPS-MIGRATION-RUNBOOK E6 KO-E6-2 · 2026-06-22 | 0 | 0 | — | open | | | E6 relocated 5 process docs to priv-obsidian _meta/docs/_governance/ (POLICY, DIGEST-SPEC, CANON-BASELINE, GITHUB-SYNC-PLAN, LEARNING-MAINTENANCE) per design §5. Obsidian [[wikilinks]] resolve by basename (unaffected); 05_canon/_README.md path ref corrected in the E6 vault commit. TOOLING FOLLOW-UP (rails/hermes domain — agent did NOT hand-edit generated/governance _meta files): two hermes artifacts still reference the OLD paths by string — (1) _meta/review-queue.md ("Overwritten by hermes each run per _meta/docs/POLICY.md section 3" + 2 handle_or_note=_meta/docs/POLICY.md task pointers) → point hermes' review-queue generator at _meta/docs/_governance/POLICY.md; (2) _meta/hermes-handoff-learning.md paste-block "Per _meta/docs/LEARNING-MAINTENANCE.md §1,§4" → update to _meta/docs/_governance/LEARNING-MAINTENANCE.md. Non-breaking (docs fully present at new path); these are reference-string updates only. |

<!-- 
Column guide:
  ID       — ITEM-NNN (sequential, zero-padded)
  Type     — bug | debt | feature | carry-over | audit-finding | research | rejection
  Source   — BUG-NNN, REJ-NNN, or free text
  Age      — sprints since first logged
  Def      — times deferred (≥3 → P0 mandatory, ≥5 → must resolve or kill)
  Sprint   — sprint number first logged
  Status   — open | assigned | done | killed
  Blocked  — blocker description or blank
  Draft    — draft filename or blank
  Notes    — free text

Governance:
  @bug     — appends bug items
  @planner — appends feature, debt, rejection items; marks done/killed
  @sprint-lead — updates status to assigned during sprint, done at completion
-->
