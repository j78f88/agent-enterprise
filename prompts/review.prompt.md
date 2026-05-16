---
description: "Lifecycle command — independent quality checks before shipping: review, security, a11y."
mode: chat
---

# /review

Use this after `/build` to run the independent quality checks that no
implementer should self-grade.

## Flow

1. Invoke `@reviewer` for code-level review of the sprint diff. Findings cite
   file + line with concrete fixes.
2. Invoke `@security` for dependency audit, secret scan, and hash registry
   verification. Findings cite CVE / advisory or `file+line`.
3. Invoke `@a11y` if any UI surface changed. Findings cite the failing WCAG
   success criterion.

## Artifacts

- Review report (CRITICAL / WARNING / SUGGESTION) for code.
- Security findings appended to `SECURITY_CHANGELOG.md`.
- A11y findings linked from `PLAN.md` quality gates.

## Exit

Every CRITICAL finding is either fixed or accepted with explicit rationale.
Ready for `/ship`.
