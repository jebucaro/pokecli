"""Tests for resolving `--game` into the groups and versions it covers."""

import pytest
import typer

from pokecli.commands._game import GameScope, resolve_game, validate_game


def test_version_resolves_to_its_group_and_itself():
    assert resolve_game("red") == GameScope(
        name="red",
        version_groups=frozenset({"red-blue"}),
        versions=frozenset({"red"}),
    )


def test_group_resolves_to_itself_and_its_versions():
    assert resolve_game("red-blue") == GameScope(
        name="red-blue",
        version_groups=frozenset({"red-blue"}),
        versions=frozenset({"red", "blue"}),
    )


def test_sword_does_not_reach_dlc_groups():
    scope = resolve_game("sword")
    assert scope.version_groups == frozenset({"sword-shield"})
    assert scope.versions == frozenset({"sword"})


@pytest.mark.parametrize("name", ["yellow", "platinum", "champions"])
def test_name_that_is_both_version_and_group_has_one_scope(name):
    scope = resolve_game(name)
    assert scope.version_groups == frozenset({name})
    assert scope.versions == frozenset({name})


def test_validate_normalizes_case_and_spaces():
    assert validate_game("Red Blue") == "red-blue"
    assert validate_game("  SWORD ") == "sword"


def test_validate_passes_none_through():
    assert validate_game(None) is None


def test_validate_rejects_unknown_game_naming_valid_values():
    with pytest.raises(typer.BadParameter) as exc:
        validate_game("rde")
    message = str(exc.value)
    assert "'rde' is not a known game" in message
    assert "red-blue" in message
    assert "red" in message


def test_game_help_mentions_both_forms():
    from pokecli.commands._helptext import GAME_FILTER

    assert "red-blue" in GAME_FILTER
    assert "red" in GAME_FILTER


@pytest.mark.parametrize(
    ("name", "base"),
    [
        ("the-isle-of-armor-sword", "sword-shield"),
        ("the-crown-tundra", "sword-shield"),
        ("the-teal-mask", "scarlet-violet"),
        ("the-indigo-disk-violet", "scarlet-violet"),
        ("mega-dimension", "legends-za"),
    ],
)
def test_dlc_learnsets_include_the_base_game(name, base):
    """PokeAPI stores DLC learnsets under the base game's group."""
    scope = resolve_game(name)
    assert base in scope.version_groups
    assert base not in scope.versions


def test_base_game_does_not_pull_in_dlc():
    assert resolve_game("sword-shield").version_groups == frozenset({"sword-shield"})
