# Project Reorganization Guide

**Date**: April 27, 2026  
**Changes**: Root directory cleanup and phase-based organization

---

## What Changed

The project structure has been reorganized to improve clarity and maintainability:

### Before (Root Directory)
```
agent-homebase/
├── validator.py
├── policy_engine.py
├── db.py
├── checkpoint.py
├── workflow.py
├── migrate.py
├── dual_write.py
├── sandbox.py
├── capabilities.py
├── sandbox_checkpoint.py
├── logical_time.py
├── prompt_versioning.py
├── deterministic_composition.py
├── llm_config.py
├── replay_verification.py
├── PHASE_4_IMPLEMENTATION_SUMMARY.md
├── sandbox-architecture.instructions.md
├── IMPLEMENTATION_PLAN.md
├── ONBOARDING.md
├── CHANGELOG.md
├── project.config.example.yml
├── plugin.json
└── ... (15+ files in root)
```

### After (Organized by Phase)
```
agent-homebase/
├── src/                          # All source code
│   ├── phase1_verification/      # Formal verification
│   │   ├── validator.py
│   │   └── policy_engine.py
│   ├── phase2_durability/        # Durable execution
│   │   ├── db.py
│   │   ├── checkpoint.py
│   │   ├── workflow.py
│   │   ├── migrate.py
│   │   └── dual_write.py
│   ├── phase3_isolation/         # Sandboxing
│   │   ├── sandbox.py
│   │   ├── capabilities.py
│   │   └── sandbox_checkpoint.py
│   ├── phase4_determinism/       # Determinism & replay
│   │   ├── logical_time.py
│   │   ├── prompt_versioning.py
│   │   ├── deterministic_composition.py
│   │   ├── llm_config.py
│   │   └── replay_verification.py
│   └── __init__.py
├── docs/                         # Documentation
│   ├── PHASE_4_IMPLEMENTATION_SUMMARY.md
│   ├── sandbox-architecture.instructions.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── ONBOARDING.md
│   └── CHANGELOG.md
├── config/                       # Configuration
│   ├── project.config.example.yml
│   └── plugin.json
├── tests/                        # Tests (unchanged)
├── instructions/                 # Instructions (unchanged)
├── skills/                       # Skills (unchanged)
└── ... (clean root directory)
```

---

## Migration Steps

### If You Have Existing Code That Imports These Modules

**Old imports:**
```python
from logical_time import tick, LogicalClock
from prompt_versioning import PromptVersioner
from deterministic_composition import sort_items_deterministic
from llm_config import LLMConfig
from replay_verification import DeterministicExecutionContext
```

**New imports:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from phase4_determinism.logical_time import tick, LogicalClock
from phase4_determinism.prompt_versioning import PromptVersioner
from phase4_determinism.deterministic_composition import sort_items_deterministic
from phase4_determinism.llm_config import LLMConfig
from phase4_determinism.replay_verification import DeterministicExecutionContext
```

**Or use package imports:**
```python
from src.phase4_determinism import (
    tick, LogicalClock, PromptVersioner, 
    sort_items_deterministic, LLMConfig
)
```

### If You Reference Documentation

**Old paths:**
```
ONBOARDING.md
IMPLEMENTATION_PLAN.md
PHASE_4_IMPLEMENTATION_SUMMARY.md
sandbox-architecture.instructions.md
```

**New paths:**
```
docs/ONBOARDING.md
docs/IMPLEMENTATION_PLAN.md
docs/PHASE_4_IMPLEMENTATION_SUMMARY.md
docs/sandbox-architecture.instructions.md
```

### If You Reference Configuration Files

**Old paths:**
```
project.config.example.yml
plugin.json
```

**New paths:**
```
config/project.config.example.yml
config/plugin.json
```

---

## Benefits of New Structure

1. **Clear Phase Separation**: Each implementation phase has its own directory
2. **Easier Navigation**: Related files grouped together
3. **Clean Root**: Only 8 top-level items vs. 25+ before
4. **Better Imports**: `from src.phase4_determinism.logical_time` is self-documenting
5. **Scalability**: Easy to add Phase 5, 6, 7 without cluttering root
6. **Documentation Consolidation**: All docs in one place
7. **Professional Structure**: Matches standard Python project layouts

---

## File Mappings

### Phase 1 - Formal Verification
| Old Location | New Location |
|--------------|--------------|
| `validator.py` | `src/phase1_verification/validator.py` |
| `policy_engine.py` | `src/phase1_verification/policy_engine.py` |

### Phase 2 - Durable Execution
| Old Location | New Location |
|--------------|--------------|
| `db.py` | `src/phase2_durability/db.py` |
| `checkpoint.py` | `src/phase2_durability/checkpoint.py` |
| `workflow.py` | `src/phase2_durability/workflow.py` |
| `migrate.py` | `src/phase2_durability/migrate.py` |
| `dual_write.py` | `src/phase2_durability/dual_write.py` |

### Phase 3 - Sandboxing & Isolation
| Old Location | New Location |
|--------------|--------------|
| `sandbox.py` | `src/phase3_isolation/sandbox.py` |
| `capabilities.py` | `src/phase3_isolation/capabilities.py` |
| `sandbox_checkpoint.py` | `src/phase3_isolation/sandbox_checkpoint.py` |

### Phase 4 - Determinism & Replay
| Old Location | New Location |
|--------------|--------------|
| `logical_time.py` | `src/phase4_determinism/logical_time.py` |
| `prompt_versioning.py` | `src/phase4_determinism/prompt_versioning.py` |
| `deterministic_composition.py` | `src/phase4_determinism/deterministic_composition.py` |
| `llm_config.py` | `src/phase4_determinism/llm_config.py` |
| `replay_verification.py` | `src/phase4_determinism/replay_verification.py` |

### Documentation
| Old Location | New Location |
|--------------|--------------|
| `ONBOARDING.md` | `docs/ONBOARDING.md` |
| `IMPLEMENTATION_PLAN.md` | `docs/IMPLEMENTATION_PLAN.md` |
| `CHANGELOG.md` | `docs/CHANGELOG.md` |
| `PHASE_4_IMPLEMENTATION_SUMMARY.md` | `docs/PHASE_4_IMPLEMENTATION_SUMMARY.md` |
| `sandbox-architecture.instructions.md` | `docs/sandbox-architecture.instructions.md` |

### Configuration
| Old Location | New Location |
|--------------|--------------|
| `project.config.example.yml` | `config/project.config.example.yml` |
| `plugin.json` | `config/plugin.json` |

---

## Running Tests

Tests have been updated with correct imports. Run as before:

```bash
# Phase 4 tests
python tests/test_phase4.py

# Or if you have pytest installed
pytest tests/
```

---

## No Breaking Changes for End Users

**Skills, instructions, profiles, and starters** remain in their original locations:
- `skills/` — Agent skill definitions (unchanged)
- `instructions/` — Workflow instructions (unchanged)
- `profiles/` — Project templates (unchanged)
- `starters/` — Starter files (unchanged)
- `schemas/` — JSON schemas (unchanged)
- `policies/` — Rego policies (unchanged)

The `init.py` script and resolved output structure remain unchanged.

---

## Questions?

- See [ONBOARDING.md](ONBOARDING.md) for usage guide
- See [PHASE_4_IMPLEMENTATION_SUMMARY.md](PHASE_4_IMPLEMENTATION_SUMMARY.md) for architecture details
- Open an issue if you encounter import problems

---

**Summary**: Root directory cleaned up from 25+ files to 8 top-level items. All source code now in `src/` organized by phase. All documentation in `docs/`. All configuration in `config/`. Tests updated with correct imports.
