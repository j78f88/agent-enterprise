#!/usr/bin/env python3
"""
init.py — Token substitution for agent-enterprise skills library.

Usage:
    python init.py --config project.config.yml
    python init.py --config profiles/react-web-app.config.yml
    python init.py --quick-setup                 # Interactive setup for key values

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

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema>=4.0")
    sys.exit(1)

import json

# Cache loaded schemas for the duration of the run (determinism + speed).
_SCHEMA_CACHE: dict[str, dict] = {}


def _load_schema(name: str) -> dict:
    """Load a JSON schema from ``schemas/`` once and cache it."""
    if name not in _SCHEMA_CACHE:
        path = Path(__file__).parent / "schemas" / name
        with open(path, encoding="utf-8") as f:
            _SCHEMA_CACHE[name] = json.load(f)
    return _SCHEMA_CACHE[name]


def validate_frontmatter(text: str, kind: str, path: Path) -> list[str]:
    """Validate the YAML frontmatter of a substrate file against frontmatter-v1.

    Args:
        text: full file contents (with or without frontmatter fences).
        kind: expected ``kind`` value (``skill``, ``instruction``, ``agent``).
              If the frontmatter omits ``kind``, this value is asserted.
        path: filesystem path used in error messages.

    Returns:
        A list of human-readable error strings. Empty list means valid.
        For skills, also validates the callable manifest portion against
        ``callable-v1.schema.json``.
    """
    errors: list[str] = []

    if not text.lstrip().startswith("---"):
        errors.append(f"{path}: missing YAML frontmatter (no leading '---')")
        return errors

    fm, _ = parse_frontmatter(text)
    if not fm:
        errors.append(f"{path}: frontmatter block is empty or unparseable")
        return errors

    # Accept ``scope:`` as a read-side alias for ``applies_to`` (ADR-0012).
    if "applies_to" not in fm and "scope" in fm:
        fm = dict(fm)
        fm["applies_to"] = fm["scope"]

    # Frontmatter-v1 validation.
    try:
        jsonschema.validate(instance=fm, schema=_load_schema("frontmatter-v1.schema.json"))
    except jsonschema.ValidationError as e:
        loc = "/".join(str(p) for p in e.absolute_path) or "<root>"
        errors.append(f"{path}: frontmatter-v1 violation at {loc}: {e.message}")

    # Cross-check kind matches caller expectation.
    declared_kind = fm.get("kind")
    if declared_kind and kind and declared_kind != kind:
        errors.append(
            f"{path}: kind mismatch — declared '{declared_kind}', expected '{kind}'"
        )

    # Skills additionally must satisfy the callable-v1 manifest contract.
    if (declared_kind or kind) == "skill":
        try:
            jsonschema.validate(instance=fm, schema=_load_schema("callable-v1.schema.json"))
        except jsonschema.ValidationError as e:
            loc = "/".join(str(p) for p in e.absolute_path) or "<root>"
            errors.append(f"{path}: callable-v1 violation at {loc}: {e.message}")

    return errors

# =============================================================================
# SECURITY VALIDATION — Phase 0 Enhancement
# =============================================================================

VALID_EDITOR_TARGETS = {'vscode', 'claude-code', 'cursor', 'codex', 'both', 'all'}


class SecurityValidator:
    """Validates config values for security vulnerabilities."""
    
    # Whitelist of allowed command prefixes
    ALLOWED_COMMANDS = {
        # Node/JavaScript
        'npm', 'pnpm', 'yarn', 'node', 'npx', 'bun', 'bunx',
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
        # Security scanning tools
        'syft', 'gitleaks', 'trivy', 'checkov', 'bandit', 'pip-licenses', 'semgrep',
        # Time command (safe)
        'date', 'powershell',
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
        if Path(path).is_absolute():
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
        
        # Validate editor target
        editor_target = config.get('editor', {}).get('target', 'both')
        if editor_target not in VALID_EDITOR_TARGETS:
            errors.append(
                f"CRITICAL: Invalid editor.target '{editor_target}'.\n"
                f"  Valid values: {', '.join(sorted(VALID_EDITOR_TARGETS))}"
            )
        
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
    print("  agent-enterprise Quick Setup")
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
    print("Next: Run `python init.py` to generate resolved files.")


# =============================================================================
# AGENT GENERATION — Dual-Platform Support
# =============================================================================

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file.
    Returns (frontmatter_dict, body_text).
    """
    if not text.startswith('---'):
        return {}, text
    end = text.find('---', 3)
    if end == -1:
        return {}, text
    fm_text = text[3:end].strip()
    body = text[end + 3:].strip()
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


def _scope_as_string(scope) -> str:
    """Render a scope value as the comma-separated string VS Code / Cursor expect."""
    if isinstance(scope, list):
        return ", ".join(str(s) for s in scope)
    return str(scope)


def _scope_as_list(scope) -> list[str]:
    if isinstance(scope, list):
        return [str(s) for s in scope]
    return [str(scope)]


def transform_frontmatter_for_target(fm: dict, target: str) -> dict:
    """Rewrite a path-scope field into the platform-native scoping field.

    Reads ``applies_to`` (canonical, frontmatter-v1) or ``scope`` (legacy
    alias, sunsets at frontmatter-v2 per ADR-0012). If both are present,
    ``applies_to`` wins.

    - vscode / both: emit ``applyTo`` (comma-joined string).
    - claude-code:   emit ``paths`` (list).
    - cursor:        leave ``scope`` for the .mdc emitter.
    - codex:         no rewrite — AGENTS.md has no scoping frontmatter.
    - all:           emit both ``applyTo`` and ``paths``.

    If neither field is present, the frontmatter is returned unchanged.
    Other fields are preserved.
    """
    out = dict(fm or {})
    scope = out.get('applies_to', out.get('scope'))
    if scope is None:
        return out
    if target in ('vscode', 'both'):
        out['applyTo'] = _scope_as_string(scope)
    elif target == 'claude-code':
        out['paths'] = _scope_as_list(scope)
    elif target == 'all':
        out['applyTo'] = _scope_as_string(scope)
        out['paths'] = _scope_as_list(scope)
    # cursor: handled by emit_cursor_mdc, no rewrite here
    # codex: no rewrite — AGENTS.md carries no per-file scoping frontmatter
    return out


