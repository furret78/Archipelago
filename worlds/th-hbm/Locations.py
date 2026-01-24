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
    for boss_sets in ALL_BOSSES_LIST[challenge_set_id]:
        if challenge_set_id <= TUTORIAL_ID or challenge_set_id >= STAGE_CHIMATA_ID: continue
        boss_challenge_id = 0
        for boss_challenge in boss_sets:
            # ID 4 is reaching the story bosses.
            if boss_challenge_id >= 4: continue
            result_boss_list.append(boss_challenge)
            boss_challenge_id += 1
        challenge_set_id += 1
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
    regionName: str = CARD_SHOP_NAME
    if is_dex: regionName = CARD_DEX_NAME
    return f"[{regionName}] {CARD_ID_TO_NAME[card_id]}"


location_id_offset = 1
location_table = {} # Name to ID
location_id_to_name = {} # ID to Name

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
# TBD

# Card Dex locations.
card_index_id = 0
for cards in ABILITY_CARD_LIST:
    cardLocationNameString: str = get_card_location_name_str(cards, True)
    location_table[cardLocationNameString] = location_id_offset
    location_id_to_name[location_id_offset] = cardLocationNameString
    location_id_offset += 1
    card_index_id += 1


def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: location_table[location_name] for location_name in location_names}


def create_regular_locations(world):
    region_dict = get_regions_dict(world)

    # Stages Tutorial-Challenge
    local_stage_id = 0
    for game_stage in STAGE_LIST:
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

                region_dict[stages].locations.append(boss_encounter_location, boss_defeat_location)
        elif getattr(world.options, "challenge_checks"):
            for challenge_boss in get_boss_names_challenge_list():
                locationEncounter: str = get_boss_location_name_str(STAGE_CHALLENGE_ID, challenge_boss)

                boss_encounter_location = TouhouHBMLocation(
                    world.player,
                    locationEncounter,
                    world.location_name_to_id[locationEncounter],
                    region_dict[CHALLENGE_NAME]
                )

                region_dict[CHALLENGE_NAME].locations.append(boss_encounter_location)

    # Ability Card Shop Unlocks
    # Not every card is available in every stage.
    # TBD.

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
            region_dict[CARD_DEX_NAME]
        )

        region_dict[CARD_DEX_NAME].locations.append(card_dex_location)