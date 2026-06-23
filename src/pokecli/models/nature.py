from pokecli.models.common import BasePokeModel, NamedResource


class Nature(BasePokeModel):
    id: int
    name: str
    decreased_stat: NamedResource | None = None
    increased_stat: NamedResource | None = None
    hates_flavor: NamedResource | None = None
    likes_flavor: NamedResource | None = None
