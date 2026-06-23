from pokecli.models.common import BasePokeModel, NamedResource
from pokecli.models.reference import LanguageEntry


class Generation(BasePokeModel):
    id: int
    name: str
    main_region: NamedResource
    names: list[LanguageEntry] = []
    pokemon_species: list[NamedResource] = []
    moves: list[NamedResource] = []
    abilities: list[NamedResource] = []
    types: list[NamedResource] = []
    version_groups: list[NamedResource] = []


class Version(BasePokeModel):
    id: int
    name: str
    names: list[LanguageEntry] = []
    version_group: NamedResource


class VersionGroup(BasePokeModel):
    id: int
    name: str
    order: int
    generation: NamedResource
    move_learn_methods: list[NamedResource] = []
    pokedexes: list[NamedResource] = []
    regions: list[NamedResource] = []
    versions: list[NamedResource] = []


class PokedexEntry(BasePokeModel):
    entry_number: int
    pokemon_species: NamedResource


class Pokedex(BasePokeModel):
    id: int
    name: str
    is_main_series: bool
    names: list[LanguageEntry] = []
    region: NamedResource | None = None
    pokemon_entries: list[PokedexEntry] = []
    version_groups: list[NamedResource] = []
