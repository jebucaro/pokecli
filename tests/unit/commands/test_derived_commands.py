"""Tests for the derived commands: moves, can-learn, evolution, encounters, forms.

Each joins or filters more than one response, so each is tested for its zero
result case as well as its happy path. `can-learn` is tested for its exit code,
which is the answer it returns.
"""

import json

import pytest
from typer.testing import CliRunner

from pokecli.main import app

from .conftest import StubClient, network_error_client, strip_ansi
from .payloads import (
    BY_RESOURCE,
    EVOLUTION_CHAIN,
    EVOLUTION_CHAIN_SINGLE,
    GYARADOS,
    LOCATION_AREA,
    POKEMON,
    POKEMON_NO_MOVES,
    POKEMON_SPECIES,
    POKEMON_SPECIES_DEFAULT_ONLY,
)

runner = CliRunner()

ENCOUNTERS = [
    {
        "location_area": {"name": "trophy-garden-area", "url": "https://x/1/"},
        "version_details": [
            {
                "version": {"name": "diamond", "url": "https://x/1/"},
                "max_chance": 5,
                "encounter_details": [
                    {
                        "min_level": 18,
                        "max_level": 18,
                        "chance": 5,
                        "method": {"name": "walk", "url": "https://x/1/"},
                        "condition_values": [],
                    }
                ],
            }
        ],
    }
]


def _client(**overrides) -> StubClient:
    resources = {
        "pokemon": POKEMON,
        "pokemon-species": POKEMON_SPECIES,
        "evolution-chain": EVOLUTION_CHAIN,
        "location-area": LOCATION_AREA,
    }
    resources.update(overrides.pop("resources", {}))
    return StubClient(
        resources=resources,
        subresources=overrides.pop("subresources", {"encounters": ENCOUNTERS}),
        **overrides,
    )


# --------------------------------------------------------------------------
# moves
# --------------------------------------------------------------------------


def test_moves_lists_learnable_moves_with_counts(install_client):
    install_client(_client())
    result = runner.invoke(app, ["moves", "pikachu", "--format", "toon"])
    assert result.exit_code == 0
    assert "thunderbolt" in result.output
    assert "thunder-shock" in result.output
    assert "count: 2" in result.output
    assert "machine:1" in result.output
    assert "level-up:1" in result.output


def test_moves_filters_by_learn_method(install_client):
    install_client(_client())
    result = runner.invoke(
        app, ["moves", "pikachu", "--method", "machine", "--format", "toon"]
    )
    assert result.exit_code == 0
    assert "thunderbolt" in result.output
    assert "thunder-shock" not in result.output
    assert "count: 1" in result.output


def test_moves_with_no_recorded_moves_reports_zero_and_exits_0(install_client):
    install_client(_client(resources={"pokemon": POKEMON_NO_MOVES}))
    result = runner.invoke(app, ["moves", "missingno", "--format", "toon"])
    assert result.exit_code == 0
    assert "count: 0" in result.output
    assert "No recorded moves" in result.output


def test_moves_with_no_matching_method_reports_zero_and_exits_0(install_client):
    install_client(_client())
    result = runner.invoke(
        app, ["moves", "pikachu", "--method", "egg", "--format", "toon"]
    )
    assert result.exit_code == 0
    assert "count: 0" in result.output
    assert "No egg moves found" in result.output


@pytest.mark.parametrize("fmt", ["table", "toon", "json"])
def test_moves_supports_every_format(fmt, install_client):
    install_client(_client())
    result = runner.invoke(app, ["moves", "pikachu", "--format", fmt])
    assert result.exit_code == 0


def test_moves_has_no_move_flag(install_client):
    """`--move` was superseded by can-learn; two ways to ask one question."""
    install_client(_client())
    result = runner.invoke(app, ["moves", "pikachu", "--move", "thunderbolt"])
    assert result.exit_code != 0


# --------------------------------------------------------------------------
# can-learn
# --------------------------------------------------------------------------


def test_can_learn_exits_0_and_reports_the_method(install_client):
    install_client(_client())
    result = runner.invoke(app, ["can-learn", "pikachu", "thunderbolt", "--format", "toon"])
    assert result.exit_code == 0
    assert "can_learn: true" in result.output
    assert "machine" in result.output


def test_can_learn_exits_1_when_not_learnable(install_client):
    install_client(_client())
    result = runner.invoke(app, ["can-learn", "pikachu", "fly", "--format", "toon"])
    assert result.exit_code == 1
    assert "can_learn: false" in result.output


