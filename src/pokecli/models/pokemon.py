from pydantic import BaseModel, ConfigDict

from pokecli.models.common import NamedResource


class PokemonType(BaseModel):
    model_config = ConfigDict(extra="ignore")

    slot: int
    type: NamedResource


class PokemonAbility(BaseModel):
    model_config = ConfigDict(extra="ignore")

    slot: int
    is_hidden: bool
    ability: NamedResource


class PokemonStat(BaseModel):
    model_config = ConfigDict(extra="ignore")

    base_stat: int
    effort: int
    stat: NamedResource


class PokemonSprites(BaseModel):
    model_config = ConfigDict(extra="ignore")

    front_default: str | None = None
    front_shiny: str | None = None
    back_default: str | None = None
    back_shiny: str | None = None
    front_female: str | None = None
    front_shiny_female: str | None = None


class PokemonMoveEntry(BaseModel):
    name: str
    learn_method: str
    level: int


class Pokemon(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    height: int
    weight: int
    base_experience: int | None = None
    types: list[PokemonType]
    abilities: list[PokemonAbility]
    stats: list[PokemonStat]
    sprites: PokemonSprites
