import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._helptext import (
    EVOLUTION_TRIGGER_NAME_OR_ID,
    FORMAT,
    LIMIT,
    NO_CACHE,
    OFFSET,
)
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.reference import render_reference
from pokecli.models.reference import SimpleNamedResource

app = typer.Typer(help="Look up evolution triggers like level-up, trade, or use-item.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=EVOLUTION_TRIGGER_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show one evolution trigger."""
    client = ctx.obj["client"]
    data = fetch_resource(
        client, "evolution-trigger", name_or_id, no_cache, err_console
    )
    try:
        resource = SimpleNamedResource.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(resource.model_dump(), console)
    else:
        render_reference(resource, console, "Evolution Trigger")


@app.command(name="list")
def list_evolution_triggers(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
) -> None:
    """Browse evolution triggers with pagination."""
    client = ctx.obj["client"]
    render_list(
        fetch_list(client, "evolution-trigger", limit, offset, err_console), console
    )
