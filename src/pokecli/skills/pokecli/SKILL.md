---
name: pokecli
description: Queries Pokemon, moves, items, abilities, types, locations, game data, forms, machines, encounters, evolutions, and other PokeAPI-backed resources via the pokecli CLI. Use when the user needs Pokemon stats, move info, type matchups, catch locations, evolution chains, sprite downloads, regional or generation data, or cache management. Also use when the user mentions pokecli, pokedex, or PokeAPI.
allowed-tools: Bash(pokecli:*)
user-invocable: false
---

# Pokemon Data Lookup With pokecli

## The whole grammar

Three patterns cover every resource:

```bash
pokecli get <resource> <name_or_id>     # one record
pokecli list <resource>                 # browse, paginated
pokecli search <resource> <query>       # find a name
```

Plus six commands that answer a question rather than return a record:

```bash
pokecli moves <pokemon>                 # every learnable move
pokecli can-learn <pokemon> <move>      # exit 0 = yes, exit 1 = no
pokecli evolution <pokemon>             # full chain, from any member
pokecli encounters <pokemon>            # where it appears in the wild
pokecli forms <pokemon>                 # Mega, Alolan, Gigantamax varieties
pokecli sprite <pokemon> -o <path>      # download an image
```

There is exactly one command path per behavior. No aliases, no nested groups.

## Options

This is every option pokecli accepts, so there's no need to read help output.

| Option | Accepted by | Values |
|--------|-------------|--------|
| `--format` | every command that returns data | omit it; pass `json` only to compute over results (see below) |
| `--no-cache` | `get`, `search`, and the six task commands | fetch fresh instead of reading the cache |
| `--limit`, `--offset` | `list` | page size (default 20) and start index (default 0) |
| `--method` | `moves`, `can-learn` | `level-up`, `machine`, `tutor`, `egg`, or a game-specific method: `stadium-surfing-pikachu`, `light-ball-egg`, `colosseum-purification`, `xd-shadow`, `xd-purification`, `form-change`, `zygarde-cube`, `train`. Case-insensitive. Any other value exits 2 |
| `--game` | `moves`, `can-learn`, `encounters` | a game (`red`, `sword`) or pair (`red-blue`). DLC has its own names (`the-isle-of-armor-sword`). Any other value exits 2 and lists valid names |
| `-o`, `--output` | `sprite` (required) | file path to write |
| `--variant` | `sprite` | `front_default` (default), `front_shiny`, `back_default`, `back_shiny`, `front_female`, `front_shiny_female` |
| `--resource` | `cache clear` | one resource name, to clear only that table |
| `--skills`, `--local`, `--agent` | `install` | installs this skill; not needed for queries |
When the user names a game, pass `--game`. Without it, results merge every game
and each move shows the newest game's method.

## Output format

Omit `--format`. Captured output is already TOON, which is compact and readable.
Narrow with `search`, `--method`, or `--limit` before reaching for a parser.

Add `--format json` only to count, sum, sort, or filter more rows than you can
reliably read. Parse with `python3` (not `python`); use `jq` only after
`command -v jq` succeeds.

```bash
pokecli moves cubone --method level-up --format json | python3 -c 'import json,sys; d=json.load(sys.stdin); print([(m["name"], m["level"]) for m in d["moves"] if m["level"] <= 10])'
```

Before filtering on a field, check what it holds on rows it doesn't apply to.
For example, a move not learned by level-up has `level: 0`, so a `level <= 10`
filter matches it unless you narrow with `--method level-up` first.

## The 18 resources

Every `get`, `list`, and `search` takes one of these names. Use this table
rather than `--help`. If pokecli rejects a name, its error lists the accepted
names; trust that over this table.

