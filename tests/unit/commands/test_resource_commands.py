"""Tests for the generic `get`, `list`, and `search` handlers."""

import pytest
from typer.testing import CliRunner

from pokecli.main import app
from pokecli.resources import RESOURCE_NAMES, RESOURCES

from .conftest import StubClient, network_error_client, strip_ansi
from .payloads import BY_RESOURCE

runner = CliRunner()


# --------------------------------------------------------------------------
# get
# --------------------------------------------------------------------------


@pytest.mark.parametrize("resource", RESOURCE_NAMES)
def test_get_renders_every_resource(resource, install_client):
    """One handler serves all eighteen resources; none may be special-cased."""
    install_client(StubClient(resources={resource: BY_RESOURCE[resource]}))
    result = runner.invoke(app, ["get", resource, "1"])
    assert result.exit_code == 0, result.output
    assert result.output.strip()


@pytest.mark.parametrize("resource", RESOURCE_NAMES)
@pytest.mark.parametrize("fmt", ["table", "toon", "json"])
def test_get_supports_every_format(resource, fmt, install_client):
    install_client(StubClient(resources={resource: BY_RESOURCE[resource]}))
    result = runner.invoke(app, ["get", resource, "1", "--format", fmt])
    assert result.exit_code == 0, result.output


def test_get_by_numeric_id(install_client):
    client = install_client(StubClient(resources={"pokemon": BY_RESOURCE["pokemon"]}))
    result = runner.invoke(app, ["get", "pokemon", "25", "--format", "toon"])
    assert result.exit_code == 0
    assert "pikachu" in result.output
    assert client.get_calls == [("pokemon", "25")]


def test_get_lowercases_supplied_name(install_client):
    client = install_client(StubClient(resources={"move": BY_RESOURCE["move"]}))
    result = runner.invoke(app, ["get", "move", "Thunderbolt", "--format", "toon"])
    assert result.exit_code == 0
    assert client.get_calls == [("move", "thunderbolt")]


def test_get_converts_spaces_to_hyphens(install_client):
    client = install_client(StubClient(resources={"item": BY_RESOURCE["item"]}))
    result = runner.invoke(app, ["get", "item", "master ball", "--format", "toon"])
    assert result.exit_code == 0
    assert client.get_calls == [("item", "master-ball")]


def test_get_not_found_exits_1_with_empty_stdout(install_client):
    install_client(StubClient(resources={}))
    result = runner.invoke(app, ["get", "pokemon", "notapokemon"])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "Not found" in strip_ansi(result.stderr)


def test_get_network_error_exits_1(install_client):
    install_client(network_error_client())
    result = runner.invoke(app, ["get", "pokemon", "pikachu"])
    assert result.exit_code == 1
    assert "Network error" in strip_ansi(result.stderr)


def test_get_unexpected_shape_exits_2(install_client):
    install_client(StubClient(resources={"pokemon": {"id": 1}}))
    result = runner.invoke(app, ["get", "pokemon", "pikachu"])
    assert result.exit_code == 2
    assert "Unexpected API response format" in strip_ansi(result.stderr)


def test_get_invalid_resource_lists_every_accepted_value(install_client):
    install_client(StubClient())
    result = runner.invoke(app, ["get", "natrue", "modest"])
    assert result.exit_code != 0
    output = strip_ansi(result.output).replace("\n", " ")
    for name in RESOURCE_NAMES:
        assert name in output


def test_get_rejects_resources_as_a_resource(install_client):
    """`resources` names no PokeAPI resource, for `get` as for `list`."""
    install_client(StubClient())
    result = runner.invoke(app, ["get", "resources", "1"])
    assert result.exit_code != 0


# --------------------------------------------------------------------------
# caching
# --------------------------------------------------------------------------


def test_second_identical_get_is_served_from_cache(install_client):
    client = install_client(StubClient(resources={"pokemon": BY_RESOURCE["pokemon"]}))
    for _ in range(2):
        result = runner.invoke(app, ["get", "pokemon", "pikachu", "--format", "toon"])
        assert result.exit_code == 0
    assert len(client.get_calls) == 1


def test_no_cache_forces_a_fresh_fetch(install_client):
    client = install_client(StubClient(resources={"pokemon": BY_RESOURCE["pokemon"]}))
    runner.invoke(app, ["get", "pokemon", "pikachu", "--format", "toon"])
    runner.invoke(app, ["get", "pokemon", "pikachu", "--format", "toon", "--no-cache"])
    assert len(client.get_calls) == 2


