from typing import TYPE_CHECKING
from BaseClasses import Entrance, Region
from .variables.boss_and_stage import *


def create_and_connect_regions(world):
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world):
    region_menu = Region(world.origin_region_name, world.player, world.multiworld)
    regions = [region_menu]

    game_region_id = 0
    for game_region in REGION_LIST:
        regions.append(Region(game_region, world.player, world.multiworld))
        game_region_id += 1

    world.multiworld.regions += regions


def get_regions_dict(world) -> dict[str, Region]:
    """
    Retrieves all of the game's regions as a dictionary, including the menu.
    The dictionary uses the short stage names as keys.
    See REGION_LIST in boss_and_stage.py for the rest of the details.
    """
    region_dict = {
        world.origin_region_name: world.get_region(world.origin_region_name)
    }

    game_region_id = 0
    for game_region in REGION_LIST:
        region_dict[game_region] = world.get_region(game_region)
        game_region_id += 1

    return region_dict


def get_regions_list(world) -> list[Region]:
    """
    Retrieves all of the game's regions as a list, including the menu.
    See REGION_LIST in boss_and_stage.py for the rest of the details.
    """
    region_list = []
    region_dict = get_regions_dict(world)

    for game_region in region_dict.keys():
        region_list.append(region_dict[game_region])

    return region_list


def connect_regions(world):
    region_menu = world.get_region(world.origin_region_name)
    region_endstage = world.get_region(ENDSTAGE_CHOOSE_NAME)

    # This helper function returns a list,
    # but it has the Market End Card Selection at the end.
    # Don't count that one in.
    region_exit_list = get_regions_list(world)
    region_exit_list.remove(region_exit_list[-1])

    # From the menu to the rest of the game.
    region_exit_id = 0
    for exit_point in ORIGIN_TO_REGION_LIST:
        region_menu.connect(region_exit_list[region_exit_id], exit_point)
        region_exit_id += 1

    # From the Markets to the card selection at the end.
    # Since not every card shows up here, each location will need a rule about requiring stage unlock minimums.
    # TBD. Should probably put them in Locations.py
    region_stage_exit_id = 0
    for region_exits in STAGE_TO_ENDSTAGE_LIST:
        # Challenge Market is special in that it offers EVERY Ability Card the game has to offer.
        # The challenge is surviving 12 waves to even get there.
        # There is an option to not connect the Challenge Market to the Market Card Reward region.
        if region_exits == CHALLENGE_TO_CHOOSE_NAME and getattr(world.options, "disable_challenge_logic"):
            continue

        region_exit_list[region_stage_exit_id].connect(region_endstage, STAGE_TO_ENDSTAGE_LIST[region_stage_exit_id])
        region_stage_exit_id += 1
