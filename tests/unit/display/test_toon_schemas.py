"""Tests for TOON schema transforms."""


from pokecli.display.toon_schemas import (
    pokemon_toon,
    move_toon,
    ability_toon,
    item_toon,
    type_toon,
    nature_toon,
    location_toon,
    region_toon,
    machine_toon,
    evolution_chain_toon,
    pokemon_moves_toon,
    encounters_toon,
    resource_list_toon,
)
from pokecli.models.pokemon import (
    Pokemon,
    PokemonType,
    PokemonAbility,
    PokemonStat,
    PokemonSprites,
    PokemonMoveEntry,
)
from pokecli.models.move import Move, MoveEffectEntry
from pokecli.models.ability import Ability, AbilityEffect
from pokecli.models.item import Item, ItemEffect
from pokecli.models.evolution import EvolutionChain, ChainLink, EvolutionDetail
from pokecli.models.location import Location, Region
from pokecli.models.common import NamedResource, ListResult
from pokecli.models.nature import Nature
from pokecli.models.type import PokemonType as TypeModel, TypeDamageRelations
from pokecli.models.machine import Machine


def _nr(name: str, url: str = "https://pokeapi.co/api/v2/test/1/") -> NamedResource:
    """Helper to create NamedResource."""
    return NamedResource(name=name, url=url)


class TestPokemonToon:
    """Tests for pokemon_toon."""

    def test_produces_correct_fields(self):
        pokemon = Pokemon(
            id=25,
            name="pikachu",
            height=4,
            weight=60,
            base_experience=112,
            types=[
                PokemonType(slot=1, type=_nr("electric")),
            ],
            abilities=[
                PokemonAbility(slot=1, is_hidden=False, ability=_nr("static")),
                PokemonAbility(slot=2, is_hidden=True, ability=_nr("lightning-rod")),
            ],
            stats=[
                PokemonStat(base_stat=35, effort=0, stat=_nr("hp")),
                PokemonStat(base_stat=55, effort=0, stat=_nr("attack")),
                PokemonStat(base_stat=40, effort=0, stat=_nr("defense")),
                PokemonStat(base_stat=50, effort=0, stat=_nr("special-attack")),
                PokemonStat(base_stat=50, effort=0, stat=_nr("special-defense")),
                PokemonStat(base_stat=90, effort=2, stat=_nr("speed")),
            ],
            sprites=PokemonSprites(front_default="https://example.com/pikachu.png"),
        )

        fields = pokemon_toon(pokemon)

        assert fields["id"] == 25
        assert fields["name"] == "pikachu"
        assert fields["types"] == "electric"
        assert fields["abilities"] == "static/lightning-rod(H)"
        assert fields["stats"] == "hp:35/atk:55/def:40/spa:50/spd:50/spe:90"

    def test_multiple_types(self):
        pokemon = Pokemon(
            id=6,
            name="charizard",
            height=17,
            weight=905,
            base_experience=267,
            types=[
                PokemonType(slot=1, type=_nr("fire")),
                PokemonType(slot=2, type=_nr("flying")),
            ],
            abilities=[
                PokemonAbility(slot=1, is_hidden=False, ability=_nr("blaze")),
            ],
            stats=[
                PokemonStat(base_stat=78, effort=0, stat=_nr("hp")),
                PokemonStat(base_stat=84, effort=0, stat=_nr("attack")),
                PokemonStat(base_stat=78, effort=0, stat=_nr("defense")),
                PokemonStat(base_stat=109, effort=3, stat=_nr("special-attack")),
                PokemonStat(base_stat=85, effort=0, stat=_nr("special-defense")),
                PokemonStat(base_stat=100, effort=0, stat=_nr("speed")),
            ],
            sprites=PokemonSprites(),
        )

        fields = pokemon_toon(pokemon)

        assert fields["types"] == "fire/flying"


class TestMoveToon:
    """Tests for move_toon."""

    def test_produces_correct_fields(self):
        move = Move(
            id=85,
            name="thunderbolt",
            accuracy=100,
            power=90,
            pp=15,
            type=_nr("electric"),
            damage_class=_nr("special"),
            effect_entries=[
                MoveEffectEntry(
                    effect="Has a $effect_chance% chance to paralyze.",
                    short_effect="Has a $effect_chance% chance to paralyze the target.",
                    language=_nr("en"),
                ),
            ],
            effect_chance=10,
        )

        fields = move_toon(move)

        assert fields["id"] == 85
        assert fields["name"] == "thunderbolt"
        assert fields["type"] == "electric"
        assert fields["class"] == "special"
        assert fields["power"] == 90
        assert fields["accuracy"] == 100
        assert fields["pp"] == 15
        assert fields["effect"] == "Has a 10% chance to paralyze the target."

    def test_none_power_and_accuracy(self):
        move = Move(
            id=45,
            name="growl",
            accuracy=100,
            power=None,
            pp=40,
            type=_nr("normal"),
            damage_class=_nr("status"),
            effect_entries=[],
            effect_chance=None,
        )

        fields = move_toon(move)

        assert fields["power"] is None
        assert fields["effect"] is None


