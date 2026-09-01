"""TOON schema transforms for each resource type.

Each function takes a Pydantic model instance and returns native Python data
structures (dicts for single resources, ``list[dict]`` for tabular lists) that
are handed directly to ``toons.dumps``. ``None`` values are preserved so the
``toons`` serializer renders them as ``null``.
"""

from __future__ import annotations

from pokecli.models.pokemon import Pokemon, PokemonMoveEntry
from pokecli.models.move import Move
from pokecli.models.ability import Ability
from pokecli.models.item import Item
from pokecli.models.berry import Berry
from pokecli.models.evolution import EvolutionChain, ChainLink, PokemonSpecies
from pokecli.display._evolution_helpers import describe_trigger as _describe_trigger
from pokecli.models.location import Location, LocationArea, Region
from pokecli.models.common import ListResult
from pokecli.models.nature import Nature
from pokecli.models.type import PokemonType
from pokecli.models.game import Generation, Pokedex, Version, VersionGroup
from pokecli.models.machine import Machine
from pokecli.models.pokemon_form import PokemonForm


def pokemon_toon(pokemon: Pokemon) -> dict:
    """Transform a Pokemon into TOON fields.

    Fields: id, name, types, abilities, stats (labeled as hp/atk/def/spa/spd/spe).
    """
    types = "/".join(t.type.name for t in pokemon.types)

    ability_parts = []
    for a in pokemon.abilities:
        label = a.ability.name
        if a.is_hidden:
            label += "(H)"
        ability_parts.append(label)
    abilities = "/".join(ability_parts)

    stat_labels = ("hp", "atk", "def", "spa", "spd", "spe")
    stats = "/".join(
        f"{label}:{s.base_stat}" for label, s in zip(stat_labels, pokemon.stats)
    )

    return {
        "id": pokemon.id,
        "name": pokemon.name,
        "types": types,
        "abilities": abilities,
        "stats": stats,
    }


def move_toon(move: Move) -> dict:
    """Transform a Move into TOON fields.

    Fields: id, name, type, class, power, accuracy, pp, effect.
    """
    effect = None
    for entry in move.effect_entries:
        if entry.language.name == "en":
            effect = entry.short_effect
            break

    # Substitute effect_chance if present
    if effect and move.effect_chance is not None:
        effect = effect.replace("$effect_chance", str(move.effect_chance))

    return {
        "id": move.id,
        "name": move.name,
        "type": move.type.name,
        "class": move.damage_class.name,
        "power": move.power,
        "accuracy": move.accuracy,
        "pp": move.pp,
        "effect": effect,
    }


def ability_toon(ability: Ability) -> dict:
    """Transform an Ability into TOON fields.

    Fields: id, name, generation, pokemon_count, effect.
    """
    effect = None
    for entry in ability.effect_entries:
        if entry.language.name == "en":
            effect = entry.short_effect
            break

    return {
        "id": ability.id,
        "name": ability.name,
        "generation": ability.generation.name,
        "pokemon_count": len(ability.pokemon),
        "effect": effect,
    }


def item_toon(item: Item) -> dict:
    """Transform an Item into TOON fields.

    Fields: id, name, cost, category, effect.
    """
    effect = None
    for entry in item.effect_entries:
        if entry.language.name == "en":
            effect = entry.short_effect
            break

    return {
        "id": item.id,
        "name": item.name,
        "cost": item.cost,
        "category": item.category.name,
        "effect": effect,
    }


def type_toon(type_data: PokemonType) -> dict:
    """Transform a Type into TOON fields.

    Fields: id, name, double_damage_to, half_damage_to, no_damage_to,
    double_damage_from, half_damage_from, no_damage_from.
    """
    dr = type_data.damage_relations
    return {
        "id": type_data.id,
        "name": type_data.name,
        "double_damage_to": "/".join(t.name for t in dr.double_damage_to) or None,
        "half_damage_to": "/".join(t.name for t in dr.half_damage_to) or None,
        "no_damage_to": "/".join(t.name for t in dr.no_damage_to) or None,
        "double_damage_from": "/".join(t.name for t in dr.double_damage_from) or None,
        "half_damage_from": "/".join(t.name for t in dr.half_damage_from) or None,
        "no_damage_from": "/".join(t.name for t in dr.no_damage_from) or None,
    }


