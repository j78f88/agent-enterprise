# Planner Session-End Menu

At natural stopping points, use #tool:askQuestions to present the next action as clickable options — **never** render the menu as a plain text list.

**Question 1 — "What's next?"** with these options (adjust based on context):

| Option                                                  | When to show                                                                                      | Recommended?                          |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------- |
| "Plan a new feature (`/plan-feature`)"                  | Always                                                                                            | If no drafts exist                    |
| "Diagnose a bug (`/plan-fix`)"                          | Always                                                                                            | —                                     |
| "Brainstorm an idea (`/brainstorm`)"                    | Always                                                                                            | —                                     |
| "Draft from brainstorm (`/plan-feature --from {slug}`)" | Brainstorm has `[SELECTED]` markers OR a saved brainstorm exists with no corresponding draft-plan | Yes, if `[SELECTED]` candidates exist |
| "Revise a draft (`/revise-draft`)"                      | Draft plans exist                                                                                 | —                                     |
| "Promote a draft (`/promote-draft`)"                    | Draft plan exists, looks ready                                                                    | Yes, if draft is complete             |
| "Promote an ADR (`/promote-adr-to-sprint ADR-NNN`)"     | Accepted ADR exists without a corresponding sprint                                                | Yes, if ADR is freshly accepted       |
| "Review pipeline (`/review-pipeline`)"                  | 2+ draft plans exist                                                                              | —                                     |
| "Combine drafts (`/combine-drafts`)"                    | 2+ related drafts exist                                                                           | —                                     |
| "Triage bugs (`/triage-bugs`)"                          | Open bugs exist in backlog                                                                        | Yes, if 🔴 bugs exist                 |
| "Capture a bug (`@bug`)"                                | Always                                                                                            | —                                     |
| "Clean up planning docs (`/plan-cleanup`)"              | Always (low priority)                                                                             | —                                     |
| "Hand off to Sprint Lead"                               | Promoted sprint exists                                                                            | —                                     |
| "Done for now"                                          | Always                                                                                            | —                                     |

**Context-aware filtering:** Only show options that are relevant. Include actual draft filenames and open bug count in the question text when available.
