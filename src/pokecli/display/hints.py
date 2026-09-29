"""Contextual disclosure: next-step command suggestions after output.

Every string emitted here is a command an agent may run next, so each one must
use the canonical verb-first grammar. ``tests/unit/display/test_hints.py``
asserts that, since these paths live in strings and so cannot be caught by a
signature change.
"""

from typing import Callable

# Placeholders for values the current response does not supply. Kept in angle
# brackets so they read as arguments to fill in rather than literal names.
POKEMON_PLACEHOLDER = "<pokemon_name>"
MOVE_PLACEHOLDER = "<move_name>"


def _hints_get_pokemon(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    return [
        f"pokecli moves {name}",
        f"pokecli evolution {name}",
        f"pokecli encounters {name}",
    ]


def _hints_get_pokemon_species(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    return [
        f"pokecli evolution {name}",
        f"pokecli forms {name}",
    ]


def _hints_get_evolution_chain(ctx: dict) -> list[str]:
    base = ctx.get("base_species")
    if base:
        return [f"pokecli evolution {base}", f"pokecli get pokemon {base}"]
    return ["pokecli get pokemon <species>"]


def _hints_get_move(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    type_name = ctx.get("type")
    hints = [f"pokecli can-learn {POKEMON_PLACEHOLDER} {name}"]
    if type_name:
        hints.append(f"pokecli get type {type_name}")
    return hints


def _hints_get_ability(ctx: dict) -> list[str]:
    return [f"pokecli get pokemon {POKEMON_PLACEHOLDER}"]


def _hints_get_item(ctx: dict) -> list[str]:
    return ["pokecli search item <query>"]


def _hints_get_type(ctx: dict) -> list[str]:
    hints: list[str] = []
    super_effective = ctx.get("super_effective")
    if super_effective:
        hints.append(f"pokecli get type {super_effective[0]}")
    hints.append("pokecli list pokemon")
    return hints


def _hints_get_berry(ctx: dict) -> list[str]:
    return ["pokecli list berry"]


def _hints_get_nature(ctx: dict) -> list[str]:
    return ["pokecli list nature"]


def _hints_get_location(ctx: dict) -> list[str]:
    first_area = ctx.get("first_area")
    if first_area:
        return [f"pokecli get location-area {first_area}"]
    return []


def _hints_get_location_area(ctx: dict) -> list[str]:
    location = ctx.get("location")
    if location:
        return [f"pokecli get location {location}"]
    return ["pokecli get location <parent>"]


def _hints_get_region(ctx: dict) -> list[str]:
    first_location = ctx.get("first_location")
    if first_location:
        return [f"pokecli get location {first_location}"]
    return []


def _hints_get_generation(ctx: dict) -> list[str]:
    return ["pokecli get pokedex <pokedex>"]


def _hints_get_pokedex(ctx: dict) -> list[str]:
    return [f"pokecli get pokemon-species {POKEMON_PLACEHOLDER}"]


def _hints_get_pokemon_form(ctx: dict) -> list[str]:
    return [f"pokecli get pokemon {POKEMON_PLACEHOLDER}"]


def _hints_moves(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    game = ctx.get("game")
    scope = f" --game {game}" if game else ""
    return [
        f"pokecli can-learn {name} {MOVE_PLACEHOLDER}{scope}",
        f"pokecli get pokemon {name}",
    ]


def _hints_evolution(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    return [
        f"pokecli get pokemon {name}",
        f"pokecli get pokemon-species {name}",
    ]


def _hints_encounters(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    first_area = ctx.get("first_area")
    area_hint = (
        f"pokecli get location-area {first_area}"
        if first_area
        else "pokecli get location-area <area_name>"
    )
    return [area_hint, f"pokecli get pokemon {name}"]


def _hints_forms(ctx: dict) -> list[str]:
    first_variety = ctx.get("first_variety")
    if first_variety:
        return [f"pokecli get pokemon-form {first_variety}"]
    return ["pokecli get pokemon-form <variety>"]


_HINT_BUILDERS: dict[str, Callable[[dict], list[str]]] = {
    # Resource reads, keyed by `get.<resource>`.
    "get.pokemon": _hints_get_pokemon,
    "get.pokemon-species": _hints_get_pokemon_species,
    "get.pokemon-form": _hints_get_pokemon_form,
    "get.evolution-chain": _hints_get_evolution_chain,
    "get.move": _hints_get_move,
    "get.ability": _hints_get_ability,
    "get.item": _hints_get_item,
    "get.type": _hints_get_type,
    "get.berry": _hints_get_berry,
    "get.nature": _hints_get_nature,
    "get.location": _hints_get_location,
    "get.location-area": _hints_get_location_area,
    "get.region": _hints_get_region,
    "get.generation": _hints_get_generation,
    "get.pokedex": _hints_get_pokedex,
    # Derived commands, keyed by command name.
    "moves": _hints_moves,
    "evolution": _hints_evolution,
    "encounters": _hints_encounters,
    "forms": _hints_forms,
}


def get_hints(command: str, context: dict) -> list[str]:
    """Return next-step command suggestions for the command that just ran.

    Args:
        command: Command identifier - ``get.<resource>``, ``list.<resource>``,
            ``search.<resource>``, or a derived command name like ``moves``.
        context: Resolved values from the response, such as ``name`` or
            ``first_area``, used to make hints concrete.

    Returns:
        Canonical command strings, for example ``pokecli moves pikachu``.
    """
    builder = _HINT_BUILDERS.get(command)
    if builder:
        return builder(context)

    # `list` and `search` share one shape across every resource: point at a
    # concrete record from the page just returned.
    if command.startswith(("list.", "search.")):
        resource = context.get("resource", "")
        first_name = context.get("first_name")
        if resource and first_name:
            return [f"pokecli get {resource} {first_name}"]
        return []

    return []


def format_hints_toon(hints: list[str]) -> str:
    """Format hints as a real TOON ``help[]`` array via ``toons.dumps``.

    Produces a spec-compliant inline array, e.g.:
    help[3]: pokecli moves pikachu,pokecli evolution pikachu,...
    """
    if not hints:
        return ""
    import toons

    return toons.dumps({"help": hints})


def format_hints_table(hints: list[str]) -> str:
    """Format hints as dim Rich markup for table output.

    Example output:
    \n[dim]Next steps:[/dim]
    [dim]  → pokecli moves pikachu[/dim]
    """
    if not hints:
        return ""
    lines = ["\n[dim]Next steps:[/dim]"]
    for hint in hints:
        lines.append(f"[dim]  → {hint}[/dim]")
    return "\n".join(lines)
