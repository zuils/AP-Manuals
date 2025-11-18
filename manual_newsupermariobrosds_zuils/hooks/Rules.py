from typing import Optional
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value
from .World import initialize_config, GameConfig
from BaseClasses import MultiWorld, CollectionState

def miniMushroom(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    return (state.has("Progressive Powerup", player, 5) or state.has("Mini Mushroom", player)) and (
        state.can_reach_location("1-2 Secret Exit", player) or
        state.can_reach_location("2-4 Normal Exit", player) or
        state.can_reach_location("3-A Normal Exit", player) or
        (state.can_reach_location("4-2 Normal Exit", player) and state.has("Star Coin", player, 5)) or
        (state.can_reach_location("5-Tower Normal Exit", player) and state.has("Star Coin", player, 5)) or
        state.can_reach_location("6-A Normal Exit", player) or
        (state.can_reach_location("7-2 Normal Exit", player) and state.has("Star Coin", player, 5)) or
        state.can_reach_location("7-A Normal Exit", player) or
        (state.can_reach_location("8-3 Normal Exit", player) and state.has("Star Coin", player, 5))
    )

def worldReq(world: World, multiworld: MultiWorld, state: CollectionState, player: int, wrld: str):
    cfg = initialize_config(world, multiworld, player)
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
            True: [lambda: state.can_reach_location("2-Castle Secret Exit", player)],
            False: [lambda: state.has("World 4 Key", player)],
        },
        "5": {
            True: [
                lambda: state.can_reach_location("3-Castle Normal Exit", player),
                lambda: state.can_reach_location("4-Castle Normal Exit", player),
                lambda: state.can_reach_location("1-Tower Secret Exit", player) and state.has("World 1 Cannon Unlock", player),
                lambda: state.can_reach_location("2-A Secret Exit", player) and state.has("World 2 Cannon Unlock", player),
            ],
            False: [
                lambda: state.has("World 5 Key", player),
                lambda: state.can_reach_location("1-Tower Secret Exit", player) and state.has("World 1 Cannon Unlock", player),
                lambda: state.can_reach_location("2-A Secret Exit", player) and state.has("World 2 Cannon Unlock", player),
            ],
        },
        "6": {
            True: [
                lambda: state.can_reach_location("5-Castle Normal Exit", player),
                lambda: state.can_reach_location("3-Ghost House Secret Exit", player) and state.has("World 3 Cannon Unlock", player),
            ],
            False: [
                lambda: state.has("World 6 Key", player),
                lambda: state.can_reach_location("3-Ghost House Secret Exit", player) and state.has("World 3 Cannon Unlock", player),
            ],
        },
        "7": {
            True: [
                lambda: state.can_reach_location("5-Castle Secret Exit", player),
                lambda: state.can_reach_location("4-Ghost House Secret Exit", player) and state.has("World 4 Cannon Unlock", player),
            ],
            False: [
                lambda: state.has("World 7 Key", player),
                lambda: state.can_reach_location("4-Ghost House Secret Exit", player) and state.has("World 4 Cannon Unlock", player),
            ],
        },
        "8": {
            True: [
                lambda: state.can_reach_location("6-Castle Normal Exit", player),
                lambda: state.can_reach_location("7-Castle Normal Exit", player),
                lambda: state.can_reach_location("5-Ghost House Secret Exit", player) and state.has("World 5 Cannon Unlock", player),
            ],
            False: [
                lambda: state.has("World 8 Key", player),
                lambda: state.can_reach_location("5-Ghost House Secret Exit", player) and state.has("World 5 Cannon Unlock", player),
            ],
        },
    }

    return any(req() for req in requirements[wrld][is_unlock_mode])