import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands import move_damage_class, move_learn_method
from pokecli.commands._group import ResourceGroup
from pokecli.commands._helptext import FORMAT, LIMIT, MOVE_NAME_OR_ID, NO_CACHE, OFFSET
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.move import render_move
from pokecli.models.move import Move

app = typer.Typer(
    help="Look up moves, damage classes, and learn methods.",
    cls=ResourceGroup,
    epilog=(
        "Examples:\n"
        "  pokecli move thunderbolt\n"
        "  pokecli move get surf\n"
        "  pokecli move damage-class get special\n"
        "  pokecli move learn-method get machine"
    ),
)
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=MOVE_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show a move's type, power, accuracy, and effect."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "move", name_or_id, no_cache, err_console)
    try:
        move = Move.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(move.model_dump(), console)
    else:
        render_move(move, console)


@app.command(name="list")
def list_moves(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
) -> None:
    """Browse moves with pagination."""
    client = ctx.obj["client"]
    render_list(fetch_list(client, "move", limit, offset, err_console), console)


app.add_typer(move_damage_class.app, name="damage-class")
app.add_typer(move_learn_method.app, name="learn-method")
