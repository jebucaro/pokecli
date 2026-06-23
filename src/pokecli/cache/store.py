from pathlib import Path

from tinydb import Query, TinyDB

from pokecli.config import CACHE_DB_PATH

RESOURCE_TABLES = [
    "pokemon",
    "berry",
    "item",
    "move",
    "ability",
    "nature",
    "type",
    "pokemon-species",
    "evolution-chain",
    "location",
    "location-area",
    "region",
    "generation",
    "version",
    "version-group",
    "pokedex",
    "machine",
    "pokemon-form",
    "egg-group",
    "growth-rate",
    "evolution-trigger",
    "move-damage-class",
    "move-learn-method",
]


class CacheStore:
    def __init__(self, db_path: str = CACHE_DB_PATH):
        path = Path(db_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = TinyDB(path)

    def _table(self, resource: str):
        return self._db.table(resource)

    def get(self, resource: str, key: str) -> dict | None:
        Record = Query()
        result = self._table(resource).get(Record.key == key)
        return result["data"] if result else None

    def set(self, resource: str, key: str, data: dict) -> None:
        Record = Query()
        self._table(resource).upsert({"key": key, "data": data}, Record.key == key)

    def clear(self, resource: str | None = None) -> int:
        if resource:
            table = self._table(resource)
            count = len(table)
            table.truncate()
            return count
        total = sum(len(self._db.table(r)) for r in RESOURCE_TABLES)
        for r in RESOURCE_TABLES:
            self._db.table(r).truncate()
        return total

    def stats(self) -> dict[str, int]:
        return {r: len(self._db.table(r)) for r in RESOURCE_TABLES}

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> "CacheStore":
        return self

    def __exit__(self, *_) -> None:
        self.close()
