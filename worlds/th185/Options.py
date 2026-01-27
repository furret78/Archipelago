from Options import *


class StartingMarket(Choice):
    """
    Determines which stage should be unlocked at the start of the game.
    """

    display_name = "Starting Market"

    option_Tutorial_Market = 0
    option_First_Market = 1
    option_Second_Market = 2
    option_Third_Market = 3
    option_Fourth_Market = 4
    option_Fifth_Market = 5
    option_Sixth_Market = 6
    option_End_of_Market = 7
    option_Challenge_Market = 8
    option_No_Markets_Unlocked = 9

    default = option_No_Markets_Unlocked


class ChallengeChecks(Toggle):
    """
    Enables checks for boss encounters in the Challenge Market.
    """

    display_name = "Challenge Market Encounters"


class DisableChallengeLogic(DefaultOnToggle):
    """
    Prevents the game from taking Challenge Market into account when placing items in Market End Reward locations. Disable to allow Challenge Market in logic.
    """

    display_name = "Disable Challenge Market in Logic"


class DexChecks(DefaultOnToggle):
    """
    Enables checks for Ability Card Dex unlocks.
    """

    display_name = "Ability Card Dex"


class TrapChance(Range):
    """
    Percentage chance that any given filler Item will be replaced by a trap Item.
    """

    display_name = "Trap Chance"

    range_start = 0
    range_end = 100
    default = 10


class StartingCard(Choice):
    """
    With no cards unlocked, the player's default choice will be the Blank Card. You can choose to have one card unlocked to begin the run with.

    Available options: No cards at all, Ringo-Brand Dango, Miracle Mallet.
    """

    display_name = "Starting Ability Card"

    option_No_Cards = 0
    option_Ringo_Brand_Dango = 1
    option_Miracle_Mallet = 2

    default = option_Miracle_Mallet


class CompletionType(Choice):
    """
    A goal to reach.

    Full Main Story - Chimata Tenkyuu, Nitori Kawashiro, and Takane Yamashiro defeated.
    Minimum Main Story - Takane Yamashiro defeated.
    All Cards Owned - Full Ability Card dex unlocked.
    All Bosses Defeated - All bosses defeated (except in Challenge Market).
    Full Clear - All of the above.
    """

    display_name = "Goal"

    option_Full_Main_Story = 0
    option_Minimum_Main_Story = 1
    option_All_Cards_Owned = 2
    option_All_Bosses_Defeated = 3
    option_Full_Clear = 4

    default = option_Full_Main_Story


@dataclass()
class TouhouHBMDataclass(PerGameCommonOptions):
    starting_market: StartingMarket
    challenge_checks: ChallengeChecks
    disable_challenge_logic: DisableChallengeLogic
    card_dex_checks: DexChecks
    trap_chance: TrapChance
    starting_card: StartingCard
    completion_type: CompletionType


option_presets = {
    "hard": {
        "starting_market": 9,
        "challenge_checks": True,
        "disable_challenge_logic": True,
        "card_dex_checks": True,
        "trap_chance": 10,
        "starting_card": 1,
        "completion_type": 3
    }
}
