"""Tests for next-step hints.

Hints are the one place where command paths live in strings rather than in the
command tree, so a restructure cannot break them by signature. They are also
agent-facing instructions, which makes a stale hint actively misleading. The
validity test at the bottom is the guard.
"""

import pytest
import typer.main

from pokecli.display.hints import (
    _HINT_BUILDERS,
    format_hints_table,
    format_hints_toon,
    get_hints,
)
from pokecli.main import app
from pokecli.resources import RESOURCE_NAMES

# Context values rich enough for every builder to take its populated branch.
FULL_CONTEXT = {
    "name": "pikachu",
    "resource": "pokemon",
    "first_name": "bulbasaur",
    "first_area": "trophy-garden-area",
    "first_variety": "pikachu-gmax",
    "first_location": "pallet-town",
    "location": "canalave-city",
    "base_species": "charmander",
    "super_effective": ["grass", "ice"],
    "type": "electric",
}


class TestGetPokemon:
    def test_returns_three_hints(self):
        hints = get_hints("get.pokemon", {"name": "pikachu"})
        assert len(hints) == 3

    def test_suggests_moves_evolution_and_encounters(self):
        hints = get_hints("get.pokemon", {"name": "pikachu"})
        assert "pokecli moves pikachu" in hints
        assert "pokecli evolution pikachu" in hints
        assert "pokecli encounters pikachu" in hints

    def test_uses_the_resolved_name(self):
        hints = get_hints("get.pokemon", {"name": "charizard"})
        assert all("charizard" in h for h in hints)


class TestGetMove:
    def test_suggests_can_learn_and_the_type(self):
        hints = get_hints("get.move", {"name": "thunderbolt", "type": "electric"})
        assert "pokecli can-learn <pokemon_name> thunderbolt" in hints
        assert "pokecli get type electric" in hints

    def test_omits_the_type_hint_when_absent(self):
        hints = get_hints("get.move", {"name": "thunderbolt", "type": None})
        assert hints == ["pokecli can-learn <pokemon_name> thunderbolt"]


class TestGetType:
    def test_suggests_the_first_super_effective_type(self):
        hints = get_hints("get.type", {"name": "fire", "super_effective": ["grass"]})
        assert "pokecli get type grass" in hints

    def test_falls_back_without_super_effective(self):
        hints = get_hints("get.type", {"name": "normal", "super_effective": []})
        assert hints == ["pokecli list pokemon"]


class TestGetLocation:
    def test_suggests_the_first_area(self):
        hints = get_hints("get.location", {"name": "x", "first_area": "kanto-route-1-area"})
        assert hints == ["pokecli get location-area kanto-route-1-area"]

    def test_returns_nothing_without_areas(self):
        assert get_hints("get.location", {"name": "x", "first_area": None}) == []


class TestGetLocationArea:
    def test_points_back_at_the_parent_location(self):
        hints = get_hints("get.location-area", {"name": "a", "location": "canalave-city"})
        assert hints == ["pokecli get location canalave-city"]


class TestGetRegion:
    def test_suggests_the_first_location(self):
        hints = get_hints("get.region", {"name": "kanto", "first_location": "pallet-town"})
        assert hints == ["pokecli get location pallet-town"]


class TestGetEvolutionChain:
    def test_suggests_the_base_species(self):
        hints = get_hints("get.evolution-chain", {"base_species": "charmander"})
        assert "pokecli evolution charmander" in hints

    def test_falls_back_without_a_base_species(self):
        hints = get_hints("get.evolution-chain", {"base_species": None})
        assert hints == ["pokecli get pokemon <species>"]


class TestDerivedCommands:
    def test_moves(self):
        hints = get_hints("moves", {"name": "pikachu"})
        assert "pokecli can-learn pikachu <move_name>" in hints
        assert "pokecli get pokemon pikachu" in hints

    def test_evolution(self):
        hints = get_hints("evolution", {"name": "eevee"})
        assert "pokecli get pokemon eevee" in hints
        assert "pokecli get pokemon-species eevee" in hints

    def test_encounters_with_an_area(self):
        hints = get_hints("encounters", {"name": "pikachu", "first_area": "forest-area"})
        assert "pokecli get location-area forest-area" in hints

    def test_encounters_without_an_area(self):
        hints = get_hints("encounters", {"name": "mewtwo", "first_area": None})
        assert "pokecli get location-area <area_name>" in hints

    def test_forms_with_a_variety(self):
        hints = get_hints("forms", {"name": "charizard", "first_variety": "charizard-mega-x"})
        assert hints == ["pokecli get pokemon-form charizard-mega-x"]

    def test_forms_without_a_variety(self):
        hints = get_hints("forms", {"name": "tauros", "first_variety": None})
        assert hints == ["pokecli get pokemon-form <variety>"]


