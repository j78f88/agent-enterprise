---
title: "Research: Agent-skill segment — enterprise-readiness patterns"
status: untrusted
trust: untrusted
classification: OFFICIAL
date: 2026-05-28
---

> ⚠️ **QUARANTINED — `untrusted`, NOT canonical.** Prior-session research (2026-05-28)
> authored before the knowledge base existed, using the old prose template with no
> per-claim provenance. It **cannot back a canonical claim** until retro-conformed into
> [source-notes](../sources/README.md) / [claims](../claims/README.md) and registered in
> [`INDEX.md`](../INDEX.md). See [`_meta/trust-policy.md`](../_meta/trust-policy.md).

# Research: Agent-skill segment — enterprise-readiness patterns for agent-enterprise-e1

**Date:** 2026-05-28
**Requested by:** user
**Scope:** Full sweep + graveyard across three overlapping segments — (S1) curated skill/plugin packs, (S2) multi-tool / multi-target agent distribution, (S3) enterprise governance of prompt artifacts (signing, scanners, marketplace governance) — read against agent-enterprise-e1's current state. All three angles in play: winning patterns, graveyard / failure modes, contributor/user complaints. No recommendations — kill/keep is `@pm`'s call.

> Surfaces patterns + evidence + failure modes. "Fit" is observed-relevance, not a build/adopt call. All star/release/push figures via `gh` API on **2026-05-28**.

## Synthesis — the gap, the tools, the maturity hierarchy, the catch

**The gap** (refreshed from 2026-05-25 org sweeps). Of six ecosystem-defining repos checked again this morning, **only one ships any version**: `addyosmani/agent-skills` (3 tags). The five biggest — `anthropics/skills` (142k★), `anthropics/claude-plugins-official` (28k★), `anthropics/knowledge-work-plugins` (17k★), `VoltAgent/awesome-agent-skills` (23k★), `agentskills/agentskills` (the open spec, 19k★) — all still ship **0 releases / 0 tags** three days later. The Dim-A versioning gap is not a quirk of one org; it is the *segment default*. e1's forward requirements (R1 no-dangling-references, R2 researcher honesty-guard) are codified but not yet implemented.

**The tools** — sorted by what they prove e1 can borrow:

