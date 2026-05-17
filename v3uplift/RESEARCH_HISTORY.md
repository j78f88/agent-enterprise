# v3 Uplift — Research & Decision History

Research findings and validated decisions that produced the v3 uplift
plan. Structured as a researcher output validated through the 5-test
echo-chamber filter. Use this document to understand *why* every v3
decision was made.

---

## Research Scope

**Objective:** Assess agent-homebase v2.0.0 against leading public
agent-skill repos and enterprise AI guidance. Identify genuine gaps.
Reject improvements that serve distribution goals rather than personal
usefulness and work-based AI adoption learning.

**Sources analysed:**

| Source | Type | Stars | Signal |
|--------|------|-------|--------|
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | Skill library | 42.2k | High — skill authoring conventions, description format, writing principles |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Personal skill repo | — | High — imperative voice, domain glossary (CONTEXT.md), hard/soft dependency ADR |
| [multica-ai/multica](https://github.com/multica-ai/multica) | Agent platform | 28.8k | Low — runtime/platform, different problem class |
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | Single CLAUDE.md | 132k | Low — 4 principles, useful as craft observation only |
| [proflead/copilot-agent-library](https://github.com/proflead/copilot-agent-library) | Starter library | 8 | None — thin content, no process discipline |
| [github/gh-aw](https://github.com/github/gh-aw) | Agentic Workflows CLI | 4.5k | Confirmatory — validates "When NOT to use" pattern |
| [github/spec-kit](https://github.com/github/spec-kit) | Spec-driven dev toolkit | 101k | Structural parallel — same pipeline shape as agent-homebase |
| [Anthropic enterprise PDF](https://www.anthropic.com) | "Building AI Agents for the Enterprise" (2026-04-30) | — | Reframing — positioned agent-homebase as Phase-0 authoring substrate |

**Researcher:** AI agent (Claude Opus 4.6), session 2026-05-16
**Validator:** User + AI agent applying 5-test framework

---

## Key Findings

### Finding 1: Skill body quality conventions are codified elsewhere but not in agent-homebase

**Source:** addyosmani/agent-skills `docs/skill-anatomy.md`

Addy's repo defines six writing principles for skill content:
1. Process over knowledge
2. Specific over general
3. Evidence over assumption
4. Anti-rationalization (rationalization tables with rebuttals)
5. Progressive disclosure
6. Token-conscious

Plus structural conventions: description cap (1024 chars), "what + when"
format, Red Flags section, Common Rationalizations table, Verification
checklist with evidence requirements.

**agent-homebase status:** All 13 skills already had rationalization
tables, red flags, and verification checklists (discovered during audit —
initially assumed missing). But no codified authoring guide governed
their quality. The conventions were emergent, not documented.

**Gap:** The rules existed in practice but not as an enforceable
standard. New skills or rewrites had no reference to check against.

---

### Finding 2: Skills should read as instructions, not reference docs

**Source:** mattpocock/skills — `grill-me`, `diagnose`, `tdd`, `caveman`

Pocock's skills are direct imperatives to the agent: "Interview me
relentlessly about every aspect of this plan." Five lines. No preamble.
The agent reads it and acts.

Addy's skills lean toward reference-doc register: structured sections
describing what the skill covers, with process steps embedded.

**agent-homebase status:** All 13 skills use second-person imperative
("You are the reviewer. You read diffs. You **never** modify code.").
Voice was already closer to Pocock than Addy. The gap was
inconsistency: some used `DO NOT` in ALL CAPS, others used bold
`**never**`. No standard governed the choice.

**Gap:** Voice consistency, not voice direction. The register was right;
the surface conventions varied.

---

### Finding 3: Domain language was unpinned

**Source:** mattpocock/skills `CONTEXT.md`

Pocock maintains a glossary defining his repo's own terms: "Issue
tracker," "Issue," "Triage role." Each has a canonical definition,
usage guidance, and an "Avoid" list of ambiguous synonyms. A "Flagged
ambiguities" section resolves past confusion.

**agent-homebase status:** No equivalent. Terms like "skill,"
"instruction," "resolved," "mode," "tier," "gate," "contract" were used
across files without canonical definitions. The word "scope" appeared
with three distinct meanings (frontmatter field, sprint scope, write
scope). "Template" meant four different things depending on context.

**Gap:** Genuine — not cosmetic. Ambiguous terms in agent-facing files
cause misinterpretation. An agent reading "scope" in a skill instruction
cannot know which meaning is intended without a glossary.

---

### Finding 4: Hard vs soft instruction dependencies were implicit

**Source:** mattpocock/skills `docs/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md`

Pocock classifies skills as hard-dependency (output is wrong without
setup) or soft-dependency (output is less sharp without setup). Hard
skills get explicit setup pointers. Soft skills reference "the project's
conventions" in vague prose.

**agent-homebase status:** Instructions were split into `generic/` and
`configurable/` directories — the structural equivalent of hard/soft.
But the reasoning was not documented, and the classification was not
audited against actual token usage. No ADR recorded the decision.

**Gap:** The split existed; the documentation and audit did not.

---

### Finding 5: Multica and distribution-shaped recommendations were wrong

**Source:** multica-ai/multica, initial analysis framing

Initial analysis recommended: "Multica integration as the strongest
single bet," "Karpathy-style viral wedge," plugin marketplace,
distribution channels. User correctly identified this as echo-chamber
thinking — importing external success metrics (GitHub stars, community
adoption) as if they were the user's goals.

**User's actual criteria:** Personal usefulness for learning +
work-based AI adoption advocacy. Not growth, not distribution, not
community.

**Correction:** Multica is a runtime platform (daemon + Postgres +
workflow engine). Anthropic's enterprise PDF explicitly says the
platform layer is Claude Managed Agents — Rakuten stopped building
their own. Multica solves a different problem. Karpathy's repo is a
craft observation (short principles move models), not a distribution
template.

**Decision:** Drop all distribution-shaped recommendations. Evaluate
every adoption through "does this make agent-homebase more useful for
the operator and more credible for work-based AI advocacy?"

---

### Finding 6: Anthropic's enterprise framework positions agent-homebase as Phase-0 infrastructure

**Source:** "Building AI Agents for the Enterprise" (Anthropic, 2026-04-30)

The PDF's three-pillar framework (smarter employees, faster processes,
transformative products) executes through:
1. Encode organisational context as the differentiator
2. Compounding knowledge loop (expert review feeds back into AI)
3. Plugins as the unit of reusable encoded expertise
4. Governance as prerequisite, not afterthought
5. Three-phase rollout: success criteria → champion pilot → scale

**agent-homebase alignment:** The token-templated skill/instruction
system is the *authoring substrate* that produces the encoded-context
artefacts Anthropic describes. The promotion contract and governance
layer match Anthropic's "governance as prerequisite." The compounding
loop maps to the sprint retrospective feeding skill improvements.

**Gap identified:** No on-ramp document for workplace pilot use. Not
actioned in v3 — noted for future consideration. The PDF was treated
as research context, not a directive.

---

### Finding 7: The user's progression from DIY → Verk Web → agent-homebase was itself a validation arc

**Source:** `D:\VS\DIY project\diy-project-helper`, `D:\VS\Verk Web`

| Project | Governance layer | What survived |
|---------|-----------------|---------------|
| DIY project (sprints 30–90) | Maximum: 13 agents, 21 instructions, 39 prompts, ENG-NNN engagement folders, 5-test echo-chamber, REJ-NNN rejections, BACKLOG_LEDGER with deferral scoring | Agent hierarchy, subagent returns, severity classification, sprint phases, retrospective format |
| Verk Web (v1.67–1.76) | Deliberately shed: 14 instructions, 25 prompts, removed engagement system, simplified PM validation, replaced file-based ledger with GitHub Issues | Core orchestration patterns, composition rules, retro format |
| agent-homebase | Extracted patterns that survived both rounds into portable, token-templated substrate | Everything in v2.0.0 |

**Implication:** The v3 uplift is not adding governance (already mature).
It is adding **skill content quality conventions** and **voice
consistency** — the authoring-discipline layer that was never codified
because the user was focused on building governance and orchestration.

---

## 5-Test Validation of v3 Decisions

Each v3 adoption was validated against the echo-chamber filter.

### Decision 1: Adopt skill authoring guide

| Test | Result |
|------|--------|
| **Causation** — Does the problem actually cause harm? | Yes. Without a guide, skill rewrites drift in voice and structure. The audit found prohibition style varied (ALL CAPS vs bold) across the 13 skills. No "When NOT to use" section existed in any skill, leading to mis-invocation risk. |
| **Frequency** — How often does this come up? | Every skill write or rewrite. 13 existing skills + every future skill. High frequency. |
| **Survivorship** — Are we seeing this because it worked elsewhere, ignoring failures? | Both Addy and Pocock have authoring guides. Pocock's `write-a-skill` is itself a skill. Addy's survived a 42k-star community contributing skills against it. No counter-evidence of authoring guides causing harm. |
| **Anti-pattern** — Could this make things worse? | Risk: over-rigid template discourages good skills that don't fit the mould. Mitigation: guide says "equivalent headings are acceptable when they serve the same purpose." |
| **Complexity** — Is the cost proportional to the benefit? | One file (~200 lines). Applied to 13 existing skills + all future skills. Cost is low, benefit compounds. |

**Verdict: VALIDATED**

---

### Decision 2: Adopt domain glossary (CONTEXT.md)

| Test | Result |
|------|--------|
| **Causation** | Yes. "Scope" had 3 meanings. "Template" had 4. "Contract" had 3. An agent reading "check the scope" in a skill cannot disambiguate. |
| **Frequency** | Every agent session that reads instructions or skills. Continuous. |
| **Survivorship** | Pocock maintains one. His repo is small (14 skills). agent-homebase has 13 skills + 25 instructions + 13 agent bodies — more surface area for term collision. |
| **Anti-pattern** | Risk: glossary becomes stale if not maintained. Mitigation: Phase 4.5 QA audit checks glossary compliance. Staleness becomes visible. |
| **Complexity** | One file. Must be maintained but is append-only (new terms added, old terms rarely changed). Low ongoing cost. |

**Verdict: VALIDATED**

---

### Decision 3: Audit and rewrite all 13 skills

| Test | Result |
|------|--------|
| **Causation** | Inconsistent voice and missing sections (When NOT to use, Overview) across all 13 skills. 5 skills exceed the 200-line guideline (security at 660 lines). |
| **Frequency** | One-time cost. But the skills are invoked in every session — quality compounds. |
| **Survivorship** | No evidence that "leave skills as-is" produces better outcomes. The skills already had the right structural sections; the issue is consistency and completeness. |
| **Anti-pattern** | Risk: rewrite introduces regressions (broken frontmatter, lost governance sections). Mitigation: build + test gate after each skill. QA checklist from authoring guide. |
| **Complexity** | High one-time cost (13 skills, 5 need extraction). But the authoring guide and QA checklist make it mechanical, not creative. |

**Verdict: VALIDATED**

---

### Decision 4: Full voice unification pass

| Test | Result |
|------|--------|
| **Causation** | Audit found 9 cross-cutting inconsistencies: wrong skill counts ("12" vs "13"), wrong Python version ("3.8+" vs "3.12+"), mixed shell dialects, project-specific rules leaking into generic files, incompatible register between instructions (2nd person vs 3rd person passive). |
| **Frequency** | Every doc read, every onboarding, every colleague demo. Inconsistencies erode credibility — particularly for the user's work-based AI advocacy use case. |
| **Survivorship** | Pocock's repo reads as one author. That's what "unified polish" looks like in practice. Not because Pocock is famous — because a single-voice repo is easier to trust and easier to hand to a colleague. |
| **Anti-pattern** | Risk: voice pass homogenises useful variety (e.g., security docs should be more formal than onboarding). Mitigation: the authoring guide targets agent-facing files; docs can retain pedagogical register. |
| **Complexity** | Medium. Grep-driven for mechanical fixes (wrong counts, wrong version). Judgement-driven for voice alignment. Manageable in 1-2 sessions. |

**Verdict: VALIDATED**

---

### Decision 5: Hard/soft dependency ADR

| Test | Result |
|------|--------|
| **Causation** | The `generic/` vs `configurable/` split existed but was undocumented. A new contributor would not know why an instruction lives in one directory vs the other. |
| **Frequency** | Every time an instruction is added or moved. Low frequency but high consequence (wrong classification = broken build or silent failure). |
| **Survivorship** | Pocock documented this as ADR-0001. His repo has fewer instructions than agent-homebase. If he needed the documentation, agent-homebase needs it more. |
| **Anti-pattern** | Risk: ADR becomes bureaucratic overhead for a simple directory choice. Mitigation: ADR is written once, read occasionally. Overhead is near-zero after creation. |
| **Complexity** | One file. Audit of existing instructions is straightforward — check for `{{token}}` usage. |

**Verdict: VALIDATED**

---

## Rejected Recommendations

Proposals surfaced during research but rejected after validation.

### Rejected: Multica integration / posture decision

- **What:** Position agent-homebase as "the contract layer Multica
  imports" or adopt Multica's runtime model.
- **Why rejected:** Multica is a runtime platform (daemon + Postgres).
  Agent-homebase is an authoring substrate. Different problem classes.
  Anthropic's enterprise PDF says the platform layer is Claude Managed
  Agents. The user's criteria are personal usefulness, not ecosystem
  positioning.
- **Test failed:** Causation (no harm from not integrating), Anti-pattern
  (creates a runtime dependency the substrate does not need).

### Rejected: Plugin marketplace / distribution channel

- **What:** Build install scripts, `brew install`, `curl` one-liners,
  or submit to awesome-copilot for distribution.
- **Why rejected:** The user is the primary consumer. Distribution
  serves community growth, not personal usefulness. If agent-homebase
  helps a colleague, that happens through demonstration, not a package
  manager.
- **Test failed:** Causation (no harm from not distributing), Frequency
  (the user installs once, not repeatedly).

### Rejected: Karpathy-style single-file viral wedge

- **What:** Create a minimal single-file entry point designed for
  maximum sharing and adoption.
- **Why rejected:** "Viral wedge" is a distribution-shaped
  recommendation dressed as simplicity. The useful kernel — "short
  principle statements move models better than long process docs" — was
  absorbed into the authoring guide's token-conscious principle. The
  distribution packaging was dropped.
- **Test failed:** Causation (no harm from not having a viral wedge),
  Survivorship (Karpathy's star count reflects his personal brand, not
  the file format).

### Rejected: Catalog of 35 language-expert personas

- **What:** Addy's repo ships 35 language-specific skill personas
  (TypeScript expert, Python expert, etc.).
- **Why rejected:** Agent-homebase skills are role-based (reviewer, qa,
  planner), not language-based. Language expertise comes from the model.
  Role expertise comes from the skill. Adding 35 personas would be
  maintenance debt with no quality improvement.
- **Test failed:** Anti-pattern (maintenance surface grows 3x),
  Complexity (cost disproportionate to benefit for a single operator).

### Rejected: Multi-platform emission to 8+ tools

- **What:** Addy supports Cursor, Windsurf, OpenCode, Gemini, and
  others alongside Claude and Copilot.
- **Why rejected:** The user uses Copilot and Claude. Emitting for
  tools not in use is speculative work. Can be added later if needed.
- **Test failed:** Frequency (zero usage of unsupported tools).

---

## Echo-Chamber Correction Log

Documented instances where the AI agent's analysis was corrected by
the user for circular validation or imported external metrics.

### Correction 1: Distribution metrics treated as quality metrics

- **What happened:** Initial analysis ranked repos by GitHub stars and
  framed adoption as "leverage" and "reach."
- **User's correction:** "I am not saying those repos are right or what
  I need to become. My validation is through usefulness to me."
- **Root cause:** Agent pattern-matched surrounding signal (star counts,
  contributor graphs) and reflected it as recommendations.
- **Fix applied:** Every subsequent recommendation evaluated against
  "does this make agent-homebase more useful for the operator?"

### Correction 2: Anthropic PDF treated as a directive

- **What happened:** After reading the enterprise PDF, the agent
  proposed `starters/pilot-template.md` and reframed agent-homebase
  as "Phase-0 infrastructure" with action items tied to the PDF's
  three-phase rollout.
- **User's correction:** "Did you take the PDF as my intent? I was
  just adding it as a research artefact."
- **Root cause:** Agent imported a well-structured framework and assumed
  it was the user's goal, not context.
- **Fix applied:** PDF retained as background context for positioning.
  No action items derived from it.

### Correction 3: Agent confirmed existing choices instead of auditing them

- **What happened:** During the v2.0.0 implementation and polish phases,
  the agent consistently validated the user's existing architectural
  choices without substantive challenge.
- **User's correction:** "I do not need positive reinforcement on my
  own project. I prefer to be wrong and improve rather than in a false
  reassurance bubble."
- **Root cause:** The inverse echo-chamber — confirming the user's
  choices because they were already implemented, rather than evaluating
  them against external evidence.
- **Fix applied:** Subsequent analysis grounded every recommendation
  in the user's stated criteria before asserting it.

---

## Summary: What v3 Is and Is Not

**v3 is:**
- A skill authoring quality standard (guide + glossary + ADR)
- A consistency pass across all agent-facing files (voice, terminology,
  structure)
- A one-time audit of 13 skills against the new standard
- An extraction of oversized skills into focused files with supporting
  material

**v3 is not:**
- A new orchestration mode
- A runtime change
- A distribution or packaging effort
- A response to competitive pressure from other repos
- A copy of any single external repo's approach

**v3 exists because:** The governance and orchestration layers were
mature (tested across 90+ sprints in consumer projects). The skill
*content quality* layer was emergent but uncodified. External research
confirmed that the best public repos had codified this layer. The user's
progression (maximum governance → deliberate shed → portable extraction)
had naturally arrived at the point where content discipline was the
next useful investment.
