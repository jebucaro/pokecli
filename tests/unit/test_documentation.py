"""Documentation must name only commands that exist.

`README.md` documented `pokecli nature <name>` and `pokecli berry <name>` for
months while both errored, because nothing checked prose against the command
tree. This module is that check. It covers the user-facing README and the
packaged agent skill, which is the surface an agent actually reads.
"""

import re
from pathlib import Path

import pytest
import typer.main

from pokecli.main import app
from pokecli.resources import RESOURCE_NAMES, RESOURCES

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "src" / "pokecli" / "skills" / "pokecli"

DOC_FILES = [
    REPO_ROOT / "README.md",
    SKILL_DIR / "SKILL.md",
    SKILL_DIR / "references" / "workflows.md",
    SKILL_DIR / "references" / "api-fields.md",
]

# The README's migration table intentionally quotes the old paths in its "Before"
# column, so that section is excluded from validation.
EXCLUDED_SECTIONS = ("## Breaking Changes",)

REMOVED_FIRST_ARGS = {
    "pokemon",
    "move",
    "item",
    "ability",
    "type",
    "nature",
    "berry",
    "location",
    "game",
    "image",
    "region",
    "generation",
    "pokedex",
    "version",
    "version-group",
    "machine",
    "location-area",
    "pokemon-form",
    "evolution-chain",
}

# Placeholders documentation uses in place of a concrete value.
PLACEHOLDER = re.compile(r"^<.*>$|^\$?\{.*\}$")

VALID_TARGETS = set(RESOURCE_NAMES)


def _strip_excluded(text: str) -> str:
    """Drop sections that intentionally quote superseded commands."""
    lines = text.splitlines()
    kept: list[str] = []
    skipping = False
    for line in lines:
        if line.startswith("## "):
            skipping = any(line.startswith(s) for s in EXCLUDED_SECTIONS)
        if not skipping:
            kept.append(line)
    return "\n".join(kept)


def _extract_invocations(path: Path) -> list[str]:
    """Every `pokecli ...` invocation in fenced blocks and inline code."""
    text = _strip_excluded(path.read_text(encoding="utf-8"))
    found: list[str] = []

    # Fenced code blocks: shell lines starting with pokecli, optionally prompted.
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        stripped = line.strip()
        if stripped.startswith("$ "):
            stripped = stripped[2:].strip()
        if stripped.startswith("pokecli "):
            found.append(stripped)

    # Inline code spans anywhere in the prose or tables.
    for span in re.findall(r"`([^`]+)`", text):
        span = span.strip()
        if span.startswith("pokecli "):
            found.append(span)

    return found


def _tokenize(invocation: str) -> list[str]:
    """Split an invocation, dropping pipes, redirects, comments, and quoting.

    Splits only on whitespace-delimited `|` and `>` so the `>` closing a
    `<placeholder>` is not mistaken for a redirect.
    """
    head = re.split(r"\s\|\s|\s>", invocation)[0]
    head = head.split(" #")[0]
    tokens = re.findall(r'"[^"]*"|\S+', head)
    return [t.strip('"') for t in tokens]


ALL_INVOCATIONS = [
    (path.name, invocation)
    for path in DOC_FILES
    for invocation in _extract_invocations(path)
]


def test_documentation_files_all_exist():
    for path in DOC_FILES:
        assert path.is_file(), path


def test_invocations_were_actually_extracted():
    assert len(ALL_INVOCATIONS) > 50


@pytest.mark.parametrize(
    ("doc", "invocation"), ALL_INVOCATIONS, ids=lambda v: str(v)[:70]
)
def test_documented_command_is_registered(doc, invocation):
    registered = typer.main.get_command(app).commands
    tokens = _tokenize(invocation)
    assert tokens[0] == "pokecli", invocation

    if len(tokens) < 2:
        return  # bare `pokecli`, the orientation view

    command = tokens[1]
    if command.startswith("-"):
        return  # `pokecli --help`

    assert command in registered, f"{doc}: '{command}' is not a registered command"


@pytest.mark.parametrize(
    ("doc", "invocation"), ALL_INVOCATIONS, ids=lambda v: str(v)[:70]
)
def test_documented_resource_is_valid(doc, invocation):
    tokens = _tokenize(invocation)
    if len(tokens) < 3 or tokens[1] not in {"get", "list", "search"}:
        return

    target = tokens[2]
    if PLACEHOLDER.match(target):
        return

    assert target in VALID_TARGETS, f"{doc}: '{target}' is not a valid resource"


