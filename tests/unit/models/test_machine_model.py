import pytest
from pydantic import ValidationError

from pokecli.models.machine import Machine


def _named(name, url):
    return {"name": name, "url": url}


def _make_machine(**overrides):
    base = {
        "id": 1,
        "item": _named("tm00", "https://pokeapi.co/api/v2/item/1287/"),
        "move": _named("mega-punch", "https://pokeapi.co/api/v2/move/5/"),
        "version_group": _named(
            "sword-shield", "https://pokeapi.co/api/v2/version-group/20/"
        ),
    }
    base.update(overrides)
    return base


class TestMachine:
    def test_valid(self):
        m = Machine.model_validate(_make_machine())
        assert m.id == 1
        assert m.item.name == "tm00"
        assert m.move.name == "mega-punch"
        assert m.version_group.name == "sword-shield"

    def test_extra_fields_ignored(self):
        data = _make_machine()
        data["unknown_field"] = "ignored"
        m = Machine.model_validate(data)
        assert not hasattr(m, "unknown_field")

    def test_missing_required_item_raises(self):
        data = _make_machine()
        del data["item"]
        with pytest.raises(ValidationError):
            Machine.model_validate(data)

    def test_missing_required_move_raises(self):
        data = _make_machine()
        del data["move"]
        with pytest.raises(ValidationError):
            Machine.model_validate(data)
