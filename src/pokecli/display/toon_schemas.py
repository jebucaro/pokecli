"""TOON schema transforms for each resource type.

Each function takes a Pydantic model instance and returns the data structures
needed by the TOON serializer core functions.
"""

from __future__ import annotations

from pokecli.models.pokemon import Pokemon, PokemonMoveEntry
from pokecli.models.move import Move
from pokecli.models.ability import Ability
from pokecli.models.item import Item
from pokecli.models.berry import Berry
from pokecli.models.evolution import EvolutionChain, ChainLink, EvolutionDetail, PokemonSpecies
from pokecli.models.location import Location, LocationArea, Region
from pokecli.models.common import ListResult
from pokecli.models.nature import Nature
from pokecli.models.type import PokemonType
from pokecli.models.game import Generation, Pokedex, Version, VersionGroup
from pokecli.models.machine import Machine
from pokecli.models.pokemon_form import PokemonForm


def _safe(value: object) -> str | None:
    """Convert a value to string or None."""
    if value is None:
        return None
    return str(value)


def pokemon_toon(pokemon: Pokemon) -> list[tuple[str, str | None]]:
    """Transform a Pokemon into TOON fields.

    Returns fields: id, name, types, abilities, stats (as hp/atk/def/spa/spd/spe)
    """
    types = "/".join(t.type.name for t in pokemon.types)
    abilities = "/".join(a.ability.name for a in pokemon.abilities)
    stats = "/".join(str(s.base_stat) for s in pokemon.stats)

    return [
        ("id", str(pokemon.id)),
        ("name", pokemon.name),
        ("types", types),
        ("abilities", abilities),
        ("stats", stats),
    ]


def move_toon(move: Move) -> list[tuple[str, str | None]]:
    """Transform a Move into TOON fields.

    Returns fields: id, name, type, class, power, accuracy, pp, effect
    """
    effect = None
    for entry in move.effect_entries:
        if entry.language.name == "en":
            effect = entry.short_effect
            break

    # Substitute effect_chance if present
    if effect and move.effect_chance is not None:
        effect = effect.replace("$effect_chance", str(move.effect_chance))

    return [
        ("id", str(move.id)),
        ("name", move.name),
        ("type", move.type.name),
        ("class", move.damage_class.name),
        ("power", _safe(move.power)),
        ("accuracy", _safe(move.accuracy)),
        ("pp", _safe(move.pp)),
        ("effect", effect),
    ]


def ability_toon(ability: Ability) -> list[tuple[str, str | None]]:
    """Transform an Ability into TOON fields.

    Returns fields: id, name, generation, pokemon_count, effect
    """
    effect = None
    for entry in ability.effect_entries:
        if entry.language.name == "en":
            effect = entry.short_effect
            break

    return [
        ("id", str(ability.id)),
        ("name", ability.name),
        ("generation", ability.generation.name),
        ("pokemon_count", str(len(ability.pokemon))),
        ("effect", effect),
    ]


def item_toon(item: Item) -> list[tuple[str, str | None]]:
    """Transform an Item into TOON fields.

    Returns fields: id, name, cost, category, effect
    """
    effect = None
    for entry in item.effect_entries:
        if entry.language.name == "en":
            effect = entry.short_effect
            break

    return [
        ("id", str(item.id)),
        ("name", item.name),
        ("cost", str(item.cost)),
        ("category", item.category.name),
        ("effect", effect),
    ]


def type_toon(type_data: PokemonType) -> list[tuple[str, str | None]]:
    """Transform a Type into TOON fields.

    Returns fields: id, name, double_damage_to, half_damage_to, no_damage_to,
                    double_damage_from, half_damage_from, no_damage_from
    """
    dr = type_data.damage_relations
    return [
        ("id", str(type_data.id)),
        ("name", type_data.name),
        ("double_damage_to", "/".join(t.name for t in dr.double_damage_to) or None),
        ("half_damage_to", "/".join(t.name for t in dr.half_damage_to) or None),
        ("no_damage_to", "/".join(t.name for t in dr.no_damage_to) or None),
        ("double_damage_from", "/".join(t.name for t in dr.double_damage_from) or None),
        ("half_damage_from", "/".join(t.name for t in dr.half_damage_from) or None),
        ("no_damage_from", "/".join(t.name for t in dr.no_damage_from) or None),
    ]


