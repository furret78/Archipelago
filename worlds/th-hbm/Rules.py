from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule
from .variables.boss_and_stage import *
from .variables.card_const import NITORI_STORY_CARD_NAME, BLANK_CARD_NAME, ABILITY_CARD_LIST, NAZRIN_CARD_1, \
    NAZRIN_CARD_2, CARD_ID_TO_NAME

def set_all_rules(world) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_goal_condition(world)

def set_all_entrance_rules(world) -> None:
    origin_to_tutorial = world.get_entrance(ORIGIN_TO_TUTORIAL_NAME)
    origin_to_stage1 = world.get_entrance(ORIGIN_TO_STAGE1_NAME)
    origin_to_stage2 = world.get_entrance(ORIGIN_TO_STAGE2_NAME)
    origin_to_stage3 = world.get_entrance(ORIGIN_TO_STAGE3_NAME)
    origin_to_stage4 = world.get_entrance(ORIGIN_TO_STAGE4_NAME)
    origin_to_stage5 = world.get_entrance(ORIGIN_TO_STAGE5_NAME)
    origin_to_stage6 = world.get_entrance(ORIGIN_TO_STAGE6_NAME)
    origin_to_chimata = world.get_entrance(ORIGIN_TO_CHIMATA_NAME)
    origin_to_challenge = world.get_entrance(ORIGIN_TO_CHALLENGE_NAME)

    origin_to_region_list = [
        origin_to_tutorial, origin_to_stage1, origin_to_stage2, origin_to_stage3,
        origin_to_stage4, origin_to_stage5, origin_to_stage6, origin_to_chimata,
        origin_to_challenge
    ]

    stage_id = 0
    for i in STAGE_NAME_LIST:
        set_rule(origin_to_region_list[stage_id], lambda state: state.has(i, world.player))
        stage_id += 1

def set_all_location_rules(world) -> None:
    # Location rules for Ability Cards here.

    # Location rules for bosses here.
    # Tutorial.

    # 1st Market - Secret Heaven Cliff.

    # 2nd Market - Misty Lake.

    # 3rd Market -

    # Nitori Kawashiro requires having Blank Card and 4th Market unlocked.

    # Takane Yamashiro requires having Capitalist's Dilemma and 6th Market unlocked.

    pass

def set_goal_condition(world) -> None:
    def minimum_story_clear(state: CollectionState) -> bool:
        return state.has_all((NITORI_STORY_CARD_NAME, STAGE6_NAME_FULL), world.player)
    def full_story_clear(state: CollectionState) -> bool:
        return state.has_all(
            (NITORI_STORY_CARD_NAME, BLANK_CARD_NAME,
            STAGE4_NAME_FULL, STAGE6_NAME_FULL, ENDSTAGE_NAME_FULL),
            world.player
        )

    shop_card_item_list = get_card_shop_item_names()

    def all_cards_clear(state: CollectionState) -> bool:
        return state.has_all(shop_card_item_list, world.player)

    # Since this checks for items, and full stage names are used as items, use that.
    # To defeat all bosses, you need all stages to be available except the Challenge Market.
    # Both instances of Mike Goutokuji are counted.
    boss_condition_list = STAGE_NAME_LIST
    boss_condition_list.remove(CHALLENGE_NAME_FULL)

    def all_bosses_clear(state: CollectionState) -> bool:
        return state.has_all(boss_condition_list, world.player)
    def full_clear_rule(state: CollectionState) -> bool:
        return state.has_all(shop_card_item_list + boss_condition_list, world.player)

    # The actual Completion Condition field
    world.multiworld.completion_condition[world.player] = lambda state: minimum_story_clear(state)

    match getattr(world.options, "completion_type"):
        # Minimum Story Clear
        case 0:
            world.multiworld.completion_condition[world.player] = lambda state: full_story_clear(state)
        # Full Story Clear
        case 1:
            world.multiworld.completion_condition[world.player] = lambda state: minimum_story_clear(state)
        # All Cards
        case 2:
            world.multiworld.completion_condition[world.player] = lambda state: all_cards_clear(state)
        # All Bosses
        case 3:
            world.multiworld.completion_condition[world.player] = lambda state: all_bosses_clear(state)
        # Full Clear
        case 4:
            world.multiworld.completion_condition[world.player] = lambda state: full_clear_rule(state)

def get_card_shop_item_names() -> list[str]:
    # Go through both lists and fetch the card names.
    # Nazrin's cards never show up in shop.
    shop_card_item_names = []
    card_list_index = 0
    for i in ABILITY_CARD_LIST:
        if i == NAZRIN_CARD_1 or i == NAZRIN_CARD_2:
            card_list_index += 1
            continue
        shop_card_item_names.append(CARD_ID_TO_NAME[card_list_index])
        card_list_index += 1
    return shop_card_item_names