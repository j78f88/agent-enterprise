"""Unit tests for ``validate_frontmatter`` in ``init.py``."""

from __future__ import annotations

from pathlib import Path

from init import validate_frontmatter


def _wrap(fm_yaml: str, body: str = "# x\n") -> str:
    return f"---\n{fm_yaml}\n---\n\n{body}"


def test_valid_skill_passes() -> None:
    text = _wrap(
        "\n".join(
            [
                "id: skill.example",
                "kind: skill",
                "version: 1.0.0",
                "applies_to: '**'",
                "name: example",
                "description: An example skill.",
                "inputs:",
                "  type: object",
                "  required: [task]",
                "  properties:",
                "    task: {type: string}",
                "outputs:",
                "  - {return_tier: 2}",
                "verifier: null",
            ]
        )
    )
    assert validate_frontmatter(text, "skill", Path("ex.skill.md")) == []


def test_skill_missing_id_fails_with_clear_message() -> None:
    text = _wrap(
        "\n".join(
            [
                "kind: skill",
                "version: 1.0.0",
                "applies_to: '**'",
                "name: example",
                "inputs: {type: object}",
                "outputs: [{return_tier: 2}]",
                "verifier: null",
            ]
        )
    )
    errors = validate_frontmatter(text, "skill", Path("ex.skill.md"))
    assert errors, "expected validation errors"
    assert any("'id' is a required property" in e for e in errors)


def test_kind_mismatch_is_reported() -> None:
    text = _wrap(
        "\n".join(
            [
                "id: instruction.x",
                "kind: instruction",
                "version: 1.0.0",
                "applies_to: '**'",
            ]
        )
    )
    errors = validate_frontmatter(text, "skill", Path("x.md"))
    assert any("kind mismatch" in e for e in errors)


def test_unknown_kind_value_fails() -> None:
    text = _wrap(
        "\n".join(
            [
                "id: thing.x",
                "kind: not-a-real-kind",
                "version: 1.0.0",
                "applies_to: '**'",
            ]
        )
    )
    errors = validate_frontmatter(text, "instruction", Path("x.md"))
    assert errors, "expected validation errors for unknown kind"


def test_scope_alias_is_accepted_for_applies_to() -> None:
    text = _wrap(
        "\n".join(
            [
                "id: instruction.aliased",
                "kind: instruction",
                "version: 1.0.0",
                "scope: src/**",
            ]
        )
    )
    assert validate_frontmatter(text, "instruction", Path("x.md")) == []


def test_missing_frontmatter_is_reported() -> None:
    errors = validate_frontmatter("# no fm here\n", "agent", Path("x.md"))
    assert errors and "missing YAML frontmatter" in errors[0]
