import pytest

from pokecli.cache.store import CacheStore


@pytest.fixture
def tmp_cache(tmp_path):
    with CacheStore(db_path=str(tmp_path / "cache.json")) as store:
        yield store
