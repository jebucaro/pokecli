import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._group import ResourceGroup
from pokecli.commands._helptext import (
    ABILITY_NAME_OR_ID,
    FORMAT,
    LIMIT,
    NO_CACHE,
    OFFSET,
)
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.ability import render_ability
from pokecli.display.common import render_json, render_list
from pokecli.models.ability import Ability

app = typer.Typer(help="Look up Pokemon abilities and what they do.", cls=ResourceGroup)
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=ABILITY_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show an ability's effect, generation, and related Pokemon."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "ability", name_or_id, no_cache, err_console)
    try:
        ability = Ability.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(ability.model_dump(), console)
    elif format == "toon":
        import toons
        from pokecli.display.toon import print_toon
        from pokecli.display.toon_schemas import ability_toon
        from pokecli.display.hints import get_hints, format_hints_toon
        hints = get_hints("ability.get", {"name": ability.name})
        print_toon(toons.dumps({"ability": ability_toon(ability)}))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        from pokecli.display.hints import get_hints, format_hints_table
        hints = get_hints("ability.get", {"name": ability.name})
        render_ability(ability, console)
        if hints:
            console.print(format_hints_table(hints))


@app.command(name="list")
def list_abilities(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Browse abilities with pagination."""
    client = ctx.obj["client"]
    result = fetch_list(client, "ability", limit, offset, err_console)
    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    first_name = result.results[0].name if result.results else None
    hints = get_hints("ability.list", {"resource": "ability", "first_name": first_name})
    if format == "toon":
        import toons
        from pokecli.display.toon import print_toon
        from pokecli.display.toon_schemas import resource_list_toon
        rows = resource_list_toon(result)
        print_toon(f"count: {len(rows)} of {result.count} total")
        print_toon(toons.dumps({"abilities": rows}))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        render_list(result, console)
        if hints:
            console.print(format_hints_table(hints))
