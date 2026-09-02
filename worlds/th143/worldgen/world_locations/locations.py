from BaseClasses import Location, ItemClassification
from .location_table import generic_scene_clear_range, item_scene_clear_range, nickname_location_range, \
	music_location_range, location_table
from ..items import ISCItem
from ..regions import get_region_dict
from ...utils.utils_get_name import get_location_name_scene, get_location_name_scene_with_item, \
	get_location_name_nickname, get_location_name_music_room
from ...utils.utils_math import clamp
from ...variables.game_info import SHORT_NAME
from ...variables.game_stat_info import CONST_DAY_SCENE_COUNT
from ...variables.location_item_name import CONST_DAY_TO_ID, CONST_NICKNAME_NAME, EVENT_ITEM_SCENE_CLEAR_NAME, \
	EVENT_ITEM_SCENE_UNLOCK_NAME, CONST_ITEM_NAMES, CONST_ITEM_SHORT_TO_ID


class ISCLocation(Location):
	game: str = SHORT_NAME

CONST_DAY_LIST = CONST_DAY_TO_ID.keys()
CONST_TOTAL_NICKNAME_COUNT = len(CONST_NICKNAME_NAME)

#
# Various Location-related utils.
#
def check_location_type(location_id: int = 0) -> int:
	"""
	Checks what kind of Location it is.

	-1 - Invalid.
	0 - Generic scene clears.
	1 - Item scene clears.
	2 - Nicknames.
	3 - Music Room.
	"""
	if generic_scene_clear_range[0] < location_id <= generic_scene_clear_range[1]:
		return 0
	if item_scene_clear_range[0] < location_id <= item_scene_clear_range[1]:
		return 1
	if nickname_location_range[0] < location_id <= nickname_location_range[1]:
		return 2
	if music_location_range[0] < location_id <= music_location_range[1]:
		return 3

	return -1

def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
	return {location_name: location_table[location_name] for location_name in location_names}

#
# Functions to be ran once.
#
def create_all_locations(world):
	all_regions_dict = get_region_dict(world)

	for region_name in all_regions_dict:
		# Menu
		selected_region = all_regions_dict[region_name]
		if region_name == world.origin_region_name:
			# Nicknames here.
			for nickname_id in range(CONST_TOTAL_NICKNAME_COUNT):
				if nickname_id >= (CONST_TOTAL_NICKNAME_COUNT - 10) and not world.options.include_hidden_nicknames:
					continue
				nickname_str: str = get_location_name_nickname(nickname_id + 1)

				nickname_location = ISCLocation(
					world.player,
					nickname_str,
					world.location_name_to_id[nickname_str],
					selected_region
				)

				selected_region.locations.append(nickname_location)
			# Music Room here.
			if not world.options.include_music_checks: continue
			for music_id in range(9):
				music_str: str = get_location_name_music_room(music_id + 1)

				music_location = ISCLocation(
					world.player,
					music_str,
					world.location_name_to_id[music_str],
					selected_region
				)

				selected_region.locations.append(music_location)
		# Day-specific
		elif region_name in CONST_DAY_LIST:
			day_id = CONST_DAY_TO_ID[region_name]
			for scene_id in range(CONST_DAY_SCENE_COUNT[day_id]):
				# Generic Scene Clears
				generic_scene_str: str = get_location_name_scene(
					day_number=day_id + 1,
					scene_number=scene_id + 1
				)

				generic_scene_location = ISCLocation(
					world.player,
					generic_scene_str,
					world.location_name_to_id[generic_scene_str],
					selected_region
				)

				selected_region.locations.append(generic_scene_location)

				# Event location for generic clears
				event_generic_location = get_fake_location(
					world, get_fake_scene_name(day_id=day_id + 1, scene_id=scene_id + 1), selected_region
				)
				event_generic_location.place_locked_item(
					get_fake_item(world, get_fake_clear_item_name(10))
				)
				selected_region.locations.append(event_generic_location)

				# Event location for scene access
				event_access_location = get_fake_location(
					world, get_fake_scene_access_name(day_id=day_id + 1, scene_id=scene_id + 1), selected_region
				)
				event_access_location.place_locked_item(
					get_fake_item(world, EVENT_ITEM_SCENE_UNLOCK_NAME)
				)
				selected_region.locations.append(event_access_location)

				# Event location for day-specific clears
				event_day_specific_location = get_fake_location(
					world, get_fake_scene_name(day_id=day_id + 1, scene_id=scene_id + 1, dupe_index=1), selected_region
				)
				event_day_specific_location.place_locked_item(
					get_fake_item(world, get_fake_day_clear_item_name(day_id + 1))
				)
				selected_region.locations.append(event_day_specific_location)

				# Item-specific Clears
				for item_string_id in CONST_ITEM_SHORT_TO_ID.keys():
					if not check_if_scene_is_possible(day_id + 1, scene_id + 1, item_string_id): continue
					item_id = CONST_ITEM_SHORT_TO_ID[item_string_id]
					# Event location
					event_item_location = get_fake_location(
						world,
						get_fake_scene_name(
							day_id=day_id + 1,
							scene_id=scene_id + 1,
							with_item=item_id
						),
						selected_region
					)
					event_item_location.place_locked_item(
						get_fake_item(world, get_fake_clear_item_name(item_id))
					)
					selected_region.locations.append(event_item_location)

					# The actual location.
					if not world.options.include_item_clears: continue
					item_scene_str: str = get_location_name_scene_with_item(
						day_number=day_id + 1,
						scene_number=scene_id + 1,
						item_id=item_id
					)

					item_scene_location = ISCLocation(
						world.player,
						item_scene_str,
						world.location_name_to_id[item_scene_str],
						selected_region
					)
					selected_region.locations.append(item_scene_location)

	return

