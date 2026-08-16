from typing import Dict, NamedTuple, Optional

from BaseClasses import Item, ItemClassification
from . import get_progress_item_count
from .variables.card_const import *
from .variables.boss_and_stage import *
from .variables.meta_data import DISPLAY_NAME

CATEGORY_ITEM = "Limited Items"
CATEGORY_FILLER = "Filler"
CATEGORY_STAGE = "Stages"
CATEGORY_TRAP = "Traps"
CATEGORY_CARD = "Ability Cards"
CATEGORY_PROGRESS = "Stage Progress"
CATEGORY_PERMA = "Permanent Upgrades"


class TouhouHBMItem(Item):
    game: str = DISPLAY_NAME


class TouhouHBMItemData(NamedTuple):
    category: str
    code: Optional[int] = None
    classification: ItemClassification = ItemClassification.filler
    max_quantity: int = 1
    weight: int = 1


def get_items_by_category(category: str) -> Dict[str, TouhouHBMItemData]:
    item_dict: Dict[str, TouhouHBMItemData] = {}
    for name, data in item_table.items():
        if data.category == category:
            item_dict.setdefault(name, data)

    return item_dict


def get_card_string_id_by_code(code: int) -> str:
    if code < 200 or code >= 200 + ITEM_TABLE_ID_TO_CARD_ID.__sizeof__(): return "Invalid."
    return ITEM_TABLE_ID_TO_CARD_ID.get(code)


def get_random_filler_item_name(world) -> str:
    filler_item_list = []

    for name in get_items_by_category(CATEGORY_ITEM).keys():
        filler_item_list.append(name)
    for name in get_items_by_category(CATEGORY_FILLER).keys():
        # Check if generation options allow for non-money filler.
        if not world.options.include_gameplay_filler:
            if check_for_nonmoney_filler(item_table[name].code): continue

        filler_item_list.append(name)

    final_item_name: str = world.random.choice(filler_item_list).__str__()

    # Check if it should be a trap instead.
    trap_item_list = []
    for name in get_items_by_category(CATEGORY_TRAP).keys():
        given_item_code = item_table[name].code
        if not world.options.include_gameplay_filler and check_for_nonmoney_filler(given_item_code): continue
        if name in world.options.trap_blacklist: continue
        trap_item_list.append(name)
    if world.random.randint(0, 99) < world.options.trap_chance:
        final_item_name = world.random.choice(trap_item_list).__str__()

    return final_item_name


def get_item_to_id_dict() -> Dict[str, int]:
    item_dict: Dict[str, int] = {}
    for name, data in item_table.items():
        item_dict.setdefault(name, data.code)
    return item_dict


# Special Item check for Capitalist's Dilemma and Blank Card.
# See the string IDs for Ability Cards in card_const.py
def check_if_story_relevant(card_id: str) -> bool:
    return card_id == NITORI_STORY_CARD or card_id == TAKANE_STORY_CARD


def create_item_with_correct_classification(world, item_name: str) -> TouhouHBMItem:
    classification = item_table[item_name].classification

    return TouhouHBMItem(
        item_name,
        classification,
        item_table[item_name].code,
        world.player
    )


