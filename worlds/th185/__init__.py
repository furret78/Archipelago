from .WebWorld import TouhouHBMWebWorld
from .variables.boss_and_stage import STAGE2_NAME_FULL
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
    The marketplace god spoke.
    "The Ability Cards will inevitably spread, inevitably become obsolete,
    and the market will return to its everyday routine."
    But contrary to the god's intent, the value of the cards is somehow rising further and further.
    Could someone be manipulating their value?
    Or could it be because a select few collectors are buying up all the stock?
    When the card market had reached the utter peak of chaos,
    markets that the god couldn't intervene in--"black markets"--began to open.
    (from thpatch.net)
    """
    game = DISPLAY_NAME
    web = TouhouHBMWebWorld()

    location_name_to_id = Locations.location_table
    item_name_to_id = Items.get_item_to_id_dict()

    options_dataclass = HBMOptions.TouhouHBMDataclass
    options: HBMOptions.TouhouHBMDataclass

    origin_region_name = "Menu"

    item_name_groups = Items.get_item_groups()
    location_name_groups = Locations.location_groups

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
        data = {
            # Options
            "disable_challenge_logic": self.options.disable_challenge_logic.value,
            "trap_chance": self.options.trap_chance.value,
            "low_skill_logic": self.options.low_skill_logic.value,
            "death_link": self.options.death_link.value,
            "death_link_trigger": self.options.death_link_trigger.value,
            "death_link_invincibility": self.options.death_link_invincibility.value,
            "completion_type": self.options.completion_type.value,
            "include_gameplay_filler": self.options.include_gameplay_filler.value
        }
        return data