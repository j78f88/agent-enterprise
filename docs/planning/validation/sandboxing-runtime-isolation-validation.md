# Validation: Sandboxing & runtime isolation (Cluster 1)

**Date:** 2026-06-15
**Validator:** `@pm` (subagent, WRITE:VALIDATION)
**Source research:** `docs/planning/research/sandboxing-runtime-isolation-research.md`
**Validation-framework:** `.github/instructions/validation-framework.instructions.md` (5-test)

---

## Chosen frame — frame (a) "control to reference/map", with two (c) "mixed" exceptions

**Decision:** For this cluster, the default frame is **(a) controls the AU-gov compliance template should reference/map to** — NOT substrate features to build. Two patterns are **(c) mixed** because the template can meaningfully ship a thin, build-time artifact (a profile/policy stub + mapping) on top of the reference, without claiming to re-implement the isolation primitive.

**Rationale:**

1. **The repositioning forecloses frame (b) for almost everything here.** As of 2026-06-01 the project is a *proposal-tier AU-gov compliance template*, not a runtime/substrate. Every isolation primitive in this cluster (Seatbelt, bubblewrap, Landlock, Firecracker, gVisor, runc, git worktree, egress proxy) is already *shipped, default-on or opt-in, in the agents themselves* (Codex CLI, Claude Code, Cursor, Copilot, Devin) and in commodity infra (E2B, Modal, Fly, Daytona). A compliance template that re-builds any of these would be re-implementing mature vendor primitives — the exact "novel substrate" trap the repositioning closed. So the unit of value the template adds is **mapping these controls to an AU-gov framework (ISM / Essential Eight / PSPF) and prescribing which to enforce**, not building them.

2. **The research's own load-bearing finding reinforces this.** The doc states filesystem/compute isolation "largely holds" and that **egress is where isolation actually fails**, and that the lethal-trifecta failure is "not patchable at the model layer — it is architectural." A template cannot patch an architectural class either; what it *can* do is require the architecture (break the trifecta, enforce two-phase network, enforce mode separation) as a control. That is compliance-template work, not substrate work.

3. **Why two patterns are (c) mixed, not (a).** Mode separation (Pattern 4) and the two-phase cloud network design (a sub-pattern of Pattern 2) are places where a proposal-tier template can ship a *concrete build-time artifact* — a default permission-mode policy stub and a network-phase profile — that is genuinely additive over "go read the vendor docs," because the value is in the *prescribed default + the AU-gov mapping*, not in the enforcement engine (which the agent already provides). This is "mixed": reference the primitive, ship the policy mapping.

---

## Pattern inventory

The research stacks five layers; I treat each as its own candidate:

- **P1** — Local OS-level process confinement (Seatbelt / bubblewrap / Landlock+seccomp)
- **P2** — Cloud microVM / container sandboxes with two-phase network
- **P3** — Isolated git worktrees for parallel agents
- **P4** — Execution-mode separation (read-only → approve → auto → YOLO)
- **P5** — Prompt-injection exfiltration through legitimate egress (the lethal trifecta / cross-layer failure)

---

