from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World
from . import Locations, Items, OptionsHBM as HBMOptions, Regions, Rules
from .variables.meta_data import *

class TouhouHBMWorld(World):
    """
    Touhou 18.5
    """
    game = DISPLAY_NAME
    # web world here

    location_name_to_id = Locations.location_table
    item_name_to_id = Items.get_item_to_id_dict()

    options_dataclass = HBMOptions.TouhouHBMDataclass
    options: HBMOptions.TouhouHBMDataclass

    origin_region_name = "Menu"

    def create_regions(self):
        Regions.create_and_connect_regions(self)
        Locations.create_all_locations(self)

    def set_rules(self) -> None:
        Rules.set_all_rules(self)

    def create_items(self) -> None:
        Items.create_all_items(self)

    def create_item(self, name: str) -> Items.TouhouHBMItem:
        return Items.create_item_with_correct_classification(self, name)

    def get_filler_item_name(self) -> str:
        return Items.get_random_filler_item_name(self)

    # The place where player data goes.
    def fill_slot_data(self) -> Mapping[str, Any]:
        # List that shows which cards should have the "New!" tag.
        # Does not affect gameplay but it is nice eye-candy.
        data = {
            # Options
            "challenge_checks": self.options.challenge_checks,
            "card_dex_checks": self.options.card_dex_checks,
            "trap_chance": self.options.trap_chance,
            "starting_card": self.options.starting_card,
            "completion_type": self.options.completion_type,
            # This is for eye-candy. List contains the string IDs of cards marked as "New!" in the game.
            "card_shop_new": self.card_shop_new,
            # Card Shop dictionary does not exist. Use the list of acquired Ability Card Items for that.
            # Dex dictionary does not exist. Use the list of acquired checks for that.
            # Owning a card and unlocking its dex entry is one and the same,
            # but it is separate for the player.
        }
        return data