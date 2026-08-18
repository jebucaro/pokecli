"""Tests for the contextual hints engine."""


from pokecli.display.hints import format_hints_table, format_hints_toon, get_hints


class TestGetHintsPokemonGet:
    """Tests for get_hints with pokemon.get command."""

    def test_returns_three_hints(self):
        hints = get_hints("pokemon.get", {"name": "pikachu"})
        assert len(hints) == 3

    def test_includes_moves_hint(self):
        hints = get_hints("pokemon.get", {"name": "pikachu"})
        assert "pokecli pokemon moves pikachu" in hints

    def test_includes_evolution_hint(self):
        hints = get_hints("pokemon.get", {"name": "pikachu"})
        assert "pokecli pokemon evolution pikachu" in hints

    def test_includes_encounters_hint(self):
        hints = get_hints("pokemon.get", {"name": "pikachu"})
        assert "pokecli pokemon encounters pikachu" in hints

    def test_uses_provided_name(self):
        hints = get_hints("pokemon.get", {"name": "charizard"})
        assert "pokecli pokemon moves charizard" in hints
        assert "pokecli pokemon evolution charizard" in hints
        assert "pokecli pokemon encounters charizard" in hints


class TestGetHintsMoveGet:
    """Tests for get_hints with move.get command."""

    def test_returns_hints_with_type(self):
        hints = get_hints("move.get", {"name": "thunderbolt", "type": "electric"})
        assert len(hints) == 2
        assert "pokecli pokemon can-learn <pokemon_name> thunderbolt" in hints
        assert "pokecli type get electric" in hints

    def test_returns_hints_without_type(self):
        hints = get_hints("move.get", {"name": "thunderbolt"})
        assert len(hints) == 1
        assert "pokecli pokemon can-learn <pokemon_name> thunderbolt" in hints


class TestGetHintsListCommands:
    """Tests for get_hints with list commands."""

    def test_list_with_first_name(self):
        hints = get_hints("pokemon.list", {"resource": "pokemon", "first_name": "bulbasaur"})
        assert hints == ["pokecli pokemon get bulbasaur"]

    def test_list_without_first_name(self):
        hints = get_hints("move.list", {"resource": "move"})
        assert hints == []

    def test_list_with_different_resource(self):
        hints = get_hints("ability.list", {"resource": "ability", "first_name": "stench"})
        assert hints == ["pokecli ability get stench"]


class TestGetHintsOtherCommands:
    """Tests for get_hints with various other commands."""

    def test_pokemon_moves(self):
        hints = get_hints("pokemon.moves", {"name": "eevee"})
        assert "pokecli pokemon can-learn eevee <move_name>" in hints
        assert "pokecli pokemon get eevee" in hints

    def test_pokemon_species(self):
        hints = get_hints("pokemon.species", {"name": "eevee"})
        assert "pokecli pokemon evolution eevee" in hints
        assert "pokecli pokemon forms eevee" in hints

    def test_pokemon_evolution(self):
        hints = get_hints("pokemon.evolution", {"name": "charmander"})
        assert "pokecli pokemon get charmander" in hints
        assert "pokecli pokemon species charmander" in hints

    def test_pokemon_encounters_with_area(self):
        hints = get_hints("pokemon.encounters", {"name": "pikachu", "first_area": "viridian-forest-area"})
        assert "pokecli location area get viridian-forest-area" in hints
        assert "pokecli pokemon get pikachu" in hints

    def test_pokemon_encounters_without_area(self):
        hints = get_hints("pokemon.encounters", {"name": "pikachu"})
        assert "pokecli location area get <area_name>" in hints

    def test_pokemon_forms_with_variety(self):
        hints = get_hints("pokemon.forms", {"name": "charizard", "first_variety": "charizard-mega-x"})
        assert "pokecli pokemon form get charizard-mega-x" in hints

    def test_pokemon_forms_without_variety(self):
        hints = get_hints("pokemon.forms", {"name": "pikachu"})
        assert "pokecli pokemon form get <variety>" in hints

    def test_type_get_with_super_effective(self):
        hints = get_hints("type.get", {"name": "fire", "super_effective": ["grass", "ice", "bug"]})
        assert "pokecli type get grass" in hints
        assert "pokecli pokemon list" in hints

    def test_type_get_without_super_effective(self):
        hints = get_hints("type.get", {"name": "fire"})
        assert "pokecli pokemon list" in hints

    def test_location_get_with_area(self):
        hints = get_hints("location.get", {"name": "pallet-town", "first_area": "pallet-town-area"})
        assert "pokecli location area get pallet-town-area" in hints

    def test_location_get_without_area(self):
        hints = get_hints("location.get", {"name": "pallet-town"})
        assert hints == []

    def test_location_area_get(self):
        hints = get_hints("location_area.get", {"name": "kanto-route-1-area", "location": "kanto-route-1"})
        assert "pokecli location get kanto-route-1" in hints

    def test_region_get_with_location(self):
        hints = get_hints("region.get", {"name": "kanto", "first_location": "pallet-town"})
        assert "pokecli location get pallet-town" in hints

    def test_region_get_without_location(self):
        hints = get_hints("region.get", {"name": "kanto"})
        assert hints == []

    def test_unknown_command(self):
        hints = get_hints("unknown.command", {"name": "something"})
        assert hints == []


class TestFormatHintsToon:
    """Tests for format_hints_toon."""

    def test_produces_correct_output(self):
        hints = [
            "pokecli pokemon moves pikachu",
            "pokecli pokemon evolution pikachu",
            "pokecli pokemon encounters pikachu",
        ]
        result = format_hints_toon(hints)
        expected = (
            "help[3]:\n"
            "  Run `pokecli pokemon moves pikachu`\n"
            "  Run `pokecli pokemon evolution pikachu`\n"
            "  Run `pokecli pokemon encounters pikachu`"
        )
        assert result == expected

    def test_single_hint(self):
        result = format_hints_toon(["pokecli berry list"])
        assert result == "help[1]:\n  Run `pokecli berry list`"

    def test_empty_hints_returns_empty_string(self):
        result = format_hints_toon([])
        assert result == ""


class TestFormatHintsTable:
    """Tests for format_hints_table."""

    def test_produces_correct_output(self):
        hints = [
            "pokecli pokemon moves pikachu",
            "pokecli pokemon evolution pikachu",
        ]
        result = format_hints_table(hints)
        assert "[dim]Next steps:[/dim]" in result
        assert "[dim]  → pokecli pokemon moves pikachu[/dim]" in result
        assert "[dim]  → pokecli pokemon evolution pikachu[/dim]" in result
        # Should start with a blank line for spacing
        assert result.startswith("\n")

    def test_single_hint(self):
        result = format_hints_table(["pokecli berry list"])
        assert "→ pokecli berry list" in result
        assert "Next steps:" in result

    def test_empty_hints_returns_empty_string(self):
        result = format_hints_table([])
        assert result == ""
