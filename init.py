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

VALID_EDITOR_TARGETS = {'vscode', 'claude-code', 'cursor', 'both', 'all'}


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

    # Build frontmatter
    fm_lines = ['---']
    fm_lines.append(f'name: {name}')
    fm_lines.append(f'description: "{full_desc}"')
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
# A token is a {{name}} pair init.py is expected to resolve from config. Two
# token-shaped strings are NOT init.py tokens and must be left alone:
#
#   1. GitHub Actions syntax — a literal '$' before '{{'. Skill and
#      instruction docs frequently recommend '${{ secrets.X }}' patterns
#      for workflow files.
#   2. Markdown inline code spans — `{{name}}` inside backticks is doc
#      prose talking about the template system, not a substitution site.
#
# `_TOKEN_RE` uses a negative lookbehind for '$'. The code-span check is
# positional because regex alone cannot reliably scope to backtick spans.

_TOKEN_RE = re.compile(r"(?<!\$)\{\{([^}]+)\}\}")
_CODE_SPAN_RE = re.compile(r"`[^`\n]+`")


def _code_span_ranges(text: str):
    """Return (start, end) byte ranges of every inline code span in `text`."""
    return [(m.start(), m.end()) for m in _CODE_SPAN_RE.finditer(text)]


def _in_any_range(pos: int, ranges) -> bool:
    for start, end in ranges:
        if start <= pos < end:
            return True
    return False


def find_unresolved_tokens(text: str) -> list:
    """Return the list of {{token}} matches that should be flagged.

    Excludes GitHub-Actions-style '${{...}}' (negative lookbehind in
    `_TOKEN_RE`) and any token whose match falls inside a backticked
    inline code span. Used by the per-file and final post-resolution
    scans to count and report unresolved tokens without false positives.
    """
    code_ranges = _code_span_ranges(text)
    return [
        m.group(0)
        for m in _TOKEN_RE.finditer(text)
        if not _in_any_range(m.start(), code_ranges)
    ]


def substitute(text: str, tokens: dict) -> str:
    """Replace {{token}} occurrences with config values.
    Unrecognised tokens are left in place and printed as warnings.

    Two kinds of token-shaped strings are deliberately ignored
    (no substitution attempt, no warning):
      - GitHub Actions syntax: a leading '$' before '{{' (e.g.
        '${{ secrets.FOO }}'). init.py tokens never use a dollar prefix.
      - Documentation literals: a '{{token}}' that appears inside a
        Markdown inline code span (backtick-delimited). Authors wrap
        token-shaped strings in backticks when discussing the template
        system in prose; those references must survive unchanged.
    """
    warnings = []
    code_ranges = _code_span_ranges(text)

    def replace(match):
        if _in_any_range(match.start(), code_ranges):
            return match.group(0)
        key = match.group(1).strip()
        if key not in tokens:
            warnings.append(key)
            return match.group(0)   # leave unreplaced — visible in output
        return tokens[key]

    result = _TOKEN_RE.sub(replace, text)

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
    parser.add_argument(
        "--allow-frontmatter-warnings",
        action="store_true",
        help="Lax mode: collect frontmatter-v1 / callable-v1 violations as warnings instead of aborting the build."
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
                # Clean stale resolved output if it exists
                stale_dir = output / "skills" / skill_dir.name
                if stale_dir.exists():
                    shutil.rmtree(stale_dir)
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

    # --- Agent wrappers (VS Code only) ---
    editor_target = config.get('editor', {}).get('target', 'both')
    agent_count = 0
    suppressed_count = 0

    if editor_target in ('vscode', 'both', 'all'):
        print()
        print("Generating agent wrappers...")
        agent_names = generate_agents(output, tokens)
        agent_count = len(agent_names)

        if editor_target == 'vscode' and agent_names:
            # Phase 6: suppress skill discoverability when agents exist
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
        print(f"⚠  {len(all_unresolved)} file(s) have unresolved tokens — check project.config.yml:")
        for path, found in all_unresolved:
            print(f"   {path}: {found}")
        print()
    else:
        print("✓ All tokens resolved — no unresolved {{placeholders}} in output.")
        print()

    print(f"Summary: {resolved_count} resolved, {copied_count} copied, {agent_count} agents, {warning_count} token warnings")
    print()
    print("Next steps:")
    print("  cp -r resolved/skills/*        .github/agents/")
    print("  cp -r resolved/instructions/*  .github/instructions/")
    if agent_count:
        print("  cp -r resolved/agents/*        .github/agents/")
    print("  Copy starters/* to your project docs if starting fresh.")


if __name__ == "__main__":
    main()
