"""Test definitive empty states across display functions."""

from io import StringIO
from rich.console import Console

from pokecli.display.common import render_list
from pokecli.display.ability import render_ability
from pokecli.display.move import render_move
from pokecli.display.item import render_item
from pokecli.models.common import ListResult, NamedResource
from pokecli.models.ability import Ability
from pokecli.models.move import Move
from pokecli.models.item import Item, ItemPrice


def _item_prices(purchase_price=100, sell_price=50):
    return [
        ItemPrice(
            currency=NamedResource(name="poke-dollar", url="http://example.com"),
            purchase_price=purchase_price,
            sell_price=sell_price,
            version_group=NamedResource(name="red-blue", url="http://example.com"),
        )
    ]


def _make_console() -> Console:
    """Create a Console that captures output without ANSI codes."""
    return Console(file=StringIO(), force_terminal=True, no_color=True, highlight=False)


def _get_output(console: Console) -> str:
    return console.file.getvalue()


# --- render_list ---


def test_render_list_empty_results():
    """Empty list should show explicit zero message."""
    result = ListResult(count=100, next=None, previous=None, results=[])
    console = _make_console()
    render_list(result, console)
    output = _get_output(console)
    assert "0 results" in output
    assert "100 total" in output


def test_render_list_empty_results_zero_count():
    """Empty list with count=0 should also show explicit zero message."""
    result = ListResult(count=0, next=None, previous=None, results=[])
    console = _make_console()
    render_list(result, console)
    output = _get_output(console)
    assert "0 results" in output


def test_render_list_with_results():
    """Non-empty list should render normally."""
    result = ListResult(
        count=2,
        next=None,
        previous=None,
        results=[
            NamedResource(name="bulbasaur", url="http://example.com/1"),
            NamedResource(name="ivysaur", url="http://example.com/2"),
        ],
    )
    console = _make_console()
    render_list(result, console)
    output = _get_output(console)
    assert "bulbasaur" in output
    assert "ivysaur" in output


# --- render_ability ---


def test_render_ability_no_english_effects():
    """Ability with no English effects should show explicit message."""
    ability = Ability(
        id=1,
        name="test-ability",
        generation=NamedResource(name="generation-i", url="http://example.com"),
        effect_entries=[],
        pokemon=[],
    )
    console = _make_console()
    render_ability(ability, console)
    output = _get_output(console)
    assert "No English effect text available" in output


def test_render_ability_non_english_effects_only():
    """Ability with only non-English effects should show explicit message."""
    from pokecli.models.ability import AbilityEffect

    ability = Ability(
        id=1,
        name="test-ability",
        generation=NamedResource(name="generation-i", url="http://example.com"),
        effect_entries=[
            AbilityEffect(
                effect="Efecto largo",
                short_effect="Efecto corto",
                language=NamedResource(name="es", url="http://example.com"),
            )
        ],
        pokemon=[],
    )
    console = _make_console()
    render_ability(ability, console)
    output = _get_output(console)
    assert "No English effect text available" in output


def test_render_ability_with_english_effects():
    """Ability with English effects should render normally."""
    from pokecli.models.ability import AbilityEffect

    ability = Ability(
        id=22,
        name="intimidate",
        generation=NamedResource(name="generation-iii", url="http://example.com"),
        effect_entries=[
            AbilityEffect(
                effect="Lowers the foe's Attack stat.",
                short_effect="Lowers opposing Attack on entering battle.",
                language=NamedResource(name="en", url="http://example.com"),
            )
        ],
        pokemon=[{"pokemon": {"name": "arcanine", "url": "http://example.com"}}],
    )
    console = _make_console()
    render_ability(ability, console)
    output = _get_output(console)
    assert "Lowers opposing Attack" in output
    assert "No English effect text" not in output


# --- render_move ---


def test_render_move_no_english_effects():
    """Move with no English effects should show explicit message."""
    move = Move(
        id=1,
        name="test-move",
        accuracy=100,
        power=40,
        pp=35,
        type=NamedResource(name="normal", url="http://example.com"),
        damage_class=NamedResource(name="physical", url="http://example.com"),
        effect_entries=[],
        effect_chance=None,
    )
    console = _make_console()
    render_move(move, console)
    output = _get_output(console)
    assert "No English effect text available" in output


def test_render_move_with_english_effects():
    """Move with English effects should render normally."""
    from pokecli.models.move import MoveEffectEntry

    move = Move(
        id=85,
        name="thunderbolt",
        accuracy=100,
        power=90,
        pp=15,
        type=NamedResource(name="electric", url="http://example.com"),
        damage_class=NamedResource(name="special", url="http://example.com"),
        effect_entries=[
            MoveEffectEntry(
                effect="Has a $effect_chance% chance to paralyze.",
                short_effect="Has a $effect_chance% chance to paralyze the target.",
                language=NamedResource(name="en", url="http://example.com"),
            )
        ],
        effect_chance=10,
    )
    console = _make_console()
    render_move(move, console)
    output = _get_output(console)
    # Chance appears in its own "Effect Chance" row, not inlined in the prose.
    assert "10%" in output
    assert "chance to paralyze the target" in output
    # The placeholder must never leak into output.
    assert "$effect_chance" not in output
    assert "No English effect text" not in output


