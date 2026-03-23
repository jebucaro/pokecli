from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pokecli.models.berry import Berry


def render_berry(berry: Berry, console: Console) -> None:
    header = f"[bold]#{berry.id}  {berry.name.capitalize()} Berry[/bold]"
    info = (
        f"[bold]Growth Time:[/bold] {berry.growth_time}h   "
        f"[bold]Max Harvest:[/bold] {berry.max_harvest}   "
        f"[bold]Firmness:[/bold] {berry.firmness.name}\n"
        f"[bold]Natural Gift Power:[/bold] {berry.natural_gift_power}   "
        f"[bold]Item:[/bold] {berry.item.name}\n"
    )
    console.print(Panel(header, expand=False))
    console.print(info)

    if berry.flavors:
        table = Table(title="Flavors", show_lines=False, box=None)
        table.add_column("Flavor", style="bold cyan")
        table.add_column("Potency", justify="right")
        for fv in berry.flavors:
            if fv.potency > 0:
                table.add_row(fv.flavor.name, str(fv.potency))
        console.print(table)