def _render_frontmatter(fm: dict) -> str:
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip() + "\n---\n"


def emit_cursor_mdc(name: str, fm: dict, body: str, out_dir: Path) -> Path:
    """Write a single ``.cursor/rules/<name>.mdc`` file.

    Cursor expects frontmatter with ``description``, ``globs``, and
    ``alwaysApply``. If the source frontmatter has no ``scope`` field, the
    rule is treated as always-applied.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    scope = fm.get('applies_to', fm.get('scope'))
    description = fm.get('description', '').strip() or name
    if scope is None:
        mdc_fm = {
            'description': description,
            'globs': '',
            'alwaysApply': True,
        }
    else:
        mdc_fm = {
            'description': description,
            'globs': _scope_as_string(scope),
            'alwaysApply': False,
        }
    target = out_dir / f"{name}.mdc"
    target.write_text(_render_frontmatter(mdc_fm) + "\n" + body.lstrip() + ("" if body.endswith("\n") else "\n"), encoding="utf-8")
    return target


def extract_agent_body(name: str, fm: dict, body: str) -> str:
    """Extract a lean agent body from a SKILL.md.

    Includes: identity paragraph, core constraints.
    References: skill folder for detailed procedures.
    Drops: Subagent Mode, Session Lifecycle, Documents You Own, Shared Rules (verbose).
    Target: ≤100 lines.
    """
    lines = body.split('\n')

    # Extract the identity section (from start until first ## heading)
    identity_lines = []
    constraints_lines = []
    current_section = 'identity'
    skip_sections = {
        'subagent mode', 'context continuity', 'session-end menu',
        'health check', 'documents you own', 'shared rules',
        'interaction style', 'session start', 'available agents',
        'retrospective instrumentation', 'execution mode',
        'retro.md forecast seeding', 'carry-over escalation gate',
        'handoff manifest', 'handoff rejections', 'slug convention',
        'draft plan template', 'non-goals ownership',
    }
    keep_sections = {
        'core constraints', 'output format', 'finding format',
        'quality gates', 'gate definitions', 'severity levels',
        'report structure', 'constraints',
    }

    in_skip = False
    in_keep = False
    skip_depth = 0

    for line in lines:
        # Detect ## headings
        if line.startswith('## '):
            heading = line.lstrip('#').strip().lower()
            if any(s in heading for s in skip_sections):
                in_skip = True
                in_keep = False
                skip_depth = line.count('#', 0, line.index(' '))
                continue
            elif any(s in heading for s in keep_sections):
                in_skip = False
                in_keep = True
                constraints_lines.append(line)
                continue
            else:
                in_skip = False
                in_keep = False
                continue
        elif line.startswith('### ') and in_skip:
            continue

        if in_skip:
            continue

        if in_keep:
            constraints_lines.append(line)
        elif current_section == 'identity':
            identity_lines.append(line)
            # End identity at first ## heading
            if line.startswith('## '):
                current_section = 'past_identity'

    # Trim identity to first meaningful paragraph
    identity = []
    found_heading = False
    for line in identity_lines:
        if line.startswith('# '):
            found_heading = True
            continue
        if found_heading:
            identity.append(line)
        if found_heading and line == '' and len(identity) > 2:
            break

    identity_text = '\n'.join(identity).strip()
    constraints_text = '\n'.join(constraints_lines).strip()

    # Build the agent body
    parts = [f"# {name.replace('-', ' ').title()}\n"]
    if identity_text:
        parts.append(identity_text)
    parts.append('')
    if constraints_text:
        parts.append(constraints_text)
        parts.append('')
    parts.append(f'For detailed workflow procedures, see `skills/{name}/SKILL.md`.')

    return '\n'.join(parts)


def generate_agent_md(name: str, fm: dict, agent_body: str) -> str:
    """Generate a .agent.md file from skill frontmatter + hand-crafted body."""
    agent_meta = fm.get('agent', {})
    tools = agent_meta.get('tools', [])
    agents_list = agent_meta.get('agents', [])
    model = agent_meta.get('model')
    handoffs = agent_meta.get('handoffs', [])

    # Build description — concatenate description + when_to_use (1024 char limit)
    description = fm.get('description', '')
    when_to_use = fm.get('when_to_use', '')
    if when_to_use:
        full_desc = f"{description} Use when: {when_to_use}"
    else:
        full_desc = description
    if len(full_desc) > 1024:
        full_desc = full_desc[:1021] + '...'

    # Build frontmatter. json.dumps produces a double-quoted scalar whose
    # escapes (\" \\ \uXXXX) are all valid YAML — safe even when the
    # description itself contains double quotes.
    fm_lines = ['---']
    fm_lines.append(f'name: {name}')
    fm_lines.append(f'description: {json.dumps(full_desc, ensure_ascii=False)}')
    if tools:
        fm_lines.append(f'tools: [{", ".join(tools)}]')
    if agents_list:
        fm_lines.append(f'agents: [{", ".join(agents_list)}]')
    if model:
        fm_lines.append(f'model: {model}')
    if handoffs:
        fm_lines.append(f'handoffs: [{", ".join(handoffs)}]')
    fm_lines.append('---')

    return '\n'.join(fm_lines) + '\n\n' + agent_body + '\n'


def generate_claude_subagent_md(name: str, fm: dict, body: str) -> str:
    """Render a Claude Code native subagent file from a resolved agent wrapper.

    Claude Code discovers subagents as <claude_agents>/<name>.md with YAML
    frontmatter carrying `name` and `description`. The wrapper's `tools` list
    uses VS Code tool identifiers (read/search/edit/...) which have no clean
    mapping onto Claude Code tool names, so `tools` is deliberately omitted —
    Claude Code then gives the subagent its default (full) tool set.
    """
    description = fm.get('description', '')
    fm_lines = ['---']
    fm_lines.append(f"name: {fm.get('name', name)}")
    # json.dumps yields a YAML-valid double-quoted scalar even when the
    # description contains double quotes (see generate_agent_md).
    fm_lines.append(f'description: {json.dumps(description, ensure_ascii=False)}')
    fm_lines.append('---')
    return '\n'.join(fm_lines) + '\n\n' + body.strip() + '\n'


def generate_agents(output: Path, tokens: dict) -> list[str]:
    """Generate .agent.md wrappers using hybrid approach.

    Frontmatter: generated from skill agent: metadata (single source of truth).
    Body: read from agents/<name>.body.md (hand-crafted for quality).
    Fallback: if no body file exists, auto-extract from SKILL.md with warning.

    Returns list of skill names that had agents generated.
    """
    resolved_skills = output / "skills"
    agents_out = output / "agents"
    agents_out.mkdir(parents=True, exist_ok=True)
    bodies_src = Path("agents")

    generated = []

    if not resolved_skills.exists():
        return generated

    for skill_dir in sorted(resolved_skills.iterdir()):
        if not skill_dir.is_dir():
            continue
        # Find the skill file — resolved as SKILL.md, or {name}.skill.md
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            candidates = list(skill_dir.glob("*.skill.md"))
            skill_md = candidates[0] if candidates else None
        if not skill_md or not skill_md.exists():
            continue

        text = skill_md.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)

        # Skip skills without agent metadata
        if 'agent' not in fm:
            continue

        name = fm.get('name', skill_dir.name)

        # Hybrid: prefer hand-crafted body, fall back to extraction
        body_file = bodies_src / f"{name}.body.md"
        if body_file.exists():
            raw = body_file.read_text(encoding="utf-8")
            # Strip the body file's own frontmatter (added at protocol-v1) so
            # only the prose body is rendered into the agent wrapper.
            _body_fm, body_text = parse_frontmatter(raw)
            agent_body = body_text.strip()
        else:
            print(f"  ⚠  no body file for {name} — using auto-extraction (agents/{name}.body.md missing)")
            agent_body = extract_agent_body(name, fm, body)

        agent_content = generate_agent_md(name, fm, agent_body)
        agent_content = substitute(agent_content, tokens)

        dest = agents_out / f"{name}.agent.md"
        dest.write_text(agent_content, encoding="utf-8")
        print(f"  generated agent: {dest}")
        generated.append(name)

    return generated


def suppress_skill_invocability(output: Path, agent_names: list[str]) -> int:
    """Set user-invocable: false on resolved skills that have agent wrappers.

    This prevents duplicate discovery — users see @agent, not /skill.
    Source skills/ are never modified.
    Returns count of skills updated.
    """
    count = 0
    resolved_skills = output / "skills"

    for name in agent_names:
        # Find the skill file — resolved as SKILL.md, or {name}.skill.md
        skill_md = resolved_skills / name / "SKILL.md"
        if not skill_md.exists():
            candidates = list((resolved_skills / name).glob("*.skill.md"))
            skill_md = candidates[0] if candidates else skill_md
        if not skill_md.exists():
            continue

        text = skill_md.read_text(encoding="utf-8")

        # Replace user-invocable: true with false in frontmatter
        if 'user-invocable: true' in text:
            text = text.replace('user-invocable: true', 'user-invocable: false', 1)
            skill_md.write_text(text, encoding="utf-8")
            print(f"  suppressed: {skill_md} (user-invocable: false)")
            count += 1

    return count


# =============================================================================
# Token detection helpers
# =============================================================================
#
# A token is a {{name}} pair init.py is expected to resolve from config.
# Tokens resolve everywhere — in prose AND inside Markdown inline code spans
# (backtick-delimited). Two kinds of token-shaped strings are NOT init.py
# substitution sites and must be left alone:
#
#   1. GitHub Actions syntax — a literal '$' before '{{'. Skill and
#      instruction docs frequently recommend '${{ secrets.X }}' patterns
#      for workflow files.
#   2. Escaped literals — a single backslash before '{{' (i.e. '\{{name}}').
#      Authors use this when discussing the template system itself and want
#      the token to survive verbatim. The backslash is stripped on output
#      and the token is neither substituted nor flagged.
#
# `_TOKEN_RE` uses a negative lookbehind for '$' (rejects GitHub Actions
# syntax) and an optional leading-backslash capture group (the escape).
#
# Escape handling is two-phase. `substitute()` PRESERVES the '\{{...}}'
# marker (it is neither resolved nor flagged) so that the unresolved-token
# scans — which run on already-substituted output — can tell an intentional
# literal apart from a genuinely-unresolved token. The backslash is removed
# only at the very end of the build by `strip_escapes()`, after every scan
# has run, leaving a clean '{{...}}' literal in the deployed files.
#
# Authoring convention for brace literals in deployable docs: only the
# no-dot form (e.g. '\{{tokens}}') may be used — after strip_escapes() it is
# still distinguishable from a real {{namespace.key}} leak. Dotted token
# names in prose must be written without braces (e.g. `paths.claude_commands`).

_TOKEN_RE = re.compile(r"(?<!\$)(\\?)\{\{([^}]+)\}\}")

# Matches an escaped literal '\{{...}}' for the final backslash-stripping pass.
_ESCAPE_RE = re.compile(r"\\(\{\{[^}]+\}\})")


def strip_escapes(text: str) -> str:
    """Remove the authoring backslash from escaped literals.

    Turns '\\{{token}}' into '{{token}}'. Run as the final transformation of
    the build, after all unresolved-token scans, so that intentional literals
    appear verbatim in the deployed files without tripping the scans.
    """
    return _ESCAPE_RE.sub(r"\1", text)


def find_unresolved_tokens(text: str) -> list:
    """Return the list of {{token}} matches that should be flagged.

    Tokens are flagged whether they appear in prose or inside a backticked
    inline code span. Two cases are NOT flagged:
      - GitHub-Actions-style '${{...}}' (negative lookbehind for '$' in
        `_TOKEN_RE').
      - Escaped literals '\\{{...}}' (a single leading backslash). These are
        documentation literals that survive verbatim.

    Used by the per-file and final post-resolution scans to count and report
    unresolved tokens without false positives.
    """
    return [
        "{{" + m.group(2) + "}}"
        for m in _TOKEN_RE.finditer(text)
        if m.group(1) != "\\"
    ]


# Stricter detector for the DEPLOYED tree: only matches real build tokens of
# the form {{namespace.key}} (at least one dot required; flatten() can emit
# multi-level keys like {{a.b.c}}, so one-or-more dot segments are accepted).
# Mirrors scripts/check_tokens.py `_TOKEN_RE` so the post-deploy scan and the
# CI guardrail agree on what counts as a leak.
_REAL_TOKEN_RE = re.compile(
    r"(?<!\$)(\\?)\{\{([a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)+)\}\}"
)


def find_unresolved_real_tokens(text: str) -> list:
    """Return the {{namespace.key}} tokens that are genuine substitution leaks.

    Deployed-tree semantics: the post-deploy scan runs on FINAL files, AFTER
    strip_escapes() has removed the authoring backslashes — so an intentional
    documentation literal like '{{tokens}}' is indistinguishable by shape from
    an escaped one. Only dotted namespace.key forms can be real config tokens
    (all config keys are namespaced); no-dot brace literals are documentation
    and are NOT flagged. This matches scripts/check_tokens.py's `_TOKEN_RE`
    exactly, so a deploy that passes here also passes the CI guardrail.

    Do NOT use this for the pre-strip scans during resolution — there,
    find_unresolved_tokens() must keep flagging every non-escaped {{...}}
    regardless of shape, because escapes still carry their backslash and
    anything else brace-wrapped is a likely authoring mistake.
    """
    return [
        "{{" + m.group(2) + "}}"
        for m in _REAL_TOKEN_RE.finditer(text)
        if m.group(1) != "\\"
    ]


def substitute(text: str, tokens: dict) -> str:
    """Replace {{token}} occurrences with config values.
    Unrecognised tokens are left in place and printed as warnings.

    Tokens resolve everywhere, including inside Markdown inline code spans
    (backtick-delimited). Two kinds of token-shaped strings are deliberately
    handled differently (no substitution attempt, no warning):
      - GitHub Actions syntax: a leading '$' before '{{' (e.g.
        '${{ secrets.FOO }}'). init.py tokens never use a dollar prefix.
      - Escaped literals: a single backslash before '{{' (i.e.
        '\\{{token}}'). The marker is preserved verbatim here so the
        unresolved-token scans can distinguish it from a real unresolved
        token; strip_escapes() removes the backslash as the build's final
        step. Authors use this when discussing the template system in prose
        and need the token to survive unchanged.
    """
    warnings = []

    def replace(match):
        if match.group(1) == "\\":
            # Escaped literal: preserve the marker verbatim (including the
            # backslash) so the unresolved-token scans skip it. The backslash
            # is stripped later by strip_escapes() as the build's final step.
            return match.group(0)
        key = match.group(2).strip()
        if key not in tokens:
            warnings.append(key)
            return "{{" + match.group(2) + "}}"   # leave unreplaced — visible in output
        return tokens[key]

    result = _TOKEN_RE.sub(replace, text)

    for w in warnings:
        print(f"  ⚠  no config value for {{{{ {w} }}}}")

    return result


# Markers delimiting the managed block init.py owns inside an adopter's
# AGENTS.md. Everything outside these markers belongs to the adopter and is
# never modified.
CODEX_BLOCK_BEGIN = "<!-- agent-enterprise:begin -->"
CODEX_BLOCK_END = "<!-- agent-enterprise:end -->"


def emit_codex_agents_md(output_dir: Path, tokens: dict, target_file: Path) -> bool:
    """Merge the agent-enterprise managed block into an adopter-owned AGENTS.md.

    Renders a block delimited by CODEX_BLOCK_BEGIN / CODEX_BLOCK_END containing
    a provenance note (no timestamps — output must be deterministic), the agent
    roster from ``output_dir/agents/*.agent.md`` (name + description from
    frontmatter, sorted by name), and a pointer to the deployed skills and
    instructions directories (``paths.skills_deploy_dir`` /
    ``paths.instructions_dir`` tokens).

    Merge semantics — content outside the markers is NEVER touched:
      - both markers present: replace only the content between the first begin
        marker and the first end marker (the marker lines are preserved);
      - no markers: append the block at the end, separated by a blank line;
      - file missing: create it containing just the block;
      - malformed markers (begin without end, end without begin, or end before
        begin): print a warning and leave the file untouched — no data loss;
      - duplicate markers (more than one begin or end marker, e.g. a verbatim
        marker example elsewhere in the file): print a warning and leave the
        file untouched — splicing at the first occurrence could eat adopter
        content.

    Line endings: the file is read and written without newline translation, so
    out-of-marker bytes are preserved exactly. The managed block itself is
    rendered with the file's dominant newline convention (CRLF files stay
    CRLF; everything else, and newly created files, use LF).

    A second run with unchanged inputs is byte-identical.
    Returns True if the file was written, False if it was skipped.
    """
    # --- Render the managed block (deterministic: sorted roster, no dates) ---
    roster = []
    src_agents = output_dir / "agents"
    if src_agents.exists():
        for md in sorted(src_agents.glob("*.agent.md")):
            fm, _body = parse_frontmatter(md.read_text(encoding="utf-8"))
            name = str(fm.get("name") or md.name[: -len(".agent.md")])
            desc = str(fm.get("description", "")).strip()
            roster.append((name, desc))
    roster.sort(key=lambda item: item[0])

    skills_dir = tokens.get("paths.skills_deploy_dir", ".github/agents/")
    instructions_dir = tokens.get("paths.instructions_dir", ".github/instructions")

    lines = [
        CODEX_BLOCK_BEGIN,
        "<!-- Generated by agent-enterprise init.py — edit the sources under "
        "skills/, instructions/, and agents/, not this block. -->",
        "",
        "## Agent roster (agent-enterprise)",
        "",
    ]
    if roster:
        for name, desc in roster:
            lines.append(f"- **{name}** — {desc}" if desc else f"- **{name}**")
    else:
        lines.append("_No agents generated._")
    lines += [
        "",
        f"Deployed skills live under `{skills_dir}` and shared instructions "
        f"under `{instructions_dir}`.",
        CODEX_BLOCK_END,
    ]
    block = "\n".join(lines)

    # --- Merge into the target file without touching out-of-marker content ---
    if target_file.exists():
        # newline="" disables universal-newline translation: the exact bytes
        # (CRLF included) are spliced, so out-of-marker content round-trips.
        with open(target_file, encoding="utf-8", newline="") as f:
            existing = f.read()
        begin_count = existing.count(CODEX_BLOCK_BEGIN)
        end_count = existing.count(CODEX_BLOCK_END)
        if begin_count > 1 or end_count > 1:
            print(
                f"  ⚠  {target_file}: multiple agent-enterprise markers found "
                f"({begin_count} begin / {end_count} end) — leaving file "
                "untouched (keep exactly one marker pair; indent or alter any "
                "marker examples so they don't match verbatim)."
            )
            return False
        begin = existing.find(CODEX_BLOCK_BEGIN)
        end = existing.find(CODEX_BLOCK_END)
        if (begin == -1) != (end == -1) or (begin != -1 and end < begin):
            print(
                f"  ⚠  {target_file}: malformed agent-enterprise markers — "
                "leaving file untouched (fix or remove the markers and re-run)."
            )
            return False
        # Render the block with the file's dominant newline convention.
        crlf_count = existing.count("\r\n")
        bare_lf_count = existing.count("\n") - crlf_count
        newline = "\r\n" if crlf_count > bare_lf_count else "\n"
        nl_block = block.replace("\n", newline) if newline != "\n" else block
        if begin != -1:
            # Replace marker-to-marker (inclusive); everything else verbatim.
            merged = existing[:begin] + nl_block + existing[end + len(CODEX_BLOCK_END):]
        elif not existing.strip():
            merged = nl_block + newline
        else:
            merged = existing.rstrip("\r\n") + newline * 2 + nl_block + newline
    else:
        merged = block + "\n"

    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, "w", encoding="utf-8", newline="") as f:
        f.write(merged)
    return True


def deploy_resolved(
    output: Path, config: dict, agent_count: int, stale_agent_names=()
) -> int:
    """Copy resolved/ into the configured deploy dirs under .github/.

    Mirrors the manual "Next steps" copy so the deployed tree (the files
    agents actually load) cannot silently drift from resolved/. Returns the
    number of unresolved-token hits found in the deployed tree (0 = clean).
    Callers should treat a non-zero return as a deploy failure.

    ``stale_agent_names`` lists agents the build itself flagged as stale
    (setup-only skills skipped after setup_complete flipped, or wrappers
    pruned because their source skill is gone). Their previously deployed
    artifacts — the <name>.agent.md wrapper and <name>/ skill bundle under
    skills_deploy_dir, plus <name>.md in claude_commands / claude_agents /
    cursor_commands — are removed so the deployed tree matches what a clean
    clone would produce. Only build-flagged names are touched; adopter-owned
    files in those directories are never pruning candidates.

    Also seeds paths.claude_commands (default: .claude/commands/) with one
    <name>.md file per agent — the filename (without .md) becomes the Claude
    Code slash-command name. When editor.target is 'claude-code', 'both', or
    'all', paths.claude_agents (default: .claude/agents/) is seeded with one
    native Claude Code subagent per agent. When editor.target is 'cursor' or
    'all', paths.cursor_commands (default: .cursor/commands/) is seeded the
    same way as claude_commands. When editor.target is 'codex' or 'all', a
    managed block is merged into paths.codex_agents_md (default: AGENTS.md)
    via emit_codex_agents_md().
    """
    paths = config.get("paths", {})
    instructions_dir = paths.get("instructions_dir")
    skills_deploy_dir = paths.get("skills_deploy_dir")
    claude_commands = paths.get("claude_commands")
    claude_agents = paths.get("claude_agents")
    cursor_commands = paths.get("cursor_commands")
    codex_agents_md = paths.get("codex_agents_md")
    editor_target = config.get("editor", {}).get("target", "both")

    if not instructions_dir or not skills_deploy_dir:
        print("⚠  Cannot deploy: paths.instructions_dir and/or "
              "paths.skills_deploy_dir not set in config.")
        return -1

    # Guard against absolute deploy paths that could write outside the project.
    for _label, _dest_val in [
        ("paths.instructions_dir", instructions_dir),
        ("paths.skills_deploy_dir", skills_deploy_dir),
        ("paths.claude_commands", claude_commands),
        ("paths.claude_agents", claude_agents),
        ("paths.cursor_commands", cursor_commands),
        ("paths.codex_agents_md", codex_agents_md),
    ]:
        if _dest_val and Path(_dest_val).is_absolute():
            print(
                f"ERROR: Deploy target '{_label}' is an absolute path — "
                "refusing to deploy outside project directory.",
                file=sys.stderr,
            )
            sys.exit(1)

    instr_dest = Path(instructions_dir)
    skills_dest = Path(skills_deploy_dir)
    instr_dest.mkdir(parents=True, exist_ok=True)
    skills_dest.mkdir(parents=True, exist_ok=True)

    deployed = 0

    # Prune deployed artifacts of agents the build flagged as stale (e.g. the
    # setup-only onboarding skill after setup_complete flips). Without this,
    # a committed tree keeps zombie files a clean clone can never reproduce.
    for stale_name in sorted(set(stale_agent_names)):
        stale_files = [skills_dest / f"{stale_name}.agent.md"]
        for seeded_dir in (claude_commands, claude_agents, cursor_commands):
            if seeded_dir:
                stale_files.append(Path(seeded_dir) / f"{stale_name}.md")
        for stale_file in stale_files:
            if stale_file.is_file():
                stale_file.unlink()
                print(f"  removed stale deployed file: {stale_file}")
        stale_bundle = skills_dest / stale_name
        if stale_bundle.is_dir():
            shutil.rmtree(stale_bundle)
            print(f"  removed stale deployed skill bundle: {stale_bundle}")

    # Instructions: resolved/instructions/*.md -> instructions_dir/
    src_instr = output / "instructions"
    if src_instr.exists():
        for md in sorted(src_instr.glob("*.md")):
            shutil.copy(md, instr_dest / md.name)
            deployed += 1

    # Agent wrappers: resolved/agents/*.agent.md -> skills_deploy_dir/
    src_agents = output / "agents"
    if agent_count and src_agents.exists():
        for md in sorted(src_agents.glob("*.agent.md")):
            shutil.copy(md, skills_dest / md.name)
            deployed += 1

    # Skill bundles: resolved/skills/<name>/* -> skills_deploy_dir/<name>/
    src_skills = output / "skills"
    if src_skills.exists():
        for skill_dir in sorted(p for p in src_skills.iterdir() if p.is_dir()):
            dest_dir = skills_dest / skill_dir.name
            dest_dir.mkdir(parents=True, exist_ok=True)
            for f in sorted(skill_dir.glob("*")):
                if f.is_file():
                    shutil.copy(f, dest_dir / f.name)
                    deployed += 1

    # Claude Code slash commands: resolved/agents/*.agent.md -> claude_commands/<name>.md
    # The filename without .md becomes the slash-command name (e.g. planner.md → /planner).
    if agent_count and src_agents.exists() and claude_commands:
        claude_dest = Path(claude_commands)
        claude_dest.mkdir(parents=True, exist_ok=True)
        for md in sorted(src_agents.glob("*.agent.md")):
            # planner.agent.md → planner.md
            name = md.name[: -len(".agent.md")]
            shutil.copy(md, claude_dest / f"{name}.md")
            deployed += 1
        print(f"  seeded {len(list(src_agents.glob('*.agent.md')))} Claude Code slash command(s) → {claude_dest}")

    # Claude Code native subagents: resolved/agents/*.agent.md -> claude_agents/<name>.md
    # Gated on the Claude Code-consuming targets ('claude-code', 'both',
    # 'all'). Each file re-renders the wrapper with Claude Code subagent
    # frontmatter (name + description; tools omitted — see
    # generate_claude_subagent_md). Sorted iteration, plain overwrite: a
    # second deploy with unchanged inputs is byte-identical.
    seed_claude_agents = editor_target in ('claude-code', 'both', 'all')
    if agent_count and src_agents.exists() and claude_agents and seed_claude_agents:
        subagents_dest = Path(claude_agents)
        subagents_dest.mkdir(parents=True, exist_ok=True)
        seeded_subagents = 0
        for md in sorted(src_agents.glob("*.agent.md")):
            # planner.agent.md → planner.md
            name = md.name[: -len(".agent.md")]
            fm, body = parse_frontmatter(md.read_text(encoding="utf-8"))
            (subagents_dest / f"{name}.md").write_text(
                generate_claude_subagent_md(name, fm or {}, body),
                encoding="utf-8",
            )
            deployed += 1
            seeded_subagents += 1
        print(f"  seeded {seeded_subagents} Claude Code subagent(s) → {subagents_dest}")

    # Cursor commands: resolved/agents/*.agent.md -> cursor_commands/<name>.md
    # Gated on cursor's composite memberships ('cursor', 'all') — mirrors the
    # emit_cursor gate for .cursor/rules/*.mdc. Wrappers are copied verbatim,
    # consistent with the Claude commands seeding: agent wrapper frontmatter
    # carries no applies_to/scope field, and transform_frontmatter_for_target
    # is a deliberate no-op for 'cursor' (scoping is the .mdc emitter's job).
    seed_cursor_commands = editor_target in ('cursor', 'all')
    if agent_count and src_agents.exists() and cursor_commands and seed_cursor_commands:
        cursor_dest = Path(cursor_commands)
        cursor_dest.mkdir(parents=True, exist_ok=True)
        for md in sorted(src_agents.glob("*.agent.md")):
            # planner.agent.md → planner.md
            name = md.name[: -len(".agent.md")]
            shutil.copy(md, cursor_dest / f"{name}.md")
            deployed += 1
        print(f"  seeded {len(list(src_agents.glob('*.agent.md')))} Cursor command(s) → {cursor_dest}")

    # Codex AGENTS.md managed block: agent roster + deploy-dir pointers merged
    # idempotently between <!-- agent-enterprise:begin/end --> markers in the
    # adopter-owned file. Gated on codex's composite memberships ('codex',
    # 'all'), mirroring the cursor_commands gate above. Content outside the
    # markers is never modified; the file is deliberately excluded from the
    # post-deploy token scan because the adopter owns everything around the
    # managed block.
    if editor_target in ('codex', 'all') and codex_agents_md:
        if emit_codex_agents_md(output, flatten(config), Path(codex_agents_md)):
            print(f"  merged Codex managed block → {codex_agents_md}")

    print(f"  deployed {deployed} file(s) to {instr_dest} and {skills_dest}")

    # Post-deploy guardrail: the deployed tree must be free of REAL token
    # leaks. These files are post-strip_escapes(), so intentional no-dot
    # documentation literals like '{{tokens}}' are clean output here —
    # find_unresolved_real_tokens() flags only dotted {{namespace.key}}
    # forms, matching scripts/check_tokens.py.
    leftover = []
    for md in sorted(skills_dest.rglob("*.md")):
        if find_unresolved_real_tokens(md.read_text(encoding="utf-8")):
            leftover.append(md)
    for md in sorted(instr_dest.rglob("*.md")):
        if find_unresolved_real_tokens(md.read_text(encoding="utf-8")):
            leftover.append(md)
    if claude_commands:
        for md in sorted(Path(claude_commands).rglob("*.md")):
            if find_unresolved_real_tokens(md.read_text(encoding="utf-8")):
                leftover.append(md)
    # Scan claude_agents whenever the token is set — even when the current
    # target gates the seeding off, a previously seeded (or stale) file in
    # the directory must still fail the deploy if it leaks tokens. Mirrors
    # the ungated claude_commands / cursor_commands scans above and below.
    if claude_agents and Path(claude_agents).is_dir():
        for md in sorted(Path(claude_agents).rglob("*.md")):
            if find_unresolved_real_tokens(md.read_text(encoding="utf-8")):
                leftover.append(md)
    if cursor_commands:
        for md in sorted(Path(cursor_commands).rglob("*.md")):
            if find_unresolved_real_tokens(md.read_text(encoding="utf-8")):
                leftover.append(md)

    return len(leftover)


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
    parser.add_argument(
        "--allow-frontmatter-warnings",
        action="store_true",
        help="Lax mode: collect frontmatter-v1 / callable-v1 violations as warnings instead of aborting the build."
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="After a clean build, copy resolved/ into the configured deploy dirs "
             "(paths.instructions_dir, paths.skills_deploy_dir). Refuses to deploy "
             "if any unresolved token remains in the output."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Legacy flag — hard failure on unresolved tokens is now the default behaviour. "
             "Kept for backward compatibility; passing it has no additional effect."
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

    # =============================================================================
    # Frontmatter Validation — protocol-v1 (frontmatter-v1 + callable-v1)
    # =============================================================================
    print("Running frontmatter validation (protocol-v1)...")
    fm_errors: list[str] = []
    for skill_md in sorted(Path("skills").rglob("*.skill.md")):
        fm_errors.extend(
            validate_frontmatter(skill_md.read_text(encoding="utf-8"), "skill", skill_md)
        )
    for instr in sorted(Path("instructions").rglob("*.instructions.md")):
        fm_errors.extend(
            validate_frontmatter(instr.read_text(encoding="utf-8"), "instruction", instr)
        )
    for body in sorted(Path("agents").rglob("*.body.md")):
        fm_errors.extend(
            validate_frontmatter(body.read_text(encoding="utf-8"), "agent", body)
        )

    if fm_errors:
        header = (
            "⚠  Frontmatter validation warnings (lax mode):"
            if args.allow_frontmatter_warnings
            else "❌ Frontmatter validation FAILED (strict mode):"
        )
        print(header)
        for err in fm_errors:
            print(f"  - {err}")
        if not args.allow_frontmatter_warnings:
            print(
                "\n  Re-run with --allow-frontmatter-warnings to convert these into warnings."
            )
            sys.exit(1)
        print()
    else:
        print("✓ Frontmatter validation passed")
        print()

    tokens = flatten(config)
    print(f"Loaded {len(tokens)} config tokens from {config_path}")

    output = Path("resolved")
    output.mkdir(exist_ok=True)   # overwrite in-place — avoids permission issues on re-runs

    resolved_count = 0
    copied_count = 0
    warning_count = 0

    # --- Skills (SKILL.md or {name}.skill.md files → resolved as SKILL.md) ---
    setup_complete = config.get('setup_complete', False)
    # Agents whose artifacts must be purged from resolved/ and the deployed
    # tree: setup-only skills skipped this build, plus any wrapper whose
    # source skill no longer produces it (pruned after generation below).
    stale_agent_names: set[str] = set()
    skills_src = Path("skills")
    if skills_src.exists():
        for skill_dir in sorted(skills_src.iterdir()):
            if not skill_dir.is_dir():
                continue
            # Find skill file — prefer SKILL.md, fall back to {name}.skill.md
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                candidates = list(skill_dir.glob("*.skill.md"))
                skill_md = candidates[0] if candidates else None
            if not skill_md or not skill_md.exists():
                continue

            # Skip setup-only skills when setup is complete
            original = skill_md.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(original)
            if fm.get('lifecycle') == 'setup-only' and setup_complete:
                print(f"  skipped (setup complete): {skill_dir.name}")
                skipped_name = fm.get('name', skill_dir.name)
                stale_agent_names.add(skipped_name)
                # Clean stale resolved output if it exists
                stale_dir = output / "skills" / skill_dir.name
                if stale_dir.exists():
                    shutil.rmtree(stale_dir)
                # Mirror the cleanup for the skill's agent wrapper — a stale
                # resolved/agents/<name>.agent.md would otherwise be
                # re-deployed as a zombie artifact.
                stale_wrapper = output / "agents" / f"{skipped_name}.agent.md"
                if stale_wrapper.exists():
                    stale_wrapper.unlink()
                    print(f"  removed stale agent wrapper: {stale_wrapper}")
                continue

            # Output as SKILL.md (VS Code convention) regardless of source filename
            dest = output / "skills" / skill_dir.name / "SKILL.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            resolved = substitute(original, tokens)
            dest.write_text(resolved, encoding="utf-8")
            unresolved = find_unresolved_tokens(resolved)
            if unresolved:
                print(f"  resolved (with warnings): {dest}")
                warning_count += len(unresolved)
            else:
                print(f"  resolved: {dest}")
            resolved_count += 1

            # Resolve companion files — non-skill *.md siblings (e.g.
            # phase-details.md, subagent-templates.md). The *.skill.md source
            # is excluded; SKILL.md output lives under resolved/ and is never
            # a source here since we iterate the source skills/ directory.
            for companion in sorted(skill_dir.glob("*.md")):
                if companion.name.endswith(".skill.md") or companion.name == "SKILL.md":
                    continue
                comp_dest = output / "skills" / skill_dir.name / companion.name
                comp_dest.parent.mkdir(parents=True, exist_ok=True)
                comp_resolved = substitute(companion.read_text(encoding="utf-8"), tokens)
                comp_dest.write_text(comp_resolved, encoding="utf-8")
                comp_unresolved = find_unresolved_tokens(comp_resolved)
                if comp_unresolved:
                    print(f"  resolved (with warnings): {comp_dest}")
                    warning_count += len(comp_unresolved)
                else:
                    print(f"  resolved: {comp_dest}")
                resolved_count += 1

    # --- Configurable instructions ---
    editor_target_early = config.get('editor', {}).get('target', 'both')
    cursor_dir = Path(".cursor") / "rules"
    emit_cursor = editor_target_early in ('cursor', 'all')

    def _apply_scope_and_emit(name: str, dest: Path, resolved_text: str) -> None:
        """Rewrite scope→platform field in resolved text; emit .mdc if needed."""
        fm, body = parse_frontmatter(resolved_text)
        if fm:
            new_fm = transform_frontmatter_for_target(fm, editor_target_early)
            if new_fm != fm:
                rewritten = _render_frontmatter(new_fm) + "\n" + body + ("\n" if not body.endswith("\n") else "")
                dest.write_text(rewritten, encoding="utf-8")
        if emit_cursor:
            emit_cursor_mdc(name, fm or {}, body, cursor_dir)

    configurable_src = Path("instructions/configurable")
    if configurable_src.exists():
        for instr in sorted(configurable_src.glob("*.md")):
            dest = output / "instructions" / instr.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            original = instr.read_text(encoding="utf-8")
            resolved = substitute(original, tokens)
            dest.write_text(resolved, encoding="utf-8")
            unresolved = find_unresolved_tokens(resolved)
            if unresolved:
                print(f"  resolved (with warnings): {dest}")
                warning_count += len(unresolved)
            else:
                print(f"  resolved: {dest}")
            resolved_count += 1
            _apply_scope_and_emit(instr.stem.replace('.instructions', ''), dest, resolved)

    # --- Generic instructions (copy as-is) ---
    generic_src = Path("instructions/generic")
    if generic_src.exists():
        for instr in sorted(generic_src.glob("*.md")):
            dest = output / "instructions" / instr.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(instr, dest)
            print(f"  copied:   {dest}")
            copied_count += 1
            _apply_scope_and_emit(instr.stem.replace('.instructions', ''), dest, dest.read_text(encoding="utf-8"))

    # --- Agent wrappers (all valid targets) ---
    # Every valid editor.target gets resolved/agents/*.agent.md — per-target
    # emission (Claude Code subagents, Cursor commands, Codex AGENTS.md
    # managed block) consumes these wrappers downstream.
    editor_target = config.get('editor', {}).get('target', 'both')
    agent_count = 0
    suppressed_count = 0

    if editor_target in VALID_EDITOR_TARGETS:
        print()
        print("Generating agent wrappers...")
        agent_names = generate_agents(output, tokens)
        agent_count = len(agent_names)

        # Prune wrappers from previous builds whose skill is now skipped,
        # renamed, or deleted — resolved/agents/ must contain exactly the
        # wrappers generated by THIS build.
        agents_out = output / "agents"
        if agents_out.exists():
            for stale in sorted(agents_out.glob("*.agent.md")):
                stale_name = stale.name[: -len(".agent.md")]
                if stale_name not in agent_names:
                    stale.unlink()
                    stale_agent_names.add(stale_name)
                    print(f"  removed stale agent wrapper: {stale}")

        if editor_target == 'vscode' and agent_names:
            # Phase 6 (vscode-only): suppress skill discoverability when
            # agents exist. Claude Code / Cursor / Codex must NOT get
            # user-invocable: false skills.
            suppressed_count = suppress_skill_invocability(output, agent_names)

        if agent_count:
            print(f"✓ Generated {agent_count} agent wrapper(s)")
            if suppressed_count:
                print(f"  ({suppressed_count} skill(s) set to user-invocable: false)")
        else:
            print("  No skills with agent: metadata found — skipping")
    else:
        print()
        print(f"Skipping agent generation (editor.target: {editor_target})")

    # --- Final unresolved token scan ---
    print()
    all_unresolved = []
    for md in sorted(output.rglob("*.md")):
        matches = find_unresolved_tokens(md.read_text(encoding="utf-8"))
        if matches:
            all_unresolved.append((md, matches))

    if all_unresolved:
        print(f"⚠  {len(all_unresolved)} file(s) have unresolved tokens:")
        for path, found in all_unresolved:
            for token in found:
                key = token.strip("{}").strip()
                print(f"   {path}: Missing config key '{key}' — add it to your project.config.yml")
        print()
    else:
        print("✓ All tokens resolved — no unresolved {{placeholders}} in output.")
        print()

    # --- Strip authoring escapes (final pass, after all scans) ---
    # '\{{token}}' -> '{{token}}'. Done last so intentional literals appear
    # verbatim in deployed files without tripping the unresolved scans above.
    for md in sorted(output.rglob("*.md")):
        content = md.read_text(encoding="utf-8")
        stripped = strip_escapes(content)
        if stripped != content:
            md.write_text(stripped, encoding="utf-8")

    print(f"Summary: {resolved_count} resolved, {copied_count} copied, {agent_count} agents, {warning_count} token warnings")
    print()

    # --- Hard guardrail: fail the build on any unresolved token ---
    # This is unconditional. --strict is kept as a legacy no-op.
    if all_unresolved:
        print("✗ Build failed — unresolved tokens detected. "
              "Add the missing config keys listed above to your project.config.yml and re-run.")
        sys.exit(1)

    # --- Optional deploy-copy into the .github tree ---
    if args.deploy:
        if all_unresolved:
            print("✗ Refusing to deploy: output still contains unresolved tokens. "
                  "Fix the config and re-run with --deploy.")
            sys.exit(1)
        print("Deploying resolved/ into configured deploy dirs...")
        leftover = deploy_resolved(
            output, config, agent_count,
            stale_agent_names=sorted(stale_agent_names),
        )
        if leftover < 0:
            sys.exit(1)
        if leftover > 0:
            print(f"✗ Deploy guardrail: {leftover} deployed file(s) still contain "
                  "unresolved {{tokens}}. This should not happen after a clean build — "
                  "investigate companion-file resolution.")
            sys.exit(1)
        print("✓ Deploy complete — deployed tree is token-free.")
        print()
        return

    print("Next steps:")
    print("  python init.py --config <config> --deploy   # build + copy into .github/ (recommended)")
    print("  — or copy manually —")
    print("  cp -r resolved/skills/*        .github/agents/")
    print("  cp -r resolved/instructions/*  .github/instructions/")
    if agent_count:
        print("  cp -r resolved/agents/*        .github/agents/")
    print("  Copy starters/* to your project docs if starting fresh.")


if __name__ == "__main__":
    main()
