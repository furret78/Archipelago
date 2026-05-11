# AP 0.6.7 moves CollectionRule to BaseClasses
try:
    from BaseClasses import CollectionRule
except ImportError:
    from worlds.generic.Rules import CollectionRule
from .Tools import get_boss_location_name_str, get_music_location_name_str, get_achievement_location_name_str, \
    get_boss_names_challenge_list, get_stage_clear_location_name_str
from .Options import StageBossLocations
from .variables.music_and_achiev import MUSIC_ROOM_NAME_DICT, ACHIEVE_NAME_DICT
from .Rules_Utils import *


def set_all_rules(world) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_goal_condition(world)


def set_all_entrance_rules(world) -> None:
    def has_correct_stage_item(given_stage: str):
        if (given_stage == CHALLENGE_NAME_FULL and world.options.disable_challenge_logic and
            not world.options.progressive_stages):
            return HasAll(*STAGE_NAME_LIST)

        progress_access = (
            OptionFilter(ProgressiveStages, True) &
            Has(PROGRESS_STAGE_ITEM_NAME, count=get_progress_item_requirement(given_stage, True))
        )
        nonprogress_access = Has(given_stage, options=[OptionFilter(ProgressiveStages, False)])
        return progress_access | nonprogress_access

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
        world.set_rule(origin_to_region_dict[stage_name], has_correct_stage_item(stage_name))


def set_all_location_rules(world) -> None:
    set_boss_location_rules(world)
    set_stage_location_rules(world)
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
                if (world.options.stage_boss_locations == StageBossLocations.option_stage_only and
                    boss_name != BOSS_NITORI_NAME and boss_name != BOSS_TAKANE_NAME): continue
                location_encounter = world.get_location(get_boss_location_name_str(stage_id_from_list, boss_name))
                location_defeat = world.get_location(get_boss_location_name_str(stage_id_from_list, boss_name, True))

                # Check if it's Nitori or Takane
                if boss_name == BOSS_NITORI_NAME:
                    world.set_rule(location_encounter, has_encounter_access(BOSS_NITORI))
                    world.set_rule(location_defeat, has_nitori_access())
                    continue
                elif boss_name == BOSS_TAKANE_NAME:
                    world.set_rule(location_encounter, has_encounter_access(BOSS_TAKANE))
                    world.set_rule(location_defeat, has_takane_access())
                    continue
                # Hidden 4th bosses can only be met if the other bosses have already been defeated.
                elif boss_name in HIDDEN_BOSSES_LIST:
                    world.set_rule(location_encounter, has_stage_access_item(stage_short_name))
                    world.set_rule(location_defeat, has_stage_access_item(stage_short_name))
                    continue

                # If it's none of them
                world.set_rule(location_encounter, has_encounter_access(stage_short_name))
                world.set_rule(location_defeat, has_stage_access_item(stage_short_name))
        # Challenge Market clause.
        else:
            if world.options.stage_boss_locations == StageBossLocations.option_stage_only: continue
            for challenge_boss in get_boss_names_challenge_list():
                location_encounter = get_boss_location_name_str(STAGE_CHALLENGE_ID, challenge_boss)
                location_defeat = get_boss_location_name_str(STAGE_CHALLENGE_ID, challenge_boss, True)
                world.set_rule(world.get_location(location_encounter), has_challenge_access_item(True))
                world.set_rule(world.get_location(location_defeat), has_challenge_access_item(True))


