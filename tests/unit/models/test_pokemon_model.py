import pytest
from pydantic import ValidationError

from pokecli.models.pokemon import Pokemon, PokemonSprites


def _named(name="fire", url="https://pokeapi.co/api/v2/type/10/"):
    return {"name": name, "url": url}


def _make_pokemon(**overrides):
    base = {
        "id": 6,
        "name": "charizard",
        "height": 17,
        "weight": 905,
        "base_experience": 240,
        "types": [{"slot": 1, "type": _named("fire")}],
        "abilities": [{"slot": 1, "is_hidden": False, "ability": _named("blaze")}],
        "stats": [{"base_stat": 90, "effort": 0, "stat": _named("speed")}],
        "sprites": {"front_default": "https://sprites.example.com/6.png"},
    }
    base.update(overrides)
    return base


class TestPokemon:
    def test_valid(self):
        p = Pokemon.model_validate(_make_pokemon())
        assert p.id == 6
        assert p.name == "charizard"
        assert p.height == 17
        assert p.weight == 905

    def test_extra_fields_ignored(self):
        data = _make_pokemon()
        data["future_field"] = {"nested": True}
        p = Pokemon.model_validate(data)
        assert not hasattr(p, "future_field")

    def test_base_experience_optional(self):
        data = _make_pokemon()
        del data["base_experience"]
        p = Pokemon.model_validate(data)
        assert p.base_experience is None

    def test_base_experience_null(self):
        p = Pokemon.model_validate(_make_pokemon(base_experience=None))
        assert p.base_experience is None

    def test_missing_required_name_raises(self):
        data = _make_pokemon()
        del data["name"]
        with pytest.raises(ValidationError):
            Pokemon.model_validate(data)

    def test_multiple_types(self):
        data = _make_pokemon(
            types=[
                {"slot": 1, "type": _named("fire")},
                {"slot": 2, "type": _named("flying")},
            ]
        )
        p = Pokemon.model_validate(data)
        assert len(p.types) == 2
        names = {t.type.name for t in p.types}
        assert names == {"fire", "flying"}

    def test_hidden_ability(self):
        data = _make_pokemon(
            abilities=[
                {"slot": 1, "is_hidden": False, "ability": _named("blaze")},
                {"slot": 3, "is_hidden": True, "ability": _named("solar-power")},
            ]
        )
        p = Pokemon.model_validate(data)
        hidden = [a for a in p.abilities if a.is_hidden]
        assert len(hidden) == 1
        assert hidden[0].ability.name == "solar-power"

    def test_stat_values(self):
        data = _make_pokemon(
            stats=[
                {"base_stat": 78, "effort": 0, "stat": _named("hp")},
                {"base_stat": 100, "effort": 3, "stat": _named("speed")},
            ]
        )
        p = Pokemon.model_validate(data)
        speed = next(s for s in p.stats if s.stat.name == "speed")
        assert speed.base_stat == 100
        assert speed.effort == 3


class TestPokemonSprites:
    def test_all_nullable(self):
        sp = PokemonSprites.model_validate(
            {
                "front_default": None,
                "front_shiny": None,
                "back_default": None,
                "back_shiny": None,
                "front_female": None,
                "front_shiny_female": None,
            }
        )
        assert sp.front_default is None

    def test_defaults_to_none(self):
        sp = PokemonSprites.model_validate({})
        assert sp.front_default is None
        assert sp.front_shiny is None

    def test_extra_fields_ignored(self):
        sp = PokemonSprites.model_validate(
            {"front_default": "https://example.com", "other": {}}
        )
        assert not hasattr(sp, "other")
