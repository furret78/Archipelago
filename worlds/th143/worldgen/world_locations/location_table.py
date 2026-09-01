from ...utils.utils_get_name import get_location_name_scene, get_location_name_scene_with_item, \
	get_location_name_nickname, get_location_name_music_room
from ...variables.game_stat_info import CONST_DAY_SCENE_COUNT
from ...variables.location_item_name import CONST_NICKNAME_NAME

location_groups: dict[str, set[str]] = {}

location_id_offset = 1
location_table = {} # Name to ID
location_table_reverse = {} # ID to Name

#
# 1. Generic Scene Clears
#
generic_scene_clear_range: tuple[int, int]

for generic_day_id in range(10):
	generic_day_group: set[str] = set()
	for generic_scene_id in range(CONST_DAY_SCENE_COUNT[generic_day_id]):
		generic_scene_str: str = get_location_name_scene(
			day_number=generic_day_id + 1,
			scene_number=generic_scene_id + 1
		)

		location_table[generic_scene_str] = location_id_offset
		location_table_reverse[location_id_offset] = generic_scene_str
		location_id_offset += 1

		generic_day_group.add(generic_scene_str)
	location_groups.update({f"Day {generic_day_id + 1} Common Clears": generic_day_group})

generic_scene_clear_range = (1, location_id_offset - 1)

#
# 2. Item-specific Scene Clears
#
item_scene_clear_range: tuple[int, int] = (location_id_offset, location_id_offset)

for item_day_id in range(10):
	item_day_group: set[str] = set()
	for item_scene_id in range(CONST_DAY_SCENE_COUNT[item_day_id]):
		for item_clear_id in range(10):
			item_scene_str: str = get_location_name_scene_with_item(
				day_number=item_day_id + 1,
				scene_number=item_scene_id + 1,
				item_id=item_clear_id
			)

			location_table[item_scene_str] = location_id_offset
			location_table_reverse[location_id_offset] = item_scene_str
			location_id_offset += 1

			item_day_group.add(item_scene_str)

	location_groups.update({f"Day {item_day_id + 1} Item Clears": item_day_group})

item_scene_clear_range = (item_scene_clear_range[0], location_id_offset - 1)

#
# 3. Nicknames
#
nickname_location_range: tuple[int, int] = (location_id_offset, location_id_offset)

CONST_TOTAL_NICKNAME_COUNT = len(CONST_NICKNAME_NAME)
common_nickname_group: set[str] = set()
hidden_nickname_group: set[str] = set()
for nickname_id in range(CONST_TOTAL_NICKNAME_COUNT):
	nickname_str: str = get_location_name_nickname(nickname_id + 1)

	location_table[nickname_str] = location_id_offset
	location_table_reverse[location_id_offset] = nickname_str
	location_id_offset += 1

	if nickname_id < (CONST_TOTAL_NICKNAME_COUNT - 11): common_nickname_group.add(nickname_str)
	else: hidden_nickname_group.add(nickname_str)
location_groups.update({
	"Visible Nicknames": common_nickname_group,
	"Hidden Nicknames": hidden_nickname_group
})

nickname_location_range = (nickname_location_range[0], location_id_offset - 1)

#
# 4. Music Room
#
music_location_range: tuple[int, int] = (location_id_offset, location_id_offset)

music_room_group: set[str] = set()
for music_id in range(9):
	music_str: str = get_location_name_music_room(music_id + 1)

	location_table[music_str] = location_id_offset
	location_table_reverse[location_id_offset] = music_str
	location_id_offset += 1

	music_room_group.add(music_str)
location_groups.update({"Music Room": music_room_group})

music_location_range = (music_location_range[0], location_id_offset - 1)