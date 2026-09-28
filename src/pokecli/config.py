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
