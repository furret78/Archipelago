from .Regions import get_regions_dict
from .variables.boss_and_stage import *
from .variables.card_const import ABILITY_CARD_LIST, CARD_ID_TO_NAME, RINGO_CARD, MALLET_CARD
from .variables.meta_data import *
from BaseClasses import Location


class TouhouHBMLocation(Location):
    game: str = SHORT_NAME


def create_all_locations(world):
    create_regular_locations(world)


def get_boss_names_challenge_list() -> list[str]:
    """
    Gets all bosses that appears in Challenge Market.
    """
    result_boss_list: list[str] = []
    challenge_set_id = 1
    # This will iterate through the entire boss list.
    for boss_sets in ALL_BOSSES_LIST:
        if challenge_set_id <= TUTORIAL_ID or challenge_set_id >= STAGE_CHIMATA_ID: continue
        # Gets the actual list data of the current stage chosen.
        current_boss_set = ALL_BOSSES_LIST[challenge_set_id]
        # Iterate through it. If the index is 4 or more, that's a story boss.
        boss_challenge_id = 0
        for boss_challenge in current_boss_set:
            if boss_challenge_id >= 4: continue
            result_boss_list.append(boss_challenge)
            boss_challenge_id += 1
        # Move onto the next stage.
        challenge_set_id += 1

    # Return the final list.
    return result_boss_list


def get_boss_location_name_str(market_stage_id: int, boss_name: str, is_defeat: bool = False) -> str:
    """
    Gets the location name according to Stage ID and Boss name.
    Has an Encounter and Defeat variant.
    """
    locationType: str = "Encounter"
    if is_defeat: locationType = "Defeat"
    return f"[{STAGE_LIST[market_stage_id]}] {boss_name} - {locationType}"


def get_card_location_name_str(card_id: str, is_dex: bool = False) -> str:
    """
    Gets the location name according to Ability Card string ID.
    Has a Shop Unlock and Dex Unlock variant.
    """
    regionName: str = ENDSTAGE_CHOOSE_NAME
    if is_dex: regionName = CARD_DEX_NAME
    return f"[{regionName}] {CARD_ID_TO_NAME[card_id]}"


location_id_offset = 1
location_table = {} # Name to ID
location_id_to_name = {} # ID to Name
location_cards_id_to_card_string_id = {}

# Boss locations
stage_id = 0
for stages in STAGE_LIST:
    # Normal stages
    if stage_id < STAGE_CHALLENGE_ID:
        # This goes through the boss list of a given market.
        for boss in ALL_BOSSES_LIST[stage_id]:
            currentBossStringEncounter: str = get_boss_location_name_str(stage_id, boss)
            currentBossStringDefeat: str = get_boss_location_name_str(stage_id, boss, True)
            # Add the boss Encounter locations.
            location_table[currentBossStringEncounter] = location_id_offset
            location_id_to_name[location_id_offset] = currentBossStringEncounter
            # Add the boss Defeat locations.
            location_table[currentBossStringDefeat] = location_id_offset + 1
            location_id_to_name[location_id_offset + 1] = currentBossStringDefeat
            # Offset the ID number.
            location_id_offset += 2

    # Challenge Market
    if stage_id == STAGE_CHALLENGE_ID:
        for boss in get_boss_names_challenge_list():
            currentBossStringEncounter: str = get_boss_location_name_str(STAGE_CHALLENGE_ID, boss)
            location_table[currentBossStringEncounter] = location_id_offset
            location_id_to_name[location_id_offset] = currentBossStringEncounter
            location_id_offset += 1

    stage_id += 1

# Card Shop locations at the end of each Market.
for cards in ABILITY_CARD_LIST:
    cardLocationNameString: str = get_card_location_name_str(cards, False)
    location_table[cardLocationNameString] = location_id_offset
    location_id_to_name[location_id_offset] = cardLocationNameString
    location_cards_id_to_card_string_id[location_id_offset] = cards
    location_id_offset += 1

# Card Dex locations.
for cards in ABILITY_CARD_LIST:
    cardLocationNameString: str = get_card_location_name_str(cards, True)
    location_table[cardLocationNameString] = location_id_offset
    location_id_to_name[location_id_offset] = cardLocationNameString
    location_cards_id_to_card_string_id[location_id_offset] = cards
    location_id_offset += 1


def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: location_table[location_name] for location_name in location_names}


def create_regular_locations(world):
    region_dict = get_regions_dict(world)

    # Stages Tutorial-Challenge
    for game_stage in STAGE_LIST:
        local_stage_id = STAGE_NAME_TO_ID[game_stage]
        if game_stage != CHALLENGE_NAME:
            for boss_name in ALL_BOSSES_LIST[local_stage_id]:
                locationEncounter: str = get_boss_location_name_str(local_stage_id, boss_name)
                locationDefeat: str = get_boss_location_name_str(local_stage_id, boss_name, True)

                boss_encounter_location = TouhouHBMLocation(
                    world.player,
                    locationEncounter,
                    world.location_name_to_id[locationEncounter],
                    region_dict[stages]
                )
                boss_defeat_location = TouhouHBMLocation(
                    world.player,
                    locationDefeat,
                    world.location_name_to_id[locationDefeat],
                    region_dict[stages]
                )

                region_dict[stages].locations.append(boss_encounter_location)
                region_dict[stages].locations.append(boss_defeat_location)
        elif getattr(world.options, "challenge_checks"):
            boss_challenge_list = get_boss_names_challenge_list()
            for challenge_boss in boss_challenge_list:
                locationEncounter: str = get_boss_location_name_str(STAGE_CHALLENGE_ID, challenge_boss)

                boss_encounter_location = TouhouHBMLocation(
                    world.player,
                    locationEncounter,
                    world.location_name_to_id[locationEncounter],
                    region_dict[CHALLENGE_NAME]
                )

                print(locationEncounter)
                region_dict[CHALLENGE_NAME].locations.append(boss_encounter_location)

    # Ability Card Shop Unlocks
    # Not every card is available in every stage.
    for stage_card in ABILITY_CARD_LIST:
        # End-level Card Selection.
        # Starting Card option allows for choosing Ringo-Brand Dango or Miracle Mallet to begin the run.
        # Remember to remove their dex checks as needed.
        starting_card_choice = getattr(world.options, "starting_card")

        if ((starting_card_choice == 1 and stage_card == RINGO_CARD)
            or (starting_card_choice == 2 and stage_card == MALLET_CARD)):
            continue

        cardLocationName: str = get_card_location_name_str(stage_card, False)

        card_dex_location = TouhouHBMLocation(
            world.player,
            cardLocationName,
            world.location_name_to_id[cardLocationName],
            region_dict[ENDSTAGE_CHOOSE_NAME]
        )

        region_dict[ENDSTAGE_CHOOSE_NAME].locations.append(card_dex_location)

    # Ability Card Dex
    for dex_card in ABILITY_CARD_LIST:
        # Starting Card option allows for choosing Ringo-Brand Dango or Miracle Mallet to begin the run.
        # Remember to remove their dex checks as needed.
        starting_card_choice = getattr(world.options, "starting_card")

        if ((starting_card_choice == 1 and dex_card == RINGO_CARD)
            or (starting_card_choice == 2 and dex_card == MALLET_CARD)):
            continue

        cardLocationName: str = get_card_location_name_str(dex_card, True)

        card_dex_location = TouhouHBMLocation(
            world.player,
            cardLocationName,
            world.location_name_to_id[cardLocationName],
            region_dict[CARD_SHOP_NAME]
        )

        region_dict[CARD_SHOP_NAME].locations.append(card_dex_location)