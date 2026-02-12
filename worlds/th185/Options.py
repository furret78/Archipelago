from Options import *


class DisableChallengeLogic(DefaultOnToggle):
    """
    Prevents the game from taking Challenge Market into account when placing items in Market Card Reward locations.
    Disable to allow Challenge Market in logic.
    """

    display_name = "Disable Challenge Market in Logic"


class TrapChance(Range):
    """
    Percentage chance that any given filler Item will be replaced by a trap item.
    """

    display_name = "Trap Chance"

    range_start = 0
    range_end = 100
    default = 10


class LowSkillLogic(DefaultOnToggle):
    """
    Whether the generation logic should include certain Ability Cards as compulsory before challenging late-game stages.

    This includes: Life Explosion Elixir, Princess Kaguya's Secret Stash, Soot-covered Uchiwa,
    Esteemed Authority, Gluttonous Centipede, and Money Is The Best Lawyer In Hell.
    """

    display_name = "Recommended Loadout in Logic"


class IncludeGameplayFiller(DefaultOnToggle):
    """
    Whether filler items that are not Funds or Bullet Money will appear during generation.
    Does not affect Traps.
    """

    display_name = "Include Non-Money Filler"


class DeathLinkTrigger(Choice):
    """
    Determines when a Death Link would be sent. Only takes effect if Death Link is enabled.

    0. Upon losing a life. This means Life Explosion Elixir will also trigger Death Link.
    1. Upon failing a stage attempt. All lives must be lost before this triggers.
    """

    display_name = "Death Link Trigger"

    option_Upon_Life_Loss = 0
    option_Upon_Stage_Fail = 1

    default = option_Upon_Life_Loss

class InvincAgainstDeathLink(DefaultOnToggle):
    """
    Determines whether invincibility can protect against incoming Death Links.
    """

    display_name = "Anti-Death Link Invincibility"


class CompletionType(Choice):
    """
    A goal to reach.

    0. Full Main Story - Chimata Tenkyuu, Nitori Kawashiro, and Takane Yamashiro defeated.
    1. Minimum Main Story - Takane Yamashiro defeated.
    2. All Cards Owned - Full Ability Card dex unlocked.
    3. All Bosses Defeated - All bosses defeated (except in Challenge Market).
    4. Full Clear - All of the above.
    """

    display_name = "Completion Goal"

    option_Full_Main_Story = 0
    option_Minimum_Main_Story = 1
    option_All_Cards_Owned = 2
    option_All_Bosses_Defeated = 3
    option_Full_Clear = 4

    default = option_Full_Main_Story


@dataclass()
class TouhouHBMDataclass(PerGameCommonOptions):
    disable_challenge_logic: DisableChallengeLogic
    trap_chance: TrapChance
    low_skill_logic: LowSkillLogic
    include_gameplay_filler: IncludeGameplayFiller
    death_link: DeathLink
    death_link_trigger: DeathLinkTrigger
    death_link_invincibility: InvincAgainstDeathLink
    completion_type: CompletionType
    start_inventory_from_pool: StartInventoryPool


option_groups = [
    OptionGroup(
        "Game Options",
        [TrapChance, DeathLinkTrigger, InvincAgainstDeathLink, CompletionType]
    ),
    OptionGroup(
        "Generation Options",
        [DisableChallengeLogic, LowSkillLogic, IncludeGameplayFiller]
    )
]

option_presets = {
    "easy": {
        "disable_challenge_logic": True,
        "trap_chance": 0,
        "low_skill_logic": True,
        "include_gameplay_filler": False,
        "death_link": False,
        "death_link_trigger": 0,
        "death_link_invincibility": True,
        "completion_type": 0 # Full Main Story
    },
    "normal": {
        "disable_challenge_logic": True,
        "trap_chance": 5,
        "low_skill_logic": True,
        "include_gameplay_filler": False,
        "death_link": False,
        "death_link_trigger": 0,
        "death_link_invincibility": True,
        "completion_type": 0 # Full Main Story
    },
    "hard": {
        "disable_challenge_logic": True,
        "trap_chance": 10,
        "low_skill_logic": False,
        "include_gameplay_filler": True,
        "death_link": True,
        "death_link_trigger": 1,
        "death_link_invincibility": False,
        "completion_type": 1 # Minimum Main Story
    },
    "lunatic": {
        "disable_challenge_logic": False,
        "trap_chance": 20,
        "low_skill_logic": False,
        "include_gameplay_filler": True,
        "death_link": True,
        "death_link_trigger": 0,
        "death_link_invincibility": False,
        "completion_type": 3 # All Bosses Defeated
    },
    "overdrive": {
        "disable_challenge_logic": False,
        "trap_chance": 50,
        "low_skill_logic": False,
        "include_gameplay_filler": True,
        "death_link": True,
        "death_link_trigger": 0,
        "death_link_invincibility": False,
        "completion_type": 4 # Full Clear
    }
}
