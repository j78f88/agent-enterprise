#!/usr/bin/env python3
"""choreography.py — Mode 3 (choreography) coordinator CLI.

A small, supported entry point over the Mode 3 registry reference coordinator.
It makes Mode 3 discoverable from the repo root, analogous to ``dispatch.py``
for Mode 2, while keeping the contract/reference implementation as the source
of truth.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
_COORD_DIR = (
    _REPO_ROOT
    / "command-centre"
    / "04-mode-choreography"
    / "reference-impls"
    / "registry-coordinator"
)
if str(_COORD_DIR) not in sys.path:
    sys.path.insert(0, str(_COORD_DIR))

from coordinator import Coordinator  # noqa: E402

DEFAULT_REGISTRY = _COORD_DIR / "fixtures" / "registry.yml"
DEFAULT_CURRENT_VERSION = "2.0.0"
CONTRACT = "mode-3-contract-v1"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_coordinator(args: argparse.Namespace) -> Coordinator:
    registry = Path(args.registry)
    if not registry.exists():
        fail(f"registry not found: {registry}")
    try:
        return Coordinator(registry_path=registry, current_substrate_version=args.current_version)
    except Exception as exc:  # schema/parse errors should be clear and non-zero
        fail(str(exc))


def cmd_validate_registry(args: argparse.Namespace) -> int:
    coord = load_coordinator(args)
    print(
        "OK: registry valid "
        f"contract={CONTRACT} projects={len(coord.registry['projects'])} "
        f"registry={Path(args.registry)}"
    )
    return 0


def cmd_drift(args: argparse.Namespace) -> int:
    coord = load_coordinator(args)
    payload = {
        "contract": CONTRACT,
        "registry": str(Path(args.registry)),
        "current_version": args.current_version,
        "drift": [d.__dict__ for d in coord.detect_drift()],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_impact(args: argparse.Namespace) -> int:
    coord = load_coordinator(args)
    payload = {
        "contract": CONTRACT,
        "registry": str(Path(args.registry)),
        "contract_tag": args.contract_tag,
        "affected_projects": coord.impact_of_contract_bump(args.contract_tag),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_meta_agents(args: argparse.Namespace) -> int:
    coord = load_coordinator(args)
    payload = {
        "contract": CONTRACT,
        "registry": str(Path(args.registry)),
        "meta_agents": {name: str(path) for name, path in coord.meta_agents().items()},
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_harvest(args: argparse.Namespace) -> int:
    coord = load_coordinator(args)
    audit_path = coord.harvest(Path(args.out_dir))
    payload = {
        "contract": CONTRACT,
        "registry": str(Path(args.registry)),
        "audit_path": str(audit_path),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY),
        help=f"Registry YAML path (default: {DEFAULT_REGISTRY}).",
    )
    parser.add_argument(
        "--current-version",
        default=DEFAULT_CURRENT_VERSION,
        help=f"Current substrate version for drift checks (default: {DEFAULT_CURRENT_VERSION}).",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="choreography.py",
        description="Mode 3 (choreography) registry coordinator CLI.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate-registry", help="Validate registry + project entries.")
    add_common(p)
    p.set_defaults(func=cmd_validate_registry)

    p = sub.add_parser("drift", help="Emit substrate-version drift report as JSON.")
    add_common(p)
    p.set_defaults(func=cmd_drift)

    p = sub.add_parser("impact", help="Report projects affected by a contract pin/tag.")
    add_common(p)
    p.add_argument("contract_tag", help="Contract tag to inspect, e.g. mode-2-contract-v1.")
    p.set_defaults(func=cmd_impact)

    p = sub.add_parser("meta-agents", help="List required Mode 3 meta-agent files.")
    add_common(p)
    p.set_defaults(func=cmd_meta_agents)

    p = sub.add_parser("harvest", help="Run a harvest cycle and write an audit record.")
    add_common(p)
    p.add_argument("--out-dir", default="audit", help="Audit output directory (default: audit).")
    p.set_defaults(func=cmd_harvest)

    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
