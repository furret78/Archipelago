import traceback

from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule
from .Locations import get_boss_location_name_str, get_card_location_name_str
from .variables.card_const import *


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
    # Helper CollectionStates specifically for generic conditions that just require stage access.
    def has_stage_access_item(state: CollectionState, stage_id: int) -> bool:
        return state.has(STAGE_SHORT_TO_FULL_NAME[STAGE_ID_TO_SHORT_NAME[stage_id]], world.player)
    def has_any_stage_access_item(state: CollectionState) -> bool:
        return state.has_any(STAGE_NAME_LIST, world.player)
    # Special access rules.
    def has_nitori_access(state: CollectionState) -> bool:
        return state.has_all((STAGE4_NAME_FULL, BLANK_CARD_NAME), world.player)
    def has_takane_access(state: CollectionState) -> bool:
        return state.has_all((STAGE6_NAME_FULL, NITORI_STORY_CARD_NAME), world.player)
    def has_teacup_access(state: CollectionState) -> bool:
        return state.has_all((ENDSTAGE_NAME_FULL, BLANK_CARD_NAME), world.player)

    #
    # Location rules for bosses here.
    #
    # Normal stages and story bosses.
    internal_stage_id = 0
    for boss_set in ALL_BOSSES_LIST:
        for boss_name in boss_set:
            location_encounter = world.get_location(get_boss_location_name_str(internal_stage_id, boss_name))
            location_defeat = world.get_location(get_boss_location_name_str(internal_stage_id, boss_name))

            # Special rules for Nitori and Takane.
            if boss_name == BOSS_NITORI_NAME:
                add_rule(location_encounter, lambda state: has_nitori_access(state))
                add_rule(location_defeat, lambda state: has_nitori_access(state))
                continue
            if boss_name == BOSS_TAKANE_NAME:
                add_rule(location_encounter, lambda state: has_takane_access(state))
                add_rule(location_defeat, lambda state: has_takane_access(state))
                continue

            # Normal rules for everyone else.
            add_rule(location_encounter, lambda state: has_stage_access_item(state, internal_stage_id))
            add_rule(location_defeat, lambda state: has_stage_access_item(state, internal_stage_id))

        internal_stage_id += 1
    # Challenge Market has all bosses except story bosses.
    # Story bosses include Tutorial Mike, Chimata, Nitori, and Takane.
    chosen_stage_set_id = 0
    if getattr(world.options, "challenge_checks"):
        for boss_set in ALL_BOSSES_LIST:
            # This checks if it's within the normal range of the Challenge Market boss list.
            if TUTORIAL_ID < chosen_stage_set_id < STAGE_CHIMATA_ID:
                for boss_name in boss_set:
                    # If this happens to be Nitori or Takane, discard and move on.
                    if boss_name == BOSS_NITORI_NAME or boss_name == BOSS_TAKANE_NAME: continue

                    location_encounter = get_boss_location_name_str(STAGE_CHALLENGE_ID, boss_name)
                    add_rule(world.get_location(location_encounter), lambda state: state.has(CHALLENGE_NAME_FULL, world.player))

            chosen_stage_set_id += 1

    #
    # Location rules for Ability Cards as stage rewards here.
    #
    # Tutorial has nothing exclusive to note.
    for stage_name in STAGE_LIST:
        if stage_name not in STAGE_EXCLUSIVE_CARD_LIST: continue
        for card in STAGE_EXCLUSIVE_CARD_LIST[stage_name]:
            name_card_reward: str = get_card_location_name_str(card, False)
            location_card_reward = world.get_location(name_card_reward)

            # Special unlock rules for Capitalist's Dilemma, Hundredth Black Market
            # as well as the two Teacup cards.
            # Capitalist's Dilemma requires Blank Card and 4th Market unlock.
            if card == NITORI_STORY_CARD:
                add_rule(location_card_reward, lambda state: has_nitori_access(state))
                continue
            # Hundredth Black Market requires Capitalist's Dilemma and 6th Market unlock.
            if card == TAKANE_STORY_CARD:
                add_rule(location_card_reward, lambda state: has_takane_access(state))
                continue
            # Teacup cards require Blank Card and End of Market unlock.
            if card == TEACUP_REIMU_CARD or card == TEACUP_MARISA_CARD:
                add_rule(location_card_reward, lambda state: has_teacup_access(state))
                continue

            # Generic stage access conditions otherwise.
            add_rule(location_card_reward, lambda state: has_stage_access_item(state, STAGE_NAME_TO_ID[stage_name]))

    #
    # Location rules for Ability Card dex entries here.
    #
    # Nazrin's cards don't have rules for unlocking. Every stage has it.
    nazrin_card1_location = world.get_location(get_card_location_name_str(NAZRIN_CARD_1, True))
    nazrin_card2_location = world.get_location(get_card_location_name_str(NAZRIN_CARD_2, True))
    add_rule(nazrin_card1_location, lambda state: has_any_stage_access_item(state))
    add_rule(nazrin_card2_location, lambda state: has_any_stage_access_item(state))
    # The rest are only available if their respective item is available in the shop.
    for card_string_id in ABILITY_CARD_LIST:
        # Skip Nazrin's cards.
        if card_string_id == NAZRIN_CARD_1 or card_string_id == NAZRIN_CARD_2:
            continue

        card_dex_location = world.get_location(get_card_location_name_str(card_string_id, True))
        add_rule(card_dex_location, lambda state: state.has(CARD_ID_TO_NAME[card_string_id], world.player))


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
    for card_string_id in ABILITY_CARD_LIST:
        if card_string_id == NAZRIN_CARD_1 or card_string_id == NAZRIN_CARD_2: continue
        shop_card_item_names.append(CARD_ID_TO_NAME[card_string_id])
    return shop_card_item_names