import httpx
import typer
from pydantic import ValidationError
from rich.console import Console
from typing import Optional

from pokecli.cache.store import CacheStore
from pathlib import Path

from pokecli.commands import evolution_chain, image, pokemon_form
from pokecli.commands._group import ResourceGroup
from pokecli.commands._helptext import (
    FORMAT,
    LIMIT,
    METHOD_FILTER,
    MOVE_FILTER,
    MOVE_NAME,
    NO_CACHE,
    OFFSET,
    OUTPUT_PATH,
    POKEMON_NAME_OR_ID,
    SPRITE_VARIANT,
)
from pokecli.commands._utils import fetch_list, fetch_resource
from pokecli.config import DEFAULT_LIMIT, DEFAULT_OFFSET
from pokecli.display.common import render_json, render_list
from pokecli.display.evolution import render_evolution, render_species
from pokecli.display.location import render_encounters
from pokecli.display.pokemon import render_pokemon, render_pokemon_moves
from pokecli.display.pokemon_form import render_pokemon_varieties
from pokecli.models.evolution import EvolutionChain, PokemonSpecies
from pokecli.models.pokemon import Pokemon, PokemonMoveEntry

app = typer.Typer(
    help="Look up Pokemon, evolutions, encounters, moves, and forms.",
    cls=ResourceGroup,
    epilog=(
        "Examples:\n"
        "  pokecli pokemon pikachu\n"
        "  pokecli pokemon can-learn pikachu thunderbolt\n"
        "  pokecli pokemon where pikachu\n"
        "  pokecli pokemon form get charizard-mega-x\n"
        "  pokecli pokemon image pikachu -o pikachu.png"
    ),
)
console = Console()
err_console = Console(stderr=True)


