---
applyTo: "{{paths.validation}}**"
---

# Validation Framework

Single source of truth for the 5-test echo-chamber validation applied to feature recommendations **before** they reach `@planner`. Owned by `@pm`.

> **Why this exists:** recommendations derived from competitive research are prone to pattern-matching against successful apps without checking whether the feature is actually what's driving the success. This framework forces explicit tests instead of analogy reasoning.

## When to apply

- Any feature recommendation derived from observing another app, market segment, or pattern.
- Any `@researcher` output being synthesised into a proposed roadmap change.
- Any brainstorm that says "app X does Y, we should too."

Routine bug fixes, UX polish, and changes driven by internal user need **do not** need this framework.

## The 5 Tests

For each, record a **Verdict** (PASS / FAIL / N/A) and a one-or-two-sentence **Reasoning**. Do not auto-pass without reasoning.

1. **Causation vs correlation.** Is the feature *why* the source app succeeds, or is it incidental to the real driver? If Strava's retention comes from the social feed, copying "last run distance" won't move the needle.

2. **Frequency match.** Does the source app's usage cadence match DIY Project Helper's? DIY is weekly-at-best; fitness and recipes are daily; knitting is project-scoped over weeks. A feature built for daily engagement warps the product when applied to low-frequency use.

3. **Survivorship bias.** Am I ignoring apps that shipped this feature and failed? If Gardenize built a rich data-entry feature and was abandoned by casuals while Planta won by being simpler, the winning lesson is *less* of this feature, not more.

4. **Anti-pattern / engagement-at-cost.** Does this drive real user value or just session counts? Duolingo's streak can push users toward 60-second low-value sessions. Reject features that drive sessions without driving progress.

5. **Complexity cost.** Does the implementation and maintenance cost match the value created? Obsidian's bidirectional link graph is beautiful for power users but costly to learn. For a hobbyist audience, that's the wrong trade-off.

## Labels

Exactly one label per validation record:

- **VALIDATED** — all five tests pass. Cleared to hand off to `@planner`.
- **REFRAMED** — one test fails but the failure is rescuable by restating the feature. Record both the original and the reframed version with the reason the reframe rescues it.
- **NEW** — emerged from research or original thinking (not a direct copy), passes all five. Treat as VALIDATED with a note about the origin.
- **REJECTED** — one or more tests fail and the failure is not rescuable. If it's a standing no, update `{{paths.non_goals}}`.
- **DEFERRED** — valid in principle but blocked by scope, timing, or a missing dependency. Add to `{{paths.roadmap}}` under "Parked" with the unblock condition.

## Output location

All validation records go to `{{paths.validation}}<feature-slug>-validation.md` using the template in the `/validate-feature` prompt.

## Enforcement (for @reviewer)

- **CRITICAL:** Hand off to `@planner` from `@pm` without a corresponding validation record in `{{paths.validation}}`.
- **WARNING:** Validation record where any test has a verdict but no reasoning sentence.
- **SUGGESTION:** Validation record labelled REFRAMED without both original and reframed versions present.
