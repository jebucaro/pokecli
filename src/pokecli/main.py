import shutil
import sys
from pathlib import Path

import typer
from rich.console import Console

from pokecli.api.client import PokeAPIClient
from pokecli.cache.store import CacheStore
from pokecli.commands import (
    ability,
    berry,
    cache,
    evolution_chain,
    game,
    generation,
    image,
    install,
    item,
    location,
    location_area,
    machine,
    move,
    nature,
    pokedex,
    pokemon,
    pokemon_form,
    region,
    type as type_cmd,
    version,
    version_group,
)

app = typer.Typer(
    name="pokecli",
    help="Look up Pokemon data, moves, locations, and game info from the terminal.",
    invoke_without_command=True,
    epilog=(
        "Examples:\n"
        "  pokecli pokemon pikachu\n"
        "  pokecli pokemon can-learn pikachu thunderbolt\n"
        "  pokecli move thunderbolt\n"
        "  pokecli game region get kanto\n"
        "  pokecli location area get kanto-route-1-area"
    ),
)


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context) -> None:
    ctx.ensure_object(dict)
    ctx.obj["client"] = ctx.with_resource(PokeAPIClient())

    if ctx.invoked_subcommand is None:
        _show_home_view()


def _show_home_view() -> None:
    console = Console()

    # Binary path
    bin_path = shutil.which("pokecli") or sys.argv[0]
    home = str(Path.home())
    if bin_path.startswith(home):
        bin_path = "~" + bin_path[len(home):]

    console.print("[bold]pokecli[/bold]")
    console.print(f"[dim]bin: {bin_path}[/dim]")
    console.print(
        "Look up Pokemon data, moves, locations, and game info from the terminal.\n"
    )

    # Cache summary
    try:
        with CacheStore() as cache:
            counts = cache.stats()
        total = sum(counts.values())
        non_empty = {k: v for k, v in counts.items() if v > 0}

        if total > 0:
            console.print(f"[bold]Cache:[/bold] {total} entries")
            parts = [
                f"{k}: {v}"
                for k, v in sorted(non_empty.items(), key=lambda x: -x[1])[:5]
            ]
            console.print(f"  [dim]{', '.join(parts)}[/dim]")
        else:
            console.print(
                "[bold]Cache:[/bold] empty (data will be fetched from PokeAPI on first use)"
            )
        console.print()
    except Exception:
        pass

    # Quick start
    console.print("[bold]Quick start:[/bold]")
    console.print("  pokecli pokemon pikachu")
    console.print("  pokecli move thunderbolt")
    console.print("  pokecli type fire")
    console.print("  pokecli pokemon can-learn charizard fly")
    console.print("  pokecli game region get kanto")
    console.print()
    console.print("[dim]Run pokecli --help for full command reference.[/dim]")


app.add_typer(install.app, name="install")
app.add_typer(pokemon.app, name="pokemon")
app.add_typer(ability.app, name="ability")
app.add_typer(move.app, name="move")
app.add_typer(item.app, name="item")
app.add_typer(type_cmd.app, name="type")
app.add_typer(location.app, name="location")
app.add_typer(game.app, name="game")
app.add_typer(image.app, name="image")
app.add_typer(cache.app, name="cache")
app.add_typer(nature.app, name="nature")
app.add_typer(berry.app, name="berry")
app.add_typer(location_area.app, name="location-area", hidden=True)
app.add_typer(region.app, name="region", hidden=True)
app.add_typer(generation.app, name="generation", hidden=True)
app.add_typer(pokedex.app, name="pokedex", hidden=True)
app.add_typer(version.app, name="version", hidden=True)
app.add_typer(version_group.app, name="version-group", hidden=True)
app.add_typer(machine.app, name="machine", hidden=True)
app.add_typer(pokemon_form.app, name="pokemon-form", hidden=True)
app.add_typer(evolution_chain.app, name="evolution-chain", hidden=True)
