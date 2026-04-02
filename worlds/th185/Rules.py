# AP 0.6.7 moves CollectionRule to BaseClasses
try:
    from BaseClasses import CollectionRule
except ImportError:
    from worlds.generic.Rules import CollectionRule
from worlds.generic.Rules import set_rule
from .Tools import get_boss_location_name_str, get_music_location_name_str, get_achievement_location_name_str, get_boss_names_challenge_list
from .variables.music_and_achiev import MUSIC_ROOM_NAME_DICT, ACHIEVE_NAME_DICT
from .Rules_Utils import *


def set_all_rules(world) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_goal_condition(world)


def get_card_shop_item_names() -> list[str]:
    # Go through both lists and fetch the card names.
    # Nazrin's cards never show up in shop.
    shop_card_item_names = []
    for card_string_id in ABILITY_CARD_LIST:
        if card_string_id == NAZRIN_CARD_1 or card_string_id == NAZRIN_CARD_2: continue
        shop_card_item_names.append(CARD_ID_TO_NAME[card_string_id])
    return shop_card_item_names


def set_all_entrance_rules(world) -> None:
    def has_correct_stage_item(state: CollectionState, given_stage: str) -> bool:
        if world.options.progressive_stages:
            progress_requirement_count = get_progress_item_requirement(given_stage, True)
            return state.has(PROGRESS_ITEM_NAME_FULL, world.player, progress_requirement_count)
        elif given_stage == CHALLENGE_NAME_FULL and world.options.disable_challenge_logic:
            return state.has_all((STAGE_NAME_LIST[:-1]), world.player)
        else:
            return state.has(given_stage, world.player)

    origin_to_region_dict = {
        TUTORIAL_NAME_FULL: world.get_entrance(ORIGIN_TO_TUTORIAL_NAME),
        STAGE1_NAME_FULL: world.get_entrance(ORIGIN_TO_STAGE1_NAME),
        STAGE2_NAME_FULL: world.get_entrance(ORIGIN_TO_STAGE2_NAME),
        STAGE3_NAME_FULL: world.get_entrance(ORIGIN_TO_STAGE3_NAME),
        STAGE4_NAME_FULL: world.get_entrance(ORIGIN_TO_STAGE4_NAME),
        STAGE5_NAME_FULL: world.get_entrance(ORIGIN_TO_STAGE5_NAME),
        STAGE6_NAME_FULL: world.get_entrance(ORIGIN_TO_STAGE6_NAME),
        ENDSTAGE_NAME_FULL: world.get_entrance(ORIGIN_TO_CHIMATA_NAME),
        CHALLENGE_NAME_FULL: world.get_entrance(ORIGIN_TO_CHALLENGE_NAME)
    }

    for stage_name in origin_to_region_dict.keys():
        set_rule(origin_to_region_dict[stage_name], lambda state, used_name=stage_name: has_correct_stage_item(state, used_name))


def set_all_location_rules(world) -> None:
    set_boss_location_rules(world)
    set_market_reward_rules(world)
    set_card_dex_rules(world)
    set_music_rules(world)
    set_achievement_rules(world)
    return


def set_boss_location_rules(world):
    #
    # Location rules for bosses here.
    #
    # Normal stages and story bosses.
    for stage_short_name in STAGE_LIST:
        stage_id_from_list = STAGE_NAME_TO_ID[stage_short_name]
        if stage_short_name != CHALLENGE_NAME:
            for boss_name in ALL_BOSSES_LIST[stage_id_from_list]:
                location_encounter = world.get_location(get_boss_location_name_str(stage_id_from_list, boss_name))
                location_defeat = world.get_location(get_boss_location_name_str(stage_id_from_list, boss_name, True))

                # Check if it's Nitori or Takane
                if boss_name == BOSS_NITORI_NAME:
                    add_rule(location_encounter, lambda state: has_nitori_access(world, state))
                    add_rule(location_defeat, lambda state: has_nitori_access(world, state))
                    continue
                elif boss_name == BOSS_TAKANE_NAME:
                    add_rule(location_encounter, lambda state: has_takane_access(world, state))
                    add_rule(location_defeat, lambda state: has_takane_access(world, state))
                    continue

                # If it's none of them
                add_rule(location_encounter,
                         lambda state, the_name=stage_short_name: has_stage_access_item(world, state, the_name))
                add_rule(location_defeat,
                         lambda state, the_name=stage_short_name: has_stage_access_item(world, state, the_name))
        # Challenge Market clause.
        else:
            for challenge_boss in get_boss_names_challenge_list():
                location_encounter = get_boss_location_name_str(STAGE_CHALLENGE_ID, challenge_boss)
                location_defeat = get_boss_location_name_str(STAGE_CHALLENGE_ID, challenge_boss, True)
                add_rule(world.get_location(location_encounter), lambda state: has_challenge_access_item(world, state, True))
                add_rule(world.get_location(location_defeat), lambda state: has_challenge_access_item(world, state, True))


