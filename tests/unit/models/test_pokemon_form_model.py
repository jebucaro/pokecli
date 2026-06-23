import pytest
from pydantic import ValidationError

from pokecli.models.pokemon_form import PokemonForm


def _named(name, url):
    return {"name": name, "url": url}


def _make_form(**overrides):
    base = {
        "id": 10034,
        "name": "charizard-mega-x",
        "order": 7,
        "form_order": 2,
        "is_default": False,
        "is_battle_only": True,
        "is_mega": True,
        "form_name": "mega-x",
        "pokemon": _named("charizard", "https://pokeapi.co/api/v2/pokemon/6/"),
        "types": [
            {"slot": 1, "type": _named("fire", "https://pokeapi.co/api/v2/type/10/")},
            {
                "slot": 2,
                "type": _named("dragon", "https://pokeapi.co/api/v2/type/16/"),
            },
        ],
        "sprites": {
            "front_default": "https://example.com/mega-x.png",
            "front_shiny": None,
            "back_default": None,
            "back_shiny": None,
        },
        "version_group": _named("x-y", "https://pokeapi.co/api/v2/version-group/15/"),
        "names": [],
        "form_names": [],
    }
    base.update(overrides)
    return base


class TestPokemonForm:
    def test_valid_mega_form(self):
        f = PokemonForm.model_validate(_make_form())
        assert f.id == 10034
        assert f.name == "charizard-mega-x"
        assert f.is_mega is True
        assert f.is_battle_only is True
        assert f.is_default is False
        assert f.form_name == "mega-x"
        assert len(f.types) == 2
        assert f.types[0].type.name == "fire"
        assert f.sprites.front_default == "https://example.com/mega-x.png"

    def test_default_form_no_sprites(self):
        data = _make_form(
            is_default=True, is_mega=False, is_battle_only=False, sprites=None
        )
        f = PokemonForm.model_validate(data)
        assert f.sprites is None

    def test_extra_fields_ignored(self):
        data = _make_form()
        data["unknown_field"] = "ignored"
        f = PokemonForm.model_validate(data)
        assert not hasattr(f, "unknown_field")

    def test_missing_required_pokemon_raises(self):
        data = _make_form()
        del data["pokemon"]
        with pytest.raises(ValidationError):
            PokemonForm.model_validate(data)

    def test_empty_types_allowed(self):
        f = PokemonForm.model_validate(_make_form(types=[]))
        assert f.types == []
