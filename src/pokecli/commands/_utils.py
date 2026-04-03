import httpx
import typer
from rich.console import Console

from pokecli.cache.store import CacheStore
from pokecli.models.common import ListResult


def fetch_resource(
    client,
    resource: str,
    name_or_id: str,
    no_cache: bool,
    err_console: Console,
) -> dict:
    """Fetch a single resource from cache or API, with unified error handling."""
    with CacheStore() as cache:
        key = name_or_id.lower()
        data = None if no_cache else cache.get(resource, key)
        if data is None:
            try:
                data = client.get_resource(resource, name_or_id)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    err_console.print(f"[red]Not found: '{name_or_id}'[/red]")
                else:
                    err_console.print(f"[red]API error: {e.response.status_code}[/red]")
                raise typer.Exit(1)
            except (httpx.ConnectError, httpx.TimeoutException):
                err_console.print("[red]Network error: could not reach PokeAPI[/red]")
                raise typer.Exit(1)
            cache.set(resource, key, data)
    return data


def fetch_list(
    client,
    resource: str,
    limit: int,
    offset: int,
    err_console: Console,
) -> ListResult:
    """Fetch a paginated resource list from the API, with unified error handling."""
    try:
        data = client.list_resource(resource, limit, offset)
    except (httpx.ConnectError, httpx.TimeoutException):
        err_console.print("[red]Network error: could not reach PokeAPI[/red]")
        raise typer.Exit(1)
    return ListResult.model_validate(data)