def create_all_items(world):
    """
    Generates an item pool to submit to AP.
    """
    def get_remaining_locations(the_pool: list[Item]):
        number_of_items = len(the_pool)
        number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
        return number_of_unfilled_locations - number_of_items

    # Initialization
    item_pool: list[Item] = []

    # Stage unlocks get added first.
    # First, check if the player wants Progressive Stages.
    if not world.options.progressive_stages:
        starting_stage_full_name = STAGE_SHORT_TO_FULL_NAME[STAGE_ID_TO_SHORT_NAME[world.options.starting_market]]
        stage_unlock_item_dict = get_items_by_category(CATEGORY_STAGE)
        for name in stage_unlock_item_dict.keys():
            if name == starting_stage_full_name: continue
            item_pool.append(world.create_item(name))
    # If stages should be progressive, only add as many progressive stage items as needed.
    else:
        progress_items_to_submit: int = 9 - get_progress_item_count(world.options.starting_market)
        if progress_items_to_submit > 0:
            progress_item_number = 0
            while progress_item_number < progress_items_to_submit:
                item_pool.append(world.create_item(PROGRESS_STAGE_ITEM_NAME))
                progress_item_number += 1

    # Ability Cards get added next.
    # There are checks to make sure it doesn't submit the Starting Card (if there are any).
    ability_card_item_dict = get_items_by_category(CATEGORY_CARD)
    for ability_card_name, data in ability_card_item_dict.items():
        # Get the String ID of the cards.
        string_id = ITEM_TABLE_ID_TO_CARD_ID[data.code]

        # Remove cards that obviously cannot be equipped at start.
        if string_id in ABILITY_CARD_CANNOT_EQUIP:
            continue

        # Grab full name of item and create.
        item_pool.append(world.create_item(CARD_ID_TO_NAME[string_id]))

    # Finally, Progressive Loadout.
    # This is the least important of the important things.
    # If it's disabled, nothing happens here.
    match world.options.progressive_loadout:
        case 1: # Upgrades go hand-in-hand.
            for prog_item_num in range(world.options.progressive_loadout_count):
                item_pool.append(world.create_item(PROGRESS_EQUIP_NAME))
        case 2: # Upgrades go separately.
            for i in range(world.options.progressive_slot_count):
                item_pool.append(world.create_item(PROGRESS_SLOT_NAME))
            for i in range(world.options.progressive_cost_count):
                item_pool.append(world.create_item(PROGRESS_COST_NAME))

    # Now that all the important stuff is added, check if there's any spots left.
    remaining_locations = get_remaining_locations(item_pool)

    # If there are any left, pad out the pool with filler items.
    # First of all are the permanent upgrade items. Check if the option for them is enabled.
    # If not, skip over to true fillers.
    if world.options.perma_upgrade_toggle:
        # A limit has been set.
        perma_item_dict = get_perma_upgrade_counts(world)
        perma_remain_index = 0
        # Iterate through all five permanent upgrade items.
        # As long as the index does not reach the limit, keep adding.
        # If the index does not reach the limit by the time we finish adding upgrade items... Great success!
        for upgrade_name, upgrade_count in perma_item_dict.items():
            if perma_remain_index >= remaining_locations: break
            for perma_item_count in range(upgrade_count):
                if perma_remain_index >= remaining_locations: break
                item_pool.append(world.create_item(upgrade_name))
                perma_remain_index += 1

        # Once this is done, check for remaining locations again.
        remaining_locations = get_remaining_locations(item_pool)

    # Useful and filler are the same here, but useful has limits.
    # Initialize a dictionary for checking useful limits, while there is no need for filler.
    # The default value is set to max, subtracted every time the filler has been added.
    # Once it reaches 0, that filler cannot be added anymore.
    filler_limit_dict = {}
    useful_item_dict = get_items_by_category(CATEGORY_ITEM)
    for name, data in useful_item_dict.items():
        filler_limit_dict[name] = data.max_quantity

    # Filler limit has been set. Do RNG to get filler names.
    remain_index = 0
    while remain_index < remaining_locations:
        filler_item_name = world.get_filler_item_name()

        # If the filler item is useful, but it has reached its limit, do not increase index.
        if filler_item_name in filler_limit_dict and filler_limit_dict[filler_item_name] <= 0:
            continue

        item_pool.append(world.create_item(filler_item_name))
        remain_index += 1

        # If the filler item is useful, remove 1 count from the limit dictionary.
        if filler_item_name in filler_limit_dict: filler_limit_dict[filler_item_name] -= 1

    # Submit item pool for the randomizer.
    world.multiworld.itempool += item_pool

# Item groups.
def get_item_groups() -> dict[str, set[str]]:
    item_groups: Dict[str, set[str]] = {}

    item_group_list = [CATEGORY_CARD, CATEGORY_STAGE, CATEGORY_PROGRESS, CATEGORY_PERMA, CATEGORY_TRAP, CATEGORY_ITEM, CATEGORY_FILLER]

    for category in item_group_list:
        category_dict = get_items_by_category(category)
        category_group: set[str] = set()
        for entry in category_dict.keys():
            category_group.add(entry)
        item_groups.update({category: category_group})

    return item_groups

def check_for_game_filler(given_item_id: int):
    """
    If True, it's filler only for stages.
    """
    if 16 < given_item_id < 100: return True
    elif given_item_id >= 300: return True

    return False

def check_for_nonmoney_filler(given_item_id: int):
    """
    If True, it's not money filler.
    """
    return given_item_id > 36

def check_for_enduring_trap_filler(given_item_id: int):
    """
    If True, it's an Enduring Trap.
    """
    return 400 <= given_item_id < 500


def check_for_extreme_trap_filler(given_item_id: int):
    """
    If True, it's an Extreme Trap.
    """
    return given_item_id >= 500

