from pokecli.models.common import BasePokeModel, NamedResource


class LanguageEntry(BasePokeModel):
    name: str
    language: NamedResource


class SimpleNamedResource(BasePokeModel):
    """Shared model for reference resources whose only useful fields are id/name/names[]."""

    id: int
    name: str
    names: list[LanguageEntry] = []