# --------------------------------------------------------------------------
# list
# --------------------------------------------------------------------------


@pytest.mark.parametrize("resource", RESOURCE_NAMES)
def test_list_works_for_every_resource(resource, install_client):
    install_client(StubClient())
    result = runner.invoke(app, ["list", resource, "--format", "toon"])
    assert result.exit_code == 0, result.output
    assert "count:" in result.output


def test_list_honors_limit_and_offset(install_client):
    client = install_client(StubClient())
    result = runner.invoke(
        app, ["list", "move", "--limit", "5", "--offset", "10", "--format", "toon"]
    )
    assert result.exit_code == 0
    assert client.list_calls == [("move", 5, 10)]
    assert "count: 5 of" in result.output
    assert "move-11" in result.output
    assert "move-16" not in result.output


def test_list_reports_total_count(install_client):
    install_client(StubClient())
    result = runner.invoke(app, ["list", "type", "--format", "toon"])
    assert "of 50 total" in result.output


def test_list_network_error_exits_1(install_client):
    install_client(network_error_client())
    result = runner.invoke(app, ["list", "pokemon"])
    assert result.exit_code == 1
    assert "Network error" in strip_ansi(result.stderr)


def test_list_of_a_nameless_resource_falls_back_to_ids(install_client):
    """PokeAPI's /machine/ entries carry only a URL; machines have no names."""
    install_client(StubClient())
    result = runner.invoke(app, ["list", "machine", "--limit", "3", "--format", "toon"])
    assert result.exit_code == 0, result.output
    assert "count: 3 of 50 total" in result.output
    for machine_id in ("1", "2", "3"):
        assert machine_id in result.output


def test_nameless_list_hint_is_a_runnable_command(install_client):
    """The derived name must be an identifier `get` accepts."""
    install_client(StubClient())
    result = runner.invoke(app, ["list", "machine", "--limit", "1", "--format", "toon"])
    assert result.exit_code == 0
    assert "pokecli get machine 1" in result.output


def test_search_of_a_nameless_resource_matches_on_id(install_client):
    install_client(StubClient())
    result = runner.invoke(app, ["search", "machine", "7", "--format", "toon"])
    assert result.exit_code == 0, result.output
    assert "7" in result.output


def test_malformed_list_response_exits_2(install_client):
    install_client(StubClient(lists={"pokemon": {"unexpected": True}}))
    result = runner.invoke(app, ["list", "pokemon"])
    assert result.exit_code == 2
    assert "Unexpected API response format" in strip_ansi(result.stderr)


# --------------------------------------------------------------------------
# help - the resource vocabulary
# --------------------------------------------------------------------------


def _help_lines(command: str) -> list[str]:
    result = runner.invoke(app, [command, "--help"], env={"COLUMNS": "200"})
    assert result.exit_code == 0
    return strip_ansi(result.output).splitlines()


def _panel_index(lines: list[str], title: str) -> int:
    return next(i for i, line in enumerate(lines) if line.startswith(f"╭─ {title} "))


def _resource_rows(lines: list[str]) -> list[list[str]]:
    start = _panel_index(lines, "Resources") + 1
    end = next(i for i in range(start, len(lines)) if lines[i].startswith("╰"))
    return [line.strip("│ ").split(maxsplit=1) for line in lines[start:end]]


@pytest.mark.parametrize("command", ["get", "list", "search"])
def test_help_ends_with_a_resources_panel_listing_each_purpose_beside_its_name(command):
    lines = _help_lines(command)
    assert _panel_index(lines, "Resources") > _panel_index(lines, "Options")
    assert _resource_rows(lines) == [[r.name, r.purpose] for r in RESOURCES]


def test_list_and_search_help_match_get_help():
    expected = _resource_rows(_help_lines("get"))
    assert _resource_rows(_help_lines("list")) == expected
    assert _resource_rows(_help_lines("search")) == expected


@pytest.mark.parametrize("command", ["get", "list", "search"])
def test_help_does_not_point_at_another_command_for_resources(command):
    output = "\n".join(_help_lines(command))
    assert "list resources" not in output


# --------------------------------------------------------------------------
# list resources - removed; `resources` is not a resource
# --------------------------------------------------------------------------


