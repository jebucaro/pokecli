import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._helptext import FORMAT, GENERATION_NAME_OR_ID, LIMIT, NO_CACHE, OFFSET
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.game import render_generation
from pokecli.models.game import Generation

app = typer.Typer(help="Look up generations and what they introduced.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=GENERATION_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show a generation and the Pokemon, moves, and regions tied to it."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "generation", name_or_id, no_cache, err_console)
    try:
        gen = Generation.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(gen.model_dump(), console)
    else:
        render_generation(gen, console)


@app.command(name="list")
def list_generations(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
) -> None:
    """Browse generations with pagination."""
    client = ctx.obj["client"]
    render_list(fetch_list(client, "generation", limit, offset, err_console), console)
