# Utils specifically for generation rules.
from BaseClasses import CollectionState
from .Tools import get_progress_item_requirement, clamp, get_card_location_name_str
from .variables.card_const import *
from worlds.generic.Rules import add_rule


def get_card_shop_item_names() -> list[str]:
    # Go through both lists and fetch the card names.
    # Nazrin's cards never show up in shop.
    shop_card_item_names = []
    for card_string_id in ABILITY_CARD_LIST:
        if card_string_id == NAZRIN_CARD_1 or card_string_id == NAZRIN_CARD_2: continue
        shop_card_item_names.append(CARD_ID_TO_NAME[card_string_id])
    return shop_card_item_names


def has_equipment_achievement_access(world, state: CollectionState) -> bool:
    # If this passes, Progressive Loadout is active. Should only require getting their respective items.
    match world.options.progressive_loadout:
        case 1:  # Together
            return state.has(PROGRESS_EQUIP_NAME, world.player, 6)
        case 2:  # Separate. Only check for Slots since the achievement only tracks that.
            return state.has(PROGRESS_SLOT_NAME, world.player, 6)
        case _:  # If it does not, require stage 4 at minimum.
            return has_stage_access_item_count(world, state, 4)


# Tutorial stage has 5 exclusive cards.
def has_tutorial_access_item(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player)
    else:
        return state.has(TUTORIAL_NAME_FULL, world.player)


def has_challenge_access_item(world, state: CollectionState, is_boss: bool = False) -> bool:
    """
    Checks for Challenge Market access.
    If generation has turned off Challenge Market in logic (disable_challenge_logic == true),
    this will always return False.
    If doing Progressive Stages, also return False.
    """
    if world.options.progressive_stages:
        if world.options.low_skill_logic:
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player,
                             get_progress_item_requirement(CHALLENGE_NAME)) and low_skill_rules(world, state)
        else:
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(CHALLENGE_NAME))
    if world.options.disable_challenge_logic and not is_boss:
        return False
    else:
        # Challenge Market is also lategame.
        if world.options.low_skill_logic:
            return state.has(CHALLENGE_NAME_FULL, world.player) and low_skill_rules(world, state)
        else:
            return state.has(CHALLENGE_NAME_FULL, world.player)


# For specific stages (excludes Challenge Market by default).
def has_stage_access_item(world, state: CollectionState, short_stage_name: str) -> bool:
    full_stage_name = STAGE_SHORT_TO_FULL_NAME[short_stage_name]
    full_stage_id = STAGE_NAME_TO_ID[short_stage_name]

    if world.options.progressive_stages:
        if world.options.low_skill_logic and full_stage_id >= STAGE4_ID:
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player,
                             get_progress_item_requirement(short_stage_name)) and low_skill_rules(world, state)

        return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(short_stage_name))
    else:
        if world.options.low_skill_logic and full_stage_id >= STAGE4_ID:
            return state.has(full_stage_name, world.player) and low_skill_rules(world, state)
        return state.has(full_stage_name, world.player)


def has_stage_list_access_item(world, state: CollectionState, stage_name_list: list[str], achieve_check: bool = False) -> bool:
    """
    Checks for whether the player would have any of the stages available.
    When checking for Progressive Market requirements, this will always take the first name on the list.
    Challenge Market-related checks have their own separate condition.

    :param world: Just pass in world from Rules.py
    :param state: CollectionState. Just pass the one from the lambda in.
    :param stage_name_list: The full names of the stages.
    :param achieve_check: Whether this is for Achievements or not.
    """
    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(stage_name_list[0], True))
    else:
        if achieve_check:
            return state.has_all(stage_name_list, world.player)
        else:
            return state.has_any(stage_name_list, world.player)


def has_any_stage_access_item(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player)

    non_challenge_stages = STAGE_NAME_LIST
    if CHALLENGE_NAME_FULL in non_challenge_stages:
        non_challenge_stages.remove(CHALLENGE_NAME_FULL)
    return state.has_any(non_challenge_stages, world.player) or has_challenge_access_item(world, state)


# Despite the name, this is actually used for the slot upgrade achievement.
def has_stage_access_item_count(world, state: CollectionState, stage_count: int) -> bool:
    if stage_count <= 0: return True

    def item_count_stages(used_count: int) -> bool:
        non_story_pool = STAGE_NAME_LIST
        if CHALLENGE_NAME_FULL in non_story_pool:
            non_story_pool.remove(CHALLENGE_NAME_FULL)
        if TUTORIAL_NAME_FULL in non_story_pool:
            non_story_pool.remove(TUTORIAL_NAME_FULL)

        if world.options.disable_challenge_logic:
            return state.has_from_list_unique(non_story_pool, world.player, used_count)
        else:
            if STAGE6_NAME_FULL in non_story_pool:
                non_story_pool.remove(STAGE6_NAME_FULL)
            return (state.has_from_list_unique(non_story_pool, world.player,
                                               clamp(used_count - 1, 0, len(non_story_pool))) and
                    state.has_from_list_unique((STAGE6_NAME_FULL, CHALLENGE_NAME_FULL), world.player, 1))

    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player, stage_count)
    return (
        # The usual.
            item_count_stages(stage_count) or
            # The rare case that someone has enough items for the story bosses.
            (state.has_all(
                (TUTORIAL_NAME_FULL, STAGE4_NAME_FULL, BLANK_CARD_NAME, STAGE6_NAME_FULL, NITORI_STORY_CARD_NAME,
                 ENDSTAGE_NAME_FULL), world.player)
             and item_count_stages(stage_count - 1))
    )


