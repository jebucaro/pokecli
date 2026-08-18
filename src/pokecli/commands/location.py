import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands import location_area
from pokecli.commands._group import ResourceGroup
from pokecli.commands._helptext import FORMAT, LIMIT, LOCATION_NAME_OR_ID, NO_CACHE, OFFSET
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.location import render_location
from pokecli.models.location import Location

app = typer.Typer(
    help="Look up locations and the encounter areas inside them.",
    cls=ResourceGroup,
    epilog=(
        "Examples:\n"
        "  pokecli location pallet-town\n"
        "  pokecli location get kanto-route-1\n"
        "  pokecli location area get kanto-route-1-area"
    ),
)
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=LOCATION_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show a location and the encounter areas inside it."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "location", name_or_id, no_cache, err_console)
    try:
        loc = Location.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(loc.model_dump(), console)
    elif format == "toon":
        from pokecli.display.toon import toon_single, print_toon
        from pokecli.display.toon_schemas import location_toon
        from pokecli.display.hints import get_hints, format_hints_toon
        first_area = loc.areas[0].name if loc.areas else None
        hints = get_hints("location.get", {"name": loc.name, "first_area": first_area})
        fields = location_toon(loc)
        print_toon(toon_single("location", fields))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        from pokecli.display.hints import get_hints, format_hints_table
        first_area = loc.areas[0].name if loc.areas else None
        hints = get_hints("location.get", {"name": loc.name, "first_area": first_area})
        render_location(loc, console)
        if hints:
            console.print(format_hints_table(hints))


@app.command(name="list")
def list_locations(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Browse locations with pagination."""
    client = ctx.obj["client"]
    result = fetch_list(client, "location", limit, offset, err_console)
    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    first_name = result.results[0].name if result.results else None
    hints = get_hints("location.list", {"resource": "location", "first_name": first_name})
    if format == "toon":
        from pokecli.display.toon import toon_list, print_toon
        from pokecli.display.toon_schemas import resource_list_toon
        schema_fields, rows = resource_list_toon(result)
        print_toon(toon_list("locations", schema_fields, rows, total=result.count))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        render_list(result, console)
        if hints:
            console.print(format_hints_table(hints))


app.add_typer(location_area.app, name="area")