def berry_toon(berry: Berry) -> dict:
    """Transform a Berry into TOON fields.

    Fields: id, name, firmness, growth_time, natural_gift_power,
    natural_gift_type, flavors.
    """
    flavors = "/".join(
        f"{fv.flavor.name}:{fv.potency}" for fv in berry.flavors if fv.potency > 0
    )

    return {
        "id": berry.id,
        "name": berry.name,
        "firmness": berry.firmness.name,
        "growth_time": f"{berry.growth_time}h",
        "natural_gift_power": berry.natural_gift_power,
        "natural_gift_type": None,
        "flavors": flavors or None,
    }


def nature_toon(nature: Nature) -> dict:
    """Transform a Nature into TOON fields.

    Fields: id, name, increased_stat, decreased_stat, likes_flavor, hates_flavor.
    """
    return {
        "id": nature.id,
        "name": nature.name,
        "increased_stat": nature.increased_stat.name if nature.increased_stat else None,
        "decreased_stat": nature.decreased_stat.name if nature.decreased_stat else None,
        "likes_flavor": nature.likes_flavor.name if nature.likes_flavor else None,
        "hates_flavor": nature.hates_flavor.name if nature.hates_flavor else None,
    }


def species_toon(species: PokemonSpecies) -> dict:
    """Transform a PokemonSpecies into TOON fields.

    Fields: id, name, generation, capture_rate, base_happiness, growth_rate,
    egg_groups, gender, flavor_text.
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

    return {
        "id": species.id,
        "name": species.name,
        "generation": species.generation.name,
        "capture_rate": species.capture_rate,
        "base_happiness": species.base_happiness,
        "growth_rate": species.growth_rate.name,
        "egg_groups": egg_groups or None,
        "gender": gender,
        "flavor_text": flavor_text,
    }


def _gender_rate(rate: int) -> str:
    """Convert gender_rate (-1 = genderless, 0-8 = female eighths)."""
    if rate == -1:
        return "genderless"
    female_pct = rate / 8 * 100
    male_pct = 100 - female_pct
    return f"{male_pct:.0f}%M/{female_pct:.0f}%F"


def location_toon(location: Location) -> dict:
    """Transform a Location into TOON fields.

    Fields: id, name, region, areas (count).
    """
    return {
        "id": location.id,
        "name": location.name,
        "region": location.region.name if location.region else None,
        "areas": len(location.areas),
    }


def location_area_toon(area: LocationArea) -> dict:
    """Transform a LocationArea into TOON fields.

    Fields: id, name, location, encounters_count.
    """
    return {
        "id": area.id,
        "name": area.name,
        "location": area.location.name,
        "encounters_count": len(area.pokemon_encounters),
    }


def region_toon(region: Region) -> dict:
    """Transform a Region into TOON fields.

    Fields: id, name, main_generation, locations_count, pokedexes.
    """
    pokedexes = "/".join(p.name for p in region.pokedexes)
    return {
        "id": region.id,
        "name": region.name,
        "main_generation": region.main_generation.name if region.main_generation else None,
        "locations_count": len(region.locations),
        "pokedexes": pokedexes or None,
    }


def generation_toon(generation: Generation) -> dict:
    """Transform a Generation into TOON fields.

    Fields: id, name, main_region, pokemon_count, moves_count.
    """
    return {
        "id": generation.id,
        "name": generation.name,
        "main_region": generation.main_region.name,
        "pokemon_count": len(generation.pokemon_species),
        "moves_count": len(generation.moves),
    }


def pokedex_toon(pokedex: Pokedex) -> dict:
    """Transform a Pokedex into TOON fields.

    Fields: id, name, region, entries_count.
    """
    return {
        "id": pokedex.id,
        "name": pokedex.name,
        "region": pokedex.region.name if pokedex.region else None,
        "entries_count": len(pokedex.pokemon_entries),
    }


def version_toon(version: Version) -> dict:
    """Transform a Version into TOON fields.

    Fields: id, name, version_group.
    """
    return {
        "id": version.id,
        "name": version.name,
        "version_group": version.version_group.name,
    }


def version_group_toon(vg: VersionGroup) -> dict:
    """Transform a VersionGroup into TOON fields.

    Fields: id, name, generation, regions, versions.
    """
    regions = "/".join(r.name for r in vg.regions)
    versions = "/".join(v.name for v in vg.versions)
    return {
        "id": vg.id,
        "name": vg.name,
        "generation": vg.generation.name,
        "regions": regions or None,
        "versions": versions or None,
    }


def machine_toon(machine: Machine) -> dict:
    """Transform a Machine into TOON fields.

    Fields: id, item, move, version_group.
    """
    return {
        "id": machine.id,
        "item": machine.item.name,
        "move": machine.move.name,
        "version_group": machine.version_group.name,
    }


def pokemon_form_toon(form: PokemonForm) -> dict:
    """Transform a PokemonForm into TOON fields.

    Fields: id, name, form_name, pokemon, types, is_mega, is_battle_only.
    """
    types = "/".join(t.type.name for t in form.types) if form.types else None
    return {
        "id": form.id,
        "name": form.name,
        "form_name": form.form_name or None,
        "pokemon": form.pokemon.name,
        "types": types,
        "is_mega": form.is_mega,
        "is_battle_only": form.is_battle_only,
    }


# --- Evolution chain tree ---


def _chain_to_node(link: ChainLink) -> dict:
    """Recursively convert an evolution ChainLink into a nested dict.

    Each node carries its species name, the trigger that produced it (``null``
    for the base species), and a list of ``evolves_to`` child nodes. This nested
    structure is rendered by ``toons`` as an expanded object tree.
    """
    trigger = None
    if link.evolution_details:
        trigger = _describe_trigger(link.evolution_details[0])

    node: dict = {
        "name": link.species.name,
        "trigger": trigger,
    }
    if link.evolves_to:
        node["evolves_to"] = [_chain_to_node(child) for child in link.evolves_to]
    return node


def evolution_chain_toon(chain: EvolutionChain) -> tuple[str, dict]:
    """Transform an EvolutionChain into a label and nested node dict.

    Returns: (label, node) where node is a nested dict suitable for
    ``toons.dumps({label: node})``.
    """
    return f"evolution_chain_{chain.id}", _chain_to_node(chain.chain)


# --- List schemas (return list[dict] for tabular rendering) ---


def pokemon_moves_toon(
    _name: str, moves: list[PokemonMoveEntry]
) -> list[dict]:
    """Transform Pokemon move entries into a uniform list of dicts.

    Columns: name, method, level.
    """
    rows: list[dict] = []
    for m in moves:
        rows.append({
            "name": m.name,
            "method": m.learn_method,
            "level": m.level if m.level > 0 else None,
        })
    return rows


def encounters_toon(
    _pokemon_name: str, encounters: list[dict]
) -> list[dict]:
    """Transform encounter data into a uniform list of dicts.

    Expects the raw encounter response from PokeAPI:
    [{"location_area": {"name": ...}, "version_details": [...]}]

    Columns: area, version, method, chance, levels.
    """
    rows: list[dict] = []

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
                rows.append({
                    "area": area_name,
                    "version": version,
                    "method": method,
                    "chance": chance,
                    "levels": levels,
                })

    return rows


def resource_list_toon(result: ListResult) -> list[dict]:
    """Transform a ListResult into a uniform list of dicts.

    Columns: name.
    """
    return [{"name": r.name} for r in result.results]