def berry_toon(berry: Berry) -> list[tuple[str, str | None]]:
    """Transform a Berry into TOON fields.

    Returns fields: id, name, firmness, growth_time, natural_gift_power, natural_gift_type, flavors
    """
    # Berry model doesn't have natural_gift_type directly, use item name fallback
    flavors = "/".join(
        f"{fv.flavor.name}:{fv.potency}" for fv in berry.flavors if fv.potency > 0
    )

    return [
        ("id", str(berry.id)),
        ("name", berry.name),
        ("firmness", berry.firmness.name),
        ("growth_time", f"{berry.growth_time}h"),
        ("natural_gift_power", str(berry.natural_gift_power)),
        ("natural_gift_type", None),
        ("flavors", flavors or None),
    ]


def nature_toon(nature: Nature) -> list[tuple[str, str | None]]:
    """Transform a Nature into TOON fields.

    Returns fields: id, name, increased_stat, decreased_stat, likes_flavor, hates_flavor
    """
    return [
        ("id", str(nature.id)),
        ("name", nature.name),
        ("increased_stat", nature.increased_stat.name if nature.increased_stat else None),
        ("decreased_stat", nature.decreased_stat.name if nature.decreased_stat else None),
        ("likes_flavor", nature.likes_flavor.name if nature.likes_flavor else None),
        ("hates_flavor", nature.hates_flavor.name if nature.hates_flavor else None),
    ]


def species_toon(species: PokemonSpecies) -> list[tuple[str, str | None]]:
    """Transform a PokemonSpecies into TOON fields.

    Returns fields: id, name, generation, capture_rate, base_happiness,
                    growth_rate, egg_groups, gender, flavor_text
    """
    egg_groups = "/".join(eg.name for eg in species.egg_groups)
    gender = _gender_rate(species.gender_rate)

    # Get latest English flavor text
    flavor_text = None
    english_entries = [
        f for f in species.flavor_text_entries
        if f.get("language", {}).get("name") == "en"
    ]
    if english_entries:
        text = english_entries[-1].get("flavor_text", "")
        flavor_text = text.replace("\n", " ").replace("\f", " ")

    return [
        ("id", str(species.id)),
        ("name", species.name),
        ("generation", species.generation.name),
        ("capture_rate", str(species.capture_rate)),
        ("base_happiness", _safe(species.base_happiness)),
        ("growth_rate", species.growth_rate.name),
        ("egg_groups", egg_groups or None),
        ("gender", gender),
        ("flavor_text", flavor_text),
    ]


def _gender_rate(rate: int) -> str:
    """Convert gender_rate (-1 = genderless, 0-8 = female eighths)."""
    if rate == -1:
        return "genderless"
    female_pct = rate / 8 * 100
    male_pct = 100 - female_pct
    return f"{male_pct:.0f}%M/{female_pct:.0f}%F"


def location_toon(location: Location) -> list[tuple[str, str | None]]:
    """Transform a Location into TOON fields.

    Returns fields: id, name, region, areas (count)
    """
    return [
        ("id", str(location.id)),
        ("name", location.name),
        ("region", location.region.name if location.region else None),
        ("areas", str(len(location.areas))),
    ]


def location_area_toon(area: LocationArea) -> list[tuple[str, str | None]]:
    """Transform a LocationArea into TOON fields.

    Returns fields: id, name, location, encounters_count
    """
    return [
        ("id", str(area.id)),
        ("name", area.name),
        ("location", area.location.name),
        ("encounters_count", str(len(area.pokemon_encounters))),
    ]


def region_toon(region: Region) -> list[tuple[str, str | None]]:
    """Transform a Region into TOON fields.

    Returns fields: id, name, main_generation, locations_count, pokedexes
    """
    pokedexes = "/".join(p.name for p in region.pokedexes)
    return [
        ("id", str(region.id)),
        ("name", region.name),
        ("main_generation", region.main_generation.name if region.main_generation else None),
        ("locations_count", str(len(region.locations))),
        ("pokedexes", pokedexes or None),
    ]


def generation_toon(generation: Generation) -> list[tuple[str, str | None]]:
    """Transform a Generation into TOON fields.

    Returns fields: id, name, main_region, pokemon_count, moves_count
    """
    return [
        ("id", str(generation.id)),
        ("name", generation.name),
        ("main_region", generation.main_region.name),
        ("pokemon_count", str(len(generation.pokemon_species))),
        ("moves_count", str(len(generation.moves))),
    ]


def pokedex_toon(pokedex: Pokedex) -> list[tuple[str, str | None]]:
    """Transform a Pokedex into TOON fields.

    Returns fields: id, name, region, entries_count
    """
    return [
        ("id", str(pokedex.id)),
        ("name", pokedex.name),
        ("region", pokedex.region.name if pokedex.region else None),
        ("entries_count", str(len(pokedex.pokemon_entries))),
    ]


def version_toon(version: Version) -> list[tuple[str, str | None]]:
    """Transform a Version into TOON fields.

    Returns fields: id, name, version_group
    """
    return [
        ("id", str(version.id)),
        ("name", version.name),
        ("version_group", version.version_group.name),
    ]


