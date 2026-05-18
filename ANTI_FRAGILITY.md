# Anti-Fragility: Lessons from First Orchestrated Deployment

This document captures failure patterns observed the first time agent-homebase
was driven by an automated dispatch orchestrator (rather than interactively by
a human in VS Code). The patterns are generic and apply to any project that
puts an autonomous dispatcher on top of agent-homebase. They are recorded here
so future adopters can avoid them.

> **TL;DR** Agent-homebase is a generic skills library. It is designed for
> interactive use by default. If you bolt on an automated orchestrator and an
> external issue tracker, do that work in a **separate orchestration repo** and
> keep project-specific governance in a **separate project repo**. Do not
> write either kind of file into agent-homebase itself. See
> [docs/EXTENSION_GUIDE.md](docs/EXTENSION_GUIDE.md).

---

## Pattern 1 â€” Ghost-Done

**What happened.** Six tracker issues were transitioned to `Done` while the
filesystem contained zero corresponding artifacts. The dispatched agents had
moved through the workflow, but nothing they were supposed to produce existed
on disk. Reviewers discovered the gap days later when trying to consume the
"completed" work.

**Root cause.** The orchestrator transitioned ticket state when an agent
session ended, not when verifiable artifacts existed at known paths. There was
no completion-verification step between "agent finished talking" and "ticket is
Done". Skills that had clear `outputs:` declarations were treated the same as
free-form ones; nothing checked that those outputs actually appeared.

### Mitigation (in the orchestration layer, not here)

- Every dispatched task should declare its expected artifact paths up front.
- Before any `Done` transition, the orchestrator must verify each path exists
  and that its content was produced in the current session (e.g., compare
  modification time to session start, or require a fresh git diff).
- If verification fails, the ticket goes back to `In Progress` with a
  rejection note, not forward to `Done`.

---

## Pattern 2 â€” Split-state

**What happened.** Active work state was scattered across markdown ledgers
(`SPRINTS.md`, `BACKLOG_LEDGER.md`, `BUG_BACKLOG.md`), tracker issues, handoff
manifests, filesystem checkboxes inside skill prompts, and git history. No
single query answered the question *"where is this piece of work right now?"*
Dispatched agents spent a meaningful share of their context window
reconstructing state instead of doing the requested work.

**Root cause.** Each subsystem (skill prompts, ledgers, tracker, handoffs) was
designed independently and the relationships between them were implicit. The
markdown-based state model assumed a human in the loop who could glance at all
of it at once. An automated dispatcher cannot.

### Mitigation

- Pick a single source of truth for "what is the current state of task X" and
  make every other surface a derived view.
- If you adopt an external tracker, stop maintaining a parallel markdown
  ledger of the same data. Either delete the ledger or make it a generated
  read-only mirror.
- Keep handoff state in one place â€” either inside the tracker issue or in a
  single manifest file per session, not both.

---

## Pattern 3 â€” Governance-before-proven-loop

**What happened.** A multi-layered governance stack (Rego policies,
composition constraints, tier-1/2/3 return schemas, escalation rules,
file-hash determinism, sandboxed isolation) was specified and partially
implemented before the basic dispatch loop had been run end-to-end on a real
project. When the dispatch loop produced Ghost-Done, the governance layer
could not catch it because governance constrains what an agent *outputs*, not
whether the dispatcher correctly observed that output.

**Root cause.** Governance was prioritized as the differentiator. The simpler
question â€” *"can the dispatcher reliably tell whether an agent did the
work?"* â€” was assumed solved.

### Mitigation

- Prove the loop on at least one real project before adding governance layers.
- Each governance feature should answer the question *"which observed failure
  mode does this prevent?"* If the answer is hypothetical, defer it.
- Verification of artifact existence is a precondition for every other layer.

---

## Pattern 4 â€” Repo pollution

**What happened.** Project-specific files (commercial validation rules, a
domain-specific rate cap, RLS policy guidance, payment-state machines) were
written directly into `instructions/configurable/`. The README was edited to
reflect a project-specific count of agents. A project-specific profile landed
in `profiles/`. The boundary between "reusable library" and "project
configuration" disappeared.

**Root cause.** The agents that did the work had write access to the library
repo and no instruction telling them their output belonged elsewhere. The
profile system's intent â€” that project-specific config lives in the consuming
project â€” was documented but not enforced at the repo boundary.

### Mitigation

- Treat agent-homebase as an external dependency. Consume it as a git
  submodule, vendored copy, or package. Do not commit project-specific files
  into it.
- If you need to extend or override a generic instruction, do it in your
  project repo and reference it from your profile. See
  [docs/EXTENSION_GUIDE.md](docs/EXTENSION_GUIDE.md).
- If a change feels generic enough to upstream, open a PR â€” but make the
  upstream commit pure (no project name, no project-specific values, no
  hard-coded counts).

---

## Recommendation for orchestrated adopters

If you are putting an automated dispatcher (e.g., a workflow agent that picks
tickets off a queue and assigns them to skills) on top of agent-homebase:

1. **Three repos, not one.**
   - `agent-homebase` â€” generic skills library (this repo).
   - `<your>-orchestration` â€” dispatch logic, tracker integration,
     completion-verification rules, retry/escalation policy.
   - `<your>-project` â€” application code plus project-specific governance
     instructions and the profile that wires everything together.
2. **Verify before transitioning.** Never mark a ticket `Done` based on
   "session ended". Require artifact paths and check they exist with fresh
   content.
3. **One source of truth per fact.** If the tracker holds task state, do not
   maintain a parallel markdown ledger of the same state.
4. **Prove the loop before adding policy.** Run the dispatcher end-to-end on
   one real ticket and inspect the result before layering governance.

See [docs/EXTENSION_GUIDE.md](docs/EXTENSION_GUIDE.md) for the intended
consumption model.
