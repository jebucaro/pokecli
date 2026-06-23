import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._helptext import FORMAT, LIMIT, NO_CACHE, OFFSET, VERSION_NAME_OR_ID
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.game import render_version
from pokecli.models.game import Version

app = typer.Typer(help="Look up individual game versions like red or sword.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=VERSION_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show one game version and the version group it belongs to."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "version", name_or_id, no_cache, err_console)
    try:
        version = Version.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(version.model_dump(), console)
    else:
        render_version(version, console)


@app.command(name="list")
def list_versions(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
) -> None:
    """Browse game versions with pagination."""
    client = ctx.obj["client"]
    render_list(fetch_list(client, "version", limit, offset, err_console), console)