class TestListAndSearch:
    def test_list_points_at_a_concrete_record(self):
        hints = get_hints("list.pokemon", {"resource": "pokemon", "first_name": "bulbasaur"})
        assert hints == ["pokecli get pokemon bulbasaur"]

    def test_search_shares_the_list_shape(self):
        hints = get_hints("search.move", {"resource": "move", "first_name": "thunderbolt"})
        assert hints == ["pokecli get move thunderbolt"]

    def test_empty_page_produces_no_hint(self):
        assert get_hints("list.pokemon", {"resource": "pokemon", "first_name": None}) == []

    @pytest.mark.parametrize("resource", RESOURCE_NAMES)
    def test_every_resource_gets_a_list_hint(self, resource):
        hints = get_hints(
            f"list.{resource}", {"resource": resource, "first_name": "example"}
        )
        assert hints == [f"pokecli get {resource} example"]


class TestUnknownCommand:
    def test_returns_no_hints(self):
        assert get_hints("nonexistent", {"name": "x"}) == []


class TestFormatting:
    def test_toon_formatting_produces_a_help_array(self):
        assert format_hints_toon(["pokecli moves pikachu"]).startswith("help")

    def test_toon_formatting_of_nothing_is_empty(self):
        assert format_hints_toon([]) == ""

    def test_table_formatting_is_dim_markup(self):
        text = format_hints_table(["pokecli moves pikachu"])
        assert "Next steps" in text
        assert "pokecli moves pikachu" in text

    def test_table_formatting_of_nothing_is_empty(self):
        assert format_hints_table([]) == ""


# --------------------------------------------------------------------------
# validity: every hint must be runnable
# --------------------------------------------------------------------------


def _all_emitted_hints() -> list[tuple[str, str]]:
    """Every hint every builder can emit, paired with its command key."""
    emitted: list[tuple[str, str]] = []
    keys = [*_HINT_BUILDERS]
    keys += [f"list.{name}" for name in RESOURCE_NAMES]
    keys += [f"search.{name}" for name in RESOURCE_NAMES]
    for key in keys:
        for hint in get_hints(key, dict(FULL_CONTEXT)):
            emitted.append((key, hint))
    # Also exercise the empty-context branch of every builder.
    for key in keys:
        for hint in get_hints(key, {}):
            emitted.append((key, hint))
    return emitted


def test_there_are_hints_to_validate():
    assert len(_all_emitted_hints()) > 30


@pytest.mark.parametrize(
    ("key", "hint"), _all_emitted_hints(), ids=lambda v: str(v)[:60]
)
def test_every_hint_resolves_to_a_real_command(key, hint):
    """A hint naming a command or resource that does not exist misleads an agent."""
    registered = typer.main.get_command(app).commands
    argv = hint.split()

    assert argv[0] == "pokecli", f"{key}: {hint}"
    assert argv[1] in registered, f"{key}: '{argv[1]}' is not a registered command"

    if argv[1] in {"get", "list", "search"}:
        target = argv[2]
        assert target in RESOURCE_NAMES, (
            f"{key}: '{target}' is not a valid resource"
        )


@pytest.mark.parametrize(
    ("key", "hint"), _all_emitted_hints(), ids=lambda v: str(v)[:60]
)
def test_no_hint_uses_a_removed_addressing_scheme(key, hint):
    removed = {
        "pokemon",
        "move",
        "item",
        "ability",
        "type",
        "nature",
        "berry",
        "location",
        "game",
        "image",
        "region",
        "generation",
        "pokedex",
        "version",
        "version-group",
        "machine",
        "location-area",
        "pokemon-form",
        "evolution-chain",
    }
    assert hint.split()[1] not in removed, f"{key}: {hint} uses a removed path"
