# Sprint Tracking

**Current: Sprint 2** — In Progress

---

## Sprint 2 — Authentication Improvements

**Status:** In Progress  
**Type:** Mixed (Feature + Bug)  
**Started:** 2026-04-27  
**Completed:** —

### Goals

- [x] Fix Safari login redirect (BUG-001)
- [ ] Implement API rate limiting
- [ ] Add session timeout handling

### Tasks

- [x] Diagnose Safari cookie issue
- [x] Update OAuth callback handler
- [ ] Add rate limit middleware
- [ ] Implement graceful session expiry
- [ ] Write integration tests

### Notes

- Safari fix merged in PR #142
- Rate limiting blocked on Redis setup

---

## Sprint 1 — Initial Setup

**Status:** Complete  
**Type:** Feature  
**Started:** 2026-04-15  
**Completed:** 2026-04-22

### Goals

- [x] Set up project scaffolding
- [x] Configure CI/CD pipeline
- [x] Implement basic authentication

### Tasks

- [x] Initialize monorepo structure
- [x] Configure ESLint + Prettier
- [x] Set up GitHub Actions
- [x] Implement OAuth login flow
- [x] Add user session management

### Retro Summary

- **Velocity:** 5 story points
- **Carry-over:** 1 item (API rate limiting)
- **Process notes:** Need to allocate time for infrastructure setup

---

<!-- 
Archive rule: when Sprint N completes, move Sprint N-2 entry to docs/archive/
Format: one H2 per sprint, most recent at top.
-->
