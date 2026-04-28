#!/usr/bin/env python3
"""
init.py — Token substitution for agent-homebase skills library.

Usage:
    python3 init.py --config project.config.yml
    python3 init.py --config profiles/react-web-app.config.yml
    python3 init.py --quick-setup                 # Interactive setup for key values

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

# =============================================================================
# SECURITY VALIDATION — Phase 0 Enhancement
# =============================================================================

class SecurityValidator:
    """Validates config values for security vulnerabilities."""
    
    # Whitelist of allowed command prefixes
    ALLOWED_COMMANDS = {
        # Node/JavaScript
        'npm', 'pnpm', 'yarn', 'node', 'npx',
        # Python
        'python', 'python3', 'pytest', 'pip', 'uv',
        # Rust
        'cargo',
        # Go
        'go',
        # .NET
        'dotnet',
        # Java
        'mvn', 'gradle',
        # Build tools
        'make', 'cmake',
        # Test runners
        'jest', 'vitest', 'mocha',
        # Linters/formatters
        'eslint', 'prettier', 'ruff', 'black',
        # Type checkers
        'tsc', 'mypy', 'pyright',
        # Version control
        'git', 'gh',
        # Time command (safe)
        'date', 'powershell -c "Get-Date"',
    }
    
    # Dangerous command patterns
    DANGEROUS_PATTERNS = [
        r';\s*rm\s',           # Command chaining with rm
        r'\|\s*rm\s',          # Piping to rm
        r'&&\s*rm\s',          # Command chaining
        r'`.*`',               # Command substitution
        r'\$\(',               # Command substitution
        r'>\s*/dev',           # Writing to /dev
        r'curl.*\|.*sh',       # Curl pipe to shell
        r'wget.*\|.*sh',       # Wget pipe to shell
    ]
    
    # Secret patterns to detect
    SECRET_PATTERNS = [
        (r'api[_-]?key\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', 'API key'),
        (r'secret\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', 'Secret'),
        (r'password\s*[:=]\s*["\']?[a-zA-Z0-9]{8,}', 'Password'),
        (r'token\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', 'Token'),
        (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI API key'),
        (r'ghp_[a-zA-Z0-9]{36,}', 'GitHub personal access token'),
    ]
    
    @classmethod
    def validate_command(cls, command: str, key: str) -> list[str]:
        """Validate a command for security issues. Returns list of errors."""
        errors = []
        
        if not command or command.strip() == '':
            return errors
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                errors.append(
                    f"CRITICAL: Dangerous pattern detected in '{key}': {pattern}\n"
                    f"  Command: {command}"
                )
        
        # Check if command starts with allowed prefix
        command_lower = command.strip().lower()
        is_allowed = False
        for allowed in cls.ALLOWED_COMMANDS:
            if command_lower.startswith(allowed.lower()):
                is_allowed = True
                break
        
        if not is_allowed and not errors:  # Only warn if not already flagged as dangerous
            errors.append(
                f"WARNING: Command '{key}' not in whitelist: {command}\n"
                f"  Allowed commands: {', '.join(sorted(cls.ALLOWED_COMMANDS))}"
            )
        
        return errors
    
    @classmethod
    def validate_path(cls, path: str, key: str) -> list[str]:
        """Validate a path for traversal attacks. Returns list of errors."""
        errors = []
        
        if not path or path.strip() == '':
            return errors
        
        # Check for path traversal
        if '..' in path:
            errors.append(
                f"CRITICAL: Path traversal detected in '{key}': {path}\n"
                f"  Paths must not contain '..'"
            )
        
        # Check for absolute paths (should be relative to project root)
        if path.startswith('/') or (len(path) > 2 and path[1] == ':'):
            errors.append(
                f"WARNING: Absolute path in '{key}': {path}\n"
                f"  Consider using relative paths from project root"
            )
        
        return errors
    
    @classmethod
    def detect_secrets(cls, text: str) -> list[tuple[str, str]]:
        """Detect potential secrets in text. Returns list of (pattern_desc, match)."""
        secrets = []
        for pattern, desc in cls.SECRET_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                secrets.append((desc, match.group(0)))
        return secrets
    
    @classmethod
    def validate_config(cls, config: dict) -> tuple[list[str], list[str]]:
        """
        Validate entire config for security issues.
        Returns (errors, warnings) where errors should block execution.
        """
        errors = []
        warnings = []
        
        # Validate all command tokens
        if 'commands' in config:
            for cmd_key, cmd_value in config['commands'].items():
                if isinstance(cmd_value, str):
                    issues = cls.validate_command(cmd_value, f'commands.{cmd_key}')
                    for issue in issues:
                        if 'CRITICAL' in issue:
                            errors.append(issue)
                        else:
                            warnings.append(issue)
        
        # Validate all path tokens
        if 'paths' in config:
            for path_key, path_value in config['paths'].items():
                if isinstance(path_value, str):
                    issues = cls.validate_path(path_value, f'paths.{path_key}')
                    for issue in issues:
                        if 'CRITICAL' in issue:
                            errors.append(issue)
                        else:
                            warnings.append(issue)
        
        # Detect secrets in config values
        config_str = yaml.dump(config)
        secrets = cls.detect_secrets(config_str)
        if secrets:
            errors.append(
                f"CRITICAL: Potential secrets detected in config:\n" +
                '\n'.join(f"  - {desc}: {match[:20]}..." for desc, match in secrets) +
                "\n  NEVER store secrets in config files. Use environment variables or secret managers."
            )
        
        return errors, warnings


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


def quick_setup(config_path: Path) -> None:
    """Interactive setup for key project config values."""
    print("\n" + "=" * 60)
    print("  agent-homebase Quick Setup")
    print("=" * 60 + "\n")
    
    # Check if config exists
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        print("Creating from example...")
        example_path = Path("config/project.config.example.yml")
        if not example_path.exists():
            print(f"ERROR: Example config not found at {example_path}")
            sys.exit(1)
        shutil.copy(example_path, config_path)
        print(f"✓ Created {config_path}\n")
    
    # Load existing config
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Interactive prompts for key values
    print("Answer the following to customize your project config.\n")
    print("Press Enter to keep current value shown in [brackets].\n")
    
    # Project name
    current_name = config.get('project', {}).get('name', 'My Project')
    new_name = input(f"Project name [{current_name}]: ").strip()
    if new_name:
        config.setdefault('project', {})['name'] = new_name
    
    # GitHub repo
    current_repo = config.get('git', {}).get('repo', 'owner/repo')
    new_repo = input(f"GitHub repository (owner/repo) [{current_repo}]: ").strip()
    if new_repo:
        config.setdefault('git', {})['repo'] = new_repo
    
    # Namespace
    current_ns = config.get('project', {}).get('namespace', '@org')
    new_ns = input(f"Monorepo namespace [{current_ns}]: ").strip()
    if new_ns:
        config.setdefault('project', {})['namespace'] = new_ns
    
    # Main branch
    current_branch = config.get('git', {}).get('main_branch', 'main')
    new_branch = input(f"Main branch [{current_branch}]: ").strip()
    if new_branch:
        config.setdefault('git', {})['main_branch'] = new_branch
    
    # Write updated config
    print()
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✓ Updated {config_path}")
    print()
    print("Summary of changes:")
    print(f"  project.name:    {config.get('project', {}).get('name', 'My Project')}")
    print(f"  git.repo:        {config.get('git', {}).get('repo', 'owner/repo')}")
    print(f"  project.namespace: {config.get('project', {}).get('namespace', '@org')}")
    print(f"  git.main_branch: {config.get('git', {}).get('main_branch', 'main')}")
    print()
    print("Next: Run `python3 init.py` to generate resolved files.")


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
    parser.add_argument(
        "--quick-setup",
        action="store_true",
        help="Interactive setup for key project values (name, repo, namespace)"
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    
    # Handle quick setup mode
    if args.quick_setup:
        quick_setup(config_path)
        return

    if not config_path.exists():
        print(f"ERROR: config file not found: {config_path}")
        print("  Copy project.config.example.yml to project.config.yml and fill it in.")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # =============================================================================
    # Security Validation — Phase 0
    # =============================================================================
    print("Running security validation...")
    sec_errors, sec_warnings = SecurityValidator.validate_config(config)
    
    if sec_warnings:
        print("\n⚠️  SECURITY WARNINGS:")
        for warning in sec_warnings:
            print(f"\n{warning}")
        print()
    
    if sec_errors:
        print("\n🚨 SECURITY ERRORS (blocking):")
        for error in sec_errors:
            print(f"\n{error}")
        print("\n❌ Config validation FAILED due to security errors.")
        print("   Fix the issues above and try again.")
        sys.exit(1)
    
    print("✓ Security validation passed")
    print()

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