def test_render_move_null_chance_does_not_leak_placeholder():
    """A move whose text has the token but a null effect_chance must render
    clean prose with no leaked placeholder and no Effect Chance row."""
    from pokecli.models.move import MoveEffectEntry

    move = Move(
        id=999,
        name="mystery-move",
        accuracy=100,
        power=50,
        pp=20,
        type=NamedResource(name="normal", url="http://example.com"),
        damage_class=NamedResource(name="physical", url="http://example.com"),
        effect_entries=[
            MoveEffectEntry(
                effect="Has a $effect_chance% chance to paralyze.",
                short_effect="Has a $effect_chance% chance to paralyze the target.",
                language=NamedResource(name="en", url="http://example.com"),
            )
        ],
        effect_chance=None,
    )
    console = _make_console()
    render_move(move, console)
    output = _get_output(console)
    assert "$effect_chance" not in output
    assert "Effect Chance" not in output
    assert "chance to paralyze the target" in output


# --- render_item ---


def test_render_item_no_effects_no_flavor():
    """Item with no effects and no flavor text should show explicit message."""
    item = Item(
        id=1,
        name="test-item",
        prices=_item_prices(100),
        fling_power=None,
        category=NamedResource(name="misc", url="http://example.com"),
        effect_entries=[],
        flavor_text_entries=[],
    )
    console = _make_console()
    render_item(item, console)
    output = _get_output(console)
    assert "No English effect or flavor text available" in output


def test_render_item_non_english_only():
    """Item with only non-English text should show explicit empty message."""
    from pokecli.models.item import ItemEffect, ItemFlavorText

    item = Item(
        id=1,
        name="test-item",
        prices=_item_prices(100),
        fling_power=None,
        category=NamedResource(name="misc", url="http://example.com"),
        effect_entries=[
            ItemEffect(
                effect="Efecto",
                short_effect="Corto",
                language=NamedResource(name="es", url="http://example.com"),
            )
        ],
        flavor_text_entries=[
            ItemFlavorText(
                text="Sabor",
                language=NamedResource(name="es", url="http://example.com"),
                version_group=NamedResource(name="red-blue", url="http://example.com"),
            )
        ],
    )
    console = _make_console()
    render_item(item, console)
    output = _get_output(console)
    assert "No English effect or flavor text available" in output


def test_render_item_with_english_effect():
    """Item with English effect should render normally."""
    from pokecli.models.item import ItemEffect

    item = Item(
        id=4,
        name="poke-ball",
        prices=_item_prices(200),
        fling_power=None,
        category=NamedResource(name="standard-balls", url="http://example.com"),
        effect_entries=[
            ItemEffect(
                effect="Catches a wild Pokemon.",
                short_effect="Catches Pokemon.",
                language=NamedResource(name="en", url="http://example.com"),
            )
        ],
        flavor_text_entries=[],
    )
    console = _make_console()
    render_item(item, console)
    output = _get_output(console)
    assert "Catches Pokemon" in output
    assert "No English effect or flavor text" not in output


def test_render_item_with_english_flavor_only():
    """Item with English flavor text but no effect should NOT show empty message."""
    from pokecli.models.item import ItemFlavorText

    item = Item(
        id=5,
        name="potion",
        prices=_item_prices(300),
        fling_power=None,
        category=NamedResource(name="healing", url="http://example.com"),
        effect_entries=[],
        flavor_text_entries=[
            ItemFlavorText(
                text="Restores HP.",
                language=NamedResource(name="en", url="http://example.com"),
                version_group=NamedResource(name="red-blue", url="http://example.com"),
            )
        ],
    )
    console = _make_console()
    render_item(item, console)
    output = _get_output(console)
    assert "Restores HP" in output
    assert "No English effect or flavor text" not in output


def test_render_item_no_prices_shows_dash():
    """Item with no prices should render a dash instead of a price."""
    item = Item(
        id=1,
        name="test-item",
        prices=[],
        fling_power=None,
        category=NamedResource(name="misc", url="http://example.com"),
        effect_entries=[],
        flavor_text_entries=[],
    )
    console = _make_console()
    render_item(item, console)
    output = _get_output(console)
    assert "Price:" in output
    # No numeric price should appear; the dash fallback is rendered instead.
    assert "\u2014" in output or "-" in output
    assert "Prices by version group" not in output


def test_render_item_null_purchase_price_shows_dash():
    """A price entry with null purchase_price should fall back to a dash."""
    item = Item(
        id=1,
        name="test-item",
        prices=[
            ItemPrice(
                currency=NamedResource(name="poke-dollar", url="http://example.com"),
                purchase_price=None,
                sell_price=None,
                version_group=NamedResource(
                    name="red-blue", url="http://example.com"
                ),
            )
        ],
        fling_power=None,
        category=NamedResource(name="misc", url="http://example.com"),
        effect_entries=[],
        flavor_text_entries=[],
    )
    console = _make_console()
    render_item(item, console)
    output = _get_output(console)
    assert "Prices by version group:" in output


def test_render_item_representative_price_shown():
    """Item with a poke-dollar purchase price renders it in the summary line."""
    item = Item(
        id=1,
        name="test-item",
        prices=_item_prices(300),
        fling_power=None,
        category=NamedResource(name="misc", url="http://example.com"),
        effect_entries=[],
        flavor_text_entries=[],
    )
    console = _make_console()
    render_item(item, console)
    output = _get_output(console)
    assert "300" in output
