import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._helptext import FORMAT, LIMIT, MACHINE_ID, NO_CACHE, OFFSET
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.machine import render_machine
from pokecli.models.machine import Machine

app = typer.Typer(help="Look up TM and HM machine records.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=MACHINE_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show what move a machine teaches and in which games."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "machine", name_or_id, no_cache, err_console)
    try:
        machine = Machine.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(machine.model_dump(), console)
    elif format == "toon":
        from pokecli.display.toon import toon_single, print_toon
        from pokecli.display.toon_schemas import machine_toon
        from pokecli.display.hints import get_hints, format_hints_toon
        hints = get_hints("machine.list", {"resource": "game machine", "first_name": str(machine.id)})
        fields = machine_toon(machine)
        print_toon(toon_single("machine", fields))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        from pokecli.display.hints import get_hints, format_hints_table
        hints = get_hints("machine.list", {"resource": "game machine", "first_name": str(machine.id)})
        render_machine(machine, console)
        if hints:
            console.print(format_hints_table(hints))


@app.command(name="list")
def list_machines(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Browse machine records with pagination."""
    client = ctx.obj["client"]
    result = fetch_list(client, "machine", limit, offset, err_console)
    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    first_name = result.results[0].name if result.results else None
    hints = get_hints("machine.list", {"resource": "game machine", "first_name": first_name})
    if format == "toon":
        from pokecli.display.toon import toon_list, print_toon
        from pokecli.display.toon_schemas import resource_list_toon
        schema_fields, rows = resource_list_toon(result)
        print_toon(toon_list("machines", schema_fields, rows, total=result.count))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        render_list(result, console)
        if hints:
            console.print(format_hints_table(hints))
