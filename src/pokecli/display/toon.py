"""TOON output helper.

Serialization is delegated to the third-party ``toons`` library via
``toons.dumps``. This module only provides the stdout print helper used across
command handlers so TOON output stays plain text with no Rich markup or ANSI
codes.
"""


def print_toon(text: str) -> None:
    """Print TOON text to stdout. Plain text, no Rich markup."""
    print(text)
