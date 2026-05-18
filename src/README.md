# src/

Standalone Python phase library providing verification, durability,
isolation, and determinism capabilities for adopter projects that want
them. `init.py` and the build pipeline operate independently of this
code.

## Modules

| Package | Purpose |
| --- | --- |
| `phase1_verification/` | Artifact existence and content checks |
| `phase2_durability/` | Hash-chain integrity and append-only guarantees |
| `phase3_isolation/` | Write-permit enforcement and path boundaries |
| `phase4_determinism/` | Reproducible output validation |

Each module is a proper Python package with `__init__.py`. Import
directly:

```python
from src.phase2_durability import verify_hash_chain
```

See `tests/test_phase2.py`, `tests/test_phase3.py`, and
`tests/test_phase4.py` for usage examples.