class TestAbilityToon:
    """Tests for ability_toon."""

    def test_produces_correct_fields(self):
        ability = Ability(
            id=22,
            name="intimidate",
            generation=_nr("generation-iii"),
            effect_entries=[
                AbilityEffect(
                    effect="Long effect text.",
                    short_effect="Lowers opponents' Attack one stage on entering battle.",
                    language=_nr("en"),
                ),
            ],
            pokemon=[{"pokemon": {"name": "arcanine"}}, {"pokemon": {"name": "gyarados"}}],
        )

        fields = ability_toon(ability)

        assert fields["id"] == 22
        assert fields["name"] == "intimidate"
        assert fields["generation"] == "generation-iii"
        assert fields["pokemon_count"] == 2
        assert "Lowers opponents" in fields["effect"]


class TestItemToon:
    """Tests for item_toon."""

    def test_produces_correct_fields(self):
        item = Item(
            id=1,
            name="master-ball",
            cost=0,
            fling_power=None,
            category=_nr("standard-balls"),
            effect_entries=[
                ItemEffect(
                    effect="Long description.",
                    short_effect="Catches a wild Pokemon without fail.",
                    language=_nr("en"),
                ),
            ],
            flavor_text_entries=[],
        )

        fields = item_toon(item)

        assert fields["id"] == 1
        assert fields["name"] == "master-ball"
        assert fields["cost"] == 0
        assert fields["category"] == "standard-balls"
        assert "Catches a wild" in fields["effect"]


class TestResourceListToon:
    """Tests for resource_list_toon."""

    def test_produces_list_of_dicts(self):
        result = ListResult(
            count=1010,
            next="https://pokeapi.co/api/v2/pokemon?offset=20&limit=20",
            previous=None,
            results=[
                _nr("bulbasaur"),
                _nr("ivysaur"),
                _nr("venusaur"),
            ],
        )

        rows = resource_list_toon(result)

        assert rows == [
            {"name": "bulbasaur"},
            {"name": "ivysaur"},
            {"name": "venusaur"},
        ]

    def test_empty_results(self):
        result = ListResult(
            count=0,
            next=None,
            previous=None,
            results=[],
        )

        rows = resource_list_toon(result)

        assert rows == []


class TestPokemonMovesToon:
    """Tests for pokemon_moves_toon."""

    def test_produces_uniform_rows(self):
        moves = [
            PokemonMoveEntry(name="thunderbolt", learn_method="level-up", level=26),
            PokemonMoveEntry(name="thunder", learn_method="machine", level=0),
        ]

        rows = pokemon_moves_toon("pikachu", moves)

        assert rows[0] == {"name": "thunderbolt", "method": "level-up", "level": 26}
        assert rows[1] == {"name": "thunder", "method": "machine", "level": None}


class TestEncountersToon:
    """Tests for encounters_toon."""

    def test_produces_uniform_rows(self):
        encounters = [
            {
                "location_area": {"name": "viridian-forest-area"},
                "version_details": [
                    {
                        "version": {"name": "red"},
                        "max_chance": 5,
                        "encounter_details": [
                            {
                                "method": {"name": "walk"},
                                "chance": 5,
                                "min_level": 3,
                                "max_level": 5,
                            }
                        ],
                    }
                ],
            }
        ]

        rows = encounters_toon("pikachu", encounters)

        assert rows[0] == {
            "area": "viridian-forest-area",
            "version": "red",
            "method": "walk",
            "chance": "5%",
            "levels": "3-5",
        }

    def test_same_level_range(self):
        encounters = [
            {
                "location_area": {"name": "area-1"},
                "version_details": [
                    {
                        "version": {"name": "blue"},
                        "max_chance": 10,
                        "encounter_details": [
                            {
                                "method": {"name": "walk"},
                                "chance": 10,
                                "min_level": 5,
                                "max_level": 5,
                            }
                        ],
                    }
                ],
            }
        ]

        rows = encounters_toon("pikachu", encounters)
        assert rows[0]["levels"] == "5"


