from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pokecli.display.common import (
    create_key_value_table,
    english_name,
    format_name,
    panel_title,
)
from pokecli.models.game import Generation, Pokedex, Version, VersionGroup


def render_version(v: Version, console: Console) -> None:
    title = format_name(v.name)
    console.print(Panel(panel_title(v.id, f"Pokemon {title}"), expand=False))
    table = create_key_value_table()
    table.add_row("Name", v.name)
    en = english_name(v)
    if en and en != title:
        table.add_row("English", en)
    table.add_row("Version Group", v.version_group.name)
    console.print(table)


def render_version_group(vg: VersionGroup, console: Console) -> None:
    title = format_name(vg.name)
    console.print(Panel(panel_title(vg.id, f"{title} Version Group"), expand=False))

    table = create_key_value_table()
    table.add_row("Name", vg.name)
    table.add_row("Order", str(vg.order))
    table.add_row("Generation", vg.generation.name)
    console.print(table)

    if vg.versions:
        console.print("\n[bold]Versions[/bold]")
        console.print(", ".join(v.name for v in vg.versions))

    if vg.regions:
        console.print("\n[bold]Regions[/bold]")
        console.print(", ".join(r.name for r in vg.regions))


def render_generation(gen: Generation, console: Console) -> None:
    console.print(Panel(panel_title(gen.id, format_name(gen.name)), expand=False))

    info = create_key_value_table()
    info.add_row("Name", gen.name)
    info.add_row("Main Region", gen.main_region.name)
    info.add_row("Pokemon Introduced", str(len(gen.pokemon_species)))
    info.add_row("Moves Introduced", str(len(gen.moves)))
    info.add_row("Abilities Introduced", str(len(gen.abilities)))
    info.add_row("Types Introduced", str(len(gen.types)))
    if gen.version_groups:
        info.add_row("Version Groups", ", ".join(vg.name for vg in gen.version_groups))
    console.print(info)

    if gen.pokemon_species:
        console.print(f"\n[bold]Pokemon Species ({len(gen.pokemon_species)})[/bold]")
        console.print(", ".join(sorted(p.name for p in gen.pokemon_species)))

    if gen.moves:
        console.print(f"\n[bold]Moves ({len(gen.moves)})[/bold]")
        console.print(", ".join(sorted(m.name for m in gen.moves)))


def render_pokedex(pdx: Pokedex, console: Console) -> None:
    title = format_name(pdx.name)
    console.print(Panel(panel_title(pdx.id, f"{title} Pokedex"), expand=False))

    info = create_key_value_table()
    info.add_row("Name", pdx.name)
    info.add_row("Main Series", "yes" if pdx.is_main_series else "no")
    if pdx.region:
        info.add_row("Region", pdx.region.name)
    if pdx.version_groups:
        info.add_row("Version Groups", ", ".join(vg.name for vg in pdx.version_groups))
    console.print(info)

    if not pdx.pokemon_entries:
        console.print("\n[dim]No entries in this pokedex.[/dim]")
        return

    console.print(f"\n[bold]Entries ({len(pdx.pokemon_entries)})[/bold]")
    entry_table = Table(show_lines=False)
    entry_table.add_column("#", justify="right", style="dim")
    entry_table.add_column("Species", style="bold cyan")
    for entry in pdx.pokemon_entries:
        entry_table.add_row(str(entry.entry_number), entry.pokemon_species.name)
    console.print(entry_table)
