from pydantic import BaseModel, ConfigDict

from pokecli.models.common import NamedResource


class ItemEffect(BaseModel):
    model_config = ConfigDict(extra="ignore")

    effect: str
    short_effect: str
    language: NamedResource


class ItemFlavorText(BaseModel):
    model_config = ConfigDict(extra="ignore")

    text: str
    language: NamedResource
    version_group: NamedResource


class Item(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    cost: int
    fling_power: int | None = None
    category: NamedResource
    effect_entries: list[ItemEffect]
    flavor_text_entries: list[ItemFlavorText]
