from test.bases import WorldTestBase
from worlds.th185 import TouhouHBMWorld
from worlds.th185.variables.boss_and_stage import CARD_DEX_NAME
from worlds.th185.variables.meta_data import DISPLAY_NAME


class TouhouWorldTestFill(WorldTestBase):
    game = DISPLAY_NAME
    world: TouhouHBMWorld

    def test_fill(self):
        super(TouhouWorldTestFill, self).test_fill()

    def can_reach_region(self, region: str) -> bool:
        return super().can_reach_region(CARD_DEX_NAME)