import json
import re
from types import SimpleNamespace

from rich.console import Console
from rich.table import Table

from pokecli.models.common import ListResult

# Matches PokeAPI's chance placeholder, with or without a trailing percent
# sign (e.g. "$effect_chance%" or a bare "$effect_chance").
_EFFECT_CHANCE_TOKEN = re.compile(r"\$effect_chance%?")


def extract_effect_and_chance(
    short_effect: str, effect_chance: int | None
) -> tuple[str, int | None]:
    """Split a move's effect prose from its effect chance.

    PokeAPI embeds the chance in ``short_effect`` as a ``$effect_chance%``
    token and exposes the number separately in ``effect_chance``. Rather than
    inlining the number back into the prose, this returns clean prose (with the
    token removed) plus the chance as a separate value, so callers can render
    them in distinct fields.

    The token is removed whether or not ``effect_chance`` is populated, so an
    unsubstituted ``$effect_chance`` placeholder never leaks into output.
    Whitespace and stray spacing left behind by removal are normalized.

    Returns ``(clean_effect_text, effect_chance)``.
    """
    text = _EFFECT_CHANCE_TOKEN.sub("", short_effect)
    # Collapse any double spaces (and " a  chance" style artifacts) and tidy
    # spacing left before punctuation after token removal.
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\s+([.,;:])", r"\1", text)
    text = text.strip()
    return text, effect_chance

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
    """Write JSON to stdout as plain text.

    Deliberately bypasses Rich. Rendering through ``rich.syntax.Syntax``
    truncates every line at the console width - 80 columns when piped - which
    silently corrupts long string values such as sprite URLs and produces
    unparseable output. JSON is the format callers pipe into a parser, so it
    carries no styling, no wrapping, and no truncation.

    ``console`` is accepted for signature symmetry with the other renderers.
    """
    print(json.dumps(data, indent=2, default=str))