def get_perma_upgrade_counts(world):
    """
    Returns a dictionary consisting of five permanent upgrade items and their counts as given in options.
    """
    return {
        PERMA_LIFE_NAME: world.options.perma_upgrade_life,
        PERMA_BM_NAME: world.options.perma_upgrade_bm,
        PERMA_POWER_NAME: world.options.perma_upgrade_power,
        PERMA_ATK_NAME: world.options.perma_upgrade_atk,
        PERMA_MAGIC_ATK_NAME: world.options.perma_upgrade_magic_atk,
    }

# An Item table documenting every Item and its data.
# If anything new is added, add it to Client.py under give_item()
# as well as add entries to the other tables below here.
item_table: Dict[str, TouhouHBMItemData] = {
    # FILLER
    # Money Filler and Traps - ID 1-29
    "+5 Funds": TouhouHBMItemData(CATEGORY_FILLER, 1),
    "+10 Funds": TouhouHBMItemData(CATEGORY_FILLER, 2),
    "+200 Funds": TouhouHBMItemData(CATEGORY_ITEM, 3, ItemClassification.useful, 10),
    "+500 Funds": TouhouHBMItemData(CATEGORY_ITEM, 4, ItemClassification.useful, 4),
    "+1000 Funds": TouhouHBMItemData(CATEGORY_ITEM, 5, ItemClassification.useful, 2),
    "+2000 Funds": TouhouHBMItemData(CATEGORY_ITEM, 6, ItemClassification.useful, 2),
    "+5000 Funds": TouhouHBMItemData(CATEGORY_ITEM, 7, ItemClassification.useful, 2),
    "+8000 Funds": TouhouHBMItemData(CATEGORY_ITEM, 8, ItemClassification.useful, 1),

    "-50 Funds Trap": TouhouHBMItemData(CATEGORY_TRAP, 10, ItemClassification.trap),
    "-100 Funds Trap": TouhouHBMItemData(CATEGORY_TRAP, 11, ItemClassification.trap),
    "-200 Funds Trap": TouhouHBMItemData(CATEGORY_TRAP, 12, ItemClassification.trap),
    "-300 Funds Trap": TouhouHBMItemData(CATEGORY_TRAP, 13, ItemClassification.trap),
    "-500 Funds Trap": TouhouHBMItemData(CATEGORY_TRAP, 14, ItemClassification.trap),
    "-1000 Funds Trap": TouhouHBMItemData(CATEGORY_TRAP, 15, ItemClassification.trap),
    "-2000 Funds Trap": TouhouHBMItemData(CATEGORY_TRAP, 16, ItemClassification.trap),
    "-3000 Funds Trap": TouhouHBMItemData(CATEGORY_TRAP, 17, ItemClassification.trap),

    ONCE_ITEM_TAG + "+5 Bullet Money": TouhouHBMItemData(CATEGORY_FILLER, 20),
    ONCE_ITEM_TAG + "+10 Bullet Money": TouhouHBMItemData(CATEGORY_FILLER, 21),
    ONCE_ITEM_TAG + "+200 Bullet Money": TouhouHBMItemData(CATEGORY_ITEM, 22, ItemClassification.useful, 10),
    ONCE_ITEM_TAG + "+500 Bullet Money": TouhouHBMItemData(CATEGORY_ITEM, 23, ItemClassification.useful, 8),
    ONCE_ITEM_TAG + "+1000 Bullet Money": TouhouHBMItemData(CATEGORY_ITEM, 24, ItemClassification.useful, 6),
    ONCE_ITEM_TAG + "+2000 Bullet Money": TouhouHBMItemData(CATEGORY_ITEM, 25, ItemClassification.useful, 4),
    ONCE_ITEM_TAG + "+5000 Bullet Money": TouhouHBMItemData(CATEGORY_ITEM, 26, ItemClassification.useful, 2),
    ONCE_ITEM_TAG + "+8000 Bullet Money": TouhouHBMItemData(CATEGORY_ITEM, 27, ItemClassification.useful, 2),

    ONCE_ITEM_TAG + "-50 Bullet Money Trap": TouhouHBMItemData(CATEGORY_TRAP, 30, ItemClassification.trap),
    ONCE_ITEM_TAG + "-100 Bullet Money Trap": TouhouHBMItemData(CATEGORY_TRAP, 31, ItemClassification.trap),
    ONCE_ITEM_TAG + "-200 Bullet Money Trap": TouhouHBMItemData(CATEGORY_TRAP, 32, ItemClassification.trap),
    ONCE_ITEM_TAG + "-300 Bullet Money Trap": TouhouHBMItemData(CATEGORY_TRAP, 33, ItemClassification.trap),
    ONCE_ITEM_TAG + "-500 Bullet Money Trap": TouhouHBMItemData(CATEGORY_TRAP, 34, ItemClassification.trap),
    ONCE_ITEM_TAG + "-1000 Bullet Money Trap": TouhouHBMItemData(CATEGORY_TRAP, 35, ItemClassification.trap),
    ONCE_ITEM_TAG + "-2000 Bullet Money Trap": TouhouHBMItemData(CATEGORY_TRAP, 36, ItemClassification.trap),
    ONCE_ITEM_TAG + "-5000 Bullet Money Trap": TouhouHBMItemData(CATEGORY_TRAP, 37, ItemClassification.trap),

    # Lives Filler and Traps - ID 30
    ONCE_ITEM_TAG + "+1 Life": TouhouHBMItemData(CATEGORY_ITEM, 38, ItemClassification.useful, 8),
    ONCE_ITEM_TAG + "+2 Lives": TouhouHBMItemData(CATEGORY_ITEM, 39, ItemClassification.useful, 5),

    # STAGE FILLER
    # Shot Attack Filler and Traps - ID 40-49
    ONCE_ITEM_TAG + "+15% Shot Attack": TouhouHBMItemData(CATEGORY_FILLER, 40),
    ONCE_ITEM_TAG + "+30% Shot Attack": TouhouHBMItemData(CATEGORY_FILLER, 41),
    ONCE_ITEM_TAG + "+45% Shot Attack": TouhouHBMItemData(CATEGORY_ITEM, 42, ItemClassification.useful, 5),
    ONCE_ITEM_TAG + "+60% Shot Attack": TouhouHBMItemData(CATEGORY_ITEM, 43, ItemClassification.useful, 4),
    ONCE_ITEM_TAG + "+100% Shot Attack": TouhouHBMItemData(CATEGORY_ITEM, 44, ItemClassification.useful, 3),
    ONCE_ITEM_TAG + "+200% Shot Attack": TouhouHBMItemData(CATEGORY_ITEM, 45, ItemClassification.useful, 2),
    ONCE_ITEM_TAG + "+300% Shot Attack": TouhouHBMItemData(CATEGORY_ITEM, 46, ItemClassification.useful, 1),
    ONCE_ITEM_TAG + "+400% Shot Attack": TouhouHBMItemData(CATEGORY_ITEM, 47, ItemClassification.useful, 1),
    TEMP_TRAP_TAG + "-30% Shot Attack Trap": TouhouHBMItemData(CATEGORY_TRAP, 48, ItemClassification.trap),
    TEMP_TRAP_TAG + "-60% Shot Attack Trap": TouhouHBMItemData(CATEGORY_TRAP, 49, ItemClassification.trap),
    # Magic Circle Attack Filler and Traps - ID 50-59
    ONCE_ITEM_TAG + "+30% Magic Circle Attack": TouhouHBMItemData(CATEGORY_FILLER, 50),
    ONCE_ITEM_TAG + "+60% Magic Circle Attack": TouhouHBMItemData(CATEGORY_FILLER, 51),
    ONCE_ITEM_TAG + "+90% Magic Circle Attack": TouhouHBMItemData(CATEGORY_FILLER, 52),
    ONCE_ITEM_TAG + "+120% Magic Circle Attack": TouhouHBMItemData(CATEGORY_FILLER, 53),
    TEMP_TRAP_TAG + "-15% Magic Circle Attack Trap": TouhouHBMItemData(CATEGORY_TRAP, 54, ItemClassification.trap),
    TEMP_TRAP_TAG + "-30% Magic Circle Attack Trap": TouhouHBMItemData(CATEGORY_TRAP, 55, ItemClassification.trap),
    TEMP_TRAP_TAG + "-45% Magic Circle Attack Trap": TouhouHBMItemData(CATEGORY_TRAP, 56, ItemClassification.trap),
    TEMP_TRAP_TAG + "-60% Magic Circle Attack Trap": TouhouHBMItemData(CATEGORY_TRAP, 57, ItemClassification.trap),
    # Magic Circle Size Filler and Traps - ID 60-69
    ONCE_ITEM_TAG + "+10% Magic Circle Size": TouhouHBMItemData(CATEGORY_FILLER, 60),
    ONCE_ITEM_TAG + "+20% Magic Circle Size": TouhouHBMItemData(CATEGORY_FILLER, 61),
    ONCE_ITEM_TAG + "+30% Magic Circle Size": TouhouHBMItemData(CATEGORY_FILLER, 62),
    ONCE_ITEM_TAG + "+50% Magic Circle Size": TouhouHBMItemData(CATEGORY_FILLER, 63),
    TEMP_TRAP_TAG + "-10% Magic Circle Size Trap": TouhouHBMItemData(CATEGORY_TRAP, 64, ItemClassification.trap),
    TEMP_TRAP_TAG + "-20% Magic Circle Size Trap": TouhouHBMItemData(CATEGORY_TRAP, 65, ItemClassification.trap),
    TEMP_TRAP_TAG + "-30% Magic Circle Size Trap": TouhouHBMItemData(CATEGORY_TRAP, 66, ItemClassification.trap),
    TEMP_TRAP_TAG + "-50% Magic Circle Size Trap": TouhouHBMItemData(CATEGORY_TRAP, 67, ItemClassification.trap),
    # Magic Circle Duration Filler and Traps - ID 70-79
    ONCE_ITEM_TAG + "+5% Magic Circle Duration": TouhouHBMItemData(CATEGORY_FILLER, 70),
    ONCE_ITEM_TAG + "+10% Magic Circle Duration": TouhouHBMItemData(CATEGORY_FILLER, 71),
    TEMP_TRAP_TAG + "+100% Magic Circle Duration Trap": TouhouHBMItemData(CATEGORY_TRAP, 72, ItemClassification.trap),
    TEMP_TRAP_TAG + "+200% Magic Circle Duration Trap": TouhouHBMItemData(CATEGORY_TRAP, 73, ItemClassification.trap),
    # Magic Circle Graze Range Filler and Traps - ID 80-89
    ONCE_ITEM_TAG + "+20% Magic Circle Graze Range": TouhouHBMItemData(CATEGORY_FILLER, 80),
    ONCE_ITEM_TAG + "+40% Magic Circle Graze Range": TouhouHBMItemData(CATEGORY_FILLER, 81),
    ONCE_ITEM_TAG + "+60% Magic Circle Graze Range": TouhouHBMItemData(CATEGORY_FILLER, 82),
    ONCE_ITEM_TAG + "+80% Magic Circle Graze Range": TouhouHBMItemData(CATEGORY_FILLER, 83),
    ONCE_ITEM_TAG + "+100% Magic Circle Graze Range": TouhouHBMItemData(CATEGORY_FILLER, 84),
    TEMP_TRAP_TAG + "-15% Magic Circle Graze Range Trap": TouhouHBMItemData(CATEGORY_TRAP, 85, ItemClassification.trap),
    TEMP_TRAP_TAG + "-30% Magic Circle Graze Range Trap": TouhouHBMItemData(CATEGORY_TRAP, 86, ItemClassification.trap),
    TEMP_TRAP_TAG + "-45% Magic Circle Graze Range Trap": TouhouHBMItemData(CATEGORY_TRAP, 87, ItemClassification.trap),
    TEMP_TRAP_TAG + "-60% Magic Circle Graze Range Trap": TouhouHBMItemData(CATEGORY_TRAP, 88, ItemClassification.trap),
    TEMP_TRAP_TAG + "-75% Magic Circle Graze Range Trap": TouhouHBMItemData(CATEGORY_TRAP, 89, ItemClassification.trap),
    # Movement Speed Filler and Traps
    ONCE_ITEM_TAG + "+20% Movement Speed": TouhouHBMItemData(CATEGORY_FILLER, 90),
    TEMP_TRAP_TAG + "Extreme Speed Trap": TouhouHBMItemData(CATEGORY_TRAP, 91, ItemClassification.trap),
    TEMP_TRAP_TAG + "Magic Circle Disable Trap": TouhouHBMItemData(CATEGORY_TRAP, 92, ItemClassification.trap),
    TEMP_TRAP_TAG + "Freeze Trap": TouhouHBMItemData(CATEGORY_TRAP, 93, ItemClassification.trap),
    TEMP_TRAP_TAG + "Powerless Shot Trap": TouhouHBMItemData(CATEGORY_TRAP, 94, ItemClassification.trap),
    # Invincibility Filler and Traps
    ONCE_ITEM_TAG + "2-second Invincibility": TouhouHBMItemData(CATEGORY_FILLER, 95), # 120 in int (60 = 1s)
    ONCE_ITEM_TAG + "5-second Invincibility": TouhouHBMItemData(CATEGORY_FILLER, 96), # 300 in int
    ONCE_ITEM_TAG + "7-second Invincibility": TouhouHBMItemData(CATEGORY_FILLER, 97), # 420
    ONCE_ITEM_TAG + "10-second Invincibility": TouhouHBMItemData(CATEGORY_FILLER, 98), # 600
    TEMP_TRAP_TAG + "Invincibility Cancel Trap": TouhouHBMItemData(CATEGORY_TRAP, 99, ItemClassification.trap),

    # EVIL TRAPS - ID 500+
    # Massively screws you over. One-and-done.
    # It is still possible to finish the stage as it is, but it will be greatly difficult.
    # Can override temporary traps.
    ONCE_ITEM_TAG + "Funds Reset Trap": TouhouHBMItemData(CATEGORY_TRAP, 500, ItemClassification.trap),
    ONCE_ITEM_TAG + "Bullet Money Reset Trap": TouhouHBMItemData(CATEGORY_TRAP, 501, ItemClassification.trap),
    ONCE_ITEM_TAG + "20% Shot Attack Trap": TouhouHBMItemData(CATEGORY_TRAP, 502, ItemClassification.trap),
    ONCE_ITEM_TAG + "0% Magic Circle Attack Trap": TouhouHBMItemData(CATEGORY_TRAP, 503, ItemClassification.trap),
    ONCE_ITEM_TAG + "1000% Magic Circle Duration Trap": TouhouHBMItemData(CATEGORY_TRAP, 504, ItemClassification.trap),
    ONCE_ITEM_TAG + "Shot Power Reset Trap": TouhouHBMItemData(CATEGORY_TRAP, 505, ItemClassification.trap),

    # STAGE UNLOCKS
    TUTORIAL_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 100, ItemClassification.progression),
    STAGE1_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 101, ItemClassification.progression),
    STAGE2_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 102, ItemClassification.progression),
    STAGE3_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 103, ItemClassification.progression),
    STAGE4_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 104, ItemClassification.progression),
    STAGE5_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 105, ItemClassification.progression),
    STAGE6_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 106, ItemClassification.progression),
    ENDSTAGE_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 107, ItemClassification.progression),
    CHALLENGE_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 108, ItemClassification.progression),

    # ABILITY CARD SHOP UNLOCKS
    LIFE_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 200, ItemClassification.progression),
    YUKARI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 201, ItemClassification.progression),
    EIRIN_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 202, ItemClassification.progression),
    TEWI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 203, ItemClassification.progression),
    REIMU_CARD_1_NAME: TouhouHBMItemData(CATEGORY_CARD, 204, ItemClassification.progression),
    NITORI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 205, ItemClassification.progression),
    KANAKO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 206, ItemClassification.progression),
    ALICE_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 207, ItemClassification.progression),
    CIRNO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 208, ItemClassification.progression),
    YOUMU_CARD_1_NAME: TouhouHBMItemData(CATEGORY_CARD, 209, ItemClassification.progression),
    YOUMU_CARD_2_NAME: TouhouHBMItemData(CATEGORY_CARD, 210, ItemClassification.progression),
    SAKI_BIGSHOT_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 211, ItemClassification.progression),
    KOISHI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 212, ItemClassification.progression),
    TENSHI_SHIELD_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 213, ItemClassification.progression),
    MALLET_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 214, ItemClassification.progression),
    MOKOU_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 215, ItemClassification.progression),
    RINGO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 216, ItemClassification.progression),
    MIKE_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 217, ItemClassification.progression),
    TAKANE_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 218, ItemClassification.progression),
    SANNYO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 219, ItemClassification.progression),
    BYAKUREN_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 220, ItemClassification.progression),
    MOON_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 221, ItemClassification.progression),
    BLANK_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 222, ItemClassification.progression),
    SANAE_CARD_1_NAME: TouhouHBMItemData(CATEGORY_CARD, 223, ItemClassification.progression),
    MARISA_CARD_1_NAME: TouhouHBMItemData(CATEGORY_CARD, 224, ItemClassification.progression),
    SAKUYA_CARD_1_NAME: TouhouHBMItemData(CATEGORY_CARD, 225, ItemClassification.progression),
    OKINA_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 226, ItemClassification.progression),
    UFO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 227, ItemClassification.progression),
    SUWAKO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 228, ItemClassification.progression),
    AYA_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 229, ItemClassification.progression),
    MAYUMI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 230, ItemClassification.progression),
    KAGUYA_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 231, ItemClassification.progression),
    MIKO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 232, ItemClassification.progression),
    MAMIZOU_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 233, ItemClassification.progression),
    YUYUKO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 234, ItemClassification.progression),
    YACHIE_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 235, ItemClassification.progression),
    REMILIA_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 236, ItemClassification.progression),
    UTSUHO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 237, ItemClassification.progression),
    LILY_WHITE_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 238, ItemClassification.progression),
    EIKI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 239, ItemClassification.progression),
    REIMU_CARD_2_NAME: TouhouHBMItemData(CATEGORY_CARD, 240, ItemClassification.progression),
    MARISA_CARD_2_NAME: TouhouHBMItemData(CATEGORY_CARD, 241, ItemClassification.progression),
    SAKUYA_CARD_2_NAME: TouhouHBMItemData(CATEGORY_CARD, 242, ItemClassification.progression),
    SANAE_CARD_2_NAME: TouhouHBMItemData(CATEGORY_CARD, 243, ItemClassification.progression),
    RAIKO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 244, ItemClassification.progression),
    SUMIREKO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 245, ItemClassification.progression),
    PATCHOULI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 246, ItemClassification.progression),
    NARUMI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 247, ItemClassification.progression),
    MISUMARU_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 248, ItemClassification.progression),
    TSUKASA_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 249, ItemClassification.progression),
    MEGUMU_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 250, ItemClassification.progression),
    MOMOYO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 251, ItemClassification.progression),
    TORAMARU_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 252, ItemClassification.progression),
    STAR_SAPPHIRE_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 253, ItemClassification.progression),
    LUNA_CHILD_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 254, ItemClassification.progression),
    SUNNY_MILK_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 255, ItemClassification.progression),
    FLANDRE_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 256, ItemClassification.progression),
    FUTO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 257, ItemClassification.progression),
    AUNN_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 258, ItemClassification.progression),
    JOON_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 259, ItemClassification.progression),
    SHION_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 260, ItemClassification.progression),
    KEIKI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 261, ItemClassification.progression),
    SEIRAN_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 262, ItemClassification.progression),
    DOREMY_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 263, ItemClassification.progression),
    JUNKO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 264, ItemClassification.progression),
    NITORI_STORY_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 265, ItemClassification.progression),
    TAKANE_STORY_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 266, ItemClassification.progression),
    MINORIKO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 267, ItemClassification.progression),
    ETERNITY_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 268, ItemClassification.progression),
    NEMUNO_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 269, ItemClassification.progression),
    WAKASAGI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 270, ItemClassification.progression),
    URUMI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 271, ItemClassification.progression),
    SEKIBANKI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 272, ItemClassification.progression),
    KUTAKA_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 273, ItemClassification.progression),
    KOMACHI_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 274, ItemClassification.progression),
    EBISU_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 275, ItemClassification.progression),
    SEIJA_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 276, ItemClassification.progression),
    TENSHI_THROW_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 277, ItemClassification.progression),
    CLOWNPIECE_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 278, ItemClassification.progression),
    SAKI_POWER_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 279, ItemClassification.progression),
    SUIKA_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 280, ItemClassification.progression),
    TEACUP_REIMU_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 281, ItemClassification.progression),
    TEACUP_MARISA_CARD_NAME: TouhouHBMItemData(CATEGORY_CARD, 282, ItemClassification.progression),
    # PROGRESSIVE ITEMS
    # Stage Progress
    PROGRESS_STAGE_ITEM_NAME: TouhouHBMItemData(CATEGORY_PROGRESS, 290, ItemClassification.progression),
    # Equipment Upgrades
    PROGRESS_EQUIP_NAME: TouhouHBMItemData(CATEGORY_PROGRESS, 291, ItemClassification.progression),
    PROGRESS_SLOT_NAME: TouhouHBMItemData(CATEGORY_PROGRESS, 292, ItemClassification.progression),
    PROGRESS_COST_NAME: TouhouHBMItemData(CATEGORY_PROGRESS, 293, ItemClassification.progression),
    # PERMANENT UPGRADES - IDs 300-399
    PERMA_LIFE_NAME: TouhouHBMItemData(CATEGORY_PERMA, 301, ItemClassification.useful),
    PERMA_BM_NAME: TouhouHBMItemData(CATEGORY_PERMA, 302, ItemClassification.useful),
    PERMA_POWER_NAME: TouhouHBMItemData(CATEGORY_PERMA, 303, ItemClassification.useful),
    PERMA_ATK_NAME: TouhouHBMItemData(CATEGORY_PERMA, 304, ItemClassification.useful),
    PERMA_MAGIC_ATK_NAME: TouhouHBMItemData(CATEGORY_PERMA, 305, ItemClassification.useful),
}

