---
title: "Control register home"
status: proposal
trust: trusted
classification: OFFICIAL
date: 2026-06-01
---

# `controls/` — AU gov control register

**Status:** PROPOSAL — container scaffolding, awaiting owner ratification. Not canonical.
The framework map below is a **candidate** drawn from the build handoff; it is **not**
ratified until the owner promotes it.

Compliance is the spine, not an add-on: claims become defensible when they trace to
**authoritative AU gov guidance** rather than being asserted. This home holds the
control register that claims anchor to via `claim.control_anchor`.

## Control-anchor record (shape)

One JSON file per control, e.g. `acsc-ism-XXXX.json`:

```json
{
  "framework": "ACSC ISM",
  "control_id": "ISM-XXXX",
  "title": "…",
  "version": "2025-XX",
  "url": "https://…",
  "retrieval_date": "YYYY-MM-DD",
  "classification": "OFFICIAL",
  "applies_to_profiles": ["own-agency", "other-gov-orgs", "vendor-baseline"]
}
```

A claim references it as:

```json
"control_anchor": { "framework": "ACSC ISM", "control_id": "ISM-XXXX", "relationship": "supports" }
```

## Candidate framework map (NOT ratified)

To be verified for current version/date when research runs, per the handoff's
compliance anchor map:

- **ACSC ISM**, **Essential Eight**, **PSPF** (+ data classification).
- **DTA** Policy for Responsible Use of AI in Government + AI assurance framework.
- **ACSC/CISA/NCSC** Guidelines for Secure AI System Development.
- **NIST** SSDF, AI RMF; **SLSA**.
- **IRAP** + Hosting Certification Framework.
- **SFIA** (vendor baseline).

Three consumer profiles consume these differently (own agency / other gov orgs /
vendors) — `applies_to_profiles` keeps that explicit. A top redundancy risk to
surface honestly: whether a reusable gov AI-coding template already exists
(US GSA/CISA, UK GDS/NCSC, ACSC/DTA).