def test_can_learn_exits_1_for_the_wrong_method(install_client):
    """Learnable, but not by the requested method, is still a no."""
    install_client(_client())
    result = runner.invoke(
        app,
        ["can-learn", "pikachu", "thunderbolt", "--method", "egg", "--format", "toon"],
    )
    assert result.exit_code == 1
    assert "can_learn: false" in result.output


def test_can_learn_normalizes_the_move_name(install_client):
    install_client(_client())
    result = runner.invoke(
        app, ["can-learn", "pikachu", "Thunder Shock", "--format", "toon"]
    )
    assert result.exit_code == 0
    assert "thunder-shock" in result.output


def test_can_learn_json_answers_with_a_boolean(install_client):
    install_client(_client())
    result = runner.invoke(
        app, ["can-learn", "pikachu", "thunderbolt", "--format", "json"]
    )
    assert result.exit_code == 0
    assert json.loads(strip_ansi(result.output))["can_learn"] is True


def test_can_learn_table_reports_a_negative_on_stderr(install_client):
    install_client(_client())
    result = runner.invoke(
        app, ["can-learn", "pikachu", "fly", "--format", "table"]
    )
    assert result.exit_code == 1
    assert "cannot learn" in strip_ansi(result.stderr)


# --------------------------------------------------------------------------
# evolution
# --------------------------------------------------------------------------


def test_evolution_resolves_the_chain_from_a_pokemon_name(install_client):
    install_client(_client())
    result = runner.invoke(app, ["evolution", "charmander", "--format", "toon"])
    assert result.exit_code == 0
    assert "charmander" in result.output
    assert "charmeleon" in result.output


def test_evolution_from_a_mid_chain_member_returns_the_whole_chain(install_client):
    """A mid-chain lookup must not truncate the stages before it."""
    install_client(_client())
    result = runner.invoke(app, ["evolution", "charmeleon", "--format", "toon"])
    assert result.exit_code == 0
    assert "charmander" in result.output
    assert "charmeleon" in result.output


def test_evolution_of_a_non_evolving_pokemon_exits_0(install_client):
    install_client(
        _client(resources={"evolution-chain": EVOLUTION_CHAIN_SINGLE})
    )
    result = runner.invoke(app, ["evolution", "tauros", "--format", "toon"])
    assert result.exit_code == 0
    assert "tauros" in result.output


def test_evolution_caches_the_chain(install_client):
    client = install_client(_client())
    runner.invoke(app, ["evolution", "charmander", "--format", "toon"])
    runner.invoke(app, ["evolution", "charmander", "--format", "toon"])
    assert len(client.url_calls) == 1


def test_evolution_unexpected_shape_exits_2(install_client):
    install_client(_client(resources={"evolution-chain": {"id": 1}}))
    result = runner.invoke(app, ["evolution", "charmander"])
    assert result.exit_code == 2


@pytest.mark.parametrize("fmt", ["table", "toon", "json"])
def test_evolution_supports_every_format(fmt, install_client):
    install_client(_client())
    result = runner.invoke(app, ["evolution", "charmander", "--format", fmt])
    assert result.exit_code == 0


# --------------------------------------------------------------------------
# encounters
# --------------------------------------------------------------------------


def test_encounters_reports_areas_and_a_count(install_client):
    install_client(_client())
    result = runner.invoke(app, ["encounters", "pikachu", "--format", "toon"])
    assert result.exit_code == 0
    assert "areas: 1" in result.output
    assert "trophy-garden-area" in result.output


def test_encounters_with_none_recorded_exits_0(install_client):
    install_client(_client(subresources={"encounters": []}))
    result = runner.invoke(app, ["encounters", "mewtwo", "--format", "toon"])
    assert result.exit_code == 0
    assert "areas: 0" in result.output
    assert "No recorded encounter locations" in result.output


def test_encounters_network_error_exits_1(install_client):
    class Failing(StubClient):
        def get_subresource(self, resource, identifier, sub):
            import httpx

            raise httpx.ConnectError("unreachable")

    install_client(Failing(resources={"pokemon": POKEMON}))
    result = runner.invoke(app, ["encounters", "pikachu"])
    assert result.exit_code == 1
    assert "Network error" in strip_ansi(result.stderr)


@pytest.mark.parametrize("fmt", ["table", "toon", "json"])
def test_encounters_supports_every_format(fmt, install_client):
    install_client(_client())
    result = runner.invoke(app, ["encounters", "pikachu", "--format", fmt])
    assert result.exit_code == 0


# --------------------------------------------------------------------------
# forms
# --------------------------------------------------------------------------


