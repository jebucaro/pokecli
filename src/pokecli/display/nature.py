from rich.console import Console
from rich.panel import Panel

from pokecli.display.common import create_key_value_table, format_name, panel_title
from pokecli.models.nature import Nature


def render_nature(nature: Nature, console: Console) -> None:
    header = panel_title(nature.id, f"{nature.name.capitalize()} Nature")
    console.print(Panel(header, expand=False))

    table = create_key_value_table()

    if nature.increased_stat and nature.decreased_stat:
        increased = format_name(nature.increased_stat.name)
        decreased = format_name(nature.decreased_stat.name)
        table.add_row(
            "Stat Modifier",
            f"[green]+10% {increased}[/green]  [red]-10% {decreased}[/red]",
        )
    else:
        table.add_row("Stat Modifier", "[dim]Neutral (no change)[/dim]")

    if nature.likes_flavor:
        table.add_row("Likes Flavor", nature.likes_flavor.name.capitalize())
    if nature.hates_flavor:
        table.add_row("Hates Flavor", nature.hates_flavor.name.capitalize())

    console.print(table)
