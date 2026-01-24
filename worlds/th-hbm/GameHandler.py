from .GameController import GameController
from .Items import ITEM_TABLE_ID_TO_STAGE_NAME, ITEM_TABLE_ID_TO_STARTING_CARD_ID, ITEM_TABLE_ID_TO_CARD_ID
from .Tools import clamp
from .variables.boss_and_stage import *
from .variables.card_const import *

# Spare Lives will not be carried over to other stages.

class GameHandler:
    """Class keeping tracking of what's unlocked and handles game interactions."""
    spare_lives = None
    game_funds = None
    menu_funds = None
    end_stage_card_chosen = {}
    permashop_card_new = []
    permashop_card = {}
    dex_card_unlocked = {}
    gameController = None
    bosses_beaten = {}
    bosses_met = {}
    stages_unlocked = {}
    previous_location_checked = []

    def __init__(self):
        self.gameController = GameController()
        self.reset()
        self.initGame()

    # Init Resources

    # Get Handler functions
    def isGameInStage(self):
        """Check if the game is currently in any stage. Returns True if yes."""
        return self.gameController.check_if_in_stage()

    def getCurrentGameFunds(self) -> int:
        return self.gameController.getGameFunds()

    def getCurrentMenuFunds(self) -> int:
        return self.gameController.getMenuFunds()

    def getCurrentBulletMoney(self) -> int:
        return self.gameController.getBulletMoney()

    def getShopCardData(self, card_string_id: str):
        """
        0x00 = Not unlocked
        0x01 - 0x79 = Unlocked but not new
        0x80 - ??? = Unlocked and new
        """
        return self.gameController.getShopCardData(card_string_id)

    def setShopCardData(self, card_string_id: str, value: int):
        self.gameController.setShopCardData(card_string_id, value)

    def getDexCardData(self, card_string_id: str) -> bool:
        """
        Gets whether a card is unlocked in the dex or not.
        0x00 means False. Anything else is True.
        """
        return self.gameController.getDexCardData(card_string_id) != 0x00

    def setDexCardData(self, card_string_id: str, value: int):
        """
        Writes data to the memory for this particular Ability Card in the dex.
        This one is for loading in the dex when reconnecting to the server.
        0x00 means False. Anything else is True (but 0x01 would be nice).
        """
        self.gameController.setDexCardData(card_string_id, value)

    # Received Item functions
    def addLife(self, value: int = 1):
        currentLives = self.gameController.getLives()
        if currentLives == 11: self.spare_lives += value
        newLives = clamp(currentLives + value, 0, 11)
        self.gameController.setLives(newLives)

    def addGameFunds(self, value: int):
        newFunds = clamp(self.getCurrentGameFunds() + value, 0, 999999)
        self.gameController.setGameFunds(newFunds)

    def addMenuFunds(self, value: int):
        newFunds = clamp(self.getCurrentMenuFunds() + value, 0, 999999)
        self.gameController.setMenuFunds(newFunds)

    def addFunds(self, value: int):
        if self.isGameInStage(): self.addGameFunds(value)
        else: self.addMenuFunds(value)

    def addBulletMoney(self, value: int):
        newFunds = clamp(self.getCurrentBulletMoney() + value, 0, 2764472319)
        self.gameController.setGameFunds(newFunds)

    # Other functions
    def reconnect(self):
        self.gameController = GameController()

    def reset(self):
        """
        Initialize everything to defaults.
        """
        self.spare_lives = None
        self.game_funds = None
        self.menu_funds = None
        self.end_stage_card_chosen = {}
        self.permashop_card_new = []
        self.permashop_card = {}
        self.dex_card_unlocked = {}
        self.gameController = None
        self.bosses_beaten = {}
        self.bosses_met = {}
        self.stages_unlocked = {}
        self.previous_location_checked = []

        for i in ABILITY_CARD_LIST:
            self.dex_card_unlocked[i] = False
            if i != NAZRIN_CARD_1 and i != NAZRIN_CARD_2:
                self.end_stage_card_chosen[i] = False
                self.permashop_card[i] = False

        self.bosses_beaten = {
            TUTORIAL_ID: {BOSS_MIKE: False},
            STAGE1_ID: {BOSS_MIKE: False, BOSS_MINORIKO: False, BOSS_ETERNITY: False, BOSS_NEMUNO: False},
            STAGE2_ID: {BOSS_CIRNO: False, BOSS_WAKASAGI: False, BOSS_SEKIBANKI: False, BOSS_URUMI: False},
            STAGE3_ID: {BOSS_EBISU: False, BOSS_KUTAKA: False, BOSS_NARUMI: False, BOSS_KOMACHI: False},
            STAGE4_ID: {BOSS_SANAE: False, BOSS_SAKUYA: False, BOSS_YOUMU: False, BOSS_REIMU: False, BOSS_NITORI: False},
            STAGE5_ID: {BOSS_TSUKASA: False, BOSS_MEGUMU: False, BOSS_CLOWNPIECE: False, BOSS_TENSHI: False},
            STAGE6_ID: {BOSS_SUIKA: False, BOSS_MAMIZOU: False, BOSS_SAKI: False, BOSS_MOMOYO: False, BOSS_TAKANE: False},
            STAGE_CHIMATA_ID: {BOSS_CHIMATA: False},
        }

        self.bosses_met = self.bosses_beaten
        self.bosses_met[STAGE_CHALLENGE_ID] = {
                BOSS_MIKE: False, BOSS_MINORIKO: False, BOSS_ETERNITY: False, BOSS_NEMUNO: False,
                BOSS_CIRNO: False, BOSS_WAKASAGI: False, BOSS_SEKIBANKI: False, BOSS_URUMI: False,
                BOSS_EBISU: False, BOSS_KUTAKA: False, BOSS_NARUMI: False, BOSS_KOMACHI: False,
                BOSS_SANAE: False, BOSS_SAKUYA: False, BOSS_YOUMU: False, BOSS_REIMU: False,
                BOSS_TSUKASA: False, BOSS_MEGUMU: False, BOSS_CLOWNPIECE: False, BOSS_TENSHI: False,
                BOSS_SUIKA: False, BOSS_MAMIZOU: False, BOSS_SAKI: False, BOSS_MOMOYO: False
            }

        for stage in STAGE_LIST:
            self.stages_unlocked[stage] = False

    def initGame(self):
        self.gameController.initAnticheatHack()
        self.gameController.setNoCardData()

    def updateStageList(self):
        """
        Updates the unlock state of stages.
        Since there are no checks to scan for these, this is primarily to sync the game with the handler.
        """
        for stage in STAGE_LIST:
            unlockStatus = self.gameController.getStageStatus(STAGE_NAME_TO_ID[stage])

            if unlockStatus == 0x00 and self.stages_unlocked[stage] == True:
                self.gameController.setStageStatus(STAGE_NAME_TO_ID[stage], 0x01)
            if unlockStatus == 0x01 and self.stages_unlocked[stage] == False:
                self.gameController.setStageStatus(STAGE_NAME_TO_ID[stage], 0x00)

    def getBossRecordHandler(self, stage_id: int, boss_id: int, type: int = 0):
        """
        Gets the stats of a boss in a specific stage from the handler.
        Type 0 is checking for encounters, and type 1 is checking for defeat.
        Challenge Market skips the type check and always returns the encounter value.
        """
        if stage_id == STAGE_CHALLENGE_ID:
            return self.bosses_met[STAGE_CHALLENGE_ID][boss_id]

        match type:
            case 0: # Encounters
                return self.bosses_met[stage_id][boss_id]
            case 1: # Defeat
                return self.bosses_beaten[stage_id][boss_id]
            case _: return False

    def setBossRecordHandler(self, stage_id: int, boss_id: int, value: bool, type: int = 0) -> None:
        """
        Sets the stats of a boss in a specific stage in the handler's data.
        Type 0 is for encounters, type 1 for defeat.
        Challenge Market exclusively has encounter stats.
        """
        if stage_id == STAGE_CHALLENGE_ID:
            self.bosses_met[STAGE_CHALLENGE_ID][boss_id] = value

        match type:
            case 0: self.bosses_met[stage_id][boss_id] = value
            case 1: self.bosses_beaten[stage_id][boss_id] = value

    def getBossRecordGame(self, stage_id: int, boss_id: int, type: int = 0) -> bool:
        """
        Gets the stats of a boss in a specific stage from the game itself.
        Type 0 is checking for encounters, and type 1 is checking for defeat.
        Challenge Market skips the type check and always returns the encounter value.
        """
        recordData = self.gameController.getBossRecord(stage_id, boss_id, type)
        if recordData != 0x00: return True
        return False

    def setBossRecordGame(self, stage_id: int, boss_id: int, value: bool, type: int = 0) -> None:
        """
        Sets the stats of a boss in a specific stage in the game memory itself.
        Type 0 is for encounters, type 1 is for defeat.
        Challenge Market exclusively has encounter stats.
        """
        self.gameController.setBossRecord(stage_id, boss_id, value, type)

    def unlockNoCard(self):
        """
        Backup function that forces the No Card option to be available,
        even if the score file disables it somehow.
        """
        self.gameController.setNoCardData()

    def unconditionalDexUnlock(self, card_string_id: str):
        """
        Function specifically for unlocking Starting Cards.
        Technically this can unlock every other dex entry, but that will break locations.
        """
        self.dex_card_unlocked[card_string_id] = True

    def unlockCardInMenuShop(self, card_string_id: str):
        """
        Function for unlocking cards in menu shop.
        The function that actually touches memory is elsewhere.
        """
        self.permashop_card[card_string_id] = True
        self.permashop_card_new.append(card_string_id)
        self.unlockCardInMenuShop_Memory(card_string_id)

    def unlockCardInMenuShop_Memory(self, card_string_id: str):
        """
        Function that actually changes game memory to show card shop unlocks.
        If the game is currently not in the menu, this function cancels itself.
        """
        if self.isGameInStage(): return
        final_value = 0x00
        if self.permashop_card[card_string_id]:
            final_value = 0x01
        if card_string_id in self.permashop_card_new:
            final_value = 0x81

        self.setShopCardData(card_string_id, final_value)

    def unlockStage(self, stage_name: str):
        self.stages_unlocked[stage_name] = True

    def handleValidItem(self, item_id: int):
        if item_id == 500 or item_id == 501:
            self.unconditionalDexUnlock(ITEM_TABLE_ID_TO_STARTING_CARD_ID[item_id])
        elif 100 <= item_id <= 108:
            self.unlockStage(ITEM_TABLE_ID_TO_STAGE_NAME[item_id])
        elif item_id >= 200:
            self.unlockCardInMenuShop(ITEM_TABLE_ID_TO_CARD_ID[item_id])