from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from pokecli.display.common import format_name, get_chars, uses_unicode
from pokecli.models.evolution import (
    ChainLink,
    EvolutionDetail,
    EvolutionChain,
    PokemonSpecies,
)


def _describe_trigger(detail: EvolutionDetail) -> str:
    trigger = detail.trigger.name
    parts = []

    if trigger == "level-up":
        if detail.min_level:
            parts.append(f"level {detail.min_level}")
        elif detail.min_happiness:
            parts.append(f"happiness {detail.min_happiness}")
        elif detail.min_beauty:
            parts.append(f"beauty {detail.min_beauty}")
        elif detail.min_affection:
            parts.append(f"affection {detail.min_affection}")
        elif detail.known_move:
            parts.append(f"knowing {detail.known_move.name}")
        elif detail.location:
            parts.append(f"at {detail.location.name}")
        else:
            parts.append("level-up")
        if detail.time_of_day:
            parts.append(f"({detail.time_of_day})")
        if detail.held_item:
            parts.append(f"holding {detail.held_item.name}")
        if detail.needs_overworld_rain:
            parts.append("(rain)")
        if detail.turn_upside_down:
            parts.append("(upside-down)")
    elif trigger == "use-item":
        if detail.item:
            parts.append(f"use {detail.item.name.replace('-', ' ')}")
        else:
            parts.append("use item")
    elif trigger == "trade":
        if detail.held_item:
            parts.append(f"trade holding {detail.held_item.name.replace('-', ' ')}")
        else:
            parts.append("trade")
    elif trigger == "shed":
        parts.append("shed (level 20, empty slot, Pokeball)")
    else:
        parts.append(trigger.replace("-", " "))

    return ", ".join(parts) if parts else trigger


def _render_chain(
    link: ChainLink,
    lines: list[str],
    prefix: str,
    is_last: bool,
    *,
    unicode: bool,
) -> None:
    connector = "\u2514\u2500 " if unicode else "+-- "
    pipe = "\u2502   " if unicode else "|   "
    tee = "\u251c\u2500 " if unicode else "+-- "

    name = link.species.name.capitalize()

    if not prefix and not link.evolution_details:
        lines.append(f"[bold white]{name}[/bold white]")
    else:
        trigger_str = ""
        if link.evolution_details:
            trigger_str = (
                f" [dim]({_describe_trigger(link.evolution_details[0])})[/dim]"
            )
        branch = connector if is_last else tee
        lines.append(f"{prefix}{branch}[bold white]{name}[/bold white]{trigger_str}")

    child_prefix = prefix + ("    " if is_last else pipe)
    for i, child in enumerate(link.evolves_to):
        _render_chain(
            child,
            lines,
            child_prefix,
            is_last=(i == len(link.evolves_to) - 1),
            unicode=unicode,
        )


def render_evolution(chain: EvolutionChain, console: Console) -> None:
    _uses_unicode = uses_unicode(console)
    header = f"[bold]Evolution Chain #{chain.id}[/bold]"
    console.print(Panel(header, expand=False))

    lines: list[str] = []
    _render_chain(chain.chain, lines, prefix="", is_last=True, unicode=_uses_unicode)
    for line in lines:
        console.print(line, highlight=False)


def render_species(species: PokemonSpecies, console: Console) -> None:
    chars = get_chars(console)
    dash = chars.dash

    header = Text()
    header.append(f"#{species.id}  ", style="dim")
    header.append(species.name.capitalize(), style="bold white")
    if species.is_legendary:
        header.append("  Legendary", style="bold yellow")
    if species.is_mythical:
        header.append("  Mythical", style="bold magenta")

    # Get English genus (e.g. "Seed Pokémon")
    english_genus = next(
        (
            g["genus"]
            for g in species.genera
            if g.get("language", {}).get("name") == "en"
        ),
        None,
    )
    if english_genus:
        header.append(f"  {dash} {english_genus}", style="dim")

    console.print(Panel(header, expand=False))

    # Core info line
    gender_str = _gender_rate(species.gender_rate)
    egg_groups = ", ".join(format_name(eg.name) for eg in species.egg_groups)
    happiness = (
        str(species.base_happiness) if species.base_happiness is not None else dash
    )
    info = (
        f"[bold]Generation:[/bold] {format_name(species.generation.name)}   "
        f"[bold]Color:[/bold] {species.color.name.capitalize()}   "
        f"[bold]Growth Rate:[/bold] {format_name(species.growth_rate.name)}\n"
        f"[bold]Capture Rate:[/bold] {species.capture_rate}   "
        f"[bold]Base Happiness:[/bold] {happiness}   "
        f"[bold]Gender:[/bold] {gender_str}\n"
        f"[bold]Egg Groups:[/bold] {egg_groups}\n"
    )
    console.print(info)

    # Latest English flavor text
    english_flavor = [
        f
        for f in species.flavor_text_entries
        if f.get("language", {}).get("name") == "en"
    ]
    if english_flavor:
        entry = english_flavor[-1]
        text = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
        version = entry.get("version", {}).get("name", "")
        console.print(f'[dim italic]"{text}"[/dim italic]')
        if version:
            console.print(f"[dim]{dash} {version}[/dim]")


def _gender_rate(rate: int) -> str:
    """Convert gender_rate (-1 = genderless, 0-8 = female eighths) to readable string."""
    if rate == -1:
        return "Genderless"
    female_pct = rate / 8 * 100
    male_pct = 100 - female_pct
    return f"{male_pct:.0f}% M / {female_pct:.0f}% F"
