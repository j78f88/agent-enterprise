# v3 Uplift — Run Sheet

Your personal reference for tracking and understanding the uplift.
This is YOUR document — not the agent's. It tells you what to expect,
what to check, and what to say to kick each phase off.

---

## How to run this

Each phase is a **separate agent session**. Start fresh each time.
Hand the agent the phase prompt and let it deliver.

### Invocation pattern

You do NOT need custom skills or instructions for execution. The plan
itself is the instruction. Use this pattern:

```
Open a new Copilot Chat session (or Claude Code session).
Paste the phase prompt below.
The agent reads PLAN.md, executes, and reports completion.
```

**Why not @sprint-lead?** Sprint-lead orchestrates YOUR project's sprints
(Verk, DIY). This is agent-homebase modifying itself — the substrate
editing its own rules. A direct prompt with the plan as context is cleaner
than routing through a skill that the skill itself might be mid-edit on.

---

## Phase prompts (what to paste)

### Phase 0 — Baseline

```
Read d:\VS\agent-homebase\v3uplift\PLAN.md.
Execute the "Baseline" section. Run all four checks. Save output to
v3uplift/baseline.log. Create branch v3-uplift from current HEAD.
Report results.
```

### Phase 1A — Skill Authoring Guide

```
Read d:\VS\agent-homebase\v3uplift\PLAN.md (Phase 1A section).
Read d:\VS\agent-homebase\docs\EXTENSION_GUIDE.md for current state.
Draft the skill authoring guide to v3uplift/drafts/SKILL_AUTHORING_GUIDE.md.
Follow the spec in the plan exactly. The voice of the guide itself must
follow its own rules (imperative, no hedging, specific).
When done, present the draft for my review before promotion.
```

### Phase 1B — Domain Glossary

```
Read d:\VS\agent-homebase\v3uplift\PLAN.md (Phase 1B section).
Read the full repo structure and all skill descriptions.
Draft CONTEXT.md to v3uplift/drafts/CONTEXT.md.
Include every domain term used across skills, instructions, and docs.
Flag any ambiguities you find. Present for review.
```

### Phase 1C — Hard/Soft Dependency ADR

```
Read d:\VS\agent-homebase\v3uplift\PLAN.md (Phase 1C section).
Read every file in instructions/generic/ and instructions/configurable/.
Classify each as hard or soft dependency with reasoning.
Draft the ADR to v3uplift/drafts/0001-hard-soft-deps.md.
Present for review.
```

### Phase 1 Promotion

```
Read the three drafts in v3uplift/drafts/.
Check them against each other for terminology consistency.
If consistent, promote:
- v3uplift/drafts/SKILL_AUTHORING_GUIDE.md → docs/SKILL_AUTHORING_GUIDE.md
- v3uplift/drafts/CONTEXT.md → CONTEXT.md (repo root)
- v3uplift/drafts/0001-hard-soft-deps.md → docs/decisions/0001-hard-soft-instruction-dependencies.md
Run build + tests. Report gate status.
```

### Phase 2 — Skill Audit (run once per skill or batch)

```
Read d:\VS\agent-homebase\v3uplift\PLAN.md (Phase 2 section).
Read docs/SKILL_AUTHORING_GUIDE.md and CONTEXT.md.
Audit and rewrite: [SKILL NAME or "all 13 skills"].
For each skill: follow the 10-point per-skill checklist in the plan.
Stage changes. Run build + tests after each skill. Report.
```

**Note:** You can run all 13 in one session if the agent handles it,
or batch them (e.g., "audit a11y, bug, perf, qa" — the shorter skills
first, then the longer ones that need extraction).

### Phase 3 — Voice Unification

```
Read d:\VS\agent-homebase\v3uplift\PLAN.md (Phase 3 section).
Read docs/SKILL_AUTHORING_GUIDE.md and CONTEXT.md.
Execute the cross-cutting fixes table and file-by-file pass.
Run the QA grep checks listed in the plan.
Run build + tests. Report.
```

### Phase 4 — Validation