def set_stage_location_rules(world):
    """
    Location rules for generic stage clears.
    """
    if world.options.stage_boss_locations == StageBossLocations.option_boss_only: return
    for stage_short_name in STAGE_LIST:
        location_stage_clear = world.get_location(get_stage_clear_location_name_str(STAGE_NAME_TO_ID[stage_short_name]))
        if stage_short_name != CHALLENGE_NAME:
            world.set_rule(location_stage_clear, has_stage_access_item(stage_short_name))
        else:
            world.set_rule(location_stage_clear, has_challenge_access_item(True))


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
                    world.set_rule(location_card_reward, has_tutorial_access_item())
                # Capitalist's Dilemma requires Blank Card and 4th Market unlock.
                elif card_string_id == NITORI_STORY_CARD:
                    world.set_rule(
                        location_card_reward,
                        has_nitori_access() | has_challenge_access_item()
                    )
                # Hundredth Black Market requires Capitalist's Dilemma and 6th Market unlock.
                elif card_string_id == TAKANE_STORY_CARD:
                    world.set_rule(
                        location_card_reward,
                        has_takane_access() | has_challenge_access_item()
                    )
                # Freewheeling Severed Head somehow shows up in End of Market.
                elif card_string_id == SEKIBANKI_CARD:
                    world.set_rule(location_card_reward, has_sekibanki_access())
                # Generic conditions otherwise.
                else:
                    world.set_rule(location_card_reward, has_stage_access_item(stage_name))

                was_exclusive_card = True

        if was_exclusive_card: continue

        # If it gets here, that means the card in question is not exclusive.
        # Check for Item Season and Sheep You Want to Count first.
        if card_string_id == LILY_WHITE_CARD:
            lily_location_name: str = get_card_location_name_str(LILY_WHITE_CARD, False)
            lily_location = world.get_location(lily_location_name)
            world.set_rule(lily_location, has_lily_white_access())
            continue
        if card_string_id == DOREMY_CARD:
            doremy_location_name: str = get_card_location_name_str(DOREMY_CARD, False)
            doremy_location = world.get_location(doremy_location_name)
            world.set_rule(doremy_location, has_doremy_access())
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
    world.set_rule(nazrin_card1_location, has_any_stage_access_item())
    nazrin_card2_location = world.get_location(get_card_location_name_str(NAZRIN_CARD_2, True))
    world.set_rule(nazrin_card2_location, has_nazrin2_access())
    # The rest are only available if their respective item is available in the shop.
    for card_string_id in ABILITY_CARD_LIST:
        # Skip Nazrin's cards.
        if card_string_id in ABILITY_CARD_CANNOT_EQUIP: continue

        card_dex_location = world.get_location(get_card_location_name_str(card_string_id, True))
        world.set_rule(card_dex_location, has_grind_access(card_string_id))


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
                    world.set_rule(
                        music_track_location,
                        has_stage_list_access_item([STAGE1_NAME_FULL, STAGE2_NAME_FULL]) |
                        has_challenge_access_item()
                    )
                case 2:  # Youkai Hook On
                    world.set_rule(
                        music_track_location,
                        has_stage_list_access_item([TUTORIAL_NAME_FULL, STAGE1_NAME_FULL, STAGE2_NAME_FULL, STAGE3_NAME_FULL]) |
                        has_challenge_access_item()
                    )
                case 3:  # Black Markets Can Happen Anywhere, Anytime
                    world.set_rule(
                        music_track_location,
                        has_stage_list_access_item([STAGE3_NAME_FULL, STAGE4_NAME_FULL]) |
                        has_challenge_access_item()
                    )
                case 4:  # Take Thy Danmaku In Hand, O Bulletphiles
                    world.set_rule(
                        music_track_location,
                        has_stage_list_access_item([STAGE5_NAME_FULL, STAGE4_NAME_FULL, STAGE6_NAME_FULL]) |
                        has_challenge_access_item()
                    )
                case 5:  # The 100th Black Market
                    world.set_rule(
                        music_track_location,
                        has_stage_list_access_item([STAGE5_NAME_FULL, STAGE6_NAME_FULL]) |
                        has_challenge_access_item()
                    )
                case 6:  # Lunatic Dreamer
                    world.set_rule(music_track_location, has_stage_access_item(TUTORIAL_NAME))
                case 7:  # Lunar Rainbow
                    world.set_rule(music_track_location,
                             has_stage_list_access_item([TUTORIAL_NAME_FULL, ENDSTAGE_NAME_FULL]))
                case 8:  # Where Is That Bustling Marketplace Now ~ Immemorial Marketeers
                    world.set_rule(music_track_location, has_stage_access_item(ENDSTAGE_NAME))
                case 9:  # A Rainbow-Colored World
                    world.set_rule(music_track_location, has_takane_access())
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
                    world.set_rule(achievement_name_location, has_takane_access())
                case 1:  # Defeat all Stage 1 bosses.
                    world.set_rule(achievement_name_location, has_stage_access_item(STAGE1_NAME))
                case 2:  # Stage 2 bosses.
                    world.set_rule(achievement_name_location, has_stage_access_item(STAGE2_NAME))
                case 3:  # etc.
                    world.set_rule(achievement_name_location, has_stage_access_item(STAGE3_NAME))
                case 4:  # Needs Blank Card as well.
                    world.set_rule(achievement_name_location, has_nitori_access())
                case 5:
                    world.set_rule(achievement_name_location, has_stage_access_item(STAGE5_NAME))
                case 6:  # Needs Capitalist's Dilemma as well.
                    world.set_rule(achievement_name_location, has_takane_access())
                case 7:  # Defeat Chimata.
                    world.set_rule(achievement_name_location, has_stage_access_item(ENDSTAGE_NAME))
                case 8:  # Defeat all bosses. Basically Full Story Clear with all stages.
                    world.set_rule(achievement_name_location, all_bosses_access())
                case 9:  # Clear Challenge Market.
                    world.set_rule(achievement_name_location, has_challenge_access_item(True))
                case 10:  # All equipment slots. 4th Market is where this can be achieved minimally.
                    world.set_rule(achievement_name_location, has_equipment_achievement_access())
                case 11:  # All cards collected. Item-dependent.
                    world.set_rule(achievement_name_location, all_cards_access())


def set_goal_condition(world) -> None:
    world.set_completion_rule(get_goal_condition(world.options.completion_type))