def test_forms_lists_varieties_marking_the_default(install_client):
    install_client(_client())
    result = runner.invoke(app, ["forms", "pikachu", "--format", "toon"])
    assert result.exit_code == 0
    assert "pikachu-gmax" in result.output
    assert "true" in result.output


def test_forms_with_only_a_default_variety_exits_0(install_client):
    install_client(
        _client(resources={"pokemon-species": POKEMON_SPECIES_DEFAULT_ONLY})
    )
    result = runner.invoke(app, ["forms", "tauros", "--format", "toon"])
    assert result.exit_code == 0
    assert "tauros" in result.output


@pytest.mark.parametrize("fmt", ["table", "toon", "json"])
def test_forms_supports_every_format(fmt, install_client):
    install_client(_client())
    result = runner.invoke(app, ["forms", "pikachu", "--format", fmt])
    assert result.exit_code == 0


# --------------------------------------------------------------------------
# shared behavior
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        ["moves", "pikachu"],
        ["can-learn", "pikachu", "thunderbolt"],
        ["evolution", "pikachu"],
        ["encounters", "pikachu"],
        ["forms", "pikachu"],
    ],
)
def test_derived_commands_report_a_missing_pokemon(argv, install_client):
    install_client(StubClient(resources={}))
    result = runner.invoke(app, argv)
    assert result.exit_code == 1
    assert "Not found" in strip_ansi(result.stderr)


@pytest.mark.parametrize(
    "argv",
    [
        ["moves", "pikachu"],
        ["evolution", "pikachu"],
        ["encounters", "pikachu"],
        ["forms", "pikachu"],
    ],
)
def test_derived_commands_accept_no_cache(argv, install_client):
    install_client(_client())
    result = runner.invoke(app, [*argv, "--no-cache", "--format", "toon"])
    assert result.exit_code == 0


def test_derived_commands_network_error_exits_1(install_client):
    install_client(network_error_client())
    result = runner.invoke(app, ["moves", "pikachu"])
    assert result.exit_code == 1


def test_all_resources_payload_fixture_is_complete():
    """Guards the fixture set the parametrized tests rely on."""
    from pokecli.resources import RESOURCE_NAMES

    assert set(BY_RESOURCE) == set(RESOURCE_NAMES)


# --------------------------------------------------------------------------
# --method validation
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        ["moves", "pikachu", "--method", "nope"],
        ["can-learn", "pikachu", "thunderbolt", "--method", "machin"],
    ],
    ids=["moves", "can-learn"],
)
def test_unknown_method_is_a_usage_error_not_an_answer(argv, install_client):
    """Exit 2, never can-learn's "no" (1) or an empty moves list (0)."""
    from pokecli.config import LEARN_METHODS

    client = install_client(_client())
    result = runner.invoke(app, argv, env={"COLUMNS": "200"})
    assert result.exit_code == 2
    output = strip_ansi(result.output)
    assert "is not a valid learn method" in output
    for method in LEARN_METHODS:
        assert method in output
    assert client.get_calls == []


def test_method_is_case_insensitive(install_client):
    install_client(_client())
    result = runner.invoke(
        app, ["moves", "pikachu", "--method", "Machine", "--format", "toon"]
    )
    assert result.exit_code == 0
    assert "thunderbolt" in result.output
    assert "count: 1" in result.output


# --------------------------------------------------------------------------
# learn-method recency
# --------------------------------------------------------------------------


def _detail(group: str, group_id: int, method: str, level: int) -> dict:
    return {
        "level_learned_at": level,
        "move_learn_method": {"name": method, "url": f"https://pokeapi.co/api/v2/move-learn-method/{method}/"},
        "version_group": {"name": group, "url": f"https://pokeapi.co/api/v2/version-group/{group_id}/"},
    }


def test_most_recent_learn_method_follows_release_order_not_id():
    """blue-japan (ID 29) is Gen I; scarlet-violet (ID 25) is newer."""
    from pokecli.commands.tasks import _extract_moves

    moves = _extract_moves(
        [
            {
                "move": {"name": "headbutt"},
                "version_group_details": [
                    _detail("scarlet-violet", 25, "level-up", 12),
                    _detail("blue-japan", 29, "machine", 0),
                ],
            }
        ]
    )
    assert [(m.name, m.learn_method, m.level) for m in moves] == [("headbutt", "level-up", 12)]


def test_unknown_version_group_is_treated_as_newest():
    from pokecli.commands.tasks import _extract_moves

    moves = _extract_moves(
        [
            {
                "move": {"name": "tackle"},
                "version_group_details": [
                    _detail("champions", 32, "level-up", 1),
                    _detail("some-future-game", 40, "tutor", 0),
                ],
            }
        ]
    )
    assert moves[0].learn_method == "tutor"


