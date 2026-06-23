from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pokecli.display.common import create_key_value_table, format_name, panel_title
from pokecli.models.pokemon_form import PokemonForm


def render_pokemon_varieties(
    species_name: str, varieties: list[dict], console: Console
) -> None:
    title = format_name(species_name)
    console.print(Panel(f"[bold]{title} - Varieties[/bold]", expand=False))

    if not varieties:
        console.print("[dim]No varieties recorded.[/dim]")
        return

    table = Table(show_lines=False)
    table.add_column("Variety", style="bold cyan")
    table.add_column("Default", justify="center")
    table.add_column("Lookup URL", style="dim")
    for v in varieties:
        is_default = "yes" if v.get("is_default") else ""
        table.add_row(v["pokemon"]["name"], is_default, v["pokemon"]["url"])
    console.print(table)
    console.print(
        "\n[dim]Inspect a variety with: pokecli pokemon form get <variety-name>[/dim]"
    )


def render_pokemon_form(form: PokemonForm, console: Console) -> None:
    display_name = format_name(form.name)
    console.print(Panel(panel_title(form.id, f"{display_name} (Form)"), expand=False))

    table = create_key_value_table()
    table.add_row("Name", form.name)
    if form.form_name:
        table.add_row("Form Name", form.form_name)
    table.add_row("Base Pokemon", form.pokemon.name)
    table.add_row("Version Group", form.version_group.name)
    table.add_row("Default Form", "yes" if form.is_default else "no")
    table.add_row("Battle Only", "yes" if form.is_battle_only else "no")
    table.add_row("Mega", "yes" if form.is_mega else "no")
    if form.types:
        type_names = ", ".join(t.type.name for t in form.types)
        table.add_row("Types", type_names)
    console.print(table)

    if form.sprites and form.sprites.front_default:
        console.print(f"[dim]Sprite:[/dim] {form.sprites.front_default}")
