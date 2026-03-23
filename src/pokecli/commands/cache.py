import typer
from rich.console import Console
from rich.table import Table

from pokecli.cache.store import RESOURCE_TABLES, CacheStore

app = typer.Typer(help="Manage the local PokeAPI cache.")
console = Console()
err_console = Console(stderr=True)


@app.command()
def clear(
    resource: str = typer.Option(
        "all",
        "--resource",
        help=f"Resource to clear: {', '.join(RESOURCE_TABLES)}, or all",
    ),
) -> None:
    """Clear cached entries."""
    valid = RESOURCE_TABLES + ["all"]
    if resource not in valid:
        err_console.print(
            f"[red]Invalid resource '{resource}'. Choose from: {', '.join(valid)}[/red]"
        )
        raise typer.Exit(1)

    with CacheStore() as cache:
        count = cache.clear(None if resource == "all" else resource)
    label = "all resources" if resource == "all" else f"'{resource}'"
    console.print(f"[green]Cleared {count} cached entries from {label}.[/green]")


@app.command()
def stats() -> None:
    """Show cache statistics."""
    with CacheStore() as cache:
        counts = cache.stats()

    table = Table(title="Cache Statistics", show_lines=False)
    table.add_column("Resource", style="bold cyan")
    table.add_column("Cached Entries", justify="right")

    total = 0
    for resource, count in counts.items():
        table.add_row(resource, str(count))
        total += count

    table.add_section()
    table.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")
    console.print(table)
