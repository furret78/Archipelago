import unittest
import ctypes
from pymem.ressources.structure import LPSECURITY_ATTRIBUTES

from .. import DISPLAY_NAME, TouhouHBMWorld

class PythonTestFunctions(unittest.TestCase):
    game = DISPLAY_NAME
    world: TouhouHBMWorld

    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.thread_context = winapi_context.CONTEXT64()
        self.NULL_SECURITY_ATTRIBUTES = ctypes.cast(0, LPSECURITY_ATTRIBUTES)

    def test_slice(self):
        list = ["REIMU", "MARISA", "SAKUYA", "SANAE"]
        print(list[1:-1])
        # list[1:] prints ["MARISA", "SAKUYA", "SANAE"]
        # list[:-1] prints ["REIMU", "MARISA", "SAKUYA"]
        #
        # list[-2:] prints ["SAKUYA", "SANAE"]
        # list[list.index("MARISA"):] includes ["MARISA"] + the above.
        # list[-list.index("MARISA"):] removes ["SAKUYA"] from the above.
        # list[-list.index("MARISA"):] removes ["SAKUYA"] from the above.