@app.command()
def get(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show a Pokemon's main profile, stats, types, and abilities."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "pokemon", name_or_id, no_cache, err_console)
    try:
        pokemon = Pokemon.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    hints = get_hints("pokemon.get", {"name": pokemon.name})

    if format == "json":
        render_json(pokemon.model_dump(), console)
    elif format == "toon":
        from pokecli.display.toon import toon_single, print_toon
        from pokecli.display.toon_schemas import pokemon_toon
        fields = pokemon_toon(pokemon)
        # Add aggregate: total_moves from raw data
        total_moves = len(data.get("moves", []))
        fields.append(("total_moves", str(total_moves)))
        print_toon(toon_single("pokemon", fields))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        render_pokemon(pokemon, console)
        if hints:
            console.print(format_hints_table(hints))


def _extract_moves(raw_moves: list[dict]) -> list[PokemonMoveEntry]:
    """Deduplicate moves across all versions, keeping the most recent learn method."""
    seen: dict[str, PokemonMoveEntry] = {}
    for entry in raw_moves:
        move_name = entry["move"]["name"]
        details = entry.get("version_group_details", [])
        if not details:
            continue
        # Pick the version group with the highest numeric ID (most recent)
        best = max(
            details,
            key=lambda d: int(d["version_group"]["url"].rstrip("/").split("/")[-1]),
        )
        seen[move_name] = PokemonMoveEntry(
            name=move_name,
            learn_method=best["move_learn_method"]["name"],
            level=best["level_learned_at"],
        )
    return sorted(
        seen.values(), key=lambda m: (m.learn_method != "level-up", m.level, m.name)
    )


def _render_move_check(
    pokemon_name: str,
    move_lower: str,
    matched: list[PokemonMoveEntry],
    format: str,
    console: Console,
    err_console: Console,
) -> bool:
    """Handle --move filter output for all formats. Returns True if should exit with code 1."""
    if format == "json":
        if matched:
            render_json(
                {
                    "pokemon": pokemon_name,
                    "move": move_lower,
                    "can_learn": True,
                    "method": matched[0].learn_method,
                    "level": matched[0].level,
                },
                console,
            )
        else:
            render_json(
                {"pokemon": pokemon_name, "move": move_lower, "can_learn": False},
                console,
            )
            return True
    elif format == "toon":
        from pokecli.display.toon import toon_kv, print_toon

        if matched:
            print_toon(toon_kv([
                ("pokemon", pokemon_name),
                ("move", move_lower),
                ("can_learn", "true"),
                ("method", matched[0].learn_method),
                ("level", str(matched[0].level) if matched[0].level > 0 else "-"),
            ]))
        else:
            print_toon(toon_kv([
                ("pokemon", pokemon_name),
                ("move", move_lower),
                ("can_learn", "false"),
            ]))
            return True
    else:
        if matched:
            render_pokemon_moves(
                pokemon_name, matched, console, move_filter=move_lower
            )
        else:
            err_console.print(
                f"[yellow]{pokemon_name.capitalize()} cannot learn {move_lower}.[/yellow]"
            )
            return True
    return False


def _render_moves_empty(
    pokemon_name: str, method: str | None, format: str, console: Console
) -> None:
    """Handle the case when no moves are found."""
    if format == "json":
        render_json(
            {"name": pokemon_name, "moves": [], "count": 0},
            console,
        )
    elif format == "toon":
        from pokecli.display.toon import toon_kv, print_toon

        if method is not None:
            print_toon(toon_kv([
                ("pokemon", pokemon_name),
                ("method", method),
                ("count", "0"),
                ("result", f"No {method} moves found"),
            ]))
        else:
            print_toon(toon_kv([
                ("pokemon", pokemon_name),
                ("count", "0"),
                ("result", "No recorded moves"),
            ]))
    else:
        if method is not None:
            console.print(f"[dim]{pokemon_name} has no {method} moves.[/dim]")
        else:
            console.print(f"[dim]{pokemon_name} has no recorded moves.[/dim]")


def _render_moves_toon(
    pokemon_name: str,
    pokemon_moves: list[PokemonMoveEntry],
    hints: list[str],
    _console: Console,
) -> None:
    """Render moves in TOON format with hints."""
    from collections import Counter
    from pokecli.display.toon import toon_list, toon_kv, print_toon
    from pokecli.display.toon_schemas import pokemon_moves_toon
    from pokecli.display.hints import format_hints_toon

    schema_fields, rows = pokemon_moves_toon(pokemon_name, pokemon_moves)
    method_counts = Counter(m.learn_method for m in pokemon_moves)
    methods_str = ", ".join(f"{k}:{v}" for k, v in sorted(method_counts.items()))
    header = toon_kv([
        ("pokemon", pokemon_name),
        ("count", str(len(pokemon_moves))),
        ("methods", methods_str),
    ])
    body = toon_list("moves", schema_fields, rows)
    print_toon(header + "\n" + body)
    hint_text = format_hints_toon(hints)
    if hint_text:
        print_toon("\n" + hint_text)


@app.command()
def moves(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
    move: Optional[str] = typer.Option(None, "--move", help=MOVE_FILTER),
    method: Optional[str] = typer.Option(
        None,
        "--method",
        help=METHOD_FILTER,
    ),
) -> None:
    """Show the moves a Pokemon can learn."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "pokemon", name_or_id, no_cache, err_console)
    pokemon_name = data["name"]
    pokemon_moves = _extract_moves(data.get("moves", []))

    if move is not None:
        move_lower = move.lower().replace(" ", "-")
        matched = [m for m in pokemon_moves if m.name == move_lower]
        should_exit = _render_move_check(
            pokemon_name, move_lower, matched, format, console, err_console
        )
        if should_exit:
            raise typer.Exit(1)
        return

    if method is not None:
        pokemon_moves = [m for m in pokemon_moves if m.learn_method == method]

    if not pokemon_moves:
        _render_moves_empty(pokemon_name, method, format, console)
        return

    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    hints = get_hints("pokemon.moves", {"name": pokemon_name})

    if format == "json":
        render_json(
            {"name": pokemon_name, "moves": [m.model_dump() for m in pokemon_moves]},
            console,
        )
    elif format == "toon":
        _render_moves_toon(pokemon_name, pokemon_moves, hints, console)
    else:
        render_pokemon_moves(pokemon_name, pokemon_moves, console, method_filter=method)
        if hints:
            console.print(format_hints_table(hints))


@app.command()
def species(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show Pokedex entry, egg groups, capture rate, and species details."""
    client = ctx.obj["client"]
    data = fetch_resource(client, "pokemon-species", name_or_id, no_cache, err_console)
    try:
        poke_species = PokemonSpecies.model_validate(data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)
    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    hints = get_hints("pokemon.species", {"name": poke_species.name})

    if format == "json":
        render_json(poke_species.model_dump(), console)
    elif format == "toon":
        from pokecli.display.toon import toon_single, print_toon
        from pokecli.display.toon_schemas import species_toon
        fields = species_toon(poke_species)
        print_toon(toon_single("species", fields))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        render_species(poke_species, console)
        if hints:
            console.print(format_hints_table(hints))


@app.command()
def evolution(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show the full evolution chain for a Pokemon."""
    client = ctx.obj["client"]

    # Step 1: fetch species to get evolution chain URL
    species_data = fetch_resource(
        client, "pokemon-species", name_or_id, no_cache, err_console
    )
    chain_url = species_data["evolution_chain"]["url"]
    chain_id = chain_url.rstrip("/").split("/")[-1]

    # Step 2: fetch evolution chain (with caching)
    with CacheStore() as cache:
        key = chain_id
        chain_data = None if no_cache else cache.get("evolution-chain", key)
        if chain_data is None:
            try:
                chain_data = client.get_resource_by_url(chain_url)
            except httpx.HTTPStatusError as e:
                err_console.print(f"[red]API error: {e.response.status_code}[/red]")
                raise typer.Exit(1)
            except (httpx.ConnectError, httpx.TimeoutException):
                err_console.print("[red]Network error: could not reach PokeAPI[/red]")
                raise typer.Exit(1)
            cache.set("evolution-chain", key, chain_data)

    try:
        chain = EvolutionChain.model_validate(chain_data)
    except ValidationError as e:
        err_console.print(f"[red]Unexpected API response format:[/red]\n{e}")
        raise typer.Exit(2)

    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    hints = get_hints("pokemon.evolution", {"name": name_or_id})

    if format == "json":
        render_json(chain.model_dump(), console)
    elif format == "toon":
        from pokecli.display.toon import toon_tree, print_toon
        from pokecli.display.toon_schemas import evolution_chain_toon
        label, lines = evolution_chain_toon(chain)
        print_toon(toon_tree(label, lines))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        render_evolution(chain, console)
        if hints:
            console.print(format_hints_table(hints))


def _render_encounters_toon(
    pokemon_name: str, result: list, _console: Console
) -> None:
    """Render encounters in TOON format with hints."""
    from pokecli.display.toon import toon_list, toon_kv, print_toon
    from pokecli.display.toon_schemas import encounters_toon
    from pokecli.display.hints import get_hints, format_hints_toon

    first_area = result[0]["location_area"]["name"] if result else None
    hints = get_hints("pokemon.encounters", {"name": pokemon_name, "first_area": first_area})
    schema_fields, rows = encounters_toon(pokemon_name, result)
    areas_count = len(result)
    if not result:
        print_toon(toon_kv([
            ("pokemon", pokemon_name),
            ("areas", "0"),
            ("result", "No recorded encounter locations"),
        ]))
    else:
        header = toon_kv([
            ("pokemon", pokemon_name),
            ("areas", str(areas_count)),
        ])
        body = toon_list("encounters", schema_fields, rows)
        print_toon(header + "\n" + body)
    hint_text = format_hints_toon(hints)
    if hint_text:
        print_toon("\n" + hint_text)


@app.command()
def encounters(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show where a Pokemon appears in the wild."""
    client = ctx.obj["client"]
    # Resolve identifier to canonical pokemon name (handles ID input)
    data = fetch_resource(client, "pokemon", name_or_id, no_cache, err_console)
    pokemon_name = data["name"]
    try:
        result = client.get_subresource("pokemon", pokemon_name, "encounters")
    except httpx.HTTPStatusError as e:
        err_console.print(f"[red]API error: {e.response.status_code}[/red]")
        raise typer.Exit(1)
    except (httpx.ConnectError, httpx.TimeoutException):
        err_console.print("[red]Network error: could not reach PokeAPI[/red]")
        raise typer.Exit(1)

    if format == "json":
        render_json({"pokemon": pokemon_name, "encounters": result}, console)
    elif format == "toon":
        _render_encounters_toon(pokemon_name, result, console)
    else:
        from pokecli.display.hints import get_hints, format_hints_table
        first_area = result[0]["location_area"]["name"] if result else None
        hints = get_hints("pokemon.encounters", {"name": pokemon_name, "first_area": first_area})
        render_encounters(pokemon_name, result, console)
        if hints:
            console.print(format_hints_table(hints))


@app.command()
def where(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Quick shortcut for catch location lookups."""
    encounters(ctx, name_or_id=name_or_id, no_cache=no_cache, format=format)


@app.command(name="image")
def image_cmd(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    output: Path = typer.Option(..., "--output", "-o", help=OUTPUT_PATH),
    variant: str = typer.Option(
        "front_default",
        "--variant",
        help=SPRITE_VARIANT,
    ),
) -> None:
    """Download a sprite without leaving the Pokemon command."""
    image.download(
        ctx,
        resource="pokemon",
        name_or_id=name_or_id,
        output=output,
        variant=variant,
    )


@app.command(name="can-learn")
def can_learn(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    move_name: str = typer.Argument(..., help=MOVE_NAME),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
    method: Optional[str] = typer.Option(
        None,
        "--method",
        help=METHOD_FILTER,
    ),
) -> None:
    """Check whether a Pokemon can learn a move."""
    moves(
        ctx,
        name_or_id=name_or_id,
        no_cache=no_cache,
        format=format,
        move=move_name,
        method=method,
    )


@app.command()
def evo(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Quick shortcut for evolution lookups."""
    evolution(ctx, name_or_id=name_or_id, no_cache=no_cache, format=format)


@app.command()
def forms(
    ctx: typer.Context,
    name_or_id: str = typer.Argument(..., help=POKEMON_NAME_OR_ID),
    no_cache: bool = typer.Option(False, "--no-cache", help=NO_CACHE),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Show a species' varieties, like Mega, Alolan, or Gigantamax forms."""
    client = ctx.obj["client"]
    species_data = fetch_resource(
        client, "pokemon-species", name_or_id, no_cache, err_console
    )
    species_name = species_data["name"]
    varieties = species_data.get("varieties", [])

    # Find first non-default variety for hints
    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    first_variety = None
    for v in varieties:
        if not v.get("is_default", True):
            first_variety = v.get("pokemon", {}).get("name")
            break
    hints = get_hints("pokemon.forms", {"name": species_name, "first_variety": first_variety})

    if format == "json":
        render_json({"species": species_name, "varieties": varieties}, console)
        return

    if format == "toon":
        from pokecli.display.toon import toon_list, toon_kv, print_toon
        if not varieties:
            print_toon(toon_kv([
                ("species", species_name),
                ("count", "0"),
                ("result", "No varieties recorded"),
            ]))
        else:
            header = toon_kv([("species", species_name)])
            schema_fields = ["name", "is_default"]
            rows = [
                [v.get("pokemon", {}).get("name", "-"), str(v.get("is_default", False)).lower()]
                for v in varieties
            ]
            body = toon_list("varieties", schema_fields, rows)
            print_toon(header + "\n" + body)
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
        return

    render_pokemon_varieties(species_name, varieties, console)
    if hints:
        console.print(format_hints_table(hints))


@app.command(name="list")
def list_pokemon(
    ctx: typer.Context,
    limit: int = typer.Option(DEFAULT_LIMIT, "--limit", help=LIMIT),
    offset: int = typer.Option(DEFAULT_OFFSET, "--offset", help=OFFSET),
    format: str = typer.Option("table", "--format", help=FORMAT),
) -> None:
    """Browse Pokemon with pagination."""
    client = ctx.obj["client"]
    result = fetch_list(client, "pokemon", limit, offset, err_console)
    from pokecli.display.hints import get_hints, format_hints_toon, format_hints_table
    first_name = result.results[0].name if result.results else None
    hints = get_hints("pokemon.list", {"resource": "pokemon", "first_name": first_name})
    if format == "toon":
        from pokecli.display.toon import toon_list, print_toon
        from pokecli.display.toon_schemas import resource_list_toon
        schema_fields, rows = resource_list_toon(result)
        print_toon(toon_list("pokemon", schema_fields, rows, total=result.count))
        hint_text = format_hints_toon(hints)
        if hint_text:
            print_toon("\n" + hint_text)
    else:
        render_list(result, console)
        if hints:
            console.print(format_hints_table(hints))


app.add_typer(pokemon_form.app, name="form")
app.add_typer(evolution_chain.app, name="evolution-chain")
