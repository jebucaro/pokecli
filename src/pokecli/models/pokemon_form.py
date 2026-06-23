from pokecli.models.common import BasePokeModel, NamedResource
from pokecli.models.reference import LanguageEntry


class FormType(BasePokeModel):
    slot: int
    type: NamedResource


class FormSprites(BasePokeModel):
    front_default: str | None = None
    front_shiny: str | None = None
    back_default: str | None = None
    back_shiny: str | None = None


class PokemonForm(BasePokeModel):
    id: int
    name: str
    order: int
    form_order: int
    is_default: bool
    is_battle_only: bool
    is_mega: bool
    form_name: str
    pokemon: NamedResource
    types: list[FormType] = []
    sprites: FormSprites | None = None
    version_group: NamedResource
    names: list[LanguageEntry] = []
    form_names: list[LanguageEntry] = []
