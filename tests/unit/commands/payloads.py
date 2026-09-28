"""Minimal valid API payloads, one per resource in the table.

Each payload carries only the fields its model requires, plus whatever a
renderer or TOON builder reads. Keeping them minimal means a new required field
on a model surfaces as a test failure rather than passing silently.
"""


def _named(name: str, resource: str = "x", ident: int = 1) -> dict:
    return {"name": name, "url": f"https://x/api/v2/{resource}/{ident}/"}


def _lang(text_key: str = "effect") -> dict:
    return {
        text_key: "Does a thing.",
        "short_effect": "Does a thing.",
        "language": _named("en", "language"),
    }


POKEMON = {
    "id": 25,
    "name": "pikachu",
    "height": 4,
    "weight": 60,
    "base_experience": 112,
    "types": [{"slot": 1, "type": _named("electric", "type", 13)}],
    "abilities": [
        {"slot": 1, "is_hidden": False, "ability": _named("static", "ability", 9)},
        {
            "slot": 3,
            "is_hidden": True,
            "ability": _named("lightning-rod", "ability", 31),
        },
    ],
    "stats": [
        {"base_stat": 35, "effort": 0, "stat": _named("hp", "stat", 1)},
        {"base_stat": 55, "effort": 0, "stat": _named("attack", "stat", 2)},
    ],
    "sprites": {
        "front_default": "https://img/25.png",
        "front_shiny": "https://img/25s.png",
        "front_female": None,
        "front_shiny_female": None,
    },
    "moves": [
        {
            "move": _named("thunderbolt", "move", 85),
            "version_group_details": [
                {
                    "level_learned_at": 0,
                    "move_learn_method": _named("machine", "move-learn-method", 4),
                    "version_group": _named("red-blue", "version-group", 1),
                }
            ],
        },
        {
            "move": _named("thunder-shock", "move", 84),
            "version_group_details": [
                {
                    "level_learned_at": 1,
                    "move_learn_method": _named("level-up", "move-learn-method", 1),
                    "version_group": _named("red-blue", "version-group", 1),
                }
            ],
        },
    ],
}

POKEMON_NO_MOVES = {**POKEMON, "name": "missingno", "moves": []}

POKEMON_SPECIES = {
    "id": 25,
    "name": "pikachu",
    "generation": _named("generation-i", "generation", 1),
    "color": _named("yellow", "pokemon-color", 10),
    "capture_rate": 190,
    "gender_rate": 4,
    "egg_groups": [_named("ground", "egg-group", 5)],
    "growth_rate": _named("medium", "growth-rate", 2),
    "evolution_chain": {"url": "https://x/api/v2/evolution-chain/10/"},
    "flavor_text_entries": [
        {
            "flavor_text": "It has small electric sacs.",
            "language": _named("en", "language"),
            "version": _named("red", "version", 1),
        }
    ],
    "genera": [{"genus": "Mouse Pokemon", "language": _named("en", "language")}],
    "is_legendary": False,
    "is_mythical": False,
    "varieties": [
        {"is_default": True, "pokemon": _named("pikachu", "pokemon", 25)},
        {"is_default": False, "pokemon": _named("pikachu-gmax", "pokemon", 10194)},
    ],
}

POKEMON_SPECIES_DEFAULT_ONLY = {
    **POKEMON_SPECIES,
    "name": "tauros",
    "varieties": [{"is_default": True, "pokemon": _named("tauros", "pokemon", 128)}],
}

POKEMON_FORM = {
    "id": 10034,
    "name": "charizard-mega-x",
    "order": 10,
    "form_order": 2,
    "is_default": False,
    "is_battle_only": True,
    "is_mega": True,
    "form_name": "mega-x",
    "pokemon": _named("charizard-mega-x", "pokemon", 10034),
    "version_group": _named("x-y", "version-group", 15),
    "types": [{"slot": 1, "type": _named("fire", "type", 10)}],
    "sprites": {"front_default": "https://img/10034.png"},
}

EVOLUTION_CHAIN = {
    "id": 2,
    "chain": {
        "species": _named("charmander", "pokemon-species", 4),
        "evolution_details": [],
        "evolves_to": [
            {
                "species": _named("charmeleon", "pokemon-species", 5),
                "evolution_details": [
                    {"trigger": _named("level-up", "evolution-trigger", 1), "min_level": 16}
                ],
                "evolves_to": [],
            }
        ],
    },
}

EVOLUTION_CHAIN_SINGLE = {
    "id": 99,
    "chain": {
        "species": _named("tauros", "pokemon-species", 128),
        "evolution_details": [],
        "evolves_to": [],
    },
}

MOVE = {
    "id": 85,
    "name": "thunderbolt",
    "accuracy": 100,
    "power": 90,
    "pp": 15,
    "type": _named("electric", "type", 13),
    "damage_class": _named("special", "move-damage-class", 3),
    "effect_entries": [_lang()],
}

