# Validation: Context management for agents (Cluster 7)

**Date:** 2026-06-15
**Validator:** `@pm`
**Source research:** `docs/planning/research/context-management-research.md`
**Cluster:** 7 — Context management (ADJACENT to core mission: efficiency / context-cost, not security/process-control)
**Framework:** `.github/instructions/validation-framework.instructions.md` (5-test echo-chamber filter)

---

## Frame decision (per-cluster)

**Chosen frame: (a) controls the AU-gov compliance template should reference — with a single (c) mixed exception for memory poisoning, and one (a)/(b)-adjacent doctrine pattern handled as a referenced control.**

**Rationale.** agent-enterprise was repositioned on 2026-06-01: its two original "novel safety substrate" claims were disconfirmed as novel, and the current direction is an **Australian-government compliance template, proposal-tier**. That repositioning is the single most important input here. A compliance template is a **document/proposal artifact that tells an integrator which controls to implement and how to evidence them** — it is not a runtime, not a memory engine, not a multi-agent orchestrator. This entire cluster is, by the researcher's own framing, ADJACENT: it is about context-cost *efficiency*, and it touches the mission only where memory becomes an *attack surface* (memory poisoning) or where context handoff becomes a *process-control* primitive.

Consequently, for an adjacent efficiency cluster, the default frame is **(a): treat each pattern as a control the template should reference (require/recommend that an implementing system address it), not a substrate feature we build.** Building any of these (a context-graph store, a compaction engine, a subagent orchestrator) would be us re-implementing tooling that frontier labs and funded vendors already ship — pure echo-chamber pattern-matching, and a direct frequency-match mismatch with a proposal-tier document deliverable. The complexity-cost bar (test 5) for *building* anything here is therefore set very high, and no pattern in this cluster clears it as a build.

The **one mixed (c) case is memory poisoning** (Pattern 6b): it is the cluster's genuine collision with the security/process-control core (OWASP ASI06, MINJA, MemMorph). It is still framed as a *control the template references* rather than a substrate feature, but it is the only item that earns a place inside the mission rather than merely adjacent to it, so it is flagged for hand-back to the security clusters.

Net: **the value of this cluster to agent-enterprise is as compliance-control content, not as features.** Every pattern below is validated against "should the AU-gov template *reference* this control?" — not "should we build it?"

---

## Patterns identified

1. Context engineering as a named discipline (doctrine layer)
2. Long-context decay / "context rot" (the problem statement)
3. Compaction & handoff (summarise-and-reinitialise)
4. Structured / graph memory with decision traces (vs flat append memory)
5. Isolated-context subagents (orchestrator-worker separation)
6a. Distilled / episodic memory (store reflections, not transcripts) — efficiency facet
6b. Memory poisoning (OWASP ASI06) — security facet of distilled persistent memory

