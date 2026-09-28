from typing import Callable, TypeVar

import httpx
import typer
from pydantic import ValidationError
from rich.console import Console
from rich.markup import escape

from pokecli.cache.store import CacheStore
from pokecli.models.common import ListResult

T = TypeVar("T")

# One request is enough to retrieve any resource's complete name index; PokeAPI
# list endpoints offer no name filter, so `search` filters this locally.
NAME_INDEX_LIMIT = 100000
NAME_INDEX_KEY = "__name_index__"


def _request_url(error: httpx.HTTPError) -> str | None:
    """The URL that failed, when httpx attached the request to the error."""
    try:
        return str(error.request.url)
    except RuntimeError:
        return None


def describe_transport_error(error: httpx.TransportError) -> str:
    """Say which network failure happened, instead of a generic 'unreachable'.

    A timeout, a refused connection, a DNS failure, and a dropped connection
    call for different fixes, so the message names the exception type, the
    URL, and for timeouts the limit that was hit.
    """
    kind = type(error).__name__
    url = _request_url(error)
    where = f" requesting {url}" if url else ""
    if isinstance(error, httpx.TimeoutException):
        limit = None
        try:
            limit = error.request.extensions.get("timeout", {}).get("read")
        except RuntimeError:
            pass
        within = f" within {limit:g}s" if isinstance(limit, (int, float)) else ""
        return f"Network error: PokeAPI did not respond{within} ({kind}{where})"
    detail = str(error).strip()
    reason = f": {detail}" if detail else ""
    return f"Network error: request to PokeAPI failed ({kind}{where}){reason}"


def api_request(
    call: Callable[[], T],
    err_console: Console,
    *,
    not_found: str | None = None,
) -> T:
    """Run one PokeAPI request, turning every failure into a message and exit code.

    Exit 1 for HTTP errors (a 404 reports ``not_found`` when given) and for any
    transport failure. Exit 2 when the body is not JSON, which is the same
    "unexpected response" class as a failed model validation.
    """
    try:
        return call()
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        if status == 404 and not_found is not None:
            err_console.print(f"[red]Not found: '{escape(not_found)}'[/red]")
        else:
            url = _request_url(e)
            suffix = f" for {url}" if url else ""
            err_console.print(f"[red]API error: HTTP {status}{escape(suffix)}[/red]")
        raise typer.Exit(1)
    except httpx.TransportError as e:
        err_console.print(f"[red]{escape(describe_transport_error(e))}[/red]")
        raise typer.Exit(1)
    except ValueError as e:
        # `response.json()` on a non-JSON body, e.g. a proxy's HTML error page.
        err_console.print(
            f"[red]Unexpected API response format: body is not JSON ({escape(str(e))})[/red]"
        )
        raise typer.Exit(2)


def normalize_identifier(name_or_id: str) -> str:
    """Normalize a user-supplied identifier for API and cache lookup.

    Names are matched case-insensitively, and spaces are treated as hyphens so
    ``"master ball"`` resolves to ``master-ball``. Numeric IDs pass through.
    """
    return name_or_id.strip().lower().replace(" ", "-")


def fetch_resource(
    client,
    resource: str,
    name_or_id: str,
    no_cache: bool,
    err_console: Console,
) -> dict:
    """Fetch a single resource from cache or API, with unified error handling."""
    with CacheStore() as cache:
        key = normalize_identifier(name_or_id)
        data = None if no_cache else cache.get(resource, key)
        if data is None:
            data = api_request(
                lambda: client.get_resource(resource, key),
                err_console,
                not_found=name_or_id,
            )
            cache.set(resource, key, data)
    return data


def _fill_missing_names(payload: dict) -> dict:
    """Give every list entry a name, deriving one from its URL when absent.

    Not every resource is named. ``/machine/`` list entries carry only a URL,
    because machines are identified by ID. Deriving the trailing path segment
    yields exactly the identifier ``get machine <id>`` accepts, so list and
    search stay usable for those resources instead of failing validation.
    """
    results = payload.get("results")
    if not isinstance(results, list):
        return payload
    filled = []
    for entry in results:
        if isinstance(entry, dict) and not entry.get("name"):
            url = str(entry.get("url", ""))
            entry = {**entry, "name": url.rstrip("/").rsplit("/", 1)[-1]}
        filled.append(entry)
    return {**payload, "results": filled}


def fetch_list(
    client,
    resource: str,
    limit: int,
    offset: int,
    err_console: Console,
) -> ListResult:
    """Fetch a paginated resource list from the API, with unified error handling."""
    data = api_request(lambda: client.list_resource(resource, limit, offset), err_console)
    try:
        return ListResult.model_validate(_fill_missing_names(data))
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)


def fetch_name_index(
    client,
    resource: str,
    no_cache: bool,
    err_console: Console,
) -> list[dict]:
    """Fetch the complete name index for a resource, cached like any response.

    Stored in the resource's own cache table, so ``cache clear --resource
    <resource>`` and ``--no-cache`` both apply to it.
    """
    with CacheStore() as cache:
        data = None if no_cache else cache.get(resource, NAME_INDEX_KEY)
        if data is None:
            data = api_request(
                lambda: client.list_resource(resource, NAME_INDEX_LIMIT, 0),
                err_console,
            )
            data = _fill_missing_names(data)
            cache.set(resource, NAME_INDEX_KEY, data)
    return data.get("results", [])
