"""Tests for the resource table that drives the generic command handlers."""

import pytest
from pydantic import BaseModel

from pokecli.resources import (
    RESOURCE_NAMES,
    RESOURCES,
    RESOURCES_BY_NAME,
    get_resource,
)

EXPECTED_NAMES = {
    "pokemon",
    "pokemon-species",
    "pokemon-form",
    "evolution-chain",
    "move",
    "item",
    "ability",
    "type",
    "nature",
    "berry",
    "location",
    "location-area",
    "region",
    "generation",
    "version",
    "version-group",
    "pokedex",
    "machine",
}


def test_table_holds_exactly_the_specified_vocabulary():
    assert set(RESOURCE_NAMES) == EXPECTED_NAMES
    assert len(RESOURCES) == 18


def test_resource_names_are_unique():
    assert len(set(RESOURCE_NAMES)) == len(RESOURCE_NAMES)


def test_lookup_by_name_covers_every_row():
    for name in RESOURCE_NAMES:
        assert get_resource(name) is not None
    assert get_resource("natrue") is None
    assert set(RESOURCES_BY_NAME) == EXPECTED_NAMES


@pytest.mark.parametrize("resource", RESOURCES, ids=lambda r: r.name)
def test_every_row_is_fully_wired(resource):
    """A missing model, renderer, or TOON builder fails here, not at invocation."""
    assert isinstance(resource.name, str) and resource.name
    assert isinstance(resource.purpose, str) and len(resource.purpose) > 10

    assert isinstance(resource.model, type)
    assert issubclass(resource.model, BaseModel)

    assert callable(resource.render)

    # Exactly one TOON strategy per row.
    assert (resource.toon is None) != (resource.toon_pair is None), (
        f"{resource.name} must define either toon or toon_pair, not both or neither"
    )
    if resource.toon is not None:
        assert callable(resource.toon)
    else:
        assert callable(resource.toon_pair)

    assert isinstance(resource.toon_label, str) and resource.toon_label
    assert isinstance(resource.list_label, str) and resource.list_label

    if resource.toon_extra is not None:
        assert callable(resource.toon_extra)
    if resource.hint_context is not None:
        assert callable(resource.hint_context)


@pytest.mark.parametrize("resource", RESOURCES, ids=lambda r: r.name)
def test_labels_contain_no_hyphens(resource):
    """TOON keys must be valid identifiers-style keys, not hyphenated names."""
    assert "-" not in resource.toon_label
    assert "-" not in resource.list_label


def test_every_resource_has_a_cache_table():
    """Cached reads and `cache clear --resource` depend on a matching table."""
    from pokecli.cache.store import RESOURCE_TABLES

    assert set(RESOURCE_NAMES) <= set(RESOURCE_TABLES)



def test_resource_panel_lists_every_resource_with_its_purpose_in_table_order():
    from rich.console import Console

    from pokecli.commands._resource_help import resource_panel

    console = Console(width=200, record=True, color_system=None)
    console.print(resource_panel())
    lines = console.export_text().splitlines()

    assert "Resources" in lines[0]
    rows = [line.strip("│ ").split(maxsplit=1) for line in lines[1:-1]]
    assert rows == [[r.name, r.purpose] for r in RESOURCES]
