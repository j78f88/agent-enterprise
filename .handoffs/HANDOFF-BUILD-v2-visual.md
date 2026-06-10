# Handoff Prompt: Build Command Centre Visual v2

**Task:** Implement the command centre visual v2 overhaul per `docs/archive/command-centre-visual-v2-plan.md`. Replace `docs/command-centre-visual.html` with a complete rewrite that adds Instructions tab, Purpose & Intent, binding matrix, and expanded Architecture section.

## What to do

Follow the 19-step implementation workflow in the plan (Phases 1-4):

**Phase 1: Content Gathering** — Extract metadata from source files
1. Parse all 25 instruction files (`instructions/generic/*.md` + `instructions/configurable/*.md`)
   - Extract: filename, frontmatter (id, description), first paragraph
   - Classify: generic vs configurable
2. Extract skill-to-instruction bindings from all 13 skill files (`skills/*/[name].skill.md`)
   - Extract: "Shared Rules" section
   - Build: instruction → agent matrix
3. Extract agent metadata from v1 visual (already present, verify it's still accurate)
4. Extract schema metadata from 7 schemas (`schemas/*.schema.json`)
   - Extract: name, description, what it validates, who uses it
5. Extract profile metadata from 3 profile configs (`profiles/*.yml`)
6. Verify counts: 13 agents, 13 skills, 25 instructions, 7 schemas, 3 profiles

**Phase 2: HTML Structure & Population** — Build the file
7. Start with v1 visual (`docs/command-centre-visual.html`) as skeleton
8. Add two new tabs: "Purpose & Intent" (position 1) and "Instructions" (position 3)
9. Build Purpose & Intent tab with: hero statement, 6 design principles, system-at-a-glance, use cases (5), non-goals table (5 rows), escape hatch table (8 rows), misconceptions (4)
10. Rebuild Agents & Skills tab: keep existing lane cards, add "Governed by:" line to each agent showing which instructions bind to it
11. Build Instructions tab with two sections (Generic 11 files + Configurable 14 files), tables with filename/purpose/description
12. Build instruction-to-agent binding matrix (rows=25 instructions, cols=13 agents, fill cells where agent reads instruction)
13. Expand Architecture tab: add Schema Registry section, expanded build pipeline showing `.github/` targets, Profiles section (3 cards)
14. Update stats bar from "13 · 13 · 25 · 3 · 3" to "13 · 13 · 25 · 7 · 3 · 3" (add schemas count)
15. Update footer generated date to today

**Phase 3: Quality & Verification** — Test everything
16. Verify content: all 25 instructions present, all 13 agents present, all 7 schemas present, all 3 profiles present
17. Test interactivity: all 6 tabs switch, filters work on "I want to..." table, filter works on Instructions tab
18. Verify icons: all Material icon names valid, no typos, icons render
19. Visual check: no overflow, alignment correct, colours match lanes, dark theme consistent, responsive

**Phase 4: Commit** — Save
20. Commit to `docs/command-centre-visual.html`
    Message: `docs: overhaul command-centre visual to v2 — add instructions tab, purpose/intent, schema registry`

## Key constraints

- Single self-contained HTML file (no external JS dependencies beyond Google Fonts & Material Icons)
- Keep CSS custom properties and colour palette (same as v1)
- Extract instruction descriptions from actual files, don't hardcode
- Instructions tab must have ≥70% fill in binding matrix (most agents bind to 5+ instructions)
- Stats bar must match actual counts on disk
- File opens standalone in browser (no build/server required)
- Purpose & Intent tab must be first tab (sets context)

## Where to find content

- Instruction files: `instructions/generic/*.instructions.md` (11) + `instructions/configurable/*.instructions.md` (14)
- Skill files with bindings: `skills/*/[name].skill.md` (read "Shared Rules" section)
- Schemas: `schemas/*.schema.json` (7 files)
- Profiles: `profiles/*.yml` (3 files)
- Current visual: `docs/command-centre-visual.html` (v1, use as skeleton)
- Plan reference: `docs/archive/command-centre-visual-v2-plan.md` (full specs)

## Verification checklist (must pass all)

- [ ] All 25 instruction files listed with type (generic/configurable)
- [ ] Binding matrix ≥80% fill
- [ ] Escape hatch table has ≥6 entries with real paths
- [ ] Stats bar shows 13 · 13 · 25 · 7 · 3 · 3
- [ ] Every agent card shows 3+ instructions in "Governed by:" line
- [ ] All Material icons render
- [ ] Tab switching smooth, no console errors
- [ ] Filters work on both tables
- [ ] File opens standalone (no build needed)
- [ ] Purpose & Intent is Tab 1
- [ ] Non-goals table ≥4 entries
- [ ] Footer date is 2026-05-29

## When done

Commit to `docs/command-centre-visual.html` and report completion.
