import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._helptext import FORMAT, LIMIT, NO_CACHE, OFFSET, POKEDEX_NAME_OR_ID
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.game import render_pokedex
from pokecli.models.game import Pokedex

app = typer.Typer(help="Look up regional and national pokedexes.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEDEX_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show a pokedex and its entry list."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "pokedex", name_or_id, no_cache, err_console)
    try:
        pdx = Pokedex.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(pdx.model_dump(), console)
    else:
        render_pokedex(pdx, console)


@app.command(name="list")
def list_pokedexes(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
) -> None:
    """Browse pokedexes with pagination."""
    client = ctx.obj["client"]
    render_list(fetch_list(client, "pokedex", limit, offset, err_console), console)
