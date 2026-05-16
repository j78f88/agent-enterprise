# 03 — Format Upgrades: Handoff Rejections + Hash-Chain Signing

> **Depends on:** Nothing (standalone)
> **Commit:** `feat(formats): structured handoff fields, hash-chain signing for FILE_HASHES`
> **Verify:** resolved handoff format includes new fields; hash-chain script validates sample

---

## Task Group 2.1: Structured-error fields for handoff rejections

Files: `instructions/configurable/handoff-rejection-format.instructions.md`

**Why:** evlog pattern. Rejections with `Fix` + `Link` fields are immediately actionable.

- [ ] Add `Fix` field (one-sentence actionable step) between `Reason` and `Proposed resolution` in entry format
- [ ] Add `Link` field (path to constraining doc/ADR/instruction) after `Fix`
- [ ] Update Enforcement section: add WARNING for missing `Fix` or `Link` on new entries
- [ ] Verify after init.py: resolved version includes new fields

---

## Task Group 2.2: Hash-chain signing for FILE_HASHES.md

Files: `starters/FILE_HASHES.md`, `scripts/verify-hash-chain.py`, `tests/test_hash_chain.py`

**Why:** evlog pattern. Each entry's hash chains to the prior — tamper-evident.

- [ ] Add `Prior Hash` column to FILE_HASHES table (first 8 chars of SHA-256 of prior row's hash; first entry = `GENESIS`)
- [ ] Update template comments to document chain semantics
- [ ] Create `scripts/verify-hash-chain.py` (~40 lines) — parses table, verifies chain integrity, exits non-zero on tamper
- [ ] Create `tests/test_hash_chain.py` — validates a sample chain with known-good and tampered data

---

## Verification

```powershell
# init.py resolves handoff format correctly
python init.py --config config/project.config.example.yml
Select-String -Path resolved/instructions/handoff-rejection-format.instructions.md -Pattern "Fix"  # matches
Select-String -Path resolved/instructions/handoff-rejection-format.instructions.md -Pattern "Link" # matches

# Hash-chain script works
python scripts/verify-hash-chain.py starters/FILE_HASHES.md

# New test passes
python -m pytest tests/test_hash_chain.py -v

# Full suite still green
python -m pytest tests/ -v
```
