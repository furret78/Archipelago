from typing import Mapping, Any

from worlds.AutoWorld import World
from .client import options
from .variables.game_info import DISPLAY_NAME
from .worldgen import regions, items
from .worldgen.world_locations import location_table
from .worldgen.world_locations import locations
from .worldgen.world_rules import rules


class ISCWorld(World):
	"""
	The amanojaku, Seija Kijin.
	She used the treasure of the inchlings, the "Miracle Mallet", in an attempt to conquer Gensokyo.
	Though her plot ended in failure, she would not give up yet.
	Knowing that the Mallet's magic had caused items to move on their own,
	she secretly gathered those items unbeknownst to their owners.
	"If I collect the remaining magic in these, then maybe..."
	But some way or another, that plot was found out as well.
	One by one, youkai began to appear before her, deeming her a rebel plotting an upheaval of Gensokyo's society.
	The youkai would show no regard for rules in their danmaku.
	You don't need to hesitate; Drive them away with the cursed tools!
	(from en.touhouwiki.net)
	"""
	game = DISPLAY_NAME

	location_name_to_id = location_table.location_table
	location_id_to_name = location_table.location_table_reverse
	item_name_to_id = items.get_item_to_id_dict()

	options_dataclass = options.ISCDataclass
	options: options.ISCDataclass

	origin_region_name = "Menu"

	item_name_groups = items.get_item_groups()
	location_name_groups = location_table.location_groups

	def generate_early(self) -> None:
		if self.options.skill_difficulty.value != 1:
			self.options.skill_difficulty.value = 1
		if self.options.include_itemless_logic:
			self.options.include_itemless_logic.value = False

	def create_regions(self):
		regions.create_and_connect_regions(self)
		locations.create_all_locations(self)

	def set_rules(self) -> None:
		rules.set_all_rules(self)

	def create_items(self) -> None:
		items.create_all_items(self)

	def create_item(self, name: str) -> items.ISCItem:
		return items.create_item_with_correct_classification(self, name)

	def get_filler_item_name(self) -> str:
		return items.get_random_filler_item_name(self)

	# The place where player data goes.
	def fill_slot_data(self) -> Mapping[str, Any]:
		data = {
			"skill_difficulty": self.options.skill_difficulty.value,
			"trap_chance": self.options.trap_chance.value,
			"trap_blacklist": self.options.trap_blacklist.value,
			"death_link": self.options.death_link.value,
			"death_link_amnesty": self.options.death_link_amnesty.value,
			"death_link_anti": self.options.death_link_anti.value,
			"completion_type": self.options.completion_type.value,
			"treasure_required": self.options.treasure_required.value,
			"treasure_percent": self.options.treasure_percent.value,
			"progressive_day": self.options.progressive_day.value,
			"progressive_scene": self.options.progressive_scene.value,
			"starting_day": self.options.starting_day.value,
			"starting_day_random_range": self.options.starting_day_random_range.value,
			"valid_starting_days": self.options.valid_starting_days.value,
			"item_upgrade_progress": self.options.item_upgrade_progress.value,
			"item_upgrade_separate": self.options.item_upgrade_separate.value,
			"item_upgrade_remove_cap": self.options.item_upgrade_remove_cap.value,
			"subitem_slot_unlock": self.options.subitem_slot_unlock.value,
			"subitem_individual": self.options.subitem_individual.value,
			"scene_skip_count": self.options.scene_skip_count.value,
			"include_music_checks": self.options.include_music_checks.value,
			"include_itemless_logic": self.options.include_itemless_logic.value,
			"include_item_clears": self.options.include_item_clears.value,
			"include_hidden_nicknames": self.options.include_hidden_nicknames.value
		}
		return data