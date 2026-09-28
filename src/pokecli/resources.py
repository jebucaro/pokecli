"""The resource table: single source of truth for supported PokeAPI resources.

Every row describes one resource completely - its CLI and API name, the model it
validates against, how it renders in each output format, and what it is for.
Generic ``get``, ``list``, and ``search`` handlers read from this table, so a
resource cannot acquire behavior its peers lack.

Five consumers read this table:
  * ``<resource>`` argument validation and shell completion
  * model and renderer dispatch in the generic handlers
  * the Resources panel in ``get``/``list``/``search`` help
  * the resource table in the packaged ``SKILL.md`` (kept in sync by a test)
  * next-step hint construction
"""

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel
from rich.console import Console

from pokecli.display.berry import render_berry
from pokecli.display.ability import render_ability
from pokecli.display.evolution import render_evolution, render_species
from pokecli.display.game import (
    render_generation,
    render_pokedex,
    render_version,
    render_version_group,
)
from pokecli.display.item import render_item
from pokecli.display.location import (
    render_location,
    render_location_area,
    render_region,
)
from pokecli.display.machine import render_machine
from pokecli.display.move import render_move
from pokecli.display.nature import render_nature
from pokecli.display.pokemon import render_pokemon
from pokecli.display.pokemon_form import render_pokemon_form
from pokecli.display.type import render_type
from pokecli.display import toon_schemas as ts
from pokecli.models.ability import Ability
from pokecli.models.berry import Berry
from pokecli.models.evolution import EvolutionChain, PokemonSpecies
from pokecli.models.game import Generation, Pokedex, Version, VersionGroup
from pokecli.models.item import Item
from pokecli.models.location import Location, LocationArea, Region
from pokecli.models.machine import Machine
from pokecli.models.move import Move
from pokecli.models.nature import Nature
from pokecli.models.pokemon import Pokemon
from pokecli.models.pokemon_form import PokemonForm
from pokecli.models.type import PokemonType


@dataclass(frozen=True)
class Resource:
    """One supported PokeAPI resource.

    Attributes:
        name: CLI name, also the PokeAPI path segment and cache table name.
        purpose: One-line description shown in the ``get``/``list``/``search``
            help and mirrored in the packaged ``SKILL.md``.
        model: Pydantic model the raw response is validated against.
        render: Rich renderer for ``--format table``.
        toon: Builds the TOON field mapping for ``--format toon``.
        toon_label: Top-level TOON key for a single record.
        list_label: Top-level TOON key for a page of records.
        toon_extra: Optional aggregates added to the TOON mapping, computed
            from the validated model and the raw response.
        toon_pair: Overrides ``toon``/``toon_label`` for resources whose TOON
            label is data-dependent.
        hint_context: Optional extra next-step hint context beyond ``name``.
    """

    name: str
    purpose: str
    model: type[BaseModel]
    render: Callable[[Any, Console], None]
    toon: Callable[[Any], dict] | None
    toon_label: str
    list_label: str
    toon_extra: Callable[[Any, dict], dict] | None = None
    toon_pair: Callable[[Any], tuple[str, dict]] | None = None
    hint_context: Callable[[Any], dict] | None = None


def _pokemon_extra(model: Pokemon, raw: dict) -> dict:
    return {"total_moves": len(raw.get("moves", []))}


def _type_extra(model: PokemonType, raw: dict) -> dict:
    return {
        "pokemon_count": len(model.pokemon),
        "move_count": len(model.moves),
    }


def _type_hints(model: PokemonType) -> dict:
    return {
        "super_effective": [r.name for r in model.damage_relations.double_damage_to]
    }


def _move_hints(model: Move) -> dict:
    return {"type": model.type.name if model.type else None}


def _location_hints(model: Location) -> dict:
    return {"first_area": model.areas[0].name if model.areas else None}


def _location_area_hints(model: LocationArea) -> dict:
    return {"location": model.location.name}


def _region_hints(model: Region) -> dict:
    return {"first_location": model.locations[0].name if model.locations else None}


def _chain_hints(model: EvolutionChain) -> dict:
    return {"base_species": model.chain.species.name if model.chain else None}


