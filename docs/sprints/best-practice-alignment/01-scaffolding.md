# 01 — Scaffolding: New Root & Reference Files

> **Depends on:** Nothing (parallel-safe, zero code changes)
> **Commit:** `feat(docs): add AGENTS.md, CLAUDE.md, honesty contract, references, skill template`
> **Verify:** `python init.py --config config/project.config.example.yml` produces same output + honesty-contract in resolved/

---

## Task Group 1.1: Add root `AGENTS.md`

Files: `AGENTS.md`

**Why:** All major platforms (Claude Code, GitHub Copilot, OpenAI Codex) look for `AGENTS.md` at repo root.

- [ ] Create `AGENTS.md` (~50 lines) at repo root
- [ ] Include: project purpose (1-line), dev setup (Python 3.12+, `pip install pyyaml`, `pip install -r requirements-dev.txt`), build command (`python init.py --config config/project.config.example.yml`), test command (`python -m pytest tests/ -v`), architecture summary (skills → init.py → resolved/), key directories table, PR conventions
- [ ] Verify file under 80 lines

---

## Task Group 1.2: Add `CLAUDE.md`

Files: `CLAUDE.md`

**Why:** Claude Code loads `CLAUDE.md` automatically. Reference AGENTS.md to avoid maintaining two parallel files.

- [ ] Create `CLAUDE.md` at repo root — reference `AGENTS.md`, add Claude Code-specific notes (regeneration command, don't edit resolved/ directly)
- [ ] Verify file under 20 lines and references AGENTS.md

---

## Task Group 1.3: Add honesty contract instruction

Files: `instructions/generic/honesty-contract.instructions.md`

**Why:** Industry pattern (awesome-cursorrules anti-sycophancy rule). agent-homebase has no explicit honesty/anti-hallucination contract.

- [ ] Create `instructions/generic/honesty-contract.instructions.md` (~40 lines) with rules: never fabricate API signatures/function names/file paths, never claim a test passes without running it, never silently skip required steps, never invent package versions, say "uncertain" when uncertain, never soften findings, never hallucinate file contents
- [ ] Verify init.py copies it to `resolved/instructions/` (generic glob handles automatically — no code change)
- [ ] Verify file under 50 lines

**Impact on init.py:** None — existing `generic_src` glob picks up new `.md` files automatically.

---

## Task Group 1.6: Create `references/` folder

Files: `references/testing-patterns.md`, `references/security-checklist.md`, `references/accessibility-checklist.md`, `references/performance-checklist.md`, `skills/qa/qa.skill.md`, `skills/security/security.skill.md`, `skills/a11y/a11y.skill.md`, `skills/perf/perf.skill.md`

**Why:** Progressive disclosure pattern — cross-skill checklists live in one place, reducing token weight.

- [ ] Create `references/testing-patterns.md` — test structure, coverage expectations, snapshot vs assertion, integration test patterns (30–50 lines)
- [ ] Create `references/security-checklist.md` — OWASP top 10 shortlist, dependency audit steps, secret detection patterns (30–50 lines)
- [ ] Create `references/accessibility-checklist.md` — WCAG 2.1 AA quick checks, screen reader testing, color contrast (30–50 lines)
- [ ] Create `references/performance-checklist.md` — bundle size checks, render performance, database query patterns (30–50 lines)
- [ ] Add reference lines in at least 4 skills: qa → testing-patterns, security → security-checklist, a11y → accessibility-checklist, perf → performance-checklist
- [ ] Verify each file under 60 lines

---

## Task Group 1.7: Update Extension Guide with skill template

Files: `docs/EXTENSION_GUIDE.md`

**Why:** New adopters writing custom skills need a template showing the new sections (Common Rationalizations, Red Flags, Verification).

- [ ] Append "Skill Template" section to `docs/EXTENSION_GUIDE.md`
- [ ] Template documents standard skill structure: frontmatter, identity, core constraints, workflow sections, Common Rationalizations table, Red Flags list, Verification checklist
- [ ] Include a minimal working example (~30 lines)

---

## Verification

After all tasks above:

```powershell
# init.py still resolves cleanly
python init.py --config config/project.config.example.yml
# Expected: 27+ resolved, 10+ copied, 13 agents, 2 token warnings
# NEW: honesty-contract.instructions.md appears in resolved/instructions/

# Tests still green
python -m pytest tests/ -v

# New files exist
Test-Path AGENTS.md               # True
Test-Path CLAUDE.md               # True
Test-Path instructions/generic/honesty-contract.instructions.md  # True
(Get-ChildItem references/*.md).Count  # 4
```
