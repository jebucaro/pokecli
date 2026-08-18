import json
from types import SimpleNamespace

from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from pokecli.models.common import ListResult

METHOD_COLORS: dict[str, str] = {
    "level-up": "green",
    "machine": "cyan",
    "tutor": "yellow",
    "egg": "magenta",
}

TYPE_COLORS: dict[str, str] = {
    "normal": "grey70",
    "fire": "bright_red",
    "water": "blue",
    "electric": "yellow",
    "grass": "green",
    "ice": "cyan",
    "fighting": "red",
    "poison": "magenta",
    "ground": "yellow3",
    "flying": "sky_blue2",
    "psychic": "hot_pink",
    "bug": "chartreuse3",
    "rock": "dark_goldenrod",
    "ghost": "medium_purple",
    "dragon": "blue_violet",
    "dark": "grey39",
    "steel": "steel_blue",
    "fairy": "light_pink1",
}


def format_name(name: str) -> str:
    return name.replace("-", " ").title()


def create_key_value_table() -> Table:
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold dim")
    table.add_column("Value", style="white")
    return table


def english_name(resource) -> str | None:
    for entry in resource.names:
        if entry.language.name == "en":
            return entry.name
    return None


def uses_unicode(console: Console) -> bool:
    return console.encoding.lower() == "utf-8"


def get_chars(console: Console) -> SimpleNamespace:
    """Return a namespace of Unicode characters with ASCII fallbacks."""
    u = uses_unicode(console)
    return SimpleNamespace(
        dash="\u2014" if u else "-",
        arrow_r="\u2192" if u else "->",
        arrow_l="\u2190" if u else "<-",
        currency="\u20bd" if u else "P",
        bullet="\u00b7" if u else "|",
    )


def panel_title(id: int, label: str) -> str:
    """Format a standard panel header: bold #id  label."""
    return f"[bold]#{id}  {label}[/bold]"


def render_list(result: ListResult, console: Console) -> None:
    chars = get_chars(console)

    if not result.results:
        console.print(f"[dim]0 results at this offset. ({result.count} total exist)[/dim]")
        return

    table = Table(title=f"Results ({result.count} total)", show_lines=False)
    table.add_column("Name", style="bold cyan")
    table.add_column("URL", style="dim")
    for item in result.results:
        table.add_row(item.name, item.url)
    if result.previous:
        console.print(f"[dim]{chars.arrow_l} previous: {result.previous}[/dim]")
    console.print(table)
    if result.next:
        console.print(f"[dim]next {chars.arrow_r}: {result.next}[/dim]")


def render_json(data: dict, console: Console) -> None:
    syntax = Syntax(json.dumps(data, indent=2), "json", theme="monokai")
    console.print(syntax)
