from rule_builder.rules import False_, True_
from .rules_utils import rule_require_day_access, rule_require_scene_access, rule_multiple_scene_access, get_scene_rule, \
	rule_require_day_clears, get_scene_rule_per_item, get_all_day_clears, get_nickname_rule, get_all_nickname_rules, \
	get_gold_hunt_rule
from ..world_locations.locations import get_fake_scene_name, get_fake_scene_access_name, check_if_scene_is_possible
from ...utils.utils_get_name import get_entrance_to_region_name, get_location_name_scene, get_location_name_music_room, \
	get_location_name_nickname, get_location_name_scene_with_item
from ...variables.game_stat_info import CONST_DAY_SCENE_COUNT
from ...variables.location_item_name import CONST_DAY_TO_ID, CONST_NICKNAME_NAME, CONST_ITEM_SHORT_TO_ID
from ..world_options.options_classes import CompletionType

def set_all_rules(world):
	set_entrance_rules(world)
	set_all_location_rules(world)
	set_goal_condition(world)

#
# ENTRANCES
#
def set_entrance_rules(world):
	origin_to_region_dict = {}

	for region_name in CONST_DAY_TO_ID.keys():
		origin_to_region_dict[region_name] = world.get_entrance(get_entrance_to_region_name(region_name))

	for region_entrance in origin_to_region_dict.keys():
		world.set_rule(
			spot=origin_to_region_dict[region_entrance],
			rule=rule_require_day_access(CONST_DAY_TO_ID[region_entrance])
		)

#
# LOCATIONS
#
def set_all_location_rules(world):
	set_generic_scene_clear_rules(world)
	set_item_scene_clear_rules(world)
	set_nickname_rules(world)
	set_music_room_rules(world)

def set_generic_scene_clear_rules(world):
	for day_id in range(10):
		for scene_id in range(CONST_DAY_SCENE_COUNT[day_id]):
			used_day_id: int = day_id + 1
			used_scene_id: int = scene_id + 1
			scene_specific_rule = get_scene_rule(day_id, scene_id)

			generic_scene_location = world.get_location(get_location_name_scene(
				day_number=used_day_id,
				scene_number=used_scene_id
			))
			world.set_rule(generic_scene_location, scene_specific_rule)

			# Set rule for event locations as well.
			# Scene clear event items.
			event_generic_location = world.get_location(get_fake_scene_name(
				day_id=used_day_id,
				scene_id=used_scene_id
			))
			world.set_rule(event_generic_location, scene_specific_rule)
			event_day_clear_location = world.get_location(get_fake_scene_name(
				day_id=used_day_id,
				scene_id=used_scene_id,
				dupe_index=1
			))
			world.set_rule(event_day_clear_location, scene_specific_rule)
			# Scene access event item.
			event_access_location = world.get_location(get_fake_scene_access_name(
				day_id=used_day_id,
				scene_id=used_scene_id
			))
			world.set_rule(event_access_location, rule_require_scene_access(
				day_id=used_day_id,
				scene_id=used_scene_id
			))

def set_item_scene_clear_rules(world):
	item_short_list = CONST_ITEM_SHORT_TO_ID.keys()
	for day_id in range(10):
		for scene_id in range(CONST_DAY_SCENE_COUNT[day_id]):
			used_day_id: int = day_id + 1
			used_scene_id: int = scene_id + 1
			for item_string_id in item_short_list:
				if not check_if_scene_is_possible(used_day_id, used_scene_id, item_string_id): continue
				used_item_id: int = CONST_ITEM_SHORT_TO_ID[item_string_id]
				item_specific_rule = get_scene_rule_per_item(
					day_id=used_day_id,
					scene_id=used_scene_id,
					item_string_id=item_string_id
				)

				event_item_location = world.get_location(get_fake_scene_name(
					day_id=used_day_id,
					scene_id=used_scene_id,
					with_item=used_item_id
				))
				world.set_rule(event_item_location, item_specific_rule)

				# Event locations are always run to ensure accessibility for achievements.
				# The real locations may not be included to spare players the pain of going through with them.
				if not world.options.include_item_clears: continue
				item_specific_location = world.get_location(get_location_name_scene_with_item(
					day_number=used_day_id,
					scene_number=used_scene_id,
					item_id=used_item_id
				))
				world.set_rule(item_specific_location, item_specific_rule)

def set_nickname_rules(world):
	"""
	Sets the rules for Nicknames.
	Cycles through ID 0 through 69 (there are 70 Nicknames total).
	"""
	nickname_total_count = len(CONST_NICKNAME_NAME)
	for nickname_id in range(nickname_total_count):
		# Special cases that can be automated.
		if nickname_id >= (nickname_total_count - 10) and not world.options.include_hidden_nicknames:
			continue
		nickname_location = world.get_location(get_location_name_nickname(nickname_id + 1))
		nickname_rule = get_nickname_rule(nickname_id)
		world.set_rule(nickname_location, nickname_rule)

def set_music_room_rules(world):
	if not world.options.include_music_checks: return
	for music_id in range(9):
		music_location = world.get_location(get_location_name_music_room(music_id + 1))
		music_rule = False_()
		match (music_id + 1):
			case 1: # Raise the Signal Fire of Cheating
				music_rule = True_()
			case 2: # Cheat Against the Impossible Danmaku
				music_rule = rule_multiple_scene_access((
					(1, 2), (2, 1)
				))
			case 3: # Midnight Spell Card
				music_rule = rule_multiple_scene_access((
					(3, 2), (4, 1)
				))
			case 4: # Romantic Escape Flight
				music_rule = rule_multiple_scene_access((
					(5, 2), (6, 2), (7, 1)
				))
			case 5: # Eternal Transient Reign
				music_rule = rule_multiple_scene_access((
					(8, 2), (9, 1), (10, 1)
				))
			case 6: # Mermaid from the Uncharted Land
				music_rule = rule_multiple_scene_access((
					(1, 1), (0, 0)
				))
			case 7: # Reverse Ideology
				music_rule = rule_multiple_scene_access((
					(3, 1), (8, 1)
				))
			case 8: # Illusionary Joururi
				music_rule = rule_multiple_scene_access((
					(5, 1), (0, 0)
				))
			case 9: # Youkai Mountain ~ Mysterious Mountain
				music_rule = rule_multiple_scene_access((
					(6, 1), (0, 0)
				))
			case _:
				music_rule = False_()
		world.set_rule(music_location, music_rule)

#
# GOAL
#
def set_goal_condition(world):
	completion_type = world.options.completion_type
	# Returns "Day 10, 4 Scenes" goal rule by default.
	completion_rule = rule_require_day_clears(10, 4)

	if completion_type == CompletionType.option_day_10_all_scenes:
		completion_rule = rule_require_day_clears(10, 10)
	elif completion_type == CompletionType.option_all_days_4_scenes:
		completion_rule = get_all_day_clears(4)
	elif completion_type == CompletionType.option_all_days_all_scenes:
		completion_rule = get_all_day_clears(10)
	elif completion_type == CompletionType.option_all_achievements_exclude:
		completion_rule = get_all_nickname_rules(60)
	elif completion_type == CompletionType.option_all_achievements_true:
		completion_rule = get_all_nickname_rules(70)
	elif completion_type == CompletionType.option_gold_rush:
		completion_rule = get_gold_hunt_rule(world.options.treasure_required)

	world.set_completion_rule(completion_rule)