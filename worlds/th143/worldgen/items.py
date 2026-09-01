from typing import NamedTuple, Optional
from unittest import case

from BaseClasses import Item, ItemClassification
from .. import ISCWorld, CONST_DAY_TO_ID
from ..utils.utils_math import get_day_item_count
from ..variables.game_info import DISPLAY_NAME
from ..variables.game_stat_info import CONST_ITEM_UPGRADE_STAT, CONST_DAY_SCENE_COUNT
from ..utils.utils_get_name import get_scene_unlock_name, get_item_upgrade_name_id, \
	get_item_remove_cap, get_item_name_usage, get_item_name_stat, get_item_name_subitem
from ..variables.location_item_name import CONST_PROGRESSIVE_DAY, CONST_SUBITEM_SLOT_NAME, CONST_TEMP_PREFIX, \
	CONST_FILLER_NAME, CONST_FILLER_USELESS_NAMES, CONST_FILLER_USELESS_PREFIX, CONST_TREASURE_ITEM_NAMES, CONST_ITEM_SHORT_TO_ID

class ISCItem(Item):
	game: str = DISPLAY_NAME

class ISCItemData(NamedTuple):
	category: str
	code: Optional[int] = None
	classification: ItemClassification = ItemClassification.filler
	max_quantity: int = 1
	weight: int = 1

#
# Item Utils
#
def get_item_to_id_dict() -> dict[str, int]:
	item_dict: dict[str, int] = {}
	for name, data in item_table.items():
		item_dict.setdefault(name, data.code)
	return item_dict

def get_items_by_category(category: str) -> dict[str, ISCItemData]:
	item_dict: dict[str, ISCItemData] = {}
	for name, data in item_table.items():
		if data.category == category:
			item_dict.setdefault(name, data)

	return item_dict

def create_item_with_correct_classification(world, item_name: str) -> ISCItem:
	classification = item_table[item_name].classification

	return ISCItem(
		item_name,
		classification,
		item_table[item_name].code,
		world.player
	)

def get_random_filler_item_name(world) -> str:
	filler_item_list = []

	for name in get_items_by_category(CATEGORY_USEFUL).keys():
		filler_item_list.append(name)

	# If useless Filler is enabled, add to pool.
	if world.options.useless_filler:
		for name in get_items_by_category(CATEGORY_FILLER).keys():
			filler_item_list.append(name)

	final_item_name: str = world.random.choice(filler_item_list).__str__()

	# Trap Chance
	if world.random.randint(0, 99) < world.options.trap_chance:
		trap_item_list = []
		for name in get_items_by_category(CATEGORY_TRAP).keys():
			if name in world.options.trap_blacklist: continue
			trap_item_list.append(name)
		final_item_name: str = world.random.choice(trap_item_list).__str__()

	# Then finally, return a filler.
	return final_item_name

#
# Other various Item utils
#
def get_vanilla_level_max(item_id: int) -> int:
	"""
	How many upgrade items are needed to reach the max vanilla level.
	Item ID is indexed from 0.
	"""
	return len(CONST_ITEM_UPGRADE_STAT[item_id]["level"])

def get_vanilla_count_max(item_id: int) -> int:
	"""
	How many use count upgrades are needed to reach the max vanilla permitted.
	Item ID is indexed from 0.
	"""
	return len(get_vanilla_count_unique(item_id))

def get_vanilla_count_unique(item_id: int) -> list[int]:
	item_use_count_list = CONST_ITEM_UPGRADE_STAT[item_id]["count"]
	return [i for i in item_use_count_list if item_use_count_list.count(i) < 2]

def get_vanilla_stat_max(item_id: int) -> int:
	"""
	How many unique stat upgrades are needed to reach the max vanilla permitted.
	Item ID is indexed from 0.
	"""
	return len(get_vanilla_stat_unique(item_id))

def get_vanilla_stat_unique(item_id: int) -> list[int]:
	unique_stat_count_list = CONST_ITEM_UPGRADE_STAT[item_id]["stat"]
	return [i for i in unique_stat_count_list if unique_stat_count_list.count(i) < 2]

def get_vanilla_max_level_dict() -> dict[str, int]:
	"""
	Returns a convenient dictionary listing the max level of each item.
	The dictionary uses the internal item string IDs as the key.
	See CONST_ITEM_SHORT_TO_ID in location_item_name.py.
	"""
	max_level_dict = {}
	for item_name, item_id in CONST_ITEM_SHORT_TO_ID:
		max_level_dict[item_name] = get_vanilla_level_max(item_id)
	return max_level_dict