#
# FAKE LOCATION UTILS
#
def get_fake_location(world, location_name: str, given_region, show_spoiler: bool = False) -> ISCLocation:
	new_fake_location = ISCLocation(world.player, location_name, None, given_region)
	new_fake_location.show_in_spoiler = show_spoiler
	return new_fake_location

def get_fake_item(world, item_name: str) -> ISCItem:
	return ISCItem(
		item_name,
		ItemClassification.progression,
		None,
		world.player
	)

# Indexing starts at 1 for Day and Scene IDs.
# 0-8 for items. 9 for no items. Leave anything else for generic clears.
def get_fake_scene_name(day_id: int = 1, scene_id: int = 1, with_item: int = 10, dupe_index: int = 0) -> str:
	fake_location_str: str
	item_id: int = clamp(with_item, 0, 9)

	if with_item < 9:
		fake_location_str = f"{day_id}-{scene_id} with {CONST_ITEM_NAMES[item_id]}"
	elif with_item == 9:
		fake_location_str = f"{day_id}-{scene_id} Itemless"
	else:
		fake_location_str = f"{day_id}-{scene_id} Generic"

	return f"EVENTLOCATION: {fake_location_str} No. {str(dupe_index)}"

def get_fake_scene_access_name(day_id: int = 1, scene_id: int = 1) -> str:
	return f"EVENTLOCATION: {day_id}-{scene_id} Access"

def get_fake_clear_item_name(with_item: int = 10) -> str:
	if 0 < with_item < 9:
		return f"{EVENT_ITEM_SCENE_CLEAR_NAME} with {with_item}"
	elif with_item == 9:
		return f"{EVENT_ITEM_SCENE_CLEAR_NAME} Itemless"
	else:
		return f"{EVENT_ITEM_SCENE_CLEAR_NAME} Generic"

def get_fake_day_clear_item_name(day_id: int = 1) -> str:
	return f"{EVENT_ITEM_SCENE_CLEAR_NAME} Day {clamp(day_id, 1, 10)}"

#
# Special check for Item-specific scenes
#
def check_if_scene_is_possible(day_id: int, scene_id: int, item_string_id: str) -> bool:
	"""
	Boolean to see if a Scene is possible to clear with the item in question.
	Day ID and Scene ID are indexed from 1.
	"""
	from ..world_rules.rules_utils import check_if_scene_in_set, CONST_ITEM_SHORT_TO_CLEAR_SET, \
		NORMAL_CLEAR_JIZO_DOLL_SET, NORMAL_CLEAR_LANTERN_DOLL_SET, NORMAL_CLEAR_MALLET_JIZO_SET, \
		get_scene_item_clear_potential, NORMAL_CLEAR_NO_ITEM_SET, NORMAL_CLEAR_DOLL_SUB_SET

	is_scene_possible = False

	if item_string_id != "none":
		if check_if_scene_in_set(day_id, scene_id, CONST_ITEM_SHORT_TO_CLEAR_SET[item_string_id]):
			is_scene_possible = True

		match item_string_id:
			case "jizo":
				if check_if_scene_in_set(day_id, scene_id, NORMAL_CLEAR_JIZO_DOLL_SET):
					is_scene_possible = True
			case "lantern":
				if check_if_scene_in_set(day_id, scene_id, NORMAL_CLEAR_LANTERN_DOLL_SET):
					is_scene_possible = True
			case "mallet":
				if check_if_scene_in_set(day_id, scene_id, NORMAL_CLEAR_MALLET_JIZO_SET):
					is_scene_possible = True

		scene_item_potential_set = tuple(get_scene_item_clear_potential(day_id, scene_id))

		if len(scene_item_potential_set) > 0:
			if item_string_id in scene_item_potential_set:
				is_scene_possible = True

	if check_if_scene_in_set(day_id, scene_id, NORMAL_CLEAR_NO_ITEM_SET):
		is_scene_possible = True
	if check_if_scene_in_set(day_id, scene_id, NORMAL_CLEAR_DOLL_SUB_SET):
		is_scene_possible = True

	return is_scene_possible