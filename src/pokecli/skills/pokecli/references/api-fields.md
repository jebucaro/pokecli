# pokecli API Field Reference

Detailed data fields returned by each resource type. Consult this when you need
to interpret or explain specific fields from `pokecli` output.

## Pokemon Fields

| Field | Description |
|-------|-------------|
| Name | Pokémon species name |
| ID | National Pokédex number |
| Types | Elemental types (e.g. Fire, Water, Grass) |
| Stats | HP, Attack, Defense, Sp. Atk, Sp. Def, Speed (base values) |
| Abilities | Normal and hidden abilities |
| Height | Height in decimetres |
| Weight | Weight in hectograms |
| Base Experience | Experience gained by defeating this Pokémon |

## Pokemon Moves Fields

Returned by `pokecli pokemon moves <name_or_id>`.

| Field | Description |
|-------|-------------|
| `name` | Move name (hyphen-separated, e.g. `flamethrower`) |
| `learn_method` | How the move is learned: `level-up`, `machine`, `tutor`, or `egg` |
| `level` | Level at which the move is learned (level-up only; `0` for all others) |

Results are deduplicated across all game versions. Each move appears once,
with the learn method taken from the most recent game version that includes it.
Sorted: level-up moves first (by level), then machine/tutor/egg alphabetically.

## Berry Fields

| Field | Description |
|-------|-------------|
| Name | Berry name |
| ID | Berry identifier |
| Growth Time | Hours per growth stage |
| Max Harvest | Maximum berries per harvest |
| Firmness | Texture category (very-soft to super-hard) |
| Flavors | Spicy, Dry, Sweet, Bitter, Sour (potency values) |
| Natural Gift Power | Power when used as Natural Gift move |
| Natural Gift Type | Type when used as Natural Gift move |

## Item Fields

| Field | Description |
|-------|-------------|
| Name | Item name |
| ID | Item identifier |
| Cost | Purchase price in Pokédollars |
| Category | Item category (e.g. medicine, pokeball) |
| Fling Power | Power when used with Fling move |
| Effect | Short mechanical effect text |
| Flavor Text | In-game description |

## Move Fields

| Field | Description |
|-------|-------------|
| Name | Move name |
| ID | Move identifier |
| Type | Elemental type |
| Damage Class | physical, special, or status |
| Power | Base power (null for status moves) |
| Accuracy | Hit chance percentage (null if always hits) |
| PP | Power Points (number of uses) |
| Effect Chance | Percentage chance of secondary effect |
| Effect | Mechanical effect description |

## Sprite Variants

| Variant Key | Description |
|-------------|-------------|
| `front_default` | Standard front-facing sprite |
| `front_shiny` | Shiny coloration, front-facing |
| `back_default` | Standard back-facing sprite |
| `back_shiny` | Shiny coloration, back-facing |
| `front_female` | Female variant, front-facing (if exists) |
| `front_shiny_female` | Shiny female variant, front-facing (if exists) |

## Cache Location

All cached responses are stored at `~/.pokecli/cache.json` using TinyDB.
Each entry is keyed by resource type and name/ID.

## Data Source

All data originates from [PokeAPI](https://pokeapi.co/api/v2).
No authentication required. Free and open.
