"""Mode 2: Orchestration — supported file-queue dispatcher.

The production implementation of ``mode-2-contract-v1`` promoted from the
frozen reference impl at
``command-centre/03-mode-orchestration/reference-impls/file-queue-dispatcher/``
per ADR 0008. Modules:

- dispatcher:  ported dispatch core (state machine, ghost-done verifier,
               tier-3 summary)
- discovery:   deterministic callable discovery + callable-v1 validation
- queue_file:  durable queue state (atomic snapshot, transition journal,
               crash-resume)
- returns:     return-tier validation (reuses phase1 SubagentReturnValidator)

Entry point: ``dispatch.py`` at the repo root (Mode 2 runtime; independent
of the Mode 1 build tool ``init.py``).
"""

from .discovery import (
    CallableViolation,
    DiscoveredCallable,
    discover_callables,
    parse_frontmatter,
)
from .dispatcher import (
    Callable_,
    Dispatcher,
    DispatchResult,
    InvocationError,
    WorkItem,
    registry_from_manifests,
    write_summary,
)
from .queue_file import (
    ALLOWED_TRANSITIONS,
    QueueStateError,
    QueueStore,
    TransitionError,
    read_pins,
)
from .returns import make_return_validator, validate_return

__version__ = "1.0.0"

CONTRACT_PIN = "mode-2-contract-v1"
PROTOCOL_PIN = "protocol-v1"

__all__ = [
    "ALLOWED_TRANSITIONS",
    "CONTRACT_PIN",
    "Callable_",
    "CallableViolation",
    "DiscoveredCallable",
    "DispatchResult",
    "Dispatcher",
    "InvocationError",
    "PROTOCOL_PIN",
    "QueueStateError",
    "QueueStore",
    "TransitionError",
    "WorkItem",
    "discover_callables",
    "make_return_validator",
    "parse_frontmatter",
    "read_pins",
    "registry_from_manifests",
    "validate_return",
    "write_summary",
]
