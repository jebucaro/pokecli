"""Tests for the sprite command.

A failed download must leave no file behind, so the caller can distinguish
"not written" from "written empty".
"""

import pytest
from typer.testing import CliRunner

from pokecli.commands.sprite import SPRITE_VARIANTS, complete_variant
from pokecli.main import app

from .conftest import StubClient, strip_ansi
from .payloads import POKEMON

runner = CliRunner()


def test_downloads_the_default_variant(tmp_path, install_client):
    client = install_client(
        StubClient(resources={"pokemon": POKEMON}, image_bytes=b"IMAGEBYTES")
    )
    out = tmp_path / "pikachu.png"
    result = runner.invoke(app, ["sprite", "pikachu", "-o", str(out)])
    assert result.exit_code == 0, result.output
    assert out.read_bytes() == b"IMAGEBYTES"
    assert client.download_calls == ["https://img/25.png"]


def test_downloads_a_named_variant(tmp_path, install_client):
    client = install_client(
        StubClient(resources={"pokemon": POKEMON}, image_bytes=b"SHINY")
    )
    out = tmp_path / "shiny.png"
    result = runner.invoke(
        app, ["sprite", "pikachu", "-o", str(out), "--variant", "front_shiny"]
    )
    assert result.exit_code == 0, result.output
    assert out.read_bytes() == b"SHINY"
    assert client.download_calls == ["https://img/25s.png"]


def test_unavailable_variant_writes_no_file(tmp_path, install_client):
    """front_female is null on this payload."""
    install_client(StubClient(resources={"pokemon": POKEMON}))
    out = tmp_path / "female.png"
    result = runner.invoke(
        app, ["sprite", "pikachu", "-o", str(out), "--variant", "front_female"]
    )
    assert result.exit_code != 0
    assert not out.exists()
    assert "No sprite available" in strip_ansi(result.stderr)


def test_unknown_variant_is_rejected(tmp_path, install_client):
    install_client(StubClient(resources={"pokemon": POKEMON}))
    out = tmp_path / "x.png"
    result = runner.invoke(
        app, ["sprite", "pikachu", "-o", str(out), "--variant", "sideways"]
    )
    assert result.exit_code != 0
    assert not out.exists()
    message = strip_ansi(result.stderr).replace("\n", " ")
    for variant in SPRITE_VARIANTS:
        assert variant in message


def test_missing_pokemon_writes_no_file(tmp_path, install_client):
    install_client(StubClient(resources={}))
    out = tmp_path / "x.png"
    result = runner.invoke(app, ["sprite", "notapokemon", "-o", str(out)])
    assert result.exit_code == 1
    assert not out.exists()


def test_download_failure_writes_no_file(tmp_path, install_client):
    class Failing(StubClient):
        def download_bytes(self, url):
            import httpx

            raise httpx.ConnectError("unreachable")

    install_client(Failing(resources={"pokemon": POKEMON}))
    out = tmp_path / "x.png"
    result = runner.invoke(app, ["sprite", "pikachu", "-o", str(out)])
    assert result.exit_code == 1
    assert not out.exists()
    assert "Failed to download" in strip_ansi(result.stderr)


def test_creates_missing_parent_directories(tmp_path, install_client):
    install_client(StubClient(resources={"pokemon": POKEMON}))
    out = tmp_path / "nested" / "deeper" / "pikachu.png"
    result = runner.invoke(app, ["sprite", "pikachu", "-o", str(out)])
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_output_is_required(install_client):
    install_client(StubClient(resources={"pokemon": POKEMON}))
    result = runner.invoke(app, ["sprite", "pikachu"])
    assert result.exit_code != 0


def test_unexpected_shape_exits_2(tmp_path, install_client):
    install_client(StubClient(resources={"pokemon": {"id": 1}}))
    out = tmp_path / "x.png"
    result = runner.invoke(app, ["sprite", "pikachu", "-o", str(out)])
    assert result.exit_code == 2
    assert not out.exists()


@pytest.mark.parametrize("variant", SPRITE_VARIANTS)
def test_every_variant_is_completable(variant):
    assert variant in complete_variant("")


def test_variant_completion_filters_on_prefix():
    assert set(complete_variant("back_")) == {"back_default", "back_shiny"}
