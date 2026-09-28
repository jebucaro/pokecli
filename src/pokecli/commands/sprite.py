"""Sprite download.

A derived command because it resolves a sprite URL out of a Pokemon record and
then writes a file, rather than rendering a record.
"""

from pathlib import Path

import httpx
import typer
from pydantic import ValidationError
from rich.console import Console
from rich.markup import escape

from pokecli.commands._helptext import (
    NO_CACHE,
    OUTPUT_PATH,
    POKEMON_NAME_OR_ID,
    SPRITE_VARIANT,
)
from pokecli.commands._utils import describe_transport_error, fetch_resource
from pokecli.models.pokemon import Pokemon

console = Console()
err_console = Console(stderr=True)

SPRITE_VARIANTS = [
    "front_default",
    "front_shiny",
    "back_default",
    "back_shiny",
    "front_female",
    "front_shiny_female",
]


def complete_variant(incomplete: str) -> list[str]:
    return [v for v in SPRITE_VARIANTS if v.startswith(incomplete)]


def sprite(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    output: Path = typer.Option(..., "--output", "-o", help=OUTPUT_PATH),
    variant: str = typer.Option(
        "front_default",
        "--variant",
        help=SPRITE_VARIANT,
        autocompletion=complete_variant,
    ),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
) -> None:
    """Download a Pokemon sprite image to a local file."""
    if variant not in SPRITE_VARIANTS:
        err_console.print(
            f"[red]Invalid variant '{variant}'. "
            f"Choose from: {', '.join(SPRITE_VARIANTS)}[/red]"
        )
        raise typer.Exit(1)

    client = ctx.obj["client"]
    data = fetch_resource(client, "pokemon", name_or_id, no_cache, err_console)

    try:
        pokemon = Pokemon.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)

    sprite_url: str | None = getattr(pokemon.sprites, variant, None)
    if not sprite_url:
        err_console.print(
            f"[red]No sprite available for variant '{variant}' on "
            f"'{name_or_id}'.[/red]\nAvailable variants: "
            f"{', '.join(SPRITE_VARIANTS)}"
        )
        raise typer.Exit(1)

    try:
        image_bytes = client.download_bytes(sprite_url)
    except httpx.HTTPStatusError as e:
        err_console.print(
            f"[red]Failed to download image: HTTP {e.response.status_code} "
            f"for {escape(sprite_url)}[/red]"
        )
        raise typer.Exit(1)
    except httpx.TransportError as e:
        err_console.print(
            f"[red]Failed to download image. {escape(describe_transport_error(e))}[/red]"
        )
        raise typer.Exit(1)

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(image_bytes)
    except OSError as e:
        err_console.print(f"[red]Failed to save image to '{output}': {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[green]Saved to:[/green] {output.resolve()}")
