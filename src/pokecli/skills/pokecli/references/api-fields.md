# pokecli API Field Reference

> When using pokecli as an agent, always pass `--format toon` for compact output.

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
| `learn_method` | How the move is learned: `level-up`, `machine`, `tutor`, `egg`, or occasionally another upstream PokeAPI value such as `train` (a training-menu method used by newer games) |
| `level` | Level at which the move is learned (level-up only; `0` for all others) |

Results are deduplicated across all game versions. Each move appears once,
with the learn method taken from the most recent game version that includes it.
Sorted: level-up moves first (by level), then machine/tutor/egg alphabetically.
An unfamiliar method value is not a bug — PokeAPI adds new methods over time and pokecli
passes them through unmodified. None of them, including `machine`, carry a TM/machine ID;
see `workflows.md` for why that lookup needs a different starting point.

## Ability Fields

Returned by `pokecli ability get <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Ability name (hyphen-separated, e.g. `speed-boost`) |
| ID | Ability identifier |
| Generation | Generation in which the ability was introduced |
| Pokemon with this ability | Count of Pokémon that can have this ability |
| Effect | Short mechanical effect summary |
| Full Effect | Detailed description including edge cases |

## Nature Fields

Returned by `pokecli nature get <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Nature name |
| ID | Nature identifier |
| Stat Modifier | Which stat is boosted +10% and which is reduced -10% (or "Neutral" if no change) |
| Likes Flavor | Berry flavor this nature prefers |
| Hates Flavor | Berry flavor this nature dislikes |

There are 25 natures. 5 are neutral (no stat change). The remaining 20 each boost one stat and drop another.

## Type Fields

Returned by `pokecli type get <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Type name (e.g. `fire`, `dragon`) |
| ID | Type identifier |
| Pokemon | Count of Pokémon with this type |
| Moves | Count of moves of this type |
| Super effective → | Types this deals 2× damage to (attacking) |
| Not very effective → | Types this deals 0.5× damage to (attacking) |
| No effect → | Types this deals 0× damage to (attacking) |
| Weak to ← | Types that deal 2× damage to this type (defending) |
| Resists ← | Types that deal 0.5× damage to this type (defending) |
| Immune to ← | Types that deal 0× damage to this type (defending) |

## Pokemon Species Fields

Returned by `pokecli pokemon species <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Pokémon species name |
| ID | National Pokédex number |
| Legendary / Mythical | Flags shown in the header if applicable |
| Genus | Species descriptor (e.g. "Mouse Pokémon") |
| Generation | Generation in which the species was introduced |
| Color | Body color category |
| Growth Rate | Level-up experience curve (e.g. medium-slow) |
| Capture Rate | Catch rate out of 255 (higher = easier to catch) |
| Base Happiness | Starting friendship value |
| Gender | Male/female percentage ratio, or "Genderless" |
| Egg Groups | Breeding compatibility groups |
| Flavor Text | Latest English Pokédex entry with game version |

## Evolution Chain Fields

Returned by `pokecli pokemon evolution <name_or_id>`.

Displayed as a tree. Each node shows the species name and the condition required to evolve from the previous stage.

| Trigger | Example condition shown |
|---------|------------------------|
| `level-up` | `level 16`, `happiness 160`, `affection 2`, `knowing <move>`, `at <location>` |
| `use-item` | `use water-stone`, `use thunder-stone` |
| `trade` | `trade`, `trade holding metal-coat` |
| `shed` | `shed (level 20, empty slot, Pokeball)` |

Additional modifiers appended when present: `(day)`, `(night)`, `(rain)`, `(upside-down)`, `holding <item>`.

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

## Version Fields

Returned by `pokecli game version get <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Game version slug (e.g. `red`, `firered`, `sword`) |
| ID | Version identifier |
| Version Group | The group this version belongs to (e.g. `red-blue`, `sword-shield`) |

## Version Group Fields

Returned by `pokecli game version-group get <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Group slug (e.g. `red-blue`, `gold-silver`, `sword-shield`) |
| ID | Version group identifier |
| Order | Chronological order across all groups |
| Generation | Generation introduced alongside this region |
| Versions | Individual game versions in the group |
| Regions | In-game regions accessible in the group |

## Machine Fields

Returned by `pokecli game machine get <id>`.

| Field | Description |
|-------|-------------|
| ID | Machine identifier (TMs and HMs share the global counter) |
| Item | The TM/HM item (e.g. `tm01`, `hm03`) |
| Teaches Move | The move this machine teaches |
| Version Group | The game group in which this machine exists |

The same move can be taught by different machine IDs across version groups.

## Pokemon Form Fields

