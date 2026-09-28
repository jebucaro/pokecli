"""Derived commands.

Each one answers a question rather than returning a record: it joins more than
one API response, or filters a nested collection. That is why they carry
dedicated names instead of being expressed as a resource read.
"""

from collections import Counter
from typing import Optional

import toons
import typer
from pydantic import ValidationError
from rich.console import Console

from pokecli.cache.store import CacheStore
from pokecli.commands._format import resolve_format, validate_format
from pokecli.commands._helptext import (
    FORMAT,
    METHOD_FILTER,
    MOVE_NAME,
    NO_CACHE,
    POKEMON_NAME_OR_ID,
)
from pokecli.commands._utils import api_request, fetch_resource
from pokecli.config import LEARN_METHODS, VERSION_GROUP_ORDER
from pokecli.display.common import render_json
from pokecli.display.evolution import render_evolution
from pokecli.display.hints import format_hints_table, format_hints_toon, get_hints
from pokecli.display.location import render_encounters
from pokecli.display.pokemon import render_pokemon_moves
from pokecli.display.pokemon_form import render_pokemon_varieties
from pokecli.display.toon import print_toon
from pokecli.display.toon_schemas import (
    encounters_toon,
    evolution_chain_toon,
    pokemon_moves_toon,
)
from pokecli.models.evolution import EvolutionChain
from pokecli.models.pokemon import PokemonMoveEntry

console = Console()
err_console = Console(stderr=True)


def validate_method(value: str | None) -> str | None:
    """Reject an unknown ``--method`` as a usage error (exit 2), naming the valid ones.

    For ``can-learn`` this matters: exit 1 means "no", so a typo must not reach
    the check and come back as a wrong answer.
    """
    if value is None:
        return None
    method = value.strip().lower().replace(" ", "-")
    if method not in LEARN_METHODS:
        raise typer.BadParameter(
            f"'{value}' is not a valid learn method. "
            f"Choose from: {', '.join(LEARN_METHODS)}"
        )
    return method


def _emit_hints(hints: list[str], fmt: str) -> None:
    if not hints:
        return
    if fmt == "toon":
        text = format_hints_toon(hints)
        if text:
            print_toon("\n" + text)
    elif fmt == "table":
        console.print(format_hints_table(hints))


_VERSION_GROUP_RANK = {name: rank for rank, name in enumerate(VERSION_GROUP_ORDER)}


def _version_group_recency(detail: dict) -> tuple[int, int]:
    """Sort key placing a version group by release, newest highest.

    A group missing from ``VERSION_GROUP_ORDER`` is assumed to be a release
    newer than the list, since PokeAPI adds new games as they ship. Its ID
    breaks ties between several unknown groups.
    """
    group = detail["version_group"]
    group_id = int(group["url"].rstrip("/").split("/")[-1])
    return (_VERSION_GROUP_RANK.get(group["name"], len(VERSION_GROUP_ORDER)), group_id)


def _extract_moves(raw_moves: list[dict]) -> list[PokemonMoveEntry]:
    """Deduplicate moves across all versions, keeping the most recent learn method."""
    seen: dict[str, PokemonMoveEntry] = {}
    for entry in raw_moves:
        move_name = entry["move"]["name"]
        details = entry.get("version_group_details", [])
        if not details:
            continue
        best = max(details, key=_version_group_recency)
        seen[move_name] = PokemonMoveEntry(
            name=move_name,
            learn_method=best["move_learn_method"]["name"],
            level=best["level_learned_at"],
        )
    return sorted(
        seen.values(), key=lambda m: (m.learn_method != "level-up", m.level, m.name)
    )