def get_vanilla_max_count_dict() -> dict[str, int]:
	"""
	Like get_vanilla_max_level_dict(), but specifically for max item use counts.
	"""
	max_count_dict = {}
	for item_name, item_id in CONST_ITEM_SHORT_TO_ID:
		max_count_dict[item_name] = get_vanilla_count_max(item_id)
	return max_count_dict

def get_vanilla_max_stat_dict() -> dict[str, int]:
	"""
	Like get_vanilla_max_level_dict(), but specifically for max item unique stats.
	"""
	max_stat_dict = {}
	for item_name, item_id in CONST_ITEM_SHORT_TO_ID:
		max_stat_dict[item_name] = get_vanilla_stat_max(item_id)
	return max_stat_dict

#
# Really specific functions that are rarely called
#
def get_item_groups() -> dict[str, set[str]]:
	item_groups: dict[str, set[str]] = {}

	item_group_list = [
		CATEGORY_SCENE_PROGRESS,
		CATEGORY_ITEM_LEVEL,
		CATEGORY_ITEM_UPGRADE,
		CATEGORY_SUBITEM,
		CATEGORY_USEFUL,
		CATEGORY_FILLER,
		CATEGORY_TRAP,
		CATEGORY_TREASURE
	]

	for category in item_group_list:
		category_dict = get_items_by_category(category)
		category_group: set[str] = set()
		for entry in category_dict.keys():
			category_group.add(entry)
		item_groups.update({category: category_group})

	return item_groups

def create_all_items(world: ISCWorld):
	def get_remaining_locations(the_pool: list[Item]):
		number_of_items = len(the_pool)
		number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
		return number_of_unfilled_locations - number_of_items

	item_pool: list[Item] = []

	# Generate all Day and Scene unlocks, if necessary. (9 Items)

	# This is only ever used if Progressive Day is active.
	latest_day_opened: int = world.options.starting_day.value
	if len(world.selected_random_starting_days) > 0:
		latest_day_opened = CONST_DAY_TO_ID[world.selected_random_starting_days[0]]
	if world.options.progressive_day:
		day_items_to_submit: int = get_day_item_count(latest_day_opened)
		if day_items_to_submit > 0:
			for item_submit_index in range(day_items_to_submit):
				item_pool.append(world.create_item(CONST_PROGRESSIVE_DAY))

	# Generating Progressive Scene items
	scene_deduct_list: list[int] = []
	for day_chosen_str in world.selected_random_starting_days:
		scene_deduct_list.append(CONST_DAY_TO_ID[day_chosen_str])

	for day_id in range(10):
		# Require only 1 item by default.
		how_many_to_append: int = 1
		match world.options.progressive_scene:
			case 0: # Lock Day 3, 5, 6 and 8 (2 items)
				if (day_id + 1) in (3, 5, 6, 8): how_many_to_append = 2
			case 1: # Lock Day 1 as well (also 2 items)
				if (day_id + 1) in (1, 3, 5, 6, 8): how_many_to_append = 2
			case 2: # Lock all Days to Scene 1
				how_many_to_append = 2
			case 3: # Actually lock all Days for real. Require several Progressive Scene items to fully unlock.
				how_many_to_append = CONST_DAY_SCENE_COUNT[day_id]

		if day_id in scene_deduct_list: how_many_to_append -= 1
		if how_many_to_append > 0:
			for count in range(how_many_to_append):
				item_pool.append(world.create_item(get_scene_unlock_name(day_id + 1)))

	# Generate all Item upgrades.
	# Check what kind of upgrade has been set in the Options.

	# Generate Treasure items, if possible and necessary.
	# Correct Treasure options here.


	# Finally, generate Filler.
	pass


CATEGORY_SCENE_PROGRESS = "Progressive Scene Unlocks"
CATEGORY_ITEM_LEVEL = "Cheat Item Level Up"
CATEGORY_ITEM_UPGRADE = "Cheat Item Upgrades"
CATEGORY_SUBITEM = "Sub-item Unlocks"
CATEGORY_USEFUL = "Useful"
CATEGORY_FILLER = "Filler"
CATEGORY_TRAP = "Traps"
CATEGORY_TREASURE = "Treasure"

