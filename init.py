#!/usr/bin/env python3
"""
init.py — Token substitution for agent-homebase skills library.

Usage:
    python3 init.py --config project.config.yml
    python3 init.py --config profiles/react-web-app.config.yml

Output:
    resolved/skills/        — copy to .github/agents/ (or your skills directory)
    resolved/instructions/  — copy to .github/instructions/

Requires: PyYAML
    pip install pyyaml
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


def flatten(d: dict, prefix: str = "") -> dict:
    """Flatten a nested dict to dot-notation keys.
    e.g. {"paths": {"ledger": "docs/..."}} → {"paths.ledger": "docs/..."}
    """
    result = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.update(flatten(v, key))
        else:
            result[key] = str(v) if v is not None else ""
    return result


def substitute(text: str, tokens: dict) -> str:
    """Replace {{token}} occurrences with config values.
    Unrecognised tokens are left in place and printed as warnings.
    """
    warnings = []

    def replace(match):
        key = match.group(1).strip()
        if key not in tokens:
            warnings.append(key)
            return match.group(0)   # leave unreplaced — visible in output
        return tokens[key]

    result = re.sub(r"\{\{([^}]+)\}\}", replace, text)

    for w in warnings:
        print(f"  ⚠  no config value for {{{{ {w} }}}}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Resolve {{tokens}} in skills and instructions using a project config."
    )
    parser.add_argument(
        "--config",
        default="project.config.yml",
        help="Path to project config YAML (default: project.config.yml)"
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"ERROR: config file not found: {config_path}")
        print("  Copy project.config.example.yml to project.config.yml and fill it in.")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    tokens = flatten(config)
    print(f"Loaded {len(tokens)} config tokens from {config_path}")

    output = Path("resolved")
    output.mkdir(exist_ok=True)   # overwrite in-place — avoids permission issues on re-runs

    resolved_count = 0
    copied_count = 0
    warning_count = 0

    # --- Skills (SKILL.md files) ---
    skills_src = Path("skills")
    if skills_src.exists():
        for skill_md in sorted(skills_src.rglob("SKILL.md")):
            dest = output / skill_md
            dest.parent.mkdir(parents=True, exist_ok=True)
            original = skill_md.read_text(encoding="utf-8")
            resolved = substitute(original, tokens)
            dest.write_text(resolved, encoding="utf-8")
            unresolved = re.findall(r"\{\{[^}]+\}\}", resolved)
            if unresolved:
                print(f"  resolved (with warnings): {dest}")
                warning_count += len(unresolved)
            else:
                print(f"  resolved: {dest}")
            resolved_count += 1

    # --- Configurable instructions ---
    configurable_src = Path("instructions/configurable")
    if configurable_src.exists():
        for instr in sorted(configurable_src.glob("*.md")):
            dest = output / "instructions" / instr.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            original = instr.read_text(encoding="utf-8")
            resolved = substitute(original, tokens)
            dest.write_text(resolved, encoding="utf-8")
            unresolved = re.findall(r"\{\{[^}]+\}\}", resolved)
            if unresolved:
                print(f"  resolved (with warnings): {dest}")
                warning_count += len(unresolved)
            else:
                print(f"  resolved: {dest}")
            resolved_count += 1

    # --- Generic instructions (copy as-is) ---
    generic_src = Path("instructions/generic")
    if generic_src.exists():
        for instr in sorted(generic_src.glob("*.md")):
            dest = output / "instructions" / instr.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(instr, dest)
            print(f"  copied:   {dest}")
            copied_count += 1

    # --- Final unresolved token scan ---
    print()
    all_unresolved = []
    for md in sorted(output.rglob("*.md")):
        matches = re.findall(r"\{\{[^}]+\}\}", md.read_text(encoding="utf-8"))
        if matches:
            all_unresolved.append((md, matches))

    if all_unresolved:
        print(f"⚠  {len(all_unresolved)} file(s) have unresolved tokens — check project.config.yml:")
        for path, found in all_unresolved:
            print(f"   {path}: {found}")
        print()
    else:
        print("✓ All tokens resolved — no unresolved {{placeholders}} in output.")
        print()

    print(f"Summary: {resolved_count} resolved, {copied_count} copied, {warning_count} token warnings")
    print()
    print("Next steps:")
    print("  cp -r resolved/skills/*        .github/agents/")
    print("  cp -r resolved/instructions/*  .github/instructions/")
    print("  Copy starters/* to your project docs if starting fresh.")


if __name__ == "__main__":
    main()
