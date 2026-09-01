"""Tests for the TOON output helper and toons serialization integration."""

import toons

from pokecli.display.toon import print_toon


class TestPrintToon:
    """Tests for print_toon."""

    def test_prints_to_stdout(self, capsys):
        print_toon("pokemon:\n  id: 25\n  name: pikachu")
        captured = capsys.readouterr()
        assert "pokemon:\n  id: 25\n  name: pikachu\n" == captured.out

    def test_no_ansi_codes(self, capsys):
        print_toon("test: value")
        captured = capsys.readouterr()
        # No ANSI escape sequences
        assert "\x1b[" not in captured.out


class TestToonsSingle:
    """Serialization of a single resource dict via toons.dumps."""

    def test_renders_label_and_fields(self):
        result = toons.dumps({"pokemon": {
            "id": 25,
            "name": "pikachu",
            "types": "electric",
        }})
        expected = "pokemon:\n  id: 25\n  name: pikachu\n  types: electric"
        assert result == expected

    def test_none_values_render_as_null(self):
        result = toons.dumps({"move": {
            "id": 1,
            "name": "pound",
            "power": None,
        }})
        assert "  power: null" in result


class TestToonsList:
    """Serialization of a uniform list[dict] via toons.dumps (tabular)."""

    def test_renders_tabular_header_and_rows(self):
        result = toons.dumps({"moves": [
            {"name": "thunderbolt", "method": "machine", "level": 0},
            {"name": "thunder", "method": "level-up", "level": 42},
        ]})
        assert "moves[2]{name,method,level}:" in result
        assert "  thunderbolt,machine,0" in result
        assert "  thunder,level-up,42" in result

    def test_empty_list_renders_zero_header(self):
        result = toons.dumps({"encounters": []})
        assert result == "encounters[0]:"

    def test_values_with_commas_get_quoted(self):
        result = toons.dumps({"items": [
            {"name": "potion", "effect": "Restores HP by 20, max 100"},
        ]})
        assert '  potion,"Restores HP by 20, max 100"' in result

    def test_none_values_in_rows_render_as_null(self):
        result = toons.dumps({"moves": [
            {"name": "growl", "power": None},
        ]})
        assert "  growl,null" in result


class TestToonsNested:
    """Serialization of a nested node (evolution chain) via toons.dumps."""

    def test_renders_nested_tree(self):
        node = {
            "name": "bulbasaur",
            "trigger": None,
            "evolves_to": [
                {"name": "ivysaur", "trigger": "level 16"},
                {"name": "venusaur", "trigger": "level 32"},
            ],
        }
        result = toons.dumps({"evolution_chain_1": node})
        assert result.startswith("evolution_chain_1:")
        assert "  name: bulbasaur" in result
        assert "  trigger: null" in result
        assert "evolves_to[2]{name,trigger}:" in result
        assert "ivysaur,level 16" in result
