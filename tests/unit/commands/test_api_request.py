"""Tests for the shared PokeAPI request wrapper and its error messages."""

import json

import httpx
import pytest
import typer
from rich.console import Console
from typer.testing import CliRunner

from pokecli.commands._utils import api_request, describe_transport_error
from pokecli.main import app

from .conftest import StubClient, strip_ansi

URL = "https://pokeapi.co/api/v2/pokemon/cubone/"
TIMEOUTS = {"connect": 10.0, "read": 10.0, "write": 10.0, "pool": 10.0}
runner = CliRunner()


def _request() -> httpx.Request:
    return httpx.Request("GET", URL, extensions={"timeout": TIMEOUTS})


def _run(exc: Exception) -> tuple[int, str]:
    def call():
        raise exc

    console = Console(record=True, width=300, color_system=None)
    with pytest.raises(typer.Exit) as exit_info:
        api_request(call, console, not_found="cubone")
    return exit_info.value.exit_code, console.export_text()


def test_timeout_names_the_limit_and_url_instead_of_unreachable():
    code, text = _run(httpx.ReadTimeout("timed out", request=_request()))
    assert code == 1
    assert "did not respond within 10s" in text
    assert "ReadTimeout" in text
    assert URL in text
    assert "could not reach" not in text


def test_connect_error_carries_the_underlying_reason():
    code, text = _run(httpx.ConnectError("[Errno -3] Temporary failure in name resolution", request=_request()))
    assert code == 1
    assert "ConnectError" in text
    assert "name resolution" in text


@pytest.mark.parametrize("exc_type", [httpx.ReadError, httpx.RemoteProtocolError, httpx.ProxyError])
def test_every_transport_error_is_reported_not_raised(exc_type):
    """These used to escape as a traceback."""
    code, text = _run(exc_type("connection reset", request=_request()))
    assert code == 1
    assert exc_type.__name__ in text


def test_404_reports_not_found():
    response = httpx.Response(404, request=_request())
    code, text = _run(httpx.HTTPStatusError("404", request=_request(), response=response))
    assert code == 1
    assert "Not found: 'cubone'" in text


def test_other_http_status_reports_code_and_url():
    response = httpx.Response(503, request=_request())
    code, text = _run(httpx.HTTPStatusError("503", request=_request(), response=response))
    assert code == 1
    assert "HTTP 503" in text
    assert URL in text


def test_non_json_body_is_an_unexpected_response_exit_2():
    code, text = _run(json.JSONDecodeError("Expecting value", "<html>", 0))
    assert code == 2
    assert "not JSON" in text


def test_error_without_an_attached_request_still_describes_itself():
    text = describe_transport_error(httpx.ConnectTimeout("timed out"))
    assert "did not respond" in text
    assert "ConnectTimeout" in text


def test_moves_reports_a_timeout_end_to_end(install_client):
    class TimingOut(StubClient):
        def get_resource(self, resource, identifier):
            raise httpx.ReadTimeout("timed out", request=_request())

    install_client(TimingOut())
    result = runner.invoke(app, ["moves", "cubone", "--no-cache"])
    assert result.exit_code == 1
    assert "did not respond within 10s" in strip_ansi(result.stderr)
    assert result.stdout == ""
