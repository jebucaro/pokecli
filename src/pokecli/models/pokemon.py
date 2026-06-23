from pokecli.models.common import BasePokeModel, NamedResource


class PokemonType(BasePokeModel):
    slot: int
    type: NamedResource


class PokemonAbility(BasePokeModel):
    slot: int
    is_hidden: bool
    ability: NamedResource


class PokemonStat(BasePokeModel):
    base_stat: int
    effort: int
    stat: NamedResource


class PokemonSprites(BasePokeModel):
    front_default: str | None = None
    front_shiny: str | None = None
    back_default: str | None = None
    back_shiny: str | None = None
    front_female: str | None = None
    front_shiny_female: str | None = None


class PokemonMoveEntry(BasePokeModel):
    name: str
    learn_method: str
    level: int


class Pokemon(BasePokeModel):
    id: int
    name: str
    height: int
    weight: int
    base_experience: int | None = None
    types: list[PokemonType]
    abilities: list[PokemonAbility]
    stats: list[PokemonStat]
    sprites: PokemonSprites
