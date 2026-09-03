from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld
from ..variables.game_info import DISPLAY_NAME
from ..worldgen.world_options.options import option_groups, option_presets


class ISCWebWorld (WebWorld):
	game = DISPLAY_NAME
	theme = "partyTime"

	setup_en = [Tutorial(
		"Multiworld Setup Guide",
		"A guide to setting up Impossible Spell Card for Archipelago.",
		"English",
		"setup_en.md",
		"setup/en",
		["Yuureiki"]
	)]

	tutorials = [setup_en]

	option_groups = option_groups
	options_presets = option_presets