from BaseClasses import Region
from ..utils.utils_get_name import get_entrance_to_region_name
from ..variables.location_item_name import CONST_DAY_TO_ID


CONST_DAY_LIST = CONST_DAY_TO_ID.keys()

def create_and_connect_regions(world):
	create_all_regions(world)
	connect_all_regions(world)

def get_region_dict(world) -> dict[str, Region]:
	"""
	Retrieves all of the game's regions as a dictionary, including the menu.
	The dictionary uses the Day names as keys.
	"""
	region_dict = {
		world.origin_region_name: world.get_region(world.origin_region_name)
	}

	for game_region in CONST_DAY_LIST:
		region_dict[game_region] = world.get_region(game_region)

	return region_dict

def create_all_regions(world):
	region_menu = Region(world.origin_region_name, world.player, world.multiworld)
	regions = [region_menu]

	for game_region in CONST_DAY_LIST:
		regions.append(Region(game_region, world.player, world.multiworld))

	world.multiworld.regions += regions

def connect_all_regions(world):
	region_menu = world.get_region(world.origin_region_name)
	all_regions_dict = get_region_dict(world)

	for region_name in all_regions_dict.keys():
		if region_name not in CONST_DAY_LIST: continue
		region_menu.connect(
			all_regions_dict[region_name],
			get_entrance_to_region_name(region_name)
		)