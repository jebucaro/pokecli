import pytest
from pydantic import ValidationError

from pokecli.models.evolution import EvolutionChain, EvolutionDetail, PokemonSpecies


def _named(name="level-up", url="https://pokeapi.co/api/v2/evolution-trigger/1/"):
    return {"name": name, "url": url}


def _make_evolution_detail(**overrides):
    base = {
        "trigger": _named("level-up"),
        "min_level": 16,
    }
    base.update(overrides)
    return base


def _make_chain_link(species_name="bulbasaur", evolves_to=None):
    return {
        "species": _named(species_name, "https://pokeapi.co/api/v2/pokemon-species/1/"),
        "evolution_details": [],
        "evolves_to": evolves_to or [],
    }


def _make_species(**overrides):
    base = {
        "id": 1,
        "name": "bulbasaur",
        "generation": _named("generation-i", "https://pokeapi.co/api/v2/generation/1/"),
        "color": _named("green", "https://pokeapi.co/api/v2/pokemon-color/5/"),
        "shape": _named("quadruped", "https://pokeapi.co/api/v2/pokemon-shape/8/"),
        "habitat": _named("grassland", "https://pokeapi.co/api/v2/pokemon-habitat/3/"),
        "capture_rate": 45,
        "base_happiness": 50,
        "gender_rate": 1,
        "egg_groups": [_named("monster", "https://pokeapi.co/api/v2/egg-group/1/")],
        "growth_rate": _named(
            "medium-slow", "https://pokeapi.co/api/v2/growth-rate/4/"
        ),
        "evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/1/"},
        "flavor_text_entries": [],
        "genera": [],
        "is_legendary": False,
        "is_mythical": False,
    }
    base.update(overrides)
    return base


class TestEvolutionDetail:
    def test_valid_level_up(self):
        d = EvolutionDetail.model_validate(_make_evolution_detail())
        assert d.trigger.name == "level-up"
        assert d.min_level == 16

    def test_all_optional_fields_none(self):
        d = EvolutionDetail.model_validate({"trigger": _named("level-up")})
        assert d.min_level is None
        assert d.item is None
        assert d.held_item is None
        assert d.known_move is None
        assert d.min_happiness is None
        assert d.min_beauty is None
        assert d.min_affection is None
        assert d.location is None

    def test_extra_fields_ignored(self):
        data = _make_evolution_detail()
        data["future_field"] = "ignored"
        d = EvolutionDetail.model_validate(data)
        assert not hasattr(d, "future_field")

    def test_boolean_defaults(self):
        d = EvolutionDetail.model_validate({"trigger": _named("level-up")})
        assert d.needs_overworld_rain is False
        assert d.turn_upside_down is False

    def test_time_of_day_default_empty_string(self):
        d = EvolutionDetail.model_validate({"trigger": _named("level-up")})
        assert d.time_of_day == ""


class TestEvolutionChain:
    def test_valid_single_stage(self):
        data = {
            "id": 67,
            "chain": _make_chain_link("eevee"),
        }
        ec = EvolutionChain.model_validate(data)
        assert ec.id == 67
        assert ec.chain.species.name == "eevee"
        assert ec.chain.evolves_to == []

    def test_three_stage_chain(self):
        venusaur = _make_chain_link(
            "venusaur",
            evolves_to=[],
        )
        venusaur["evolution_details"] = [_make_evolution_detail(min_level=32)]

        ivysaur = _make_chain_link(
            "ivysaur",
            evolves_to=[venusaur],
        )
        ivysaur["evolution_details"] = [_make_evolution_detail(min_level=16)]

        bulbasaur = _make_chain_link("bulbasaur", evolves_to=[ivysaur])

        ec = EvolutionChain.model_validate({"id": 1, "chain": bulbasaur})
        assert ec.chain.species.name == "bulbasaur"
        assert ec.chain.evolves_to[0].species.name == "ivysaur"
        assert ec.chain.evolves_to[0].evolves_to[0].species.name == "venusaur"
        assert ec.chain.evolves_to[0].evolution_details[0].min_level == 16

    def test_extra_fields_ignored(self):
        data = {"id": 1, "chain": _make_chain_link(), "future_field": True}
        ec = EvolutionChain.model_validate(data)
        assert not hasattr(ec, "future_field")


class TestPokemonSpecies:
    def test_valid(self):
        s = PokemonSpecies.model_validate(_make_species())
        assert s.id == 1
        assert s.name == "bulbasaur"
        assert s.capture_rate == 45
        assert s.gender_rate == 1
        assert s.is_legendary is False
        assert s.is_mythical is False

    def test_extra_fields_ignored(self):
        data = _make_species()
        data["future_field"] = "ignored"
        s = PokemonSpecies.model_validate(data)
        assert not hasattr(s, "future_field")

    def test_shape_and_habitat_nullable(self):
        s = PokemonSpecies.model_validate(_make_species(shape=None, habitat=None))
        assert s.shape is None
        assert s.habitat is None

    def test_base_happiness_nullable(self):
        s = PokemonSpecies.model_validate(_make_species(base_happiness=None))
        assert s.base_happiness is None

    def test_legendary_and_mythical_flags(self):
        s = PokemonSpecies.model_validate(
            _make_species(is_legendary=True, is_mythical=False)
        )
        assert s.is_legendary is True
        assert s.is_mythical is False

    def test_missing_required_name_raises(self):
        data = _make_species()
        del data["name"]
        with pytest.raises(ValidationError):
            PokemonSpecies.model_validate(data)
