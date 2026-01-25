import os
import shutil
import traceback
from typing import Optional
import asyncio
import colorama

from CommonClient import (
	CommonContext,
	ClientCommandProcessor,
	get_base_parser,
	logger,
	server_loop,
	gui_enabled,
)
from .GameHandler import *
from .Items import GAME_ONLY_ITEM_ID, check_if_item_id_exists
from .Locations import *
# Handles the game itself. The watcher that runs loops is down below.

class TouhouHBMClientProcessor(ClientCommandProcessor):
    def __init__(self, ctx):
        super().__init__(ctx)

    def _cmd_relink_game(self):
        self.ctx.inError = True

    def _cmd_unlock_stage(self, stage_name: str):
        """
        Unlocks the stage according to its name:
        Tutorial, 1st Market, 2nd Market, 3rd Market, 4th Market, 5th Market, 6th Market, End of Market, Challenge Market.
        """
        if stage_name not in STAGE_LIST:
            logger.error("There is no stage with this number!")
            return

        self.ctx.handler.stages_unlocked[stage_name] = True
        self.ctx.update_stage_list()

        logger.info(f"{stage_name}: Set to {self.ctx.handler.stages_unlocked[stage_name]}")

    def _cmd_show_life(self):
        """
        Retrieves this slot's current number of lives.
        """
        if self.ctx.handler.gameController.check_if_in_stage():
            life_count = self.ctx.handler.gameController.getLives()
            logger.info(f"Current lives: {life_count}")
        else:
            logger.error("This slot is currently not in a stage!")

    def _cmd_unlock_no_card(self):
        """
        Command to forcibly unlock the option to equip no cards in the loadout.
        """
        self.ctx.handler.gameController.setNoCardData()

    def _cmd_show_scorefile_path(self):
        logger.info(f"Scorefile path is currently set to: {self.ctx.scorefile_path}")

    def _cmd_replace_save(self):
        """
        Replaces the scorefile at the game's Appdata folder.
        Recommended to manually back up save data before doing this.
        """
        empty_save_path = ""


