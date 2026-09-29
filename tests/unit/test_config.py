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


def test_version_group_versions_cover_exactly_the_ordered_groups():
    from pokecli.config import VERSION_GROUP_ORDER, VERSION_GROUP_VERSIONS

    assert tuple(VERSION_GROUP_VERSIONS) == VERSION_GROUP_ORDER


def test_every_version_belongs_to_exactly_one_group():
    from pokecli.config import VERSION_GROUP_VERSIONS

    versions = [v for vs in VERSION_GROUP_VERSIONS.values() for v in vs]
    assert len(versions) == len(set(versions))
    assert all(VERSION_GROUP_VERSIONS.values())


def test_version_group_versions_match_pokeapi_examples():
    from pokecli.config import VERSION_GROUP_VERSIONS

    assert VERSION_GROUP_VERSIONS["red-blue"] == ("red", "blue")
    assert VERSION_GROUP_VERSIONS["yellow"] == ("yellow",)
    assert VERSION_GROUP_VERSIONS["the-isle-of-armor"] == (
        "the-isle-of-armor-sword",
        "the-isle-of-armor-shield",
    )
