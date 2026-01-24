import unittest
import pymem

from worlds.th185.Tools import getPointerAddress
from worlds.th185.variables.address_menu import ADDR_BASE_MENU_PTR
from worlds.th185.variables.boss_and_stage import ADDR_STAGE_ID_TO_PTR, STAGE1_ID
from worlds.th185.variables.meta_data import FILE_NAME


class SetBytesTest(unittest.TestCase):

    def test_write_bytes(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        self.addrToWrite = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR, [ADDR_STAGE_ID_TO_PTR[STAGE1_ID]])
        try:
            self.pm.write_bytes(self.addrToWrite, bytes([0x00]), 1)
        except Exception as e:
            print(f"ERROR: {e}")