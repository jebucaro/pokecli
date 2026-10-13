from pokecli.models.item import Item


def _named(name="medicine", url="https://pokeapi.co/api/v2/item-category/1/"):
    return {"name": name, "url": url}


def _price(
    currency="poke-dollar",
    purchase_price=300,
    sell_price=150,
    version_group="red-blue",
):
    return {
        "currency": _named(currency, "https://pokeapi.co/api/v2/currency/1/"),
        "purchase_price": purchase_price,
        "sell_price": sell_price,
        "version_group": _named(
            version_group, "https://pokeapi.co/api/v2/version-group/1/"
        ),
    }


def _make_item(**overrides):
    base = {
        "id": 17,
        "name": "potion",
        "prices": [_price()],
        "fling_power": None,
        "category": _named("medicine"),
        "effect_entries": [
            {
                "effect": "Restores 20 HP.",
                "short_effect": "Restores 20 HP.",
                "language": _named("en", "https://pokeapi.co/api/v2/language/9/"),
            }
        ],
        "flavor_text_entries": [
            {
                "text": "A spray-type medicine.",
                "language": _named("en", "https://pokeapi.co/api/v2/language/9/"),
                "version_group": _named(
                    "red-blue", "https://pokeapi.co/api/v2/version-group/1/"
                ),
            }
        ],
    }
    base.update(overrides)
    return base


class TestItem:
    def test_valid(self):
        item = Item.model_validate(_make_item())
        assert item.id == 17
        assert item.name == "potion"
        assert item.prices[0].purchase_price == 300
        assert item.prices[0].sell_price == 150
        assert item.prices[0].currency.name == "poke-dollar"
        assert item.prices[0].version_group.name == "red-blue"

    def test_fling_power_nullable(self):
        item = Item.model_validate(_make_item(fling_power=None))
        assert item.fling_power is None

    def test_fling_power_with_value(self):
        item = Item.model_validate(_make_item(fling_power=30))
        assert item.fling_power == 30

    def test_extra_fields_ignored(self):
        data = _make_item()
        data["future_field"] = "ignored"
        item = Item.model_validate(data)
        assert not hasattr(item, "future_field")

    def test_empty_effect_entries(self):
        item = Item.model_validate(_make_item(effect_entries=[]))
        assert item.effect_entries == []

    def test_empty_flavor_text_entries(self):
        item = Item.model_validate(_make_item(flavor_text_entries=[]))
        assert item.flavor_text_entries == []

    def test_missing_prices_defaults_empty(self):
        data = _make_item()
        del data["prices"]
        item = Item.model_validate(data)
        assert item.prices == []

    def test_empty_prices(self):
        item = Item.model_validate(_make_item(prices=[]))
        assert item.prices == []

    def test_null_purchase_and_sell_price(self):
        item = Item.model_validate(
            _make_item(prices=[_price(purchase_price=None, sell_price=None)])
        )
        assert item.prices[0].purchase_price is None
        assert item.prices[0].sell_price is None

    def test_effect_entry_language(self):
        item = Item.model_validate(_make_item())
        assert item.effect_entries[0].language.name == "en"
        assert item.effect_entries[0].short_effect == "Restores 20 HP."
