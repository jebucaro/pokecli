import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._helptext import (
    FORMAT,
    LIMIT,
    LOCATION_AREA_NAME_OR_ID,
    NO_CACHE,
    OFFSET,
)
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.location import render_location_area
from pokecli.models.location import LocationArea

app = typer.Typer(help="Look up encounter areas and the Pokemon found there.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=LOCATION_AREA_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show an encounter area and its Pokemon encounter table."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "location-area", name_or_id, no_cache, err_console)
    try:
        area = LocationArea.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(area.model_dump(), console)
    else:
        render_location_area(area, console)


@app.command(name="list")
def list_location_areas(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
) -> None:
    """Browse encounter areas with pagination."""
    client = ctx.obj["client"]
    render_list(
        fetch_list(client, "location-area", limit, offset, err_console), console
    )
