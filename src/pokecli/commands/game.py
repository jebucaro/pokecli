import typer

from pokecli.commands import (
    generation,
    machine,
    pokedex,
    region,
    version,
    version_group,
)

app = typer.Typer(
    help="Look up regions, generations, versions, pokedexes, and machines.",
    epilog=(
        "Examples:\n"
        "  pokecli game region get kanto\n"
        "  pokecli game generation get generation-i\n"
        "  pokecli game pokedex get national\n"
        "  pokecli game machine get 79"
    ),
)

app.add_typer(generation.app, name="generation")
app.add_typer(pokedex.app, name="pokedex")
app.add_typer(region.app, name="region")
app.add_typer(version.app, name="version")
app.add_typer(version_group.app, name="version-group")
app.add_typer(machine.app, name="machine")
