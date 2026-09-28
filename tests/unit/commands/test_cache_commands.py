"""Tests for the cache commands.

`cache stats` reports local state, so it is a data command and must honor
`--format` like any other. `cache clear` performs an action and is exempt.
"""

import json

import pytest
from typer.testing import CliRunner

from pokecli.cache.store import RESOURCE_TABLES
from pokecli.commands._format import FORMATS
from pokecli.commands.cache import complete_cache_resource
from pokecli.main import app

from .conftest import StubClient, strip_ansi
from .payloads import BY_RESOURCE

runner = CliRunner()

BOX_CHARS = "─━│┏┡╭╰┳┩╇"


def _populate(install_client) -> None:
    install_client(StubClient(resources={"pokemon": BY_RESOURCE["pokemon"]}))
    assert runner.invoke(app, ["get", "pokemon", "pikachu"]).exit_code == 0


# --------------------------------------------------------------------------
# stats honors the format
# --------------------------------------------------------------------------


@pytest.mark.parametrize("fmt", FORMATS)
def test_stats_supports_every_format(fmt, install_client):
    _populate(install_client)
    result = runner.invoke(app, ["cache", "stats", "--format", fmt])
    assert result.exit_code == 0, result.output


def test_stats_rejects_an_unknown_format(install_client):
    _populate(install_client)
    result = runner.invoke(app, ["cache", "stats", "--format", "yaml"])
    assert result.exit_code != 0
    output = strip_ansi(result.output).replace("\n", " ")
    for fmt in FORMATS:
        assert fmt in output


def test_piped_stats_carries_no_styling_or_box_characters(install_client):
    """Regression: this emitted a Rich table with box drawing even when piped."""
    _populate(install_client)
    result = runner.invoke(app, ["cache", "stats"])
    assert result.exit_code == 0
    assert "\x1b[" not in result.output
    for char in BOX_CHARS:
        assert char not in result.output, f"box character {char!r} in piped output"


def test_piped_stats_reports_the_total_and_populated_resources(install_client):
    _populate(install_client)
    result = runner.invoke(app, ["cache", "stats"])
    assert "total: 1" in result.output
    assert "pokemon,1" in result.output


def test_piped_stats_omits_empty_resources(install_client):
    _populate(install_client)
    result = runner.invoke(app, ["cache", "stats"])
    assert "berry" not in result.output


def test_empty_cache_reports_a_zero_total(install_client):
    install_client(StubClient())
    result = runner.invoke(app, ["cache", "stats"])
    assert result.exit_code == 0
    assert "total: 0" in result.output
    assert "Cache is empty" in result.output


def test_stats_json_parses_and_covers_every_table(install_client):
    _populate(install_client)
    result = runner.invoke(app, ["cache", "stats", "--format", "json"])
    payload = json.loads(strip_ansi(result.output))
    assert payload["total"] == 1
    assert set(payload["resources"]) == set(RESOURCE_TABLES)
    assert payload["resources"]["pokemon"] == 1


def test_stats_table_shows_a_total_row(install_client, monkeypatch):
    from pokecli.commands import _format

    monkeypatch.setattr(_format, "stdout_is_interactive", lambda: True)
    _populate(install_client)
    result = runner.invoke(app, ["cache", "stats"], env={"COLUMNS": "200"})
    output = strip_ansi(result.output)
    assert "Cache Statistics" in output
    assert "Total" in output


# --------------------------------------------------------------------------
# clear
# --------------------------------------------------------------------------


def test_clear_removes_everything(install_client):
    _populate(install_client)
    assert runner.invoke(app, ["cache", "clear"]).exit_code == 0
    result = runner.invoke(app, ["cache", "stats"])
    assert "total: 0" in result.output


def test_clear_narrows_to_one_resource(install_client):
    _populate(install_client)
    result = runner.invoke(app, ["cache", "clear", "--resource", "pokemon"])
    assert result.exit_code == 0
    assert "total: 0" in runner.invoke(app, ["cache", "stats"]).output


def test_clear_leaves_other_resources_alone(install_client):
    install_client(
        StubClient(
            resources={
                "pokemon": BY_RESOURCE["pokemon"],
                "move": BY_RESOURCE["move"],
            }
        )
    )
    runner.invoke(app, ["get", "pokemon", "pikachu"])
    runner.invoke(app, ["get", "move", "thunderbolt"])
    runner.invoke(app, ["cache", "clear", "--resource", "pokemon"])
    stats = runner.invoke(app, ["cache", "stats"]).output
    assert "move,1" in stats
    assert "pokemon,1" not in stats


def test_clear_rejects_an_unknown_resource(install_client):
    install_client(StubClient())
    result = runner.invoke(app, ["cache", "clear", "--resource", "natrue"])
    assert result.exit_code == 1
    assert "Invalid resource" in strip_ansi(result.stderr)


def test_clear_has_no_format_option(install_client):
    """It performs an action and reports the outcome; it returns no data."""
    install_client(StubClient())
    result = runner.invoke(app, ["cache", "clear", "--format", "toon"])
    assert result.exit_code != 0


# --------------------------------------------------------------------------
# completion
# --------------------------------------------------------------------------


def test_cache_resource_completion_covers_every_table_plus_all():
    completions = complete_cache_resource("")
    assert set(completions) == {*RESOURCE_TABLES, "all"}


def test_cache_resource_completion_filters_on_prefix():
    assert set(complete_cache_resource("pokemon")) == {
        "pokemon",
        "pokemon-species",
        "pokemon-form",
    }
