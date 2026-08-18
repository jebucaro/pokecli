"""TOON (Token-Optimized Object Notation) serializer core.

Renders data into a compact, plain-text format optimized for LLM token efficiency.
All output is plain text with no Rich markup or ANSI codes.
"""


def _format_value(value: str | None) -> str:
    """Format a value for TOON output. None becomes '-'."""
    if value is None:
        return "-"
    return value


def _quote_if_needed(value: str) -> str:
    """Quote a value with double quotes if it contains commas."""
    if "," in value:
        return f'"{value}"'
    return value


def toon_single(label: str, fields: list[tuple[str, str | None]]) -> str:
    """Render a single resource as key:value pairs under a label.

    Example output:
        pokemon:
          id: 25
          name: pikachu
          types: electric
    """
    lines = [f"{label}:"]
    for key, value in fields:
        lines.append(f"  {key}: {_format_value(value)}")
    return "\n".join(lines)


def toon_list(
    label: str,
    schema_fields: list[str],
    rows: list[list[str | None]],
    total: int | None = None,
) -> str:
    """Render a list of items with schema header and indented rows.

    Example output:
        count: 14 of 8771 total
        moves[14]{name,method,level}:
          thunderbolt,level-up,5
          thunder,machine,-
    """
    count = len(rows)
    lines = []

    if total is not None:
        lines.append(f"count: {count} of {total} total")

    fields_str = ",".join(schema_fields)
    lines.append(f"{label}[{count}]{{{fields_str}}}:")

    for row in rows:
        formatted = [_quote_if_needed(_format_value(v)) for v in row]
        lines.append(f"  {','.join(formatted)}")

    return "\n".join(lines)


def toon_kv(pairs: list[tuple[str, str | None]]) -> str:
    """Render flat key:value lines.

    Example output:
        bin: ~/.local/bin/pokecli
        description: Look up Pokemon data from the terminal
    """
    lines = []
    for key, value in pairs:
        lines.append(f"{key}: {_format_value(value)}")
    return "\n".join(lines)


def toon_tree(label: str, lines: list[str]) -> str:
    """Render a tree structure (for evolution chains).

    Example output:
        evolution:
          Bulbasaur
            -> Ivysaur (level 16)
              -> Venusaur (level 32)
    """
    output = [f"{label}:"]
    for line in lines:
        output.append(f"  {line}")
    return "\n".join(output)


def print_toon(text: str) -> None:
    """Print TOON text to stdout. Plain text, no Rich markup."""
    print(text)