# --------------------------------------------------------------------------
# --game and method matching across games
# --------------------------------------------------------------------------


def test_extract_moves_matches_older_method_when_newest_differs():
    from pokecli.commands.tasks import _extract_moves

    moves = _extract_moves(GYARADOS["moves"], method="machine")
    assert {m.name for m in moves} == {"blizzard", "earthquake"}
    assert all(m.learn_method == "machine" for m in moves)


def test_extract_moves_without_filters_keeps_newest_detail():
    from pokecli.commands.tasks import _extract_moves

    by_name = {m.name: m for m in _extract_moves(GYARADOS["moves"])}
    assert by_name["blizzard"].learn_method == "train"
    assert by_name["bite"].level == 1


def test_extract_moves_limits_to_version_groups():
    from pokecli.commands.tasks import _extract_moves

    moves = _extract_moves(GYARADOS["moves"], version_groups=frozenset({"red-blue"}))
    by_name = {m.name: m for m in moves}
    assert set(by_name) == {"blizzard", "bite"}
    assert by_name["bite"].level == 20


def test_can_learn_by_machine_matches_an_older_game(install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(
        app, ["can-learn", "gyarados", "blizzard", "--method", "machine", "--format", "toon"]
    )
    assert result.exit_code == 0
    assert "method: machine" in result.output


@pytest.mark.parametrize("game", ["red", "red-blue", "Red Blue"])
def test_can_learn_in_game_accepts_version_or_group(game, install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(
        app,
        ["can-learn", "gyarados", "blizzard", "--method", "machine", "--game", game, "--format", "toon"],
    )
    assert result.exit_code == 0
    assert "game: " in result.output


def test_can_learn_answers_no_when_game_lacks_the_move(install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(
        app,
        ["can-learn", "gyarados", "earthquake", "--method", "machine", "--game", "red", "--format", "toon"],
    )
    assert result.exit_code == 1
    assert "can_learn: false" in result.output
    assert "game: red" in result.output


def test_moves_in_game_echoes_game_and_filters(install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(app, ["moves", "gyarados", "--game", "red", "--format", "toon"])
    assert result.exit_code == 0
    assert "game: red" in result.output
    assert "count: 2" in result.output
    assert "earthquake" not in result.output


def test_moves_normalizes_game_in_output(install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(app, ["moves", "gyarados", "--game", "Red Blue", "--format", "toon"])
    assert "game: red-blue" in result.output


def test_moves_empty_in_game_names_the_game(install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(
        app,
        ["moves", "gyarados", "--method", "egg", "--game", "red", "--format", "toon"],
    )
    assert result.exit_code == 0
    assert "count: 0" in result.output
    assert "No egg moves found in red" in result.output


def test_moves_empty_in_game_json_carries_game_and_zero(install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(
        app,
        ["moves", "gyarados", "--method", "egg", "--game", "red", "--format", "json"],
    )
    data = json.loads(result.output)
    assert data["game"] == "red"
    assert data["count"] == 0
    assert data["moves"] == []


def test_moves_json_in_game_carries_game(install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(app, ["moves", "gyarados", "--game", "red", "--format", "json"])
    data = json.loads(result.output)
    assert data["game"] == "red"
    assert {m["name"] for m in data["moves"]} == {"blizzard", "bite"}


@pytest.mark.parametrize("fmt", ["table", "toon", "json"])
def test_moves_and_can_learn_with_game_support_every_format(fmt, install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    assert runner.invoke(app, ["moves", "gyarados", "--game", "red", "--format", fmt]).exit_code == 0
    assert (
        runner.invoke(app, ["can-learn", "gyarados", "bite", "--game", "red", "--format", fmt]).exit_code
        == 0
    )


@pytest.mark.parametrize(
    "args",
    [
        ["moves", "gyarados", "--game", "rde"],
        ["can-learn", "gyarados", "blizzard", "--game", "rde"],
    ],
)
def test_unknown_game_exits_2(args, install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(app, args)
    assert result.exit_code == 2
    assert "not a known game" in strip_ansi(result.output)


def _encounter(area: str, version: str) -> dict:
    return {
        "location_area": {"name": area, "url": "https://x/1/"},
        "version_details": [
            {
                "version": {"name": version, "url": "https://x/1/"},
                "max_chance": 4,
                "encounter_details": [
                    {
                        "min_level": 4,
                        "max_level": 4,
                        "chance": 4,
                        "method": {"name": "walk", "url": "https://x/1/"},
                        "condition_values": [],
                    }
                ],
            }
        ],
    }


MULTI_GAME_ENCOUNTERS = [
    _encounter("hoenn-route-102-area", "ruby"),
    _encounter("sinnoh-route-203-area", "diamond"),
    _encounter("rolling-fields-area", "sword"),
    _encounter("fields-of-honor-area", "the-isle-of-armor-sword"),
]


def _multi_client():
    return _client(subresources={"encounters": MULTI_GAME_ENCOUNTERS})


def test_encounters_in_game_keeps_only_that_version(install_client):
    install_client(_multi_client())
    result = runner.invoke(app, ["encounters", "ralts", "--game", "ruby", "--format", "toon"])
    assert result.exit_code == 0
    assert "game: ruby" in result.output
    assert "areas: 1" in result.output
    assert "hoenn-route-102-area" in result.output
    assert "sinnoh-route-203-area" not in result.output


def test_encounters_in_group_keeps_its_versions(install_client):
    install_client(_multi_client())
    result = runner.invoke(
        app, ["encounters", "ralts", "--game", "ruby-sapphire", "--format", "json"]
    )
    data = json.loads(result.output)
    assert data["game"] == "ruby-sapphire"
    assert [e["location_area"]["name"] for e in data["encounters"]] == ["hoenn-route-102-area"]


def test_encounters_sword_excludes_dlc_versions(install_client):
    install_client(_multi_client())
    result = runner.invoke(app, ["encounters", "ralts", "--game", "sword", "--format", "toon"])
    assert "rolling-fields-area" in result.output
    assert "fields-of-honor-area" not in result.output


def test_encounters_empty_in_game_names_the_game(install_client):
    install_client(_multi_client())
    result = runner.invoke(app, ["encounters", "ralts", "--game", "red", "--format", "toon"])
    assert result.exit_code == 0
    assert "areas: 0" in result.output
    assert "No recorded encounter locations in red" in result.output


def test_encounters_without_game_is_unchanged(install_client):
    install_client(_multi_client())
    result = runner.invoke(app, ["encounters", "ralts", "--format", "toon"])
    assert "areas: 4" in result.output
    assert "game:" not in result.output


@pytest.mark.parametrize("fmt", ["table", "toon", "json"])
def test_encounters_with_game_supports_every_format(fmt, install_client):
    install_client(_multi_client())
    result = runner.invoke(app, ["encounters", "ralts", "--game", "ruby", "--format", fmt])
    assert result.exit_code == 0


def test_encounters_unknown_game_exits_2(install_client):
    install_client(_multi_client())
    result = runner.invoke(app, ["encounters", "ralts", "--game", "rde"])
    assert result.exit_code == 2
    assert "not a known game" in strip_ansi(result.output)


def test_can_learn_in_dlc_uses_base_game_learnset(install_client):
    base_only = {
        **GYARADOS,
        "moves": [
            {
                "move": {"name": "blizzard", "url": "https://x/api/v2/move/59/"},
                "version_group_details": [
                    {
                        "level_learned_at": 0,
                        "move_learn_method": {"name": "machine", "url": "https://x/1/"},
                        "version_group": {
                            "name": "sword-shield",
                            "url": "https://x/api/v2/version-group/20/",
                        },
                    }
                ],
            }
        ],
    }
    install_client(_client(resources={"pokemon": base_only}))
    result = runner.invoke(
        app,
        ["can-learn", "gyarados", "blizzard", "--game", "the-isle-of-armor-sword", "--format", "toon"],
    )
    assert result.exit_code == 0


def test_moves_hint_keeps_the_game(install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(app, ["moves", "gyarados", "--game", "red", "--format", "toon"])
    assert "pokecli can-learn gyarados <move_name> --game red" in result.output


def test_moves_in_game_without_learnset_data_says_so(install_client):
    """No detail at all for the game is missing data, not an empty filter."""
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(app, ["moves", "gyarados", "--game", "legends-za", "--format", "toon"])
    assert result.exit_code == 0
    assert "count: 0" in result.output
    assert "No learnset data for gyarados in legends-za" in result.output


@pytest.mark.parametrize("fmt", ["toon", "json"])
def test_can_learn_in_game_without_learnset_data_is_an_error_not_no(fmt, install_client):
    install_client(_client(resources={"pokemon": GYARADOS}))
    result = runner.invoke(
        app, ["can-learn", "gyarados", "blizzard", "--game", "legends-za", "--format", fmt]
    )
    assert result.exit_code == 1
    assert "can_learn" not in result.stdout
    assert "No learnset data for gyarados in legends-za" in strip_ansi(result.stderr)
