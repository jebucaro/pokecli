"""Regression tests for the Windows "success-looks-like-an-error" bug.

When stdout is not UTF-8 (e.g. a redirected/legacy Windows console using cp1252
with errors="strict"), printing a character the codec cannot encode raises
UnicodeEncodeError. That crash propagates out of an otherwise successful command
and the shell sees a non-zero exit code. These tests drive the success output
paths against a cp1252 console and assert they render without crashing.
"""

import io

import pytest
from rich.console import Console

from pokecli.display.common import uses_unicode
from pokecli.display.pokemon import _stat_bar, render_pokemon
from pokecli.models.pokemon import Pokemon


def _cp1252_console() -> tuple[Console, io.BytesIO]:
    """A non-UTF-8 console that mimics a redirected legacy Windows stdout."""
    buf = io.BytesIO()
    stream = io.TextIOWrapper(buf, encoding="cp1252", errors="strict")
    console = Console(file=stream, force_terminal=False, width=80)
    return console, buf


def _named(name="fire", url="https://pokeapi.co/api/v2/type/10/"):
    return {"name": name, "url": url}


def _make_pokemon(**overrides):
    base = {
        "id": 6,
        "name": "charizard",
        "height": 17,
        "weight": 905,
        "base_experience": 240,
        "types": [{"slot": 1, "type": _named("fire")}],
        # Two abilities so the bullet separator is actually rendered between them.
        "abilities": [
            {"slot": 1, "is_hidden": False, "ability": _named("blaze")},
            {"slot": 3, "is_hidden": True, "ability": _named("solar-power")},
        ],
        "stats": [{"base_stat": 90, "effort": 0, "stat": _named("speed")}],
        "sprites": {"front_default": "https://sprites.example.com/6.png"},
    }
    base.update(overrides)
    return Pokemon.model_validate(base)


def test_uses_unicode_gates_on_encoding():
    cp1252, _ = _cp1252_console()
    utf8 = Console(file=io.TextIOWrapper(io.BytesIO(), encoding="utf-8"))
    assert uses_unicode(cp1252) is False
    assert uses_unicode(utf8) is True


def test_render_pokemon_does_not_crash_on_cp1252():
    console, buf = _cp1252_console()
    render_pokemon(_make_pokemon(), console)
    console.file.flush()  # would raise UnicodeEncodeError if a glyph leaked through
    output = buf.getvalue().decode("cp1252")
    # ASCII bullet fallback is used, not the Unicode middle dot.
    assert "|" in output
    assert "·" not in output


def test_stat_bar_ascii_fallback_is_pure_ascii():
    bar = _stat_bar(90, unicode=False)
    bar.encode("cp1252")  # must not raise
    assert set(bar) <= {"#", "."}


def test_checkmark_crashes_but_ascii_marker_is_safe():
    """Documents why install.py gates the marker: the raw checkmark is unencodable."""
    console, _ = _cp1252_console()
    with pytest.raises(UnicodeEncodeError):
        console.print("✓")
        console.file.flush()

    safe, buf = _cp1252_console()
    safe.print("[OK] Skills installed")
    safe.file.flush()
    assert "[OK]" in buf.getvalue().decode("cp1252")
