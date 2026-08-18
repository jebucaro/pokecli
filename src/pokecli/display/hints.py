"""Contextual disclosure: next-step command suggestions after output."""


def get_hints(command: str, context: dict) -> list[str]:
    """Return 2-3 next-step command suggestions based on current command and context.

    Args:
        command: The command that just ran (e.g., 'pokemon.get', 'move.get', 'pokemon.moves')
        context: Dict with relevant data like resource name, available sub-data, etc.

    Returns:
        List of command suggestion strings like 'pokecli pokemon moves pikachu'
    """
    name = context.get("name", "")

    if command == "pokemon.get":
        return [
            f"pokecli pokemon moves {name}",
            f"pokecli pokemon evolution {name}",
            f"pokecli pokemon encounters {name}",
        ]

    if command == "pokemon.moves":
        return [
            f"pokecli pokemon can-learn {name} <move_name>",
            f"pokecli pokemon get {name}",
        ]

    if command == "pokemon.species":
        return [
            f"pokecli pokemon evolution {name}",
            f"pokecli pokemon forms {name}",
        ]

    if command == "pokemon.evolution":
        return [
            f"pokecli pokemon get {name}",
            f"pokecli pokemon species {name}",
        ]

    if command == "pokemon.encounters":
        first_area = context.get("first_area")
        area_hint = f"pokecli location area get {first_area}" if first_area else "pokecli location area get <area_name>"
        return [
            area_hint,
            f"pokecli pokemon get {name}",
        ]

    if command == "pokemon.forms":
        first_variety = context.get("first_variety")
        variety_hint = f"pokecli pokemon form get {first_variety}" if first_variety else "pokecli pokemon form get <variety>"
        return [variety_hint]

    if command == "move.get":
        type_name = context.get("type")
        hints = [f"pokecli pokemon can-learn <pokemon_name> {name}"]
        if type_name:
            hints.append(f"pokecli type get {type_name}")
        return hints

    if command == "ability.get":
        return ["pokecli pokemon get <pokemon_name>"]

    if command == "item.get":
        return ["pokecli item list"]

    if command == "type.get":
        hints: list[str] = []
        super_effective = context.get("super_effective")
        if super_effective and len(super_effective) > 0:
            hints.append(f"pokecli type get {super_effective[0]}")
        hints.append("pokecli pokemon list")
        return hints

    if command == "berry.get":
        return ["pokecli berry list"]

    if command == "nature.get":
        return ["pokecli nature list"]

    if command == "location.get":
        first_area = context.get("first_area")
        if first_area:
            return [f"pokecli location area get {first_area}"]
        return []

    if command == "location_area.get":
        location = context.get("location")
        if location:
            return [f"pokecli location get {location}"]
        return ["pokecli location get <parent>"]

    if command == "region.get":
        first_location = context.get("first_location")
        if first_location:
            return [f"pokecli location get {first_location}"]
        return []

    if command == "generation.get":
        return ["pokecli game pokedex get <pokedex>"]

    if command == "pokedex.get":
        return ["pokecli pokemon get <species>"]

    # Wildcard list commands
    if command.endswith(".list"):
        resource = context.get("resource", "")
        first_name = context.get("first_name")
        if first_name:
            return [f"pokecli {resource} get {first_name}"]
        return []

    return []


def format_hints_toon(hints: list[str]) -> str:
    """Format hints as TOON help[] block.

    Example output:
    help[3]:
      Run `pokecli pokemon moves pikachu`
      Run `pokecli pokemon evolution pikachu`
      Run `pokecli pokemon encounters pikachu`
    """
    if not hints:
        return ""
    lines = [f"help[{len(hints)}]:"]
    for hint in hints:
        lines.append(f"  Run `{hint}`")
    return "\n".join(lines)


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
