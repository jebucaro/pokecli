from pokecli.display.common import extract_effect_and_chance


class TestExtractEffectAndChance:
    def test_token_with_percent_and_chance(self):
        text, chance = extract_effect_and_chance(
            "Has a $effect_chance% chance to paralyze the target.", 10
        )
        assert text == "Has a chance to paralyze the target."
        assert chance == 10
        assert "$effect_chance" not in text

    def test_bare_token_without_percent(self):
        text, chance = extract_effect_and_chance(
            "Has a $effect_chance chance to burn the target.", 10
        )
        assert text == "Has a chance to burn the target."
        assert chance == 10

    def test_repeated_token(self):
        text, chance = extract_effect_and_chance(
            "Has a $effect_chance% chance to burn and a $effect_chance% chance to flinch.",
            10,
        )
        assert "$effect_chance" not in text
        assert text == "Has a chance to burn and a chance to flinch."
        assert chance == 10

    def test_token_with_null_chance_does_not_leak(self):
        text, chance = extract_effect_and_chance(
            "Has a $effect_chance% chance to paralyze the target.", None
        )
        assert "$effect_chance" not in text
        assert text == "Has a chance to paralyze the target."
        assert chance is None

    def test_chance_present_but_no_token(self):
        text, chance = extract_effect_and_chance(
            "Inflicts regular damage.", 30
        )
        assert text == "Inflicts regular damage."
        assert chance == 30

    def test_no_token_no_chance(self):
        text, chance = extract_effect_and_chance("Inflicts regular damage.", None)
        assert text == "Inflicts regular damage."
        assert chance is None

    def test_whitespace_normalized(self):
        text, _ = extract_effect_and_chance(
            "Lowers   Attack  $effect_chance%  sharply .", 10
        )
        assert "  " not in text
        assert text == "Lowers Attack sharply."

    def test_empty_string(self):
        text, chance = extract_effect_and_chance("", None)
        assert text == ""
        assert chance is None
