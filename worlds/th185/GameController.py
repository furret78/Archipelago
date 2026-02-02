import pymem
import pymem.exception

from .Tools import *
from .variables.card_const import *
from .variables.meta_data import *
from .variables.address_gameplay import *
from .variables.boss_and_stage import *

class GameController:
    """Class accessing the game's memory."""

    # I honestly have no idea why it's written this way.
    # I consider the implementation of memory editing the game below magic.
    # The helper function that gets addresses from pointers I also consider to be magic.
    # But it works so I don't really care.
    def __init__(self):
        self.pm = pymem.Pymem(process_name=FILE_NAME)

        # Gameplay only.
        # Read straight from them as is to get the value.
        self.addrCurrentStage = self.pm.base_address+ADDR_CURRENT_STAGE_PTR # Check if pointer itself is valid.
        self.addrGameFunds = self.pm.base_address+ADDR_GAME_FUNDS_PTR
        self.addrBulletMoney = self.pm.base_address+ADDR_BULLET_MONEY_PTR
        self.addrBulletMoney2 = self.pm.base_address+ADDR_BULLET_MONEY_2_PTR
        self.addrLives = self.pm.base_address+ADDR_LIVES_PTR

        # Menu and record-keeping.
        # These use pointers.
        self.has_allocated_memory_to_anticheat = False

    # Helper function
    def getAddressFromPointerWithBase(self, offset):
        """
        Helper function. Essentially just tacks the static base address for the menu onto getAddressFromPointer.
        """
        static_base_pointer = self.pm.base_address + ADDR_BASE_MENU_PTR

        return getPointerAddress(self.pm, static_base_pointer, [offset])

    def check_if_in_stage(self) -> bool:
        """
        Returns True if in a stage.
        """
        return int.from_bytes(self.pm.read_bytes(self.pm.base_address + ADDR_CURRENT_STAGE_PTR, 2)) != 0

    def check_if_in_game(self):
        """
        Returns True if the game is open and not the window resolution selection dialogue box.
        """
        try:
            card_slot = int.from_bytes(self.pm.read_bytes(self.getAddressFromPointerWithBase(ADDR_EQUIP_SLOT_COUNT), 4))
        except Exception as e:
            return False
        # If this does not raise an exception, the game is running.
        return True

    # Gameplay.
    # Lives (in-game) functions
    def getLives(self) -> int:
        return int.from_bytes(self.pm.read_bytes(self.addrLives, 4))

    def setLives(self, value):
        self.pm.write_int(self.addrLives, value)

    # Funds (in-game) functions
    def getGameFunds(self) -> int:
        return self.pm.read_int(self.addrGameFunds)

    def setGameFunds(self, value):
        self.pm.write_int(self.addrGameFunds, value)

    # Bullet Money (in-game) functions
    def getBulletMoney(self) -> int:
        return self.pm.read_int(self.addrBulletMoney)

    def setBulletMoney(self, value):
        self.pm.write_int(self.addrBulletMoney, value)

    # Recordkeeping starts here.
    # Funds (menu) functions
    def getMenuFunds(self) -> int:
        addrMenuFunds = self.getAddressFromPointerWithBase(ADDR_MENU_FUNDS_PTR)
        return self.pm.read_int(addrMenuFunds)

    def setMenuFunds(self, value):
        addrMenuFunds = self.getAddressFromPointerWithBase(ADDR_MENU_FUNDS_PTR)
        self.pm.write_int(addrMenuFunds, value)

    # Stage lock functions
    def getStageStatus(self, stage_id: int) -> bool:
        stageLockAddress = self.getAddressFromPointerWithBase(ADDR_STAGE_ID_TO_PTR[stage_id])
        return bool.from_bytes(self.pm.read_bytes(stageLockAddress, 1))

    def setStageStatus(self, stage_id: int, value: int):
        stageLockAddress = self.getAddressFromPointerWithBase(ADDR_STAGE_ID_TO_PTR[stage_id])
        self.pm.write_bytes(stageLockAddress, bytes([value]), 1)

    # Functions that control boss records
    def getBossRecord(self, stage: int, boss: int, category: int) -> bool:
        boss_address_list_normal = ADDR_BOSS_ID_TO_PTR[stage][boss]

        if stage != STAGE_CHALLENGE_ID:
            bossRecordAddress = self.getAddressFromPointerWithBase(boss_address_list_normal[category])
        else:
            bossRecordAddress = self.getAddressFromPointerWithBase(ADDR_BOSS_ID_TO_PTR[stage][boss])
        return self.pm.read_bytes(bossRecordAddress, 1) != bytes([0x00])

    def setBossRecord(self, stage: int, boss: int, value: int, category: int):
        # Practically unused, but might be handy at some point.
        if stage != STAGE_CHALLENGE_ID:
            bossRecordAddress = self.getAddressFromPointerWithBase(ADDR_BOSS_ID_TO_PTR[stage][boss][category])
        else:
            bossRecordAddress = self.getAddressFromPointerWithBase(ADDR_BOSS_ID_TO_PTR[stage][boss])
        self.pm.write_bytes(bossRecordAddress, bytes([value]), 1)

    # Card Shop functions
    def getShopCardData(self, card_id: str) -> bytes:
        if card_id == NAZRIN_CARD_1 or card_id == NAZRIN_CARD_2: return bytes([0x00])
        addrFromCardShop = self.getAddressFromPointerWithBase(ADDR_CARD_TO_SHOP[card_id])
        return self.pm.read_bytes(addrFromCardShop, 1)

    def setShopCardData(self, card_id: str, value: bytes):
        addrFromCardShop = self.getAddressFromPointerWithBase(ADDR_CARD_TO_SHOP[card_id])
        self.pm.write_bytes(addrFromCardShop, value, 1)

    # Card Dex functions
    def getDexCardData(self, card_id: str) -> bool:
        addrFromCardDex = self.getAddressFromPointerWithBase(ADDR_CARD_TO_DEX[card_id])
        return self.pm.read_bytes(addrFromCardDex, 1) != bytes([0x00])

    def setDexCardData(self, card_id: str, value: bytes):
        addrFromCardDex = self.getAddressFromPointerWithBase(ADDR_CARD_TO_DEX[card_id])
        self.pm.write_bytes(addrFromCardDex, value, 1)

    # Things to do on boot-up before anything else.
    def initAnticheatHack(self):
        self.pm.write_bytes(self.pm.base_address+ADDR_ANTICHEAT_HACK, bytes([0x90, 0x90]), 2)

    def setNoCardData(self):
        addrFromCardDex = self.getAddressFromPointerWithBase(ADDR_DEX_NO_CARD)
        self.pm.write_bytes(addrFromCardDex, bytes([0x01]), 1)