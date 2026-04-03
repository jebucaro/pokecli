---
name: pokecli
description: Queries Pokémon, Berries, Items, and Moves data via the pokecli CLI. Use when the user needs to look up Pokémon stats, berries, items, or moves, download sprites, or manage the local cache. Also use when the user mentions "pokecli", "pokedex", or "PokeAPI"
allowed-tools: Bash(pokecli:*)
---

# Pokémon Data Lookup with pokecli

## Quick start

```bash
pokecli pokemon get pikachu
pokecli berry get oran
pokecli item get master-ball
pokecli move get thunderbolt
```

## Core workflow

1. Query: Use `pokecli <resource> get <name_or_id>` to fetch details
2. Browse: Use `pokecli <resource> list` to paginate through all entries
3. Download: Use `pokecli image download pokemon <name> -o <path>` for sprites
4. Cache: Use `pokecli cache stats` and `pokecli cache clear` to manage local data

Responses are cached locally after the first request. Use `--no-cache` to force a fresh fetch.

## Commands

### Pokemon

```bash
pokecli pokemon get pikachu
pokecli pokemon get 25
pokecli pokemon get charizard --format json
pokecli pokemon get bulbasaur --no-cache
pokecli pokemon list
pokecli pokemon list --limit 50
pokecli pokemon list --limit 20 --offset 40
pokecli pokemon moves charmander
pokecli pokemon moves 4 --format json
pokecli pokemon moves pikachu --move thunderbolt
pokecli pokemon moves pikachu --move thunderbolt --format json
pokecli pokemon moves eevee --method egg
pokecli pokemon moves charizard --method level-up
```

### Berry

```bash
pokecli berry get cheri
pokecli berry get 1
pokecli berry get oran --format json
pokecli berry list
pokecli berry list --limit 10
pokecli berry list --limit 10 --offset 20
```

### Item

```bash
pokecli item get potion
pokecli item get 1
pokecli item get master-ball --format json
pokecli item list
pokecli item list --limit 30
pokecli item list --limit 30 --offset 60
```

### Move

```bash
pokecli move get thunderbolt
pokecli move get 24
pokecli move get surf --format json
pokecli move get flamethrower --no-cache
pokecli move list
pokecli move list --limit 40
pokecli move list --limit 20 --offset 100
```

### Image Download

```bash
pokecli image download pokemon pikachu -o pikachu.png
pokecli image download pokemon pikachu -o pikachu_shiny.png --variant front_shiny
pokecli image download pokemon 6 -o charizard_back.png --variant back_default
pokecli image download pokemon 133 -o /tmp/eevee.png
```

Sprite variants: `front_default`, `front_shiny`, `back_default`, `back_shiny`, `front_female`, `front_shiny_female`

### Cache Management

```bash
pokecli cache stats
pokecli cache clear
pokecli cache clear --resource pokemon
pokecli cache clear --resource item
```

## Global options

| Option | Description |
|--------|-------------|
| `--no-cache` | Bypass local cache, fetch fresh from PokeAPI |
| `--format table` | Rich formatted table output (default) |
| `--format json` | Raw JSON with syntax highlighting |

## `pokemon moves` options

| Option | Description |
|--------|-------------|
| `--move <name>` | Filter to a specific move; exits 1 if the Pokémon cannot learn it |
| `--method <method>` | Filter by learn method: `level-up`, `machine`, `tutor`, `egg` |

## Example: Compare two Pokémon

```bash
pokecli pokemon get charizard
pokecli pokemon get blastoise
```

## Example: Browse and then inspect

```bash
pokecli move list --limit 10
pokecli move get pound
```

## Example: Download all starters

```bash
pokecli image download pokemon bulbasaur -o bulbasaur.png
pokecli image download pokemon charmander -o charmander.png
pokecli image download pokemon squirtle -o squirtle.png
```

## Example: Look up moves a Pokémon can learn

```bash
# All moves with summary footer
pokecli pokemon moves pikachu

# Check if a Pokémon can learn a specific move (table)
pokecli pokemon moves pikachu --move thunderbolt

# Agent-friendly: returns {"can_learn": true/false, "method": "...", "level": N}
pokecli pokemon moves pikachu --move thunderbolt --format json

# Filter by learn method: level-up, machine, tutor, egg
pokecli pokemon moves eevee --method egg
pokecli pokemon moves charizard --method level-up --format json
```

**`--move` exit codes:** `0` if the Pokémon can learn the move, `1` if it cannot.

## Troubleshooting

For detailed command reference and data field descriptions, consult `references/api-fields.md`.