# For more open reward pools. Of course, these all imply Challenge Market clauses as well.
# Common. Shows up in every stage except Tutorial.
def has_common_access_item(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(STAGE1_NAME))

    non_challenge_stages = STAGE_NAME_LIST
    if TUTORIAL_NAME_FULL in non_challenge_stages:
        non_challenge_stages.remove(TUTORIAL_NAME_FULL)
    if CHALLENGE_NAME_FULL in non_challenge_stages:
        non_challenge_stages.remove(CHALLENGE_NAME_FULL)
    return state.has_any(non_challenge_stages, world.player) or has_challenge_access_item(world, state)


# Very early game (Stage 1+). Does not show up in Stage 5 or End of Market.
def has_very_early_game_access_item(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(STAGE1_NAME))

    return has_early_game_access_item(world, state) or state.has(STAGE1_NAME_FULL, world.player)


# Early game (Stage 2+). Does not show up in Stage 5 or End of Market.
def has_early_game_access_item(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(STAGE2_NAME))

    return has_midgame_access_item(world, state) or state.has(STAGE2_NAME_FULL, world.player)


# Midgame (Stage 3+). Does not show up in Stage 5 or End of Market.
def has_midgame_access_item(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(STAGE3_NAME))

    return (state.has_any((STAGE3_NAME_FULL, STAGE4_NAME_FULL, STAGE6_NAME_FULL), world.player)
            or has_challenge_access_item(world, state))


# Lategame (Stage 4+). Does not show up in End of Market.
# Low Skill Logic forces the generation to include certain Ability Cards as compulsory.
def has_lategame_access_item(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        if world.options.low_skill_logic:
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player,
                             get_progress_item_requirement(STAGE4_NAME)) and low_skill_rules(world, state)
        else:
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(STAGE4_NAME))

    if world.options.low_skill_logic:
        return ((state.has_any((STAGE4_NAME_FULL, STAGE5_NAME_FULL, STAGE6_NAME_FULL), world.player)
                 and low_skill_rules(world, state)) or has_challenge_access_item(world, state))
    else:
        return (state.has_any((STAGE4_NAME_FULL, STAGE5_NAME_FULL, STAGE6_NAME_FULL), world.player)
                or has_challenge_access_item(world, state))


def low_skill_rules(world, state: CollectionState, is_boss_encounter: bool = False) -> bool:
    if is_boss_encounter:
        pass

    match world.options.progressive_loadout:
        case 1:  # Simultaneous upgrades.
            return state.has_all(LOW_SKILL_CARD_LIST, world.player) and state.has(PROGRESS_EQUIP_NAME, world.player, 3)
        case 2:  # Separate upgrades.
            return (state.has_all(LOW_SKILL_CARD_LIST, world.player) and state.has(PROGRESS_SLOT_NAME, world.player, 3)
                    and state.has(PROGRESS_COST_NAME, world.player, 3))
        case _:
            return state.has_all(LOW_SKILL_CARD_LIST, world.player)


# Special access rules.
def has_nitori_access(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        if world.options.low_skill_logic:
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player,
                             get_progress_item_requirement(STAGE4_NAME)) and state.has(BLANK_CARD_NAME,
                                                                                       world.player) and low_skill_rules(world,
                state)
        else:
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player,
                             get_progress_item_requirement(STAGE4_NAME)) and state.has(BLANK_CARD_NAME, world.player)

    if world.options.low_skill_logic:
        return state.has_all((STAGE4_NAME_FULL, BLANK_CARD_NAME), world.player) and low_skill_rules(world, state)
    else:
        return state.has_all((STAGE4_NAME_FULL, BLANK_CARD_NAME), world.player)


def has_takane_access(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        if world.options.low_skill_logic:
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player,
                             get_progress_item_requirement(STAGE6_NAME)) and state.has(NITORI_STORY_CARD_NAME,
                                                                                       world.player) and low_skill_rules(world,
                state)
        else:
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player,
                             get_progress_item_requirement(STAGE6_NAME)) and state.has(NITORI_STORY_CARD_NAME,
                                                                                       world.player)

    if world.options.low_skill_logic:
        return state.has_all((STAGE6_NAME_FULL, NITORI_STORY_CARD_NAME), world.player) and low_skill_rules(world, state)
    else:
        return state.has_all((STAGE6_NAME_FULL, NITORI_STORY_CARD_NAME), world.player)


