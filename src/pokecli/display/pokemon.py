import os
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pokecli.display.common import uses_unicode
from pokecli.models.pokemon import Pokemon, PokemonMoveEntry

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

STAT_BAR_MAX = 255


def _stat_bar(value: int, width: int = 20, *, unicode: bool = True) -> str:
    filled = round(value / STAT_BAR_MAX * width)
    if unicode:
        return "\u2588" * filled + "\u2591" * (width - filled)
    return "#" * filled + "." * (width - filled)


def render_pokemon(pokemon: Pokemon, console: Console) -> None:
    # Header info
    header = Text()
    header.append(f"#{pokemon.id}  ", style="dim")
    header.append(pokemon.name.capitalize(), style="bold white")
    header.append(
        f"   Height: {pokemon.height / 10:.1f}m   Weight: {pokemon.weight / 10:.1f}kg",
        style="dim",
    )
    if pokemon.base_experience is not None:
        header.append(f"   Base XP: {pokemon.base_experience}", style="dim")

    # Types
    type_badges = []
    for pt in sorted(pokemon.types, key=lambda t: t.slot):
        color = TYPE_COLORS.get(pt.type.name, "white")
        type_badges.append(f"[bold {color}] {pt.type.name.upper()} [/]")
    types_line = "  ".join(type_badges)

    _uses_unicode = uses_unicode(console)
    _supports_hyperlinks = console.is_terminal and (
        sys.platform != "win32" or bool(os.environ.get("WT_SESSION"))
    )

    # Stats table
    stats_table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    stats_table.add_column("Stat", style="dim", width=14)
    stats_table.add_column("Base", justify="right", width=4)
    stats_table.add_column("Bar", width=22)
    for ps in pokemon.stats:
        bar = _stat_bar(ps.base_stat, unicode=_uses_unicode)
        stats_table.add_row(ps.stat.name, str(ps.base_stat), f"[green]{bar}[/]")

    # Abilities
    ability_parts = []
    for pa in sorted(pokemon.abilities, key=lambda a: a.slot):
        label = pa.ability.name
        if pa.is_hidden:
            label += " [dim](hidden)[/dim]"
        ability_parts.append(label)
    abilities_line = "  ·  ".join(ability_parts)

    # Sprites
    sprites = pokemon.sprites
    sprite_url = sprites.front_default or "(no sprite)"
    sprite_line = (
        f"[bold]Sprite:[/bold] [link={sprite_url}]{sprite_url}[/link]"
        if _supports_hyperlinks
        else f"[bold]Sprite:[/bold] {sprite_url}"
    )

    panel_content = (
        f"{types_line}\n\n[bold]Abilities:[/bold] {abilities_line}\n\n{sprite_line}\n\n"
    )

    console.print(Panel(header, expand=False))
    console.print(panel_content)
    console.print(stats_table)


def render_pokemon_moves(
    name: str,
    moves: list[PokemonMoveEntry],
    console: Console,
    *,
    move_filter: str | None = None,
    method_filter: str | None = None,
) -> None:
    _uses_unicode = uses_unicode(console)

    METHOD_COLORS = {
        "level-up": "green",
        "machine": "cyan",
        "tutor": "yellow",
        "egg": "magenta",
    }

    if move_filter is not None and len(moves) == 1:
        m = moves[0]
        color = METHOD_COLORS.get(m.learn_method, "white")
        level_part = f" at level {m.level}" if m.learn_method == "level-up" else ""
        console.print(
            f"[bold white]{name.capitalize()}[/] can learn [bold]{m.name}[/] "
            f"via [{color}]{m.learn_method}[/]{level_part}."
        )
        return

    dash = "\u2014" if _uses_unicode else "-"

    if method_filter is not None:
        title = f"{name.capitalize()} {dash} {method_filter} moves ({len(moves)})"
    else:
        title = f"{name.capitalize()} {dash} learnable moves ({len(moves)})"

    table = Table(
        title=title,
        show_header=True,
        header_style="bold",
        box=None,
        padding=(0, 1),
    )
    table.add_column("Move", style="bold white", width=24)
    table.add_column("Method", width=12)
    table.add_column("Level", justify="right", width=6)

    level_placeholder = "\u2014" if _uses_unicode else "-"
    for m in moves:
        color = METHOD_COLORS.get(m.learn_method, "white")
        level_str = str(m.level) if m.learn_method == "level-up" else level_placeholder
        table.add_row(m.name, f"[{color}]{m.learn_method}[/]", level_str)

    console.print(table)

    if method_filter is None and moves:
        from collections import Counter

        counts = Counter(m.learn_method for m in moves)
        separator = "  \u00b7  " if _uses_unicode else "  |  "
        parts = []
        for method in ("level-up", "machine", "egg", "tutor"):
            if method in counts:
                color = METHOD_COLORS.get(method, "white")
                parts.append(f"[{color}]{counts[method]} {method}[/]")
        console.print("  " + separator.join(parts), highlight=False)