def moves(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option(
        None, "--format", help=FORMAT, callback=validate_format
    ),
    method: Optional[str] = typer.Option(
        None, "--method", help=METHOD_FILTER, callback=validate_method
    ),
) -> None:
    """Show the moves a Pokemon can learn."""
    fmt = resolve_format(format)
    client = ctx.obj["client"]
    data = fetch_resource(client, "pokemon", name_or_id, no_cache, err_console)
    pokemon_name = data["name"]
    pokemon_moves = _extract_moves(data.get("moves", []))

    if method is not None:
        pokemon_moves = [m for m in pokemon_moves if m.learn_method == method]

    if not pokemon_moves:
        _render_moves_empty(pokemon_name, method, fmt)
        return

    hints = get_hints("moves", {"name": pokemon_name})

    if fmt == "json":
        render_json(
            {"name": pokemon_name, "moves": [m.model_dump() for m in pokemon_moves]},
            console,
        )
        return

    if fmt == "toon":
        rows = pokemon_moves_toon(pokemon_name, pokemon_moves)
        method_counts = Counter(m.learn_method for m in pokemon_moves)
        methods_str = ", ".join(f"{k}:{v}" for k, v in sorted(method_counts.items()))
        print_toon(
            toons.dumps(
                {
                    "pokemon": pokemon_name,
                    "count": len(pokemon_moves),
                    "methods": methods_str,
                    "moves": rows,
                }
            )
        )
    else:
        render_pokemon_moves(pokemon_name, pokemon_moves, console, method_filter=method)

    _emit_hints(hints, fmt)


def _render_moves_empty(pokemon_name: str, method: str | None, fmt: str) -> None:
    """A Pokemon with no matching moves is a zero result, not a failure."""
    if fmt == "json":
        render_json({"name": pokemon_name, "moves": [], "count": 0}, console)
        return
    if fmt == "toon":
        payload: dict = {"pokemon": pokemon_name}
        if method is not None:
            payload["method"] = method
        payload["count"] = 0
        payload["result"] = (
            f"No {method} moves found" if method else "No recorded moves"
        )
        print_toon(toons.dumps(payload))
        return
    if method is not None:
        console.print(f"[dim]{pokemon_name} has no {method} moves.[/dim]")
    else:
        console.print(f"[dim]{pokemon_name} has no recorded moves.[/dim]")


def can_learn(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    move_name: str = typer.Argument(..., help=MOVE_NAME),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option(
        None, "--format", help=FORMAT, callback=validate_format
    ),
    method: Optional[str] = typer.Option(
        None, "--method", help=METHOD_FILTER, callback=validate_method
    ),
) -> None:
    """Check whether a Pokemon can learn a move. Exit code carries the answer."""
    fmt = resolve_format(format)
    client = ctx.obj["client"]
    data = fetch_resource(client, "pokemon", name_or_id, no_cache, err_console)
    pokemon_name = data["name"]
    pokemon_moves = _extract_moves(data.get("moves", []))

    target = move_name.strip().lower().replace(" ", "-")
    matched = [m for m in pokemon_moves if m.name == target]
    if method is not None:
        matched = [m for m in matched if m.learn_method == method]

    if fmt == "json":
        if matched:
            render_json(
                {
                    "pokemon": pokemon_name,
                    "move": target,
                    "can_learn": True,
                    "method": matched[0].learn_method,
                    "level": matched[0].level,
                },
                console,
            )
        else:
            render_json(
                {"pokemon": pokemon_name, "move": target, "can_learn": False},
                console,
            )
    elif fmt == "toon":
        if matched:
            print_toon(
                toons.dumps(
                    {
                        "pokemon": pokemon_name,
                        "move": target,
                        "can_learn": True,
                        "method": matched[0].learn_method,
                        "level": matched[0].level if matched[0].level > 0 else None,
                    }
                )
            )
        else:
            print_toon(
                toons.dumps(
                    {
                        "pokemon": pokemon_name,
                        "move": target,
                        "can_learn": False,
                    }
                )
            )
    else:
        if matched:
            render_pokemon_moves(pokemon_name, matched, console, move_filter=target)
        else:
            suffix = f" via {method}" if method else ""
            err_console.print(
                f"[yellow]{pokemon_name.capitalize()} cannot learn "
                f"{target}{suffix}.[/yellow]"
            )

    if not matched:
        raise typer.Exit(1)


