from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pokecli.models.move import Move


def render_move(move: Move, console: Console) -> None:
    header = f"[bold]#{move.id}  {move.name.replace('-', ' ').title()}[/bold]"
    console.print(Panel(header, expand=False))

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold dim")
    table.add_column("Value", style="white")
    table.add_row("Type", move.type.name.capitalize())
    table.add_row("Category", move.damage_class.name.capitalize())
    table.add_row("Power", str(move.power) if move.power is not None else "—")
    table.add_row("Accuracy", f"{move.accuracy}%" if move.accuracy is not None else "—")
    table.add_row("PP", str(move.pp) if move.pp is not None else "—")
    if move.effect_chance is not None:
        table.add_row("Effect Chance", f"{move.effect_chance}%")
    console.print(table)

    english_effects = [e for e in move.effect_entries if e.language.name == "en"]
    if english_effects:
        effect_text = english_effects[0].short_effect
        if move.effect_chance is not None:
            effect_text = effect_text.replace("$effect_chance", str(move.effect_chance))
        console.print(f"\n[bold]Effect:[/bold] {effect_text}")
