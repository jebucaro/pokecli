import json

from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from pokecli.models.common import ListResult


def uses_unicode(console: Console) -> bool:
    return console.encoding.lower() == "utf-8"


def render_list(result: ListResult, console: Console) -> None:
    _uses_unicode = uses_unicode(console)
    arrow_left = "\u2190" if _uses_unicode else "<"
    arrow_right = "\u2192" if _uses_unicode else ">"

    table = Table(title=f"Results ({result.count} total)", show_lines=False)
    table.add_column("Name", style="bold cyan")
    table.add_column("URL", style="dim")
    for item in result.results:
        table.add_row(item.name, item.url)
    if result.previous:
        console.print(f"[dim]{arrow_left} previous: {result.previous}[/dim]")
    console.print(table)
    if result.next:
        console.print(f"[dim]next {arrow_right}: {result.next}[/dim]")


def render_json(data: dict, console: Console) -> None:
    syntax = Syntax(json.dumps(data, indent=2), "json", theme="monokai")
    console.print(syntax)
