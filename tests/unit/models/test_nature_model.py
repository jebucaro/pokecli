import pytest
from pydantic import ValidationError

from pokecli.models.nature import Nature


def _named(name="attack", url="https://pokeapi.co/api/v2/stat/2/"):
    return {"name": name, "url": url}


def _make_nature(**overrides):
    base = {
        "id": 3,
        "name": "adamant",
        "increased_stat": _named("attack", "https://pokeapi.co/api/v2/stat/2/"),
        "decreased_stat": _named("special-attack", "https://pokeapi.co/api/v2/stat/4/"),
        "hates_flavor": _named("dry", "https://pokeapi.co/api/v2/berry-flavor/3/"),
        "likes_flavor": _named("spicy", "https://pokeapi.co/api/v2/berry-flavor/1/"),
    }
    base.update(overrides)
    return base


class TestNature:
    def test_valid_with_stat_modifiers(self):
        n = Nature.model_validate(_make_nature())
        assert n.id == 3
        assert n.name == "adamant"
        assert n.increased_stat.name == "attack"
        assert n.decreased_stat.name == "special-attack"
        assert n.likes_flavor.name == "spicy"
        assert n.hates_flavor.name == "dry"

    def test_neutral_nature(self):
        data = {
            "id": 6,
            "name": "hardy",
            "increased_stat": None,
            "decreased_stat": None,
            "hates_flavor": None,
            "likes_flavor": None,
        }
        n = Nature.model_validate(data)
        assert n.increased_stat is None
        assert n.decreased_stat is None
        assert n.hates_flavor is None
        assert n.likes_flavor is None

    def test_extra_fields_ignored(self):
        data = _make_nature()
        data["future_field"] = "ignored"
        n = Nature.model_validate(data)
        assert not hasattr(n, "future_field")

    def test_missing_required_name_raises(self):
        data = _make_nature()
        del data["name"]
        with pytest.raises(ValidationError):
            Nature.model_validate(data)

    def test_stat_fields_nullable(self):
        n = Nature.model_validate(
            _make_nature(increased_stat=None, decreased_stat=None)
        )
        assert n.increased_stat is None
        assert n.decreased_stat is None
