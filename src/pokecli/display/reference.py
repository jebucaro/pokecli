from rich.console import Console
from rich.panel import Panel

from pokecli.display.common import (
    create_key_value_table,
    english_name,
    format_name,
    panel_title,
)
from pokecli.models.reference import SimpleNamedResource


def render_reference(
    resource: SimpleNamedResource, console: Console, label: str
) -> None:
    """Render a simple reference resource (id, name, English localized name)."""
    en = english_name(resource)
    title = format_name(resource.name)
    header = panel_title(resource.id, f"{title} {label}")
    console.print(Panel(header, expand=False))

    table = create_key_value_table()
    table.add_row("Name", resource.name)
    if en and en != title:
        table.add_row("English", en)
    console.print(table)