def test_list_resources_is_rejected_like_any_unknown_resource(install_client):
    client = install_client(StubClient())
    result = runner.invoke(app, ["list", "resources"], env={"COLUMNS": "200"})
    assert result.exit_code != 0
    output = strip_ansi(result.output)
    assert "'resources' is not a valid resource" in output
    for name in RESOURCE_NAMES:
        assert name in output
    assert client.list_calls == []


# --------------------------------------------------------------------------
# search
# --------------------------------------------------------------------------


def test_search_matches_substring(install_client):
    install_client(
        StubClient(
            lists={
                "pokemon": _index(
                    ["charmander", "charmeleon", "charizard", "pikachu"]
                )
            }
        )
    )
    result = runner.invoke(app, ["search", "pokemon", "char", "--format", "toon"])
    assert result.exit_code == 0
    assert "charmander" in result.output
    assert "charmeleon" in result.output
    assert "charizard" in result.output
    assert "pikachu" not in result.output
    assert "count: 3 of 4 total" in result.output


def test_search_is_case_insensitive(install_client):
    install_client(
        StubClient(lists={"pokemon": _index(["charmander", "charizard", "pikachu"])})
    )
    result = runner.invoke(app, ["search", "pokemon", "CHAR", "--format", "toon"])
    assert result.exit_code == 0
    assert "charmander" in result.output
    assert "charizard" in result.output


def test_search_with_no_matches_reports_zero_and_exits_0(install_client):
    install_client(StubClient(lists={"move": _index(["tackle", "growl"])}))
    result = runner.invoke(app, ["search", "move", "zzzz", "--format", "toon"])
    assert result.exit_code == 0
    assert "count: 0 of 2 total" in result.output
    assert "zzzz" in result.output


def test_search_index_is_cached_across_invocations(install_client):
    client = install_client(StubClient(lists={"item": _index(["poke-ball"])}))
    runner.invoke(app, ["search", "item", "ball", "--format", "toon"])
    runner.invoke(app, ["search", "item", "poke", "--format", "toon"])
    assert len(client.list_calls) == 1


def test_search_no_cache_refetches_the_index(install_client):
    client = install_client(StubClient(lists={"item": _index(["poke-ball"])}))
    runner.invoke(app, ["search", "item", "ball", "--format", "toon"])
    runner.invoke(app, ["search", "item", "ball", "--format", "toon", "--no-cache"])
    assert len(client.list_calls) == 2


def test_cache_clear_forces_the_index_to_be_refetched(install_client):
    client = install_client(StubClient(lists={"item": _index(["poke-ball"])}))
    runner.invoke(app, ["search", "item", "ball", "--format", "toon"])
    assert len(client.list_calls) == 1
    assert runner.invoke(app, ["cache", "clear", "--resource", "item"]).exit_code == 0
    runner.invoke(app, ["search", "item", "ball", "--format", "toon"])
    assert len(client.list_calls) == 2


@pytest.mark.parametrize("fmt", ["table", "toon", "json"])
def test_search_supports_every_format(fmt, install_client):
    install_client(StubClient(lists={"berry": _index(["cheri", "chesto"])}))
    result = runner.invoke(app, ["search", "berry", "che", "--format", fmt])
    assert result.exit_code == 0


def test_search_invalid_resource_is_rejected(install_client):
    install_client(StubClient())
    result = runner.invoke(app, ["search", "resources", "x"])
    assert result.exit_code != 0


# --------------------------------------------------------------------------
# completion
# --------------------------------------------------------------------------


def test_resource_completion_returns_every_name():
    from pokecli.commands.resource_cmds import complete_resource

    assert set(complete_resource("")) == set(RESOURCE_NAMES)


def test_resource_completion_filters_on_prefix():
    from pokecli.commands.resource_cmds import complete_resource

    assert set(complete_resource("pokemon")) == {
        "pokemon",
        "pokemon-species",
        "pokemon-form",
    }
    assert complete_resource("vers") == ["version", "version-group"]


def test_list_completion_offers_only_resources():
    """`list` shares `get`'s completion; `resources` is no longer offered."""
    from pokecli.commands.resource_cmds import complete_resource

    assert complete_resource("reso") == []
    assert list(complete_resource("")) == list(RESOURCE_NAMES)


def _index(names: list[str]) -> dict:
    return {
        "count": len(names),
        "next": None,
        "previous": None,
        "results": [
            {"name": n, "url": f"https://x/api/v2/x/{i + 1}/"}
            for i, n in enumerate(names)
        ],
    }
