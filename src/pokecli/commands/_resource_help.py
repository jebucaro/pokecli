"""The Resources panel shown in ``get``, ``list``, and ``search`` help.

Typer builds its help panels from parameters and commands only, so the
vocabulary is appended by a command class passed through ``cls=``, Typer's
documented extension point. The border style and title alignment match
Typer's own panels.
"""

from typing import Any

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from typer.core import TyperCommand

from pokecli.resources import RESOURCES

PANEL_TITLE = "Resources"


def resource_panel() -> Panel:
    """Every resource name beside its purpose, in table order."""
    table = Table(show_header=False, box=None, expand=True, padding=(0, 1), pad_edge=False)
    table.add_column("Resource", style="bold cyan", no_wrap=True)
    table.add_column("Purpose")
    for res in RESOURCES:
        table.add_row(res.name, escape(res.purpose))
    return Panel(table, title=PANEL_TITLE, title_align="left", border_style="dim")


class ResourceHelpCommand(TyperCommand):
    """A command whose help ends with the Resources panel."""

    def format_help(self, ctx: typer.Context, formatter: Any) -> None:
        # Typer's rich help prints directly rather than through `formatter`,
        # so printing afterwards places the panel below Options. `formatter`
        # stays untyped: Typer >= 0.27 vendors Click instead of depending on
        # it, so importing `click` for the annotation would break installs.
        super().format_help(ctx, formatter)
        Console().print(resource_panel())
