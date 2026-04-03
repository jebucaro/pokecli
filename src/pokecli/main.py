import typer

from pokecli.api.client import PokeAPIClient
from pokecli.commands import berry, cache, image, install, item, move, pokemon

app = typer.Typer(
    name="pokecli",
    help="A Pokemon CLI powered by PokeAPI with local caching.",
    no_args_is_help=True,
)


@app.callback()
def root(ctx: typer.Context) -> None:
    ctx.ensure_object(dict)
    ctx.obj["client"] = ctx.with_resource(PokeAPIClient())


app.add_typer(install.app, name="install")
app.add_typer(pokemon.app, name="pokemon")
app.add_typer(berry.app, name="berry")
app.add_typer(item.app, name="item")
app.add_typer(move.app, name="move")
app.add_typer(image.app, name="image")
app.add_typer(cache.app, name="cache")
