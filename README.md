# pokecli

`pokecli` is a command line interface for looking up Pokemon data from [PokeAPI](https://pokeapi.co/api/v2). It covers Pokemon, moves, items, abilities, locations, game data, forms, machines, and a few lower-level reference resources. Results are shown as rich terminal tables by default, raw JSON is available when you need it, and responses are cached locally.

## Features

- Canonical `get` and `list` commands for agents and scripts
- Human-friendly shortcuts like `pokecli pokemon pikachu`
- Pokemon task commands for moves, evolutions, encounters, forms, and sprites
- Grouped reference commands under `pokemon`, `move`, `location`, and `game`
- Rich output with tables, panels, and syntax-highlighted JSON
- Local TinyDB cache to cut down on repeated API calls

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

Most common lookups:

```bash
pokecli pokemon pikachu
pokecli move thunderbolt
pokecli ability intimidate
pokecli type fire
pokecli location pallet-town
```

Canonical commands, best for scripts and agents:

```bash
pokecli pokemon get pikachu
pokecli move get thunderbolt
pokecli ability get intimidate
pokecli type get fire
pokecli game region get kanto
```

## Command Model

There are two layers in the CLI:

1. Canonical commands, these are stable and explicit.
2. Human aliases, these are shorter and easier to type.

Examples:

```bash
# Human alias
pokecli pokemon pikachu

# Canonical equivalent
pokecli pokemon get pikachu

# Human alias
pokecli move thunderbolt

# Canonical equivalent
pokecli move get thunderbolt
```

For agents, prefer the canonical command paths. Human aliases are there for quicker manual use.

## Common Workflows

### Look up a Pokemon

```bash
pokecli pokemon pikachu
pokecli pokemon get charizard
pokecli pokemon get bulbasaur --no-cache
```

### Check where to find a Pokemon

```bash
pokecli pokemon where pikachu
pokecli pokemon encounters pikachu
```

### Check if a Pokemon can learn a move

```bash
pokecli pokemon can-learn pikachu thunderbolt
pokecli pokemon can-learn charizard fly --method machine
```

### View an evolution chain

```bash
pokecli pokemon evo eevee
pokecli pokemon evolution charmander
```

### List all moves a Pokemon can learn

```bash
pokecli pokemon moves eevee
pokecli pokemon can-learn pikachu thunderbolt
pokecli pokemon moves charizard --method level-up
```

### Download a sprite

```bash
pokecli pokemon image pikachu -o pikachu.png
pokecli pokemon image pikachu -o pikachu_shiny.png --variant front_shiny
```

### Browse a region and its encounter areas

```bash
pokecli game region get kanto
pokecli location get kanto-route-1
pokecli location area get kanto-route-1-area
```

## Top-Level Commands

| Command | Purpose |
|--------|---------|
| `pokemon` | Pokemon lookup, species, moves, evolutions, forms, encounters, and Pokemon-adjacent reference data |
| `move` | Move lookup, damage classes, and learn methods |
| `item` | Item lookup |
| `ability` | Ability lookup |
| `type` | Type matchup lookup |
| `location` | Location lookup and location areas |
| `game` | Regions, generations, versions, pokedexes, and machines |
| `image` | Direct sprite download command |
| `cache` | Cache stats and cache clearing |
| `nature` | Nature lookup |
| `berry` | Berry lookup |

## Canonical Command Reference

### `pokemon`

Canonical lookup commands:

```bash
pokecli pokemon get <name_or_id>
pokecli pokemon list [--limit --offset]
pokecli pokemon moves <name_or_id>
pokecli pokemon species <name_or_id>
pokecli pokemon evolution <name_or_id>
pokecli pokemon encounters <name_or_id>
pokecli pokemon forms <name_or_id>
```

Task aliases:

```bash
pokecli pokemon <name_or_id>
pokecli pokemon where <name_or_id>
pokecli pokemon can-learn <name_or_id> <move_name>
pokecli pokemon evo <name_or_id>
pokecli pokemon image <name_or_id> -o <path>
```

Nested reference groups:

```bash
pokecli pokemon form get <form_name>
pokecli pokemon egg-group get <name>
pokecli pokemon growth-rate get <name>
pokecli pokemon evolution-trigger get <name>
pokecli pokemon evolution-chain get <id>
```

### `move`

```bash
pokecli move get <name_or_id>
pokecli move list [--limit --offset]
pokecli move damage-class get <name_or_id>
pokecli move learn-method get <name_or_id>
```

Human alias:

```bash
pokecli move <name_or_id>
```

### `item`

```bash
pokecli item get <name_or_id>
pokecli item list [--limit --offset]
```

Human alias:

```bash
pokecli item <name_or_id>
```

### `ability`

```bash
pokecli ability get <name_or_id>
pokecli ability list [--limit --offset]
```

Human alias:

```bash
pokecli ability <name_or_id>
```

### `type`

```bash
pokecli type get <name_or_id>
pokecli type list [--limit --offset]
```

Human alias:

```bash
pokecli type <name_or_id>
```

### `location`

```bash
pokecli location get <name_or_id>
pokecli location list [--limit --offset]
pokecli location area get <name_or_id>
```

Human alias:

```bash
pokecli location <name_or_id>
```

### `game`

```bash
pokecli game region get <name_or_id>
pokecli game generation get <name_or_id>
pokecli game version get <name_or_id>
pokecli game version-group get <name_or_id>
pokecli game pokedex get <name_or_id>
pokecli game machine get <id>
```

### `image`

```bash
pokecli image download pokemon <name_or_id> -o <path>
```

If you are already in a Pokemon workflow, `pokecli pokemon image ...` is the shorter path.

### `cache`

```bash
pokecli cache stats
pokecli cache clear
pokecli cache clear --resource pokemon
```

## Output Formats

All `get` commands, plus the richer Pokemon task commands, support `--format`.

| Format | Description |
|--------|-------------|
| `table` | Rich formatted output, default |
| `json` | Raw JSON with syntax highlighting |

Use `table` by default when you are reading the result in the terminal.

Use `json` only when the next step includes a parser, for example `jq` or a Python script.

Examples:

```bash
pokecli game pokedex get kanto --format json | jq -r '.pokemon_entries[].pokemon_species.name'
pokecli pokemon encounters pikachu --format json | jq '.[].location_area.name'
```

## Caching

The local cache lives at `~/.pokecli/cache.json`.

Use `--no-cache` on resource lookups when you want fresh data:

```bash
pokecli pokemon get pikachu --no-cache
pokecli pokemon encounters pikachu --no-cache
pokecli move get thunderbolt --no-cache
```

Inspect or clear the cache:

```bash
pokecli cache stats
pokecli cache clear
pokecli cache clear --resource pokemon
pokecli cache clear --resource pokemon-species
```

## Notes For Agents

- Prefer canonical commands like `pokemon get`, `move get`, `game region get`
- Use bare aliases like `pokemon pikachu` only when you want the shorter human path
- Prefer table output for direct reading in the terminal
- Only use `--format json` when the next step explicitly includes a parser like `jq` or a Python script
- Avoid switching to JSON if you are just going to read the output yourself, table output is usually easier

## Data Source

All data comes from [PokeAPI](https://pokeapi.co), `https://pokeapi.co/api/v2`.

## Credits

Pokemon and Pokemon character names are trademarks of Nintendo.
