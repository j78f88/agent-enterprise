# Bug Backlog

Reproduction context for all logged bugs. Status is tracked in BACKLOG_LEDGER.md — not here.
Only @bug appends entries below the marker. Never edit existing entries.

---
<!-- BUG ENTRIES BELOW THIS LINE — do not edit above -->

## BUG-001 — Login redirect fails on Safari

**Severity:** WARNING  
**Reported:** 2026-04-20  
**Reporter:** QA team  

### Description

After successful OAuth login, Safari users are redirected to a blank page instead of the dashboard.

### Steps to Reproduce

1. Open app in Safari 17.x
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Observe blank page instead of dashboard

### Expected Behavior

User should land on `/dashboard` after successful authentication.

### Actual Behavior

User sees blank white page. URL shows `/callback?code=...` — redirect never completes.

### Environment

- Browser: Safari 17.4
- OS: macOS Sonoma 14.4
- Device: MacBook Pro M3

### Screenshots

See `bugs/screenshots/BUG-001-safari-blank.png`

### Notes

- Works correctly in Chrome, Firefox, Edge
- Likely related to Safari's stricter cookie handling
- Possibly a SameSite cookie issue

---

## BUG-002 — Dashboard charts don't render on slow connections

**Severity:** SUGGESTION  
**Reported:** 2026-04-25  
**Reporter:** User feedback  

### Description

On slow 3G connections, dashboard charts show loading spinner indefinitely.

### Steps to Reproduce

1. Enable network throttling (Slow 3G preset)
2. Navigate to dashboard
3. Wait 30+ seconds

### Expected Behavior

Charts should render within 10 seconds or show error state.

### Actual Behavior

Loading spinner persists indefinitely. No error shown.

### Environment

- Any browser with network throttling
- Simulated Slow 3G (400ms RTT, 400kbps down)

### Notes

- Timeout appears to be missing
- Consider adding skeleton loading state
- Lower priority — affects edge case users only
