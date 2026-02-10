from test.bases import WorldTestBase
from .. import DISPLAY_NAME, TouhouHBMWorld


class PythonTestFunctions(WorldTestBase):
    game = DISPLAY_NAME
    world: TouhouHBMWorld

    def test_slice(self):
        list = ["REIMU", "MARISA", "SAKUYA", "SANAE"]
        print(list[1:])
        # This prints ["MARISA", "SAKUYA", "SANAE"]