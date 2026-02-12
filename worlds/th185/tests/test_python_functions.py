import traceback
import unittest

import pymem
import ctypes

import pywintypes
from pymem.ressources.kernel32 import GetThreadContext, SetThreadContext, OpenThread, ResumeThread, CloseHandle, \
    CreateRemoteThread
from pymem.ressources.structure import LPSECURITY_ATTRIBUTES
from win32con import CONTEXT_INTEGER, NULL
from win32process import CREATE_SUSPENDED

from test.bases import WorldTestBase
from .. import DISPLAY_NAME, TouhouHBMWorld, FILE_NAME
from ..variables import winapi_context
from ..variables.address_gameplay import ADDR_ANTICHEAT_HACK

class PythonTestFunctions(unittest.TestCase):
    game = DISPLAY_NAME
    world: TouhouHBMWorld

    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.thread_context = winapi_context.CONTEXT64()
        self.NULL_SECURITY_ATTRIBUTES = ctypes.cast(0, LPSECURITY_ATTRIBUTES)

    def test_slice(self):
        list = ["REIMU", "MARISA", "SAKUYA", "SANAE"]
        print(list[1:])
        # This prints ["MARISA", "SAKUYA", "SANAE"]

    def test_kill_player(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        self.pm.write_bytes(self.pm.base_address + ADDR_ANTICHEAT_HACK, bytes([0x90, 0x90]), 2)
        try:
            self.player_ptr: int = self.pm.read_uint(self.pm.base_address+0x000D7C3C)
            self.death_function = self.pm.base_address+0x00063450
            #game_thread = self.pm.start_thread(self.death_function)
            something_idk = None
            security_attribute = pywintypes.SECURITY_ATTRIBUTES()
            security_attribute.SECURITY_DESCRIPTOR = pywintypes.SECURITY_DESCRIPTOR()
            game_thread = CreateRemoteThread(
                self.pm.process_handle,
                security_attribute,
                0,
                self.death_function,
                0,
                CREATE_SUSPENDED,
                something_idk)

            # Check if this machine 64-bit is talking to 32-bit.
            # Since it's Touhou, of course it is 32-bit.
            self.thread_context: winapi_context.CONTEXT64
            self.new_thread_context: winapi_context.CONTEXT64

            self.thread_context.ContextFlags = CONTEXT_INTEGER

            GetThreadContext(game_thread, self.thread_context)

            self.thread_context.Ecx = self.player_ptr
            self.thread_context.ContextFlags = CONTEXT_INTEGER
            SetThreadContext(game_thread, self.thread_context)

            # Game crashes at Resume Thread since pointer was not set correctly.
            ResumeThread(game_thread)
            CloseHandle(game_thread)
        except Exception as e:
            print(f"ERROR: {e}")
            print(traceback.format_exc())
