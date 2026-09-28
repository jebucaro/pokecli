"""The bare-invocation orientation view.

It follows the same context-dependent default as every other output: readable in
a terminal, machine-readable when piped. Its quick-start examples are the first
commands a new user copies, so every one must resolve to a real command.
"""

import json

import typer.main
from typer.testing import CliRunner

from pokecli.commands import _format
from pokecli.main import DESCRIPTION, QUICK_START, QUICK_START_EXAMPLES, app
from pokecli.resources import RESOURCE_NAMES

from .conftest import strip_ansi

runner = CliRunner()


def _interactive(monkeypatch):
    monkeypatch.setattr(_format, "stdout_is_interactive", lambda: True)


# --------------------------------------------------------------------------
# interactive rendering
# --------------------------------------------------------------------------


def test_terminal_shows_a_readable_orientation_view(monkeypatch):
    _interactive(monkeypatch)
    result = runner.invoke(app, [], env={"COLUMNS": "200"})
    assert result.exit_code == 0
    output = strip_ansi(result.output)
    assert "pokecli" in output
    assert "bin:" in output
    assert "Quick start" in output
    assert "Cache" in output
    assert "Usage:" not in output


def test_terminal_view_is_visually_structured(monkeypatch):
    """It should use the same panel-and-table language as the record renderers,
    not a flat list of plain lines."""
    _interactive(monkeypatch)
    result = runner.invoke(app, [], env={"COLUMNS": "200"})
    output = strip_ansi(result.output)
    assert any(char in output for char in "╭─╰"), "expected a panel border"


def test_terminal_view_reports_the_installed_version(monkeypatch):
    from pokecli.main import _version

    _interactive(monkeypatch)
    result = runner.invoke(app, [], env={"COLUMNS": "200"})
    assert _version() in strip_ansi(result.output)


def test_terminal_view_pairs_each_example_with_its_purpose(monkeypatch):
    _interactive(monkeypatch)
    result = runner.invoke(app, [], env={"COLUMNS": "200"})
    output = strip_ansi(result.output)
    for command, purpose in QUICK_START_EXAMPLES:
        assert command in output
        assert purpose in output


def test_terminal_view_points_at_the_resource_help(monkeypatch):
    _interactive(monkeypatch)
    result = runner.invoke(app, [], env={"COLUMNS": "200"})
    output = strip_ansi(result.output)
    assert "pokecli get --help" in output
    assert "pokecli --help" in output


def test_empty_cache_is_reported_in_the_terminal_view(monkeypatch):
    _interactive(monkeypatch)
    result = runner.invoke(app, [], env={"COLUMNS": "200"})
    output = strip_ansi(result.output)
    assert "Cache" in output
    assert "empty" in output or "entries" in output


def test_terminal_view_prints_every_quick_start_example(monkeypatch):
    _interactive(monkeypatch)
    result = runner.invoke(app, [], env={"COLUMNS": "200"})
    output = strip_ansi(result.output)
    for example in QUICK_START:
        assert example in output


# --------------------------------------------------------------------------
# piped rendering
# --------------------------------------------------------------------------


def test_piped_view_is_machine_readable():
    """CliRunner is not a TTY, which is the automated-caller case."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert result.output.startswith("pokecli:")
    assert "\x1b[" not in result.output
    assert "[bold" not in result.output


def test_piped_view_reports_version_bin_and_cache_total():
    from pokecli.main import _version

    result = runner.invoke(app, [])
    assert "bin:" in result.output
    assert "cache_entries:" in result.output
    assert f"version: {_version()}" in result.output


def test_piped_view_lists_quick_start_examples():
    result = runner.invoke(app, [])
    assert "quick_start" in result.output
    for example in QUICK_START:
        assert example in result.output


def test_piped_view_reports_the_description():
    result = runner.invoke(app, [])
    assert DESCRIPTION in result.output


def test_piped_view_uses_no_box_drawing_characters():
    result = runner.invoke(app, [])
    for char in "─━│┏┡╭╰":
        assert char not in result.output


def test_empty_cache_reports_zero_rather_than_omitting_the_field():
    result = runner.invoke(app, [])
    assert "cache_entries: 0" in result.output


# --------------------------------------------------------------------------
# shared
# --------------------------------------------------------------------------


def test_help_flag_still_works():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in strip_ansi(result.output)


def test_no_view_or_root_help_mentions_the_removed_list_resources(monkeypatch):
    """`list resources` was removed; neither entry point may still advertise it."""
    piped = runner.invoke(app, [])
    root_help = runner.invoke(app, ["--help"], env={"COLUMNS": "200"})
    _interactive(monkeypatch)
    terminal = runner.invoke(app, [], env={"COLUMNS": "200"})
    for result in (piped, root_help, terminal):
        assert result.exit_code == 0
        assert "list resources" not in strip_ansi(result.output)


def test_no_format_option_at_root():
    """A root-level --format would be ambiguous with the subcommand option."""
    result = runner.invoke(app, ["--format", "toon"])
    assert result.exit_code != 0


def test_every_printed_example_resolves_to_a_real_command():
    """Guards against the drift that left `pokecli nature <name>` documented but broken."""
    registered = typer.main.get_command(app).commands
    for example in QUICK_START:
        argv = example.split()
        assert argv[0] == "pokecli", example
        assert argv[1] in registered, f"{example} names an unregistered command"
        if argv[1] in {"get", "list", "search"}:
            assert argv[2] in RESOURCE_NAMES, example


def test_examples_use_no_removed_addressing_scheme():
    removed_first_args = {
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
    }
    for example in QUICK_START:
        assert example.split()[1] not in removed_first_args, example


def test_a_broken_cache_does_not_break_the_view(monkeypatch):
    """The view is an orientation aid; an unreadable cache must not fail it."""
    import sys

    def boom(*_args, **_kwargs):
        raise OSError("cache unreadable")

    # `pokecli.main` cannot be used as a string target: `pokecli/__init__`
    # defines a `main()` function that shadows the submodule attribute.
    monkeypatch.setattr(sys.modules["pokecli.main"], "CacheStore", boom)
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "quick_start" in result.output


def test_piped_view_is_valid_toon():
    """Round-trips through a TOON-shaped assertion: keys are colon-delimited."""
    result = runner.invoke(app, [])
    first_lines = [
        line for line in result.output.splitlines() if line and not line.startswith(" ")
    ]
    assert first_lines[0] == "pokecli:"
    assert any(line.startswith("quick_start") for line in first_lines)


def test_json_is_not_offered_for_the_orientation_view():
    """It is an orientation aid, not a record; only two renderings exist."""
    result = runner.invoke(app, [])
    try:
        json.loads(result.output)
    except json.JSONDecodeError:
        return
    raise AssertionError("orientation view unexpectedly emitted JSON")
