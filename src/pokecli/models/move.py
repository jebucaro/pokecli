from pokecli.models.common import BasePokeModel, NamedResource


class MoveEffectEntry(BasePokeModel):
    effect: str
    short_effect: str
    language: NamedResource


class Move(BasePokeModel):
    id: int
    name: str
    accuracy: int | None = None
    power: int | None = None
    pp: int | None = None
    type: NamedResource
    damage_class: NamedResource
    effect_entries: list[MoveEffectEntry]
    effect_chance: int | None = None