ITEM_TABLE_ID_TO_STAGE_NAME: Dict[int, str] = {
    100: TUTORIAL_NAME,
    101: STAGE1_NAME,
    102: STAGE2_NAME,
    103: STAGE3_NAME,
    104: STAGE4_NAME,
    105: STAGE5_NAME,
    106: STAGE6_NAME,
    107: ENDSTAGE_NAME,
    108: CHALLENGE_NAME
}

ITEM_TABLE_ID_TO_CARD_ID: Dict[int, str] = {
    200: LIFE_CARD,
    201: YUKARI_CARD,
    202: EIRIN_CARD,
    203: TEWI_CARD,
    204: REIMU_CARD_1,
    205: NITORI_CARD,
    206: KANAKO_CARD,
    207: ALICE_CARD,
    208: CIRNO_CARD,
    209: YOUMU_CARD_1,
    210: YOUMU_CARD_2,
    211: SAKI_BIGSHOT_CARD,
    212: KOISHI_CARD,
    213: TENSHI_SHIELD_CARD,
    214: MALLET_CARD,
    215: MOKOU_CARD,
    216: RINGO_CARD,
    217: MIKE_CARD,
    218: TAKANE_CARD,
    219: SANNYO_CARD,
    220: BYAKUREN_CARD,
    221: MOON_CARD,
    222: BLANK_CARD,
    223: SANAE_CARD_1,
    224: MARISA_CARD_1,
    225: SAKUYA_CARD_1,
    226: OKINA_CARD,
    227: UFO_CARD,
    228: SUWAKO_CARD,
    229: AYA_CARD,
    230: MAYUMI_CARD,
    231: KAGUYA_CARD,
    232: MIKO_CARD,
    233: MAMIZOU_CARD,
    234: YUYUKO_CARD,
    235: YACHIE_CARD,
    236: REMILIA_CARD,
    237: UTSUHO_CARD,
    238: LILY_WHITE_CARD,
    239: EIKI_CARD,
    240: REIMU_CARD_2,
    241: MARISA_CARD_2,
    242: SAKUYA_CARD_2,
    243: SANAE_CARD_2,
    244: RAIKO_CARD,
    245: SUMIREKO_CARD,
    246: PATCHOULI_CARD,
    247: NARUMI_CARD,
    248: MISUMARU_CARD,
    249: TSUKASA_CARD,
    250: MEGUMU_CARD,
    251: MOMOYO_CARD,
    252: TORAMARU_CARD,
    253: STAR_SAPPHIRE_CARD,
    254: LUNA_CHILD_CARD,
    255: SUNNY_MILK_CARD,
    256: FLANDRE_CARD,
    257: FUTO_CARD,
    258: AUNN_CARD,
    259: JOON_CARD,
    260: SHION_CARD,
    261: KEIKI_CARD,
    262: SEIRAN_CARD,
    263: DOREMY_CARD,
    264: JUNKO_CARD,
    265: NITORI_STORY_CARD,
    266: TAKANE_STORY_CARD,
    267: MINORIKO_CARD,
    268: ETERNITY_CARD,
    269: NEMUNO_CARD,
    270: WAKASAGI_CARD,
    271: URUMI_CARD,
    272: SEKIBANKI_CARD,
    273: KUTAKA_CARD,
    274: KOMACHI_CARD,
    275: EBISU_CARD,
    276: SEIJA_CARD,
    277: TENSHI_THROW_CARD,
    278: CLOWNPIECE_CARD,
    279: SAKI_POWER_CARD,
    280: SUIKA_CARD,
    281: TEACUP_REIMU_CARD,
    282: TEACUP_MARISA_CARD
}

PROGRESSIVE_ITEMS_LIST = [290, 291, 292, 293, 301, 302, 303, 304, 305]
PROGRESSIVE_COST_LIST = [291, 293]
STARTING_UPGRADE_LIST = [301, 302, 303, 304, 305]