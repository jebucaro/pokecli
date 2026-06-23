from pathlib import Path

import httpx
import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.cache.store import CacheStore
from pokecli.commands._helptext import OUTPUT_PATH, RESOURCE, RESOURCE_NAME_OR_ID, SPRITE_VARIANT
from pokecli.models.pokemon import Pokemon

app = typer.Typer(help="Download Pokemon images and sprites.")
console = Console()
err_console = Console(stderr=True)

SUPPORTED_RESOURCES = ["pokemon"]
SPRITE_VARIANTS = [
    "front_default",
    "front_shiny",
    "back_default",
    "back_shiny",
    "front_female",
    "front_shiny_female",
]


@app.command()
def download(
    ctx: typer.Context,
    resource: str = typer.Argument(
        ..., help=RESOURCE
    ),
    name_or_id: str = typer.Argument(..., help=RESOURCE_NAME_OR_ID),
    output: Path = typer.Option(..., "--output", "-o", help=OUTPUT_PATH),
    variant: str = typer.Option(
        "front_default",
        "--variant",
        help=SPRITE_VARIANT,
    ),
) -> None:
    """Download a Pokemon sprite image to a local file."""
    if resource not in SUPPORTED_RESOURCES:
        err_console.print(
            f"[red]Unsupported resource '{resource}'. Supported: {', '.join(SUPPORTED_RESOURCES)}[/red]"
        )
        raise typer.Exit(1)

    if variant not in SPRITE_VARIANTS:
        err_console.print(
            f"[red]Invalid variant '{variant}'. Choose from: {', '.join(SPRITE_VARIANTS)}[/red]"
        )
        raise typer.Exit(1)

    client = ctx.obj["client"]
    with CacheStore() as cache:
        key = name_or_id.lower()
        data = cache.get(resource, key)
        if data is None:
            try:
                data = client.get_resource(resource, name_or_id)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    err_console.print(f"[red]Not found: '{name_or_id}'[/red]")
                else:
                    err_console.print(f"[red]API error: {e.response.status_code}[/red]")
                raise typer.Exit(1)
            except (httpx.ConnectError, httpx.TimeoutException):
                err_console.print("[red]Network error: could not reach PokeAPI[/red]")
                raise typer.Exit(1)
            cache.set(resource, key, data)

        try:
            pokemon = Pokemon.model_validate(data)
        except ValidationError as e:
            err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
            raise typer.Exit(2)

        sprite_url: str | None = getattr(pokemon.sprites, variant, None)
        if not sprite_url:
            err_console.print(
                f"[red]No sprite available for variant '{variant}' on '{name_or_id}'.[/red]\n"
                f"Available variants: {', '.join(SPRITE_VARIANTS)}"
            )
            raise typer.Exit(1)

        console.print(
            f"Downloading [cyan]{variant}[/cyan] sprite for [bold]{name_or_id}[/bold]..."
        )
        try:
            image_bytes = client.download_bytes(sprite_url)
        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
            err_console.print(f"[red]Failed to download image: {e}[/red]")
            raise typer.Exit(1)

        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(image_bytes)
        except OSError as e:
            err_console.print(f"[red]Failed to save image to '{output}': {e}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]Saved to:[/green] {output.resolve()}")
