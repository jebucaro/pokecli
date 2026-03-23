from pydantic import BaseModel, ConfigDict

from pokecli.models.common import NamedResource


class MoveEffectEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    effect: str
    short_effect: str
    language: NamedResource


class Move(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    accuracy: int | None = None
    power: int | None = None
    pp: int | None = None
    type: NamedResource
    damage_class: NamedResource
    effect_entries: list[MoveEffectEntry]
    effect_chance: int | None = None
