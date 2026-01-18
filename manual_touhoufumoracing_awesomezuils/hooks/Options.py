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
class CharacterTop3(Toggle):
    """Enables checks for placing in the top 3 with each character."""
    display_name = "Character Top 3"
    default = False

class CharacterFirst(Toggle):
    """Enables checks for placing first with each character."""
    display_name = "Character First"
    default = False

class VehicleTop3(Toggle):
    """Enables checks for placing in the top 3 with each vehicle."""
    display_name = "Vehicle Top 3"
    default = False

class VehicleFirst(Toggle):
    """Enables checks for placing first with each vehicle."""
    display_name = "Vehicle First"
    default = False

class TrackTop3(Toggle):
    """Enables checks for placing in the top 3 on each track."""
    display_name = "Track Top 3"
    default = False

class TrackFirst(Toggle):
    """Enables checks for placing first on each track."""
    display_name = "Track First"
    default = False
    
class Fumosanity(Toggle):
    """Enables checks for completing every race with every character.
    This also includes top 3 and/or first place checks if you have those checks on"""
    display_name = "Fumosanity"
    default = False

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    options["char_top_3"] = CharacterTop3
    options["char_first"] = CharacterFirst
    options["vehicle_top_3"] = VehicleTop3
    options["vehicle_first"] = VehicleFirst
    options["track_top_3"] = TrackTop3
    options["track_first"] = TrackFirst
    options["fumosanity"] = Fumosanity
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