class TouhouHBMContext(CommonContext):
    """Touhou 18.5 Game Context"""
    handler = None
    scorefile_path = ""

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)
        self.item_ap_id_to_name = None
        self.item_name_to_ap_id = None
        self.location_ap_id_to_name = None
        self.options = None
        self.is_connected = None
        self.inError = None
        self.location_name_to_ap_id = None
        self.all_location_ids = []
        self.previous_location_checked = []
        self.game = DISPLAY_NAME
        self.items_handling = 0b111  # Item from starting inventory, own world and other world
        self.command_processor = TouhouHBMClientProcessor

        self.is_in_menu = False
        self.no_card_unlocked = False
        self.scorefile_path = "os.getenv('APPDATA')"
        self.loadingDataSetup = True
        self.retrievedCustomData = False
        # Networking things concerning the Permanent Card Shop unlocks
        self.isWaitingReplyFromServer = False
        self.replyFromServerReceived = False

        # Additional game data.
        # Funds as shown in the menu.
        # Should only be sent to the server when:
        # - A check for the Ability Card Dex was found.
        # - Exiting a stage.
        self.menuFunds = 0
        # This is for eye-candy. List contains the string IDs of cards marked as "New!" in the game.
        self.permashop_cards_new = []
        # List of Cards that are unlocked in Shop.
        # There is no Item list that can cover this.
        # Sent to the server upon receiving an item.
        self.permashop_cards = []
        self.unlocked_stages = {}
        # Dex dictionary does not exist. Use the list of acquired checks for that.
        # Owning a card and unlocking its dex entry is one and the same,
        # but it is separate for the player.

        # Set to True when scanning the card shop addresses as locations.
        # Set to False when in the menu.
        self.enable_card_selection_checking = False
        # The opposite of the above.
        # Set to True when scanning the card shop addresses as items.
        # Set to False when in stages.
        self.enable_card_shop_scanning = True

        self.receivedItemQueue = [] # All items freshly arrived. Will be filtered for wrong IDs as it's processed.
        self.menuItemQueue = [] # Items received but not yet executed because game is in a stage.
        self.gameItemQueue = [] # Items received but not yet executed because game is in the menu.
        # Note: Funds do not go in here, but they have separate functions to execute
        # depending on whether the game is in the menu or not instead.

        self.reset()


    def reset(self):
        self.previous_location_checked = []
        self.all_location_ids = []
        self.handler = None
        self.no_card_unlocked = False

        self.is_in_menu = False
        self.disable_check_scanning = True
        self.inError = False

        self.menuFunds = 0
        self.permashop_cards_new = []
        self.permashop_cards = []
        self.unlocked_stages = {}

        # List of items/locations
        self.previous_location_checked = None
        self.is_connected = False
        self.loadingDataSetup = True

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = f"{DISPLAY_NAME} Client"
        return ui

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        """
        Manage the package received from the server
        """
        if cmd == "Connected":
            self.previous_location_checked = args['checked_locations']
            self.all_location_ids = set(args["missing_locations"] + args["checked_locations"])
            self.options = args["slot_data"]  # Yaml Options
            self.is_connected = True

            if self.handler is not None:
                self.handler.reset()

            asyncio.create_task(self.send_msgs([{"cmd": "GetDataPackage", "games": [DISPLAY_NAME]}]))

        if cmd == "ReceivedItems":
            asyncio.create_task(self.give_item(args["items"]))

        elif cmd == "Retrieved": # Custom data
            self.menuFunds = args["menuFunds"]
            self.unlocked_stages = args["unlocked_stages"]
            self.permashop_cards = args["permashop_cards"]
            self.permashop_cards_new = args["permashop_cards_new"]
            logger.info("Data from the server has been received!")

        elif cmd == "DataPackage":
            if not self.all_location_ids:
                # Connected package not received yet, wait for datapackage request after connected package
                return
            self.location_name_to_ap_id = args["data"]["games"][DISPLAY_NAME]["location_name_to_id"]
            self.location_name_to_ap_id = {
                name: loc_id for name, loc_id in
                self.location_name_to_ap_id.items() if loc_id in self.all_location_ids
            }
            self.location_ap_id_to_name = {v: k for k, v in self.location_name_to_ap_id.items()}
            self.item_name_to_ap_id = args["data"]["games"][DISPLAY_NAME]["item_name_to_id"]
            self.item_ap_id_to_name = {v: k for k, v in self.item_name_to_ap_id.items()}
            
        elif cmd == "Bounced":
            tags = args.get("tags", [])

        if cmd == "SetReply":
            # Main concern is with the Permanent Shop Card unlock list.
            # Funds update or the list for the above with the "New!" tag can be dropped,
            # but the unlock list itself is important since that interferes with checks.
            if args["key"] == "permashop_cards":
                self.replyFromServerReceived = True

    def client_received_initial_server_data(self):
        """
        This method waits until the client finishes the initial conversation with the server.
        This means:
            - All LocationInfo packages received - requested only if patch files dont exist.
            - DataPackage package received (id_to_name maps and name_to_id maps are popualted)
            - Connection package received (slot number populated)
            - RoomInfo package received (seed name populated)
        """
        return self.is_connected

    #
    # More game helper functions
    #
    def update_stage_list(self):
        self.handler.updateStageList()
        if self.disable_check_scanning: self.disable_check_scanning = False

    #
    # Victory conditions
    #
    def checkVictory(self) -> bool:
        """
        Check if the player has won the game.
        """
        completion_goal = self.options["completion_type"]

        match completion_goal:
            case 0: return self.checkFullStory()
            case 1: return self.checkMinimumStory()
            case 2: return self.checkAllCards()
            case 3: return self.checkAllBosses()
            case 4: return self.checkFullClear()

        return False

    def checkMinimumStory(self) -> bool:
        return get_boss_location_name_str(STAGE6_ID, BOSS_TAKANE_NAME, True) in self.previous_location_checked

    def checkFullStory(self) -> bool:
        if get_boss_location_name_str(STAGE4_ID, BOSS_NITORI_NAME, True) not in self.previous_location_checked: return False
        if get_boss_location_name_str(STAGE_CHIMATA_ID, BOSS_CHIMATA_NAME, True) not in self.previous_location_checked: return False
        if not self.checkMinimumStory(): return False

        return True

    def checkAllCards(self) -> bool:
        if not self.handler.dex_card_unlocked: return False
        for name, data in self.handler.dex_card_unlocked:
            if not data: return False
        return True

    def checkAllBosses(self) -> bool:
        if not self.handler.bosses_beaten: return False

        for stage_id_key in self.handler.bosses_beaten:
            for boss_data_key in self.handler.bosses_beaten[stage_id_key]:
                if not self.handler.bosses_beaten[stage_id_key][boss_data_key]: return False
        return True

    def checkFullClear(self) -> bool:
        return self.checkAllCards() and self.checkAllBosses()

    def handleValidItem(self, item_id: int):
        self.handler.handleValidItem(item_id)
        if 100 <= item_id <= 108:
            self.unlocked_stages[ITEM_TABLE_ID_TO_STAGE_NAME[item_id]] = True
            self.save_stages_to_server()
        elif item_id >= 200 and item_id != 500 and item_id != 501:
            card_string_id = ITEM_TABLE_ID_TO_CARD_ID[item_id]
            if card_string_id not in self.permashop_cards:
                self.permashop_cards.append(card_string_id)
                self.permashop_cards_new.append(card_string_id)
                self.save_new_permashop_cards_to_server(card_string_id)
                self.save_new_tag_from_card_to_server(card_string_id)

    #
    # Functions for saving custom data to server.
    #

    def save_funds_to_server(self):
        asyncio.create_task(self.send_msgs(
            [{"cmd": 'Set', "key": 'menuFunds', "default": 0, "operation": 'replace', "value": self.menuFunds}]))

    def save_stages_to_server(self):
        asyncio.create_task(self.send_msgs(
            [{"cmd": 'Set', "key": 'unlocked_stages', "operation": 'update', "value": self.unlocked_stages}]))

    def save_new_permashop_cards_to_server(self, card_string_id: str):
        asyncio.create_task(self.send_msgs(
            [{"cmd": 'Set', "key": 'permashop_cards', "want_reply": 'true', "operation": 'update', "value": card_string_id}]
        ))
        self.isWaitingReplyFromServer = True

    def save_new_tag_from_card_to_server(self, card_string_id: str):
        asyncio.create_task(self.send_msgs(
            [{"cmd": 'Set', "key": 'permashop_cards_new', "operation": 'update', "value": card_string_id}]
        ))

    def remove_new_tag_from_card_to_server(self, card_string_id: str):
        asyncio.create_task(self.send_msgs(
            [{"cmd": 'Set', "key": 'permashop_cards_new', "operation": 'remove', "value": card_string_id}]
        ))

    #
    # Async for various client needs
    #
    async def give_item(self, items):
        """
		Give an item to the player. This method will always give the oldest
		item that the player has received from AP, but not in game yet.

		:NetworkItem item: The item to give to the player
		"""

        # We wait for the link to be established to the game before giving any items
        while self.handler is None or self.handler.gameController is None:
            await asyncio.sleep(0.5)

        for item in items:
            self.receivedItemQueue.append(item.item)

        self.handler.updateStageList()

    #
    # Async loops that handle the game process.
    #

    async def wait_for_initial_connection_info(self):
        """
        This method waits until the client finishes the initial conversation with the server.
        See client_recieved_initial_server_data for wait requirements.
        """
        if self.client_received_initial_server_data():
            return

        logger.info("Waiting for connect from server...")
        while not self.client_received_initial_server_data() and not self.exit_event.is_set():
            await asyncio.sleep(1)

    async def connect_to_game(self):
        """
        Connect the client to the game process.
        """
        self.handler = None

        while self.handler is None:
            try:
                self.handler: GameHandler = GameHandler()
            except Exception as e:
                await asyncio.sleep(2)

    async def reconnect_to_game(self):
        """
        Reconnect to the game without resetting everything
        """

        while self.handler.gameController is None:
            try:
                self.handler.reconnect()
            except Exception as e:
                await asyncio.sleep(2)

    async def wait_for_setreply_from_server(self):
        """
        This function waits until it has received a SetReply from the server.
        Ideally should only be used when asking for a SetReply for the Permanent Card Shop unlocks.
        """
        if self.isWaitingReplyFromServer and self.replyFromServerReceived:
            self.isWaitingReplyFromServer = False
            self.replyFromServerReceived = False
            return True
        else: return False

    async def main_loop(self):
        """
        Main loop. Responsible for general management of Items and scanning locations for checks.
        """
        try:
            if len(self.receivedItemQueue) > 0:
                current_item_id = self.receivedItemQueue[-1]

                if check_if_item_id_exists(current_item_id):
                    if current_item_id in GAME_ONLY_ITEM_ID:
                        self.gameItemQueue.append(current_item_id)
                    else:
                        match current_item_id:
                            case 1: self.handler.addFunds(200)
                            case 2: self.handler.addFunds(1000)
                            case 10: self.handler.addFunds(5)
                            case 11: self.handler.addFunds(10)
                            case 51: self.handler.addFunds(-100)
                            case 52: self.handler.addFunds(-50)
                            case _: self.handleValidItem(current_item_id)

                self.receivedItemQueue.pop(-1)

            await self.update_locations_checked()
        except Exception as e:
            logger.error(f"Error in the MAIN loop:")
            logger.error(traceback.format_exc())
            self.inError = True


    async def game_loop(self):
        """
        Game loop. Responsible for handling resources during gameplay.
        """
        # Handles items that go only into stages.
        try:
            if not self.handler.isGameInStage(): return

            if self.enable_card_shop_scanning: self.enable_card_shop_scanning = False
            if not self.enable_card_selection_checking:
                await self.transfer_from_menu_to_stage()
                self.enable_card_selection_checking = True

            if len(self.gameItemQueue) > 0:
                current_item_id = self.gameItemQueue[-1]

                match current_item_id:
                    case 0: self.handler.addLife(1)
                    case 3: self.handler.addBulletMoney(200)
                    case 4: self.handler.addBulletMoney(500)
                    case 12: self.handler.addBulletMoney(5)
                    case 13: self.handler.addBulletMoney(10)
                    case 51: self.handler.addBulletMoney(-100)
                    case 52: self.handler.addBulletMoney(-50)

                self.gameItemQueue.pop(-1)

            return
        except Exception as e:
            logger.error(f"Error in the GAME loop:")
            logger.error(traceback.format_exc())
            self.inError = True


    async def menu_loop(self):
        """
        Menu-only loop. Responsible for handling menu-exclusive things.
        Mainly here to fiddle with the Permanent Card Shop since it has 2 checks in 1,
        split between the gameplay section and the menu section.
        """
        try:
            if not self.no_card_unlocked:
                self.handler.unlockNoCard()
                self.no_card_unlocked = True

            if self.handler.isGameInStage(): return
            if not self.enable_card_selection_checking: self.enable_card_selection_checking = False
            if self.enable_card_shop_scanning:
                await self.transfer_from_stage_to_menu()
                self.enable_card_shop_scanning = True
        except Exception as e:
            logger.error(f"Error in the MENU loop:")
            logger.error(traceback.format_exc())
            self.inError = True


    async def update_locations_checked(self):
        """
        Check if any locations has been checked since this was last called.
        If there is, send a message and update the checked location list.
        """
        new_locations = []

        if self.loadingDataSetup:
            logger.info("Attempting to load previous data...")
            return

        # Check bosses first.
        for stage_name in STAGE_LIST:
            if stage_name != CHALLENGE_NAME:
                for boss_name in ALL_BOSSES_LIST[STAGE_NAME_TO_ID[stage_name]]:
                    # Get the location name first, convert that to ID,
                    # and then append if it is not in previously checked locations.
                    # Encounters
                    if self.handler.getBossRecordGame(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name]):
                        locationName: str = get_boss_location_name_str(STAGE_NAME_TO_ID[stage_name], boss_name)
                        if location_table[locationName] not in self.previous_location_checked and location_table[
                            locationName] in self.all_location_ids:
                            self.handler.setBossRecordHandler(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name],
                                                              True)
                            new_locations.append(location_table[locationName])
                    # Defeat
                    if self.handler.getBossRecordGame(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name], 1):
                        locationName: str = get_boss_location_name_str(STAGE_NAME_TO_ID[stage_name], boss_name, True)
                        if location_table[locationName] not in self.previous_location_checked and location_table[
                            locationName] in self.all_location_ids:
                            self.handler.setBossRecordHandler(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name],
                                                              True, 1)
                            new_locations.append(location_table[locationName])
            elif self.options["challenge_checks"] is True:
                # Special Challenge Market clause
                boss_set_id_loc = 1
                for boss_set in ALL_BOSSES_LIST:
                    # If it's the Tutorial set or End of Market set, discard those.
                    if TUTORIAL_ID <= boss_set_id_loc >= STAGE_CHIMATA_ID: continue
                    for boss_name in boss_set:
                        # There are only encounters. Check those.
                        if self.handler.getBossRecordGame(STAGE_CHALLENGE_ID, BOSS_NAME_TO_ID[boss_name]):
                            locationName: str = get_boss_location_name_str(STAGE_CHALLENGE_ID, boss_name)
                            if location_table[locationName] not in self.previous_location_checked and location_table[locationName] in self.all_location_ids:
                                self.handler.setBossRecordHandler(STAGE_CHALLENGE_ID, BOSS_NAME_TO_ID[boss_name], True)
                                new_locations.append(location_table[locationName])

        # Check Ability Cards.
        # Split into stage-exclusive and dex.
        # First step is checking if the card location exists in the big location table.

        # Stage-exclusive.
        # TODO: Add functionality.
        if self.enable_card_selection_checking:
            pass

        # Dex
        for card in ABILITY_CARD_LIST:
            cardLocationName: str = get_card_location_name_str(card, True)
            if location_table[cardLocationName] in self.all_location_ids:
                continue
            if location_table[cardLocationName] not in self.previous_location_checked:
                continue

            # Card dex location does exist if it made it past that.
            if self.handler.getDexCardData(card):
                # Card dex location is True. This is a check.
                new_locations.append(location_table[cardLocationName])

        # If there are new locations, send a message to the server
        # and add to the list of previously checked locations.
        if new_locations:
            self.menuFunds = self.handler.getMenuFunds()
            self.save_funds_to_server()

            self.previous_location_checked = self.previous_location_checked + new_locations
            await self.send_msgs([{"cmd": 'LocationChecks', "locations": new_locations}])

        # Finally, check for victory.
        if self.checkVictory() and not self.finished_game:
            self.finished_game = True
            await self.send_msgs([{"cmd": 'StatusUpdate', "status": 30}])

    async def get_custom_data_from_server(self):
        logger.info("Grabbing data from the server...")
        self.retrievedCustomData = True
        await self.send_msgs([{"cmd": 'Get', "keys": ["menuFunds", "permashop_cards", "permashop_cards_new", "unlocked_stages"]}])
        return

    async def load_save_data(self):
        """
        Load all save data as needed before location checking can begin.
        Should be carried out at the very first game connection.
        """
        # Load boss defeat records for the handler, then update the records in-game.
        # Retrieve these from previously checked locations.
        logger.info("Loading boss save data...")
        self.load_save_data_bosses()
        # Load stage data for the handler, then update stage data in-game.
        logger.info("Loading stage save data...")
        for stage_name in self.unlocked_stages:
            self.handler.unlockStage(stage_name)
        # Load Ability Card shop data for the handler.
        # This is only the menu data. Data as used for checks during the stages are loaded in the stage part.
        self.load_save_data_shop()
        # Load Ability Card dex data for the handler, then update it in-game.
        self.load_save_data_dex()
        # Load menu funds. The player's grinding should be rewarded.
        logger.info("Loading funds save data...")
        self.handler.setMenuFunds(self.menuFunds)
        # Finish loading save data.
        logger.info("Finished loading all save data!")
        return

    def load_save_data_bosses(self):
        # Assume that the game is in 100% locked mode.
        previous_checks = self.previous_location_checked
        for location_id in previous_checks:
            full_location_name = location_id_to_name[location_id]
            # Iterate through all shortened stage names.
            for stage_name in STAGE_LIST:
                # If this stage name exists in the location's name, continue.
                # If not, abort mission.
                if stage_name in full_location_name:
                    if stage_name == CHALLENGE_NAME:
                        # Special Challenge Market clause
                        boss_set_id_loc = 1
                        for boss_set in ALL_BOSSES_LIST:
                            # If it's the Tutorial set or End of Market set, discard those.
                            if TUTORIAL_ID <= boss_set_id_loc >= STAGE_CHIMATA_ID: continue
                            for boss_name in boss_set:
                                self.handler.setBossRecordHandler(STAGE_CHALLENGE_ID,
                                                                  BOSS_NAME_TO_ID[boss_name], True)
                                self.handler.setBossRecordGame(STAGE_CHALLENGE_ID, BOSS_NAME_TO_ID[boss_name], True)
                    else:
                        for boss_name in ALL_BOSSES_LIST[STAGE_NAME_TO_ID[stage_name]]:
                            record_type = ENCOUNTER_ID
                            if "Defeat" in full_location_name: record_type = DEFEAT_ID
                            self.handler.setBossRecordHandler(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name], True, record_type)
                            self.handler.setBossRecordGame(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name], True)

    def load_save_data_dex(self):
        # Assume that the game is in 100% locked mode.
        previous_checks = self.previous_location_checked
        for location_id in previous_checks:
            full_location_name = location_id_to_name[location_id]
            # If none of these locations talk about the Card Dex, discard and move on.
            if CARD_DEX_NAME not in full_location_name:
                continue

            for card_string_id in ABILITY_CARD_LIST:
                if CARD_ID_TO_NAME[card_string_id] in full_location_name:
                    self.handler.unconditionalDexUnlock(card_string_id)

    def load_save_data_shop(self):
        self.handler.permashop_card_new = self.permashop_cards_new
        for card_name in self.permashop_cards:
            self.handler.permashop_card[card_name] = True


    async def transfer_from_menu_to_stage(self):
        """
        Handles transferring from the menu to the game stage.
        Mainly for the Ability Card shop addresses.
        Previously checked locations are save data for Card Selection checks.
        """
        previous_checks = self.previous_location_checked
        for location_id in previous_checks:
            full_location_name = location_id_to_name[location_id]
            # If none of these locations talk about the Market Card Reward, discard and move on.
            if ENDSTAGE_CHOOSE_NAME not in full_location_name:
                continue

            # It does not really matter what value the records are set to aside from 0x00 and non-0x00.
            for card_string_id in ABILITY_CARD_LIST:
                self.handler.setCardShopRecordGame(card_string_id, CARD_ID_TO_NAME[card_string_id] in full_location_name)

    async def transfer_from_stage_to_menu(self):
        """
        Handles transferring from the game stage to the menu.
        Mainly for the Ability Card shop addresses.
        """
        self.save_funds_to_server()

        menu_shop_card_list = ABILITY_CARD_LIST
        menu_shop_card_list.remove(NAZRIN_CARD_1)
        menu_shop_card_list.remove(NAZRIN_CARD_2)

        # For all cards that can be bought in the shop...
        for card_name in menu_shop_card_list:
            # Check if it's unlocked.
            if self.handler.getCardShopRecordHandler(card_name):
                self.handler.setCardShopRecordHandler(card_name, True)
                self.handler.permashop_card_new = self.permashop_cards_new
            self.handler.setCardShopRecordGame(card_name, card_name in self.permashop_cards)

        # If the client was saving the card info, wait for a response from the server.
        if self.isWaitingReplyFromServer: await self.wait_for_setreply_from_server()
        else: return

