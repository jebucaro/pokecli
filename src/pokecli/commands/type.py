import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._group import ResourceGroup
from pokecli.commands._helptext import FORMAT, LIMIT, NO_CACHE, OFFSET, TYPE_NAME_OR_ID
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.type import render_type
from pokecli.models.type import PokemonType

app = typer.Typer(help="Look up type matchups, weaknesses, and resistances.", cls=ResourceGroup)
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=TYPE_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show a type's strengths, weaknesses, and immunities."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "type", name_or_id, no_cache, err_console)
    try:
        pokemon_type = PokemonType.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(pokemon_type.model_dump(), console)
    elif format == "toon":
        import toons
        from pokecli.display.toon import print_toon
        from pokecli.display.toon_schemas import type_toon
        from pokecli.display.hints import get_hints, format_hints_toon
        super_effective = [r.name for r in pokemon_type.damage_relations.double_damage_to]
        hints = get_hints("type.get", {"name": pokemon_type.name, "super_effective": super_effective})
        fields = type_toon(pokemon_type)
        # Add aggregate: pokemon and move counts
        fields["pokemon_count"] = len(pokemon_type.pokemon)
        fields["move_count"] = len(pokemon_type.moves)
        print_toon(toons.dumps({"type": fields}))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        from pokecli.display.hints import get_hints, format_hints_table
        super_effective = [r.name for r in pokemon_type.damage_relations.double_damage_to]
        hints = get_hints("type.get", {"name": pokemon_type.name, "super_effective": super_effective})
        render_type(pokemon_type, console)
        if hints:
            console.print(format_hints_table(hints))


@app.command(name="list")
def list_types(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Browse Pokemon types with pagination."""
    client = ctx.obj["client"]
    result = fetch_list(client, "type", limit, offset, err_console)
    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    first_name = result.results[0].name if result.results else None
    hints = get_hints("type.list", {"resource": "type", "first_name": first_name})
    if format == "toon":
        import toons
        from pokecli.display.toon import print_toon
        from pokecli.display.toon_schemas import resource_list_toon
        rows = resource_list_toon(result)
        print_toon(f"count: {len(rows)} of {result.count} total")
        print_toon(toons.dumps({"types": rows}))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        render_list(result, console)
        if hints:
            console.print(format_hints_table(hints))
