import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._helptext import FORMAT, GENERATION_NAME_OR_ID, LIMIT, NO_CACHE, OFFSET
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.game import render_generation
from pokecli.models.game import Generation

app = typer.Typer(help="Look up generations and what they introduced.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=GENERATION_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show a generation and the Pokemon, moves, and regions tied to it."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "generation", name_or_id, no_cache, err_console)
    try:
        gen = Generation.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(gen.model_dump(), console)
    elif format == "toon":
        import toons
        from pokecli.display.toon import print_toon
        from pokecli.display.toon_schemas import generation_toon
        from pokecli.display.hints import get_hints, format_hints_toon
        hints = get_hints("generation.get", {"name": gen.name})
        print_toon(toons.dumps({"generation": generation_toon(gen)}))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        from pokecli.display.hints import get_hints, format_hints_table
        hints = get_hints("generation.get", {"name": gen.name})
        render_generation(gen, console)
        if hints:
            console.print(format_hints_table(hints))


@app.command(name="list")
def list_generations(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Browse generations with pagination."""
    client = ctx.obj["client"]
    result = fetch_list(client, "generation", limit, offset, err_console)
    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    first_name = result.results[0].name if result.results else None
    hints = get_hints("generation.list", {"resource": "game generation", "first_name": first_name})
    if format == "toon":
        import toons
        from pokecli.display.toon import print_toon
        from pokecli.display.toon_schemas import resource_list_toon
        rows = resource_list_toon(result)
        print_toon(f"count: {len(rows)} of {result.count} total")
        print_toon(toons.dumps({"generations": rows}))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        render_list(result, console)
        if hints:
            console.print(format_hints_table(hints))
