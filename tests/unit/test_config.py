"""Tests for shared configuration constants."""

from pokecli.config import LEARN_METHODS


def test_learn_methods_hold_pokeapis_vocabulary_with_common_methods_first():
    """Mirrors PokeAPI's `move-learn-method` resource (12 entries)."""
    assert LEARN_METHODS[:4] == ("level-up", "machine", "tutor", "egg")
    assert set(LEARN_METHODS) == {
        "level-up",
        "machine",
        "tutor",
        "egg",
        "stadium-surfing-pikachu",
        "light-ball-egg",
        "colosseum-purification",
        "xd-shadow",
        "xd-purification",
        "form-change",
        "zygarde-cube",
        "train",
    }
    assert len(LEARN_METHODS) == len(set(LEARN_METHODS))


def test_method_help_names_every_learn_method():
    from pokecli.commands._helptext import METHOD_FILTER

    for method in LEARN_METHODS:
        assert method in METHOD_FILTER


def test_version_group_order_is_unique_and_starts_with_gen_one():
    from pokecli.config import VERSION_GROUP_ORDER

    assert len(VERSION_GROUP_ORDER) == len(set(VERSION_GROUP_ORDER))
    assert VERSION_GROUP_ORDER.index("blue-japan") < VERSION_GROUP_ORDER.index("scarlet-violet")
