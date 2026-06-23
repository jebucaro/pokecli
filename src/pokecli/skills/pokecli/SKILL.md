---
name: pokecli
description: Queries Pokemon, moves, items, abilities, types, locations, game data, forms, machines, encounters, evolutions, and other PokeAPI-backed resources via the pokecli CLI. Use when the user needs Pokemon stats, move info, type matchups, catch locations, evolution chains, sprite downloads, regional or generation data, or cache management. Also use when the user mentions pokecli, pokedex, or PokeAPI.
allowed-tools: Bash(pokecli:*)
user-invocable: false
---

# Pokemon Data Lookup With pokecli

## Agent rule

Use the canonical command path shown in this skill. Human aliases exist, but agents should prefer explicit commands like `pokemon get`, `move get`, and `game region get`.

If a memorized command fails, check `pokecli --help` or the subgroup help before guessing.

Prefer the default table output. Do not switch to `--format json` unless the next step explicitly includes `jq` or another parser, for example a Python script. Raw JSON is harder for agents to read directly, and it usually adds extra parsing work instead of helping.

## Quick start

```bash
pokecli pokemon get pikachu
pokecli move get thunderbolt
pokecli ability get intimidate
pokecli type get fire
pokecli game region get kanto
pokecli location get pallet-town
```

## Core workflow

1. Query: use `pokecli <resource> get <name_or_id>` on the main resources.
2. Browse: use `pokecli <resource> list` when available.
3. Pokemon-specific tasks live under `pokemon`, for example `species`, `evolution`, `encounters`, `forms`, and `can-learn`.
4. Nested reference resources are grouped under `pokemon`, `move`, `location`, and `game`.
5. Cache is managed with `pokecli cache stats` and `pokecli cache clear`.

Responses are cached locally after the first request. Use `--no-cache` to force a fresh fetch.

## Decision tree

| User intent | Canonical command |
|-------------|-------------------|
| Pokemon stats, types, abilities | `pokecli pokemon get <name>` |
| Moves a Pokemon can learn | `pokecli pokemon moves <name>` |
| Can this Pokemon learn move X? | `pokecli pokemon can-learn <name> <move>` |
| Pokedex entry, egg groups, capture rate | `pokecli pokemon species <name>` |
| Full evolution chain for a Pokemon | `pokecli pokemon evolution <name>` |
| Where can I catch this Pokemon? | `pokecli pokemon encounters <name>` |
| All varieties for a species | `pokecli pokemon forms <name>` |
| Inspect a specific form | `pokecli pokemon form get <form-name>` |
| Download a sprite | `pokecli pokemon image <name> -o <path>` |
| What does an ability do? | `pokecli ability get <name>` |
| What does a move do? | `pokecli move get <name>` |
| What is this move damage class? | `pokecli move damage-class get <name>` |
| What is this move learn method? | `pokecli move learn-method get <name>` |
| Type matchups | `pokecli type get <name>` |
| Item details | `pokecli item get <name>` |
| Nature effects | `pokecli nature get <name>` |
| Berry details | `pokecli berry get <name>` |
| Egg group meaning | `pokecli pokemon egg-group get <name>` |
| Growth rate meaning | `pokecli pokemon growth-rate get <name>` |
| Evolution trigger meaning | `pokecli pokemon evolution-trigger get <name>` |
| Region details | `pokecli game region get <name>` |
| Location details | `pokecli location get <name>` |
| Location encounter area details | `pokecli location area get <name>` |
| Generation roster | `pokecli game generation get <name>` |
| Regional pokedex listing | `pokecli game pokedex get <name>` |
| Game version details | `pokecli game version get <name>` |
| Version group details | `pokecli game version-group get <name>` |
| TM or HM lookup | `pokecli game machine get <id>` |
| Evolution chain by chain ID | `pokecli pokemon evolution-chain get <id>` |

## Human aliases

These are fine for manual use, but agents should not default to them.

```bash
pokecli pokemon pikachu
pokecli move thunderbolt
pokecli item master-ball
pokecli ability intimidate
pokecli type fire
pokecli location pallet-town
pokecli pokemon where pikachu
pokecli pokemon evo eevee
```

## Commands

### Pokemon

```bash
pokecli pokemon get pikachu
pokecli pokemon list
pokecli pokemon moves pikachu
pokecli pokemon species pikachu
pokecli pokemon evolution eevee
pokecli pokemon encounters pikachu
pokecli pokemon forms charizard
pokecli pokemon can-learn pikachu thunderbolt
pokecli pokemon image pikachu -o pikachu.png
pokecli pokemon form get charizard-mega-x
pokecli pokemon egg-group get monster
pokecli pokemon growth-rate get medium-slow
pokecli pokemon evolution-trigger get use-item
pokecli pokemon evolution-chain get 67
```

### Move

```bash
pokecli move get thunderbolt
pokecli move list
pokecli move damage-class get special
pokecli move learn-method get machine
```

### Game

```bash
pokecli game region get kanto
pokecli game generation get generation-i
pokecli game pokedex get national
pokecli game version get red
pokecli game version-group get red-blue
pokecli game machine get 79
```

### Location

```bash
pokecli location get kanto-route-1
pokecli location area get kanto-route-1-area
```

### Other main resources

```bash
pokecli ability get intimidate
pokecli item get master-ball
pokecli type get fire
pokecli nature get modest
pokecli berry get oran
```

### Cache

```bash
pokecli cache stats
pokecli cache clear
pokecli cache clear --resource pokemon
```

## Output format guidance

Prefer the default table output.

Use `--format json` only when the next shell step actually needs JSON, and only when you also have a parser step planned, for example `jq` or a Python script.

Good:

```bash
pokecli game pokedex get kanto --format json | jq -r '.pokemon_entries[].pokemon_species.name'
```

Avoid:

```bash
pokecli pokemon get pikachu --format json
```

Use the table output instead when you are just reading the result in the terminal.

## Multi-step workflows

For recipes that jump across commands, read `references/workflows.md`.

## Field details

For response field explanations, read `references/api-fields.md`.
