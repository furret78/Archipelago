from typing import Dict, NamedTuple, Optional

from BaseClasses import Item, ItemClassification
from .variables.card_const import *
from .variables.boss_and_stage import *
from .variables.meta_data import DISPLAY_NAME

CATEGORY_ITEM = "Items"
CATEGORY_FILLER = "Filler"
CATEGORY_STAGE = "Markets"
CATEGORY_TRAP = "Traps"
CATEGORY_CARD = "Ability Cards"
CATEGORY_START = "Starting Ability Cards"


class TouhouHBMItem(Item):
    game: str = DISPLAY_NAME


class TouhouHBMItemData(NamedTuple):
    category: str
    code: Optional[int] = None
    classification: ItemClassification = None
    max_quantity: int = 1
    weight: int = 1


def get_items_by_category(category: str) -> Dict[str, TouhouHBMItemData]:
    item_dict: Dict[str, TouhouHBMItemData] = {}
    for name, data in item_table.items():
        if data.category == category:
            item_dict.setdefault(name, data)

    return item_dict


def get_card_id_by_code(code: int) -> str:
    if code < 200 or code >= 200 + ITEM_TABLE_ID_TO_CARD_ID.__sizeof__(): return "Invalid."
    return ITEM_TABLE_ID_TO_CARD_ID.get(code)


def get_random_filler_item_name(world) -> str:
    filler_item_list = []

    for name in get_items_by_category(CATEGORY_ITEM).keys():
        filler_item_list.append(name)
    for name in get_items_by_category(CATEGORY_FILLER).keys():
        filler_item_list.append(name)

    final_item_name: str = world.random.choice(filler_item_list).__str__()
    if world.random.randint(0, 99) < world.options.trap_chance:
        final_item_name = world.random.choice(filler_item_list).__str__()
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
    # Initialization
    item_pool: list[Item] = []

    # Stage unlocks get added first.
    stage_unlock_item_dict = get_items_by_category(CATEGORY_STAGE)
    for name in stage_unlock_item_dict.keys():
        item_pool.append(world.create_item(name))

    # Ability Cards get added next.
    # There are checks to make sure it doesn't submit the Starting Card (if there are any).
    ability_card_item_dict = get_items_by_category(CATEGORY_CARD)
    for ability_card_name, data in ability_card_item_dict.items():
        # Get the String ID of the cards.
        string_id = ITEM_TABLE_ID_TO_CARD_ID[data.code]

        # Remove cards that obviously cannot be equipped at start.
        if string_id in ABILITY_CARD_CANNOT_EQUIP:
            continue

        # Check if item is redundant or not.
        match world.options.starting_card:
            case 1:
                if string_id == RINGO_CARD: continue
            case 2:
                if string_id == MALLET_CARD: continue

        # Grab full name of item and create.
        item_pool.append(world.create_item(CARD_ID_TO_NAME[ability_card_name]))

    # Now that all the important stuff is added, check if there's any spots left.
    number_of_items = len(item_pool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    remaining_locations = number_of_unfilled_locations - number_of_items

    # If there are any left, pad out the pool with filler items.
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
        # If the filler item is useful, remove 1 count from the limit dictionary.
        if filler_item_name in filler_limit_dict: filler_limit_dict[filler_item_name] -= 1

        remain_index += 1

    # Submit item pool for the randomizer.
    world.multiworld.itempool += item_pool

    # Final function that grants the starting card since it was removed from the item pool.
    create_starting_card(world)


def create_starting_card(world):
    """
    Internal function for Items.create_all_items().
    This function artificially gives the player a starting Ability Card.
    The check for unlocking this card in the Dex is removed from the location pool.
    Implementation is done in Locations.py
    """
    if 0 < world.options.starting_card < 3:
        starting_card_name: str = STARTING_RINGO_CARD_NAME

        match world.options.starting_card:
            case 2:
                starting_card_name = STARTING_MALLET_CARD_NAME

        world.push_precollected(world.create_item(starting_card_name))

def check_if_item_id_exists(given_id: int) -> bool:
    if given_id < 0: return False
    if 4 > given_id < 10: return False
    if 13 > given_id < 50: return False
    if 52 > given_id < 100: return False
    if 108 > given_id < 200: return False
    if 282 > given_id < 500: return False
    if given_id > 501: return False
    return True

# An Item table documenting every Item and its data.
# If anything new is added, add it to Client.py under give_item()
# as well as add entries to the other tables below here.
item_table: Dict[str, TouhouHBMItemData] = {
    # In-game occurrences
    "+1 Life": TouhouHBMItemData(CATEGORY_ITEM, 0, ItemClassification.useful, 6),
    "+200 Funds": TouhouHBMItemData(CATEGORY_ITEM, 1, ItemClassification.useful, 7),
    "+1000 Funds": TouhouHBMItemData(CATEGORY_ITEM, 2, ItemClassification.useful, 4),
    "+200 Bullet Money": TouhouHBMItemData(CATEGORY_ITEM, 3, ItemClassification.useful, 7),
    "+500 Bullet Money": TouhouHBMItemData(CATEGORY_ITEM, 4, ItemClassification.useful, 8),

    # Filler
    "+5 Funds": TouhouHBMItemData(CATEGORY_FILLER, 10),
    "+10 Funds": TouhouHBMItemData(CATEGORY_FILLER, 11),
    "+5 Bullet Money": TouhouHBMItemData(CATEGORY_FILLER, 12),
    "+10 Bullet Money": TouhouHBMItemData(CATEGORY_FILLER, 13),

    # Trap
    "-100 Bullet Money": TouhouHBMItemData(CATEGORY_TRAP, 50, ItemClassification.trap),
    "-100 Funds": TouhouHBMItemData(CATEGORY_TRAP, 51, ItemClassification.trap),
    "-50 Funds": TouhouHBMItemData(CATEGORY_TRAP, 52, ItemClassification.trap),

    # Stage unlocks
    TUTORIAL_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 100, ItemClassification.progression),
    STAGE1_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 101, ItemClassification.progression),
    STAGE2_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 102, ItemClassification.progression),
    STAGE3_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 103, ItemClassification.progression),
    STAGE4_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 104, ItemClassification.progression),
    STAGE5_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 105, ItemClassification.progression),
    STAGE6_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 106, ItemClassification.progression),
    ENDSTAGE_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 107, ItemClassification.progression),
    CHALLENGE_NAME_FULL: TouhouHBMItemData(CATEGORY_STAGE, 108, ItemClassification.progression),

    # Card Shop unlocks
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

    STARTING_MALLET_CARD_NAME: TouhouHBMItemData(CATEGORY_START, 500, ItemClassification.useful),
    STARTING_RINGO_CARD_NAME: TouhouHBMItemData(CATEGORY_START, 501, ItemClassification.useful),
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

ITEM_TABLE_ID_TO_STARTING_CARD_ID: Dict[int, str] = {
    500: MALLET_CARD,
    501: RINGO_CARD
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

GAME_ONLY_ITEM_ID = [0, 3, 4, 12, 13, 50]