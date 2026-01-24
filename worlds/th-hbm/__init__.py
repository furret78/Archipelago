from .variables.meta_data import SHORT_NAME, DISPLAY_NAME
from ..LauncherComponents import Component, components, launch_subprocess, Type
from .World import TouhouHBMWorld as TouhouHBMWorld

def launch_client():
    """
    Launch a Client instance.
    """
    from .Client import launch
    launch_subprocess(launch, name="GameClient")

components.append(Component(
    display_name=SHORT_NAME+" Client",
    func=launch_client,
    component_type=Type.CLIENT,
    game_name=DISPLAY_NAME
))