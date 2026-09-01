import copy

from ..variables.game_stat_info import CONST_DAY_SCENE_COUNT

def duplicate_list(original_list):
	return copy.deepcopy(original_list)

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def read_bit(bitarray: int = 0, index: int = 0) -> bool:
	"""
	If operation could not be done, return False.
	Index cannot go higher than 511 (512 bits).
	"""
	if index > 511: return False
	return bitarray & 1 << index != 0

def write_bit(bitarray: int = 0, index: int = 0, value: bool = False) -> int:
	"""
	If operation could not be carried out, return -1.
	Index cannot go higher than 511 (512 bits).
	"""
	if index > 511: return bitarray
	new_bitarray = bitarray
	if value:
		new_bitarray |= 1 << index
	else:
		new_bitarray &= ~(1 << index)
	return new_bitarray

def get_relative_scene_id(absolute_scene_id: int = 0) -> tuple[int, int]:
	"""
	Returns the Day ID and Scene ID of this absolute scene ID in the form of a List.
	Day ID and Scene ID are both indexed from 1.
	"""
	relative_day_id: int = 1

	if 65 < absolute_scene_id <= 75: relative_day_id = 10
	elif 57 < absolute_scene_id <= 65: relative_day_id = 9
	elif 50 < absolute_scene_id <= 57: relative_day_id = 8
	elif 42 < absolute_scene_id <= 50: relative_day_id = 7
	elif 34 < absolute_scene_id <= 42: relative_day_id = 6
	elif 26 < absolute_scene_id <= 34: relative_day_id = 5
	elif 19 < absolute_scene_id <= 26: relative_day_id = 4
	elif 12 < absolute_scene_id <= 19: relative_day_id = 3
	elif 6 < absolute_scene_id <= 12: relative_day_id = 2

	relative_scene_id: int = clamp(absolute_scene_id, 1, 75)
	if relative_day_id > 1:
		for i in range(relative_day_id - 1):
			relative_scene_id -= CONST_DAY_SCENE_COUNT[i]

	return relative_day_id, relative_scene_id

def get_absolute_scene_id(day_id: int = 0, scene_id: int = 0) -> int:
	"""
	Day ID and Scene ID indexed from 1.
	Returns the absolute scene ID for a given Day and Scene within said Day.
	Absolute scene IDs are indexed from 1 to 75.
	"""
	clean_day_id: int = clamp(day_id, 1, 10)
	final_scene_id: int = clamp(scene_id, 1, CONST_DAY_SCENE_COUNT[clean_day_id - 1])
	if clean_day_id <= 1: return clamp(final_scene_id, 1, 6)
	for i in range(clean_day_id - 1):
		final_scene_id += CONST_DAY_SCENE_COUNT[i]
	return final_scene_id

def get_day_item_count(starting_day: int) -> int:
	"""
	How many Progressive Day items are remaining to unlock the rest of the Days.
	"""
	return clamp(9 - starting_day, 0, 9)