from .variables.meta_data import SHORT_NAME, DISPLAY_NAME
from ..LauncherComponents import Component, components, launch_subprocess, Type, icon_paths
from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World
from . import Locations, Items, Options as HBMOptions, Regions, Rules
from .variables.meta_data import *

def launch_client():
    """
    Launch a Client instance.
    """
    from .Client import launch
    launch_subprocess(launch, name="GameClient")

components.append(Component(
    display_name=SHORT_NAME+" Client",
    func=launch_client,
    component_type=Type.CLIENT,
    game_name=DISPLAY_NAME,
    icon="th185_card"
))

icon_paths["th185_card"] = f"ap:{__name__}/icons/th185_card.png"

class TouhouHBMWorld(World):
    """
    Touhou 18.5: 100th Black Market
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
            "starting_market": self.options.starting_market.value,
            "challenge_checks": self.options.challenge_checks.value,
            "disable_challenge_logic": self.options.disable_challenge_logic.value,
            "card_dex_checks": self.options.card_dex_checks.value,
            "trap_chance": self.options.trap_chance.value,
            "starting_card": self.options.starting_card.value,
            "completion_type": self.options.completion_type.value,
        }
        return data