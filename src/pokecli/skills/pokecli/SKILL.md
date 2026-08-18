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

Always use `--format toon` for token-efficient output. This produces compact key:value output optimized for LLM context windows (~40% smaller than JSON). Only use `--format json` when the next step explicitly includes `jq` or another parser. Do not use `--format table` — it contains Rich markup that wastes tokens.

## Quick start

```bash
pokecli pokemon get pikachu --format toon
pokecli move get thunderbolt --format toon
pokecli ability get intimidate --format toon
pokecli type get fire --format toon
pokecli game region get kanto --format toon
pokecli location get pallet-town --format toon
```

## TOON output format

The `--format toon` output uses Token-Optimized Object Notation:
- Single resources show as `label:` followed by indented `key: value` pairs
- Lists show as `label[count]{fields}:` followed by indented comma-separated rows
- Every response ends with `help[]` hints for next steps
- Aggregates like `count`, `total_moves`, `methods` appear as top-level keys

## Core workflow

1. Query: use `pokecli <resource> get <name_or_id>` on the main resources.
2. Browse: use `pokecli <resource> list` when available.
3. Pokemon-specific tasks live under `pokemon`, for example `species`, `evolution`, `encounters`, `forms`, and `can-learn`.
4. Nested reference resources are grouped under `pokemon`, `location`, and `game`.
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
| Type matchups | `pokecli type get <name>` |
| Item details | `pokecli item get <name>` |
| Nature effects | `pokecli nature get <name>` |
| Berry details | `pokecli berry get <name>` |
| Region details | `pokecli game region get <name>` |
| Location details | `pokecli location get <name>` |
| Location encounter area details | `pokecli location area get <name>` |
| Generation roster | `pokecli game generation get <name>` |
| Regional pokedex listing | `pokecli game pokedex get <name>` |
| Game version details | `pokecli game version get <name>` |
| Version group details | `pokecli game version-group get <name>` |
| TM or HM lookup | `pokecli game machine get <id>` |
| Evolution chain by chain ID | `pokecli pokemon evolution-chain get <id>` |
| Browse available resources | `pokecli <resource> list` |

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
pokecli pokemon form list
pokecli pokemon evolution-chain get 67
pokecli pokemon evolution-chain list
```

### Move

```bash
pokecli move get thunderbolt
pokecli move list
```

### Game

```bash
pokecli game region get kanto
pokecli game region list
pokecli game generation get generation-i
pokecli game generation list
pokecli game pokedex get national
pokecli game pokedex list
pokecli game version get red
pokecli game version list
pokecli game version-group get red-blue
pokecli game version-group list
pokecli game machine get 79
pokecli game machine list
```

### Location

```bash
pokecli location get kanto-route-1
pokecli location list
pokecli location area get kanto-route-1-area
pokecli location area list
```

### Other main resources

```bash
pokecli ability get intimidate
pokecli ability list
pokecli item get master-ball
pokecli item list
pokecli type get fire
pokecli type list
pokecli nature get modest
pokecli nature list
pokecli berry get oran
pokecli berry list
```

### Cache

```bash
pokecli cache stats
pokecli cache clear
pokecli cache clear --resource pokemon
```

## Output format guidance

Always use `--format toon` when calling pokecli:

```bash
pokecli pokemon get pikachu --format toon
pokecli move get thunderbolt --format toon
pokecli pokemon moves charizard --format toon
```

The output includes contextual `help[]` hints suggesting logical next steps.

Only use `--format json` when piping to `jq` or another JSON parser:

```bash
pokecli game pokedex get kanto --format json | jq -r '.pokemon_entries[].pokemon_species.name'
```

## Multi-step workflows

For recipes that jump across commands, read `references/workflows.md`.

## Field details

For response field explanations, read `references/api-fields.md`.
