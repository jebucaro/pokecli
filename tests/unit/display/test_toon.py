"""Tests for the TOON serializer core."""



from pokecli.display.toon import (
    toon_single,
    toon_list,
    toon_kv,
    toon_tree,
    print_toon,
)


class TestToonSingle:
    """Tests for toon_single."""

    def test_renders_label_and_fields(self):
        result = toon_single("pokemon", [
            ("id", "25"),
            ("name", "pikachu"),
            ("types", "electric"),
        ])
        expected = "pokemon:\n  id: 25\n  name: pikachu\n  types: electric"
        assert result == expected

    def test_renders_stats_format(self):
        result = toon_single("pokemon", [
            ("id", "25"),
            ("name", "pikachu"),
            ("stats", "35/55/40/50/50/90"),
        ])
        assert "  stats: 35/55/40/50/50/90" in result

    def test_none_values_render_as_dash(self):
        result = toon_single("move", [
            ("id", "1"),
            ("name", "pound"),
            ("power", None),
        ])
        assert "  power: -" in result


class TestToonList:
    """Tests for toon_list."""

    def test_renders_header_with_count_and_rows(self):
        result = toon_list(
            "moves",
            ["name", "method", "level"],
            [
                ["thunderbolt", "machine", "0"],
                ["thunder", "level-up", "42"],
            ],
        )
        assert "moves[2]{name,method,level}:" in result
        assert "  thunderbolt,machine,0" in result
        assert "  thunder,level-up,42" in result

    def test_with_total_shows_count_line(self):
        result = toon_list(
            "pokemon",
            ["name"],
            [["pikachu"], ["charizard"]],
            total=1010,
        )
        assert "count: 2 of 1010 total" in result
        assert "pokemon[2]{name}:" in result

    def test_empty_rows_shows_definitive_empty_state(self):
        result = toon_list(
            "encounters",
            ["area", "version", "method"],
            [],
        )
        assert "encounters[0]{area,version,method}:" in result
        # Should have no indented rows
        lines = result.strip().split("\n")
        assert len(lines) == 1

    def test_empty_rows_with_total(self):
        result = toon_list(
            "pokemon",
            ["name"],
            [],
            total=0,
        )
        assert "count: 0 of 0 total" in result
        assert "pokemon[0]{name}:" in result

    def test_values_with_commas_get_quoted(self):
        result = toon_list(
            "items",
            ["name", "effect"],
            [["potion", "Restores HP by 20, max 100"]],
        )
        assert '  potion,"Restores HP by 20, max 100"' in result

    def test_none_values_in_rows_render_as_dash(self):
        result = toon_list(
            "moves",
            ["name", "power"],
            [["growl", None]],
        )
        assert "  growl,-" in result


class TestToonKv:
    """Tests for toon_kv."""

    def test_renders_flat_pairs(self):
        result = toon_kv([
            ("bin", "~/.local/bin/pokecli"),
            ("description", "Look up Pokemon data from the terminal"),
        ])
        expected = (
            "bin: ~/.local/bin/pokecli\n"
            "description: Look up Pokemon data from the terminal"
        )
        assert result == expected

    def test_none_value_renders_as_dash(self):
        result = toon_kv([("key", None)])
        assert result == "key: -"


class TestToonTree:
    """Tests for toon_tree."""

    def test_renders_tree_with_label_and_lines(self):
        result = toon_tree("evolution", [
            "Bulbasaur",
            "  -> Ivysaur (level 16)",
            "    -> Venusaur (level 32)",
        ])
        expected = (
            "evolution:\n"
            "  Bulbasaur\n"
            "    -> Ivysaur (level 16)\n"
            "      -> Venusaur (level 32)"
        )
        assert result == expected


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
