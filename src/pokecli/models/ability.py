from pokecli.models.common import BasePokeModel, NamedResource


class AbilityEffect(BasePokeModel):
    effect: str
    short_effect: str
    language: NamedResource


class Ability(BasePokeModel):
    id: int
    name: str
    generation: NamedResource
    effect_entries: list[AbilityEffect]
    pokemon: list[dict]
