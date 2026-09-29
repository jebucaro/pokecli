# pokecli

`pokecli` is a command line interface for looking up Pokemon data from [PokeAPI](https://pokeapi.co/api/v2). It covers Pokemon, moves, items, abilities, locations, game data, forms, machines, and other reference resources.

The command surface is deliberately small: two patterns cover every resource, and six commands cover the questions that span more than one request. Output adapts to who is asking — rich tables in a terminal, compact token-optimized TOON when piped.

Running `pokecli` with no arguments shows cache status and quick-start examples, rendered to suit whoever is asking like any other output.

## Features

- One command shape for all 18 resources: `get`, `list`, `search`
- Six task commands for questions a single resource read cannot answer
- `search` for finding a name without paging thousands of results
- Format that follows context: tables for humans, TOON for pipes and agents
- Contextual `help[]` hints suggesting valid next commands
- Local cache to cut down on repeated API calls

## Requirements

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) recommended, or pip

## Installation

Using `uv`:

```bash
git clone https://github.com/jebucaro/PokeCli
cd pokecli
uv sync
uv run pokecli --help
```

Using `pip`:

```bash
git clone https://github.com/jebucaro/PokeCli
cd pokecli
pip install -e .
pokecli --help
```

## Quick Start

```bash
pokecli get pokemon pikachu
pokecli moves pikachu
pokecli can-learn charizard fly
pokecli search item ball
```

## The Command Model

Every resource is addressed the same way, verb first:

```bash
pokecli get <resource> <name_or_id>
pokecli list <resource>
pokecli search <resource> <query>
```

There is exactly one path to any resource. No shortcuts, no nested groups, no aliases.

The resources are:

| | | | |
|---|---|---|---|
| `pokemon` | `pokemon-species` | `pokemon-form` | `evolution-chain` |
| `move` | `item` | `ability` | `type` |
| `nature` | `berry` | `location` | `location-area` |
| `region` | `generation` | `version` | `version-group` |
| `pokedex` | `machine` | | |

`pokecli get --help` (and `list --help`, `search --help`) prints the same list with a one-line description of each.

## Task Commands

Six questions need more than one request, or write a file. They get their own names:

| Command | Answers |
|---------|---------|
| `pokecli moves <pokemon>` | Every move it can learn, grouped by method |
| `pokecli can-learn <pokemon> <move>` | Yes or no, as an exit code |
| `pokecli evolution <pokemon>` | The full chain, from any member of it |
| `pokecli encounters <pokemon>` | Where it appears in the wild |
| `pokecli forms <pokemon>` | Mega, Alolan, Gigantamax and other varieties |
| `pokecli sprite <pokemon> -o <path>` | Downloads a sprite image |

## Common Workflows

### Look up a Pokemon

```bash
pokecli get pokemon pikachu
pokecli get pokemon-species pikachu
pokecli get pokemon 25
```

### Find something when you half-remember the name

```bash
pokecli search pokemon char
pokecli search item ball
pokecli search move thunder
```

Names are case-insensitive and spaces become hyphens, so `pokecli get item "master ball"` works.

### Check where to find a Pokemon

```bash
pokecli encounters pikachu
pokecli encounters pikachu --game yellow
pokecli get location-area trophy-garden-area
```

### Check if a Pokemon can learn a move

```bash
pokecli can-learn pikachu thunderbolt
pokecli can-learn charizard fly --method machine
pokecli can-learn gyarados blizzard --method machine --game red
```

`--game` takes a single game (`red`, `sword`) or a pair (`red-blue`). Without it,
results merge every game. DLC areas have their own names, such as
`the-isle-of-armor-sword`.

The exit code is the answer: 0 for yes, 1 for no. That makes it usable directly in a script:

```bash
if pokecli can-learn charizard fly; then echo "yes"; fi
```

### View an evolution chain

```bash
pokecli evolution eevee
pokecli evolution charmeleon    # mid-chain lookups return the whole chain
```

### Browse a region and its encounter areas

```bash
pokecli get region kanto
pokecli get location kanto-route-1
pokecli get location-area kanto-route-1-area
```

### Download a sprite

```bash
pokecli sprite pikachu -o pikachu.png
pokecli sprite pikachu -o shiny.png --variant front_shiny
```

## All Commands

| Command | Purpose |
|---------|---------|
| `get <resource> <id>` | Fetch one record |
| `list <resource>` | Browse, paginated with `--limit` and `--offset` |
| `search <resource> <query>` | Find names containing a substring |
| `moves <pokemon>` | Learnable moves, `--method` and `--game` to filter |
| `can-learn <pokemon> <move>` | Learnability check, answer in the exit code; `--method` and `--game` to narrow |
| `evolution <pokemon>` | Full evolution chain |
| `encounters <pokemon>` | Wild encounter locations, `--game` to filter |
| `forms <pokemon>` | Species varieties |
| `sprite <pokemon> -o <path>` | Download a sprite, `--variant` to choose |
| `cache stats` | Cached entry counts per resource |
| `cache clear` | Clear the cache, `--resource` to narrow |
| `install --skills` | Install the packaged agent skill files, `--agent` for `claude` or `kiro`, `--local` for the workspace |

## Output Formats

