from pokecli.models.common import BasePokeModel, NamedResource


class Machine(BasePokeModel):
    id: int
    item: NamedResource
    move: NamedResource
    version_group: NamedResource
