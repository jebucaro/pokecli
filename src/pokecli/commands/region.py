import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._group import ResourceGroup
from pokecli.commands._helptext import FORMAT, LIMIT, NO_CACHE, OFFSET, REGION_NAME_OR_ID
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.location import render_region
from pokecli.models.location import Region

app = typer.Typer(help="Look up regions and the places you can explore in them.", cls=ResourceGroup)
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=REGION_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show a region and the locations inside it."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "region", name_or_id, no_cache, err_console)
    try:
        region = Region.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(region.model_dump(), console)
    else:
        render_region(region, console)


@app.command(name="list")
def list_regions(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
) -> None:
    """Browse regions with pagination."""
    client = ctx.obj["client"]
    render_list(fetch_list(client, "region", limit, offset, err_console), console)
