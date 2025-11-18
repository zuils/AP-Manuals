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
class Goal(Choice):
    """
    Light World: Beat LW Dr. Fetus
    Dark World: Beat DW Dr. Fetus
    Light World Chapter 7: Beat all of LW Chapter 7
    Dark World Chapter 7: Beat all of DW Chapter 7
    """
    display_name = "Goal"
    option_light_world = 0
    option_dark_world = 1
    option_lightworld_chpt7 = 2
    option_darkworld_chpt7 = 3
    default = 0


class BossAmount(Range):
    """
    How many level keys are in the pool (only affects Chapters 1-5)
    """
    display_name = "Boss Amount"
    range_start = 0
    range_end = 20
    default = 20


class BossReq(Range):
    """
    How many level keys are required to fight the boss (only affects Chapters 1-5)
    """
    display_name = "Boss Requirement"
    range_start = 0
    range_end = 20
    default = 17


class DrFetusAmount(Range):
    """
    How many dw dr. fetus keys should be in the pool
    This setting and the next setting won't do anything if dark world levels are not enabled
    If chapter 7 is not enabled or goal is to complete lw/dw chpt 7, then the max amount will be 105
    """
    display_name = "DW Dr. Fetus Amount"
    range_start = 0
    range_end = 125
    default = 105


class DrFetusReq(Range):
    """
    How many dw dr. fetus keys should be required to beat dw dr. fetus
    """
    display_name = "DW Dr. Fetus Requirement"
    range_start = 0
    range_end = 125
    default = 85


class Bandages(Toggle):
    """
    Enable the bandage collectibles, this setting will always be on if the goal is 106
    Note: if this is enabled, you will be using a fresh save and start on chapter 1 and go in order
    If this is disabled you will be using a fully completed save
    """
    display_name = "Bandages"


class DarkWorld(DefaultOnToggle):
    """
    If the goal is light world, enable dark world levels
    This setting will always be on if the goal is either dw dr. fetus or dw chpt 7
    """
    display_name = "Enable Dark World Levels"


class ChapterSeven(Toggle):
    """
    Enable Chapter 7 levels 
    """
    display_name = "Chapter 7"


class StartingChpt(Range):
    """
    Choose starting chapter
    If starting chapter is 7 and chapter seven levels are off or goal is complete lw/dw chpt 7, then it will select 1-6 at random
    If bandages are on, starting chapter will be 1
    """
    display_name = "Starting Chapter"
    range_start = 1
    range_end = 7
    default = 1


class StartingCharacters(Choice):
    """
    Choose your starting character
    If starting chapter is 6 or bandages are on, character is forced to be meat boy
    If starting chapter is 7, character is forced to be bandage girl
    Character will be random if starting chapter is NOT 7 and your starting character is bandage girl
    """
    display_name = "Starting Character"
    option_meat_boy = 0
    option_commander_video = 1
    option_jill = 2
    option_ogmo = 3
    option_flywrench = 4
    option_the_kid = 5
    option_naija = 6
    option_steve = 7
    option_bandage_girl = 8
    default = 0


class TheKidXmas(Toggle):
    """
    This will include all of The Kid Xmas levels
    """
    display_name = "The Kid Xmas Levels"


class Achievements(Toggle):
    """
    Puts most steam achievements in the pool
    """
    display_name = "Achievements"


class DeathlessAchievements(Toggle):
    """
    Puts all deathless achievements in the pool
    """
    display_name = "Deathless Achievements"


class SpeedrunAchievements(Toggle):
    """
    Puts all speedrun achievements in the pool
    This setting will always be off if there are no dark world levels in the pool
    """
    display_name = "Speedrun Achievements"


# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["Goal"] = Goal
    options["bandages"] = Bandages
    options["boss_amount"] = BossAmount
    options["boss_req"] = BossReq
    options["dark_world"] = DarkWorld
    options["dw_drfetus_amount"] = DrFetusAmount
    options["dw_drfetus_req"] = DrFetusReq
    options["chapter_seven"] = ChapterSeven
    options["starting_chapter"] = StartingChpt
    options["starting_character"] = StartingCharacters
    options["xmas"] = TheKidXmas
    options["achievements"] = Achievements
    options["deathless"] = DeathlessAchievements
    options["speedrun"] = SpeedrunAchievements
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