```
Read d:\VS\agent-homebase\v3uplift\PLAN.md (Phase 4 section).
Execute all validation checks (4A through 4F).
Report full results. Do not proceed to next phase.
```

### Phase 4.5 — Tone QA (SEPARATE AGENT)

```
[Use the full prompt from v3uplift/prompts/tone-qa-audit.md verbatim]
```

**Important:** This MUST be a fresh agent session with no prior context.
The point is a cold-read audit. If the same agent that wrote the skills
also audits them, it will miss its own blind spots.

### Phase 5 — Release

```
Read d:\VS\agent-homebase\v3uplift\PLAN.md (Phase 5 section).
Read v3uplift/QA_REPORT.md — confirm zero critical violations.
If clear: update CHANGELOG, bump version references, run final
validation, commit, and tag agent-homebase@3.0.0.
Report completion.
```

---

## What to watch for (your checklist)

As the delivery owner, you're checking quality at each gate:

### After Phase 1 (review drafts before promotion)
- [ ] Does the authoring guide read clearly? Could you hand it to a
      colleague and they'd understand the rules?
- [ ] Does the glossary cover the terms YOU use when talking about
      agent-homebase?
- [ ] Does the dependency classification match your intuition about
      which instructions need project config?

### After Phase 2 (spot-check skills)
- [ ] Pick 2-3 rewritten skills and read them. Do they sound like one
      author? Do the prohibitions feel natural, not theatrical?
- [ ] Do the "When NOT to use" sections make sense? Would they
      actually prevent mis-invocation?
- [ ] Are the extracted supporting files (from oversized skills)
      genuinely reference material, not core workflow?

### After Phase 3 (scan for feel)
- [ ] Open README.md — does it read as direct and confident?
- [ ] Open one agent body — does it feel like the skills in tone?
- [ ] Run: `grep -ri "DO NOT" skills/ agents/` — should be empty.

### After Phase 4.5 (read the QA report)
- [ ] Are the critical violations real problems or false positives?
- [ ] Are there patterns (same mistake repeated) that suggest a
      systemic fix rather than one-by-one patches?
- [ ] If violations exist, send the report back to an agent with:
      "Fix the critical violations in this report. Run build + tests."

### After Phase 5
- [ ] Read the CHANGELOG entry. Does it accurately describe what changed?
- [ ] Run `python init.py --config config/project.config.example.yml`
      yourself. Does it complete cleanly?
- [ ] Read one resolved skill in `resolved/skills/`. Does the output
      look right?

---

## Timeline expectations

| Phase | Complexity | Sessions |
|-------|-----------|----------|
| 0. Baseline | Trivial | 1 (5 min) |
| 1A. Authoring guide | Medium — needs careful drafting | 1 |
| 1B. Glossary | Medium — needs full-repo read | 1 |
| 1C. Dependency ADR | Low | 1 (can combine with 1B) |
| 1 Promotion | Low — mechanical | 1 |
| 2. Skill audit | High — 13 skills, 5 need extraction | 2-3 |
| 3. Voice pass | Medium — grep + edit pattern | 1-2 |
| 4. Validation | Low — mechanical | 1 |
| 4.5 Tone QA | Medium — cold-read audit | 1 (MUST be separate agent) |
| 5. Release | Low — mechanical | 1 |

**Total: 10-13 agent sessions.** Not a single marathon — deliberate
short sessions with gates between them.

---

## If something goes wrong

| Problem | Action |
|---------|--------|
| Tests fail after a skill rewrite | Revert that skill. Check if the test validates content structure. Adjust the rewrite to satisfy the test contract. |
| Build fails after a change | Check `init.py` validation errors. Usually a frontmatter field mismatch. Fix and re-run. |
| QA report has 50+ violations | That's a pattern, not a list. Look for the systemic cause (probably a term the glossary defines differently than current usage). Fix the pattern, not individual instances. |
| Agent rewrites a skill and loses the governance sections | The authoring guide's section template is the safety net. Point the agent at it and re-run that single skill. |
| Agent's tone doesn't match your intent | Paste a before/after example of what you want. "This is wrong: [excerpt]. This is right: [excerpt]. Redo." |
