import pytest
from pydantic import ValidationError

from pokecli.models.location import (
    EncounterDetail,
    Location,
    LocationArea,
    PokemonEncounter,
    Region,
)


def _named(name, url="..."):
    return {"name": name, "url": url}


class TestRegion:
    def test_valid(self):
        data = {
            "id": 1,
            "name": "kanto",
            "locations": [_named("pallet-town"), _named("viridian-city")],
            "main_generation": _named("generation-i"),
            "pokedexes": [_named("kanto")],
            "version_groups": [_named("red-blue")],
        }
        r = Region.model_validate(data)
        assert r.name == "kanto"
        assert len(r.locations) == 2
        assert r.main_generation.name == "generation-i"

    def test_null_main_generation_allowed(self):
        r = Region.model_validate(
            {"id": 99, "name": "future-region", "main_generation": None}
        )
        assert r.main_generation is None


class TestLocation:
    def test_valid(self):
        data = {
            "id": 1,
            "name": "pallet-town",
            "region": _named("kanto"),
            "areas": [_named("pallet-town-area")],
        }
        loc = Location.model_validate(data)
        assert loc.name == "pallet-town"
        assert loc.region.name == "kanto"
        assert loc.areas[0].name == "pallet-town-area"

    def test_null_region_allowed(self):
        loc = Location.model_validate({"id": 1, "name": "void", "region": None})
        assert loc.region is None


class TestEncounterDetail:
    def test_valid(self):
        e = EncounterDetail.model_validate(
            {
                "min_level": 2,
                "max_level": 4,
                "chance": 35,
                "method": _named("walk"),
                "condition_values": [],
            }
        )
        assert e.min_level == 2
        assert e.max_level == 4
        assert e.chance == 35
        assert e.method.name == "walk"


class TestPokemonEncounter:
    def test_valid_nested(self):
        data = {
            "pokemon": _named("pidgey"),
            "version_details": [
                {
                    "version": _named("red"),
                    "max_chance": 25,
                    "encounter_details": [
                        {
                            "min_level": 2,
                            "max_level": 4,
                            "chance": 25,
                            "method": _named("walk"),
                        }
                    ],
                }
            ],
        }
        pe = PokemonEncounter.model_validate(data)
        assert pe.pokemon.name == "pidgey"
        assert pe.version_details[0].max_chance == 25
        assert pe.version_details[0].encounter_details[0].chance == 25


class TestLocationArea:
    def test_valid_with_encounters(self):
        data = {
            "id": 1,
            "name": "kanto-route-1-area",
            "game_index": 1,
            "location": _named("kanto-route-1"),
            "pokemon_encounters": [
                {
                    "pokemon": _named("pidgey"),
                    "version_details": [
                        {
                            "version": _named("red"),
                            "max_chance": 50,
                            "encounter_details": [],
                        }
                    ],
                }
            ],
            "encounter_method_rates": [],
        }
        la = LocationArea.model_validate(data)
        assert la.name == "kanto-route-1-area"
        assert la.location.name == "kanto-route-1"
        assert len(la.pokemon_encounters) == 1

    def test_missing_required_location_raises(self):
        with pytest.raises(ValidationError):
            LocationArea.model_validate({"id": 1, "name": "x", "game_index": 0})
