"""Shared help strings.

One constant per argument or option, so the same wording appears wherever an
argument does.
"""

from pokecli.config import LEARN_METHODS

RESOURCE = "Resource type (see Resources below)"
NAME_OR_ID = "Name or ID to look up"
SEARCH_QUERY = "Substring to match against resource names"
POKEMON_NAME_OR_ID = "Pokemon name or Pokedex number"
MOVE_NAME = "Move name to check"

NO_CACHE = "Fetch fresh data instead of using the local cache"
FORMAT = "Output format: table, toon, or json. Defaults to table in a terminal, toon otherwise"
LIMIT = "Number of results to show"
OFFSET = "Number of results to skip"
METHOD_FILTER = f"Only include this learn method: {', '.join(LEARN_METHODS)}"
GAME_FILTER = (
    "Only include data from this game: a version (red, sword) or "
    "version group (red-blue, sword-shield)"
)
OUTPUT_PATH = "Where to save the downloaded image"
SPRITE_VARIANT = (
    "Sprite variant: front_default, front_shiny, back_default, back_shiny, "
    "front_female, front_shiny_female"
)
