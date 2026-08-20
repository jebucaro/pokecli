"""Shared evolution trigger description logic used by both rich and toon renderers."""

from pokecli.models.evolution import EvolutionDetail


def describe_level_up(detail: EvolutionDetail) -> list[str]:
    """Build description parts for a level-up evolution trigger."""
    parts: list[str] = []
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
    return parts


def describe_trigger(detail: EvolutionDetail) -> str:
    """Describe an evolution trigger in plain text."""
    trigger = detail.trigger.name

    if trigger == "level-up":
        parts = describe_level_up(detail)
    elif trigger == "use-item":
        if detail.item:
            parts = [f"use {detail.item.name.replace('-', ' ')}"]
        else:
            parts = ["use item"]
    elif trigger == "trade":
        if detail.held_item:
            parts = [f"trade holding {detail.held_item.name.replace('-', ' ')}"]
        else:
            parts = ["trade"]
    elif trigger == "shed":
        parts = ["shed (level 20, empty slot, Pokeball)"]
    else:
        parts = [trigger.replace("-", " ")]

    return ", ".join(parts) if parts else trigger
