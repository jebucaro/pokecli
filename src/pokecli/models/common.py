from pydantic import BaseModel, ConfigDict


class NamedResource(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    url: str


class ListResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    count: int
    next: str | None
    previous: str | None
    results: list[NamedResource]
