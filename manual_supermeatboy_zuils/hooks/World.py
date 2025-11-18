# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item, ItemClassification

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat

from dataclasses import dataclass

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

import re

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################

@dataclass
class GameConfig:
    goal: int
    bandages: bool
    boss_amount: int
    boss_req: int
    dark_world: bool
    dw_drfetus_amount: int
    dw_drfetus_req: int
    chapter_seven: bool
    starting_chpt: int
    starting_char: int
    achievements: bool
    deathless: bool
    speedrun: bool
    xmas: bool

def initalize_globals(world: World, multiworld: MultiWorld, player: int) -> GameConfig:
    if hasattr(world, "_config_cache") and player in world._config_cache:
        return world._config_cache[player]
    
    goal = get_option_value(multiworld, player, "Goal")
    bandages = is_option_enabled(multiworld, player, "bandages")
    boss_amount = get_option_value(multiworld, player, "boss_amount")
    boss_req = min(boss_amount, get_option_value(multiworld, player, "boss_req"))
    dark_world = is_option_enabled(multiworld, player, "dark_world") or goal in (1, 3)
    dw_drfetus_amount = get_option_value(multiworld, player, "dw_drfetus_amount")
    chapter_seven = is_option_enabled(multiworld, player, "chapter_seven") or goal >= 2
    starting_chpt = get_option_value(multiworld, player, "starting_chapter")
    starting_char = get_option_value(multiworld, player, "starting_character")
    achievements = is_option_enabled(multiworld, player, "achievements")
    deathless = is_option_enabled(multiworld, player, "deathless")
    speedrun = is_option_enabled(multiworld, player, "speedrun")
    xmas = is_option_enabled(multiworld, player, "xmas")

    if dark_world and dw_drfetus_amount > 105 and not chapter_seven:
        logging.info("Chapter 7 is not enabled or goal is to beat lw/dw chpt 7. Setting DW Dr. Fetus amount to 105.")
        dw_drfetus_amount = 105
        world.options.dw_drfetus_amount.value = 105

    dw_drfetus_req = min(dw_drfetus_amount, get_option_value(multiworld, player, "dw_drfetus_req"))

    if starting_chpt == 7 and (not chapter_seven or goal in (2, 3)):
        logging.info("Starting Chapter is 7 yet chapter seven levels are off or goal is to beat lw/dw chpt 7, selecting 1-6 at random")
        starting_chpt = multiworld.random.randint(1, 6)
        world.options.starting_chapter.value = starting_chpt

    if bandages and starting_chpt != 1:
        logging.info("Bandages is on, setting starting chapter to 1")
        starting_chpt = 1
        world.options.starting_chapter.value = 1

    if (starting_chpt == 6 or bandages) and starting_char != 0:
        logging.info("Starting chapter is 6 or bandages is on, setting starting character to meat boy")
        starting_char = 0
        world.options.starting_character.value = 0

    if starting_chpt == 7 and starting_char != 8:
        logging.info("Starting chapter is 7, forcing starting character to be bandage girl")
        starting_char = 8
        world.options.starting_character.value = 8

    if starting_char == 8 and starting_chpt != 7:
        logging.info("Starting character is bandage girl yet starting chapter is not 7, selecting a random character")
        if starting_chpt == 6:
            starting_char = 0
        else:
            starting_char = multiworld.random.randint(0, 7)
        world.options.starting_character.value = starting_char

    cfg = GameConfig(
        goal=goal,
        bandages=bandages,
        boss_amount=boss_amount,
        boss_req=boss_req,
        dark_world=dark_world,
        dw_drfetus_amount=dw_drfetus_amount,
        dw_drfetus_req=dw_drfetus_req,
        chapter_seven=chapter_seven,
        starting_chpt=starting_chpt,
        starting_char=starting_char,
        achievements=achievements,
        deathless=deathless,
        speedrun=speedrun,
        xmas=xmas
    )
    
    if not hasattr(world, "_config_cache"):
        world._config_cache = {}
    world._config_cache[player] = cfg

    return cfg


# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    cfg: GameConfig = initalize_globals(world, multiworld, player)
    if not cfg.bandages:
        return "Bandage"

    return False

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    cfg: GameConfig = initalize_globals(world, multiworld, player)
    locationNamesToRemove: list[str] = []  # List of location names

    # Add your code here to calculate which locations to remove
    if not cfg.dark_world:
        locationNamesToRemove.extend(
            i["name"] for i in location_table if any("DW" in category for category in i.get("category", [])) \
                or "Dark World" in i["name"])
        locationNamesToRemove.extend(
            i["name"] for i in location_table if "Achievements (Speedrun)" in i.get("category", []))
        locationNamesToRemove.append("MS PAINT RULZ! (Collect 70 Bandages)")
        locationNamesToRemove.append("Vx6 (Collect 90 Bandages)")
        locationNamesToRemove.append("Accidental Arsonist (Collect 100 Bandages)")
        locationNamesToRemove.append("Old School (Complete 10 retro warp zones)")
        locationNamesToRemove.append("Retro Rampage (Complete all retro warp zones)")
        
    if not cfg.chapter_seven:
        locationNamesToRemove.extend(i["name"] for i in location_table if i.get("region") == "Chapter 7")
        
    if not cfg.achievements:
        locationNamesToRemove.extend(
            i["name"] for i in location_table if "Achievements" in i.get("category", []))

    if not cfg.deathless:
        locationNamesToRemove.extend(
            i["name"] for i in location_table if "Achievements (Deathless)" in i.get("category", []))

    if not cfg.speedrun:
        locationNamesToRemove.extend(
            i["name"] for i in location_table if "Achievements (Speedrun)" in i.get("category", []))

    if not cfg.xmas:
        locationNamesToRemove.extend(
            i["name"] for i in location_table if "xmas" in i.get("category", []))
        
    if not cfg.bandages:
        locationNamesToRemove.extend(i["name"] for i in location_table if "Bandage" in i["name"])

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)