def set_market_reward_rules(world):
    #
    # Location rules for Ability Cards as stage rewards here.
    #
    # Tutorial has 5 cards only obtainable there.
    # Challenge Market has every single card in the game except for the 5 in Tutorial.
    # Boss exclusive cards first.
    for card_string_id in ABILITY_CARD_LIST:
        # Skip over Nazrin's cards and the Mallet card.
        if card_string_id in ABILITY_CARD_CANNOT_EQUIP: continue
        if card_string_id == MALLET_CARD: continue
        # Card exclusivity check.
        was_exclusive_card: bool = False

        for stage_name, card_set in STAGE_EXCLUSIVE_CARD_LIST.items():
            for card_id in card_set:
                if card_string_id != card_id: continue
                name_card_reward: str = get_card_location_name_str(card_string_id, False)
                location_card_reward = world.get_location(name_card_reward)

                # Tutorial stage has 5 exclusive cards not seen in Challenge Market.
                if stage_name == TUTORIAL_NAME:
                    add_rule(location_card_reward, lambda state: has_tutorial_access_item(world, state))
                    was_exclusive_card = True
                    continue
                # Capitalist's Dilemma requires Blank Card and 4th Market unlock.
                if card_string_id == NITORI_STORY_CARD:
                    add_rule(location_card_reward,
                             lambda state: has_nitori_access(world, state) or has_challenge_access_item(world, state))
                # Hundredth Black Market requires Capitalist's Dilemma and 6th Market unlock.
                elif card_string_id == TAKANE_STORY_CARD:
                    add_rule(location_card_reward,
                             lambda state: has_takane_access(world, state) or has_challenge_access_item(world, state))
                # Freewheeling Severed Head somehow shows up in End of Market.
                elif card_string_id == SEKIBANKI_CARD:
                    add_rule(location_card_reward, lambda state: has_sekibanki_access(world, state))
                # Generic conditions otherwise.
                else:
                    add_rule(location_card_reward,
                             lambda state, the_name=stage_name: has_stage_access_item(world, state, the_name))

                was_exclusive_card = True

        if was_exclusive_card: continue

        # If it gets here, that means the card in question is not exclusive.
        # Check for Item Season and Sheep You Want to Count first.
        if card_string_id == LILY_WHITE_CARD:
            lily_location_name: str = get_card_location_name_str(LILY_WHITE_CARD, False)
            lily_location = world.get_location(lily_location_name)
            add_rule(lily_location, lambda state: has_lily_white_access(world, state))
            continue
        if card_string_id == DOREMY_CARD:
            doremy_location_name: str = get_card_location_name_str(DOREMY_CARD, False)
            doremy_location = world.get_location(doremy_location_name)
            add_rule(doremy_location, lambda state: has_doremy_access(world, state))
            continue

        # If it's not those two, then it belongs in a card tier.
        if card_string_id in STAGE_COMMON_CARD_LIST:
            add_generic_access_card_rule(world, card_string_id, 0)
            continue
        if card_string_id in STAGE1_CARD_LIST:
            add_generic_access_card_rule(world, card_string_id, 1)
            continue
        if card_string_id in STAGE2_CARD_LIST:
            add_generic_access_card_rule(world, card_string_id, 2)
            continue
        if card_string_id in STAGE3_CARD_LIST:
            add_generic_access_card_rule(world, card_string_id, 3)
            continue
        if card_string_id in LATEGAME_CARD_LIST:
            add_generic_access_card_rule(world, card_string_id, 4)
            continue


