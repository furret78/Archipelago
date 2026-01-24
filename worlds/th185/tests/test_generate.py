import random
from typing import Optional, Dict, Any, cast

from BaseClasses import *
from Generate import *
from test.bases import WorldTestBase
from test.general import gen_steps
from worlds.AutoWorld import call_all
from worlds.th185 import TouhouHBMWorld
from worlds.th185.variables.meta_data import DISPLAY_NAME


class TouhouWorldTest(WorldTestBase):
    game = DISPLAY_NAME
    world: TouhouHBMWorld

    seed: Optional[int] = None
    player = 1

    def generate_world(self, options: Dict[str, Any]) -> None:
        self.multiworld = MultiWorld(1)
        self.multiworld.game[self.player] = self.game
        self.multiworld.player_name = {self.player: "Tester"}
        self.multiworld.set_seed(self.seed)
        random.seed(self.multiworld.seed)
        self.multiworld.seed_name = get_seed_name(random)  # only called to get same RNG progression as Generate.py
        args = Namespace()
        for name, option in AutoWorld.AutoWorldRegister.world_types[self.game].options_dataclass.type_hints.items():
            new_option = option.from_any(options.get(name, option.default))
            new_option.verify(TouhouHBMWorld, "Tester",
                              PlandoOptions.items | PlandoOptions.connections | PlandoOptions.texts | PlandoOptions.bosses)
            setattr(args, name, {
                1: new_option
            })
        self.multiworld.set_options(args)
        self.world: TouhouHBMWorld = cast(TouhouHBMWorld, self.multiworld.worlds[self.player])
        self.multiworld.state = CollectionState(self.multiworld)
        try:
            for step in gen_steps:
                call_all(self.multiworld, step)
        except Exception as ex:
            ex.add_note(f"Seed: {self.multiworld.seed}")
            raise