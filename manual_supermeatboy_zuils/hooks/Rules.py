from typing import Optional
from worlds.AutoWorld import World
from ..Helpers import is_option_enabled, get_option_value, clamp, get_items_with_value
from .World import initalize_globals, GameConfig, bandages_amount
from BaseClasses import MultiWorld, CollectionState

import re

def progCharacter(world: World, multiworld: MultiWorld, state: CollectionState, player: int):
    if is_option_enabled(multiworld, player, "bandages"):
        return (
            (state.has("Naija", player) and state.can_reach_location("2-Boss C.H.A.D", player) and state.has("Bandage", player, 50) and bandages_amount(50, state)) or
            (state.has("Steve", player) and state.can_reach_location("4-Boss Little Horn", player) and state.has("Bandage", player, 100) and bandages_amount(100, state)) or
            state.has("Commander Video", player) or
            (state.has("Jill", player) and state.can_reach_location("1-Boss Lil' Slugger", player)) or
            (state.has("Ogmo", player) and state.can_reach_location("2-Boss C.H.A.D", player)) or
            (state.has("Flywrench", player) and state.can_reach_location("3-Boss Brownie", player)) or
            (state.has("The Kid", player) and state.can_reach_location("4-Boss Little Horn", player))
        )
    else:
        return state.has_group("ProgCharacters", player)


def chapterReq(world: World, multiworld: MultiWorld, state: CollectionState, player: int, chpt: str):
    cfg: GameConfig = initalize_globals(world, multiworld, player)
    boss = {
        "1": "1-Boss Lil' Slugger",
        "2": "2-Boss C.H.A.D",
        "3": "3-Boss Brownie",
        "4": "4-Boss Little Horn",
        "5": "5-Boss Larries Lament",
        "6": "6-Boss LW Dr. Fetus"
    }
    
    if cfg.bandages:
        if chpt == "1":
            return True
        
        return state.has(f"Chapter {int(chpt) - 1} LW Level Key", player, cfg.boss_req if chpt != "7" else 5) and \
            state.can_reach_location(boss[str(int(chpt) - 1)], player)
    else:
        if chpt == "7" and (cfg.goal == 2 or cfg.goal == 3):
            return state.has_group("Chapter Keys", player, 7)
        else:
            return state.has(f"Chapter {int(chpt)} Key", player)


def speedrunReq(world: World, multiworld: MultiWorld, state: CollectionState, player: int, chpt: str):
    return state.has_all([f"{chpt}-{i} A+ Rank" for i in range(1, 21 if chpt != "6" else 6)], player)

def bossReq(world: World, multiworld: MultiWorld, state: CollectionState, player: int, chpt: str):
    cfg: GameConfig = initalize_globals(world, multiworld, player)
    return state.has(f"Chapter {chpt} LW Level Key", player, cfg.boss_req) and state.has("4bit/4color/8bit/Normal Meat Boy", player)