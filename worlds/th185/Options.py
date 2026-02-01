from Options import *


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


class LowSkillLogic(DefaultOnToggle):
    """
    Whether the generation logic should include certain lategame cards as compulsory logic.
    """

    display_name = "Recommended Loadout in Logic"

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
    disable_challenge_logic: DisableChallengeLogic
    card_dex_checks: DexChecks
    trap_chance: TrapChance
    low_skill_logic: LowSkillLogic
    completion_type: CompletionType
    start_inventory_from_pool: StartInventoryPool


option_groups = [
    OptionGroup(
        "Gameplay Options",
        [TrapChance]
    ),
    OptionGroup(
        "Generation Options",
        [DisableChallengeLogic, DexChecks, LowSkillLogic, CompletionType]
    )
]

option_presets = {
    "easy": {
        "disable_challenge_logic": True,
        "card_dex_checks": False,
        "trap_chance": 0,
        "low_skill_logic": True,
        "completion_type": 0
    },
    "normal": {
        "disable_challenge_logic": True,
        "card_dex_checks": True,
        "trap_chance": 5,
        "low_skill_logic": True,
        "completion_type": 0
    },
    "hard": {
        "disable_challenge_logic": True,
        "card_dex_checks": True,
        "trap_chance": 10,
        "low_skill_logic": False,
        "completion_type": 1
    },
    "lunatic": {
        "disable_challenge_logic": False,
        "card_dex_checks": True,
        "trap_chance": 20,
        "low_skill_logic": False,
        "completion_type": 3
    },
    "overdrive": {
        "disable_challenge_logic": False,
        "card_dex_checks": True,
        "trap_chance": 25,
        "low_skill_logic": False,
        "completion_type": 4
    }
}
