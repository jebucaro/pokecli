import httpx
import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.cache.store import CacheStore
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.move import render_move
from pokecli.models.common import ListResult
from pokecli.models.move import Move

app = typer.Typer(help="Search and browse Moves.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help="Move name or ID"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Skip local cache"),
    format: str = typer.Option(
        "table", "--format", help="Output format: table or json"
    ),
) -> None:
    """Get detailed information about a Move."""
    client = ctx.obj["client"]
    with CacheStore() as cache:
        key = name_or_id.lower()
        data = None if no_cache else cache.get("move", key)
        if data is None:
            try:
                data = client.get_resource("move", name_or_id)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    err_console.print(f"[red]Not found: '{name_or_id}'[/red]")
                else:
                    err_console.print(f"[red]API error: {e.response.status_code}[/red]")
                raise typer.Exit(1)
            except (httpx.ConnectError, httpx.TimeoutException):
                err_console.print("[red]Network error: could not reach PokeAPI[/red]")
                raise typer.Exit(1)
            cache.set("move", key, data)
        try:
            move = Move.model_validate(data)
        except ValidationError as e:
            err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
            raise typer.Exit(2)
        if format == "json":
            render_json(data, console)
        else:
            render_move(move, console)


@app.command(name="list")
def list_moves(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help="Number of results"),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help="Pagination offset"),
) -> None:
    """List Moves with pagination."""
    client = ctx.obj["client"]
    try:
        data = client.list_resource("move", limit, offset)
    except (httpx.ConnectError, httpx.TimeoutException):
        err_console.print("[red]Network error: could not reach PokeAPI[/red]")
        raise typer.Exit(1)
    result = ListResult.model_validate(data)
    render_list(result, console)
