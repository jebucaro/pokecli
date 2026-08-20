from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pokecli.display.common import create_key_value_table, format_name, panel_title
from pokecli.models.location import Location, LocationArea, Region

_STYLE_HEADER = "bold cyan"


def render_region(region: Region, console: Console) -> None:
    title = format_name(region.name)
    console.print(Panel(panel_title(region.id, f"{title} Region"), expand=False))

    info = create_key_value_table()
    info.add_row("Name", region.name)
    if region.main_generation:
        info.add_row("Main Generation", region.main_generation.name)
    if region.pokedexes:
        info.add_row("Pokedexes", ", ".join(p.name for p in region.pokedexes))
    if region.version_groups:
        info.add_row(
            "Version Groups", ", ".join(vg.name for vg in region.version_groups)
        )
    console.print(info)

    if region.locations:
        console.print(f"\n[bold]Locations ({len(region.locations)})[/bold]")
        loc_table = Table(show_lines=False, box=None)
        loc_table.add_column("Name", style=_STYLE_HEADER)
        for loc in region.locations:
            loc_table.add_row(loc.name)
        console.print(loc_table)


def render_location(loc: Location, console: Console) -> None:
    title = format_name(loc.name)
    console.print(Panel(panel_title(loc.id, title), expand=False))

    info = create_key_value_table()
    info.add_row("Name", loc.name)
    if loc.region:
        info.add_row("Region", loc.region.name)
    console.print(info)

    if loc.areas:
        console.print(f"\n[bold]Areas ({len(loc.areas)})[/bold]")
        area_table = Table(show_lines=False, box=None)
        area_table.add_column("Name", style=_STYLE_HEADER)
        for area in loc.areas:
            area_table.add_row(area.name)
        console.print(area_table)
    else:
        console.print("\n[dim]No sub-areas listed for this location.[/dim]")


def render_location_area(area: LocationArea, console: Console) -> None:
    title = format_name(area.name)
    console.print(Panel(panel_title(area.id, title), expand=False))

    info = create_key_value_table()
    info.add_row("Name", area.name)
    info.add_row("Location", area.location.name)
    info.add_row("Game Index", str(area.game_index))
    console.print(info)

    if not area.pokemon_encounters:
        console.print("\n[dim]No Pokemon encounters recorded for this area.[/dim]")
        return

    console.print(
        f"\n[bold]Pokemon Encounters ({len(area.pokemon_encounters)} species)[/bold]"
    )
    enc_table = Table(show_lines=False)
    enc_table.add_column("Pokemon", style=_STYLE_HEADER)
    enc_table.add_column("Version", style="dim")
    enc_table.add_column("Method", style="white")
    enc_table.add_column("Chance", justify="right")
    enc_table.add_column("Levels", justify="right", style="dim")

    for enc in area.pokemon_encounters:
        for vd in enc.version_details:
            for d in vd.encounter_details:
                level = (
                    str(d.min_level)
                    if d.min_level == d.max_level
                    else f"{d.min_level}-{d.max_level}"
                )
                enc_table.add_row(
                    enc.pokemon.name,
                    vd.version.name,
                    d.method.name,
                    f"{d.chance}%",
                    level,
                )
    console.print(enc_table)


def render_encounters(pokemon_name: str, encounters: list, console: Console) -> None:
    """Render `/pokemon/{id}/encounters/` response (list of dicts)."""
    title = format_name(pokemon_name)
    console.print(Panel(f"[bold]{title} - Encounter Locations[/bold]", expand=False))

    if not encounters:
        console.print("[dim]No recorded encounter locations.[/dim]")
        return

    table = Table(show_lines=False)
    table.add_column("Location Area", style=_STYLE_HEADER)
    table.add_column("Version", style="dim")
    table.add_column("Method", style="white")
    table.add_column("Chance", justify="right")
    table.add_column("Levels", justify="right", style="dim")

    for entry in encounters:
        area_name = entry["location_area"]["name"]
        for vd in entry.get("version_details", []):
            version = vd["version"]["name"]
            for d in vd.get("encounter_details", []):
                method = d["method"]["name"]
                level = (
                    str(d["min_level"])
                    if d["min_level"] == d["max_level"]
                    else f"{d['min_level']}-{d['max_level']}"
                )
                table.add_row(area_name, version, method, f"{d['chance']}%", level)
    console.print(table)
    console.print(f"\n[dim]Total: {len(encounters)} location areas[/dim]")
