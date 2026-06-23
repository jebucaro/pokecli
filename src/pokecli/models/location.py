from pokecli.models.common import BasePokeModel, NamedResource
from pokecli.models.reference import LanguageEntry


class Region(BasePokeModel):
    id: int
    name: str
    names: list[LanguageEntry] = []
    main_generation: NamedResource | None = None
    locations: list[NamedResource] = []
    pokedexes: list[NamedResource] = []
    version_groups: list[NamedResource] = []


class Location(BasePokeModel):
    id: int
    name: str
    region: NamedResource | None = None
    names: list[LanguageEntry] = []
    areas: list[NamedResource] = []


class EncounterDetail(BasePokeModel):
    min_level: int
    max_level: int
    chance: int
    method: NamedResource
    condition_values: list[NamedResource] = []


class VersionEncounterDetail(BasePokeModel):
    version: NamedResource
    max_chance: int
    encounter_details: list[EncounterDetail] = []


class PokemonEncounter(BasePokeModel):
    pokemon: NamedResource
    version_details: list[VersionEncounterDetail] = []


class EncounterVersionDetail(BasePokeModel):
    rate: int
    version: NamedResource


class EncounterMethodRate(BasePokeModel):
    encounter_method: NamedResource
    version_details: list[EncounterVersionDetail] = []


class LocationArea(BasePokeModel):
    id: int
    name: str
    game_index: int
    location: NamedResource
    names: list[LanguageEntry] = []
    encounter_method_rates: list[EncounterMethodRate] = []
    pokemon_encounters: list[PokemonEncounter] = []
