import importlib.resources
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Install pokecli integrations.")
console = Console()
err_console = Console(stderr=True)


@app.callback(invoke_without_command=True)
def install(
    ctx: typer.Context,
    skills: bool = typer.Option(
        False,
        "--skills",
        help="Install Claude Code skills (use --local to target the current directory).",
    ),
    local: bool = typer.Option(
        False,
        "--local",
        help="Install to .claude/skills/pokecli/ relative to the current directory.",
    ),
) -> None:
    """Install pokecli integrations."""
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
    api_fields = (
        skill_pkg.joinpath("references")
        .joinpath("api-fields.md")
        .read_text(encoding="utf-8")
    )
    (refs_dir / "api-fields.md").write_text(api_fields, encoding="utf-8")

    console.print(f"[green]✓ Skills installed to {dest_dir}[/green]")
