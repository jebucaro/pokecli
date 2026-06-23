import importlib.resources
from pathlib import Path

import typer
from rich.console import Console

from pokecli.display.common import uses_unicode

app = typer.Typer(help="Install pokecli agent skills.")
console = Console()
err_console = Console(stderr=True)


@app.callback(invoke_without_command=True)
def install(
    ctx: typer.Context,
    skills: bool = typer.Option(
        False,
        "--skills",
        help="Install the packaged pokecli skill files, use --local to target the current directory.",
    ),
    local: bool = typer.Option(
        False,
        "--local",
        help="Install under .claude/skills/pokecli/ in the current directory.",
    ),
) -> None:
    """Install pokecli agent skills."""
    if not skills:
        console.print(ctx.get_help())
        raise typer.Exit()

    base = Path.cwd() if local else Path.home()
    dest_dir = base / ".claude" / "skills" / "pokecli"
    dest_dir.mkdir(parents=True, exist_ok=True)

    skill_pkg = importlib.resources.files("pokecli.skills.pokecli")

    skill_md = skill_pkg.joinpath("SKILL.md").read_text(encoding="utf-8")
    (dest_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    refs_dir = dest_dir / "references"
    refs_dir.mkdir(exist_ok=True)
    for ref_name in ("api-fields.md", "workflows.md"):
        content = (
            skill_pkg.joinpath("references")
            .joinpath(ref_name)
            .read_text(encoding="utf-8")
        )
        (refs_dir / ref_name).write_text(content, encoding="utf-8")

    marker = "✓" if uses_unicode(console) else "[OK]"
    console.print(f"[green]{marker} Skills installed to {dest_dir}[/green]")
