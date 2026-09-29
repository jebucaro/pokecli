"""Tests for `pokecli install --skills`.

Every test points HOME and the working directory at a temp dir, so nothing is
written to the real ~/.claude or ~/.kiro.
"""

import importlib.resources
import re

import pytest
from typer.testing import CliRunner

from pokecli.main import app

from .conftest import strip_ansi

runner = CliRunner()

SKILL_PKG = importlib.resources.files("pokecli.skills.pokecli")
PACKAGED_SKILL = SKILL_PKG.joinpath("SKILL.md").read_text(encoding="utf-8")
REFERENCE_FILES = ("api-fields.md", "workflows.md")


def _split_frontmatter(text: str) -> tuple[list[str], str]:
    """Frontmatter lines (without the `---` fences) and the body after them."""
    lines = text.splitlines(keepends=True)
    assert lines[0].strip() == "---"
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    return [line.rstrip("\n") for line in lines[1:end]], "".join(lines[end + 1 :])


def _frontmatter_dict(text: str) -> dict[str, str]:
    fields, _ = _split_frontmatter(text)
    return dict(line.split(":", 1) for line in fields)


@pytest.fixture
def home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("KIRO_HOME", raising=False)
    return home


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    workspace = tmp_path / "project"
    workspace.mkdir()
    monkeypatch.chdir(workspace)
    return workspace


def _install(*args: str, env: dict | None = None):
    return runner.invoke(
        app, ["install", "--skills", *args], env={"COLUMNS": "500", **(env or {})}
    )


# --- destinations -----------------------------------------------------------


def test_default_agent_installs_to_claude_home(home, workspace):
    result = _install()
    assert result.exit_code == 0, result.output
    assert (home / ".claude" / "skills" / "pokecli" / "SKILL.md").is_file()
    assert not (home / ".kiro").exists()


def test_local_installs_to_claude_workspace(home, workspace):
    result = _install("--local")
    assert result.exit_code == 0, result.output
    assert (workspace / ".claude" / "skills" / "pokecli" / "SKILL.md").is_file()
    assert not (home / ".claude").exists()


def test_kiro_installs_to_kiro_home(home, workspace):
    result = _install("--agent", "kiro")
    assert result.exit_code == 0, result.output
    assert (home / ".kiro" / "skills" / "pokecli" / "SKILL.md").is_file()
    assert not (home / ".claude").exists()


def test_kiro_local_installs_to_kiro_workspace(home, workspace):
    result = _install("--agent", "kiro", "--local")
    assert result.exit_code == 0, result.output
    assert (workspace / ".kiro" / "skills" / "pokecli" / "SKILL.md").is_file()
    assert list(home.iterdir()) == []


def test_kiro_home_relocates_global_kiro_install(home, workspace, tmp_path):
    kiro_home = tmp_path / "team-kiro"
    result = _install("--agent", "kiro", env={"KIRO_HOME": str(kiro_home)})
    assert result.exit_code == 0, result.output
    assert (kiro_home / "skills" / "pokecli" / "SKILL.md").is_file()
    assert not (home / ".kiro").exists()


def test_empty_kiro_home_falls_back_to_home(home, workspace):
    result = _install("--agent", "kiro", env={"KIRO_HOME": ""})
    assert result.exit_code == 0, result.output
    assert (home / ".kiro" / "skills" / "pokecli" / "SKILL.md").is_file()


def test_kiro_home_does_not_affect_local_install(home, workspace, tmp_path):
    kiro_home = tmp_path / "team-kiro"
    result = _install(
        "--agent", "kiro", "--local", env={"KIRO_HOME": str(kiro_home)}
    )
    assert result.exit_code == 0, result.output
    assert (workspace / ".kiro" / "skills" / "pokecli" / "SKILL.md").is_file()
    assert not kiro_home.exists()


def test_agent_value_is_case_insensitive(home, workspace):
    result = _install("--agent", "KIRO", "--local")
    assert result.exit_code == 0, result.output
    assert (workspace / ".kiro" / "skills" / "pokecli" / "SKILL.md").is_file()


def test_unknown_agent_exits_2_and_writes_nothing(home, workspace):
    result = _install("--agent", "cursor", "--local")
    assert result.exit_code == 2
    output = strip_ansi(result.output)
    assert "claude" in output and "kiro" in output
    assert list(workspace.iterdir()) == []
    assert list(home.iterdir()) == []


def test_agent_without_skills_prints_help_and_writes_nothing(home, workspace):
    result = runner.invoke(app, ["install", "--agent", "kiro"])
    assert result.exit_code == 0
    assert "--skills" in strip_ansi(result.output)
    assert list(workspace.iterdir()) == []
    assert list(home.iterdir()) == []


def test_success_message_names_the_destination(home, workspace):
    result = _install("--agent", "kiro", "--local")
    assert result.exit_code == 0
    dest = workspace / ".kiro" / "skills" / "pokecli"
    assert str(dest) in strip_ansi(result.output).replace("\n", "")


# --- content ----------------------------------------------------------------


def test_claude_skill_equals_packaged_file(home, workspace):
    _install("--local")
    installed = (workspace / ".claude" / "skills" / "pokecli" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert installed == PACKAGED_SKILL


def test_kiro_skill_has_only_name_and_description(home, workspace):
    _install("--agent", "kiro", "--local")
    installed = (workspace / ".kiro" / "skills" / "pokecli" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    installed_fields = _frontmatter_dict(installed)
    packaged_fields = _frontmatter_dict(PACKAGED_SKILL)

    assert set(installed_fields) == {"name", "description"}
    assert installed_fields["name"] == packaged_fields["name"]
    assert installed_fields["description"] == packaged_fields["description"]
    assert _split_frontmatter(installed)[1] == _split_frontmatter(PACKAGED_SKILL)[1]


@pytest.mark.parametrize("agent,dot_dir", [("claude", ".claude"), ("kiro", ".kiro")])
def test_references_match_packaged_files(agent, dot_dir, home, workspace):
    _install("--agent", agent, "--local")
    refs = workspace / dot_dir / "skills" / "pokecli" / "references"
    for name in REFERENCE_FILES:
        packaged = SKILL_PKG.joinpath("references").joinpath(name)
        assert (refs / name).read_text(encoding="utf-8") == packaged.read_text(
            encoding="utf-8"
        )


def test_reinstall_restores_edited_skill(home, workspace):
    _install("--agent", "kiro", "--local")
    skill = workspace / ".kiro" / "skills" / "pokecli" / "SKILL.md"
    expected = skill.read_text(encoding="utf-8")
    skill.write_text("stale", encoding="utf-8")

    result = _install("--agent", "kiro", "--local")
    assert result.exit_code == 0
    assert skill.read_text(encoding="utf-8") == expected


def test_packaged_frontmatter_is_single_line_key_values():
    """The Kiro rewrite filters frontmatter line by line, so values must not wrap."""
    fields, _ = _split_frontmatter(PACKAGED_SKILL)
    for line in fields:
        assert re.match(r"^[A-Za-z][\w-]*: \S", line), (
            f"SKILL.md frontmatter line is not a single-line `key: value`: {line!r}"
        )
