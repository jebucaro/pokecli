"""Output format resolution.

Format is resolved at two levels only: an explicit ``--format`` wins, otherwise
the execution context decides. An interactive terminal gets human-readable
``table`` output; anything else - a pipe, a redirect, an agent subprocess - gets
token-optimized ``toon``. Automated callers therefore need no flag.
"""

import sys

import typer

FORMATS: tuple[str, ...] = ("table", "toon", "json")


def validate_format(value: str | None) -> str | None:
    """Reject an unrecognized ``--format`` value, naming the accepted ones."""
    if value is None:
        return None
    if value not in FORMATS:
        raise typer.BadParameter(
            f"'{value}' is not a valid format. Choose from: {', '.join(FORMATS)}"
        )
    return value


def stdout_is_interactive() -> bool:
    """Whether standard output is an interactive terminal.

    A detached or closed stream counts as non-interactive, so an automated
    caller never receives styled output by accident.
    """
    try:
        return sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False


def resolve_format(explicit: str | None) -> str:
    """Return the format to render in.

    An explicit value always wins. Otherwise ``table`` when stdout is an
    interactive terminal, ``toon`` when it is not.
    """
    if explicit is not None:
        return explicit
    return "table" if stdout_is_interactive() else "toon"
