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

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

from dataclasses import dataclass

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
    cannons: bool
    world_unlocks: int
    starting_world: int
    mini_mushroom: int
    tower_keys: bool
    goal: int
    boss_tokens_req: int
    star_coins_amount: int
    star_coins_req: int

def initialize_config(world: World, multiworld: MultiWorld, player: int) -> GameConfig:
    if hasattr(world, "_config_cache") and player in world._config_cache:
        return world._config_cache[player]
    
    cannons = is_option_enabled(multiworld, player, "enable_world_cannons")
    world_unlocks = get_option_value(multiworld, player, "world_unlocks")
    starting_world = get_option_value(multiworld, player, "starting_world")
    mini_mushroom = get_option_value(multiworld, player, "mini_mushroom")
    tower_keys = is_option_enabled(multiworld, player, "tower_keys")
    goal = get_option_value(multiworld, player, "Goal")
    boss_tokens_req = get_option_value(multiworld, player, "boss_tokens_req")
    star_coins_amount = get_option_value(multiworld, player, "star_coins_amount")
    star_coins_req = min(star_coins_amount, get_option_value(multiworld, player, "star_coins_req"))
    
    if world_unlocks == 1:
        starting_world = 1
        world.options.starting_world.value = 1
        
    cfg = GameConfig(
        cannons=cannons,
        world_unlocks=world_unlocks,
        starting_world=starting_world,
        mini_mushroom=mini_mushroom,
        tower_keys=tower_keys,
        goal=goal,
        boss_tokens_req=boss_tokens_req,
        star_coins_amount=star_coins_amount,
        star_coins_req=star_coins_req
    )
    
    if not hasattr(world, "_config_cache"):
        world._config_cache = {}
    world._config_cache[player] = cfg
    
    return cfg

# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    cfg = initialize_config(world, multiworld, player)
    # Use this hook to remove locations from the world
    locationNamesToRemove: list[str] = [] # List of location names

    # Add your code here to calculate which locations to remove
    if cfg.goal != 1:
        locationNamesToRemove.extend(f"{i}-Castle Boss Token" for i in range(1, 9))

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
    cfg = initialize_config(world, multiworld, player)
    item_config["Star Coin"] = {ItemClassification.progression_deprioritized_skip_balancing: cfg.star_coins_amount}
    
    return item_config

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    cfg = initialize_config(world, multiworld, player)
    if cfg.world_unlocks == 0:
        start = next(i for i in item_pool if i.name == f"World {cfg.starting_world} Key")
        multiworld.push_precollected(start)
        item_pool.remove(start)
    
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    cfg = initialize_config(world, multiworld, player)
    
    # Use this hook to remove items from the item pool
    itemNamesToRemove: list[str] = [] # List of item names

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.
    
    if not cfg.cannons:
        itemNamesToRemove.extend(f"World {i} Cannon Unlock" for i in range(1, 6))
    
    if cfg.world_unlocks == 0:
        itemNamesToRemove.extend(f"World {i} Castle Key" for i in range(1, 9))
        itemNamesToRemove.append("Bowser's Castle Key")
    else:
        itemNamesToRemove.extend(f"World {i} Key" for i in range(1, 9))
        
    if cfg.mini_mushroom == 0:
        itemNamesToRemove.append("Mini Mushroom")
    else:
        itemNamesToRemove.append("Progressive Powerup")
    
    if not cfg.tower_keys:
        itemNamesToRemove.extend(f"World {i} Tower Key" for i in range(1, 9))
        itemNamesToRemove.append("World 6 Tower Key")
        itemNamesToRemove.append("World 8 Tower Key")
    
    if cfg.goal != 1:
        itemNamesToRemove.extend("Boss Token" for _ in range(8))


    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        item_pool.remove(item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # item_pool.remove(item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    cfg = initialize_config(world, multiworld, player)
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True
    
    def bowser(state: CollectionState):
        if cfg.goal == 0:
            if cfg.world_unlocks == 0:
                return state.has_all([f"World {i} Key" for i in range(1, 9)], player)
            else:
                return state.has("Bowser's Castle Key", player)
        elif cfg.goal == 1:
            return state.has("Boss Token", player, cfg.boss_tokens_req)
        else:
            return state.has("Star Coin", player, cfg.star_coins_req)

    for i in range(1, 4):
        location = multiworld.get_location(f"8-Bowser's Castle Star Coin {i}", player)
        old_rule = location.access_rule
        location.access_rule = lambda state: old_rule(state) and bowser(state)

    location = multiworld.get_location("8-Bowser's Castle Normal Exit", player)
    old_rule = location.access_rule
    location.access_rule = lambda state: old_rule(state) and bowser(state)

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

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
