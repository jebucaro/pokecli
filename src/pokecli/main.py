import importlib.metadata
import shutil
import sys
from pathlib import Path

import toons
import typer
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pokecli.api.client import PokeAPIClient
from pokecli.cache.store import CacheStore
from pokecli.commands import cache, install, resource_cmds, sprite, tasks
from pokecli.commands._format import resolve_format
from pokecli.commands._resource_help import ResourceHelpCommand
from pokecli.display.common import get_chars
from pokecli.display.toon import print_toon

DESCRIPTION = "Look up Pokemon data, moves, locations, and game info from the terminal."

#: Quick-start commands paired with the question each one answers. The commands
#: feed the help epilog and the orientation view; the pairing is what makes the
#: terminal view readable rather than a bare list.
QUICK_START_EXAMPLES: tuple[tuple[str, str], ...] = (
    ("pokecli get pokemon pikachu", "Stats, types, and abilities"),
    ("pokecli moves pikachu", "Every move it can learn"),
    ("pokecli can-learn charizard fly", "Yes or no, as an exit code"),
    ("pokecli search item ball", "Find a name you half-remember"),
    ("pokecli evolution eevee", "The full chain, from any member"),
)

QUICK_START: tuple[str, ...] = tuple(cmd for cmd, _ in QUICK_START_EXAMPLES)


def _version() -> str:
    try:
        return importlib.metadata.version("pokecli")
    except importlib.metadata.PackageNotFoundError:
        return "dev"


app = typer.Typer(
    name="pokecli",
    help=DESCRIPTION,
    invoke_without_command=True,
    epilog="Examples:\n" + "\n".join(f"  {line}" for line in QUICK_START),
)


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context) -> None:
    ctx.ensure_object(dict)
    ctx.obj["client"] = ctx.with_resource(PokeAPIClient())

    if ctx.invoked_subcommand is None:
        _show_home_view()


def _bin_path() -> str:
    path = shutil.which("pokecli") or sys.argv[0]
    home = str(Path.home())
    if path.startswith(home):
        path = "~" + path[len(home):]
    return path


def _cache_counts() -> dict[str, int] | None:
    """Cached entry counts, or None when the cache cannot be read."""
    try:
        with CacheStore() as cache_store:
            return cache_store.stats()
    except Exception:
        return None


def _show_home_view() -> None:
    """Print the orientation view, following the context-dependent default.

    Takes no ``--format`` option: a root-level option would be ambiguous with
    the same option on a subcommand.
    """
    if resolve_format(None) == "table":
        _show_home_view_table()
    else:
        _show_home_view_toon()


def _show_home_view_toon() -> None:
    counts = _cache_counts() or {}
    non_empty = [
        {"resource": k, "entries": v}
        for k, v in sorted(counts.items(), key=lambda x: -x[1])
        if v > 0
    ]
    payload: dict = {
        "pokecli": {
            "version": _version(),
            "bin": _bin_path(),
            "description": DESCRIPTION,
            "cache_entries": sum(counts.values()),
        }
    }
    if non_empty:
        payload["cached"] = non_empty
    payload["quick_start"] = list(QUICK_START)
    print_toon(toons.dumps(payload))


def _indented(renderable) -> Padding:
    """Indent a renderable by two spaces, matching the section labels."""
    return Padding(renderable, (0, 0, 0, 2))


def _show_home_view_table() -> None:
    console = Console()
    chars = get_chars(console)

    title = Text()
    title.append("pokecli ", style="bold white")
    title.append(_version(), style="bold cyan")
    console.print(Panel(title, expand=False, border_style="bright_black"))

    console.print(f"[dim]{DESCRIPTION}[/dim]")
    console.print(f"[dim]bin: {_bin_path()}[/dim]\n")

    counts = _cache_counts()
    if counts is not None:
        total = sum(counts.values())
        non_empty = sorted(
            ((k, v) for k, v in counts.items() if v > 0), key=lambda x: -x[1]
        )
        if non_empty:
            console.print(f"[bold]Cache[/bold] [dim]{chars.dash} {total} entries[/dim]")
            cache_table = Table(show_header=False, box=None, padding=(0, 2), pad_edge=False)
            cache_table.add_column("Resource", style="cyan", no_wrap=True)
            cache_table.add_column("Entries", justify="right", style="bold")
            for resource, count in non_empty[:5]:
                cache_table.add_row(resource, str(count))
            console.print(_indented(cache_table))
            if len(non_empty) > 5:
                console.print(
                    f"  [dim]+{len(non_empty) - 5} more resources cached[/dim]"
                )
        else:
            console.print(f"[bold]Cache[/bold] [dim]{chars.dash} empty[/dim]")
            console.print("  [dim]fetched from PokeAPI on first use[/dim]")
        console.print()

    console.print("[bold]Quick start[/bold]")
    quick_table = Table(show_header=False, box=None, padding=(0, 2), pad_edge=False)
    quick_table.add_column("Command", style="bold green", no_wrap=True)
    quick_table.add_column("Answers", style="dim")
    for command, purpose in QUICK_START_EXAMPLES:
        quick_table.add_row(command, purpose)
    console.print(_indented(quick_table))
    console.print()

    footer = Table(show_header=False, box=None, padding=(0, 1), pad_edge=False)
    footer.add_column("", style="dim", no_wrap=True)
    footer.add_column("Command", style="dim", no_wrap=True)
    footer.add_column("Purpose", style="dim")
    footer.add_row(chars.arrow_r, "pokecli get --help", "every resource you can query")
    footer.add_row(chars.arrow_r, "pokecli --help", "the full command reference")
    console.print(_indented(footer))


# Resource plane: one command shape for all eighteen resources. Each one's
# `--help` ends with the Resources panel, answering "which resources?".
app.command("get", cls=ResourceHelpCommand)(resource_cmds.get)
app.command("list", cls=ResourceHelpCommand)(resource_cmds.list_resources)
app.command("search", cls=ResourceHelpCommand)(resource_cmds.search)

# Derived commands: joins, filters, and side effects.
app.command("moves")(tasks.moves)
app.command("can-learn")(tasks.can_learn)
app.command("evolution")(tasks.evolution)
app.command("encounters")(tasks.encounters)
app.command("forms")(tasks.forms)
app.command("sprite")(sprite.sprite)

# Meta.
app.add_typer(cache.app, name="cache")
app.add_typer(install.app, name="install")
