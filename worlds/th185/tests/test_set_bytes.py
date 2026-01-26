import unittest
import pymem

from worlds.th185.Tools import getPointerAddress
from worlds.th185.variables.address_gameplay import ADDR_BULLET_MONEY_2_PTR, ADDR_GAME_FUNDS_PTR, ADDR_ANTICHEAT_HACK
from worlds.th185.variables.address_menu import ADDR_BASE_MENU_PTR, ADDR_MENU_FUNDS_PTR
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

    def test_write_bullet_money(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        self.addrToWrite = self.pm.base_address + ADDR_BULLET_MONEY_2_PTR
        try:
            self.pm.write_int(self.addrToWrite, 500)
        except Exception as e:
            print(f"ERROR: {e}")

    def test_write_game_funds(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        self.addrToWrite = self.pm.base_address + ADDR_GAME_FUNDS_PTR
        try:
            self.pm.write_int(self.addrToWrite, 500)
        except Exception as e:
            print(f"ERROR: {e}")

    def test_write_menu_funds(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        self.pm.write_bytes(self.pm.base_address + ADDR_ANTICHEAT_HACK, bytes([0x90, 0x90]), 2)
        self.addrToWrite = getPointerAddress(self.pm, self.pm.base_address+ADDR_BASE_MENU_PTR, [ADDR_MENU_FUNDS_PTR])
        try:
            self.pm.write_int(self.addrToWrite, 20000)
        except Exception as e:
            print(f"ERROR: {e}")