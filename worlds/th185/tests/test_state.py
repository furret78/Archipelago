from test.bases import WorldTestBase
from worlds.th185 import DISPLAY_NAME


class TouhouWorldTest(WorldTestBase):
    game = DISPLAY_NAME

    def test_all_state_can_reach_everything(self):
        super().test_all_state_can_reach_everything()
    
    def test_empty_state_can_reach_something(self):
        super().test_empty_state_can_reach_something()