| Format | Description |
|--------|-------------|
| `table` | Rich formatted output for reading in a terminal |
| `toon` | Token-optimized compact output for agents and scripts |
| `json` | Raw JSON, nothing else on stdout |

**The default follows context.** When stdout is an interactive terminal you get `table`. When output is piped, redirected, or captured by another program you get `toon`. An automated caller needs no flag.

This applies to every command that returns data, including `cache stats` and the no-argument view. Commands that perform an action and report the outcome — `cache clear`, `sprite`, `install` — take no `--format`.

An explicit `--format` always wins:

```bash
pokecli get pokemon pikachu --format table | less -R
pokecli get pokedex kanto --format json | jq -r '.pokemon_entries[].pokemon_species.name'
```

Use `json` when the next step is a parser. It contains only the record — no hints, no styling.

## TOON Format

```bash
$ pokecli get pokemon pikachu --format toon
pokemon:
  id: 25
  name: pikachu
  types: electric
  abilities: static/lightning-rod(H)
  stats: "hp:35/atk:55/def:40/spa:50/spd:50/spe:90"
  total_moves: 109

help[3]: pokecli moves pikachu,pokecli evolution pikachu,pokecli encounters pikachu
```

For collections:

```bash
$ pokecli list pokemon --format toon
count: 20 of 1302 total
pokemon[20]{name}:
  bulbasaur
  ivysaur
  ...

help[1]: pokecli get pokemon bulbasaur
```

Every response includes `help[]` hints naming valid next commands.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success. For `can-learn`, also means yes |
| 1 | Not found, unreachable API, invalid `--variant`, no learnset data for `--game`, or `can-learn` answering no |
| 2 | Invalid invocation (unknown command, resource, option, `--method`, or `--game`), or a response that did not match the expected shape |

A mistyped `--method` or `--game` exits 2, so `can-learn` never reports a typo as "no".

## Caching

The cache lives at `~/.pokecli/cache.json`.

```bash
pokecli get pokemon pikachu --no-cache
pokecli cache stats
pokecli cache clear
pokecli cache clear --resource pokemon
```

`search` caches a name index per resource, so the first search costs one request and later searches on that resource cost none.

## Notes For Agents

- `pokecli get <resource> <id>` covers every resource. There is no second way.
- Do not pass `--format`. Piped output is already TOON.
- Use `--format json` only when a result must be filtered or calculated, not just read. Prefer `python3` as the parser, and use `jq` only after confirming it is installed.
- The resource vocabulary, each name with its purpose, is in the installed skill. Read it there rather than calling `--help`, which is styled terminal output and wastes tokens. Re-run `pokecli install --skills` after upgrading so the installed copy matches the binary.
- Branch on `can-learn`'s exit code instead of parsing its output.
- `pokecli install --skills` installs the packaged skill and references for Claude Code. Use `pokecli install --skills --agent kiro` for Kiro. Add `--local` to install into the current project instead of the home directory:

| Agent | Global (default) | Workspace (`--local`) |
|-------|------------------|-----------------------|
| `claude` (default) | `~/.claude/skills/pokecli/` | `.claude/skills/pokecli/` |
| `kiro` | `~/.kiro/skills/pokecli/`, or `$KIRO_HOME/skills/pokecli/` | `.kiro/skills/pokecli/` |

```bash
pokecli install --skills --agent kiro          # all your projects
pokecli install --skills --agent kiro --local  # this project only
```

The Kiro copy keeps only the `name` and `description` frontmatter fields, since those are the ones Kiro documents.

## Breaking Changes in 0.2.0

The command surface was consolidated from 73 invocable paths to 12. If you used an earlier version:

| Before | Now |
|--------|-----|
| `pokecli pokemon pikachu` | `pokecli get pokemon pikachu` |
| `pokecli pokemon get pikachu` | `pokecli get pokemon pikachu` |
| `pokecli move thunderbolt` | `pokecli get move thunderbolt` |
| `pokecli pokemon species pikachu` | `pokecli get pokemon-species pikachu` |
| `pokecli pokemon where pikachu` | `pokecli encounters pikachu` |
| `pokecli pokemon evo eevee` | `pokecli evolution eevee` |
| `pokecli pokemon moves pikachu` | `pokecli moves pikachu` |
| `pokecli pokemon can-learn a b` | `pokecli can-learn a b` |
| `pokecli pokemon forms charizard` | `pokecli forms charizard` |
| `pokecli pokemon form get x` | `pokecli get pokemon-form x` |
| `pokecli pokemon evolution-chain get 2` | `pokecli get evolution-chain 2` |
| `pokecli game region get kanto` | `pokecli get region kanto` |
| `pokecli game machine get 79` | `pokecli get machine 79` |
| `pokecli location area get x` | `pokecli get location-area x` |
| `pokecli image download pokemon x -o f` | `pokecli sprite x -o f` |
| `pokecli moves x --move y` | `pokecli can-learn x y` |
| `pokecli list resources` | `pokecli get --help`, or the installed skill for agents |
| `pokecli ... --format toon` | omit it; piped output is TOON |

Piped invocations that previously received `table` output now receive `toon`. Pass `--format table` explicitly if you depended on it.

## Data Source

All data comes from [PokeAPI](https://pokeapi.co), `https://pokeapi.co/api/v2`.

## Credits

Pokemon and Pokemon character names are trademarks of Nintendo.