RESOURCES: tuple[Resource, ...] = (
    Resource(
        name="pokemon",
        purpose="Stats, types, abilities, and sprites for a single Pokemon",
        model=Pokemon,
        render=render_pokemon,
        toon=ts.pokemon_toon,
        toon_label="pokemon",
        list_label="pokemon",
        toon_extra=_pokemon_extra,
    ),
    Resource(
        name="pokemon-species",
        purpose="Pokedex text, egg groups, capture rate, and growth rate",
        model=PokemonSpecies,
        render=render_species,
        toon=ts.species_toon,
        toon_label="species",
        list_label="pokemon_species",
    ),
    Resource(
        name="pokemon-form",
        purpose="A specific variant such as a Mega, Alolan, or Gigantamax form",
        model=PokemonForm,
        render=render_pokemon_form,
        toon=ts.pokemon_form_toon,
        toon_label="pokemon_form",
        list_label="pokemon_forms",
    ),
    Resource(
        name="evolution-chain",
        purpose="A full evolution chain addressed by its numeric chain ID",
        model=EvolutionChain,
        render=render_evolution,
        toon=None,
        toon_label="evolution_chain",
        list_label="evolution_chains",
        toon_pair=ts.evolution_chain_toon,
        hint_context=_chain_hints,
    ),
    Resource(
        name="move",
        purpose="Power, accuracy, PP, type, and damage class of a move",
        model=Move,
        render=render_move,
        toon=ts.move_toon,
        toon_label="move",
        list_label="moves",
        hint_context=_move_hints,
    ),
    Resource(
        name="item",
        purpose="Cost, effect, and flavor text of a held or usable item",
        model=Item,
        render=render_item,
        toon=ts.item_toon,
        toon_label="item",
        list_label="items",
    ),
    Resource(
        name="ability",
        purpose="What an ability does and which Pokemon have it",
        model=Ability,
        render=render_ability,
        toon=ts.ability_toon,
        toon_label="ability",
        list_label="abilities",
    ),
    Resource(
        name="type",
        purpose="Damage relations - strengths, weaknesses, and immunities",
        model=PokemonType,
        render=render_type,
        toon=ts.type_toon,
        toon_label="type",
        list_label="types",
        toon_extra=_type_extra,
        hint_context=_type_hints,
    ),
    Resource(
        name="nature",
        purpose="Which stat a nature raises and which it lowers",
        model=Nature,
        render=render_nature,
        toon=ts.nature_toon,
        toon_label="nature",
        list_label="natures",
    ),
    Resource(
        name="berry",
        purpose="Growth time, size, flavors, and natural gift data",
        model=Berry,
        render=render_berry,
        toon=ts.berry_toon,
        toon_label="berry",
        list_label="berries",
    ),
    Resource(
        name="location",
        purpose="A named place and the encounter areas inside it",
        model=Location,
        render=render_location,
        toon=ts.location_toon,
        toon_label="location",
        list_label="locations",
        hint_context=_location_hints,
    ),
    Resource(
        name="location-area",
        purpose="An encounter area and the Pokemon found there",
        model=LocationArea,
        render=render_location_area,
        toon=ts.location_area_toon,
        toon_label="location_area",
        list_label="location_areas",
        hint_context=_location_area_hints,
    ),
    Resource(
        name="region",
        purpose="A region such as kanto, with its locations and pokedexes",
        model=Region,
        render=render_region,
        toon=ts.region_toon,
        toon_label="region",
        list_label="regions",
        hint_context=_region_hints,
    ),
    Resource(
        name="generation",
        purpose="A generation and the species, moves, and types it introduced",
        model=Generation,
        render=render_generation,
        toon=ts.generation_toon,
        toon_label="generation",
        list_label="generations",
    ),
    Resource(
        name="version",
        purpose="A single game release such as red or sword",
        model=Version,
        render=render_version,
        toon=ts.version_toon,
        toon_label="version",
        list_label="versions",
    ),
    Resource(
        name="version-group",
        purpose="A paired release such as red-blue or sword-shield",
        model=VersionGroup,
        render=render_version_group,
        toon=ts.version_group_toon,
        toon_label="version_group",
        list_label="version_groups",
    ),
    Resource(
        name="pokedex",
        purpose="A regional or national pokedex and its species entries",
        model=Pokedex,
        render=render_pokedex,
        toon=ts.pokedex_toon,
        toon_label="pokedex",
        list_label="pokedexes",
    ),
    Resource(
        name="machine",
        purpose="A TM or HM record - which move it teaches, in which games",
        model=Machine,
        render=render_machine,
        toon=ts.machine_toon,
        toon_label="machine",
        list_label="machines",
    ),
)

RESOURCES_BY_NAME: dict[str, Resource] = {r.name: r for r in RESOURCES}

RESOURCE_NAMES: tuple[str, ...] = tuple(r.name for r in RESOURCES)


def get_resource(name: str) -> Resource | None:
    """Return the table row for ``name``, or None when unsupported."""
    return RESOURCES_BY_NAME.get(name)