def has_sekibanki_access(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(STAGE2_NAME))

    return state.has_any((STAGE2_NAME_FULL, ENDSTAGE_NAME_FULL), world.player) or has_challenge_access_item(world, state)


# Lily White's and Doremy's cards are a little more open.
def has_lily_white_access(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(STAGE1_NAME))

    if world.options.low_skill_logic:
        return has_very_early_game_access_item(world, state) or (
                    has_stage_access_item(world, state,  STAGE5_NAME) and low_skill_rules(world, state)) or has_challenge_access_item(world,
            state)
    else:
        return has_very_early_game_access_item(world, state) or has_stage_access_item(world, state, 
                                                                               STAGE5_NAME) or has_challenge_access_item(world,
            state)


def has_doremy_access(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(STAGE2_NAME))

    if world.options.low_skill_logic:
        return has_early_game_access_item(world, state) or (
                    has_stage_access_item(world, state,  STAGE5_NAME) and low_skill_rules(world, state)) or has_challenge_access_item(world, state)
    else:
        return has_early_game_access_item(world, state) or has_stage_access_item(world, state, STAGE5_NAME) or has_challenge_access_item(world, state)


def has_nazrin2_access(world, state: CollectionState) -> bool:
    if world.options.progressive_stages:
        return state.has(PROGRESS_ITEM_NAME_FULL, world.player)

    black_market_stages = STAGE_NAME_LIST
    if ENDSTAGE_NAME_FULL in black_market_stages:
        black_market_stages.remove(ENDSTAGE_NAME_FULL)
    if CHALLENGE_NAME_FULL in black_market_stages:
        black_market_stages.remove(CHALLENGE_NAME_FULL)
    return state.has_any(black_market_stages, world.player) or has_challenge_access_item(world, state)


def all_bosses_access(world, state: CollectionState) -> bool:
    """
    Checks if the player can access all bosses outside of Challenge Market.
    This accounts for not only all stage unlocks but also the two special cards.
    """
    if world.options.progressive_stages:
        if world.options.low_skill_logic:
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player,
                             get_progress_item_requirement(ENDSTAGE_NAME)) and state.has_all(
                (BLANK_CARD_NAME, NITORI_STORY_CARD_NAME), world.player) and low_skill_rules(world, state)
        else:
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player,
                             get_progress_item_requirement(ENDSTAGE_NAME)) and state.has_all(
                (BLANK_CARD_NAME, NITORI_STORY_CARD_NAME), world.player)

    if world.options.low_skill_logic:
        return state.has_all(
            (TUTORIAL_NAME_FULL, STAGE1_NAME_FULL, STAGE2_NAME_FULL, STAGE3_NAME_FULL, STAGE4_NAME_FULL,
             STAGE5_NAME_FULL, STAGE6_NAME_FULL, ENDSTAGE_NAME_FULL, NITORI_STORY_CARD_NAME, BLANK_CARD_NAME),
            world.player) and low_skill_rules(world, state)
    else:
        return state.has_all(
            (TUTORIAL_NAME_FULL, STAGE1_NAME_FULL, STAGE2_NAME_FULL, STAGE3_NAME_FULL, STAGE4_NAME_FULL,
             STAGE5_NAME_FULL, STAGE6_NAME_FULL, ENDSTAGE_NAME_FULL, NITORI_STORY_CARD_NAME, BLANK_CARD_NAME),
            world.player)


def all_cards_access(world, state: CollectionState) -> bool:
    return state.has_all(get_card_shop_item_names(), world.player)


# Access rules for the Ability Card dex entries.
# Ensures that the player has a way to grind for Funds + the card in the Permanent Card Shop.
# This will fail if this is a solo game and the player chooses to start with no Markets unlocked.
# (Hopefully)
def has_grind_access(world, state: CollectionState, the_card_id: str) -> bool:
    return state.has(CARD_ID_TO_NAME[the_card_id], world.player) and has_any_stage_access_item(world, state)


def add_generic_access_card_rule(world, card_name_id: str, access_level: int):
    generic_location_card_name: str = get_card_location_name_str(card_name_id, False)
    generic_location_card = world.get_location(generic_location_card_name)

    match access_level:
        case 0:  # Common access.
            add_rule(generic_location_card, lambda state: has_common_access_item(world, state))
        case 1:  # Stage 1+
            add_rule(generic_location_card, lambda state: has_very_early_game_access_item(world, state))
        case 2:  # Stage 2+
            add_rule(generic_location_card, lambda state: has_early_game_access_item(world, state))
        case 3:  # Stage 3+
            add_rule(generic_location_card, lambda state: has_midgame_access_item(world, state))
        case 4:  # Lategame
            add_rule(generic_location_card, lambda state: has_lategame_access_item(world, state))
        case _:
            pass