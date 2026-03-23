import pytest
from pydantic import ValidationError

from pokecli.models.berry import Berry


def _named(name="cheri", url="https://pokeapi.co/api/v2/berry/1/"):
    return {"name": name, "url": url}


def _make_berry(**overrides):
    base = {
        "id": 1,
        "name": "cheri",
        "growth_time": 3,
        "max_harvest": 5,
        "natural_gift_power": 60,
        "flavors": [
            {
                "potency": 10,
                "flavor": _named("spicy", "https://pokeapi.co/api/v2/berry-flavor/1/"),
            }
        ],
        "item": _named("cheri-berry", "https://pokeapi.co/api/v2/item/126/"),
        "firmness": _named("soft", "https://pokeapi.co/api/v2/berry-firmness/2/"),
    }
    base.update(overrides)
    return base


class TestBerry:
    def test_valid(self):
        b = Berry.model_validate(_make_berry())
        assert b.id == 1
        assert b.name == "cheri"
        assert b.growth_time == 3
        assert b.max_harvest == 5
        assert b.natural_gift_power == 60

    def test_extra_fields_ignored(self):
        data = _make_berry()
        data["future_field"] = "ignored"
        b = Berry.model_validate(data)
        assert not hasattr(b, "future_field")

    def test_flavors_empty_list(self):
        b = Berry.model_validate(_make_berry(flavors=[]))
        assert b.flavors == []

    def test_flavor_zero_potency(self):
        data = _make_berry(flavors=[{"potency": 0, "flavor": _named("dry")}])
        b = Berry.model_validate(data)
        assert b.flavors[0].potency == 0

    def test_missing_required_field_raises(self):
        data = _make_berry()
        del data["natural_gift_power"]
        with pytest.raises(ValidationError):
            Berry.model_validate(data)

    def test_item_and_firmness_are_named_resources(self):
        b = Berry.model_validate(_make_berry())
        assert b.item.name == "cheri-berry"
        assert b.firmness.name == "soft"
