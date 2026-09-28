import toons
import typer
from rich.console import Console
from rich.table import Table

from pokecli.cache.store import RESOURCE_TABLES, CacheStore
from pokecli.commands._format import resolve_format, validate_format
from pokecli.commands._helptext import FORMAT
from pokecli.display.common import render_json
from pokecli.display.toon import print_toon

app = typer.Typer(help="Manage the local PokeAPI cache.")
console = Console()
err_console = Console(stderr=True)


def complete_cache_resource(incomplete: str) -> list[str]:
    targets = [*RESOURCE_TABLES, "all"]
    return [name for name in targets if name.startswith(incomplete)]


@app.command()
def clear(
    resource: str = typer.Option(
        "all",
        "--resource",
        help=f"Which cached resource to clear: {', '.join(RESOURCE_TABLES)}, or all",
        autocompletion=complete_cache_resource,
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
def stats(
    format: str = typer.Option(
        None, "--format", help=FORMAT, callback=validate_format
    ),
) -> None:
    """Show cached entry counts per resource."""
    fmt = resolve_format(format)
    with CacheStore() as cache:
        counts = cache.stats()

    total = sum(counts.values())

    if fmt == "json":
        render_json({"total": total, "resources": counts}, console)
        return

    if fmt == "toon":
        rows = [
            {"resource": resource, "entries": count}
            for resource, count in counts.items()
            if count > 0
        ]
        payload: dict = {"total": total}
        if rows:
            payload["cached"] = rows
        else:
            payload["result"] = "Cache is empty"
        print_toon(toons.dumps(payload))
        return

    table = Table(title="Cache Statistics", show_lines=False)
    table.add_column("Resource", style="bold cyan")
    table.add_column("Cached Entries", justify="right")
    for resource, count in counts.items():
        table.add_row(resource, str(count))
    table.add_section()
    table.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")
    console.print(table)
