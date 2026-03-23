from pydantic import BaseModel, ConfigDict

from pokecli.models.common import NamedResource


class BerryFlavorValue(BaseModel):
    model_config = ConfigDict(extra="ignore")

    potency: int
    flavor: NamedResource


class Berry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    growth_time: int
    max_harvest: int
    natural_gift_power: int
    flavors: list[BerryFlavorValue]
    item: NamedResource
    firmness: NamedResource
