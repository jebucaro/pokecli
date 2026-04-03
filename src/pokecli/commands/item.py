import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.item import render_item
from pokecli.models.item import Item

app = typer.Typer(help="Search and browse Items.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help="Item name or ID"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Skip local cache"),
    format: str = typer.Option(
        "table", "--format", help="Output format: table or json"
    ),
) -> None:
    """Get detailed information about an Item."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "item", name_or_id, no_cache, err_console)
    try:
        item = Item.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(item.model_dump(), console)
    else:
        render_item(item, console)


@app.command(name="list")
def list_items(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help="Number of results"),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help="Pagination offset"),
) -> None:
    """List Items with pagination."""
    client = ctx.obj["client"]
    render_list(fetch_list(client, "item", limit, offset, err_console), console)
