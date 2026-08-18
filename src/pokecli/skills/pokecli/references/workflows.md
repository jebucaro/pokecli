# pokecli Multi-Step Workflows

Recipes for questions that span multiple resources.

## Where can I catch Pokemon X?

Fastest path:

```bash
pokecli pokemon encounters pikachu --format toon
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
pokecli location area get trophy-garden-area --format toon
```

## What lives at Route N in region R?

Top-down traversal: region, then location, then area.

```bash
# 1. List locations in a region
pokecli game region get kanto --format toon

# 2. Inspect the location to find sub-areas
pokecli location get kanto-route-1 --format toon

# 3. Inspect the encounter area
pokecli location area get kanto-route-1-area --format toon
```

Shell scripting variant only, requires `jq`:

```bash
pokecli game region get kanto --format json | jq '.locations[].name'
pokecli location area get kanto-route-1-area --format json \
  | jq '.pokemon_encounters[].pokemon.name'
```

## What's new in Generation N?

```bash
pokecli game generation get generation-i --format toon
```

Shell scripting variant only, requires `jq`:

```bash
pokecli game generation get generation-iii --format json \
  | jq -r '.pokemon_species[].name' | sort
```

## Regional Pokedex listing

```bash
pokecli game pokedex get kanto --format toon
```

Shell scripting variant only, requires `jq`:

```bash
pokecli game pokedex get kanto --format json \
  | jq -r '.pokemon_entries[] | "\(.entry_number) \(.pokemon_species.name)"'
```

## Which TM teaches a move?

pokecli has no move-to-machine index. `game machine get <id>` only works once you already
have the numeric ID; `move get` and `pokemon moves` never surface it:

```bash
pokecli move get thunderbolt --format toon
```

Do not try to reconstruct the mapping by guessing machine IDs across generations or by
querying the PokeAPI directly outside pokecli — that burns many round trips for an answer
that's still likely wrong, and it defeats the point of using the CLI.

If the user already has a machine ID or TM/TR number (from an in-game label, a previous
lookup, etc.), look it up directly:

```bash
pokecli game machine get 79 --format toon
```

Otherwise, tell the user pokecli can't resolve a move name to its TM/machine number on its
own, and offer to browse instead (paginated, 20 per page):

```bash
pokecli game machine list
```

Cross-referencing learnability only needs the move name, not a machine ID:

```bash
pokecli pokemon can-learn charizard thunderbolt --method machine --format toon
```

## Full Pokemon profile

Use the Pokemon command family to build context quickly:

```bash
pokecli pokemon get pikachu --format toon
pokecli pokemon species pikachu --format toon
pokecli pokemon evolution pikachu --format toon
pokecli pokemon forms pikachu --format toon
pokecli pokemon encounters pikachu --format toon
pokecli pokemon moves pikachu --format toon
```

## Alternative form inspection

List varieties, then inspect a specific form.

```bash
pokecli pokemon forms charizard --format toon
pokecli pokemon form get charizard-mega-x --format toon
```

## Evolution chain by chain ID

If you already have a chain ID, skip the species lookup:

```bash
pokecli pokemon evolution-chain get 67 --format toon
```
