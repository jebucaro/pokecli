from pydantic import BaseModel, ConfigDict


class BasePokeModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class NamedResource(BasePokeModel):
    name: str
    url: str


class ListResult(BasePokeModel):
    count: int
    next: str | None
    previous: str | None
    results: list[NamedResource]
