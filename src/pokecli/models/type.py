from pokecli.models.common import BasePokeModel, NamedResource


class TypeDamageRelations(BasePokeModel):
    no_damage_to: list[NamedResource]
    half_damage_to: list[NamedResource]
    double_damage_to: list[NamedResource]
    no_damage_from: list[NamedResource]
    half_damage_from: list[NamedResource]
    double_damage_from: list[NamedResource]


class PokemonType(BasePokeModel):
    id: int
    name: str
    damage_relations: TypeDamageRelations
    pokemon: list[dict]
    moves: list[NamedResource]