def set_card_dex_rules(world):
    #
    # Location rules for Ability Card dex entries here.
    #
    # Nazrin's cards don't have rules for unlocking. Practically every stage has it.
    nazrin_card1_location = world.get_location(get_card_location_name_str(NAZRIN_CARD_1, True))
    add_rule(nazrin_card1_location, lambda state: has_any_stage_access_item(world, state))
    nazrin_card2_location = world.get_location(get_card_location_name_str(NAZRIN_CARD_2, True))
    add_rule(nazrin_card2_location, lambda state: has_nazrin2_access(world, state))
    # The rest are only available if their respective item is available in the shop.
    for card_string_id in ABILITY_CARD_LIST:
        # Skip Nazrin's cards.
        if card_string_id in ABILITY_CARD_CANNOT_EQUIP: continue

        card_dex_location = world.get_location(get_card_location_name_str(card_string_id, True))
        add_rule(card_dex_location, lambda state, the_card_name=card_string_id: has_grind_access(world, state, the_card_name))


def set_music_rules(world):
    #
    # Location rules for Music Room tracks here.
    #
    # Each track pretty much plays under different conditions. Not much of a way to classify them.
    # Check if their checks are enabled first.
    if world.options.music_room_checks:
        for track_id in MUSIC_ROOM_NAME_DICT.keys():
            music_track_location = world.get_location(get_music_location_name_str(track_id))

            match track_id:
                case 1:  # An Exciting and Familiar Gensokyo
                    add_rule(music_track_location, lambda state: has_stage_list_access_item(world, state, [STAGE1_NAME_FULL,
                                                                                                    STAGE2_NAME_FULL]) or has_challenge_access_item(world,
                        state))
                case 2:  # Youkai Hook On
                    add_rule(music_track_location, lambda state: has_stage_list_access_item(world, state, [TUTORIAL_NAME_FULL,
                                                                                                    STAGE1_NAME_FULL,
                                                                                                    STAGE2_NAME_FULL,
                                                                                                    STAGE3_NAME_FULL]) or has_challenge_access_item(world,
                        state))
                case 3:  # Black Markets Can Happen Anywhere, Anytime
                    add_rule(music_track_location, lambda state: has_stage_list_access_item(world, state, [STAGE3_NAME_FULL,
                                                                                                    STAGE4_NAME_FULL]) or has_challenge_access_item(world,
                        state))
                case 4:  # Take Thy Danmaku In Hand, O Bulletphiles
                    add_rule(music_track_location, lambda state: has_stage_list_access_item(world, state, [STAGE4_NAME_FULL,
                                                                                                    STAGE5_NAME_FULL,
                                                                                                    STAGE6_NAME_FULL]) or has_challenge_access_item(world,
                        state))
                case 5:  # The 100th Black Market
                    add_rule(music_track_location, lambda state: has_stage_list_access_item(world, state, [STAGE5_NAME_FULL,
                                                                                                    STAGE6_NAME_FULL]) or has_challenge_access_item(world,
                        state))
                case 6:  # Lunatic Dreamer
                    add_rule(music_track_location,
                             lambda state: has_stage_list_access_item(world, state, [TUTORIAL_NAME_FULL]))
                case 7:  # Lunar Rainbow
                    add_rule(music_track_location,
                             lambda state: has_stage_list_access_item(world, state, [TUTORIAL_NAME_FULL, ENDSTAGE_NAME_FULL]))
                case 8:  # Where Is That Bustling Marketplace Now ~ Immemorial Marketeers
                    add_rule(music_track_location,
                             lambda state: has_stage_list_access_item(world, state, [ENDSTAGE_NAME_FULL]))
                case 9:  # A Rainbow-Colored World
                    add_rule(music_track_location, lambda state: has_takane_access(world, state))
                case _:
                    continue


def set_achievement_rules(world):
    #
    # Location rules for Achievements here.
    #
    # Each achievement has different conditions.
    # Check if their checks are enabled first.
    if world.options.achievement_checks:
        for achieve_id in ACHIEVE_NAME_DICT.keys():
            achievement_name_location = world.get_location(get_achievement_location_name_str(achieve_id))

            match achieve_id:
                case 0:  # Clear the game.
                    add_rule(achievement_name_location, lambda state: has_takane_access(world, state))
                case 1:  # Defeat all Stage 1 bosses.
                    add_rule(achievement_name_location, lambda state: has_stage_access_item(world, state, STAGE1_NAME))
                case 2:  # Stage 2 bosses.
                    add_rule(achievement_name_location, lambda state: has_stage_access_item(world, state, STAGE2_NAME))
                case 3:  # etc.
                    add_rule(achievement_name_location, lambda state: has_stage_access_item(world, state, STAGE3_NAME))
                case 4:  # Needs Blank Card as well.
                    add_rule(achievement_name_location, lambda state: has_nitori_access(world, state))
                case 5:
                    add_rule(achievement_name_location, lambda state: has_stage_access_item(world, state, STAGE5_NAME))
                case 6:  # Needs Capitalist's Dilemma as well.
                    add_rule(achievement_name_location, lambda state: has_takane_access(world, state))
                case 7:  # Defeat Chimata.
                    add_rule(achievement_name_location, lambda state: has_stage_access_item(world, state, ENDSTAGE_NAME))
                case 8:  # Defeat all bosses. Basically Full Story Clear with all stages.
                    add_rule(achievement_name_location, lambda state: all_bosses_access(world, state))
                case 9:  # Clear Challenge Market.
                    add_rule(achievement_name_location, lambda state: has_challenge_access_item(world, state, True))
                case 10:  # All equipment slots. 4th Market is where this can be achieved minimally.
                    add_rule(achievement_name_location, lambda state: has_equipment_achievement_access(world, state))
                case 11:  # All cards collected. Item-dependent.
                    add_rule(achievement_name_location, lambda state: all_cards_access(world, state))


