import httpx
import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.cache.store import CacheStore
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.pokemon import render_pokemon
from pokecli.models.common import ListResult
from pokecli.models.pokemon import Pokemon

app = typer.Typer(help="Search and browse Pokemon.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help="Pokemon name or Pokedex number"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Skip local cache"),
    format: str = typer.Option(
        "table", "--format", help="Output format: table or json"
    ),
) -> None:
    """Get detailed information about a Pokemon."""
    client = ctx.obj["client"]
    with CacheStore() as cache:
        key = name_or_id.lower()
        data = None if no_cache else cache.get("pokemon", key)
        if data is None:
            try:
                data = client.get_resource("pokemon", name_or_id)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    err_console.print(f"[red]Not found: '{name_or_id}'[/red]")
                else:
                    err_console.print(f"[red]API error: {e.response.status_code}[/red]")
                raise typer.Exit(1)
            except (httpx.ConnectError, httpx.TimeoutException):
                err_console.print("[red]Network error: could not reach PokeAPI[/red]")
                raise typer.Exit(1)
            cache.set("pokemon", key, data)
        try:
            pokemon = Pokemon.model_validate(data)
        except ValidationError as e:
            err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
            raise typer.Exit(2)
        if format == "json":
            render_json(data, console)
        else:
            render_pokemon(pokemon, console)


@app.command(name="list")
def list_pokemon(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help="Number of results"),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help="Pagination offset"),
) -> None:
    """List Pokemon with pagination."""
    client = ctx.obj["client"]
    try:
        data = client.list_resource("pokemon", limit, offset)
    except (httpx.ConnectError, httpx.TimeoutException):
        err_console.print("[red]Network error: could not reach PokeAPI[/red]")
        raise typer.Exit(1)
    result = ListResult.model_validate(data)
    render_list(result, console)