# Some of the data here is automatically filled out with For loops below.
item_table: dict[str, ISCItemData] = {
	# Progression - ID 1-58
	# Day Unlock - ID 11
	CONST_PROGRESSIVE_DAY: ISCItemData(CATEGORY_SCENE_PROGRESS, 11, ItemClassification.progression),
	# Sub-item Slot Unlock - ID 30
	CONST_SUBITEM_SLOT_NAME: ISCItemData(CATEGORY_SUBITEM, 30, ItemClassification.progression),
	# Remove Level Cap Item - ID 31
	"Progressive Items: Remove Level Cap": ISCItemData(CATEGORY_ITEM_UPGRADE, 31, ItemClassification.progression),

	# Gold Hunt - ID 60-69
	CONST_TREASURE_ITEM_NAMES[0]: ISCItemData(CATEGORY_TREASURE, 60, ItemClassification.progression),
	CONST_TREASURE_ITEM_NAMES[1]: ISCItemData(CATEGORY_TREASURE, 61, ItemClassification.progression),
	CONST_TREASURE_ITEM_NAMES[2]: ISCItemData(CATEGORY_TREASURE, 62, ItemClassification.progression),

	# Useful - ID 70-79
	"Scene Skip": ISCItemData(CATEGORY_USEFUL, 70, ItemClassification.useful),
	CONST_TEMP_PREFIX + CONST_FILLER_NAME["invinc"]: ISCItemData(CATEGORY_USEFUL, 71, ItemClassification.useful),
	CONST_TEMP_PREFIX + CONST_FILLER_NAME["invinc2"]: ISCItemData(CATEGORY_USEFUL, 72, ItemClassification.useful),
	CONST_TEMP_PREFIX + CONST_FILLER_NAME["invinc3"]: ISCItemData(CATEGORY_USEFUL, 73, ItemClassification.useful),
	CONST_TEMP_PREFIX + CONST_FILLER_NAME["count_up"]: ISCItemData(CATEGORY_USEFUL, 74, ItemClassification.useful),
	CONST_TEMP_PREFIX + CONST_FILLER_NAME["count_up2"]: ISCItemData(CATEGORY_USEFUL, 75, ItemClassification.useful),

	# Traps - ID 80-99
	CONST_TEMP_PREFIX + CONST_FILLER_NAME["freeze"]: ISCItemData(CATEGORY_TRAP, 80, ItemClassification.trap),
	CONST_TEMP_PREFIX + CONST_FILLER_NAME["null_sub"]: ISCItemData(CATEGORY_TRAP, 81, ItemClassification.trap),
	CONST_TEMP_PREFIX + CONST_FILLER_NAME["count_down"]: ISCItemData(CATEGORY_TRAP, 82, ItemClassification.trap),
	CONST_TEMP_PREFIX + CONST_FILLER_NAME["count_down2"]: ISCItemData(CATEGORY_TRAP, 83, ItemClassification.trap),

	# Any above 100 is Useless Filler.
}

# Progressive Scene Unlocks - ID 1-10
for i in range(10):
	item_table[get_scene_unlock_name(i + 1)] = ISCItemData(CATEGORY_SCENE_PROGRESS, (i + 1), ItemClassification.progression)

for k in range(9):
	# Item Level Up - ID 12-20
	item_table[get_item_upgrade_name_id(k)] = ISCItemData(CATEGORY_ITEM_LEVEL, (12 + k), ItemClassification.progression)
	# Remove Level Cap Items for specific items - ID 21-29
	item_table[get_item_remove_cap(k)] = ISCItemData(CATEGORY_ITEM_UPGRADE, (21 + k), ItemClassification.progression)
	# Item Use Count Upgrades - ID 32-40
	item_table[get_item_name_usage(k)] = ISCItemData(CATEGORY_ITEM_UPGRADE, (32 + k), ItemClassification.progression)
	# Individual Sub-item Unlocks - ID 51-58
	item_table[get_item_name_subitem(k)] = ISCItemData(CATEGORY_SUBITEM, (51 + k), ItemClassification.progression)
	if k == 4: continue
	# Item Unique Stat Upgrades - ID 41-50 (no yin-yang upgrades)
	item_table[get_item_name_stat(k)] = ISCItemData(CATEGORY_ITEM_UPGRADE, (41 + k), ItemClassification.progression)

# Useless Filler - ID 100+
useless_filler_index: int = 100
for filler_useless_name in CONST_FILLER_USELESS_NAMES:
	filler_entry = f"{CONST_FILLER_USELESS_PREFIX}: {filler_useless_name}"
	item_table[filler_entry] = ISCItemData(CATEGORY_FILLER, useless_filler_index, ItemClassification.filler)
	useless_filler_index += 1