## P1 — Local OS-level process confinement

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Process confinement is causally *why* a local coding agent is safe to run — it is the enforced boundary, not incidental decoration. For a compliance template, "require an enforced OS sandbox" is the actual control that produces the security outcome. |
| 2. Frequency match | PASS | Applies every time an agent runs locally; matches the project-scoped, per-engagement cadence of a compliance template (the control is asserted once per environment baseline, exactly the template's unit of output). |
| 3. Survivorship bias | PASS | The doc shows the *losers' lesson too*: `sandbox-exec` is deprecated, Landlock has documented bypasses, exclusion lists grow. The template must reference the control while *citing its limits* — which is what survivorship-aware framing requires, and the research supplies it. |
| 4. Anti-pattern / value | PASS | Drives real risk reduction (filesystem/compute isolation "largely holds" per the research), not engagement metrics. N/A-adjacent to engagement; clearly value-side. |
| 5. Complexity cost | PASS (as frame-a reference) | As a *control to map*, cost is low: cite the vendor primitive + map to ISM/E8. It would FAIL if scoped as build-it-yourself (re-implementing Seatbelt/bwrap is exactly the disconfirmed-substrate trap), which is why frame (a) is chosen. |

**Label: VALIDATED** (as a frame-(a) control reference). The template should require "agent shell/tool execution runs inside an OS-enforced, deny-by-default sandbox" and map it to AU-gov framework controls, explicitly noting the macOS `sandbox-exec` deprecation gap and Landlock non-FS bypass as residual-risk caveats. **Do not build the sandbox.**

---

## P2 — Cloud microVM / container sandboxes (two-phase network)

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Ephemeral per-task VM + offline agent phase is causally the thing that keeps a cloud agent from touching prod / exfiltrating during execution. The two-phase split is *the* de-facto cloud control, not a side effect. |
| 2. Frequency match | PASS | Asserted once per cloud-environment baseline — matches template cadence. The two-phase network profile is a standing config, not a per-session interaction. |
| 3. Survivorship bias | PASS | Research surfaces the failures of the apparent winners: AWS Bedrock AgentCore "complete isolation" still leaked DNS; shared-kernel Docker inherits the runc-escape class; microVM immunity is *vendor self-attested, not independently audited*. A template that cites these caveats avoids copying a marketing claim. |
| 4. Anti-pattern / value | PASS | Genuine value (prod-blast-radius containment). Not engagement-driven. |
| 5. Complexity cost | PASS as (c) mixed | Reference + map = low cost. The additive build-time artifact (a prescribed two-phase network profile: networked setup → secrets-wiped offline agent phase) is a *thin policy stub*, not an isolation engine. It would FAIL if scoped to build the sandbox runtime. |

**Label: VALIDATED** (frame (c) mixed). Reference microVM/container isolation as a mappable control **and** ship a prescribed two-phase-network policy stub (setup-online → agent-offline, secrets wiped) as a template artifact, with an explicit caveat that "Docker == sandbox" is false (runc-escape class) and microVM claims are unaudited. **The egress sub-layer is the weak point — see P5.**

---

## P3 — Isolated git worktrees for parallel agents

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | **FAIL** | Worktrees solve *developer-ergonomics collision* (file/index contention across N parallel agents), not the security/compliance outcome. The research is explicit: worktrees "isolate code but not the runtime" — shared ports, DB, services, host FS. They are correlated with multi-agent setups, not causal to isolation. |
| 2. Frequency match | N/A | Moot once Test 1 fails for compliance framing; would only matter for a dev-productivity feature, which is out of template scope. |
| 3. Survivorship bias | **FAIL** | Strong disconfirming evidence: the two highest-profile worktree GUIs wound down despite traction (Crystal deprecated Feb 2026, vibe-kanban sunsetting), and Imbue built Sculptor *specifically to escape worktree pain*, shifting toward full containers. Copying the worktree pattern copies an approach the market is actively retreating from. |
| 4. Anti-pattern / value | FAIL (for this project) | Value is real for parallel-agent dev throughput, but that is not the compliance template's value axis. No security/compliance value to map. |
| 5. Complexity cost | FAIL | High ongoing pain (stale-worktree GC, `.env`/`node_modules` non-propagation, Docker name collisions, incomplete submodule support) for zero compliance-template payoff. |

**Label: REJECTED.** Worktree isolation is a dev-ergonomics pattern, not a compliance control, and the market is migrating away from it toward containers. Failed Tests 1, 3, 5. **The salvageable signal is not the worktree — it is "runtime isolation per parallel agent," which is already covered by P2 (container/VM per task).** Recommend recording a standing non-goal so this doesn't resurface.

---

## P4 — Execution-mode separation (read-only → approve → auto → YOLO)

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Mode separation is causally the control that contains the Replit-class incident (over-permissioned, in-sandbox destruction). The research's single most-cited lesson: "mode separation and environment isolation must be enforced, not instructed." Directly causal to the compliance outcome. |
| 2. Frequency match | PASS | A prescribed default mode + protected-path policy is a standing baseline assertion — matches template cadence. |
| 3. Survivorship bias | PASS | Research shows the *failed* variant (denylist-based YOLO gating is "structurally unsound" — Backslash showed 4 bypasses; mode leaks at the MCP boundary). The validated control is therefore "enforce safe-default modes + classifier-or-sandbox enforcement," NOT "ship a denylist" — survivorship-corrected. |
| 4. Anti-pattern / value | PASS | Real value (blast-radius reduction). Caveat the template must encode: approval fatigue (93% rubber-stamped) means *prompt-count is not a control* — value comes from enforced defaults, not from asking more often. |
| 5. Complexity cost | PASS as (c) mixed | As a frame-(a) reference: low. The additive artifact — a prescribed default permission-mode + protected-path policy stub mapped to AU-gov controls — is cheap and genuinely additive. Building the enforcement engine would FAIL (agents already ship it). |

**Label: VALIDATED** (frame (c) mixed). Reference the mode ladder as a mappable control **and** ship a prescribed-default policy stub (safe default mode, protected paths, no-denylist-only gating, enforce-don't-instruct) mapped to AU-gov framework controls. Encode the explicit caveats: denylists are not a control, `bypassPermissions` "offers no protection against prompt injection," and mode leaks at the MCP boundary.

---

## P5 — Prompt-injection exfiltration through legitimate egress (lethal trifecta)

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | This *is* the dominant residual-risk class — every documented exfil chain reused a legitimate egress path. For a compliance template, "require breaking the lethal trifecta / TLS-aware egress control" is the highest-leverage control to map. Causal to the actual failure mode. |
| 2. Frequency match | PASS | A standing architectural requirement asserted per environment baseline — matches template cadence. |
| 3. Survivorship bias | PASS | The research IS the survivorship correction: it documents that filesystem sandboxing (the apparent "winner") does NOT address this, and that vendor fixes were capability-removal, not sandbox-hardening. Mapping this control avoids the trap of assuming a sandbox is sufficient. |
| 4. Anti-pattern / value | PASS | Pure value (prevents the CVSS 9.x zero-click exfil class: EchoLeak, CamoLeak). No engagement dimension. |
| 5. Complexity cost | PASS as control-reference; **partial gap** | As a *control to require/map*: low cost and high value. But the research is explicit that **TLS-aware egress filtering is "not shipped by default" by any vendor** — so the control the template prescribes (TLS-aware egress + trifecta-breaking) currently has no off-the-shelf compliant implementation. The template can *require* it and *flag the gap*; it cannot point to a shipped solution. |

**Label: VALIDATED** (frame (a) control reference) — **but flag the implementation gap.** The template should make "break the lethal trifecta (no co-presence of private-data access + untrusted content + external egress) and require TLS-aware egress control" a top-priority mapped control, while explicitly recording that no vendor ships a default-on compliant egress filter today (residual-risk / unsolved). This is the cluster's single most load-bearing control.

> **Note on CVE/CVSS provenance:** the research flags that CVE IDs and CVSS scores came from security-vendor writeups, not NVD directly. Any control mapping that *cites* a specific CVE as evidence must verify against NVD/vendor advisories before the template quotes it as authoritative. This is a documentation-integrity caveat, not a validation blocker.

---

## Summary table

| Pattern | Frame | Label |
| --- | --- | --- |
| P1 — Local OS-level process confinement | (a) control reference | VALIDATED |
| P2 — Cloud microVM/container + two-phase network | (c) mixed | VALIDATED |
| P3 — Isolated git worktrees | (a) attempted → rejected | REJECTED |
| P4 — Execution-mode separation | (c) mixed | VALIDATED |
| P5 — Lethal-trifecta egress exfil | (a) control reference | VALIDATED (gap-flagged) |

**Cluster verdict:** Validate four of five as AU-gov-mappable controls (two with thin build-time policy stubs). Reject worktrees as a dev-ergonomics pattern the market is abandoning. The load-bearing control is **egress / lethal-trifecta (P5)**, which has no shipped compliant implementation and must be flagged as the cluster's primary residual risk.
