"""The command surface contract.

Asserts the eleven top-level commands exist, and that every addressing scheme
the consolidation removed is now rejected. The removal assertions matter as much
as the presence ones: the point of the change was one path per behavior.
"""

import pytest
from typer.testing import CliRunner

from pokecli.main import QUICK_START, app
from pokecli.resources import RESOURCE_NAMES

from .conftest import strip_ansi

runner = CliRunner()

TOP_LEVEL_COMMANDS = [
    "get",
    "list",
    "search",
    "moves",
    "can-learn",
    "evolution",
    "encounters",
    "forms",
    "sprite",
    "cache",
    "install",
]


def _root_help() -> str:
    result = runner.invoke(app, ["--help"], env={"COLUMNS": "200"})
    assert result.exit_code == 0
    return strip_ansi(result.output)


def registered_command_names() -> set[str]:
    import typer.main

    click_app = typer.main.get_command(app)
    return set(click_app.commands)


# --------------------------------------------------------------------------
# what exists
# --------------------------------------------------------------------------


def test_exactly_eleven_top_level_commands():
    assert registered_command_names() == set(TOP_LEVEL_COMMANDS)


@pytest.mark.parametrize("command", TOP_LEVEL_COMMANDS)
def test_each_top_level_command_is_listed_in_help(command):
    assert command in _root_help()


@pytest.mark.parametrize("command", TOP_LEVEL_COMMANDS)
def test_each_top_level_command_has_help(command):
    result = runner.invoke(app, [command, "--help"])
    assert result.exit_code == 0, result.output


def test_cache_exposes_stats_and_clear():
    output = strip_ansi(runner.invoke(app, ["cache", "--help"]).output)
    assert "stats" in output
    assert "clear" in output


def test_get_takes_a_resource_and_an_identifier():
    output = strip_ansi(
        runner.invoke(app, ["get", "--help"], env={"COLUMNS": "200"}).output
    )
    assert "RESOURCE" in output
    assert "--no-cache" in output
    assert "--format" in output


def test_help_epilog_examples_use_canonical_paths():
    output = _root_help()
    assert "Examples:" in output
    for example in QUICK_START:
        assert example.replace("pokecli ", "") in output.replace("\n", " ") or (
            example in output.replace("\n", " ")
        )


@pytest.mark.parametrize("example", QUICK_START)
def test_every_quick_start_example_resolves_to_a_real_command(example):
    argv = example.split()
    assert argv[0] == "pokecli"
    assert argv[1] in TOP_LEVEL_COMMANDS
    if argv[1] in {"get", "list", "search"}:
        assert argv[2] in RESOURCE_NAMES


# --------------------------------------------------------------------------
# what was removed
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        # Bare-name shortcuts, formerly provided by ResourceGroup.
        ["pokemon", "pikachu"],
        ["move", "thunderbolt"],
        ["item", "master-ball"],
        ["ability", "intimidate"],
        ["type", "fire"],
        ["location", "pallet-town"],
        # Per-resource command groups.
        ["pokemon", "get", "pikachu"],
        ["move", "get", "thunderbolt"],
        ["type", "get", "fire"],
        ["nature", "get", "modest"],
        ["berry", "get", "oran"],
        # Hidden flat top-level groups.
        ["region", "get", "kanto"],
        ["generation", "get", "generation-i"],
        ["pokedex", "get", "national"],
        ["version", "get", "red"],
        ["version-group", "get", "red-blue"],
        ["machine", "get", "79"],
        ["location-area", "get", "kanto-route-1-area"],
        ["pokemon-form", "get", "charizard-mega-x"],
        ["evolution-chain", "get", "67"],
        # Nested groups.
        ["game", "region", "get", "kanto"],
        ["game", "machine", "get", "79"],
        ["location", "area", "get", "kanto-route-1-area"],
        ["pokemon", "form", "get", "charizard-mega-x"],
        ["pokemon", "evolution-chain", "get", "67"],
        # Duplicate task aliases.
        ["pokemon", "where", "pikachu"],
        ["pokemon", "evo", "eevee"],
        ["pokemon", "species", "pikachu"],
        ["pokemon", "moves", "pikachu"],
        ["pokemon", "can-learn", "pikachu", "thunderbolt"],
        ["pokemon", "image", "pikachu"],
        # Renamed commands.
        ["image", "download", "pokemon", "pikachu"],
    ],
)
def test_removed_command_paths_are_rejected(argv):
    result = runner.invoke(app, argv)
    assert result.exit_code != 0, f"{argv} should no longer be a valid command"


@pytest.mark.parametrize(
    "name",
    [
        "pokemon",
        "move",
        "item",
        "ability",
        "type",
        "nature",
        "berry",
        "location",
        "game",
        "image",
        "region",
        "generation",
        "pokedex",
        "version",
        "version-group",
        "machine",
        "location-area",
        "pokemon-form",
        "evolution-chain",
    ],
)
def test_removed_groups_are_not_registered(name):
    assert name not in registered_command_names()


def test_resource_group_class_is_gone():
    with pytest.raises(ModuleNotFoundError):
        import pokecli.commands._group  # noqa: F401


@pytest.mark.parametrize(
    "module",
    [
        "ability",
        "berry",
        "evolution_chain",
        "game",
        "generation",
        "image",
        "item",
        "location",
        "location_area",
        "machine",
        "move",
        "nature",
        "pokedex",
        "pokemon",
        "pokemon_form",
        "region",
        "type",
        "version",
        "version_group",
    ],
)
def test_per_resource_command_modules_are_gone(module):
    with pytest.raises(ModuleNotFoundError):
        __import__(f"pokecli.commands.{module}")
