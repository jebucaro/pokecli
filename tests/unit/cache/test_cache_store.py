import pytest

from pokecli.cache.store import CacheStore


class TestCRUD:
    def test_get_miss_returns_none(self, tmp_cache):
        assert tmp_cache.get("pokemon", "pikachu") is None

    def test_set_then_get(self, tmp_cache):
        tmp_cache.set("pokemon", "pikachu", {"id": 25, "name": "pikachu"})
        result = tmp_cache.get("pokemon", "pikachu")
        assert result == {"id": 25, "name": "pikachu"}

    def test_set_upserts_not_duplicates(self, tmp_cache):
        tmp_cache.set("pokemon", "pikachu", {"id": 25})
        tmp_cache.set("pokemon", "pikachu", {"id": 25, "name": "pikachu"})
        result = tmp_cache.get("pokemon", "pikachu")
        assert result["name"] == "pikachu"
        # Verify only one record exists for the key
        from tinydb import Query

        records = tmp_cache._table("pokemon").search(Query().key == "pikachu")
        assert len(records) == 1

    def test_different_resources_are_isolated(self, tmp_cache):
        tmp_cache.set("pokemon", "bulbasaur", {"id": 1})
        assert tmp_cache.get("berry", "bulbasaur") is None

    def test_get_different_key_returns_none(self, tmp_cache):
        tmp_cache.set("pokemon", "pikachu", {"id": 25})
        assert tmp_cache.get("pokemon", "raichu") is None


class TestClear:
    def test_clear_specific_resource(self, tmp_cache):
        tmp_cache.set("pokemon", "bulbasaur", {"id": 1})
        tmp_cache.set("berry", "cheri", {"id": 1})
        count = tmp_cache.clear("pokemon")
        assert count == 1
        assert tmp_cache.get("pokemon", "bulbasaur") is None
        assert tmp_cache.get("berry", "cheri") is not None

    def test_clear_all_resources(self, tmp_cache):
        tmp_cache.set("pokemon", "bulbasaur", {"id": 1})
        tmp_cache.set("berry", "cheri", {"id": 1})
        tmp_cache.set("item", "potion", {"id": 1})
        count = tmp_cache.clear()
        assert count == 3
        assert tmp_cache.get("pokemon", "bulbasaur") is None
        assert tmp_cache.get("berry", "cheri") is None

    def test_clear_empty_resource_returns_zero(self, tmp_cache):
        assert tmp_cache.clear("pokemon") == 0

    def test_clear_empty_all_returns_zero(self, tmp_cache):
        assert tmp_cache.clear() == 0


class TestStats:
    def test_stats_empty(self, tmp_cache):
        stats = tmp_cache.stats()
        assert all(v == 0 for v in stats.values())

    def test_stats_counts_per_resource(self, tmp_cache):
        tmp_cache.set("pokemon", "bulbasaur", {})
        tmp_cache.set("pokemon", "ivysaur", {})
        tmp_cache.set("berry", "cheri", {})
        stats = tmp_cache.stats()
        assert stats["pokemon"] == 2
        assert stats["berry"] == 1
        assert stats["item"] == 0
        assert stats["move"] == 0

    def test_stats_all_resource_keys_present(self, tmp_cache):
        stats = tmp_cache.stats()
        assert set(stats.keys()) == {"pokemon", "berry", "item", "move"}


class TestContextManager:
    def test_context_manager_returns_self(self, tmp_path):
        with CacheStore(db_path=str(tmp_path / "cache.json")) as store:
            assert isinstance(store, CacheStore)

    def test_context_manager_closes_db(self, tmp_path):
        with CacheStore(db_path=str(tmp_path / "cache.json")) as store:
            store.set("pokemon", "pikachu", {"id": 25})
        # After close, TinyDB operations should raise
        with pytest.raises(Exception):
            store.get("pokemon", "pikachu")
