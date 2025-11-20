# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value
from typing import Type, Any


####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################


# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#

class EnableWorldCannons(DefaultOnToggle):
    """
    When enabled, world cannons will be in the item pool
    """
    display_name = "Enable World Cannons"
    
class WorldUnlocks(Choice):
    """
    How should worlds be unlocked
    keys: By world keys
    castles: By unlocking the ability to play castle levels (you will be forced to start in world 1)
    If world cannons are in the pool, then they'll be considered in logic for either choice
    """
    display_name = "World Unlocks"
    option_keys = 0
    option_castles = 1
    default = 0

class StartingWorld(Range):
    """
    Which world to start in
    This option is ignored if world unlocks is by castles as you'll be starting in world 1
    """
    display_name = "Starting World"
    range_start = 1
    range_end = 8
    default = 1
    
class MiniMushroom(Choice):
    """
    How should the mini mushroom powerup be handled
    Selecting progressive powerup will make it the 5th progressive powerup
    """
    display_name = "Mini Mushroom"
    option_progressive_powerup = 0
    option_seperate_item = 1
    default = 0

class ItemStorage(Toggle):
    """
    Set to true if the item storage should be in the item pool
    """
    display_name = "Item Storage"

class TowerKeys(Toggle):
    """
    Put Tower Keys in the world to unlock the next section of the same world
    Ex. Getting access to World 1 Tower Key will allow you to play 1-Tower, 1-4, 1-5, 1-A
    """
    display_name = "Tower Keys"

class Goal(Choice):
    """
    bowser: Get world 1-8 keys, or obtain the Bowser's Castle Key
    boss_tokens: Boss Tokens are placed at each boss, obtain x amount of boss tokens and access world 8 to beat bowser
    star_coins: Get access to world 8 and obtain x amount of star coins to beat bowser
    """
    display_name = "Goal"
    option_bowser = 0
    option_boss_tokens = 1
    option_star_coins = 2
    default = 0
    
class BossTokensReq(Range):
    """
    If goal is boss tokens, how many should be required
    """
    display_name = "Boss Tokens Amount"
    range_start = 1
    range_end = 8
    default = 8
    
class StarCoinsAmount(Range):
    """
    How many should be in the pool
    """
    display_name = "Star Coins Amount"
    range_start = 30
    range_end = 240
    default = 240

class StarCoinsReq(Range):
    """
    If goal is star coins, how many should be required to goal
    """
    display_name = "Star Coins Required"
    range_start = 1
    range_end = 240
    default = 120

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["enable_world_cannons"] = EnableWorldCannons
    options["world_unlocks"] = WorldUnlocks
    options["starting_world"] = StartingWorld
    options["mini_mushroom"] = MiniMushroom
    options["item_storage"] = ItemStorage
    options["tower_keys"] = TowerKeys
    options["Goal"] = Goal
    options["boss_tokens_req"] = BossTokensReq
    options["star_coins_amount"] = StarCoinsAmount
    options["star_coins_req"] = StarCoinsReq
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: Type[PerGameCommonOptions]):
    # To access a modifiable version of options check the dict in options.type_hints
    # For example if you want to change DLC_enabled's display name you would do:
    # options.type_hints["DLC_enabled"].display_name = "New Display Name"

    #  Here's an example on how to add your aliases to the generated goal
    # options.type_hints['goal'].aliases.update({"example": 0, "second_alias": 1})
    # options.type_hints['goal'].options.update({"example": 0, "second_alias": 1})  #for an alias to be valid it must also be in options

    pass

# Use this Hook if you want to add your Option to an Option group (existing or not)
def before_option_groups_created(groups: dict[str, list[Type[Option[Any]]]]) -> dict[str, list[Type[Option[Any]]]]:
    # Uses the format groups['GroupName'] = [TotalCharactersToWinWith]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
