# PLAN — Command Centre Visual v2

> Overhaul of `docs/command-centre-visual.html`. The current visual
> (v1, generated 2026-05-17) is missing entire artifact categories,
> has no purpose/intent framing, and doesn't surface the instruction
> files that govern agent behaviour.

## Problem statement

The command centre visual is supposed to be the single interactive
reference for the agent-enterprise operating system. In its current
state it fails at this because:

1. **No purpose or intent.** Opens cold with agent cards. A new user
   has no idea what this system is, what problem it solves, or what
   the design philosophy is.

2. **Instruction files are invisible.** 25 instruction files (11
   generic + 14 configurable) define how every agent behaves, but
   they appear nowhere in the visual. This is the biggest gap — the
   instructions are the rules of the system and they're hidden.

3. **No instruction-to-agent binding.** Even if instructions were
   listed, there's no map showing which instructions bind to which
   agents. Users can't answer "what rules does @planner follow?"

4. **Schema registry absent.** 7 JSON schemas (frontmatter-v1,
   callable-v1, project-v1, registry-v1, subagent-return-tier1/2/3)
   enforce structural contracts but aren't shown.

5. **Build pipeline is shallow.** The architecture tab shows
   `skills/ → init.py → resolved/` but doesn't explain the
   instruction resolution flow or the `.github/` deployment targets.

6. **Stats line is wrong.** Says "25 instructions" but the actual
   count is 25 (11 generic + 14 configurable). The number happens to
   be correct but the visual never shows what those 25 are.

7. **No design philosophy.** The system has clear principles
   (runtime-agnostic, zero project-specific content, single build
   step, progressive enhancement) but these aren't surfaced as
   first-class concepts.

## Goals

- Make the visual the **single source of truth** for understanding
  agent-enterprise at a glance.
- Surface every artifact category: agents, skills, instructions,
  schemas, profiles, modes.
- Show the relationships between artifacts (which instructions bind
  to which agents, which schemas validate which contracts).
- Open with purpose and intent so a new user understands the system
  before diving into details.
- Keep the same visual language (dark theme, colour-coded lanes,
  Material icons, interactive tabs).

## Non-goals

- Replacing the command-centre contract documents. The visual is a
  reference overlay, not the contracts themselves.
- Adding interactivity beyond tabs and filtering. No live data, no
  API calls, no build-time generation.
- Documenting Mode 2/3 implementation details. The visual shows
  what the modes are, not how to build dispatchers or coordinators.

---

## Changes

### Tab restructure

**v1 tabs (4):**
1. Cheat Sheet
2. Process Flow
3. I want to...
4. Architecture

**v2 tabs (6):**
1. **Purpose & Intent** *(new)* — what this system is, design
   philosophy, key principles
2. **Agents & Skills** *(renamed from Cheat Sheet)* — same lane-based
   agent cards, same handoff map
3. **Instructions** *(new)* — all 25 instruction files with purpose,
   type (generic/configurable), and agent bindings
4. **Process Flow** *(kept)* — three modes, severity contract
5. **I want to...** *(kept)* — intent-based routing table
6. **Architecture** *(expanded)* — build pipeline, schemas, directory
   structure, progressive enhancement, return tiers

### Tab 1: Purpose & Intent *(new)*

Content:
- **Hero statement:** One-paragraph description of what agent-enterprise
  is and what problem it solves.
