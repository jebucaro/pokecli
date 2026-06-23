from pokecli.models.common import BasePokeModel, NamedResource


class ItemEffect(BasePokeModel):
    effect: str
    short_effect: str
    language: NamedResource


class ItemFlavorText(BasePokeModel):
    text: str
    language: NamedResource
    version_group: NamedResource


class Item(BasePokeModel):
    id: int
    name: str
    cost: int
    fling_power: int | None = None
    category: NamedResource
    effect_entries: list[ItemEffect]
    flavor_text_entries: list[ItemFlavorText]
