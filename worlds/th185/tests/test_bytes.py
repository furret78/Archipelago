import unittest

import pymem

from ..Tools import getPointerAddress, get_internal_boss_id_to_client
from ..variables.address_gameplay import ADDR_LAST_BOSS_MET, ADDR_CURRENT_STAGE_PTR, ADDR_SHOT_ATTACK
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

    def test_read_boss_data(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrBossMet = self.pm.base_address + ADDR_LAST_BOSS_MET
        last_boss_met_id = self.pm.read_int(addrBossMet)
        if last_boss_met_id < 1 or last_boss_met_id > 28: last_boss_met_id = -1
        print(f"Boss Met: {get_internal_boss_id_to_client(last_boss_met_id)}")

    def test_read_stage_status(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrStageStatus = self.pm.base_address + ADDR_CURRENT_STAGE_PTR
        addrUsed = getPointerAddress(self.pm, addrStageStatus, [0xB0])
        print(f"Stage status: {self.pm.read_int(addrUsed)}")

    def test_read_shot_attack(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrShotAttack = self.pm.base_address + ADDR_SHOT_ATTACK
        #addrUsed = getPointerAddress(self.pm, addrStageStatus, [0xB0])
        print(f"Shot Attack%: {self.pm.read_short(addrShotAttack)}")

    def test_write_shot_attack(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)
        addrShotAttack = self.pm.base_address + ADDR_SHOT_ATTACK
        self.pm.write_short(addrShotAttack, 1000)
        print(f"Shot Attack%: {self.pm.read_short(addrShotAttack)}")