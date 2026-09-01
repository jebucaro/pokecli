"""Contextual disclosure: next-step command suggestions after output."""

from typing import Callable


def _hints_pokemon_get(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    return [
        f"pokecli pokemon moves {name}",
        f"pokecli pokemon evolution {name}",
        f"pokecli pokemon encounters {name}",
    ]


def _hints_pokemon_moves(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    return [
        f"pokecli pokemon can-learn {name} <move_name>",
        f"pokecli pokemon get {name}",
    ]


def _hints_pokemon_species(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    return [
        f"pokecli pokemon evolution {name}",
        f"pokecli pokemon forms {name}",
    ]


def _hints_pokemon_evolution(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    return [
        f"pokecli pokemon get {name}",
        f"pokecli pokemon species {name}",
    ]


def _hints_pokemon_encounters(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    first_area = ctx.get("first_area")
    area_hint = f"pokecli location area get {first_area}" if first_area else "pokecli location area get <area_name>"
    return [area_hint, f"pokecli pokemon get {name}"]


def _hints_pokemon_forms(ctx: dict) -> list[str]:
    first_variety = ctx.get("first_variety")
    variety_hint = f"pokecli pokemon form get {first_variety}" if first_variety else "pokecli pokemon form get <variety>"
    return [variety_hint]


def _hints_move_get(ctx: dict) -> list[str]:
    name = ctx.get("name", "")
    type_name = ctx.get("type")
    hints = [f"pokecli pokemon can-learn <pokemon_name> {name}"]
    if type_name:
        hints.append(f"pokecli type get {type_name}")
    return hints


def _hints_ability_get(ctx: dict) -> list[str]:
    return ["pokecli pokemon get <pokemon_name>"]


def _hints_item_get(ctx: dict) -> list[str]:
    return ["pokecli item list"]


def _hints_type_get(ctx: dict) -> list[str]:
    hints: list[str] = []
    super_effective = ctx.get("super_effective")
    if super_effective and len(super_effective) > 0:
        hints.append(f"pokecli type get {super_effective[0]}")
    hints.append("pokecli pokemon list")
    return hints


def _hints_berry_get(ctx: dict) -> list[str]:
    return ["pokecli berry list"]


def _hints_nature_get(ctx: dict) -> list[str]:
    return ["pokecli nature list"]


def _hints_location_get(ctx: dict) -> list[str]:
    first_area = ctx.get("first_area")
    if first_area:
        return [f"pokecli location area get {first_area}"]
    return []


def _hints_location_area_get(ctx: dict) -> list[str]:
    location = ctx.get("location")
    if location:
        return [f"pokecli location get {location}"]
    return ["pokecli location get <parent>"]


def _hints_region_get(ctx: dict) -> list[str]:
    first_location = ctx.get("first_location")
    if first_location:
        return [f"pokecli location get {first_location}"]
    return []


def _hints_generation_get(ctx: dict) -> list[str]:
    return ["pokecli game pokedex get <pokedex>"]


def _hints_pokedex_get(ctx: dict) -> list[str]:
    return ["pokecli pokemon get <species>"]


_HINT_BUILDERS: dict[str, Callable[[dict], list[str]]] = {
    "pokemon.get": _hints_pokemon_get,
    "pokemon.moves": _hints_pokemon_moves,
    "pokemon.species": _hints_pokemon_species,
    "pokemon.evolution": _hints_pokemon_evolution,
    "pokemon.encounters": _hints_pokemon_encounters,
    "pokemon.forms": _hints_pokemon_forms,
    "move.get": _hints_move_get,
    "ability.get": _hints_ability_get,
    "item.get": _hints_item_get,
    "type.get": _hints_type_get,
    "berry.get": _hints_berry_get,
    "nature.get": _hints_nature_get,
    "location.get": _hints_location_get,
    "location_area.get": _hints_location_area_get,
    "region.get": _hints_region_get,
    "generation.get": _hints_generation_get,
    "pokedex.get": _hints_pokedex_get,
}


def get_hints(command: str, context: dict) -> list[str]:
    """Return 2-3 next-step command suggestions based on current command and context.

    Args:
        command: The command that just ran (e.g., 'pokemon.get', 'move.get', 'pokemon.moves')
        context: Dict with relevant data like resource name, available sub-data, etc.

    Returns:
        List of command suggestion strings like 'pokecli pokemon moves pikachu'
    """
    builder = _HINT_BUILDERS.get(command)
    if builder:
        return builder(context)

    # Wildcard list commands
    if command.endswith(".list"):
        resource = context.get("resource", "")
        first_name = context.get("first_name")
        if first_name:
            return [f"pokecli {resource} get {first_name}"]
        return []

    return []


def format_hints_toon(hints: list[str]) -> str:
    """Format hints as a real TOON ``help[]`` array via ``toons.dumps``.

    Produces a spec-compliant inline array, e.g.:
    help[3]: pokecli pokemon moves pikachu,pokecli pokemon evolution pikachu,...
    """
    if not hints:
        return ""
    import toons

    return toons.dumps({"help": hints})


def format_hints_table(hints: list[str]) -> str:
    """Format hints as dim Rich markup for table output.

    Example output:
    \n[dim]Next steps:[/dim]
    [dim]  → pokecli pokemon moves pikachu[/dim]
    [dim]  → pokecli pokemon evolution pikachu[/dim]
    """
    if not hints:
        return ""
    lines = ["\n[dim]Next steps:[/dim]"]
    for hint in hints:
        lines.append(f"[dim]  → {hint}[/dim]")
    return "\n".join(lines)