async def game_watcher(ctx: TouhouHBMContext):
    """
    Client loop that watches the gameplay progress.
    Start the different loops once connected that will handle the game.
	It will also attempt to reconnect if the connection to the game is lost.
    """
    await ctx.wait_for_initial_connection_info()

    while not ctx.exit_event.is_set():
        # Client was disconnected from the server
        if not ctx.server:
            # Reset the context in that case
            ctx.reset()
            await ctx.wait_for_initial_connection_info()
        else:
            if not ctx.retrievedCustomData:
                await ctx.get_custom_data_from_server()

        # Trying to make first connection to the game
        if ctx.handler is None and not ctx.inError:
            logger.info(f"Awaiting connection to {SHORT_NAME}...")
            asyncio.create_task(ctx.connect_to_game())
            while ctx.handler is None and not ctx.exit_event.is_set():
                await asyncio.sleep(1)

        # Trying to reconnect to the game after an error
        if ctx.inError or (ctx.handler.gameController is None and not ctx.exit_event.is_set()):
            logger.info(f"Connection was lost. Trying to reconnect...")
            ctx.handler.gameController = None
            ctx.loadingDataSetup = True

            asyncio.create_task(ctx.reconnect_to_game())
            await asyncio.sleep(1)

            while ctx.handler.gameController is None and not ctx.exit_event.is_set():
                await asyncio.sleep(1)

        # No connection issues. Start loops.
        if ctx.handler and ctx.handler.gameController:
            ctx.inError = False
            if ctx.loadingDataSetup:
                logger.info(f"Found {SHORT_NAME} process! Loading previous save data and initiating game loops...")
                asyncio.create_task(ctx.load_save_data())
                await asyncio.sleep(2)
                ctx.loadingDataSetup = False
                continue

            # Start the different loops.
            loops = []
            loops.append(asyncio.create_task(ctx.main_loop()))
            loops.append(asyncio.create_task(ctx.menu_loop()))
            loops.append(asyncio.create_task(ctx.game_loop()))

            await ctx.update_locations_checked()
            ctx.update_stage_list()

            # Potential Death Link implementation here.

            # Infinitely loop if there is no error.
            await asyncio.sleep(1)
            # If there is, exit to restart the connection.
            # Stop all loops if possible at this phase.
            if ctx.inError or ctx.exit_event.is_set() or not ctx.server:
                for loop in loops:
                    try: loop.cancel()
                    except: pass

def launch():
    """
    Launch a client instance (wrapper / args parser)
    """

    async def main(args):
        """
        Launch a client instance (threaded)
        """
        ctx = TouhouHBMContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx))
        if gui_enabled: ctx.run_gui()
        ctx.run_cli()
        watcher = asyncio.create_task(
            game_watcher(ctx),
            name="GameProgressionWatcher"
        )
        await ctx.exit_event.wait()
        await watcher
        await ctx.shutdown()

    parser = get_base_parser(description=SHORT_NAME + " Client")
    args, _ = parser.parse_known_args()

    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()
