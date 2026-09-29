# pokecli Multi-Step Workflows

Recipes for questions that span more than one command.

Output is TOON automatically when piped, so none of these pass `--format`.
Answer from the default output first. The "Shell scripting variant" blocks are
for scripts that need a parser. They use `jq`, so confirm it exists
(`command -v jq`) before running one, and otherwise read the default output or
use `python3` as shown in SKILL.md.

## Where can I catch Pokemon X?

```bash
pokecli encounters pikachu
pokecli encounters pikachu --game yellow
```

Then inspect one area in detail:

```bash
pokecli get location-area trophy-garden-area
```

Shell scripting variant, requires `jq`:

```bash
pokecli encounters pikachu --format json | jq -r '.encounters[].location_area.name'
```

## What lives at Route N in region R?

Top-down: region, then location, then area.

```bash
pokecli get region kanto
pokecli get location kanto-route-1
pokecli get location-area kanto-route-1-area
```

Shell scripting variant, requires `jq`:

```bash
pokecli get region kanto --format json | jq -r '.locations[].name'
pokecli get location-area kanto-route-1-area --format json \
  | jq -r '.pokemon_encounters[].pokemon.name'
```

## I only remember part of the name

`search` matches any substring of a resource name, case-insensitively. Reach for
it instead of paging `list` when the resource is large.

```bash
pokecli search pokemon char
pokecli search item ball
pokecli search move thunder
pokecli search location-area route-1
```

The first search for a resource fetches and caches its name index; later
searches on that resource cost no request.

## What's new in Generation N?

```bash
pokecli get generation generation-i
```

Shell scripting variant, requires `jq`:

```bash
pokecli get generation generation-iii --format json \
  | jq -r '.pokemon_species[].name' | sort
```

## Regional Pokedex listing

```bash
pokecli get pokedex kanto
```

Shell scripting variant, requires `jq`:

```bash
pokecli get pokedex kanto --format json \
  | jq -r '.pokemon_entries[] | "\(.entry_number) \(.pokemon_species.name)"'
```

## Which TM teaches a move?

pokecli has no move-to-machine index, and PokeAPI does not expose one. `get
machine <id>` works only once you already have the numeric ID, and neither `get
move` nor `moves` surfaces it.

Do not try to reconstruct the mapping by guessing machine IDs across generations
or by querying PokeAPI outside pokecli. That burns many round trips for an answer
that is still likely wrong.

If the user already has a TM number from an in-game label or an earlier lookup:

```bash
pokecli get machine 79
```

If they do not, say pokecli cannot resolve a move name to its TM number, and
answer the question they probably meant instead — whether the Pokemon can learn
it by machine:

```bash
pokecli can-learn charizard thunderbolt --method machine --game red
```

To explore what machines exist at all:

```bash
pokecli search machine tm
pokecli list machine --limit 50
```

## Full Pokemon profile

```bash
pokecli get pokemon pikachu
pokecli get pokemon-species pikachu
pokecli evolution pikachu
pokecli forms pikachu
pokecli encounters pikachu
pokecli moves pikachu
```

## Alternate form inspection

List varieties, then inspect one.

```bash
pokecli forms charizard
pokecli get pokemon-form charizard-mega-x
```

## Evolution chain by chain ID

`evolution <pokemon>` resolves the chain for you and is the normal path. Use the
chain ID directly only when you already have one:

```bash
pokecli get evolution-chain 2
```

## Checking learnability in a script

`can-learn` returns its answer as an exit code, so it composes directly:

```bash
for p in pikachu charizard gyarados; do
  if pokecli can-learn "$p" surf >/dev/null; then
    echo "$p can learn surf"
  fi
done
```
