from rich.console import Console
from rich.panel import Panel

from pokecli.display.common import (
    create_key_value_table,
    format_name,
    get_chars,
    panel_title,
)
from pokecli.models.move import Move


def render_move(move: Move, console: Console) -> None:
    chars = get_chars(console)

    console.print(Panel(panel_title(move.id, format_name(move.name)), expand=False))

    table = create_key_value_table()
    table.add_row("Type", move.type.name.capitalize())
    table.add_row("Category", move.damage_class.name.capitalize())
    table.add_row("Power", str(move.power) if move.power is not None else chars.dash)
    table.add_row(
        "Accuracy", f"{move.accuracy}%" if move.accuracy is not None else chars.dash
    )
    table.add_row("PP", str(move.pp) if move.pp is not None else chars.dash)
    if move.effect_chance is not None:
        table.add_row("Effect Chance", f"{move.effect_chance}%")
    console.print(table)

    english_effects = [e for e in move.effect_entries if e.language.name == "en"]
    if english_effects:
        effect_text = english_effects[0].short_effect
        if move.effect_chance is not None:
            effect_text = effect_text.replace("$effect_chance", str(move.effect_chance))
        console.print(f"\n[bold]Effect:[/bold] {effect_text}")