def set_goal_condition(world) -> None:
    def minimum_story_clear(state: CollectionState) -> bool:
        if world.options.progressive_stages:
            if world.options.low_skill_logic:
                return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(STAGE6_NAME)) and state.has(NITORI_STORY_CARD_NAME, world.player) and low_skill_rules(world, state)
            else:
                return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(STAGE6_NAME)) and state.has(NITORI_STORY_CARD_NAME, world.player)

        if world.options.low_skill_logic:
            return state.has_all((NITORI_STORY_CARD_NAME, STAGE6_NAME_FULL), world.player) and low_skill_rules(world, state)
        else:
            return state.has_all((NITORI_STORY_CARD_NAME, STAGE6_NAME_FULL), world.player)

    def full_story_clear(state: CollectionState) -> bool:
        if world.options.progressive_stages:
            if world.options.low_skill_logic:
                return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(ENDSTAGE_NAME)) and state.has_all((NITORI_STORY_CARD_NAME, BLANK_CARD_NAME), world.player) and low_skill_rules(world, state)
            else:
                return state.has(PROGRESS_ITEM_NAME_FULL, world.player, get_progress_item_requirement(ENDSTAGE_NAME)) and state.has_all((NITORI_STORY_CARD_NAME, BLANK_CARD_NAME), world.player)

        if world.options.low_skill_logic:
            return state.has_all(
                (NITORI_STORY_CARD_NAME, BLANK_CARD_NAME, STAGE4_NAME_FULL, STAGE6_NAME_FULL, ENDSTAGE_NAME_FULL),
                world.player) and low_skill_rules(world, state)
        else:
            return state.has_all(
            (NITORI_STORY_CARD_NAME, BLANK_CARD_NAME, STAGE4_NAME_FULL, STAGE6_NAME_FULL, ENDSTAGE_NAME_FULL),
            world.player)

    # Since this checks for items, and full stage names are used as items, use that.
    def all_cards_clear(state: CollectionState) -> bool:
        return state.has_all(get_card_shop_item_names(), world.player)

    # To defeat all bosses, you need all stages to be available except the Challenge Market.
    # Both instances of Mike Goutokuji are counted.
    boss_condition_list = STAGE_NAME_LIST
    if CHALLENGE_NAME_FULL in boss_condition_list: boss_condition_list.remove(CHALLENGE_NAME_FULL)

    def all_bosses_clear(state: CollectionState) -> bool:
        # If Progressive Stages is enabled, this is just straight up Full Story Clear conditions.
        if world.options.progressive_stages:
            return full_story_clear(state)

        if world.options.low_skill_logic:
            return state.has_all((boss_condition_list + LOW_SKILL_CARD_LIST + [NITORI_STORY_CARD_NAME, BLANK_CARD_NAME]), world.player)
        else:
            return state.has_all((boss_condition_list + [NITORI_STORY_CARD_NAME, BLANK_CARD_NAME]), world.player)

    def full_clear_rule(state: CollectionState) -> bool:
        if world.options.progressive_stages:
            return state.has_all((get_card_shop_item_names()), world.player) and full_story_clear(state)

        return state.has_all((get_card_shop_item_names() + boss_condition_list), world.player)

    match world.options.completion_type:
        # Minimum Story Clear
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
        # Full Story Clear/Default
        case _:
            world.multiworld.completion_condition[world.player] = lambda state: full_story_clear(state)