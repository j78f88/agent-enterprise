"""
Platform emission matrix tests (Sprint 4, Task Group 5).

Cross-target view of the build + deploy pipeline: for every valid
``editor.target`` value, a full ``init.py`` run (``main()`` with ``--deploy``)
in a temp project dir must emit EXACTLY the pinned artifact set for that
target — nothing missing, nothing extra from another target's set.

Encoded artifact matrix (one agent-bearing skill ``architect``, one scoped
instruction ``style``):

| Artifact                                  | vscode | claude-code | cursor | codex | both | all |
|-------------------------------------------|:------:|:-----------:|:------:|:-----:|:----:|:---:|
| resolved/agents/*.agent.md                |   x    |      x      |   x    |   x   |  x   |  x  |
| .github/instructions/ (deploy)            |   x    |      x      |   x    |   x   |  x   |  x  |
| .github/agents/*.agent.md (deploy)        |   x    |      x      |   x    |   x   |  x   |  x  |
| .github/agents/<skill>/SKILL.md (deploy)  |   x    |      x      |   x    |   x   |  x   |  x  |
| .claude/commands/<name>.md                |   x    |      x      |   x    |   x   |  x   |  x  |
| .claude/agents/<name>.md                  |        |      x      |        |       |  x   |  x  |
| .cursor/rules/*.mdc                       |        |             |   x    |       |      |  x  |
| .cursor/commands/<name>.md                |        |             |   x    |       |      |  x  |
| AGENTS.md managed block                   |        |             |        |   x   |      |  x  |
| skill user-invocable suppression          |   x    |             |        |       |      |     |

Note: ``.claude/commands/`` seeding is deliberately ungated by
``editor.target`` in ``deploy_resolved`` — it fires for every target whenever
``paths.claude_commands`` is configured. This module pins that behaviour.

Per-feature behaviour tests (merge edge cases, absolute-path guards,
leftover-token accounting) live in tests/test_init.py — this module only
holds the matrix, token-free, and determinism invariants.

Run with: pytest tests/test_platform_emission.py -v
"""

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from init import (
    CODEX_BLOCK_BEGIN,
    CODEX_BLOCK_END,
    find_unresolved_real_tokens,
    main,
)
from tests.test_init import make_minimal_config


TARGETS = ["vscode", "claude-code", "cursor", "codex", "both", "all"]

# Adopter-owned AGENTS.md content that must survive every build untouched.
ADOPTER_AGENTS_MD = "# Adopter Guide\n\nHand-written adopter notes.\n"

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

SCOPED_INSTRUCTION = (
    "---\n"
    "id: instruction.style\n"
    "kind: instruction\n"
    "version: 1.0.0\n"
    "applies_to: 'src/**'\n"
    "description: style instruction\n"
    "---\n\n"
    "# Style\n\nFollow the {{project.name}} style guide.\n"
)

# --- The pinned artifact matrix -------------------------------------------
# Relative paths emitted by build (resolved/, .cursor/rules) + deploy
# (.github/, .claude/, .cursor/commands, AGENTS.md). AGENTS.md is excluded
# here (it pre-exists as adopter content); its managed block is asserted
# separately below.

COMMON_ARTIFACTS = {
    # build output — all targets generate agent wrappers (Sprint 4 TG1)
    "resolved/skills/architect/SKILL.md",
    "resolved/instructions/style.instructions.md",
    "resolved/agents/architect.agent.md",
    # .github deploy tree — deploy_resolved copies it for every target
    ".github/instructions/style.instructions.md",
    ".github/agents/architect.agent.md",
    ".github/agents/architect/SKILL.md",
    # Claude Code slash commands — ungated by editor.target
    ".claude/commands/architect.md",
}

TARGET_GATED_ARTIFACTS = {
    ".claude/agents/architect.md": {"claude-code", "both", "all"},
    ".cursor/rules/style.mdc": {"cursor", "all"},
    ".cursor/commands/architect.md": {"cursor", "all"},
}

CODEX_BLOCK_TARGETS = {"codex", "all"}
SUPPRESSION_TARGETS = {"vscode"}


def expected_artifacts(target: str) -> set:
    gated = {
        path
        for path, targets in TARGET_GATED_ARTIFACTS.items()
        if target in targets
    }
    return COMMON_ARTIFACTS | gated


def _setup_project(tmp_path: Path, target: str) -> Path:
    """Seed a minimal adopter project: config, one skill, one instruction,
    and a pre-existing adopter-owned AGENTS.md."""
    config_path = make_minimal_config(tmp_path, editor={"target": target})
    # make_minimal_config has no paths.claude_commands — add it so the
    # ungated Claude commands seeding is exercised by the matrix.
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    cfg["paths"]["claude_commands"] = ".claude/commands"
    config_path.write_text(yaml.dump(cfg), encoding="utf-8")

    skill_dir = tmp_path / "skills" / "architect"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(AGENT_SKILL, encoding="utf-8")

    instr_dir = tmp_path / "instructions" / "configurable"
    instr_dir.mkdir(parents=True)
    (instr_dir / "style.instructions.md").write_text(
        SCOPED_INSTRUCTION, encoding="utf-8"
    )

    (tmp_path / "AGENTS.md").write_text(ADOPTER_AGENTS_MD, encoding="utf-8")
    return config_path


