# Sprint History (archived)

Entries moved out of SPRINTS.md per the archive rule
(when Sprint N completes, Sprint N-2 moves here). Most recent at top.

---

## Sprint 1 — Onboarding Path Resolution Remediation

**Status:** Complete  
**Type:** fix (build-system debt / bug-fix)  
**Started:** 2026-04-27  
**Completed:** 2026-05-30

### Goals

- [x] Resolve and deploy skill companion files
- [x] Resolve inline code-span tokens with two-phase escape
- [x] Cross-references use deploy path (`paths.skills_deploy_dir` token)

### Tasks

- [x] TG1 (A): companion-file resolution loop + setup-skip interaction
- [x] TG2 (C): `paths.skills_deploy_dir` token + cross-reference rewrites
- [x] TG3 (B): inline code-span policy + two-phase escape (preserve → strip after scans)
- [x] Review fix: agent-wrapper refs corrected to deploy path

### Retro Summary

- **Velocity:** 3 task groups + 1 review-fix; 100% completion rate
- **Carry-over:** none
- **Forecast calibration:** 100% (3/3 assumptions, 3/3 complexity)
- **Process notes:** Escape must preserve marker through scans; strip-after-scan ordering is now test-locked.

---
