import pytest
from pydantic import ValidationError

from pokecli.models.reference import LanguageEntry, SimpleNamedResource


def _named(name="en", url="https://pokeapi.co/api/v2/language/9/"):
    return {"name": name, "url": url}


def _make_simple(**overrides):
    base = {
        "id": 1,
        "name": "monster",
        "names": [
            {"name": "Monster", "language": _named("en")},
            {"name": "かいじゅう", "language": _named("ja")},
        ],
    }
    base.update(overrides)
    return base


class TestSimpleNamedResource:
    def test_valid(self):
        r = SimpleNamedResource.model_validate(_make_simple())
        assert r.id == 1
        assert r.name == "monster"
        assert len(r.names) == 2
        assert r.names[0].name == "Monster"
        assert r.names[0].language.name == "en"

    def test_empty_names_default(self):
        r = SimpleNamedResource.model_validate({"id": 5, "name": "human-like"})
        assert r.names == []

    def test_extra_fields_ignored(self):
        data = _make_simple()
        data["pokemon_species"] = [{"name": "tauros", "url": "..."}]
        data["future_field"] = "ignored"
        r = SimpleNamedResource.model_validate(data)
        assert not hasattr(r, "pokemon_species")
        assert not hasattr(r, "future_field")

    def test_missing_required_id_raises(self):
        data = _make_simple()
        del data["id"]
        with pytest.raises(ValidationError):
            SimpleNamedResource.model_validate(data)

    def test_missing_required_name_raises(self):
        data = _make_simple()
        del data["name"]
        with pytest.raises(ValidationError):
            SimpleNamedResource.model_validate(data)


class TestLanguageEntry:
    def test_valid(self):
        e = LanguageEntry.model_validate({"name": "Monster", "language": _named("en")})
        assert e.name == "Monster"
        assert e.language.name == "en"

    def test_missing_language_raises(self):
        with pytest.raises(ValidationError):
            LanguageEntry.model_validate({"name": "Monster"})