def _snapshot(tmp_path: Path) -> dict:
    """Map every emitted artifact (relative path) to its bytes."""
    snap = {}
    for top in ("resolved", ".github", ".claude", ".cursor"):
        base = tmp_path / top
        if not base.exists():
            continue
        for f in sorted(base.rglob("*")):
            if f.is_file():
                snap[f.relative_to(tmp_path).as_posix()] = f.read_bytes()
    agents_md = tmp_path / "AGENTS.md"
    if agents_md.exists():
        snap["AGENTS.md"] = agents_md.read_bytes()
    return snap


def _run_build_deploy(tmp_path: Path, config_path: Path) -> None:
    mp = pytest.MonkeyPatch()
    try:
        mp.chdir(tmp_path)
        mp.setattr(
            sys,
            "argv",
            [
                "init.py",
                "--config",
                str(config_path),
                "--allow-frontmatter-warnings",
                "--deploy",
            ],
        )
        main()
    finally:
        mp.undo()


@pytest.fixture(scope="module", params=TARGETS)
def built_project(request, tmp_path_factory):
    """Build + deploy TWICE per target (determinism evidence), once per
    module — every test below reads the same snapshots."""
    target = request.param
    tmp_path = tmp_path_factory.mktemp(f"emission-{target}")
    config_path = _setup_project(tmp_path, target)

    _run_build_deploy(tmp_path, config_path)
    first = _snapshot(tmp_path)
    _run_build_deploy(tmp_path, config_path)
    second = _snapshot(tmp_path)

    return target, first, second


class TestPlatformEmissionMatrix:
    """Exact artifact set per editor.target — presence AND absence."""

    def test_exact_artifact_set_per_target(self, built_project):
        target, first, _second = built_project
        emitted = set(first) - {"AGENTS.md"}
        expected = expected_artifacts(target)

        missing = expected - emitted
        extra = emitted - expected
        assert not missing, (
            f"editor.target '{target}': expected artifacts missing: {sorted(missing)}"
        )
        assert not extra, (
            f"editor.target '{target}': unexpected artifacts emitted "
            f"(another target's set leaked in?): {sorted(extra)}"
        )

    def test_agents_md_managed_block_gated_to_codex_targets(self, built_project):
        target, first, _second = built_project
        content = first["AGENTS.md"].decode("utf-8")
        if target in CODEX_BLOCK_TARGETS:
            assert CODEX_BLOCK_BEGIN in content and CODEX_BLOCK_END in content, (
                f"editor.target '{target}' must merge the AGENTS.md managed block"
            )
            assert "- **architect**" in content, "roster entry missing from block"
        else:
            assert first["AGENTS.md"] == ADOPTER_AGENTS_MD.encode("utf-8"), (
                f"editor.target '{target}' must leave the adopter AGENTS.md "
                "byte-identical (no managed block, no rewrite)"
            )

    def test_agents_md_merge_preserves_out_of_marker_content(self, built_project):
        """Light merge check — deep marker/merge cases live in
        tests/test_init.py::TestCodexAgentsMdEmission."""
        target, first, _second = built_project
        if target not in CODEX_BLOCK_TARGETS:
            pytest.skip("managed block only emitted for codex/all")
        content = first["AGENTS.md"].decode("utf-8")
        assert content.startswith(ADOPTER_AGENTS_MD), (
            "adopter content outside the markers must be preserved verbatim"
        )
        assert content.index(CODEX_BLOCK_BEGIN) < content.index(CODEX_BLOCK_END)

    def test_skill_suppression_is_vscode_only(self, built_project):
        target, first, _second = built_project
        for key in (
            "resolved/skills/architect/SKILL.md",
            ".github/agents/architect/SKILL.md",
        ):
            text = first[key].decode("utf-8")
            if target in SUPPRESSION_TARGETS:
                assert "user-invocable: false" in text, (
                    f"{key}: vscode must suppress invocability for agent-backed skills"
                )
            else:
                assert "user-invocable: true" in text, (
                    f"{key}: editor.target '{target}' must NOT get "
                    "user-invocable: false skills"
                )

    def test_every_emitted_artifact_is_token_free(self, built_project):
        target, first, _second = built_project
        for relpath, content in sorted(first.items()):
            if relpath == "AGENTS.md" and target not in CODEX_BLOCK_TARGETS:
                continue  # untouched adopter file — not an emitted artifact
            leaks = find_unresolved_real_tokens(content.decode("utf-8"))
            assert not leaks, (
                f"editor.target '{target}': {relpath} has unresolved tokens: {leaks}"
            )
            # Spot-check substitution actually ran where the source had a token.
            if relpath.endswith(("architect.agent.md", "style.instructions.md", "style.mdc")):
                assert b"TestProj" in content, f"{relpath}: token not substituted"

    def test_double_build_is_byte_identical(self, built_project):
        target, first, second = built_project
        assert sorted(first) == sorted(second), (
            f"editor.target '{target}': second build changed the artifact set"
        )
        differing = [k for k in first if first[k] != second[k]]
        assert not differing, (
            f"editor.target '{target}': artifacts not byte-identical across "
            f"two builds (includes AGENTS.md): {differing}"
        )
