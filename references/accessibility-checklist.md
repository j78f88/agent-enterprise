# Accessibility Checklist

Cross-skill reference for `@a11y` and any agent that touches UI.

## WCAG 2.1 AA — quick checks

- **Perceivable**
  - All images have descriptive `alt` text; decorative images use `alt=""`.
  - Text contrast ratio ≥ **4.5:1** for normal text, **3:1** for large text.
  - Captions or transcripts for any audio/video content.
  - Information is never conveyed by colour alone.
- **Operable**
  - Every interactive control is keyboard reachable and usable.
  - Visible focus indicator on every focusable element.
  - No keyboard traps. `Esc` closes modal-style UI.
  - Time limits are adjustable or extendable.
- **Understandable**
  - Page has a unique, descriptive `<title>` and a single `<h1>`.
  - Form fields have associated `<label>` elements; errors are programmatic.
  - Language declared via `<html lang="…">`.
- **Robust**
  - HTML validates; no duplicate IDs.
  - ARIA used only when a native element won't do; roles match patterns.

## Screen reader testing

- Run an automated pass first (`axe-core`, `pa11y`, Lighthouse).
- Smoke-test key flows with NVDA on Windows or VoiceOver on macOS.
- Listen for: meaningful link text, announced state changes, no orphan
  `aria-live` chatter, no element read as "clickable" with no role.

## Colour contrast

- Use a contrast checker on every text-over-background combination,
  including hover, focus, and disabled states.
- Verify in both light and dark themes if both ship.

## Reporting

Severity follows WCAG impact: CRITICAL = blocks task completion for
assistive-tech users, WARNING = friction, SUGGESTION = polish. Every
finding cites the page/component and the failing success criterion.
