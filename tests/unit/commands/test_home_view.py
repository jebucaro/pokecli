from typer.testing import CliRunner

from pokecli.main import app

runner = CliRunner()


def test_no_args_shows_home_view():
    """Running pokecli with no arguments shows live dashboard, not help."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "pokecli" in result.output
    assert "bin:" in result.output
    assert "Quick start" in result.output
    # Should NOT show the standard help format
    assert "Usage:" not in result.output


def test_help_flag_still_works():
    """--help should still show standard help text."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output or "usage" in result.output.lower()


def test_home_view_shows_cache_info():
    """Home view includes cache information."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Cache" in result.output or "cache" in result.output