def version_group_toon(vg: VersionGroup) -> list[tuple[str, str | None]]:
    """Transform a VersionGroup into TOON fields.

    Returns fields: id, name, generation, regions, versions
    """
    regions = "/".join(r.name for r in vg.regions)
    versions = "/".join(v.name for v in vg.versions)
    return [
        ("id", str(vg.id)),
        ("name", vg.name),
        ("generation", vg.generation.name),
        ("regions", regions or None),
        ("versions", versions or None),
    ]


def machine_toon(machine: Machine) -> list[tuple[str, str | None]]:
    """Transform a Machine into TOON fields.

    Returns fields: id, item, move, version_group
    """
    return [
        ("id", str(machine.id)),
        ("item", machine.item.name),
        ("move", machine.move.name),
        ("version_group", machine.version_group.name),
    ]


def pokemon_form_toon(form: PokemonForm) -> list[tuple[str, str | None]]:
    """Transform a PokemonForm into TOON fields.

    Returns fields: id, name, form_name, pokemon, types, is_mega, is_battle_only
    """
    types = "/".join(t.type.name for t in form.types) if form.types else None
    return [
        ("id", str(form.id)),
        ("name", form.name),
        ("form_name", form.form_name or None),
        ("pokemon", form.pokemon.name),
        ("types", types),
        ("is_mega", str(form.is_mega).lower()),
        ("is_battle_only", str(form.is_battle_only).lower()),
    ]


# --- Evolution chain tree ---


def _describe_trigger(detail: EvolutionDetail) -> str:
    """Describe an evolution trigger in plain text."""
    trigger = detail.trigger.name
    parts: list[str] = []

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


def _render_chain_plain(link: ChainLink, lines: list[str], depth: int) -> None:
    """Recursively render an evolution chain as plain text tree lines."""
    name = link.species.name.capitalize()

    if depth == 0:
        lines.append(name)
    else:
        indent = "  " * depth
        trigger_str = ""
        if link.evolution_details:
            trigger_str = f" ({_describe_trigger(link.evolution_details[0])})"
        lines.append(f"{indent}-> {name}{trigger_str}")

    for child in link.evolves_to:
        _render_chain_plain(child, lines, depth + 1)


def evolution_chain_toon(chain: EvolutionChain) -> tuple[str, list[str]]:
    """Transform an EvolutionChain into a label and tree lines for toon_tree().

    Returns: (label, tree_lines)
    """
    lines: list[str] = []
    _render_chain_plain(chain.chain, lines, depth=0)
    return f"evolution_chain_{chain.id}", lines


# --- List schemas ---


def pokemon_moves_toon(
    name: str, moves: list[PokemonMoveEntry]
) -> tuple[list[str], list[list[str | None]]]:
    """Transform Pokemon move entries into list schema.

    Returns: (schema_fields, rows)
    schema_fields: [name, method, level]
    """
    schema_fields = ["name", "method", "level"]
    rows: list[list[str | None]] = []
    for m in moves:
        level_str = str(m.level) if m.level > 0 else None
        rows.append([m.name, m.learn_method, level_str])
    return schema_fields, rows


def encounters_toon(
    pokemon_name: str, encounters: list[dict]
) -> tuple[list[str], list[list[str | None]]]:
    """Transform encounter data into list schema.

    Expects the raw encounter response from PokeAPI:
    [{"location_area": {"name": ...}, "version_details": [...]}]

    Returns: (schema_fields, rows)
    schema_fields: [area, version, method, chance, levels]
    """
    schema_fields = ["area", "version", "method", "chance", "levels"]
    rows: list[list[str | None]] = []

    for enc in encounters:
        area_name = enc.get("location_area", {}).get("name", "-")
        for vd in enc.get("version_details", []):
            version = vd.get("version", {}).get("name", "-")
            for ed in vd.get("encounter_details", []):
                method = ed.get("method", {}).get("name", "-")
                chance = f"{ed.get('chance', 0)}%"
                min_lvl = ed.get("min_level", 0)
                max_lvl = ed.get("max_level", 0)
                if min_lvl == max_lvl:
                    levels = str(min_lvl)
                else:
                    levels = f"{min_lvl}-{max_lvl}"
                rows.append([area_name, version, method, chance, levels])

    return schema_fields, rows


def resource_list_toon(result: ListResult) -> tuple[list[str], list[list[str]]]:
    """Transform a ListResult into list schema.

    Returns: (schema_fields, rows)
    schema_fields: [name]
    """
    schema_fields = ["name"]
    rows: list[list[str]] = [[r.name] for r in result.results]
    return schema_fields, rows