| Resource | Purpose |
|----------|---------|
| `pokemon` | Stats, types, abilities, and sprites for a single Pokemon |
| `pokemon-species` | Pokedex text, egg groups, capture rate, and growth rate |
| `pokemon-form` | A specific variant such as a Mega, Alolan, or Gigantamax form |
| `evolution-chain` | A full evolution chain addressed by its numeric chain ID |
| `move` | Power, accuracy, PP, type, and damage class of a move |
| `item` | Cost, effect, and flavor text of a held or usable item |
| `ability` | What an ability does and which Pokemon have it |
| `type` | Damage relations - strengths, weaknesses, and immunities |
| `nature` | Which stat a nature raises and which it lowers |
| `berry` | Growth time, size, flavors, and natural gift data |
| `location` | A named place and the encounter areas inside it |
| `location-area` | An encounter area and the Pokemon found there |
| `region` | A region such as kanto, with its locations and pokedexes |
| `generation` | A generation and the species, moves, and types it introduced |
| `version` | A single game release such as red or sword |
| `version-group` | A paired release such as red-blue or sword-shield |
| `pokedex` | A regional or national pokedex and its species entries |
| `machine` | A TM or HM record - which move it teaches, in which games |

## Reading the default output

This is what you get with no `--format` (TOON):

- A single record is `label:` followed by indented `key: value` pairs
- A collection is `label[count]{fields}:` followed by indented rows
- Aggregates like `count`, `total_moves`, `methods` appear as top-level keys
- Every response ends with `help[]` hints naming valid follow-up commands
- `list` and `search` start with `count: N of TOTAL total`. When `N` is less
  than `TOTAL`, page with `--offset`, or better, narrow the results with `search`

## Decision table

| User intent | Command |
|-------------|---------|
| Pokemon stats, types, abilities | `pokecli get pokemon <name>` |
| Pokedex text, egg groups, capture rate | `pokecli get pokemon-species <name>` |
| Moves a Pokemon can learn | `pokecli moves <name>` |
| Can this Pokemon learn move X? | `pokecli can-learn <name> <move>` |
| Can it learn move X in game Z? | `pokecli can-learn <name> <move> --game <game>` |
| Full evolution chain | `pokecli evolution <name>` (every branch; conditions like gender are not exposed, so don't re-query `get evolution-chain`) |
| Where can I catch this Pokemon? | `pokecli encounters <name>` |
| All varieties for a species | `pokecli forms <name>` |
| Inspect one alternate form | `pokecli get pokemon-form <form-name>` |
| Download a sprite | `pokecli sprite <name> -o <path>` |
| Anything else about one named thing | `pokecli get <resource> <name>` |
| I know part of the name only | `pokecli search <resource> <query>` |

## Examples

```bash
pokecli get pokemon pikachu
pokecli get move thunderbolt
pokecli get ability intimidate
pokecli get type fire
pokecli get region kanto
pokecli get location pallet-town
pokecli get location-area kanto-route-1-area
pokecli get machine 79
pokecli get version-group red-blue
pokecli get evolution-chain 2

pokecli list type
pokecli list region
pokecli list pokemon --limit 50 --offset 100

pokecli search item ball
pokecli search move thunder
pokecli search pokemon char
```

## Names

Identifiers are case-insensitive and spaces become hyphens, so
`pokecli get item "master ball"` and `pokecli get item master-ball` are the same
request. Numeric IDs work wherever a name does.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success. For `can-learn`, also means yes |
| 1 | Not found, unreachable API, invalid `--variant`, or `can-learn` answering no |
| 2 | Invalid invocation (unknown command, resource, option, `--method`, or `--game`), or a response that did not match the expected shape |

On exit 2, read stderr. For an invalid resource it names every accepted value.
Fix the invocation and retry; don't retry it unchanged.

`can-learn` is the only command whose exit code carries an answer rather than an
error, so branch on it directly:

```bash
if pokecli can-learn charizard fly; then echo "yes"; fi
```

## Caching

Responses are cached locally after the first request. Pass `--no-cache` to force
a fresh fetch (not available on `list`). Inspect or clear with:

```bash
pokecli cache stats
pokecli cache clear
pokecli cache clear --resource pokemon
```

`search` caches a name index per resource, so the first search for a resource
costs one request and later searches cost none.

## Multi-step workflows

For recipes that span commands, read `references/workflows.md`.

## Field details

For response field explanations, read `references/api-fields.md`.
