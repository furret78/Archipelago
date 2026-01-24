import pymem
import pymem.exception
from pyshortcuts import sleep

from .Tools import *
from .variables.card_const import *
from .variables.meta_data import *
from .variables.address_gameplay import *
from .variables.boss_and_stage import *

class GameController:
    """Class accessing the game's memory."""

    def __init__(self):
        self.pm = pymem.Pymem(GAME_NAME)

        # Gameplay only.
        self.addrCurrentStage = self.pm.base_address+ADDR_CURRENT_STAGE_PTR # Check if pointer itself is valid.
        self.addrGameFunds = self.pm.base_address+ADDR_GAME_FUNDS_PTR
        self.addrBulletMoney = self.pm.base_address+ADDR_BULLET_MONEY_PTR
        self.addrBulletMoney2 = self.pm.base_address+ADDR_BULLET_MONEY_2_PTR
        self.addrLives = self.pm.base_address+ADDR_LIVES_PTR

        # Menu and record-keeping.
        usable_address_menu = self.pm.base_address+ADDR_BASE_MENU_PTR
        self.addrMenuFunds = getPointerAddress(self.pm, usable_address_menu, ADDR_MENU_FUNDS_PTR)
        self.allocated_memory_to_cheat = False

    def check_if_in_stage(self) -> bool:
        try:
            self.addrCurrentStage = self.pm.base_address+ADDR_CURRENT_STAGE_PTR
            stage = int.from_bytes(self.pm.read_bytes(self.addrCurrentStage, 1))
            return True
        except pymem.exception.MemoryReadError as e:
            return False

    # Lives (in-game) functions
    def getLives(self) -> int:
        return int.from_bytes(self.pm.read_bytes(self.addrLives, 1))

    def setLives(self, value):
        self.pm.write_int(self.addrLives, value)

    # Funds (in-game) functions
    def getGameFunds(self) -> int:
        return int.from_bytes(self.pm.read_bytes(self.addrGameFunds, 4))

    def setGameFunds(self, value):
        self.pm.write_int(self.addrGameFunds, value)

    # Bullet Money (in-game) functions
    def getBulletMoney(self) -> int:
        return int.from_bytes(self.pm.read_bytes(self.addrBulletMoney, 4))

    def setBulletMoney(self, value):
        self.pm.write_int(self.addrBulletMoney, value)
        self.pm.write_int(self.addrBulletMoney2, value)

    # Funds (menu) functions
    def getMenuFunds(self) -> int:
        self.addrMenuFunds = getPointerAddress(self.pm, self.pm.base_address+ADDR_BASE_MENU_PTR, ADDR_MENU_FUNDS_PTR)
        return int.from_bytes(self.pm.read_bytes(self.addrMenuFunds, 4))

    def setMenuFunds(self, value):
        self.pm.write_int(self.addrMenuFunds, value)

    # Stage lock functions
    def getStageStatus(self, stage_id: int) -> bool:
        stageLockAddress = getPointerAddress(self.pm, self.pm.base_address+ADDR_BASE_MENU_PTR, ADDR_STAGE_ID_TO_PTR[stage_id])
        return int.from_bytes(self.pm.read_bytes(stageLockAddress, 1)) > 0

    def setStageStatus(self, stage_id: int, value: int):
        stageLockAddress = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR, ADDR_STAGE_ID_TO_PTR[stage_id])
        self.pm.write_bytes(stageLockAddress, bytes(value), 1)

    # Functions that control boss records
    def getBossRecord(self, stage: int, boss: int, type: int) -> bool:
        if stage != STAGE_CHALLENGE_ID:
            bossRecordAddress = getPointerAddress(self.pm, self.pm.base_address+ADDR_BASE_MENU_PTR, ADDR_BOSS_ID_TO_PTR[stage][boss][type])
        else:
            bossRecordAddress = getPointerAddress(self.pm, self.pm.base_address+ADDR_BASE_MENU_PTR, ADDR_BOSS_ID_TO_PTR[stage][boss])
        return int.from_bytes(self.pm.read_bytes(bossRecordAddress, 1)) > 0

    def setBossRecord(self, stage: int, boss: int, value: int, type: int):
        if stage != STAGE_CHALLENGE_ID:
            addrBossRecord = getPointerAddress(self.pm, self.pm.base_address+ADDR_BASE_MENU_PTR, ADDR_BOSS_ID_TO_PTR[stage][boss][type])
        else:
            addrBossRecord = getPointerAddress(self.pm, self.pm.base_address+ADDR_BASE_MENU_PTR, ADDR_BOSS_ID_TO_PTR[stage][boss])
        self.pm.write_bytes(addrBossRecord, bytes(value), 1)

    # Card Shop functions
    def getShopCardData(self, card_id: str) -> int:
        if card_id == NAZRIN_CARD_1 or card_id == NAZRIN_CARD_2: return -1
        addrFromCardShop = getPointerAddress(self.pm, self.pm.base_address+ADDR_BASE_MENU_PTR, ADDR_CARD_TO_SHOP[card_id])
        return int.from_bytes(self.pm.read_bytes(addrFromCardShop, 1))

    def setShopCardData(self, card_id: str, value: int):
        addrFromCardShop = getPointerAddress(self.pm, self.pm.base_address+ADDR_BASE_MENU_PTR, ADDR_CARD_TO_SHOP[card_id])
        self.pm.write_bytes(addrFromCardShop, bytes(value), 1)

    # Card Dex functions
    def getDexCardData(self, card_id: str) -> int:
        addrFromCardDex = getPointerAddress(self.pm, self.pm.base_address+ADDR_BASE_MENU_PTR, ADDR_CARD_TO_DEX[card_id])
        return int.from_bytes(self.pm.read_bytes(addrFromCardDex, 1))

    def setDexCardData(self, card_id: str, value: int):
        addrFromCardDex = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR, ADDR_CARD_TO_DEX[card_id])
        self.pm.write_bytes(addrFromCardDex, bytes(value), 1)

    def setNoCardData(self):
        addrFromCardDex = getPointerAddress(self.pm, self.pm.base_address + ADDR_BASE_MENU_PTR, ADDR_DEX_NO_CARD)
        self.pm.write_bytes(addrFromCardDex, bytes(0x01), 1)

    # Things to do on boot-up before anything else.
    def initAnticheatHack(self):
        bytesAtAddress = self.pm.read_bytes(self.pm.base_address+ADDR_ANTICHEAT)
        if bytesAtAddress != BYTES_ANTICHEAT_ORIGINAL: return