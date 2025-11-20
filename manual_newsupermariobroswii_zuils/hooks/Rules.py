from typing import Optional
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value
from BaseClasses import MultiWorld, CollectionState
from .World import initialize_config, GameConfig

import re

# Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# Define a function here, and you can use it in a requires string with {function_name()}.
def bowser(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    cfg: GameConfig = initialize_config(world, multiworld, player)
    
    if cfg.goal == 0:
        if cfg.world_unlocks == 0:
            return state.has_group("World Keys", player, 8)
        else:
            return state.has("Bowser's Castle Key", player)
    elif cfg.goal == 1:
        if cfg.world_unlocks == 0:
            return state.has("World 8 Key", player)
        else:
            return state.has("Bowser's Castle Key", player)
    elif cfg.goal == 2:
        return state.has("Boss Token", player, cfg.boss_tokens_req)
    else:
        return state.has("Star Coin", player, cfg.star_coins_req)
    
def worldReq(world: World, multiworld: MultiWorld, state: CollectionState, player: int, wrld: str):
    cfg: GameConfig = initialize_config(world, multiworld, player)
    is_unlock_mode = cfg.world_unlocks != 0

    requirements = {
        "1": {
            True: [lambda: True],
            False: [lambda: state.has("World 1 Key", player)],
        },
        "2": {
            True: [lambda: state.can_reach_location("1-Castle Normal Exit", player)],
            False: [lambda: state.has("World 2 Key", player)],
        },
        "3": {
            True: [lambda: state.can_reach_location("2-Castle Normal Exit", player)],
            False: [lambda: state.has("World 3 Key", player)],
        },
        "4": {
            True: [lambda: state.can_reach_location("3-Castle Normal Exit", player)],
            False: [lambda: state.has("World 4 Key", player)],
        },
        "5": {
            True: [
                lambda: state.can_reach_location("4-Castle Normal Exit", player),
                lambda: state.can_reach_location("1-3 Secret Exit", player) and state.has("World 1 Cannon Unlock", player),
                lambda: state.can_reach_location("2-6 Secret Exit", player) and state.has("World 2 Cannon Unlock", player),
            ],
            False: [
                lambda: state.has("World 5 Key", player),
                lambda: state.can_reach_location("1-3 Secret Exit", player) and state.has("World 1 Cannon Unlock", player),
                lambda: state.can_reach_location("2-6 Secret Exit", player) and state.has("World 2 Cannon Unlock", player),
            ],
        },
        "6": {
            True: [
                lambda: state.can_reach_location("5-Castle Normal Exit", player),
                lambda: state.can_reach_location("3-Ghost House Secret Exit", player) and state.has("World 3 Cannon Unlock", player),
                lambda: state.can_reach_location("4-Tower Secret Exit", player) and state.has("World 4 Cannon Unlock", player),
            ],
            False: [
                lambda: state.has("World 6 Key", player),
                lambda: state.can_reach_location("3-Ghost House Secret Exit", player) and state.has("World 3 Cannon Unlock", player),
                lambda: state.can_reach_location("4-Tower Secret Exit", player) and state.has("World 4 Cannon Unlock", player),
            ],
        },
        "7": {
            True: [lambda: state.can_reach_location("6-Castle Normal Exit", player)],
            False: [lambda: state.has("World 7 Key", player)],
        },
        "8": {
            True: [
                lambda: state.can_reach_location("7-Castle Normal Exit", player),
                lambda: state.can_reach_location("5-Ghost House Secret Exit", player) and state.has("World 5 Cannon Unlock", player),
                lambda: state.can_reach_location("6-6 Secret Exit", player) and state.has("World 6 Cannon Unlock", player),
            ],
            False: [
                lambda: state.has("World 8 Key", player),
                lambda: state.can_reach_location("5-Ghost House Secret Exit", player) and state.has("World 5 Cannon Unlock", player),
                lambda: state.can_reach_location("6-6 Secret Exit", player) and state.has("World 6 Cannon Unlock", player),
            ],
        },
        "9": {
            True: [lambda: state.can_reach_location("8-Bowser's Castle Normal Exit", player)],
            False: [lambda: state.has_group("World Keys", player, 9)]
        }
    }

    return any(req() for req in requirements[wrld][is_unlock_mode])