class TestEvolutionChainToon:
    """Tests for evolution_chain_toon."""

    def test_renders_simple_chain(self):
        chain = EvolutionChain(
            id=1,
            chain=ChainLink(
                species=_nr("bulbasaur"),
                evolution_details=[],
                evolves_to=[
                    ChainLink(
                        species=_nr("ivysaur"),
                        evolution_details=[
                            EvolutionDetail(
                                trigger=_nr("level-up"),
                                min_level=16,
                            )
                        ],
                        evolves_to=[
                            ChainLink(
                                species=_nr("venusaur"),
                                evolution_details=[
                                    EvolutionDetail(
                                        trigger=_nr("level-up"),
                                        min_level=32,
                                    )
                                ],
                                evolves_to=[],
                            )
                        ],
                    )
                ],
            ),
        )

        label, node = evolution_chain_toon(chain)

        assert label == "evolution_chain_1"
        assert node["name"] == "bulbasaur"
        assert node["trigger"] is None
        ivysaur = node["evolves_to"][0]
        assert ivysaur["name"] == "ivysaur"
        assert ivysaur["trigger"] == "level 16"
        venusaur = ivysaur["evolves_to"][0]
        assert venusaur["name"] == "venusaur"
        assert venusaur["trigger"] == "level 32"

    def test_branching_chain(self):
        chain = EvolutionChain(
            id=67,
            chain=ChainLink(
                species=_nr("eevee"),
                evolution_details=[],
                evolves_to=[
                    ChainLink(
                        species=_nr("vaporeon"),
                        evolution_details=[
                            EvolutionDetail(
                                trigger=_nr("use-item"),
                                item=_nr("water-stone"),
                            )
                        ],
                        evolves_to=[],
                    ),
                    ChainLink(
                        species=_nr("jolteon"),
                        evolution_details=[
                            EvolutionDetail(
                                trigger=_nr("use-item"),
                                item=_nr("thunder-stone"),
                            )
                        ],
                        evolves_to=[],
                    ),
                ],
            ),
        )

        label, node = evolution_chain_toon(chain)

        assert label == "evolution_chain_67"
        assert node["name"] == "eevee"
        children = node["evolves_to"]
        assert children[0]["name"] == "vaporeon"
        assert children[0]["trigger"] == "use water stone"
        assert children[1]["name"] == "jolteon"
        assert children[1]["trigger"] == "use thunder stone"


class TestTypeToon:
    """Tests for type_toon."""

    def test_produces_correct_fields(self):
        type_data = TypeModel(
            id=10,
            name="fire",
            damage_relations=TypeDamageRelations(
                double_damage_to=[_nr("grass"), _nr("ice")],
                half_damage_to=[_nr("water"), _nr("rock")],
                no_damage_to=[],
                double_damage_from=[_nr("water"), _nr("ground")],
                half_damage_from=[_nr("grass"), _nr("fire")],
                no_damage_from=[],
            ),
            pokemon=[],
            moves=[],
        )

        fields = type_toon(type_data)

        assert fields["id"] == 10
        assert fields["name"] == "fire"
        assert fields["double_damage_to"] == "grass/ice"
        assert fields["half_damage_to"] == "water/rock"
        assert fields["no_damage_to"] is None
        assert fields["double_damage_from"] == "water/ground"


class TestNatureToon:
    """Tests for nature_toon."""

    def test_produces_correct_fields(self):
        nature = Nature(
            id=1,
            name="adamant",
            increased_stat=_nr("attack"),
            decreased_stat=_nr("special-attack"),
            likes_flavor=_nr("spicy"),
            hates_flavor=_nr("dry"),
        )

        fields = nature_toon(nature)

        assert fields["id"] == 1
        assert fields["name"] == "adamant"
        assert fields["increased_stat"] == "attack"
        assert fields["decreased_stat"] == "special-attack"
        assert fields["likes_flavor"] == "spicy"
        assert fields["hates_flavor"] == "dry"

    def test_neutral_nature(self):
        nature = Nature(
            id=10,
            name="hardy",
            increased_stat=None,
            decreased_stat=None,
            likes_flavor=None,
            hates_flavor=None,
        )

        fields = nature_toon(nature)

        assert fields["increased_stat"] is None
        assert fields["decreased_stat"] is None


class TestMachineToon:
    """Tests for machine_toon."""

    def test_produces_correct_fields(self):
        machine = Machine(
            id=1,
            item=_nr("tm01"),
            move=_nr("mega-punch"),
            version_group=_nr("red-blue"),
        )

        fields = machine_toon(machine)

        assert fields["id"] == 1
        assert fields["item"] == "tm01"
        assert fields["move"] == "mega-punch"
        assert fields["version_group"] == "red-blue"


class TestRegionToon:
    """Tests for region_toon."""

    def test_produces_correct_fields(self):
        region = Region(
            id=1,
            name="kanto",
            main_generation=_nr("generation-i"),
            locations=[_nr("pallet-town"), _nr("viridian-city")],
            pokedexes=[_nr("kanto")],
        )

        fields = region_toon(region)

        assert fields["id"] == 1
        assert fields["name"] == "kanto"
        assert fields["main_generation"] == "generation-i"
        assert fields["locations_count"] == 2
        assert fields["pokedexes"] == "kanto"


class TestLocationToon:
    """Tests for location_toon."""

    def test_produces_correct_fields(self):
        location = Location(
            id=1,
            name="canalave-city",
            region=_nr("sinnoh"),
            areas=[_nr("canalave-city-area")],
        )

        fields = location_toon(location)

        assert fields["id"] == 1
        assert fields["name"] == "canalave-city"
        assert fields["region"] == "sinnoh"
        assert fields["areas"] == 1
