"""Shared fixtures for CLI command tests.

Command tests must never touch the real cache at ``~/.pokecli/cache.json`` or
the live API, so both are replaced here.
"""

import re
import sys

import httpx
import pytest

from pokecli.cache.store import CacheStore
import pokecli.main  # noqa: F401  - ensures sys.modules["pokecli.main"] exists


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences so assertions can match plain text."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """Point every CacheStore() in the code under test at a temp database."""
    db_path = str(tmp_path / "cache.json")
    real_init = CacheStore.__init__

    def init(self, db_path=db_path):
        real_init(self, db_path)

    monkeypatch.setattr(CacheStore, "__init__", init)
    return db_path


class StubClient:
    """Records calls and returns canned responses keyed by resource."""

    def __init__(
        self,
        resources: dict | None = None,
        lists: dict | None = None,
        subresources: dict | None = None,
        image_bytes: bytes = b"PNGDATA",
    ):
        self._resources = resources or {}
        self._lists = lists or {}
        self._subresources = subresources or {}
        self._image_bytes = image_bytes
        self.get_calls: list[tuple[str, str]] = []
        self.list_calls: list[tuple[str, int, int]] = []
        self.url_calls: list[str] = []
        self.download_calls: list[str] = []

    def get_resource(self, resource: str, identifier):
        self.get_calls.append((resource, str(identifier)))
        try:
            return self._resources[resource]
        except KeyError:
            raise _not_found()

    def list_resource(self, resource: str, limit: int, offset: int):
        self.list_calls.append((resource, limit, offset))
        payload = self._lists.get(resource)
        if payload is None:
            payload = _default_list_payload(resource)
        results = payload.get("results")
        if not isinstance(results, list):
            # Malformed payload: hand it through so validation reports it.
            return payload
        return {**payload, "results": results[offset : offset + limit]}

    def get_resource_by_url(self, url: str):
        self.url_calls.append(url)
        return self._resources["evolution-chain"]

    def get_subresource(self, resource: str, identifier, sub: str):
        self.get_calls.append((f"{resource}/{sub}", str(identifier)))
        return self._subresources.get(sub, [])

    def download_bytes(self, url: str) -> bytes:
        self.download_calls.append(url)
        return self._image_bytes

    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None


def _not_found() -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://x")
    response = httpx.Response(404, request=request)
    return httpx.HTTPStatusError("404", request=request, response=response)


#: Resources whose list entries carry no `name`, only a `url`. PokeAPI really
#: responds this way for /machine/, and the stub must reproduce it or tests
#: pass against a shape the API never returns.
NAMELESS_LIST_RESOURCES = {"machine"}


def _default_list_payload(resource: str) -> dict:
    entries = []
    for i in range(1, 51):
        url = f"https://x/api/v2/{resource}/{i}/"
        if resource in NAMELESS_LIST_RESOURCES:
            entries.append({"url": url})
        else:
            entries.append({"name": f"{resource}-{i}", "url": url})
    return {
        "count": len(entries),
        "next": None,
        "previous": None,
        "results": entries,
    }


def network_error_client():
    class Failing(StubClient):
        def get_resource(self, resource, identifier):
            raise httpx.ConnectError("unreachable")

        def list_resource(self, resource, limit, offset):
            raise httpx.ConnectError("unreachable")

    return Failing()


@pytest.fixture
def install_client(monkeypatch):
    """Install a stub client in place of the real PokeAPIClient.

    ``pokecli.main`` cannot be addressed as a string target: ``pokecli/__init__``
    defines a ``main()`` function that shadows the submodule attribute, so the
    module object is taken from ``sys.modules`` instead.
    """
    main_module = sys.modules["pokecli.main"]

    def _install(client):
        monkeypatch.setattr(main_module, "PokeAPIClient", lambda: client)
        return client

    return _install
