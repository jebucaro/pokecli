"""Generic resource commands: ``get``, ``list``, and ``search``.

These three handlers serve every resource in the table. Per-resource behavior
comes from the table row, never from a branch here, so a resource cannot
acquire behavior its peers lack.
"""

import toons
import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from pokecli.commands._format import resolve_format, validate_format
from pokecli.commands._helptext import (
    FORMAT,
    LIMIT,
    NAME_OR_ID,
    NO_CACHE,
    OFFSET,
    RESOURCE,
    SEARCH_QUERY,
)
from pokecli.commands._utils import fetch_list, fetch_name_index, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.hints import format_hints_table, format_hints_toon, get_hints
from pokecli.display.toon import print_toon
from pokecli.display.toon_schemas import resource_list_toon
from pokecli.resources import RESOURCE_NAMES, RESOURCES_BY_NAME

console = Console()
err_console = Console(stderr=True)


def complete_resource(incomplete: str) -> list[str]:
    """Shell completion for the ``<resource>`` argument, fed from the table."""
    return [name for name in RESOURCE_NAMES if name.startswith(incomplete)]


def validate_resource(value: str) -> str:
    """Constrain ``<resource>`` to the table, naming every accepted value."""
    name = value.strip().lower()
    if name not in RESOURCES_BY_NAME:
        raise typer.BadParameter(
            f"'{value}' is not a valid resource. "
            f"Choose from: {', '.join(RESOURCE_NAMES)}"
        )
    return name


def _emit_hints(hints: list[str], fmt: str) -> None:
    """Attach next-step hints to table and toon output. JSON stays parseable."""
    if not hints:
        return
    if fmt == "toon":
        text = format_hints_toon(hints)
        if text:
            print_toon("\n" + text)
    elif fmt == "table":
        console.print(format_hints_table(hints))


def get(
    ctx: typer.Context,
    resource: str = typer.Argument(
        ...,
        help=RESOURCE,
        callback=validate_resource,
        autocompletion=complete_resource,
        metavar="RESOURCE",
    ),
    name_or_id: str = typer.Argument(..., help=NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option(
        None, "--format", help=FORMAT, callback=validate_format
    ),
) -> None:
    """Fetch one resource record by name or ID."""
    res = RESOURCES_BY_NAME[resource]
    fmt = resolve_format(format)
    client = ctx.obj["client"]

    data = fetch_resource(client, res.name, name_or_id, no_cache, err_console)
    try:
        model = res.model.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)

    hint_ctx: dict = {"name": getattr(model, "name", str(name_or_id))}
    if res.hint_context is not None:
        hint_ctx.update(res.hint_context(model))
    hints = get_hints(f"get.{res.name}", hint_ctx)

    if fmt == "json":
        render_json(model.model_dump(), console)
        return

    if fmt == "toon":
        if res.toon_pair is not None:
            label, fields = res.toon_pair(model)
        else:
            label, fields = res.toon_label, res.toon(model)
        if res.toon_extra is not None:
            fields.update(res.toon_extra(model, data))
        print_toon(toons.dumps({label: fields}))
    else:
        res.render(model, console)

    _emit_hints(hints, fmt)


def list_resources(
    ctx: typer.Context,
    resource: str = typer.Argument(
        ...,
        help=RESOURCE,
        callback=validate_resource,
        autocompletion=complete_resource,
        metavar="RESOURCE",
    ),
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
    format: str = typer.Option(
        None, "--format", help=FORMAT, callback=validate_format
    ),
) -> None:
    """Browse a resource's records with pagination."""
    fmt = resolve_format(format)

    res = RESOURCES_BY_NAME[resource]
    client = ctx.obj["client"]
    result = fetch_list(client, res.name, limit, offset, err_console)

    first_name = result.results[0].name if result.results else None
    hints = get_hints(
        f"list.{res.name}", {"resource": res.name, "first_name": first_name}
    )

    if fmt == "json":
        render_json(result.model_dump(), console)
        return

    if fmt == "toon":
        rows = resource_list_toon(result)
        print_toon(f"count: {len(rows)} of {result.count} total")
        print_toon(toons.dumps({res.list_label: rows}))
    else:
        render_list(result, console)

    _emit_hints(hints, fmt)


def search(
    ctx: typer.Context,
    resource: str = typer.Argument(
        ...,
        help=RESOURCE,
        callback=validate_resource,
        autocompletion=complete_resource,
        metavar="RESOURCE",
    ),
    query: str = typer.Argument(..., help=SEARCH_QUERY),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option(
        None, "--format", help=FORMAT, callback=validate_format
    ),
) -> None:
    """Find resource names containing a substring."""
    res = RESOURCES_BY_NAME[resource]
    fmt = resolve_format(format)
    client = ctx.obj["client"]

    index = fetch_name_index(client, res.name, no_cache, err_console)
    needle = query.strip().lower()
    matches = [
        entry for entry in index if needle in str(entry.get("name", "")).lower()
    ]

    first_name = matches[0].get("name") if matches else None
    hints = get_hints(
        f"search.{res.name}", {"resource": res.name, "first_name": first_name}
    )
    rows = [{"name": entry.get("name", "")} for entry in matches]

    if fmt == "json":
        render_json(
            {"resource": res.name, "query": needle, "count": len(rows), "matches": rows},
            console,
        )
        return

    if fmt == "toon":
        print_toon(f"count: {len(rows)} of {len(index)} total")
        if rows:
            print_toon(toons.dumps({res.list_label: rows}))
        else:
            print_toon(toons.dumps({"result": f"No {res.name} names match '{needle}'"}))
    else:
        if not rows:
            console.print(
                f"[dim]No {res.name} names match '{needle}'. "
                f"({len(index)} searched)[/dim]"
            )
        else:
            table = Table(
                title=f"{len(rows)} match(es) for '{needle}' in {res.name}",
                show_lines=False,
            )
            table.add_column("Name", style="bold cyan")
            for row in rows:
                table.add_row(row["name"])
            console.print(table)

    _emit_hints(hints, fmt)