ITEM = {
    "id": 1,
    "name": "master-ball",
    "cost": 0,
    "category": _named("standard-balls", "item-category", 34),
    "effect_entries": [_lang()],
    "flavor_text_entries": [
        {
            "text": "The best ball.",
            "language": _named("en", "language"),
            "version_group": _named("red-blue", "version-group", 1),
        }
    ],
}

ABILITY = {
    "id": 22,
    "name": "intimidate",
    "generation": _named("generation-iii", "generation", 3),
    "effect_entries": [_lang()],
    "pokemon": [{"is_hidden": False, "pokemon": _named("gyarados", "pokemon", 130)}],
}

TYPE = {
    "id": 10,
    "name": "fire",
    "damage_relations": {
        "no_damage_to": [],
        "half_damage_to": [_named("water", "type", 11)],
        "double_damage_to": [_named("grass", "type", 12)],
        "no_damage_from": [],
        "half_damage_from": [],
        "double_damage_from": [_named("water", "type", 11)],
    },
    "pokemon": [{"slot": 1, "pokemon": _named("charmander", "pokemon", 4)}],
    "moves": [_named("ember", "move", 52)],
}

NATURE = {
    "id": 1,
    "name": "modest",
    "increased_stat": _named("special-attack", "stat", 4),
    "decreased_stat": _named("attack", "stat", 2),
}

BERRY = {
    "id": 1,
    "name": "cheri",
    "growth_time": 3,
    "max_harvest": 5,
    "natural_gift_power": 60,
    "flavors": [{"potency": 10, "flavor": _named("spicy", "berry-flavor", 1)}],
    "item": _named("cheri-berry", "item", 126),
    "firmness": _named("soft", "berry-firmness", 2),
    "natural_gift_type": _named("fire", "type", 10),
    "size": 20,
    "smoothness": 25,
}

LOCATION = {
    "id": 1,
    "name": "canalave-city",
    "region": _named("sinnoh", "region", 4),
    "areas": [_named("canalave-city-area", "location-area", 1)],
}

LOCATION_NO_AREAS = {**LOCATION, "name": "empty-place", "areas": []}

LOCATION_AREA = {
    "id": 1,
    "name": "canalave-city-area",
    "game_index": 1,
    "location": _named("canalave-city", "location", 1),
    "encounter_method_rates": [],
    "pokemon_encounters": [
        {
            "pokemon": _named("tentacool", "pokemon", 72),
            "version_details": [],
        }
    ],
}

REGION = {
    "id": 1,
    "name": "kanto",
    "main_generation": _named("generation-i", "generation", 1),
    "locations": [_named("pallet-town", "location", 1)],
    "pokedexes": [_named("kanto", "pokedex", 2)],
    "version_groups": [_named("red-blue", "version-group", 1)],
}

GENERATION = {
    "id": 1,
    "name": "generation-i",
    "main_region": _named("kanto", "region", 1),
    "pokemon_species": [_named("bulbasaur", "pokemon-species", 1)],
    "moves": [_named("pound", "move", 1)],
    "types": [_named("normal", "type", 1)],
    "version_groups": [_named("red-blue", "version-group", 1)],
}

VERSION = {
    "id": 1,
    "name": "red",
    "version_group": _named("red-blue", "version-group", 1),
}

VERSION_GROUP = {
    "id": 1,
    "name": "red-blue",
    "order": 1,
    "generation": _named("generation-i", "generation", 1),
    "versions": [_named("red", "version", 1)],
    "regions": [_named("kanto", "region", 1)],
}

POKEDEX = {
    "id": 2,
    "name": "kanto",
    "is_main_series": True,
    "descriptions": [],
    "pokemon_entries": [
        {"entry_number": 1, "pokemon_species": _named("bulbasaur", "pokemon-species", 1)}
    ],
}

MACHINE = {
    "id": 79,
    "item": _named("tm24", "item", 313),
    "move": _named("thunderbolt", "move", 85),
    "version_group": _named("red-blue", "version-group", 1),
}


#: Payload per resource name, matching the resource table's vocabulary.
BY_RESOURCE: dict[str, dict] = {
    "pokemon": POKEMON,
    "pokemon-species": POKEMON_SPECIES,
    "pokemon-form": POKEMON_FORM,
    "evolution-chain": EVOLUTION_CHAIN,
    "move": MOVE,
    "item": ITEM,
    "ability": ABILITY,
    "type": TYPE,
    "nature": NATURE,
    "berry": BERRY,
    "location": LOCATION,
    "location-area": LOCATION_AREA,
    "region": REGION,
    "generation": GENERATION,
    "version": VERSION,
    "version-group": VERSION_GROUP,
    "pokedex": POKEDEX,
    "machine": MACHINE,
}
