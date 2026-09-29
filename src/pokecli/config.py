POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
DEFAULT_LIMIT = 20
DEFAULT_OFFSET = 0
CACHE_DB_PATH = "~/.pokecli/cache.json"

#: PokeAPI's `move-learn-method` vocabulary, the accepted `--method` values.
#: The four common methods come first; the rest are game-specific.
LEARN_METHODS: tuple[str, ...] = (
    "level-up",
    "machine",
    "tutor",
    "egg",
    "stadium-surfing-pikachu",
    "light-ball-egg",
    "colosseum-purification",
    "xd-shadow",
    "xd-purification",
    "form-change",
    "zygarde-cube",
    "train",
)

#: PokeAPI version groups in release order (their ``order`` field). Numeric IDs
#: are not chronological: ``red-green-japan`` and ``blue-japan`` (Gen I) were
#: added as IDs 28 and 29, after ``scarlet-violet`` (25). Ranking by ID made Gen I
#: Japanese data look like the newest games.
VERSION_GROUP_ORDER: tuple[str, ...] = (
    "red-green-japan",
    "blue-japan",
    "red-blue",
    "yellow",
    "gold-silver",
    "crystal",
    "ruby-sapphire",
    "emerald",
    "colosseum",
    "xd",
    "firered-leafgreen",
    "diamond-pearl",
    "platinum",
    "heartgold-soulsilver",
    "black-white",
    "black-2-white-2",
    "x-y",
    "omega-ruby-alpha-sapphire",
    "sun-moon",
    "ultra-sun-ultra-moon",
    "lets-go-pikachu-lets-go-eevee",
    "sword-shield",
    "the-isle-of-armor",
    "the-crown-tundra",
    "brilliant-diamond-shining-pearl",
    "legends-arceus",
    "scarlet-violet",
    "the-teal-mask",
    "the-indigo-disk",
    "legends-za",
    "mega-dimension",
    "champions",
)

#: Each version group's versions, from PokeAPI's `version-group` resources.
#: Learnsets are keyed by group, encounters by version, so `--game` needs both
#: directions. DLC groups have their own versions (`the-isle-of-armor-sword`),
#: so every version belongs to exactly one group. Keep in step with
#: ``VERSION_GROUP_ORDER`` when PokeAPI adds a game.
VERSION_GROUP_VERSIONS: dict[str, tuple[str, ...]] = {
    "red-green-japan": ("red-japan", "green-japan"),
    "blue-japan": ("blue-japan",),
    "red-blue": ("red", "blue"),
    "yellow": ("yellow",),
    "gold-silver": ("gold", "silver"),
    "crystal": ("crystal",),
    "ruby-sapphire": ("ruby", "sapphire"),
    "emerald": ("emerald",),
    "colosseum": ("colosseum",),
    "xd": ("xd",),
    "firered-leafgreen": ("firered", "leafgreen"),
    "diamond-pearl": ("diamond", "pearl"),
    "platinum": ("platinum",),
    "heartgold-soulsilver": ("heartgold", "soulsilver"),
    "black-white": ("black", "white"),
    "black-2-white-2": ("black-2", "white-2"),
    "x-y": ("x", "y"),
    "omega-ruby-alpha-sapphire": ("omega-ruby", "alpha-sapphire"),
    "sun-moon": ("sun", "moon"),
    "ultra-sun-ultra-moon": ("ultra-sun", "ultra-moon"),
    "lets-go-pikachu-lets-go-eevee": ("lets-go-pikachu", "lets-go-eevee"),
    "sword-shield": ("sword", "shield"),
    "the-isle-of-armor": ("the-isle-of-armor-sword", "the-isle-of-armor-shield"),
    "the-crown-tundra": ("the-crown-tundra-sword", "the-crown-tundra-shield"),
    "brilliant-diamond-shining-pearl": ("brilliant-diamond", "shining-pearl"),
    "legends-arceus": ("legends-arceus",),
    "scarlet-violet": ("scarlet", "violet"),
    "the-teal-mask": ("the-teal-mask-scarlet", "the-teal-mask-violet"),
    "the-indigo-disk": ("the-indigo-disk-scarlet", "the-indigo-disk-violet"),
    "legends-za": ("legends-za",),
    "mega-dimension": ("mega-dimension",),
    "champions": ("champions",),
}

#: DLC version groups and the base game they extend. PokeAPI records DLC
#: encounters under the DLC's own versions but its learnsets under the base
#: group, so a DLC `--game` must also search the base group's moves.
DLC_BASE_GROUP: dict[str, str] = {
    "the-isle-of-armor": "sword-shield",
    "the-crown-tundra": "sword-shield",
    "the-teal-mask": "scarlet-violet",
    "the-indigo-disk": "scarlet-violet",
    "mega-dimension": "legends-za",
}
