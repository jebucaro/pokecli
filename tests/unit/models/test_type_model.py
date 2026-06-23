import pytest
from pydantic import ValidationError

from pokecli.models.type import PokemonType


def _named(name="fire", url="https://pokeapi.co/api/v2/type/10/"):
    return {"name": name, "url": url}


def _make_damage_relations(**overrides):
    base = {
        "no_damage_to": [],
        "half_damage_to": [],
        "double_damage_to": [
            _named("grass"),
            _named("ice"),
            _named("bug"),
            _named("steel"),
        ],
        "no_damage_from": [],
        "half_damage_from": [
            _named("fire"),
            _named("grass"),
            _named("ice"),
            _named("bug"),
            _named("steel"),
            _named("fairy"),
        ],
        "double_damage_from": [_named("water"), _named("ground"), _named("rock")],
    }
    base.update(overrides)
    return base


def _make_type(**overrides):
    base = {
        "id": 10,
        "name": "fire",
        "damage_relations": _make_damage_relations(),
        "pokemon": [
            {
                "slot": 1,
                "pokemon": _named("charmander", "https://pokeapi.co/api/v2/pokemon/4/"),
            }
        ],
        "moves": [_named("ember", "https://pokeapi.co/api/v2/move/52/")],
    }
    base.update(overrides)
    return base


class TestPokemonType:
    def test_valid(self):
        t = PokemonType.model_validate(_make_type())
        assert t.id == 10
        assert t.name == "fire"

    def test_extra_fields_ignored(self):
        data = _make_type()
        data["future_field"] = "ignored"
        t = PokemonType.model_validate(data)
        assert not hasattr(t, "future_field")

    def test_missing_required_name_raises(self):
        data = _make_type()
        del data["name"]
        with pytest.raises(ValidationError):
            PokemonType.model_validate(data)

    def test_damage_relations_all_lists(self):
        t = PokemonType.model_validate(_make_type())
        dr = t.damage_relations
        assert len(dr.double_damage_to) == 4
        assert {r.name for r in dr.double_damage_to} == {"grass", "ice", "bug", "steel"}
        assert len(dr.double_damage_from) == 3
        assert len(dr.half_damage_from) == 6

    def test_damage_relations_all_empty(self):
        empty_relations = {
            "no_damage_to": [],
            "half_damage_to": [],
            "double_damage_to": [],
            "no_damage_from": [],
            "half_damage_from": [],
            "double_damage_from": [],
        }
        t = PokemonType.model_validate(_make_type(damage_relations=empty_relations))
        dr = t.damage_relations
        assert dr.no_damage_to == []
        assert dr.double_damage_to == []
        assert dr.double_damage_from == []

    def test_moves_list(self):
        t = PokemonType.model_validate(_make_type())
        assert len(t.moves) == 1
        assert t.moves[0].name == "ember"

    def test_pokemon_list_passthrough(self):
        t = PokemonType.model_validate(_make_type())
        assert isinstance(t.pokemon, list)
        assert isinstance(t.pokemon[0], dict)
