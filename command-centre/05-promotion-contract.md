# Promotion contract

> **Contract tag:** part of `mode-3-contract-v1`.
>
> Schema defining when a project-local artifact (skill, instruction,
> agent, profile fragment) becomes eligible for promotion into
> substrate. Governs every harvest decision.

## Purpose

Without an explicit promotion contract, harvest decisions are
ad-hoc. Some artifacts get promoted because the reviewer likes them;
others get parked indefinitely without explanation. Substrate
accumulates noise and projects lose trust in the promotion process.

This contract makes promotion a checked transition with documented
evidence requirements.

## Eligibility criteria

An artifact is **eligible** for promotion if all of the following
hold:

1. **Generic.** Removable from its origin project without functional
   loss; contains no project-specific names, paths, or assumptions.
2. **Reused or reusable.** Either already used in 2+ projects, or
   articulated to apply to a class of projects (not one specific
   project).
3. **Stable.** Has not changed materially in the most recent
   `min_stable_cycles` harvest cycles (default: 2).
4. **Tested.** Has at least one verifiable test or smoke check in its
   origin project.
5. **Documented.** Has the frontmatter and description required by
   the substrate it would join (per
   [frontmatter-spec.md](01-protocols/frontmatter-spec.md)).
6. **Aligned.** Does not contradict any existing substrate file or
   contract.

Failure of any criterion makes the artifact **ineligible** — a
legitimate rejection ground, not a defect.

## Required evidence

For each promotion candidate, `@harvest` MUST attach:

| Evidence | Source |
| --- | --- |
| Path in origin project | `harvest/candidates/<cycle-id>/<candidate>.md` |
| Frontmatter snapshot | Embedded |
| Usage citations | Links to commits, issues, or files showing reuse |
| Stability window | Cycle ids over which the artifact has not changed |
| Test reference | Link to test file or smoke script |
| Genericity assessment | Free-text justification with redaction examples if needed |
| Conflict check | List of substrate files compared against |

A candidate without complete evidence is parked, not rejected.
Reviewer cannot make a defensible decision on incomplete evidence.

## Promotion workflow

1. **Identify** — `@harvest` scans project repos.
2. **Assess eligibility** — against criteria above.
3. **Gather evidence** — per the table above.
4. **Propose** — candidate file written under
   `harvest/candidates/<cycle-id>/`.
5. **Review** — reviewer reads evidence and decides.
6. **Apply** — accepted candidates merged into substrate (separate PR
   with migration notes if needed). Parked candidates kept under
   `harvest/parked/`. Rejected candidates noted in the audit record
   with reason.
7. **Audit** — outcome recorded in the cycle's audit record.

## Rejection grounds

Legitimate rejection reasons (must be one of):

- Fails eligibility criterion N (cite which).
- Duplicate of existing substrate file (cite which).
- Project-specific despite cosmetic generalisation.
- Better solved by an instruction than a skill (or vice versa) —
  reviewer should suggest the alternative shape.
- Out of scope for the substrate (cite which scope rule).

"Reviewer dislikes" is not a legitimate rejection ground. If the
reviewer cannot articulate a documented reason, the candidate is
parked, not rejected.

## Reviewer role

The reviewer is a named role (may be the same person as the harvest
owner or different). Responsibilities:

- Read candidate evidence.
- Render a decision per candidate: `promoted` / `parked` / `rejected`.
- Provide a written reason for `parked` and `rejected`.
- Sign off the audit record's promotion section.

The reviewer is the gate; `@harvest` is the proposer; they MUST be
separable roles even if held by the same person, to keep
accountability legible in the audit record.

## Outcome states

| State | Meaning |
| --- | --- |
| `promoted` | Merged into substrate. Origin project should now consume substrate version. |
| `parked` | Eligible but not promoted this cycle. Re-evaluated in future cycles. |
| `rejected` | Ineligible or otherwise declined. Not re-evaluated unless conditions change. |

All three are valid terminal states for a cycle. None is a failure.

## Audit trail

Every promotion decision is recorded in the cycle's audit record with:

- Candidate path in origin project.
- Outcome state.
- Reason (for `parked` / `rejected`).
- Reviewer name.
- Date.
- Link to the promotion PR (for `promoted`).

Audit records are append-only. A later cycle may re-evaluate a parked
candidate, but the original cycle's record does not change.