- **Design principles** (card grid):
  - Runtime-agnostic (Copilot, Claude Code, Cursor)
  - Zero project-specific content
  - Single build step (`python init.py`)
  - Progressive enhancement (Phases 0-4)
  - Contract-first (schemas enforce structure)
  - Separation of concerns (agents don't cross lanes)
- **System-at-a-glance** summary: "13 agents across 5 lanes,
  governed by 25 instructions, validated by 7 schemas, built from
  source through a single deterministic build step."
- **How the pieces fit** (visual flow):
  ```
  Skills (what agents can do)
    + Instructions (rules agents follow)
    + Agent bodies (persona + tool boundary)
    + Config (project-specific tokens)
    ──→ init.py ──→ resolved/ (deployable artifacts)
                ──→ .github/ (runtime targets)
  ```
- **Use cases** (when to reach for this system):
  - You want AI coding agents to follow consistent processes across
    sprints without re-explaining every time
  - You need quality gates that block bad code from shipping without
    manual review of every line
  - You want structured planning → execution → documentation flow
    that doesn't drift between projects
  - You're running multiple projects and want shared patterns to
    propagate without copy-paste
  - You want to onboard a new project into a working agent team in
    one session

- **Non-goals & boundaries** (what this system is NOT):
  - **Not a CI/CD pipeline.** Agents run inside coding assistants,
    not as GitHub Actions. For CI, use your existing pipeline.
  - **Not a project management tool.** Agents draft plans and track
    sprint state, but this isn't Jira/Linear. Use those for
    cross-team visibility.
  - **Not an AI model.** This is a governance layer over existing
    coding agents (Copilot, Claude Code, Cursor). It doesn't
    replace them — it structures their work.
  - **Not a code generator.** Agents follow contracts and produce
    plans/reports/audits. The actual code is written by subagents
    under @sprint-lead, not by the framework itself.
  - **Not prescriptive about stack.** Zero project-specific content.
    Works with React, Python, Go, or anything — you provide the
    config, it provides the process.

- **"If it doesn't exist here" escape hatches:**

  | You're looking for... | It's not here because... | Go here instead |
  |---|---|---|
  | A specific dispatcher implementation | Mode 2 is contract-only; impls vary by runtime | `command-centre/03-mode-orchestration/reference-impls/` |
  | Project-specific config values | The framework ships zero project content | `config/project.config.yml` (your copy) |
  | How to write a new agent | Extension is documented separately | `docs/EXTENSION_GUIDE.md` |
  | Runtime-specific setup (Copilot vs Claude Code vs Cursor) | Visual is runtime-agnostic | `docs/QUICKSTART.md` per-runtime sections |
  | Customising instruction behaviour | Token resolution is the mechanism | `docs/CUSTOMIZATION.md` |
  | Troubleshooting a broken agent | Operational, not architectural | `docs/TROUBLESHOOTING.md` |
  | The contract documents themselves | Visual is a reference overlay | `command-centre/` folder (per-mode contracts) |
  | Historical decisions and reasoning | ADRs live in their own folder | `command-centre/decisions/` or `docs/decisions/` |

- **Common misconceptions** (callout box):
  - "@sprint-lead writes code" → No, it delegates to unnamed
    subagents. Sprint-lead is a thin orchestrator.
  - "I need Mode 2 to use agents" → No, Mode 1 (direct invocation)
    is the foundation and works standalone.
  - "Instructions are optional guidelines" → No, they're enforced
    rules. Agents are contractually bound to read them.
  - "resolved/ is the source of truth" → No, it's build output.
    Source is `skills/`, `instructions/`, `agents/`.

### Tab 2: Agents & Skills *(renamed)*

Changes from v1:
- Rename tab from "Cheat Sheet" to "Agents & Skills" for clarity.
- Add a **"Governed by"** line to each agent card showing which
  instruction files that agent reads. Example:
  ```
  Governed by: commit-conventions, severity-levels,
               subagent-return-schemas, sprint-docs-format,
               backlog-ledger, bug-backlog-format,
               non-goals-governance
  ```
- Keep all existing content: lane headers, agent cards with role
  description, commands, handoff targets, write surfaces.
- Keep the handoff chain map.
- Add instruction count per agent as a small badge.

Source for agent-instruction bindings: each `*.skill.md` file lists
its instructions in the "Shared Rules" section. Parse from:
- `skills/docs/docs.skill.md` → 7 instructions
- `skills/planner/planner.skill.md` → N instructions
- `skills/qa/qa.skill.md` → N instructions
- (all 13 skill files)

### Tab 3: Instructions *(new)*

Two sections:

**Generic instructions (11 files):**
Universal rules with no token dependency. Apply to every project.

| File | Purpose |
|------|---------|
| `askquestions-contract` | When and how agents ask clarifying questions |
| `batch-report` | Structured batch reporting format |
| `commit-conventions` | Git commit message format and rules |
| `contract-change-checklist` | Checklist for modifying agent contracts |
| `determinism-guarantees` | Reproducibility requirements (Phase 4) |
| `fsm-orchestration` | Finite state machine for sprint phases |
| `honesty-contract` | Truthfulness and uncertainty disclosure rules |
| `observability` | Logging and tracing requirements |
| `security-model` | Command whitelist and path traversal rules |
| `state-management` | How agents persist and read state |
| `subagent-return-schemas` | Structured return formats (Tier 1/2/3) |

**Configurable instructions (14 files):**
Rules that consume `{{tokens}}` from project config. Resolved at
build time.

| File | Purpose |
|------|---------|
| `backlog-ledger` | Backlog ledger format and discipline |
| `bug-backlog-format` | Bug entry format (detail store, no status) |
| `composition-rules` | How agents compose into workflows |
| `engagement-format` | Engagement and session format |
| `engagement-gates` | Entry/exit gates for agent engagement |
| `handoff-rejection-format` | Format for rejected handoffs |
| `non-goals-governance` | NON_GOALS.md read-only governance |
| `planning-compliance` | Sprint planning compliance rules |
| `planning-preflight` | Pre-flight checks before sprint execution |
| `retro-report` | Retrospective report format |
| `security-audit` | Security audit procedure and format |
| `severity-levels` | CRITICAL/WARNING/SUGGESTION contract |
| `sprint-docs-format` | Sprint documentation archival format |
| `validation-framework` | Feature validation framework rules |

**Instruction-to-agent binding matrix:**
A visual grid/table showing which instructions each agent reads.
Rows = instructions, columns = agents. Filled cells show the binding.
This answers "what rules does @X follow?" and "which agents use
instruction Y?"

### Tab 4: Process Flow *(kept)*

No structural changes. Content is accurate and complete.
- Three orchestration mode flows
- Severity contract table

### Tab 5: I want to... *(kept)*

No structural changes. Content is accurate and complete.
- Intent-based routing table with filter

### Tab 6: Architecture *(expanded)*

Keep all existing content and add:

**Schema registry** *(new section):*

| Schema | Validates | Used by |
|--------|-----------|---------|
| `frontmatter-v1` | Skill/instruction frontmatter | `init.py` build |
| `callable-v1` | Mode 2 callable contract | Dispatchers |
| `project-v1` | Project config structure | `init.py`, onboarding |
| `registry-v1` | Mode 3 project registry | Coordinators |
| `subagent-return-tier1` | Analysis-only returns | All quality gates |
| `subagent-return-tier2` | Standard returns (with artifacts) | Sprint-lead subagents |
| `subagent-return-tier3` | Composition returns (sprint-level) | Sprint-lead |

**Expanded build pipeline** *(replace shallow version):*
Show the full flow including `.github/` deployment targets:
```
Source artifacts          Build step              Deployment targets
─────────────────        ──────────              ──────────────────
skills/*.skill.md    ─┐                      ┌─→ resolved/skills/
instructions/**      ─┤                      ├─→ resolved/instructions/
agents/*.body.md     ─┼──→ python init.py ──→├─→ resolved/agents/
config/*.yml         ─┤   (validate + resolve)├─→ .github/agents/
schemas/*.json       ─┘                      └─→ .github/instructions/
```

**Profiles section** *(new):*
Show the 3 pre-built profiles and what they configure:
- `react-web-app` — SPA/PWA with component testing
- `monorepo-fullstack` — Multi-package with shared config
- `python-api` — FastAPI/Flask with pytest

---

## Stats line update

v1: `13 agents · 13 skills · 25 instructions · 3 modes · 3 profiles`

v2: `13 agents · 13 skills · 25 instructions · 7 schemas · 3 modes · 3 profiles`

Add schemas to the hero stats bar.

## Footer update

Update generated date to current date on implementation.

---

## Implementation workflow

### Phase 1: Content Gathering (read-only)

1. **Extract instruction metadata** from all 25 instruction files
   - Files: `instructions/generic/*.instructions.md` (11) +
     `instructions/configurable/*.instructions.md` (14)
   - Extract: frontmatter, purpose, first paragraph
   - Classify: generic vs configurable

2. **Extract skill-to-instruction bindings** from all 13 skill files
   - Files: `skills/*/[name].skill.md`
   - Extract: "Shared Rules" section
   - Build: instruction → agent matrix (rows=instructions, cols=agents)

3. **Extract agent metadata** (already done, verify against 13 files)
   - Lane, role, commands, handoffs, write surfaces
   - Add: which instructions govern each agent

4. **Extract schema metadata** from all 7 schemas
   - Files: `schemas/*.schema.json`
   - Extract: name, purpose, what it validates, who uses it

5. **Extract profile metadata** from 3 profile configs
   - Files: `profiles/*.yml`
   - Extract: name, description, what it configures

6. **Verify stats**
   - Count agents: 13
   - Count skills: 13
   - Count instructions: 25 (11 + 14)
   - Count schemas: 7
   - Count profiles: 3

### Phase 2: HTML Structure & Content Population

7. **Set up HTML skeleton**
   - Copy existing v1 file as starting point (preserve CSS, fonts, JS)
   - Add new tab buttons for "Purpose & Intent" and "Instructions"
   - Update tab switching logic if needed

8. **Build Purpose & Intent tab**
   - Write hero statement (1 paragraph)
   - Create design principles card grid (6 cards)
   - Add system-at-a-glance summary
   - Add "How the pieces fit" visual flow
   - Add use cases list (5 items)
   - Add non-goals table (5 rows)
   - Add escape hatch table (8 rows)
   - Add misconceptions callout (4 items)

9. **Rebuild Agents & Skills tab**
   - Copy all existing lane-based agent cards from v1
   - For each agent card, add new "Governed by:" line
   - Extract list of instructions from skill file
   - Populate with actual instruction filenames
   - Add instruction count badge to each agent
   - Keep all existing content (lane headers, handoff map, etc.)

10. **Build Instructions tab**
    - Create two sections: Generic (11 files) + Configurable (14 files)
    - For each section, populate a table with filename, purpose, description
    - Extract purpose from frontmatter
    - Extract description from first paragraph of each instruction file
    - Build instruction-to-agent binding matrix
    - Rows: all 25 instructions
    - Columns: all 13 agents
    - Filled cells = agent reads that instruction
    - Add table filter (search/input field) for instruction name

11. **Expand Architecture tab**
    - Keep all existing content
    - Add Schema Registry section (3-column table: Schema name, Validates, Used by)
    - Replace shallow build pipeline with expanded version showing .github/ targets
    - Add Profiles section (3 cards, one per profile, with description)

12. **Update stats bar**
    - v1: 13 · 13 · 25 · 3 · 3
    - v2: 13 · 13 · 25 · 7 · 3 · 3 (add schemas)

13. **Update footer**
    - Set generated date to today

### Phase 3: Quality & Verification

14. **Verify all content is present**
    - All 25 instructions appear
    - All 13 agents appear with lane assignments
    - All 7 schemas appear
    - All 3 profiles appear
    - Binding matrix has ≥70% fill (agents read multiple instructions)

15. **Test interactivity**
    - Tab switching works for all 6 tabs
    - Filters work on "I want to..." table
    - Filter works on Instructions tab
    - No console errors in browser dev tools

16. **Verify icon references**
    - All Material icon names are valid
    - No typos in icon class names
    - Icons render consistently across tabs

17. **Visual/layout check**
    - No text overflow in cards
    - No misaligned elements
    - Colours match expected lane assignments
    - Dark theme is consistent
    - Responsive behaviour (mobile viewing)

18. **Link & reference check**
    - All instruction filenames match actual files on disk
    - All agent names match actual agents
    - All schema names match actual schemas
    - No placeholder or TODO text remains

### Phase 4: Commit & Deploy

19. **Commit changes**
    - File: `docs/command-centre-visual.html` (replaces v1)
    - Message: `docs: overhaul command-centre visual to v2 — add instructions tab, purpose/intent, schema registry`

---

## Implementation notes

- Single self-contained HTML file (no external JS dependencies).
- Keep Google Fonts (Plus Jakarta Sans, Material Symbols).
- Keep the same CSS custom properties and colour palette.
- Keep all existing interactions (tab switching, table filtering).
- Add table filtering to the new Instructions tab.
- File stays at `docs/command-centre-visual.html` (same path).
- This is a complete rewrite of the file, not a patch.
- Extract content from `.skill.md` files programmatically where possible (frontmatter parsing).

---

## Anti-patterns to avoid

- **Hardcoding instruction descriptions** — extract from actual files, don't hand-write summaries.
- **Incomplete binding matrix** — agents must list all instructions they read, not just highlights.
- **Schema descriptions that don't match actual schema purpose** — verify against frontmatter.
- **Missing escape hatch entries** — every common "I'm looking for X" should have a redirect.
- **Stale stats** — stats bar must match actual artifact counts on disk.
- **Orphaned content** — every table row, card, and matrix cell must correspond to real files/agents.

---

## Key decision points

| Decision | Options | Guidance |
|----------|---------|----------|
| **Instruction-to-agent binding format** | Matrix grid vs. per-agent list | Matrix is faster to scan ("which agents follow X"); per-agent is faster to navigate ("what rules does @Y follow?"). Implement matrix in Instructions tab; add per-agent "Governed by" lines in Agents tab for both. |
| **Escape hatch location** | Part of Purpose tab or separate | Purpose tab. It's contextual: users land here when they learn what the system IS, so it's natural to explain what it's NOT and where to find those things. |
| **Filter performance** | Client-side (current) or server-side | Client-side. File is self-contained; no server. Filtering 25 instructions is fast enough. |
| **Binding matrix scroll behaviour** | Horizontal scroll vs. collapsible columns | Horizontal scroll with sticky first column (instruction names). Readable on desktop; acceptable on mobile. |

---

## Verification checklist

A reviewer can confirm this visual is complete when:

- [ ] All 25 instruction files are listed with correct type classification
- [ ] Instruction-to-agent binding matrix has ≥80% fill (most agents bind to 5+ instructions)
- [ ] All escape hatch entries match actual file paths and exist on disk
- [ ] Stats bar shows 13 · 13 · 25 · 7 · 3 · 3
- [ ] Every agent card shows 3+ instructions in "Governed by:" line
- [ ] All Material icons render without errors
- [ ] Tab switching works smoothly with no lag
- [ ] Filter works on both "I want to..." and Instructions tabs
- [ ] File opens standalone in browser (no build/server required)
- [ ] Purpose & Intent tab is the first tab (sets context before detail)
- [ ] Non-goals table includes at least 4 clear boundaries
- [ ] Escape hatch table includes at least 6 redirects to other docs