# This hook allows you to access the item names & counts before the items are created. Use this to increase/decrease the amount of a specific item in the pool
# Valid item_config key/values:
# {"Item Name": 5} <- This will create qty 5 items using all the default settings
# {"Item Name": {"useful": 7}} <- This will create qty 7 items and force them to be classified as useful
# {"Item Name": {"progression": 2, "useful": 1}} <- This will create 3 items, with 2 classified as progression and 1 as useful
# {"Item Name": {0b0110: 5}} <- If you know the special flag for the item classes, you can also define non-standard options. This setup
#       will create 5 items that are the "useful trap" class
# {"Item Name": {ItemClassification.useful: 5}} <- You can also use the classification directly
def before_create_items_all(item_config: dict[str, int|dict], world: World, multiworld: MultiWorld, player: int) -> dict[str, int|dict]:
    cfg: GameConfig = initalize_globals(world, multiworld, player)
    item_config["DW Dr. Fetus Key"] = {ItemClassification.progression_deprioritized_skip_balancing if cfg.dw_drfetus_req > 0 else "filler": cfg.dw_drfetus_amount}
    for i in range(1, 6):
        item_config[f"Chapter {i} LW Level Key"] = {ItemClassification.progression_deprioritized if cfg.boss_req > 0 else "filler": cfg.boss_amount}
    return item_config

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    cfg: GameConfig = initalize_globals(world, multiworld, player)
    chars = [
        "4bit/4color/8bit/Normal Meat Boy",
        "Commander Video",
        "Jill",
        "Ogmo",
        "Flywrench",
        "The Kid",
        "Naija",
        "Steve",
        "Bandage Girl"
    ]

    char = next(i for i in item_pool if i.name == chars[cfg.starting_char])

    if not cfg.bandages:            
        chpt = next(i for i in item_pool if i.name == f"Chapter {cfg.starting_chpt} Key")
        multiworld.push_precollected(chpt)
        item_pool.remove(chpt)
    
    multiworld.push_precollected(char)
    item_pool.remove(char)
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    cfg: GameConfig = initalize_globals(world, multiworld, player)
    # Use this hook to remove items from the item pool
    itemNamesToRemove: list[str] = []  # List of item names

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.
    
    if not cfg.dark_world:
        itemNamesToRemove.extend("DW Dr. Fetus Key" for _ in range(cfg.dw_drfetus_amount))
    
    if cfg.bandages:
        itemNamesToRemove.extend(f"Chapter {i} Key" for i in range(1, 8))
    else:
        itemNamesToRemove.extend("Bandage" for _ in range(100))

    if cfg.goal != 3:
        itemNamesToRemove.extend("Chapter 7 DW Key" for _ in range(20))

    if cfg.goal == 0:
        location = next(l for l in multiworld.get_unfilled_locations(player) if l.name == "6-Boss LW Dr. Fetus")
        item = next(i for i in item_pool if i.name == "Victory")
        location.place_locked_item(item)
        item_pool.remove(item)
    elif cfg.goal == 1:
        location = next(l for l in multiworld.get_unfilled_locations(player) if l.name == "6-Boss DW Dr. Fetus")
        item = next(i for i in item_pool if i.name == "Victory")
        location.place_locked_item(item)
        item_pool.remove(item)

    if cfg.goal == 2:
        itemNamesToRemove.append("Victory")
        # all patterns that are 7-<num> Level Name (excludes A+ Ranks)
        pattern = re.compile(rf"^7-\d+\b(?!X).*?(?<!\(A\+ Rank\))$")
        for _ in range(20):
            location = next(l for l in multiworld.get_unfilled_locations(player) if pattern.match(l.name))
            item = next(i for i in item_pool if i.name == "Chapter 7 LW Level Key")
            location.place_locked_item(item)
            item_pool.remove(item)

    if cfg.goal == 3:
        itemNamesToRemove.append("Victory")
        # all patterns that are 7-<num>X Level Name (excludes A+ Ranks)
        pattern = re.compile(rf"^7-\d+X\b(?!.*\(A\+ Rank\))")
        for _ in range(20):
            location = next(l for l in multiworld.get_unfilled_locations(player) if pattern.match(l.name))
            item = next(i for i in item_pool if i.name == "Chapter 7 DW Level Key")
            location.place_locked_item(item)
            item_pool.remove(item)

    if not cfg.chapter_seven:
        itemNamesToRemove.extend("Chapter 7 LW Level Key" for _ in range(20))
        itemNamesToRemove.append("Bandage Girl")
        itemNamesToRemove.extend(f"7-{i} A+ Rank" for i in range(1, 21))
        if not cfg.bandages:
            itemNamesToRemove.append("Chapter 7 Key")

    for itemName in itemNamesToRemove:
        try:
            item = next(i for i in item_pool if i.name == itemName)
            item_pool.remove(item)
        except StopIteration:
            print(f"Item '{itemName}' not found in item pool.")
            raise StopIteration

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # item_pool.remove(item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    cfg: GameConfig = initalize_globals(world, multiworld, player)
    if cfg.goal != 2:
        for i in item_pool:
            if i.name == "Chapter 7 LW Level Key":
                i.classification = ItemClassification.filler
    
    if cfg.bandages:
        for i in item_pool:
            if i.name == "Bandage":
                i.classification = ItemClassification.progression_deprioritized_skip_balancing

    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    cfg: GameConfig = initalize_globals(world, multiworld, player)
    # Use this hook to modify the access rules for a given location
    # Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    # Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)
    
    def lwDrFetus(state: CollectionState) -> bool:
        if cfg.bandages:
            return state.can_reach_location("5-Boss Larries Lament", player) and \
                state.has("Chapter 6 LW Level Key", player, 5)
        else:
            if cfg.goal == 0:
                return state.has_all([f"Chapter {i} Key" for i in range(1, 7)], player) and \
                    state.has("Chapter 6 LW Level Key", player, 5)
            else:
                return state.has("Chapter 6 Key", player) and state.has("Chapter 6 LW Level Key", player, 5)

    def dwDrFetus(state: CollectionState) -> bool:
        if cfg.bandages:
            return state.can_reach_location("5-Boss Larries Lament", player) and \
                state.has("DW Dr. Fetus Key", player, cfg.dw_drfetus_req) and darkZoneAccess(cfg.dw_drfetus_req, state)
        else:
            if cfg.goal == 1:
                return state.has_all([f"Chapter {i} Key" for i in range(1, 7)], player) and \
                    state.has("DW Dr. Fetus Key", player, cfg.dw_drfetus_req)
            else:
                return state.has("Chapter 6 Key", player) and \
                    state.has("DW Dr. Fetus Key", player, cfg.dw_drfetus_req)

    def warpZones(req: int, state: CollectionState) -> bool:
        counter = 0
        if state.can_reach_location("1-1 Hello World", player):
            counter += 2
            if cfg.dark_world:
                counter += state.has("1-13 A+ Rank", player)
        if state.can_reach_location("1-Boss Lil' Slugger", player):
            counter += 2
            if cfg.dark_world:
                counter += state.has("2-5 A+ Rank", player)
        if state.can_reach_location("2-Boss C.H.A.D", player):
            counter += 1
            if cfg.dark_world:
                counter += state.can_reach_location("3-7WZ Tunnel Vision", player)
                counter += state.has("3-8 A+ Rank", player)
        if state.can_reach_location("3-Boss Brownie", player):
            counter += 2
            if cfg.dark_world:
                counter += state.can_reach_location("4-7XWZ MMMMMM", player)
        if state.can_reach_location("4-Boss Little Horn", player):
            counter += 2
            if cfg.dark_world:
                counter += state.has("5-20 A+ Rank", player)

        return counter >= req

    def bandagesAmount(req: int, state: CollectionState) -> bool:
        counter = 0
        if state.can_reach_location("1-1 Hello World", player):
            counter += 11
            if cfg.dark_world:
                counter += (
                    state.has("1-3 A+ Rank", player)
                    + state.has("1-5 A+ Rank", player)
                    + state.has("1-10 A+ Rank", player)
                    + (state.has("1-13 A+ Rank", player) * 2)
                    + state.has("1-14 A+ Rank", player)
                    + state.has("1-15 A+ Rank", player)
                    + state.has("1-17 A+ Rank", player)
                    + state.has("1-19 A+ Rank", player)
                )
        if state.can_reach_location("1-Boss Lil' Slugger", player):
            counter += 11
            if cfg.dark_world:
                counter += (
                    state.has("2-4 A+ Rank", player)
                    + (state.has("2-5 A+ Rank", player) * 2)
                    + state.has("2-6 A+ Rank", player)
                    + state.has("2-7 A+ Rank", player)
                    + state.has("2-10 A+ Rank", player)
                    + state.has("2-12 A+ Rank", player)
                    + state.has("2-15 A+ Rank", player)
                    + state.has("2-16 A+ Rank", player)
                )
        if state.can_reach_location("2-Boss C.H.A.D", player):
            counter += 8
            if cfg.dark_world:
                counter += (
                    (state.can_reach_location("3-7WZ Tunnel Vision", player) * 2)
                    + state.can_reach_location("3-4 Bandage", player)
                    + state.has("3-3 A+ Rank", player)
                    + state.has("3-5 A+ Rank", player)
                    + state.has("3-6 A+ Rank", player)
                    + state.has("3-7 A+ Rank", player)
                    + (state.has("3-8 A+ Rank", player) * 2)
                    + state.can_reach_location("3-14X Bandage", player)
                    + state.has("3-16 A+ Rank", player)
                    + state.has("3-19 A+ Rank", player)
                )
        if state.can_reach_location("3-Boss Brownie", player):
            counter += 11
            if cfg.dark_world:
                counter += (
                    state.has("4-3 A+ Rank", player)
                    + state.has("4-4 A+ Rank", player)
                    + (state.can_reach_location("4-7XWZ MMMMMM", player) * 2)
                    + state.has("4-8 A+ Rank", player)
                    + state.has("4-10 A+ Rank", player)
                    + state.has("4-14 A+ Rank", player)
                    + state.has("4-18 A+ Rank", player)
                    + state.has("4-19 A+ Rank", player)
                )
        if state.can_reach_location("4-Boss Little Horn", player):
            counter += 11
            if cfg.dark_world:
                counter += (
                    state.has("5-4 A+ Rank", player)
                    + state.has("5-5 A+ Rank", player)
                    + state.has("5-8 A+ Rank", player)
                    + state.has("5-10 A+ Rank", player)
                    + state.has("5-11 A+ Rank", player)
                    + state.has("5-17 A+ Rank", player)
                    + state.has("5-18 A+ Rank", player)
                    + (state.has("5-20 A+ Rank", player) * 2)
                )
        return counter >= req

    def darkZoneAccess(req: int, state: CollectionState) -> bool:
        counter = 0
        if state.can_reach_location("1-1 Hello World", player):
            counter += state.count_from_list([f"1-{i} A+ Rank" for i in range(1, 21)], player)
        if state.can_reach_location("1-Boss Lil' Slugger", player):
            counter += state.count_from_list([f"2-{i} A+ Rank" for i in range(1, 21)], player)
        if state.can_reach_location("2-Boss C.H.A.D", player):
            counter += state.count_from_list([f"3-{i} A+ Rank" for i in range(1, 21)], player)
        if state.can_reach_location("3-Boss Brownie", player):
            counter += state.count_from_list([f"4-{i} A+ Rank" for i in range(1, 21)], player)
        if state.can_reach_location("4-Boss Little Horn", player):
            counter += state.count_from_list([f"5-{i} A+ Rank" for i in range(1, 21)], player)
        if state.can_reach_location("5-Boss Larries Lament", player):
            counter += state.count_from_list([f"6-{i} A+ Rank" for i in range(1, 6)], player)
        if state.can_reach_location("6-Boss LW Dr. Fetus", player) and cfg.chapter_seven:
            counter += state.count_from_list([f"7-{i} A+ Rank" for i in range(1, 21)], player)
        return counter >= req

    location = world.get_location("6-Boss LW Dr. Fetus")
    location.access_rule = lwDrFetus

    if cfg.dark_world:
        location = world.get_location("6-Boss DW Dr. Fetus")
        location.access_rule = dwDrFetus

    location = world.get_location("Victory")
    if cfg.goal == 2:
        location.access_rule = lambda state: state.has("Chapter 7 LW Level Key", player, 20)
    elif cfg.goal == 3:
        location.access_rule = lambda state: state.has("Chapter 7 DW Level Key", player, 20)
    else:
        location.access_rule = lambda state: state.has("Victory", player)

    if cfg.achievements:
        location = world.get_location("Nostalgia (Unlock a retro warp zone)")
        location.access_rule = lambda state: warpZones(1, state)
        location = world.get_location("Living In the Past (Complete 5 retro warp zones)")
        location.access_rule = lambda state: warpZones(5, state)
        location = world.get_location("The End (Beat Chapter 6 Light World)")
        location.access_rule = lambda state: state.can_reach_location("6-Boss LW Dr. Fetus", player)
        if cfg.dark_world:
            location = world.get_location("Old School (Complete 10 retro warp zones)")
            location.access_rule = lambda state: warpZones(10, state)
            location = world.get_location("Retro Rampage (Complete all retro warp zones)")
            location.access_rule = lambda state: warpZones(15, state)
            location = world.get_location("The Real End (Beat Chapter 6 Dark World)")
            location.access_rule = lambda state: state.can_reach_location("6-Boss DW Dr. Fetus", player)
        if cfg.bandages:
            location = world.get_location("I Have Crabs! (Collect 10 Bandages)")
            location.access_rule = lambda state: bandagesAmount(10, state)
            location = world.get_location("Metalhead (Collect 30 Bandages)")
            location.access_rule = lambda state: bandagesAmount(30, state)
            location = world.get_location("I Smell something Fishy... (Collect 50 Bandages)")
            location.access_rule = lambda state: bandagesAmount(50, state)
            if cfg.dark_world:
                location = world.get_location("MS PAINT RULZ! (Collect 70 Bandages)")
                location.access_rule = lambda state: bandagesAmount(70, state)
                location = world.get_location("Vx6 (Collect 90 Bandages)")
                location.access_rule = lambda state: bandagesAmount(90, state)
                location = world.get_location("Accidental Arsonist (Collect 100 Bandages)")
                location.access_rule = lambda state: bandagesAmount(100, state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass

# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    spoiler_handle.write
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:

    ### Example way to use this hook:
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string

    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass
