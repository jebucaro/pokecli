# pokecli Multi-Step Workflows

Recipes for questions that span multiple resources.

## Where can I catch Pokemon X?

Fastest path:

```bash
pokecli pokemon encounters pikachu
```

Short manual alias:

```bash
pokecli pokemon where pikachu
```

Shell scripting variant only, requires `jq`:

```bash
pokecli pokemon encounters pikachu --format json
```

Inspect one encounter area in detail:

```bash
pokecli location area get trophy-garden-area
```

## What lives at Route N in region R?

Top-down traversal: region, then location, then area.

```bash
# 1. List locations in a region
pokecli game region get kanto

# 2. Inspect the location to find sub-areas
pokecli location get kanto-route-1

# 3. Inspect the encounter area
pokecli location area get kanto-route-1-area
```

Shell scripting variant only, requires `jq`:

```bash
pokecli game region get kanto --format json | jq '.locations[].name'
pokecli location area get kanto-route-1-area --format json \
  | jq '.pokemon_encounters[].pokemon.name'
```

## What's new in Generation N?

```bash
pokecli game generation get generation-i
```

Shell scripting variant only, requires `jq`:

```bash
pokecli game generation get generation-iii --format json \
  | jq -r '.pokemon_species[].name' | sort
```

## Regional Pokedex listing

```bash
pokecli game pokedex get kanto
```

Shell scripting variant only, requires `jq`:

```bash
pokecli game pokedex get kanto --format json \
  | jq -r '.pokemon_entries[] | "\(.entry_number) \(.pokemon_species.name)"'
```

## Which TM teaches a move?

Start with the move:

```bash
pokecli move get thunderbolt
```

Then inspect one machine ID:

```bash
pokecli game machine get 79
```

Cross-reference with Pokemon learnability:

```bash
pokecli pokemon can-learn charizard thunderbolt --method machine
```

## Full Pokemon profile

Use the Pokemon command family to build context quickly:

```bash
pokecli pokemon get pikachu
pokecli pokemon species pikachu
pokecli pokemon evolution pikachu
pokecli pokemon forms pikachu
pokecli pokemon encounters pikachu
pokecli pokemon moves pikachu
```

## Alternative form inspection

List varieties, then inspect a specific form.

```bash
pokecli pokemon forms charizard
pokecli pokemon form get charizard-mega-x
```

## Evolution chain by chain ID

If you already have a chain ID, skip the species lookup:

```bash
pokecli pokemon evolution-chain get 67
```

## Decoding cross-reference fields

When `pokemon species` returns egg groups, growth rate, or trigger names, resolve them inside the Pokemon group:

```bash
pokecli pokemon egg-group get ground
pokecli pokemon growth-rate get medium-slow
pokecli pokemon evolution-trigger get use-item
```

Move-specific references stay under `move`:

```bash
pokecli move damage-class get special
pokecli move learn-method get machine
```
