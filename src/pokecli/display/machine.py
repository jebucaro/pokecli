from rich.console import Console
from rich.panel import Panel

from pokecli.display.common import create_key_value_table, format_name, panel_title
from pokecli.models.machine import Machine


def render_machine(machine: Machine, console: Console) -> None:
    item_name = format_name(machine.item.name)
    move_name = format_name(machine.move.name)
    console.print(Panel(panel_title(machine.id, f"{item_name}"), expand=False))

    table = create_key_value_table()
    table.add_row("Item", machine.item.name)
    table.add_row(
        "Teaches Move", f"[bold cyan]{move_name}[/bold cyan] ({machine.move.name})"
    )
    table.add_row("Version Group", machine.version_group.name)
    console.print(table)
