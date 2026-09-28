"""Tests for output format resolution.

Format resolution has exactly two levels: an explicit ``--format`` wins,
otherwise the execution context decides. Automated callers get ``toon`` with no
flag, which is why the shipped agent skill no longer instructs one.
"""

import json

import pytest
import typer
from typer.testing import CliRunner

from pokecli.commands import _format
from pokecli.commands._format import (
    FORMATS,
    resolve_format,
    stdout_is_interactive,
    validate_format,
)
from pokecli.main import app

from .conftest import StubClient, strip_ansi
from .payloads import BY_RESOURCE

runner = CliRunner()


class _FakeStdout:
    def __init__(self, interactive: bool):
        self._interactive = interactive

    def isatty(self) -> bool:
        return self._interactive


# --------------------------------------------------------------------------
# detection
# --------------------------------------------------------------------------


def test_detects_an_interactive_terminal(monkeypatch):
    monkeypatch.setattr(_format.sys, "stdout", _FakeStdout(True))
    assert stdout_is_interactive() is True


def test_detects_a_non_interactive_stream(monkeypatch):
    monkeypatch.setattr(_format.sys, "stdout", _FakeStdout(False))
    assert stdout_is_interactive() is False


def test_a_stream_without_isatty_counts_as_non_interactive(monkeypatch):
    monkeypatch.setattr(_format.sys, "stdout", object())
    assert stdout_is_interactive() is False


def test_a_closed_stream_counts_as_non_interactive(monkeypatch):
    class Closed:
        def isatty(self):
            raise ValueError("I/O operation on closed file")

    monkeypatch.setattr(_format.sys, "stdout", Closed())
    assert stdout_is_interactive() is False


# --------------------------------------------------------------------------
# resolution
# --------------------------------------------------------------------------


def test_interactive_defaults_to_table(monkeypatch):
    monkeypatch.setattr(_format, "stdout_is_interactive", lambda: True)
    assert resolve_format(None) == "table"


def test_non_interactive_defaults_to_toon(monkeypatch):
    monkeypatch.setattr(_format, "stdout_is_interactive", lambda: False)
    assert resolve_format(None) == "toon"


@pytest.mark.parametrize("fmt", FORMATS)
@pytest.mark.parametrize("interactive", [True, False])
def test_explicit_format_always_wins(fmt, interactive, monkeypatch):
    monkeypatch.setattr(_format, "stdout_is_interactive", lambda: interactive)
    assert resolve_format(fmt) == fmt


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------


def test_validate_accepts_each_supported_format():
    for fmt in FORMATS:
        assert validate_format(fmt) == fmt


def test_validate_passes_none_through():
    assert validate_format(None) is None


def test_validate_rejects_an_unknown_format_naming_all_three():
    with pytest.raises(typer.BadParameter) as excinfo:
        validate_format("yaml")
    message = str(excinfo.value)
    for fmt in FORMATS:
        assert fmt in message


def test_only_three_formats_are_supported():
    assert FORMATS == ("table", "toon", "json")


# --------------------------------------------------------------------------
# end to end
# --------------------------------------------------------------------------


def test_piped_invocation_renders_toon(install_client):
    """CliRunner is not a TTY, which is the automated-caller case."""
    install_client(StubClient(resources={"pokemon": BY_RESOURCE["pokemon"]}))
    result = runner.invoke(app, ["get", "pokemon", "pikachu"])
    assert result.exit_code == 0
    assert result.output.startswith("pokemon:")
    assert "\x1b[" not in result.output


def test_interactive_invocation_renders_table(install_client, monkeypatch):
    install_client(StubClient(resources={"pokemon": BY_RESOURCE["pokemon"]}))
    monkeypatch.setattr(_format, "stdout_is_interactive", lambda: True)
    result = runner.invoke(app, ["get", "pokemon", "pikachu"])
    assert result.exit_code == 0
    assert not result.output.startswith("pokemon:")
    assert "Pikachu" in strip_ansi(result.output)


def test_explicit_json_overrides_the_non_interactive_default(install_client):
    install_client(StubClient(resources={"pokemon": BY_RESOURCE["pokemon"]}))
    result = runner.invoke(app, ["get", "pokemon", "pikachu", "--format", "json"])
    assert result.exit_code == 0
    payload = json.loads(strip_ansi(result.output))
    assert payload["name"] == "pikachu"


def test_invalid_format_is_rejected_end_to_end(install_client):
    install_client(StubClient(resources={"type": BY_RESOURCE["type"]}))
    result = runner.invoke(app, ["get", "type", "fire", "--format", "yaml"])
    assert result.exit_code != 0
    output = strip_ansi(result.output).replace("\n", " ")
    for fmt in FORMATS:
        assert fmt in output


# --------------------------------------------------------------------------
# JSON stays parseable
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        ["get", "pokemon", "pikachu"],
        ["moves", "pikachu"],
        ["encounters", "pikachu"],
        ["forms", "pikachu"],
    ],
)
def test_json_output_parses_and_carries_no_hints(argv, install_client):
    install_client(
        StubClient(
            resources={
                "pokemon": BY_RESOURCE["pokemon"],
                "pokemon-species": BY_RESOURCE["pokemon-species"],
            },
            subresources={"encounters": []},
        )
    )
    result = runner.invoke(app, [*argv, "--format", "json"])
    assert result.exit_code == 0, result.output
    text = strip_ansi(result.output)
    payload = json.loads(text)
    assert "help" not in payload
    assert "Next steps" not in text
    assert "pokecli " not in text


def test_json_output_is_not_truncated_at_the_console_width(install_client):
    """Regression: Rich's Syntax renderer truncated every line at 80 columns,
    silently corrupting long values such as sprite URLs into invalid JSON."""
    long_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/" + "x" * 200
    payload = {
        **BY_RESOURCE["pokemon"],
        "sprites": {"front_default": long_url},
    }
    install_client(StubClient(resources={"pokemon": payload}))
    result = runner.invoke(
        app, ["get", "pokemon", "pikachu", "--format", "json"], env={"COLUMNS": "80"}
    )
    assert result.exit_code == 0, result.output
    decoded = json.loads(strip_ansi(result.output))
    assert decoded["sprites"]["front_default"] == long_url


def test_json_output_has_no_ansi_escapes(install_client):
    install_client(StubClient(resources={"pokemon": BY_RESOURCE["pokemon"]}))
    result = runner.invoke(app, ["get", "pokemon", "pikachu", "--format", "json"])
    assert "\x1b[" not in result.output
