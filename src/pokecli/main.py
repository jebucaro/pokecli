import typer

from pokecli.api.client import PokeAPIClient
from pokecli.commands import (
    ability,
    berry,
    cache,
    egg_group,
    evolution_chain,
    evolution_trigger,
    game,
    generation,
    growth_rate,
    image,
    install,
    item,
    location,
    location_area,
    machine,
    move,
    move_damage_class,
    move_learn_method,
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
    no_args_is_help=True,
    epilog=(
        "Examples:\n"
        "  pokecli pokemon pikachu\n"
        "  pokecli pokemon can-learn pikachu thunderbolt\n"
        "  pokecli move thunderbolt\n"
        "  pokecli game region get kanto\n"
        "  pokecli location area get kanto-route-1-area"
    ),
)


@app.callback()
def root(ctx: typer.Context) -> None:
    ctx.ensure_object(dict)
    ctx.obj["client"] = ctx.with_resource(PokeAPIClient())


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
app.add_typer(egg_group.app, name="egg-group", hidden=True)
app.add_typer(growth_rate.app, name="growth-rate", hidden=True)
app.add_typer(evolution_trigger.app, name="evolution-trigger", hidden=True)
app.add_typer(move_damage_class.app, name="move-damage-class", hidden=True)
app.add_typer(move_learn_method.app, name="move-learn-method", hidden=True)
app.add_typer(evolution_chain.app, name="evolution-chain", hidden=True)
