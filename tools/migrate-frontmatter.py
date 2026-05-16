"""One-shot substrate migration to protocol-v1 frontmatter.

Walks ``skills/``, ``instructions/``, ``agents/`` and rewrites each file's
frontmatter so it satisfies ``schemas/frontmatter-v1.schema.json`` and
(for skills) ``schemas/callable-v1.schema.json``.

Idempotent: re-running on already-migrated files produces no diff.
"""

from __future__ import annotations

import sys
from pathlib import Path
from collections import OrderedDict

import yaml


# Make YAML emit OrderedDict in insertion order.
def _ordered_dict_representer(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


yaml.add_representer(OrderedDict, _ordered_dict_representer, Dumper=yaml.SafeDumper)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    fm_text = text[3:end].strip()
    body = text[end + 3:].lstrip("\n")
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


def render(fm: OrderedDict, body: str) -> str:
    dumped = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=1000)
    return "---\n" + dumped.rstrip() + "\n---\n\n" + body


def migrate_skill(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if not fm:
        print(f"  SKIP (no fm): {path}")
        return

    name = fm.get("name", path.stem.replace(".skill", ""))
    description = fm.get("description", "")

    # Migrate scope → applies_to.
    applies_to = fm.pop("applies_to", None) or fm.pop("scope", None) or "**"

    new = OrderedDict()
    new["id"] = f"skill.{name}"
    new["kind"] = "skill"
    new["version"] = fm.pop("version", "1.0.0")
    new["applies_to"] = applies_to
    new["name"] = name
    if description:
        new["description"] = description
    # Preserve original optional fields.
    for k in ("when_to_use", "user-invocable", "lifecycle", "tags", "owner", "depends_on", "runtime"):
        if k in fm:
            new[k] = fm.pop(k)
    # Callable manifest — minimum acceptable shape (idempotent if present).
    new["inputs"] = fm.pop("inputs", None) or {
        "type": "object",
        "required": ["task"],
        "properties": {
            "task": {"type": "string", "description": "What the skill should do."}
        },
    }
    new["outputs"] = fm.pop("outputs", None) or [{"return_tier": 2}]
    new["verifier"] = fm.pop("verifier", None) if "verifier" in fm else None
    if "runtime_hints" in fm:
        new["runtime_hints"] = fm.pop("runtime_hints")
    # Preserve `agent:` metadata used by init.py for VS Code wrappers.
    if "agent" in fm:
        new["agent"] = fm.pop("agent")
    # Sweep up any remaining unknown fields verbatim.
    for k, v in fm.items():
        new[k] = v

    path.write_text(render(new, body), encoding="utf-8")
    print(f"  migrated skill: {path}")


def migrate_instruction(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    # Some instructions had no frontmatter at all.
    fm = fm or {}
    name = path.name.replace(".instructions.md", "")
    description = fm.pop("description", "") or f"{name} instruction"

    applies_to = fm.pop("applies_to", None) or fm.pop("scope", None) or "**"

    new = OrderedDict()
    new["id"] = f"instruction.{name}"
    new["kind"] = "instruction"
    new["version"] = fm.pop("version", "1.0.0")
    new["applies_to"] = applies_to
    new["description"] = description
    for k, v in fm.items():
        new[k] = v

    path.write_text(render(new, body), encoding="utf-8")
    print(f"  migrated instruction: {path}")


def migrate_agent(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    name = path.name.replace(".body.md", "")
    fm = fm or {}

    new = OrderedDict()
    new["id"] = fm.pop("id", f"agent.{name}")
    new["kind"] = "agent"
    new["version"] = fm.pop("version", "1.0.0")
    new["applies_to"] = fm.pop("applies_to", None) or fm.pop("scope", None) or "**"
    if "description" in fm:
        new["description"] = fm.pop("description")
    for k, v in fm.items():
        new[k] = v

    # When the original file had no frontmatter at all, `body` is the entire
    # file content. Preserve it verbatim under the new fences.
    path.write_text(render(new, body if fm or body else text), encoding="utf-8")
    print(f"  migrated agent: {path}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    for p in sorted(root.glob("skills/*/*.skill.md")):
        migrate_skill(p)
    for p in sorted(root.glob("instructions/**/*.instructions.md")):
        migrate_instruction(p)
    for p in sorted(root.glob("agents/*.body.md")):
        migrate_agent(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
