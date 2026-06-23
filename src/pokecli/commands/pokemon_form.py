import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._group import ResourceGroup
from pokecli.commands._helptext import FORMAT, FORM_NAME_OR_ID, LIMIT, NO_CACHE, OFFSET
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.pokemon_form import render_pokemon_form
from pokecli.models.pokemon_form import PokemonForm

app = typer.Typer(
    help="Inspect special forms like Mega, Alolan, and Gigantamax variants.",
    cls=ResourceGroup,
)
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=FORM_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show details for one specific Pokemon form."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "pokemon-form", name_or_id, no_cache, err_console)
    try:
        form = PokemonForm.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(form.model_dump(), console)
    else:
        render_pokemon_form(form, console)


@app.command(name="list")
def list_pokemon_forms(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
) -> None:
    """Browse Pokemon forms with pagination."""
    client = ctx.obj["client"]
    render_list(fetch_list(client, "pokemon-form", limit, offset, err_console), console)