@pytest.mark.parametrize(
    ("doc", "invocation"), ALL_INVOCATIONS, ids=lambda v: str(v)[:70]
)
def test_no_documented_command_uses_a_removed_path(doc, invocation):
    tokens = _tokenize(invocation)
    if len(tokens) < 2 or tokens[1].startswith("-"):
        return
    assert tokens[1] not in REMOVED_FIRST_ARGS, (
        f"{doc}: '{invocation}' uses a removed addressing scheme"
    )


def test_readme_does_not_claim_the_stale_bare_aliases():
    """These two were documented but never worked; they must not return."""
    readme = _strip_excluded((REPO_ROOT / "README.md").read_text(encoding="utf-8"))
    assert "pokecli nature modest" not in readme
    assert "pokecli berry oran" not in readme


def test_skill_does_not_instruct_a_format_flag_per_call():
    """The non-interactive default replaced that instruction."""
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "always pass `--format toon`" not in skill.lower()
    assert "always use `--format toon`" not in skill.lower()


def test_skill_documents_the_resource_vocabulary():
    """The skill's resource table must equal the code's table: names, purposes, order.

    Agents choose a resource from this table instead of calling the CLI, so a
    missing or reworded row is a silent behavior change for them.
    """
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    heading = "## The 18 resources"
    assert heading in skill, f"SKILL.md has no '{heading}' section"
    section = skill.split(heading, 1)[1].split("\n## ", 1)[0]

    documented = re.findall(r"^\| `([a-z-]+)` \| (.+?) \|$", section, re.MULTILINE)
    expected = [(r.name, r.purpose) for r in RESOURCES]

    expected_table = "\n".join(f"| `{n}` | {p} |" for n, p in expected)
    assert documented == expected, (
        f"SKILL.md '{heading}' is out of sync with pokecli.resources. "
        f"Expected rows:\n{expected_table}"
    )


def _cli_option_flags() -> set[str]:
    """Every option flag on every command, walking into groups like `cache`."""
    flags: set[str] = set()
    pending = [typer.main.get_command(app)]
    while pending:
        command = pending.pop()
        pending.extend(getattr(command, "commands", {}).values())
        for param in command.params:
            if param.param_type_name == "option":
                flags.update(param.opts)
    flags.discard("--help")
    # Typer's shell-completion setup flags; not part of pokecli's surface.
    flags -= {"--install-completion", "--show-completion"}
    return flags


def test_skill_options_table_covers_every_cli_option():
    """The skill tells agents not to read `--help`, so it must name every option."""
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    section = skill.split("## Options", 1)[1].split("\n## ", 1)[0]
    documented = set(re.findall(r"`(--?[a-z][a-z-]*)`", section))

    missing = _cli_option_flags() - documented
    assert not missing, f"SKILL.md '## Options' omits: {sorted(missing)}"
    stale = documented - _cli_option_flags()
    assert not stale, f"SKILL.md '## Options' names options that no longer exist: {sorted(stale)}"


def test_skill_options_table_lists_every_learn_method():
    from pokecli.config import LEARN_METHODS

    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    method_row = next(
        line for line in skill.splitlines() if line.startswith("| `--method` |")
    )
    missing = [m for m in LEARN_METHODS if f"`{m}`" not in method_row]
    assert not missing, f"SKILL.md '--method' row omits: {missing}"


def test_readme_and_skill_agree_on_exit_codes():
    def exit_rows(text: str) -> list[str]:
        return re.findall(r"^\| [012] \|.*$", text, re.MULTILINE)

    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert len(exit_rows(readme)) == 3
    assert exit_rows(readme) == exit_rows(skill)


def test_readme_documents_the_resource_vocabulary():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    for name in RESOURCE_NAMES:
        assert name in readme, f"README.md omits resource '{name}'"


def test_readme_documents_the_context_dependent_format_default():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "interactive terminal" in readme
    assert "toon" in readme


def test_skill_options_table_ends_before_following_prose():
    """A line right after a table without a blank line renders as a table row."""
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    section = skill.split("## Options", 1)[1].split("\n## ", 1)[0]
    lines = section.splitlines()
    last_row = max(i for i, line in enumerate(lines) if line.startswith("|"))
    assert last_row + 1 == len(lines) or lines[last_row + 1].strip() == ""