Patterns 6a and 6b are split because they fail/pass differently: 6a is an efficiency feature (low value to a template), 6b is a security control (the cluster's one core tie-in).

---

## Pattern 1 — Context engineering as a named discipline (doctrine)

**Frame:** (a) control the template references — as a *requirement that implementing systems apply a context-engineering discipline*, not as something we build.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | The discipline is causally the right framing — every concrete control below derives from it, and a compliance template that references controls needs a doctrine label to organise them under. It earns its place as the umbrella, not by analogy. |
| 2. Frequency match | PASS | Doctrine is reference material, not a runtime feature, so it matches a proposal-tier document deliverable's cadence perfectly — it is read once and cited, not exercised per-session. No frequency warp. |
| 3. Survivorship bias | PASS | This is a frontier-lab published practice (Anthropic), not a pattern lifted from a winner while ignoring losers; there is no failed-app cohort to compare because it is doctrine, not a product. |
| 4. Anti-pattern / engagement-at-cost | PASS | It drives real value (it is the organising principle for the genuinely useful controls) and creates no session-count incentive — it is a document section, not an engagement mechanic. |
| 5. Complexity cost | PASS | As a *referenced control* the cost is one template section pointing implementers at the discipline; near-zero build cost. (It would FAIL hard if framed as "build a context-engineering layer" — but that is not the frame.) |

**Label: VALIDATED** — but strictly as the doctrine/umbrella section of the template, not as a feature. Cleared to hand off only as reference content that frames Patterns 2–6.

---

## Pattern 2 — Long-context decay / "context rot" (problem statement)

**Frame:** (a) control the template references — as a *requirement that implementing systems acknowledge and bound effective context length* (e.g., benchmark per-model, do not assume uniform recall across the advertised window).

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | The decay is independently replicated across four benchmark efforts (Lost-in-the-Middle, RULER, NoLiMa, Chroma) — it is the actual causal driver of why every mitigation exists, not an incidental correlate. |
| 2. Frequency match | PASS | As referenced control content (an evidence requirement: "demonstrate awareness of effective vs advertised context length"), it fits a document deliverable. It does not impose any runtime cadence on the template. |
| 3. Survivorship bias | PASS | The evidence is benchmark data over 12–18 models per study, not survivor apps; it explicitly includes models that *fail* (the whole point of the benchmarks), so the survivorship trap is inverted/avoided. |
| 4. Anti-pattern / engagement-at-cost | PASS | Acknowledging decay drives correctness (avoids silent confident-wrong answers); no engagement-at-cost dimension exists for a problem-statement control. |
| 5. Complexity cost | PASS | Referencing it costs one control + evidence note. (FAIL if mistaken for "build a context-length benchmark harness" — out of scope for a proposal-tier template.) |

**Label: VALIDATED** — as a referenced control/evidence requirement only. This is the empirical floor the template should cite to justify the compaction and memory-hygiene controls below.

---

## Pattern 3 — Compaction & handoff (summarise-and-reinitialise)

**Frame:** (a) control the template references — specifically a *process-control* requirement: where a system uses compaction/handoff, it must verify that the summary preserved load-bearing constraints (the unmet need the research surfaced).

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Compaction is the most broadly *deployed* technique (default-on in Claude Code, a Claude API primitive); it is causally the standard answer to window overflow, not incidental. The control-relevant insight is its documented failure (lossy drop), which is the real driver of risk. |
| 2. Frequency match | PASS | As a referenced control ("if you compact, verify the summary"), it maps to a document deliverable. We are not shipping a compaction engine, so no runtime-cadence mismatch with proposal-tier scope. |
| 3. Survivorship bias | PASS | The research surfaces both the winners (shipped, default-on) and the documented failure (agents "spiral" post-compact; nested rules silently dropped) — the failure cohort is explicitly included, so the lesson is balanced, not winner-only. |
| 4. Anti-pattern / engagement-at-cost | PASS | The control drives real value (preventing silent context loss) and has no session-count incentive. |
| 5. Complexity cost | PASS | As a *referenced verification control* the cost is a template clause + evidence checklist item. This is genuinely useful because compaction is lossy-by-default and ships with no built-in "did we keep what mattered" check — a compliance template demanding that verification adds real value at low cost. (Building a compaction-verification tool would FAIL the cost bar; referencing the control passes.) |

**Label: VALIDATED** — as a referenced process-control + evidence requirement. This is the strongest *core-adjacent* item in the cluster because "verify the handoff summary preserved constraints" is a genuine process-control gap with no default fix, and a compliance template is exactly the right place to mandate it.

---

## Pattern 4 — Structured / graph memory with decision traces (vs flat append)

**Frame:** Evaluated as candidate substrate feature (b) — and rejected to (a)-only-if-at-all.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | FAIL | The funded/starred success of Mem0/Zep/Letta is correlated with the *memory-product* market, not with anything agent-enterprise sells. Adopting graph memory because vendors raised money is textbook analogy reasoning; the accuracy claims that would establish causation are almost entirely vendor-self-reported on benchmarks the vendors selected (research's own honesty caveat). |
| 2. Frequency match | FAIL | A temporal knowledge-graph memory engine is a continuously-running runtime component; a proposal-tier AU-gov compliance template is a project-scoped document. The cadence mismatch is severe — this is infrastructure for a memory product, not content for a template. |
| 3. Survivorship bias | FAIL | The research flags exactly the survivor trap: GraphRAG's ~$33K indexing cliff made it "impractical for most teams" at launch, and benchmark wins "don't reliably transfer to bespoke production data." Validating graph memory off the funded survivors while the cost-failed cohort is on record is the bias the framework exists to catch. |
| 4. Anti-pattern / engagement-at-cost | N/A | No engagement-mechanic dimension; the relevant failure is operational, captured under tests 3 and 5. |
| 5. Complexity cost | FAIL | Indexing cost, 2–3× inference latency, super-linear index growth, edge-invalidation correctness risk, and operational complexity vs flat memory — for a proposal-tier deliverable that ships no runtime, the build cost is wholly disproportionate to any value, and even as a *referenced* control it is too implementation-specific to mandate. |

**Label: REJECTED** — fails tests 1, 2, 3, and 5. Not rescuable by reframing for this project: the only rescuable kernel ("flat memory loses the why; prefer trace/validity-aware memory") is too vendor-specific and runtime-heavy to mandate in a proposal-tier compliance template, and recommending it would be recommend-by-analogy. If anything survives, it is a *non-binding note* under the memory-hygiene control, not a feature.

---

## Pattern 5 — Isolated-context subagents (orchestrator-worker separation)

**Frame:** Evaluated as candidate substrate feature (b) — and rejected.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | FAIL | The "+90.2% vs single-agent" headline is Anthropic-internal and unaudited (research caveat), and the design is openly *contested*: Cognition's "Don't Build Multi-Agents" documents subagents producing incompatible work. There is no settled causal claim to adopt — it is a live debate, not an established driver. |
| 2. Frequency match | FAIL | A subagent orchestration runtime is continuous infrastructure at ~15× token cost; a proposal-tier compliance template neither runs agents nor would mandate a 15× cost multiplier on integrators. Severe cadence and scope mismatch. |
| 3. Survivorship bias | FAIL | Validating isolation off Anthropic's read-only-research win while Cognition's coordination-failure cohort (the Mario/bird merge) is explicitly on record is the survivorship trap; the research itself calls it "task-shape-dependent... not a settled best practice." |
| 4. Anti-pattern / engagement-at-cost | N/A | No engagement-mechanic dimension; the ~15× token cost is captured under test 5. |
| 5. Complexity cost | FAIL | ~15× tokens plus an unresolved coordination-coherence problem, for a template that ships no orchestrator — cost vastly exceeds any value to a proposal-tier deliverable. |

**Label: REJECTED** — fails tests 1, 2, 3, and 5. The design axis is openly unresolved in the field, so there is nothing stable to validate; not rescuable for this project.

---

## Pattern 6a — Distilled / episodic memory (efficiency facet: store reflections, not transcripts)

**Frame:** Evaluated as candidate substrate feature (b) — and rejected as a feature.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | FAIL | The distillation lineage (Generative Agents, ChatGPT memory) is foundational research and consumer product, but its *measured* outcome is poor — ChatGPT pre-2026 memory ran 41.5% factual recall and "Dreaming V3" was a fix for it. The success we'd be copying is unproven at the layer we'd build; the efficiency gain is not causally established. |
| 2. Frequency match | FAIL | A persistent distilled-memory store is continuous runtime; a proposal-tier compliance template is project-scoped. Building it is infrastructure unrelated to the deliverable. |
| 3. Survivorship bias | FAIL | The dominant documented outcome is the failure cohort: "graveyard of stale preferences and contradictory notes," users disabling memory, 41.5% recall. Treating distilled memory as a win ignores that the most-measured instance largely failed. |
| 4. Anti-pattern / engagement-at-cost | N/A | No engagement-mechanic dimension. |
| 5. Complexity cost | FAIL | Requires a reconciliation/expiry mechanism most products lack, plus persistent-store ops — disproportionate for a no-runtime template deliverable. |

**Label: REJECTED** (as an efficiency feature) — fails tests 1, 2, 3, 5. The rescuable kernel is *not* the efficiency story but the hygiene/security story, which is Pattern 6b.

---

## Pattern 6b — Memory poisoning (security facet of distilled persistent memory; OWASP ASI06)

**Frame:** (c) mixed — the cluster's one genuine collision with the security/process-control core. Framed as a *control the template references* (memory-integrity / persistent-store hardening), AND flagged for hand-back to the security clusters where it properly belongs.

| Test | Verdict | Reasoning |
| --- | --- | --- |
| 1. Causation vs correlation | PASS | Memory poisoning is causally a distinct, named threat class (OWASP ASI06), not an incidental correlate: persistent memory is *temporally decoupled* — planted today, triggered weeks later on semantic retrieval — which is materially different from session-scoped prompt injection and squarely in the security mission. |
| 2. Frequency match | PASS | As a referenced security control + evidence requirement, it fits a compliance-template deliverable exactly; controls are read-and-cited, matching the proposal-tier cadence with no runtime warp. |
| 3. Survivorship bias | PASS | The evidence base is attack research and defence-gap analysis (MINJA ~95%/70%, MemMorph, "Sleeper"; defences nascent and not default-on), not a survivor-app pattern; the failure cohort *is* the evidence, so the bias is avoided. |
| 4. Anti-pattern / engagement-at-cost | PASS | A security control drives real risk reduction with no session-count incentive. |
| 5. Complexity cost | PASS | As a *referenced control* (require persistent-memory integrity controls, provenance, and detection where a system uses persistent memory) the template cost is one control + evidence note — low cost, high relevance to the actual mission. Numbers (MINJA ~95%/70%) must be re-verified against primary arXiv before quoting, per the research caveat. |

**Label: NEW** — passes all five and emerges from the research as the cluster's one item that belongs *inside* the security/process-control mission rather than adjacent to it (origin note: surfaced via the distilled-memory failure analysis, not copied from a source app). It is the thread `@pm` should pull back into the security clusters rather than treat as Cluster-7 efficiency content. **Cleared to hand off — to the security cluster owners, not as a Cluster-7 feature.**

---

## Summary table

| Pattern | Frame | Label |
| --- | --- | --- |
| 1. Context-engineering doctrine | (a) referenced control | VALIDATED |
| 2. Long-context decay / context rot | (a) referenced control | VALIDATED |
| 3. Compaction & handoff (+ verify the summary) | (a) referenced process-control | VALIDATED |
| 4. Structured / graph memory | (b) build → rejected | REJECTED |
| 5. Isolated-context subagents | (b) build → rejected | REJECTED |
| 6a. Distilled / episodic memory (efficiency) | (b) build → rejected | REJECTED |
| 6b. Memory poisoning (security) | (c) mixed; security control | NEW |

**Bottom line.** This adjacent efficiency cluster yields no substrate features worth building for a proposal-tier AU-gov compliance template. Its real value is **compliance-control content**: three referenced controls (context-engineering doctrine, effective-context-length awareness, and compaction-verification as a process control) plus one genuine security tie-in (memory poisoning) that belongs back in the security clusters. The three "build the memory/orchestration runtime" patterns (graph memory, subagents, distilled-memory store) are rejected on frequency-match and complexity-cost grounds — they are vendor infrastructure we would be copying by analogy, not features that fit the deliverable.

---

## Flagged decisions (for the user — ROADMAP.md does not exist)

- **NEW — Memory poisoning (Pattern 6b) should be re-homed into the security clusters (1–6), not tracked under Cluster 7.** It is the one item here that hits the actual mission (OWASP ASI06, temporally-decoupled persistent-store compromise). Decision needed: route 6b to the security cluster owners as a referenced memory-integrity control. *What do you think — fold it into an existing security cluster, or stand it up as its own control line?*
- **DEFERRED — Compaction-verification control (Pattern 3).** Strongest core-adjacent item: "verify the handoff summary preserved load-bearing constraints" is a real process-control gap with no default fix. Valid in principle as a template control; deferred only because the template's control taxonomy isn't established yet (missing dependency). *Unblock condition: the AU-gov control taxonomy/structure is defined so this can be slotted as a process control.*
- **DEFERRED — Doctrine + effective-context-length controls (Patterns 1 & 2).** VALIDATED as referenced content but only meaningful once the template structure exists; park until the template skeleton is defined.
- **Rejections to consider for `docs/NON_GOALS.md`:** building a graph-memory store (Pattern 4), a subagent orchestrator (Pattern 5), or a distilled-memory runtime (Pattern 6a). These are standing "no, we don't build vendor infrastructure" calls for a proposal-tier template. *Note: `@planner` owns NON_GOALS.md and any edit needs an approval marker — flagging, not writing.*
- **Verification debt before any of this is quoted as authoritative:** the GraphRAG "$33K / ~1000×" figures, all memory-vendor accuracy deltas, Anthropic's "+90.2% / ~15×" internals, and MINJA's "~95% / ~70%" rates are single-source / vendor / preprint per the research's own caveat. Do not cite as neutral in any template control without primary-source confirmation.
