import pytest
from pydantic import ValidationError

from pokecli.models.move import Move


def _named(name="normal", url="https://pokeapi.co/api/v2/type/1/"):
    return {"name": name, "url": url}


def _make_move(**overrides):
    base = {
        "id": 33,
        "name": "tackle",
        "accuracy": 100,
        "power": 40,
        "pp": 35,
        "type": _named("normal"),
        "damage_class": _named(
            "physical", "https://pokeapi.co/api/v2/move-damage-class/2/"
        ),
        "effect_entries": [
            {
                "effect": "Inflicts regular damage.",
                "short_effect": "Inflicts regular damage.",
                "language": _named("en", "https://pokeapi.co/api/v2/language/9/"),
            }
        ],
        "effect_chance": None,
    }
    base.update(overrides)
    return base


class TestMove:
    def test_valid(self):
        m = Move.model_validate(_make_move())
        assert m.id == 33
        assert m.name == "tackle"
        assert m.accuracy == 100
        assert m.power == 40
        assert m.pp == 35

    def test_accuracy_nullable(self):
        m = Move.model_validate(_make_move(accuracy=None))
        assert m.accuracy is None

    def test_power_nullable(self):
        m = Move.model_validate(_make_move(power=None))
        assert m.power is None

    def test_pp_nullable(self):
        m = Move.model_validate(_make_move(pp=None))
        assert m.pp is None

    def test_effect_chance_nullable(self):
        m = Move.model_validate(_make_move(effect_chance=None))
        assert m.effect_chance is None

    def test_effect_chance_with_value(self):
        m = Move.model_validate(_make_move(effect_chance=30))
        assert m.effect_chance == 30

    def test_extra_fields_ignored(self):
        data = _make_move()
        data["future_field"] = "ignored"
        m = Move.model_validate(data)
        assert not hasattr(m, "future_field")

    def test_empty_effect_entries(self):
        m = Move.model_validate(_make_move(effect_entries=[]))
        assert m.effect_entries == []

    def test_missing_required_name_raises(self):
        data = _make_move()
        del data["name"]
        with pytest.raises(ValidationError):
            Move.model_validate(data)

    def test_type_and_damage_class(self):
        m = Move.model_validate(_make_move())
        assert m.type.name == "normal"
        assert m.damage_class.name == "physical"