Returned by `pokecli pokemon form get <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Form name (e.g. `charizard-mega-x`, `vulpix-alola`, `pikachu-gmax`) |
| ID | Form identifier (mega/alolan/gigantamax forms start at 10000+) |
| Form Name | Short form suffix (e.g. `mega-x`, `alola`, `gmax`) |
| Base Pokemon | The species this form belongs to |
| Version Group | Version group that introduced the form |
| Default Form | `yes` if this is the species' default appearance |
| Battle Only | `yes` for transformations that revert after battle (Mega, Primal, Ultra) |
| Mega | `yes` for Mega Evolutions specifically |
| Types | Type(s) used while in this form |

## Pokemon Encounters Fields

Returned by `pokecli pokemon encounters <name_or_id>` (`/pokemon/{id}/encounters/`).

| Field | Description |
|-------|-------------|
| Location Area | The encounter area slug (e.g. `kanto-route-1-area`) |
| Version | Game version this encounter applies to |
| Method | Encounter method (`walk`, `surf`, `old-rod`, `gift`, `overworld-flying-special`, etc.) |
| Chance | Per-step encounter probability (0–100%) |
| Levels | Level range as `<min>` or `<min>-<max>` |

Rows are duplicated across versions; an agent should filter by version when answering version-specific questions.

## Pokemon Forms Fields

Returned by `pokecli pokemon forms <name_or_id>`. Sourced from the species `varieties[]` field.

| Field | Description |
|-------|-------------|
| Variety | The variety's pokemon slug (e.g. `charizard-mega-x`, `vulpix-alola`, `pikachu-gmax`) |
| Default | `yes` for the species' default variety; empty otherwise |
| Lookup URL | Direct PokeAPI URL; the slug feeds `pokecli pokemon form get <variety>` |

## Region Fields

Returned by `pokecli game region get <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Region slug (e.g. `kanto`, `johto`, `hoenn`, `paldea`) |
| ID | Region identifier |
| Main Generation | Generation introduced alongside this region |
| Pokedexes | Regional pokedex names (some regions have multiple) |
| Version Groups | Game version groups set in this region |
| Locations (inline table) | Every child location slug |

## Location Fields

Returned by `pokecli location get <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Location slug (e.g. `pallet-town`, `kanto-route-1`) |
| ID | Location identifier |
| Region | Parent region |
| Areas (inline table) | Every child location-area slug (the actual encounter spots) |

A `location` is a top-level place (city, route, dungeon). A `location-area` is a sub-zone within it that defines encounters.

## Location Area Fields

Returned by `pokecli location area get <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Area slug (e.g. `kanto-route-1-area`, `trophy-garden-area`) |
| ID | Area identifier |
| Location | Parent location |
| Game Index | Internal game ID |
| Pokemon Encounters (inline table) | Pokemon × version × method × chance × level range |

The encounter table has one row per (pokemon, version, encounter_detail) tuple, so a single Pokemon may appear many times for different conditions.

## Generation Fields

Returned by `pokecli game generation get <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Generation slug (e.g. `generation-i`, `generation-ix`) |
| ID | Generation identifier |
| Main Region | The region introduced with this generation |
| Pokemon Introduced | Count of new species this generation |
| Moves Introduced | Count of new moves this generation |
| Abilities Introduced | Count of new abilities (0 for Gen I/II) |
| Types Introduced | Count of new types (only Gen I introduced base types) |
| Version Groups | Game groups belonging to this generation |
| Pokemon Species (inline) | Sorted list of new species slugs |
| Moves (inline) | Sorted list of new move slugs |

## Pokedex Fields

Returned by `pokecli game pokedex get <name_or_id>`.

| Field | Description |
|-------|-------------|
| Name | Pokedex slug (e.g. `kanto`, `national`, `letsgo-kanto`, `paldea`) |
| ID | Pokedex identifier |
| Main Series | `yes` for main-series pokedexes, `no` for spin-offs |
| Region | Owning region (null for `national`) |
| Version Groups | Versions that use this pokedex |
| Entries (inline table) | `entry_number` + `pokemon_species` pairs, sorted by entry |

The `national` pokedex spans all generations; regional pokedexes are subsets.

## Evolution Chain Standalone

Returned by `pokecli pokemon evolution-chain get <id>`. Renders identically to
`pokecli pokemon evolution`, but accepts a chain ID directly. Use this when the
chain ID was extracted from another response (e.g. `pokemon species` returns
`evolution_chain.url`, whose trailing path segment is the chain ID).

## Cache Location

All cached responses are stored at `~/.pokecli/cache.json` using TinyDB.
Each entry is keyed by resource type and name/ID.

Tracked resource tables: `pokemon`, `berry`, `item`, `move`, `ability`, `nature`, `type`, `pokemon-species`, `evolution-chain`, `location`, `location-area`, `region`, `generation`, `version`, `version-group`, `pokedex`, `machine`, `pokemon-form`.

All tables are visible in `pokecli cache stats` and can be cleared individually with `pokecli cache clear --resource <table>`.

## Data Source

All data originates from [PokeAPI](https://pokeapi.co/api/v2).
No authentication required. Free and open.

## Related References

- `workflows.md` — multi-step recipes for traversing related resources (regional encounter lookup, TM tracing, full Pokemon profile).
