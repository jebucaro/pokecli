"""Resolve `--game` into the version groups and versions it covers.

PokeAPI keys learnsets by version group (``red-blue``) and encounters by
version (``red``). Users name either, so both resolve to one scope.
"""

from dataclasses import dataclass

import typer

from pokecli.config import VERSION_GROUP_VERSIONS

_GROUP_OF_VERSION = {
    version: group
    for group, versions in VERSION_GROUP_VERSIONS.items()
    for version in versions
}


@dataclass(frozen=True)
class GameScope:
    name: str
    version_groups: frozenset[str]
    versions: frozenset[str]


def _valid_names() -> list[str]:
    groups = list(VERSION_GROUP_VERSIONS)
    return groups + [v for v in _GROUP_OF_VERSION if v not in VERSION_GROUP_VERSIONS]


def validate_game(value: str | None) -> str | None:
    """Reject an unknown ``--game`` as a usage error (exit 2), naming the valid ones.

    Like ``--method``: for ``can-learn`` exit 1 means "no", so a typo must not
    reach the check.
    """
    if value is None:
        return None
    name = value.strip().lower().replace(" ", "-")
    if name not in VERSION_GROUP_VERSIONS and name not in _GROUP_OF_VERSION:
        raise typer.BadParameter(
            f"'{value}' is not a known game. "
            f"Choose a version group or version: {', '.join(_valid_names())}"
        )
    return name


def resolve_game(name: str) -> GameScope:
    """Scope for a validated game name."""
    if name in VERSION_GROUP_VERSIONS:
        return GameScope(
            name=name,
            version_groups=frozenset({name}),
            versions=frozenset(VERSION_GROUP_VERSIONS[name]),
        )
    return GameScope(
        name=name,
        version_groups=frozenset({_GROUP_OF_VERSION[name]}),
        versions=frozenset({name}),
    )
