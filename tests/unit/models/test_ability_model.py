import pytest
from pydantic import ValidationError

from pokecli.models.ability import Ability


def _named(name="en", url="https://pokeapi.co/api/v2/language/9/"):
    return {"name": name, "url": url}


def _make_ability(**overrides):
    base = {
        "id": 65,
        "name": "overgrow",
        "generation": _named("generation-i", "https://pokeapi.co/api/v2/generation/1/"),
        "effect_entries": [
            {
                "effect": "When this Pokémon has 1/3 or less of its HP remaining, its Grass-type moves inflict 1.5× as much regular damage.",
                "short_effect": "Strengthens grass moves to inflict 1.5× damage at 1/3 HP or less.",
                "language": _named("en", "https://pokeapi.co/api/v2/language/9/"),
            }
        ],
        "pokemon": [
            {
                "is_hidden": False,
                "slot": 1,
                "pokemon": _named("bulbasaur", "https://pokeapi.co/api/v2/pokemon/1/"),
            }
        ],
    }
    base.update(overrides)
    return base


class TestAbility:
    def test_valid(self):
        a = Ability.model_validate(_make_ability())
        assert a.id == 65
        assert a.name == "overgrow"
        assert a.generation.name == "generation-i"

    def test_extra_fields_ignored(self):
        data = _make_ability()
        data["future_field"] = {"nested": True}
        a = Ability.model_validate(data)
        assert not hasattr(a, "future_field")

    def test_missing_required_name_raises(self):
        data = _make_ability()
        del data["name"]
        with pytest.raises(ValidationError):
            Ability.model_validate(data)

    def test_empty_effect_entries(self):
        a = Ability.model_validate(_make_ability(effect_entries=[]))
        assert a.effect_entries == []

    def test_empty_pokemon_list(self):
        a = Ability.model_validate(_make_ability(pokemon=[]))
        assert a.pokemon == []

    def test_effect_entry_fields(self):
        a = Ability.model_validate(_make_ability())
        entry = a.effect_entries[0]
        assert "Grass-type" in entry.effect
        assert "1.5×" in entry.short_effect
        assert entry.language.name == "en"
