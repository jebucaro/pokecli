import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.commands._helptext import EVOLUTION_CHAIN_ID, FORMAT, LIMIT, NO_CACHE, OFFSET
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.evolution import render_evolution
from pokecli.models.evolution import EvolutionChain

app = typer.Typer(help="Look up Evolution Chains by chain ID.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=EVOLUTION_CHAIN_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show an evolution chain when you already have the chain ID."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "evolution-chain", name_or_id, no_cache, err_console)
    try:
        chain = EvolutionChain.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    if format == "json":
        render_json(chain.model_dump(), console)
    elif format == "toon":
        from pokecli.display.toon import toon_tree, print_toon
        from pokecli.display.toon_schemas import evolution_chain_toon
        from pokecli.display.hints import get_hints, format_hints_toon
        base_name = chain.chain.species.name if chain.chain else None
        hints = get_hints("pokemon.evolution", {"name": base_name}) if base_name else []
        label, lines = evolution_chain_toon(chain)
        print_toon(toon_tree(label, lines))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        from pokecli.display.hints import get_hints, format_hints_table
        base_name = chain.chain.species.name if chain.chain else None
        hints = get_hints("pokemon.evolution", {"name": base_name}) if base_name else []
        render_evolution(chain, console)
        if hints:
            console.print(format_hints_table(hints))


@app.command(name="list")
def list_chains(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Browse evolution chains with pagination."""
    client = ctx.obj["client"]
    result = fetch_list(client, "evolution-chain", limit, offset, err_console)
    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    first_name = result.results[0].name if result.results else None
    hints = get_hints("evolution_chain.list", {"resource": "pokemon evolution-chain", "first_name": first_name})
    if format == "toon":
        from pokecli.display.toon import toon_list, print_toon
        from pokecli.display.toon_schemas import resource_list_toon
        schema_fields, rows = resource_list_toon(result)
        print_toon(toon_list("evolution_chains", schema_fields, rows, total=result.count))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        render_list(result, console)
        if hints:
            console.print(format_hints_table(hints))