| Layer | Best-in-segment example | What it proves |
| --- | --- | --- |
| Multi-tool distribution | [obra/superpowers](https://github.com/obra/superpowers) — **209,873★**, MIT, **27 tags / 5 releases**, 8 harnesses (Claude/Codex CLI+App/Droid/Gemini/OpenCode/Cursor/Copilot), 4 envelope dirs, 3 primary instruction files | A prose-pack repo CAN ship semver + tags + per-tool install flows + structured release notes + automated mirror tooling (`sync-to-codex-plugin`) |
| Multi-target installer | [vercel-labs/skills](https://github.com/vercel-labs/skills) — 20,385★, **28 tags**, `npx skills add owner/repo`, **51+ agents** | "One source → many tools" can be a CLI installer (not a per-target hand-maintained dir tree). Husky pre-commit + `scripts/validate-agents.ts` + `sync-agents.ts` + `execute-tests.ts` — the tooling shape of a real generator |
| Validator-as-governance | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) `scripts/validate-skills.js` | Anti-bypass design: **exemptions live in the validator, not in skill frontmatter**; cross-reference resolver = e1's R1 acceptance test, already implemented |
| Defensive scanning | [snyk/agent-scan](https://github.com/snyk/agent-scan) — 2,487★, Apache-2.0, **30 tags**, PyPI; [cisco-ai-defense/skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) — 2,073★, **SARIF output** | Real CLI scanners exist; 15+ codified threat codes; Cisco closes the **SARIF gap** prior research flagged as missing on the Anthropic side |
| Open standard + conformance | [agentskills/agentskills](https://github.com/agentskills/agentskills) — 19,499★, Apache-2.0 spec / CC-BY-4.0 docs | The standard is now formally governed: Client Showcase, `adding-skills-support` guide, multiple logoed adopters |
| Signed/provenanced distribution | `skills-oci` (Cosign + SLSA attestation), `sigstore/sigstore-a2a` (Agent-Card signing), NVIDIA Verified Agent Skills, GitHub Artifact Attestations | The signing/SLSA-provenance path that was *absent* in the Anthropic sweep is being pioneered outside it — early but real |

**The maturity hierarchy.** addyosmani isn't the segment leader — **obra/superpowers is**, by 4.5× the stars, 9× the tags, 2× the harness count, and with a structured release-notes practice (`v5.1.0` documents a 94% PR rejection rate from "AI-generated slop" and adds a contributor checklist *for AI agents*). Vercel ships the segment's only general-purpose multi-target installer. Snyk and Cisco ship working scanners with SARIF + pre-commit integration. The open spec exists and has logoed adopters. The signing/provenance path exists (`skills-oci`, `sigstore-a2a`, NVIDIA) but adoption is early.

**The catch.** This segment is on fire. **341 malicious skills found in ClawHub** (Feb 2026, The Hacker News); **5 of the top-7 most-downloaded ClawHub skills were malware**; Snyk's **ToxicSkills/ClawHavoc** study found **1,467 malicious payloads** across 3,984 skills scanned. Snyk's number for the user: "**13% chance** any skill installed in the past month contains a critical security flaw." ClawHub survived only via mandatory review + VirusTotal + Gemini Code Insight scanning post-crisis; Vercel's `skills.sh` adopted triple-scan (Gen Digital + Socket + Snyk). The *distribution mechanism* e1's eventual skill layer will plug into is a contested supply chain with documented adversaries, and most segment leaders ship neither signing nor provenance — only addyosmani's MIT+tags and obra's MIT+semver are even *pinnable*. Cisco's scanner is admirably explicit: "**No findings ≠ no risk.**"

## Target characterised (verbatim lens)

`agent-enterprise-e1` has pivoted from v2's config-driven Python+Jinja2 generator to a **TypeScript/Node generator structured as Ports & Adapters** (ADR-003, Accepted 2026-05-27), whose dominant concern is the **platform-provider abstraction** (ADR-005: SCM hosts + issue trackers via typed ports). Source today is the adapter core (`src/core/ports/issue-tracker.ts`, `src/adapters/fake.ts`, `src/cli/composition-root.ts`, a `tsx` smoke test). **The skill layer is a forward requirement, not built** (`docs/sop/skill-layer-requirements.md`: R1 no-dangling-references, R2 researcher session-end + honesty-guard). Process is enforced **asymmetrically** (ADR-006): ungated research bench, hard `commit-msg` + `promote.sh` gates at boundaries, server-side branch protection deferred. MIT (ADR-004), Node ≥24. Two structural facts shape what this sweep can transfer: e1 abstracts the *enterprise-platform* layer (GitHub/AzDO/Linear/Jira) — these segment repos abstract the *agent-tool* layer (Claude/Codex/Gemini/Cursor/…); and e1 ships **prompts** not a model, so its threat surface is the segment's threat surface once it distributes.

## Method

`gh` REST/GraphQL searches across `agent skills`, `claude skills`, and `claude plugin marketplace` queries (top 30 by stars each, 2026-05-28); per-repo `repos/*` (stars/forks/license/pushed/archived), `releases`, `tags`, recursive `git/trees`, and raw content via `contents` + `Accept: application/vnd.github.raw` for READMEs, manifests, CI workflows, validators, scanners, and skill-anatomy docs. Independent triangulation via web search for the ClawHub/ClawHavoc/ToxicSkills supply-chain timeline, SLSA/Sigstore/OCI signing precedents, and contributor/user complaint sources. Prior research (2026-05-25 Anthropic/OpenAI/Microsoft org sweeps) used as the baseline for what changed, and refreshed in-line.

## Apps / sources surveyed (≥10 surface scans across the three segments)

### S1 — Curated skill/plugin packs

| Repo | ★ | License | Releases / tags | Last push | Notable signal |
| --- | ---: | --- | ---: | --- | --- |
| [obra/superpowers](https://github.com/obra/superpowers) | 209,873 | MIT | **5 / 27** | 2026-05-27 | 8 harnesses, 4 envelope dirs, structured release notes, sync-to-codex-plugin |
| [anthropics/skills](https://github.com/anthropics/skills) | 142,067 | none | 0 / 0 | 2026-05-19 | The reference; still 0 SPDX, still 0 tags (gap from 2026-05-25 persists) |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 46,529 | MIT | **3 / 3** | 2026-05-24 | Validator + install-CI; described in detail below |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | 33,962 | MIT | 0 / 0 | 2026-05-28 | Copilot equivalent: `.github/plugin/marketplace.json` + 10+ CI checks (line-endings, plugin-structure, contributor-check, codespell, duplicate-resource-detector) |
| [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | 33,320 | MIT | — | 2026-05-28 | Domain-specific (Obsidian) — niche-pack pattern |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | 27,210 | none | 0 / 0 | 2026-05-27 | Skills as **TS packages with build steps + tests** (`packages/react-best-practices-build/`, `packages/vercel-optimize-tests/`) |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 26,286 | MIT | — | 2026-05-28 | Vertical pack (science) — same shape as Anthropic's `knowledge-work-plugins` |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 23,358 | MIT | 0 / 0 | 2026-05-27 | The curated meta-list ("1000+ skills") |
| [muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | 16,087 | MIT | — | 2026-05-28 | Context-engineering vertical |
| [phuryn/pm-skills](https://github.com/phuryn/pm-skills) | 11,683 | MIT | — | 2026-05-28 | PM vertical ("100+ agentic skills, commands, plugins") |
| [google/skills](https://github.com/google/skills) | 10,793 | Apache-2.0 | 0 / 0 | 2026-05-27 | Includes a first-party **`agent-platform-skill-registry`** skill — registry pattern |
| [antfu/skills](https://github.com/antfu/skills) | 5,083 | MIT | 0 / 0 | 2026-05-01 | TS-native: `meta.ts`, `scripts/cli.ts`, pnpm-workspace, ESLint on prose; `instructions/` separated from `skills/` |
| [browserbase/skills](https://github.com/browserbase/skills) | 3,444 | none | — | 2026-05-27 | Vendor pack |
| [simonw/claude-skills](https://github.com/simonw/claude-skills) | 922 | none | 0 / 1 | 2025-12-12 | Simon Willison's snapshot of Claude's `/mnt/skills` — useful as **provenance reference** for what Anthropic ships internally |
| [snyk-labs/toxicskills-goof](https://github.com/snyk-labs/toxicskills-goof) | 9 | none | — | 2026-05-07 | Snyk's deliberately-vulnerable "Juice Shop for skills" — research artifact |

### S2 — Multi-tool / multi-target distribution

| Repo | ★ | License | Releases / tags | Notable signal |
| --- | ---: | --- | ---: | --- |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | 20,385 | none | **28 / 28** | `npx skills add owner/repo` — 51+ agents; Husky pre-commit; validate/sync/test scripts; ThirdPartyNoticeText.txt |
| [agentskills/agentskills](https://github.com/agentskills/agentskills) | 19,499 | Apache-2.0 (code) / CC-BY-4.0 (docs) | 0 / 0 | The formal open standard, Client Showcase, adding-skills-support guide |
| Setup docs (in addyosmani/agent-skills) | — | — | — | Per-tool setup docs for Cursor, Copilot, Gemini CLI, Windsurf, OpenCode, Kiro, Codex — 7 hand-rendered envelopes |

### S3 — Enterprise governance, scanners, signing

| Repo / project | ★ | License | Releases / tags | Notable signal |
| --- | ---: | --- | ---: | --- |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | 28,275 | none | 0 / 0 | The governed marketplace: policy scan + SHA-pinned externals + nightly bumps (detailed in prior research) |
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | 17,399 | Apache-2.0 | 0 / 0 | Role-as-plugin (11 verticals + `cowork-plugin-management`) |
| [snyk/agent-scan](https://github.com/snyk/agent-scan) | 2,487 | Apache-2.0 | **30 / 30** | PyPI `snyk-agent-scan`; auto-discovers MCP + skills across 13 agents × 3 OSes; 15+ documented threat codes (E001 PI, E002 Tool Shadowing, E004/E006 skill injection/malware, W007/W008 credentials/secrets, ToxicFlows) |
| [cisco-ai-defense/skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) | 2,073 | NOASSERTION | — | PyPI `cisco-ai-skill-scanner`; **SARIF output**; reusable GH Action; pre-commit hook; YAML+YARA + LLM-as-judge + behavioral dataflow; threat taxonomy doc |
| [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) | 137 | Apache-2.0 | 0 / 0 | Community marketplace variant — slow growth (124→137 in 3 days) |
| `skills-oci` ([salaboy.com](https://www.salaboy.com/2026/04/19/manage-and-distribute-skills-with-skills-oci/)) | — | — | — | Distribute skills as OCI images; Cosign sign + SLSA attestation |
| [sigstore/sigstore-a2a](https://github.com/sigstore/sigstore-a2a) | — | Apache-2.0 | — | Agent-to-Agent Card signing: embeds source revision + build env + CI workflow |
| [NVIDIA Verified Agent Skills](https://developer.nvidia.com/blog/nvidia-verified-agent-skills-provide-capability-governance-for-ai-agents/) | — | — | — | Daily catalog updates, automated+human review, risk scan, signing, machine-readable skill cards |
| GitHub Artifact Attestations | — | — | — | Publish SLSA provenance + signed SBOMs from GH Actions; free for public repos |
| npm publish provenance (Sigstore PGI) | — | — | — | Publish attestations + SLSA provenance via Sigstore public good instance |
| Pre-commit framework | — | — | — | Used by Snyk Agent-Scan + Cisco Skill-Scanner — segment's standard hook precedent |
| Husky | — | — | — | Used by vercel-labs/skills — JS-side hook precedent |

## Patterns found

Each pattern lists source apps, the user/contributor complaint, and the failure mode.

### P1 — Versioned releases on a prose-artifact repo
- **What it is:** SemVer tags + dated release notes + (ideally) version-bump automation on a repo that ships *prose* skills, not code.
- **Source apps:** `obra/superpowers` (27 tags, `.version-bump.json`, detailed `RELEASE-NOTES.md` with PR/issue numbers and deprecation rationale) — leader; `addyosmani/agent-skills` (3 tags, 6-week cadence) — second; `vercel-labs/skills` (28 tags) and `snyk/agent-scan` (30 tags) prove it scales on *tooling* repos.
- **Adoption scale:** essentially 2/6 in the top tier of *prose* repos; the Anthropic axis (5 of those 6) still ships 0 releases as of 2026-05-28.
- **User complaints:** none surfaced about *versioning*; complaints surface against the *opposite* (e.g. ClawHub pre-crisis pushed unversioned skills directly to consumers).
- **Failure mode:** addyosmani's README still installs from `@main`, not a tag — versioning exists, pinning at consumption doesn't. obra/superpowers documents specific deprecations *between* versions (legacy slash commands removed in v5.1.0) — consumers who don't pin will get breaks. Versioning without pinning trades one risk (drift) for another (silent break).

### P2 — Multi-tool distribution via per-tool envelope dirs (the dominant pattern) vs CLI installer (the converging pattern)
- **What it is:** Two competing approaches: (a) hand-maintained per-tool envelopes (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/plugins/...js`, `.gemini/commands/*.toml`, etc.) — one dir per target; (b) a CLI installer that resolves a single source to the correct target at install time (`npx skills add owner/repo --agent claude-code,opencode`).
- **Source apps:** (a) `obra/superpowers` — 8 harnesses across 4 envelope dirs + 3 primary instruction files (`AGENTS.md` / `CLAUDE.md` / `GEMINI.md`, CLAUDE.md symlinked to AGENTS.md per v5.1.0 release notes); `addyosmani/agent-skills` — 7 documented tool setups; `vercel-labs/agent-skills` ships skills as TS packages with CI per package. (b) `vercel-labs/skills` — `npx skills` resolves any repo to **51+ agents** with `--agent`, `--skill`, `--global`, `--copy`/symlink, `-y` for CI.
- **Adoption scale:** obra at 209k★, Vercel CLI at 20k★ — both real, different bets.
- **User complaints:** obra's `RELEASE-NOTES.md` v5.1.0 explicitly calls out **94% PR rejection rate driven by "AI-generated slop"** — agents fabricating problem descriptions, opening duplicates, pushing fork/domain-specific changes upstream, or wrapping with `npx skills` instead of loading the proper bootstrap. Multi-tool support PRs require a "**clean-session transcript**" as acceptance evidence.
- **Failure mode:** (a) drift — hand-maintained envelopes can diverge with no CI parity check (none of these repos has a "are `.claude` and `.gemini` payloads identical?" test). (b) installer abstracts over tools' actual capabilities — Vercel's `npx skills` "supports 51 agents" but the depth of support varies; symlink-vs-copy is a real footgun on Windows.

### P3 — Schema validator that owns its own exemptions (anti-bypass design)
- **What it is:** A CI-blocking validator whose **exemption list lives in the validator**, not in the artifact frontmatter; if an artifact tries to declare self-exemption, the validator fails loud.
- **Source apps:** `addyosmani/agent-skills/scripts/validate-skills.js` — the cleanest implementation; `github/awesome-copilot` runs `check-plugin-structure.yml` + `check-line-endings.yml` + `check-pr-target.yml` + `duplicate-resource-detector.yml` + `codespell.yml` (5+ structural gates); `vercel-labs/skills/scripts/validate-agents.ts` validates the agent registry.
- **Adoption scale:** structural validation is now standard across the top tier; addyosmani's anti-bypass design is unique among the artifacts read.
- **User complaints:** none specific to validators — but the *absence* of validation in ClawHub was singled out by every post-crisis writeup ("no infrastructure for safety" — Snyk, SentinelOne).
- **Failure mode:** addyosmani's `parseFrontmatter()` is a regex, not a YAML library (brittle on multi-line values, anchors, block scalars) — ironic for a project whose risk surface is YAML frontmatter; the dead-cross-reference check is *warning-only*; presence-checks pass on token-quality content. Validates structure, not safety.

### P4 — Anti-rationalization tables as a required, validated structural section
- **What it is:** Every skill must contain `## Common Rationalizations` (excuse → rebuttal), `## Red Flags`, `## Verification` — and CI blocks if they're absent. Structural prompt-hardening, not a red-team eval.
- **Source apps:** `addyosmani/agent-skills` (enforced via `REQUIRED_SECTIONS` in validate-skills.js); e1's own skills already use the same tables (visible in the researcher skill running this) but not validated; `obra/superpowers` uses subagent prompts (`subagent-driven-development/{implementer,spec-reviewer,code-quality-reviewer}-prompt.md`) — different shape of structural discipline.
- **Adoption scale:** the structural pattern is widespread (e1, addyosmani, anthropics/skills examples); machine-enforced presence is rarer.
- **Failure mode:** **tests presence, not content quality** — self-attested safety, not evaluated safety. Closes nothing on Dim B (no eval/red-team harness shipped in any segment repo); consistent with prior Anthropic finding #3.

### P5 — Three-layer composition with explicit anti-patterns
- **What it is:** Skills (how) / Personas (who) / Slash commands (when, = orchestrator). Rule: "the user or a slash command is the orchestrator; **personas do not invoke other personas**." Only endorsed multi-agent pattern: parallel fan-out + merge. Router personas explicitly **banned**.
- **Source apps:** `addyosmani/agent-skills` documents the catalog in `references/orchestration-patterns.md` with the rule and the ban; `obra/superpowers` ships dedicated skills for subagent orchestration (`dispatching-parallel-agents`, `subagent-driven-development` with per-role prompt files); `anthropics/knowledge-work-plugins` packages role-as-plugin.
- **Adoption scale:** consistent across the top three; differs in *how much* it's machine-enforced (rarely) vs *how much* it's downstream platform-imposed (subagents can't spawn subagents on Claude Code).
- **Failure mode:** documented, not machine-enforced; some "rules" are downstream platform constraints dressed as design choices and may not hold across e1's seven target tools.

### P6 — Progressive disclosure + token-budget discipline as a *stated* constraint
- **What it is:** SKILL.md ≤ 500 lines; description ≤ 1024 chars (validator-enforced); long reference material lives in `references/` and loads on demand; scripts preferred over inline code "because script execution doesn't consume context."
- **Source apps:** `addyosmani/agent-skills/docs/skill-anatomy.md` (1024-char limit enforced); `anthropics/skills/spec` (same shape); `agentskills/agentskills` defines the same three-stage progressive disclosure (Discovery → Activation → Execution) as the **open standard**.
- **Adoption scale:** universal across the segment — it's a property of the SKILL.md format itself.
- **Failure mode:** only the 1024-char description is enforced; the line-budget is advisory; whether the agent loads the right reference at the right moment is probabilistic — trades determinism for tokens.

### P7 — Tested, fail-open hooks (and the case for fail-closed enforcement hooks)
- **What it is:** Lifecycle hooks shipped with regression tests (assertions on JSON payload across dependency-present and dependency-missing branches), plus graceful-degradation guards (`command -v jq || exit 0`).
- **Source apps:** `addyosmani/agent-skills/hooks/session-start-test.sh` (asserts IMPORTANT-vs-INFO payload branches); `vercel-labs/skills` uses Husky for pre-commit; `snyk/agent-scan` and `cisco-ai-defense/skill-scanner` both integrate with the **pre-commit framework** (`.pre-commit-config.yaml`) — segment's standard precedent.
- **Adoption scale:** scanners use industry-standard pre-commit; per-repo hook-test discipline is rare.
- **Failure mode:** fail-open is correct for UX/caching hooks but is the **wrong default for integrity gates** — a supply-chain check that "lets it through when a dep is missing" is bypassable by removing the dep. e1's ADR-006 `commit-msg` and `promote.sh` are correctly fail-*closed*; the addyosmani pattern doesn't transfer wholesale.

### P8 — Defensive scanning of skills (the Dim-A/B tooling that didn't exist 6 months ago)
- **What it is:** Standalone CLIs that auto-discover and scan agent components (MCP configs, skills, prompts) for documented threat patterns; CI-integratable; SARIF-emitting (Cisco).
- **Source apps:** [`snyk/agent-scan`](https://github.com/snyk/agent-scan) (Apache-2.0, 30 tags, `uvx snyk-agent-scan@latest`, auto-discovers across 13 agents × 3 OSes, 15+ codified threat codes, technical report `.github/reports/skills-report.pdf`); [`cisco-ai-defense/skill-scanner`](https://github.com/cisco-ai-defense/skill-scanner) (PyPI `cisco-ai-skill-scanner`, multi-engine: YAML+YARA + LLM-as-judge + behavioral dataflow, **SARIF output**, reusable GH Action workflow, threat taxonomy doc, pre-commit hook).
- **Adoption scale:** 2.5k★ + 2k★ respectively — small relative to packs, but these are the products users *run on* the packs.
- **User complaints:** Snyk's tool requires `SNYK_TOKEN` (auth wall); both scanners disclaim with notable honesty — Cisco: "**No findings ≠ no risk … Coverage is inherently incomplete … Human review remains essential**"; Snyk: scanning MCP configs *executes* the commands inside them (consent prompt + `--dangerously-run-mcp-servers` flag for non-interactive).
- **Failure mode:** LLM-judge analyzers can hallucinate findings (false positives) and miss novel attack patterns (false negatives) — same caveat prior research flagged for `claude-code-security-review`. SARIF output (Cisco) closes the gap that one had; Snyk emits its own JSON.

### P9 — Cryptographic signing + SLSA provenance for prose artifacts (early, but exists)
- **What it is:** Treat a skill as an OCI image (or a signed artifact) and attach SLSA provenance via Sigstore/Cosign so consumers can cryptographically verify *who built it* and *from which source commit*.
- **Source apps:** **`skills-oci`** (salaboy.com, 2026-04-19) — concrete worked example: skill → OCI image → `cosign sign` → SLSA attestation; **`sigstore/sigstore-a2a`** — Agent-to-Agent Card signing, embeds source revision + build env + CI workflow into the signature; **NVIDIA Verified Agent Skills** — daily catalog updates, automated+human review, risk scan, signing, machine-readable skill cards; **GitHub Artifact Attestations** publish SLSA provenance + signed SBOMs for anything built in GH Actions (free for public repos); **npm publish attestations + SLSA provenance** via Sigstore public good instance.
- **Adoption scale:** early — none of the top 10 skill packs surveyed ships SLSA provenance today (prior research finding #2 stands: Anthropic SDK publish workflow has no `id-token: write` and no `--provenance`, npm attestations API returns Not found for `@anthropic-ai/sdk@latest`).
- **Failure mode:** the OCI distribution path adds a runtime dependency (an OCI client) to consumers; verification UX is still developer-grade (`cosign verify-blob …`); meaningful only if consumers actually *check*, which the marketplace install flows don't.

### P10 — Open standard with conformance test + client registry
- **What it is:** A standards-body-shaped governance layer: spec repo + docs + Client Showcase + an "adding-skills-support" implementer guide + multi-logo adopter wall.
- **Source apps:** [`agentskills/agentskills`](https://github.com/agentskills/agentskills) — 19,499★, Apache-2.0 code / CC-BY-4.0 docs (proper dual licensing), "originally developed by Anthropic, released as an open standard." Adopter logos surveyed in `docs/images/logos/`: agentman, amp, autohand, block… (long tail).
- **Adoption scale:** independent reporting (prior research triangulation) put `SKILL.md` adoption at ~32 tools by March 2026, including VS Code, OpenAI/Codex, Cursor, Copilot, Gemini CLI, JetBrains Junie, AWS Kiro, Block Goose.
- **Failure mode:** standard governs the *format*, not the *integrity* — passing as a valid `SKILL.md` is silent on whether the skill is malicious (that's what P8 scanners exist for). And the standard repo itself ships 0 releases / 0 tags — the spec versioning question is unanswered.

### P11 — Plans, release-notes, and a published "what we will not accept" list
- **What it is:** Public dated plans + a structured changelog where each release documents *what was removed and why*, plus an explicit contributor-guidelines section addressed *to AI agents*.
- **Source apps:** `obra/superpowers/docs/plans/` (e.g. `2025-11-22-opencode-support-design.md`, `skills-improvements-from-user-feedback.md`); `RELEASE-NOTES.md` v5.1.0 with PR/issue links; v5.1.0 also added "**Pre-submission checklist** — read the PR template, search for existing PRs, verify a real problem exists" and "**What we will not accept** — third-party deps, 'compliance' rewrites of skill content, project-specific config, bulk PRs, speculative fixes, domain-specific skills, fork-specific changes, fabricated content, and bundled unrelated changes." `snyk/agent-scan` ships CHANGELOG.md; `addyosmani/agent-skills` ships CONTRIBUTING.md with a quality bar.
- **Adoption scale:** obra is the standout; most repos ship none of this.
- **User complaints:** the existence of obra's "what we will not accept" *is* the complaint — 94% PR rejection rate from AI-generated slop forced the practice.
- **Failure mode:** documents culture, doesn't enforce it; needs human reviewers at the door (which obra has, at scale; smaller packs don't).

### P12 — Marketplace policy enforcement (SHA-pinning + policy scan; live ecosystem pattern)
- **What it is:** Distribution layer that pins externals to commit SHAs, runs a Claude policy scan as a required check, sweeps nightly for valid upstream bumps, auto-reverts failures.
- **Source apps:** [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) — detailed in prior research; refreshed today (28,275★, 0 releases still, pushed today). `github/awesome-copilot` does *structural* CI but not the policy-scan layer.
- **Adoption scale:** the canonical model; one implementation.
- **Failure mode:** integrity rests on **SHA-pinning + a Claude policy scan** — *not* on cryptographic signing / SBOM / SLSA provenance. The marketplace itself ships 0 releases. Trust disclaimer present: "Anthropic does not control what MCP servers, files, or other software are included in plugins and cannot verify that they will work as intended or that they won't change."

## Graveyard / failure-mode evidence

Documented failures, abandoned models, and post-mortem outcomes:

| Case | Date | What happened | Source |
| --- | --- | --- | --- |
| **ClawHub / ClawHavoc** | Jan–Feb 2026 | 341 malicious skills found in ClawHub registry; coordinated 1,467-skill malware campaign (Snyk ToxicSkills, named ClawHavoc); **5 of top-7 most-downloaded skills were malware**; "no infrastructure for safety" before. **Did not shut down** — survived via mandatory code review + VirusTotal SHA-256 lookup + Gemini Code Insight scanning. | [The Hacker News](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html), [Snyk](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/), [SpecWeave](https://spec-weave.com/docs/guides/why-verified-skill-matters/) |
| **`skills.sh`** (Vercel-run) | 2026 | 59,000+ skills, **no automated scanning** initially; post-crisis added Gen Digital + Socket + Snyk triple-scan partnership | Search results, [Snyk](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) |
| **SkillsMP** | 2026 | 96,000+ skills, "minimal verification" | Search results |
| **Anthropic archived repos** (refreshed) | 2024-2025 | Still archived: `hh-rlhf`, `anthropic-tools`, `ConstitutionalHarmlessnessPaper`, `sleeper-agents-paper`, `rogue-deploy-eval`, `anthropic-retrieval-demo`, interpretability/demo repos | Prior research (2026-05-25 sweep), still valid |
| **`anthropics/evals`** | 2024-07-02 | Not archived but stale — dataset published, no gating harness, never updated past mid-2024 | Prior research |
| **Snyk's "13% chance" finding** | 2026 | A skill installed in the past month has a 13% chance of containing a critical security flaw — measured population effect, not anecdote | [Snyk](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) |
| **obra/superpowers PR culture** | 2026-04 | Audit of last 100 closed PRs showed **94% rejection** from AI-generated slop — fabricated descriptions, duplicates, fork-specific changes pushed upstream | obra/superpowers `RELEASE-NOTES.md` v5.1.0 |

Patterns that have *not* failed visibly but lack adoption proof: SLSA provenance on prose artifacts (no top-10 skill pack ships it), full multi-target install-CI (none of the 7-target packs gates all 7), eval-gated red-teaming of shipped prompts (zero in segment).

## Contributor / user complaints (collected)

| Where | Complaint | Pattern it exposes |
| --- | --- | --- |
| `addyosmani/agent-skills` Issue #180 | `SPEC.md` is global to project root — conflicts when working on multiple parallel tasks | Single-file-per-project pattern doesn't scale to parallel agents |
| `addyosmani/agent-skills` Issue #2 (early) | Request for `/code-simplify` skill (eventually shipped) | Backlog-driven evolution; no graveyard |
| `obra/superpowers` `RELEASE-NOTES.md` v5.1.0 | 94% PR rejection rate from AI slop; new harness PRs now require session transcripts | The contributor side is itself being colonised by agents; maintainers need *agent*-readable contribution rules |
| Snyk "13% chance of critical flaw" | Population-level user risk on installed skills | The marketplace *consumer* is exposed; not just one-off bad actor |
| Cisco scanner disclaimer | "No findings ≠ no risk … Human review remains essential" | Scanner false-confidence is itself a failure mode |
| Snyk scanner warning | Scanning MCP configs *executes* their commands | Defensive tooling has its own threat surface |

(External search for reddit/HN critique returned little indexed — the discourse lives in GitHub issues and security-vendor blogs.)

## Unmet needs / tensions observed

1. **Versioning gap is the segment default, not a bug.** 5/6 ecosystem-defining repos still ship 0 releases as of 2026-05-28 (refreshed from 2026-05-25). Only obra (27) and addyosmani (3) tag prose; only Vercel (28) and Snyk (30) tag the *tools*. The "how do we version markdown contracts" question (prior finding M1) has working answers but they're rare exceptions.
2. **Versioned ≠ pinned.** Even where tags exist, the documented install path is usually `@main`. The signing/provenance layer (P9) addresses this in principle but has zero adoption in the top 10 skill packs.
3. **Multi-target claims outrun multi-target verification.** Every multi-tool pack (addyosmani 7, obra 8, Vercel 51+) ships an install/render gate for **one** target at most. A generator emitting N targets either gates all N or inherits the same unguarded-drift risk.
4. **Validators check structure, not safety.** Closes nothing on Dim-B — no segment repo ships an eval/red-team harness for prompts. The defensive scanners (P8) partly fill the gap but are *consumer-side* tooling, not producer-side gates.
5. **The supply-chain threat is measured and active.** ClawHub/ClawHavoc, 1,467 malicious payloads, 5/7 top downloads malware, 13% installed-skill-flaw rate. A generator that distributes skills into the same marketplaces inherits that exposure unless it ships signing/provenance (P9, none does today).
6. **Contributor channels are being colonised by agents.** obra's 94% PR rejection rate is the contributor-side analogue of the consumer-side threat — quality gates on *contribution* now matter as much as quality gates on *installation*.
7. **The open standard is governed; the open *distribution* is not.** `agentskills/agentskills` ships the format with a Client Showcase and implementer guide — that's mature. But the marketplaces consuming that format (ClawHub, skills.sh, SkillsMP, Vercel's, Anthropic's official) have wildly different governance — and the top 5 all carry trust disclaimers.
8. **Defensive scanners are real but consumer-only.** Snyk + Cisco are working products; neither ships as a *producer-side* CI gate inside the top skill packs (Cisco does ship a reusable GH Action, addyosmani et al. haven't adopted it). The scanners exist; the integration into the publish pipeline is mostly aspirational.

## What would falsify these findings

- **"Anthropic ecosystem still ships 0 releases":** falsifiable if any of `anthropics/skills`, `claude-plugins-official`, `knowledge-work-plugins`, `agentskills/agentskills`, `VoltAgent/awesome-agent-skills` adds tagged releases — re-check via `gh api repos/*/releases --jq length`.
- **"No top-10 skill pack ships SLSA provenance":** falsifiable by adding `id-token: write` + `--provenance` to any publish workflow, or by `cosign verify-blob` succeeding on any pack's release artifact.
- **"5 of top-7 ClawHub downloads were malware":** triangulated via Snyk + The Hacker News + SentinelOne; falsifiable if a primary-source registry audit contradicts.
- **"Skills.sh has Gen Digital + Socket + Snyk triple-scan":** based on Snyk blog + search summaries; falsifiable by inspecting skills.sh's published vetting policy.
- **"Validators are structural-only":** falsifiable by any pack publishing an *eval-gated* CI run on its own prompts (Promptfoo / PyRIT / model-graded eval) — none surfaced.
- All star/release/push figures point-in-time **2026-05-28**; the segment pushes daily.

## Sources

**GitHub API (`gh`), 2026-05-28** — repo searches (`gh search repos "agent skills" | "claude skills" | "claude plugin marketplace"`), `repos/*`, `releases`, `tags`, recursive `git/trees`, raw `contents` for READMEs/validators/manifests/workflows on: `obra/superpowers` (incl. README, RELEASE-NOTES, skills/ tree), `addyosmani/agent-skills`, `anthropics/{skills, claude-plugins-official, knowledge-work-plugins, claude-plugins-community}`, `agentskills/agentskills`, `VoltAgent/awesome-agent-skills`, `vercel-labs/{skills, agent-skills}`, `google/skills`, `github/awesome-copilot`, `snyk/agent-scan`, `cisco-ai-defense/skill-scanner`, `snyk-labs/toxicskills-goof`, `antfu/skills`, `simonw/claude-skills`, `kepano/obsidian-skills`, `K-Dense-AI/scientific-agent-skills`, `muratcankoylan/Agent-Skills-for-Context-Engineering`, `phuryn/pm-skills`, `browserbase/skills`.

**e1 (local, `c:\VS\agent-enterprise-e1`)** — `README.md`, `package.json`, `src/`, ADR-003 / ADR-004 / ADR-005 / ADR-006, `docs/sop/00-principles.md`, `docs/sop/skill-layer-requirements.md`.

**Independent triangulation / supply chain / signing:**
- ClawHub/ClawHavoc/ToxicSkills: [Snyk](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/), [The Hacker News](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html), [SentinelOne](https://www.sentinelone.com/blog/marketplace-skills-and-dependency-hijack-in-claude-code/), [Datadog Security Labs](https://securitylabs.datadoghq.com/articles/malicious-skills-supply-chain-risks-in-coding-agents-with-dynamic-context/), [prompt.security](https://prompt.security/blog/when-your-plugin-starts-picking-your-dependencies-marketplace-skills-and-dependency-hijack-in-claude-code), [Repello AI](https://repello.ai/blog/claude-code-skill-security), [agensi.io](https://www.agensi.io/learn/toxicskills-clawhavoc-agent-skills-security-crisis-2026), [SpecWeave](https://spec-weave.com/docs/guides/why-verified-skill-matters/), [skillshield.dev](https://skillshield.dev/blog/toxicskills-snyk-research-openclaw-users/), [SkillSieve arXiv](https://arxiv.org/html/2604.06550v1), [Blink Blog](https://blink.new/blog/is-openclaw-safe-clawhub-malware-guide-2026), [Penligent](https://www.penligent.ai/hackinglabs/openclaw-virustotal-the-skill-marketplace-just-became-a-supply-chain-boundary/).
- SLSA / Sigstore / OCI signing: [SLSA v1.2 spec](https://slsa.dev/spec/v1.2/), [Sigstore cosign-verify-bundles](https://blog.sigstore.dev/cosign-verify-bundles/), [Legit Security SLSA part 2](https://www.legitsecurity.com/blog/slsa-provenance-blog-series-part-2-deeper-dive-into-slsa-provenance), [AquilaX — Beyond SBOMs](https://aquilax.ai/blog/supply-chain-artifact-signing-slsa), [salaboy — skills-oci](https://www.salaboy.com/2026/04/19/manage-and-distribute-skills-with-skills-oci/), [sigstore/sigstore-a2a](https://github.com/sigstore/sigstore-a2a), [NVIDIA Verified Agent Skills](https://developer.nvidia.com/blog/nvidia-verified-agent-skills-provide-capability-governance-for-ai-agents/), [Always Further — AI agent provenance](https://www.alwaysfurther.ai/blog/sigstore-ai-agent-provenance).
- Adoption / open standard: [agentskills.io](https://agentskills.io/specification), [paperclipped.de](https://www.paperclipped.de/en/blog/agent-skills-open-standard-interoperability/), [inference.sh](https://inference.sh/blog/skills/agent-skills-overview), [VS Code agent skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills), [OpenAI Codex Skills](https://developers.openai.com/codex/skills).
- Addy Osmani context: [jimmysong.io](https://jimmysong.io/ai/addyosmani-agent-skills/), [DEV Community](https://dev.to/_46ea277e677b888e0cd13/agent-skills-19-production-grade-skills-that-make-ai-coding-agents-work-like-senior-engineers-5bi9), [addyosmani.com/blog/agent-skills](https://addyosmani.com/blog/agent-skills/).

**Prior research (this repo)** — `anthropics-org-enterprise-readiness-tooling-research.md`, `openai-org-enterprise-readiness-tooling-research.md`, `microsoft-org-enterprise-readiness-tooling-research.md` (baseline for versioning gaps, ToxicSkills/ClawHub Feb-2026 snapshot, no-red-team-harness, SARIF lingua franca, npm-provenance gap on Anthropic SDKs).
