"""Smoke tests for pokemon encounters/forms sub-commands wiring."""

from typer.testing import CliRunner

from pokecli.main import app

runner = CliRunner()


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
    assert "name_or_id" in result.stdout.lower() or "NAME_OR_ID" in result.stdout
    assert "--no-cache" in result.stdout


def test_pokemon_forms_help():
    result = runner.invoke(app, ["pokemon", "forms", "--help"])
    assert result.exit_code == 0
    assert "--no-cache" in result.stdout
    assert "--format" in result.stdout


def test_pokemon_bare_lookup_alias_resolves_to_get():
    result = runner.invoke(app, ["pokemon", "pikachu", "--help"])
    assert result.exit_code == 0
    assert "Usage: pokecli pokemon get" in result.stdout or "Usage: root pokemon get" in result.stdout


def test_move_bare_lookup_alias_resolves_to_get():
    result = runner.invoke(app, ["move", "thunderbolt", "--help"])
    assert result.exit_code == 0
    assert "Usage: pokecli move get" in result.stdout or "Usage: root move get" in result.stdout
