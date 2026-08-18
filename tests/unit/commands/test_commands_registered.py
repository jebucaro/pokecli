"""Smoke tests confirming the grouped CLI surface is wired into the root app."""

import pytest
from typer.testing import CliRunner

from pokecli.main import app

runner = CliRunner()

ROOT_COMMANDS = [
    "pokemon",
    "ability",
    "move",
    "item",
    "type",
    "location",
    "game",
    "image",
    "cache",
]


def test_root_help_lists_primary_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ROOT_COMMANDS:
        assert cmd in result.stdout, f"missing '{cmd}' in root --help"
    assert "move-damage-class" not in result.stdout
    assert "pokemon-form" not in result.stdout


@pytest.mark.parametrize(
    ("cmd", "expected"),
    [
        ("move", ["get", "list"]),
        (
            "pokemon",
            ["get", "moves", "species", "evolution", "encounters", "form"],
        ),
        (
            "game",
            [
                "generation",
                "pokedex",
                "region",
                "version",
                "version-group",
                "machine",
            ],
        ),
        ("location", ["get", "list", "area"]),
    ],
)
def test_grouped_commands_expose_expected_subcommands(cmd, expected):
    result = runner.invoke(app, [cmd, "--help"])
    assert result.exit_code == 0, f"`{cmd} --help` failed: {result.output}"
    for subcommand in expected:
        assert subcommand in result.stdout


@pytest.mark.parametrize(
    "cmd",
    [
        ["region", "--help"],
        ["pokemon-form", "--help"],
    ],
)
def test_hidden_legacy_commands_still_work(cmd):
    result = runner.invoke(app, cmd)
    assert result.exit_code == 0, result.output


def test_root_help_includes_examples():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Examples:" in result.stdout
    assert "pokecli pokemon pikachu" in result.stdout
    assert "pokecli game region get kanto" in result.stdout
