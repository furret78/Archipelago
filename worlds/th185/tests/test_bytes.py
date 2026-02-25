import unittest

import pymem

import Utils
from ..Tools import getAddressFromPointer, getPointerAddress, write_user_data, get_user_data
from ..variables.card_const import ADDR_CARD_TO_DEX, MALLET_CARD
from ..variables.meta_data import DISPLAY_NAME
from .. import TouhouHBMWorld, FILE_NAME, ADDR_BASE_MENU_PTR


class PythonTestFunctions(unittest.TestCase):
    game = DISPLAY_NAME
    world: TouhouHBMWorld

    def test_read_mallet_bytes(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrFromCardDex = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR, [ADDR_CARD_TO_DEX[MALLET_CARD]])
        print(self.pm.read_bytes(addrFromCardDex, 1))

    def test_write_mallet_bytes(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrFromCardDex = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR,
                                            [ADDR_CARD_TO_DEX[MALLET_CARD]])
        self.pm.write_bytes(addrFromCardDex, bytes([0x00]), 1)
        print(self.pm.read_bytes(addrFromCardDex, 1))

    def test_write_client_settings(self):
        write_user_data({
            "path": "something here",
            "numbers": 40
        })

    def test_read_client_settings(self):
        print(get_user_data())