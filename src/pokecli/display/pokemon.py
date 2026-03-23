from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pokecli.models.pokemon import Pokemon

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


def _stat_bar(value: int, width: int = 20) -> str:
    filled = round(value / STAT_BAR_MAX * width)
    return "█" * filled + "░" * (width - filled)


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

    # Stats table
    stats_table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    stats_table.add_column("Stat", style="dim", width=14)
    stats_table.add_column("Base", justify="right", width=4)
    stats_table.add_column("Bar", width=22)
    for ps in pokemon.stats:
        bar = _stat_bar(ps.base_stat)
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

    panel_content = (
        f"{types_line}\n\n"
        f"[bold]Abilities:[/bold] {abilities_line}\n\n"
        f"[bold]Sprite:[/bold] [link={sprite_url}]{sprite_url}[/link]\n\n"
    )

    console.print(Panel(header, expand=False))
    console.print(panel_content)
    console.print(stats_table)