def evolution(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option(
        None, "--format", help=FORMAT, callback=validate_format
    ),
) -> None:
    """Show the full evolution chain a Pokemon belongs to."""
    fmt = resolve_format(format)
    client = ctx.obj["client"]

    species_data = fetch_resource(
        client, "pokemon-species", name_or_id, no_cache, err_console
    )
    chain_url = species_data["evolution_chain"]["url"]
    chain_id = chain_url.rstrip("/").split("/")[-1]

    with CacheStore() as cache:
        chain_data = None if no_cache else cache.get("evolution-chain", chain_id)
        if chain_data is None:
            chain_data = api_request(
                lambda: client.get_resource_by_url(chain_url), err_console
            )
            cache.set("evolution-chain", chain_id, chain_data)

    try:
        chain = EvolutionChain.model_validate(chain_data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)

    hints = get_hints("evolution", {"name": species_data.get("name", name_or_id)})

    if fmt == "json":
        render_json(chain.model_dump(), console)
        return

    if fmt == "toon":
        label, node = evolution_chain_toon(chain)
        print_toon(toons.dumps({label: node}))
    else:
        render_evolution(chain, console)

    _emit_hints(hints, fmt)


def encounters(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option(
        None, "--format", help=FORMAT, callback=validate_format
    ),
) -> None:
    """Show where a Pokemon appears in the wild."""
    fmt = resolve_format(format)
    client = ctx.obj["client"]
    data = fetch_resource(client, "pokemon", name_or_id, no_cache, err_console)
    pokemon_name = data["name"]

    result = api_request(
        lambda: client.get_subresource("pokemon", pokemon_name, "encounters"),
        err_console,
    )

    first_area = result[0]["location_area"]["name"] if result else None
    hints = get_hints(
        "encounters", {"name": pokemon_name, "first_area": first_area}
    )

    if fmt == "json":
        render_json({"pokemon": pokemon_name, "encounters": result}, console)
        return

    if fmt == "toon":
        if not result:
            print_toon(
                toons.dumps(
                    {
                        "pokemon": pokemon_name,
                        "areas": 0,
                        "result": "No recorded encounter locations",
                    }
                )
            )
        else:
            print_toon(
                toons.dumps(
                    {
                        "pokemon": pokemon_name,
                        "areas": len(result),
                        "encounters": encounters_toon(pokemon_name, result),
                    }
                )
            )
    else:
        render_encounters(pokemon_name, result, console)

    _emit_hints(hints, fmt)


def forms(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option(
        None, "--format", help=FORMAT, callback=validate_format
    ),
) -> None:
    """Show a species' varieties, like Mega, Alolan, or Gigantamax forms."""
    fmt = resolve_format(format)
    client = ctx.obj["client"]
    species_data = fetch_resource(
        client, "pokemon-species", name_or_id, no_cache, err_console
    )
    species_name = species_data["name"]
    varieties = species_data.get("varieties", [])

    first_variety = None
    for v in varieties:
        if not v.get("is_default", True):
            first_variety = v.get("pokemon", {}).get("name")
            break
    hints = get_hints(
        "forms", {"name": species_name, "first_variety": first_variety}
    )

    if fmt == "json":
        render_json({"species": species_name, "varieties": varieties}, console)
        return

    if fmt == "toon":
        if not varieties:
            print_toon(
                toons.dumps(
                    {
                        "species": species_name,
                        "count": 0,
                        "result": "No varieties recorded",
                    }
                )
            )
        else:
            rows = [
                {
                    "name": v.get("pokemon", {}).get("name", "-"),
                    "is_default": bool(v.get("is_default", False)),
                }
                for v in varieties
            ]
            print_toon(toons.dumps({"species": species_name, "varieties": rows}))
    else:
        render_pokemon_varieties(species_name, varieties, console)

    _emit_hints(hints, fmt)
