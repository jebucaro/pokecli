import pytest
from pydantic import ValidationError

from pokecli.models.game import (
    Generation,
    Pokedex,
    PokedexEntry,
    Version,
    VersionGroup,
)


def _named(name, url):
    return {"name": name, "url": url}


def _en_name(name):
    return {"name": name, "language": _named("en", "...")}


class TestVersion:
    def test_valid(self):
        data = {
            "id": 1,
            "name": "red",
            "names": [_en_name("Red")],
            "version_group": _named(
                "red-blue", "https://pokeapi.co/api/v2/version-group/1/"
            ),
        }
        v = Version.model_validate(data)
        assert v.id == 1
        assert v.name == "red"
        assert v.version_group.name == "red-blue"
        assert v.names[0].name == "Red"

    def test_missing_version_group_raises(self):
        with pytest.raises(ValidationError):
            Version.model_validate({"id": 1, "name": "red"})


class TestVersionGroup:
    def test_valid(self):
        data = {
            "id": 1,
            "name": "red-blue",
            "order": 3,
            "generation": _named("generation-i", "..."),
            "versions": [_named("red", "..."), _named("blue", "...")],
            "regions": [_named("kanto", "...")],
            "move_learn_methods": [_named("level-up", "...")],
            "pokedexes": [_named("kanto", "...")],
        }
        vg = VersionGroup.model_validate(data)
        assert vg.order == 3
        assert vg.generation.name == "generation-i"
        assert len(vg.versions) == 2
        assert vg.regions[0].name == "kanto"

    def test_empty_lists_default(self):
        vg = VersionGroup.model_validate(
            {
                "id": 1,
                "name": "x",
                "order": 1,
                "generation": _named("g", "u"),
            }
        )
        assert vg.versions == []
        assert vg.regions == []


class TestGeneration:
    def test_valid(self):
        data = {
            "id": 1,
            "name": "generation-i",
            "main_region": _named("kanto", "..."),
            "pokemon_species": [_named("bulbasaur", "..."), _named("ivysaur", "...")],
            "moves": [_named("pound", "...")],
            "version_groups": [_named("red-blue", "...")],
            "abilities": [],
            "types": [],
        }
        g = Generation.model_validate(data)
        assert g.name == "generation-i"
        assert g.main_region.name == "kanto"
        assert len(g.pokemon_species) == 2
        assert g.moves[0].name == "pound"

    def test_missing_main_region_raises(self):
        with pytest.raises(ValidationError):
            Generation.model_validate({"id": 1, "name": "g"})


class TestPokedexEntry:
    def test_valid(self):
        e = PokedexEntry.model_validate(
            {"entry_number": 1, "pokemon_species": _named("bulbasaur", "...")}
        )
        assert e.entry_number == 1
        assert e.pokemon_species.name == "bulbasaur"


class TestPokedex:
    def test_valid_with_region(self):
        data = {
            "id": 2,
            "name": "kanto",
            "is_main_series": True,
            "region": _named("kanto", "..."),
            "pokemon_entries": [
                {"entry_number": 1, "pokemon_species": _named("bulbasaur", "...")},
                {"entry_number": 25, "pokemon_species": _named("pikachu", "...")},
            ],
            "version_groups": [_named("red-blue", "...")],
        }
        p = Pokedex.model_validate(data)
        assert p.is_main_series is True
        assert p.region.name == "kanto"
        assert len(p.pokemon_entries) == 2
        assert p.pokemon_entries[1].entry_number == 25

    def test_null_region_allowed(self):
        data = {
            "id": 1,
            "name": "national",
            "is_main_series": True,
            "region": None,
        }
        p = Pokedex.model_validate(data)
        assert p.region is None
