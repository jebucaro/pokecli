from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pokecli.display.common import TYPE_COLORS, get_chars
from pokecli.models.type import PokemonType


def _type_badge(name: str) -> str:
    color = TYPE_COLORS.get(name, "white")
    return f"[bold {color}]{name.upper()}[/]"


def _type_list(types: list, *, dash: str) -> str:
    if not types:
        return f"[dim]{dash}[/dim]"
    return "  ".join(_type_badge(t.name) for t in types)


def render_type(pokemon_type: PokemonType, console: Console) -> None:
    chars = get_chars(console)
    dash = chars.dash
    arrow_r = chars.arrow_r
    arrow_l = chars.arrow_l

    dr = pokemon_type.damage_relations
    type_color = TYPE_COLORS.get(pokemon_type.name, "white")
    header = Text()
    header.append(f"#{pokemon_type.id}  ", style="dim")
    header.append(pokemon_type.name.upper(), style=f"bold {type_color}")
    header.append(
        f"   Pokemon: {len(pokemon_type.pokemon)}   Moves: {len(pokemon_type.moves)}",
        style="dim",
    )
    console.print(Panel(header, expand=False))

    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
    table.add_column("", style="bold dim", width=20)
    table.add_column("Types", no_wrap=False)

    table.add_section()
    table.add_row("[bold]Attacking[/bold]", "")
    table.add_row(
        f"Super effective {arrow_r}", _type_list(dr.double_damage_to, dash=dash)
    )
    table.add_row(
        f"Not very effective {arrow_r}", _type_list(dr.half_damage_to, dash=dash)
    )
    table.add_row(f"No effect {arrow_r}", _type_list(dr.no_damage_to, dash=dash))

    table.add_section()
    table.add_row("[bold]Defending[/bold]", "")
    table.add_row(f"Weak to {arrow_l}", _type_list(dr.double_damage_from, dash=dash))
    table.add_row(f"Resists {arrow_l}", _type_list(dr.half_damage_from, dash=dash))
    table.add_row(f"Immune to {arrow_l}", _type_list(dr.no_damage_from, dash=dash))

    console.print(table)
