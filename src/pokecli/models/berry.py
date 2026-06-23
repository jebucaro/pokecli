from pokecli.models.common import BasePokeModel, NamedResource


class BerryFlavorValue(BasePokeModel):
    potency: int
    flavor: NamedResource


class Berry(BasePokeModel):
    id: int
    name: str
    growth_time: int
    max_harvest: int
    natural_gift_power: int
    flavors: list[BerryFlavorValue]
    item: NamedResource
    firmness: NamedResource
