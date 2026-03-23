# pokecli

A command-line interface for querying Pokemon, Berries, Items, and Moves data from the [PokeAPI](https://pokeapi.co/api/v2). Results are displayed in formatted tables or raw JSON, and responses are cached locally to reduce redundant API calls.

## Features

- Query detailed information about Pokemon, Berries, Items, and Moves by name or ID
- Paginated listing for all resource types
- Download Pokemon sprite images in multiple variants
- Local response caching with TinyDB to minimize network requests
- Rich terminal output with color-coded tables and panels
- JSON output mode with syntax highlighting
- Cache inspection and management commands

## Requirements

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Installation

**Using uv:**

```bash
git clone https://github.com/jebucaro/PokeCli
cd pokecli
uv sync
uv run pokecli --help
```

**Using pip:**

```bash
git clone https://github.com/jebucaro/PokeCli
cd pokecli
pip install -e .
pokecli --help
```

## Configuration

The local cache is stored at `~/.pokecli/cache.json`. This file is created automatically on first use. No additional configuration is required.

## Output Formats

All `get` commands support two output formats via the `--format` option:

| Format | Description |
|--------|-------------|
| `table` | Rich formatted table output (default) |
| `json` | Raw JSON response with syntax highlighting |

```bash
pokecli pokemon get pikachu --format json
```

## Caching

Responses from the PokeAPI are cached locally after the first request. Subsequent requests for the same resource will be served from the cache without making a network call.

To bypass the cache and fetch fresh data from the API, use the `--no-cache` flag on any `get` command:

```bash
pokecli pokemon get pikachu --no-cache
```

---

## Commands

### `pokemon`

Search and browse Pokemon.

#### `pokemon get`

Retrieve detailed information about a Pokemon, including its types, stats, abilities, height, weight, and base experience.

```
pokecli pokemon get <name_or_id> [OPTIONS]
```

| Argument / Option | Type | Default | Description |
|-------------------|------|---------|-------------|
| `name_or_id` | string or int | required | Pokemon name or Pokedex number |
| `--no-cache` | flag | `False` | Skip local cache and fetch from API |
| `--format` | string | `table` | Output format: `table` or `json` |

**Examples:**

```bash
pokecli pokemon get pikachu
pokecli pokemon get 25
pokecli pokemon get charizard --format json
pokecli pokemon get bulbasaur --no-cache
```

#### `pokemon list`

List Pokemon with pagination.

```
pokecli pokemon list [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit` | int | `20` | Number of results per page |
| `--offset` | int | `0` | Number of results to skip |

**Examples:**

```bash
pokecli pokemon list
pokecli pokemon list --limit 50
pokecli pokemon list --limit 20 --offset 40
```

---

### `berry`

Search and browse Berries.

#### `berry get`

Retrieve detailed information about a Berry, including its growth time, harvest count, firmness, flavors, and natural gift properties.

```
pokecli berry get <name_or_id> [OPTIONS]
```

| Argument / Option | Type | Default | Description |
|-------------------|------|---------|-------------|
| `name_or_id` | string or int | required | Berry name or ID |
| `--no-cache` | flag | `False` | Skip local cache and fetch from API |
| `--format` | string | `table` | Output format: `table` or `json` |

**Examples:**

```bash
pokecli berry get cheri
pokecli berry get 1
pokecli berry get oran --format json
```

#### `berry list`

List Berries with pagination.

```
pokecli berry list [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit` | int | `20` | Number of results per page |
| `--offset` | int | `0` | Number of results to skip |

**Examples:**

```bash
pokecli berry list
pokecli berry list --limit 10
pokecli berry list --limit 10 --offset 20
```

---

### `item`

Search and browse Items.

#### `item get`

Retrieve detailed information about an Item, including its cost, category, fling power, effect, and flavor text.

```
pokecli item get <name_or_id> [OPTIONS]
```

| Argument / Option | Type | Default | Description |
|-------------------|------|---------|-------------|
| `name_or_id` | string or int | required | Item name or ID |
| `--no-cache` | flag | `False` | Skip local cache and fetch from API |
| `--format` | string | `table` | Output format: `table` or `json` |

**Examples:**

```bash
pokecli item get potion
pokecli item get 1
pokecli item get master-ball --format json
```

#### `item list`

List Items with pagination.

```
pokecli item list [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit` | int | `20` | Number of results per page |
| `--offset` | int | `0` | Number of results to skip |

**Examples:**

```bash
pokecli item list
pokecli item list --limit 30
pokecli item list --limit 30 --offset 60
```

---

### `move`

Search and browse Moves.

#### `move get`

Retrieve detailed information about a Move, including its type, damage class, power, accuracy, PP, effect chance, and effect description.

```
pokecli move get <name_or_id> [OPTIONS]
```

| Argument / Option | Type | Default | Description |
|-------------------|------|---------|-------------|
| `name_or_id` | string or int | required | Move name or ID |
| `--no-cache` | flag | `False` | Skip local cache and fetch from API |
| `--format` | string | `table` | Output format: `table` or `json` |

**Examples:**

```bash
pokecli move get thunderbolt
pokecli move get 24
pokecli move get surf --format json
pokecli move get flamethrower --no-cache
```

#### `move list`

List Moves with pagination.

```
pokecli move list [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit` | int | `20` | Number of results per page |
| `--offset` | int | `0` | Number of results to skip |

**Examples:**

```bash
pokecli move list
pokecli move list --limit 40
pokecli move list --limit 20 --offset 100
```

---

### `image`

Download Pokemon images and sprites.

#### `image download`

Download a Pokemon sprite to a local file. The output path must be specified.

```
pokecli image download <resource> <name_or_id> --output <path> [OPTIONS]
```

| Argument / Option | Type | Default | Description |
|-------------------|------|---------|-------------|
| `resource` | string | required | Resource type. Currently only `pokemon` is supported |
| `name_or_id` | string or int | required | Pokemon name or Pokedex number |
| `--output`, `-o` | path | required | Destination file path for the downloaded image |
| `--variant` | string | `front_default` | Sprite variant to download |

**Available sprite variants:**

| Variant | Description |
|---------|-------------|
| `front_default` | Front-facing default sprite (default) |
| `front_shiny` | Front-facing shiny sprite |
| `back_default` | Back-facing default sprite |
| `back_shiny` | Back-facing shiny sprite |
| `front_female` | Front-facing female sprite |
| `front_shiny_female` | Front-facing shiny female sprite |

**Examples:**

```bash
pokecli image download pokemon pikachu -o pikachu.png
pokecli image download pokemon pikachu -o pikachu_shiny.png --variant front_shiny
pokecli image download pokemon 6 -o charizard_back.png --variant back_default
pokecli image download pokemon 133 -o /tmp/eevee.png
```

---

### `cache`

Manage the local PokeAPI cache stored at `~/.pokecli/cache.json`.

#### `cache stats`

Display the number of cached entries per resource type.

```
pokecli cache stats
```

#### `cache clear`

Remove cached entries. Defaults to clearing all resources.

```
pokecli cache clear [OPTIONS]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--resource` | string | `all` | Resource to clear: `pokemon`, `berry`, `item`, `move`, or `all` |

**Examples:**

```bash
pokecli cache clear
pokecli cache clear --resource pokemon
pokecli cache clear --resource item
pokecli cache stats
```

---

## Data Source

All data is fetched from the [PokeAPI](https://pokeapi.co) (`https://pokeapi.co/api/v2`). The PokeAPI is a free, open API and does not require authentication.
