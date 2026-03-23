import pytest
from pydantic import ValidationError

from pokecli.models.common import ListResult, NamedResource


class TestNamedResource:
    def test_valid(self):
        r = NamedResource.model_validate(
            {"name": "fire", "url": "https://pokeapi.co/api/v2/type/10/"}
        )
        assert r.name == "fire"
        assert r.url == "https://pokeapi.co/api/v2/type/10/"

    def test_extra_fields_ignored(self):
        r = NamedResource.model_validate(
            {"name": "fire", "url": "https://example.com", "unknown": 42}
        )
        assert not hasattr(r, "unknown")

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            NamedResource.model_validate({"url": "https://example.com"})

    def test_missing_url_raises(self):
        with pytest.raises(ValidationError):
            NamedResource.model_validate({"name": "fire"})


class TestListResult:
    def _make(self, **overrides):
        base = {
            "count": 100,
            "next": "https://pokeapi.co/api/v2/pokemon/?offset=20",
            "previous": None,
            "results": [
                {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}
            ],
        }
        base.update(overrides)
        return base

    def test_valid(self):
        r = ListResult.model_validate(self._make())
        assert r.count == 100
        assert r.next is not None
        assert r.previous is None
        assert len(r.results) == 1
        assert r.results[0].name == "bulbasaur"

    def test_next_and_previous_nullable(self):
        r = ListResult.model_validate(self._make(next=None, previous=None))
        assert r.next is None
        assert r.previous is None

    def test_empty_results(self):
        r = ListResult.model_validate(self._make(results=[]))
        assert r.results == []

    def test_extra_fields_ignored(self):
        data = self._make()
        data["extra_field"] = "ignored"
        r = ListResult.model_validate(data)
        assert not hasattr(r, "extra_field")

    def test_missing_count_raises(self):
        data = self._make()
        del data["count"]
        with pytest.raises(ValidationError):
            ListResult.model_validate(data)
