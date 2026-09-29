import importlib.resources
import os
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console

from pokecli.display.common import uses_unicode

app = typer.Typer(help="Install pokecli agent skills.")
console = Console()
err_console = Console(stderr=True)

REFERENCE_FILES = ("api-fields.md", "workflows.md")

# Kiro documents only these frontmatter fields; Claude Code-only fields such as
# `allowed-tools` and `user-invocable` are dropped from the Kiro copy.
KIRO_FRONTMATTER_KEYS = frozenset({"name", "description"})


class Agent(str, Enum):
    claude = "claude"
    kiro = "kiro"


# Dot-directory holding each agent's config, both under home and in a workspace.
AGENT_DIRS = {Agent.claude: ".claude", Agent.kiro: ".kiro"}


def global_root(agent: Agent) -> Path:
    """The agent's user-level config root, honoring KIRO_HOME like Kiro does."""
    if agent is Agent.kiro:
        kiro_home = os.environ.get("KIRO_HOME")
        if kiro_home:
            return Path(kiro_home)
    return Path.home() / AGENT_DIRS[agent]


def skill_destination(agent: Agent, local: bool) -> Path:
    root = Path.cwd() / AGENT_DIRS[agent] if local else global_root(agent)
    return root / "skills" / "pokecli"


def skill_text_for(agent: Agent, text: str) -> str:
    """Packaged SKILL.md adapted to the frontmatter fields the agent documents."""
    if agent is Agent.claude:
        return text
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    end = next(
        (i for i in range(1, len(lines)) if lines[i].strip() == "---"), None
    )
    if end is None:
        return text
    kept = [
        line
        for line in lines[1:end]
        if line.split(":", 1)[0].strip() in KIRO_FRONTMATTER_KEYS
    ]
    return "".join([lines[0], *kept, *lines[end:]])


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
        help="Install into the current directory's workspace skills (./.claude/ or ./.kiro/) instead of the home directory.",
    ),
    agent: Agent = typer.Option(
        Agent.claude,
        "--agent",
        case_sensitive=False,
        help="Agent to install for: claude (~/.claude/skills/) or kiro (~/.kiro/skills/, or $KIRO_HOME/skills/).",
    ),
) -> None:
    """Install pokecli agent skills."""
    if not skills:
        console.print(ctx.get_help())
        raise typer.Exit()

    dest_dir = skill_destination(agent, local)
    dest_dir.mkdir(parents=True, exist_ok=True)

    skill_pkg = importlib.resources.files("pokecli.skills.pokecli")

    skill_md = skill_pkg.joinpath("SKILL.md").read_text(encoding="utf-8")
    (dest_dir / "SKILL.md").write_text(skill_text_for(agent, skill_md), encoding="utf-8")

    refs_dir = dest_dir / "references"
    refs_dir.mkdir(exist_ok=True)
    for ref_name in REFERENCE_FILES:
        content = (
            skill_pkg.joinpath("references")
            .joinpath(ref_name)
            .read_text(encoding="utf-8")
        )
        (refs_dir / ref_name).write_text(content, encoding="utf-8")

    marker = "✓" if uses_unicode(console) else "[OK]"
    console.print(f"[green]{marker} Skills installed to {dest_dir}[/green]")
