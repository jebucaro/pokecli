"""Smoke tests for pokemon encounters/forms sub-commands wiring."""

import re

from typer.testing import CliRunner

from pokecli.main import app

runner = CliRunner()


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences for assertion matching."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_pokemon_help_lists_navigation_subcommands():
    result = runner.invoke(app, ["pokemon", "--help"])
    assert result.exit_code == 0
    assert "Examples:" in result.stdout
    assert "pokecli pokemon pikachu" in result.stdout
    assert "pokecli pokemon can-learn" in result.stdout
    assert "thunderbolt" in result.stdout
    assert "encounters" in result.stdout
    assert "where" in result.stdout
    assert "can-learn" in result.stdout
    assert "evo" in result.stdout
    assert "forms" in result.stdout
    # Existing sub-commands still present
    assert "moves" in result.stdout
    assert "species" in result.stdout
    assert "evolution" in result.stdout


def test_pokemon_encounters_help():
    result = runner.invoke(app, ["pokemon", "encounters", "--help"])
    assert result.exit_code == 0
    output = _strip_ansi(result.stdout)
    assert "name_or_id" in output.lower() or "NAME_OR_ID" in output
    assert "--no-cache" in output


def test_pokemon_forms_help():
    result = runner.invoke(app, ["pokemon", "forms", "--help"])
    assert result.exit_code == 0
    output = _strip_ansi(result.stdout)
    assert "--no-cache" in output
    assert "--format" in output


def test_pokemon_bare_lookup_alias_resolves_to_get():
    result = runner.invoke(app, ["pokemon", "pikachu", "--help"])
    assert result.exit_code == 0
    output = _strip_ansi(result.stdout)
    assert "Usage: pokecli pokemon get" in output or "Usage: root pokemon get" in output


def test_move_bare_lookup_alias_resolves_to_get():
    result = runner.invoke(app, ["move", "thunderbolt", "--help"])
    assert result.exit_code == 0
    output = _strip_ansi(result.stdout)
    assert "Usage: pokecli move get" in output or "Usage: root move get" in output
