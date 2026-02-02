import os
import pkgutil
import traceback
from typing import Optional
import asyncio
import colorama
import pymem.exception

from CommonClient import (
	CommonContext,
	ClientCommandProcessor,
	get_base_parser,
	logger,
	server_loop,
	gui_enabled,
)
from NetUtils import NetworkItem
from .GameHandler import *
from .Items import GAME_ONLY_ITEM_ID, check_if_item_id_exists
from .Locations import *

# Handles the game itself. The watcher that runs loops is down below.

def copy_and_replace(directory: str):
    ap_scorefile_data = pkgutil.get_data("worlds.th185", "scorefile/scoreth185.dat")
    if ap_scorefile_data is None:
        logger.error("The Client could not find its own pre-existing save data!")
        return

    # The actual scorefile used by the game.
    full_file_path = os.path.join(directory, os.path.basename(SCOREFILE_NAME))
    if os.path.exists(full_file_path):
        os.remove(full_file_path)
    with open(full_file_path, "wb") as binary_file:
        binary_file.write(ap_scorefile_data)

    # Remove the backup scorefile in there since it interferes with Archipelago functionality.
    backup_file_path = os.path.join(directory, os.path.basename(SCOREFILE_BACKUP_NAME))
    if os.path.exists(backup_file_path):
        os.remove(backup_file_path)

    logger.info(f"Successfully replaced save data at: {full_file_path}")


class TouhouHBMClientProcessor(ClientCommandProcessor):
    def __init__(self, ctx):
        super().__init__(ctx)

    def _cmd_relink_game(self):
        self.ctx.inError = True

    def _cmd_show_life(self):
        """
        Retrieves this slot's current number of lives.
        """
        if not self.ctx.handler or not self.ctx.handler.gameController:
            logger.error("The game is not running!")
            return

        if self.ctx.handler.gameController.check_if_in_stage():
            life_count = self.ctx.handler.gameController.getLives()
            logger.info(f"Current lives: {life_count}")
        else:
            logger.error("This slot is currently not in a stage!")

    def _cmd_show_funds(self):
        """
        Retrieves the number of Funds in the menu.
        """
        if not self.ctx.handler or not self.ctx.handler.gameController:
            logger.error("The game is not running!")
            return

        funds_count = self.ctx.handler.gameController.getMenuFunds()
        logger.info(f"Current Funds: {funds_count}")

    def _cmd_unlock_no_card(self):
        """
        Command to forcibly unlock the option to equip no cards in the loadout.
        """
        if not self.ctx.handler or not self.ctx.handler.gameController:
            logger.error("The game is not running!")
            return

        self.ctx.handler.gameController.setNoCardData()

    def _cmd_show_save_directory(self):
        """
        Show the current save data directory the client is using.
        """
        logger.info(f"Save data directory is currently set to: {self.ctx.scorefile_path}")

    def _cmd_set_save_directory(self, save_path: str = None):
        """
        Sets a new path to the save data directory.
        """
        if save_path is not None:
            self.ctx.scorefile_path = save_path
            logger.info(f"Save data directory was changed to: {self.ctx.scorefile_path}")
        else:
            default_appdata_path = os.getenv("APPDATA")
            if default_appdata_path is None:
                self.ctx.scorefile_path = None
            else:
                self.ctx.scorefile_path = default_appdata_path + APPDATA_PATH

            logger.info(f"Save data directory was reset to default.")

    def _cmd_replace_save(self):
        """
        Replaces the game's scoreth185.dat file and deletes scoreth185bak.dat file.
        Recommended to manually back up save data before doing this.
        The game's save data is often located at %appdata%/ShanghaiAlice/th185.
        """
        copy_and_replace(self.ctx.scorefile_path)


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

        self.no_card_unlocked: bool = False
        self.loadingDataSetup: bool = True
        self.retrievedCustomData: bool = False
        # Networking things concerning the Permanent Card Shop unlocks
        self.isWaitingReplyFromServer: bool = False
        self.replyFromServerReceived: bool = False

        # Scorefile path.
        default_appdata_path = os.getenv("APPDATA")
        if default_appdata_path is None:
            self.ctx.scorefile_path = None
        else:
            self.scorefile_path = default_appdata_path + APPDATA_PATH

        # Additional game data.
        # Funds as shown in the menu.
        # Should only be sent to the server when:
        # - A check for the Ability Card Dex was found.
        # - Exiting a stage.
        self.menuFunds: int = 0
        # Number of Ability Cards the player can equip at the start of a stage.
        self.loadout_slots: int = 0 # Max 7 in-game.
        # Equipment cost.
        self.equip_cost: int = 0 # Max 350% in-game.
        # This is for eye-candy. List contains the string IDs of cards marked as "New!" in the game.
        self.permashop_cards_new: list = []
        # List of Cards that are unlocked in Shop.
        # When connected to the server, the entire ReceivedItem package will be scanned
        # for any cards that are in there. Same with the list of unlocked stages.
        self.permashop_cards: list = []
        self.unlocked_stages: list = []
        # Dex dictionary does not exist. Use the list of acquired checks for that.
        # Owning a card and unlocking its dex entry is one and the same,
        # but it is separate for the player.
        self.custom_data_keys_list: list = [str(self.slot)+"Funds185",
                                            str(self.slot)+"LastItem185",
                                            str(self.slot)+"Slots185",
                                            str(self.slot)+"EquipCost185"]

        # Set to True when scanning the card shop addresses as locations.
        # Set to False when in the menu.
        self.enable_card_selection_checking: bool = False
        # The opposite of the above.
        # Set to True when scanning the card shop addresses as items.
        # Set to False when in stages.
        self.enable_card_shop_scanning: bool = True

        self.receivedItemQueue: list = [] # All items freshly arrived. Will be filtered for wrong IDs as it's processed.
        self.menuItemQueue: list = [] # Items received but not yet executed because game is in a stage.
        self.gameItemQueue: list = [] # Items received but not yet executed because game is in the menu.
        # Note: Funds do not go in here, but they have separate functions to execute
        # depending on whether the game is in the menu or not instead.

        # Last received item index from the server.
        self.lastReceivedItem: int = 0

        # Whether the game is running or not.
        # Checks for whether it is the game itself or just the window resolution dialogue box.
        self.isGameRunning: bool = False

        self.reset()


    def reset(self):
        self.previous_location_checked = []
        self.all_location_ids = []
        self.handler = None
        self.no_card_unlocked = False

        self.inError = False

        self.menuFunds = 0
        self.permashop_cards_new = []
        self.permashop_cards = []
        self.unlocked_stages = []

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
            asyncio.create_task(self.handle_received_items(args["index"], args["items"]))

        elif cmd == "Retrieved": # Custom data
            # Menu Funds
            if self.custom_data_keys_list[0] in args["keys"]:
                if args["keys"][self.custom_data_keys_list[0]] is not None:
                    self.menuFunds = args["keys"][self.custom_data_keys_list[0]]

            # Last Received Item Index integer
            if self.custom_data_keys_list[1] in args["keys"]:
                if args["keys"][self.custom_data_keys_list[1]] is not None:
                    self.lastReceivedItem = args["keys"][self.custom_data_keys_list[1]]

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
            if args["value"] is not None:
                #if args["key"] == self.custom_data_keys_list[0]:
                #    self.menuFunds = args["value"]
                if args["key"] == self.custom_data_keys_list[1]:
                    self.lastReceivedItem = args["value"]
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

    async def handleValidItem(self, item_id: int):
        self.handler.handleValidItem(item_id)

    #
    # Item Reception and helper functions.
    #
    async def handle_received_items(self, network_index, network_items_list):
        """
        Handle items received from the server. Since some save data is also
        embedded into the items list, the index will be ignored for them specifically.
        The rest of the items will be put into a queue.

        The first argument is the index, second is the NetworkItem list.
        """
        # We wait for the link to be established to the game before giving any items
        while self.handler is None or self.handler.gameController is None:
            await asyncio.sleep(0.5)

        logger.info("Processing a ReceivedItems package from the server!")
        logger.info(f"Last item index is: {network_index}")

        self.handle_items(network_index, network_items_list)


    def handle_items(self, index: int, network_item_list: list[NetworkItem]):
        ability_card_unlock_list = []
        stage_unlock_list = []
        filler_list = []

        for network_item in network_item_list:
            if network_item.item in ITEM_TABLE_ID_TO_STAGE_NAME:
                stage_unlock_list.append(ITEM_TABLE_ID_TO_STAGE_NAME[network_item.item])
            elif network_item.item in ITEM_TABLE_ID_TO_CARD_ID:
                ability_card_unlock_list.append(ITEM_TABLE_ID_TO_CARD_ID[network_item.item])
            else:
                filler_list.append(network_item.item)

        self.handle_ability_cards(ability_card_unlock_list)
        self.handle_stages(stage_unlock_list)
        self.handle_filler_items(filler_list)

    def handle_ability_cards(self, filtered_list):
        if len(filtered_list) <= 0: return
        logger.info("Handling Ability Cards...")
        for card_name in filtered_list:
            if card_name not in self.permashop_cards:
                self.permashop_cards.append(card_name)
                # self.permashop_cards_new.append(card_name)
                self.try_unlock_card_in_shop(card_name)

    def handle_stages(self, filtered_list):
        logger.info("Currently trying to handle stages...")
        if len(filtered_list) <= 0: return
        logger.info("Handling Stages...")
        for stage_short_name in filtered_list:
            if stage_short_name not in self.unlocked_stages:
                self.unlocked_stages.append(stage_short_name)
                self.handler.stages_unlocked[stage_short_name] = True

        self.handler.updateStageList()

    def handle_filler_items(self, filtered_list):
        if len(filtered_list) <= 0: return
        logger.info("Handling Filler Items...")
        # Handle filler stuff here.

    def try_unlock_card_in_shop(self, card_name: str):
        if self.handler.isGameInStage(): return
        if self.enable_card_selection_checking: return
        if not self.enable_card_shop_scanning: return

        self.handler.permashop_card_new = self.permashop_cards_new
        self.handler.setCardShopRecordHandler(card_name, True)
        self.handler.setCardShopRecordGame(card_name, True)

    #
    # Functions for saving custom data to server.
    #

    # TODO: Fix networking with custom data sent to the server.
    async def save_funds_to_server(self):
        self.menuFunds = self.handler.getMenuFunds()
        await self.send_msgs(
            [{"cmd": 'Set', "key": self.custom_data_keys_list[0], "default": 0, "operations": [{"operation": 'replace', "value": self.menuFunds}]}])

    async def save_last_received_item_index_to_server(self):
        await self.send_msgs(
            [{"cmd": 'Set', "key": self.custom_data_keys_list[1], "default": 0, "operations": [{"operation": 'replace', "value": self.lastReceivedItem}]}]
        )

    #
    # Async loops that handle the game process.
    #

    async def wait_for_initial_connection_info(self):
        """
        This method waits until the client finishes the initial conversation with the server.
        See client_recieved_initial_server_data for wait requirements.
        """
        self.retrievedCustomData = False

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
        Main loop. Responsible for scanning locations for checks.
        """
        try:
            await self.update_locations_checked()
        except Exception as e:
            self.inError = True
            if e is pymem.exception.ProcessError:
                logger.error(f"The client can't detect the game process!")
            else:
                logger.error(f"Error in the MAIN loop.")
                logger.error(traceback.format_exc())


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
                current_item_id = self.gameItemQueue[0]

                match current_item_id:
                    case 0: self.handler.addLife(1)
                    case 3: self.handler.addBulletMoney(200)
                    case 4: self.handler.addBulletMoney(500)
                    case 12: self.handler.addBulletMoney(5)
                    case 13: self.handler.addBulletMoney(10)
                    case 51: self.handler.addBulletMoney(-100)
                    case 52: self.handler.addBulletMoney(-50)

                self.gameItemQueue.pop(0)

            return
        except Exception as e:
            self.inError = True
            if e is pymem.exception.ProcessError:
                logger.error(f"The client can't detect the game process!")
            else:
                logger.error(f"Error in the GAME loop.")
                logger.error(traceback.format_exc())


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
            if self.enable_card_selection_checking: self.enable_card_selection_checking = False
            if not self.enable_card_shop_scanning:
                await self.transfer_from_stage_to_menu()
                self.enable_card_shop_scanning = True
        except Exception as e:
            self.inError = True
            if e is pymem.exception.ProcessError:
                logger.error(f"The client can't detect the game process!")
            else:
                logger.error(f"Error in the MENU loop.")
                logger.error(traceback.format_exc())


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
            else:
                # Special Challenge Market clause
                boss_set_id_loc = 1
                for boss_set in ALL_BOSSES_LIST:
                    # If it's the Tutorial set or End of Market set, discard those.
                    if TUTORIAL_ID <= boss_set_id_loc >= STAGE_CHIMATA_ID: continue
                    for boss_name in boss_set:
                        # Make sure to exclude the story bosses.
                        if boss_name in STORY_BOSSES_LIST: continue
                        # There are only encounters. Check those.
                        if self.handler.getBossRecordGame(STAGE_CHALLENGE_ID, BOSS_NAME_TO_ID[boss_name]):
                            locationName: str = get_boss_location_name_str(STAGE_CHALLENGE_ID, boss_name)
                            if locationName not in location_table: continue
                            if location_table[locationName] not in self.previous_location_checked and location_table[locationName] in self.all_location_ids:
                                self.handler.setBossRecordHandler(STAGE_CHALLENGE_ID, BOSS_NAME_TO_ID[boss_name], True)
                                new_locations.append(location_table[locationName])

        # Check Ability Cards.
        # Split into stage-exclusive and dex.
        # First step is checking if the card location exists in the big location table.

        # Stage-exclusive.
        player_has_found_card_in_stage = False
        if self.handler.isGameInStage() and self.enable_card_selection_checking:
            shop_card_list = ABILITY_CARD_LIST
            for invalid_card in ABILITY_CARD_CANNOT_EQUIP:
                if invalid_card in shop_card_list: shop_card_list.remove(invalid_card)

            for card in shop_card_list:
                cardLocationName: str = get_card_location_name_str(card, False)
                if location_table[cardLocationName] not in self.all_location_ids:
                    continue
                if location_table[cardLocationName] in self.previous_location_checked:
                    continue

                # Card shop unlock location does exist if it made it past that.
                if self.handler.getCardShopRecordGame(card) != 0:
                    # Card shop location is True. This is a check.
                    new_locations.append(location_table[cardLocationName])
                    player_has_found_card_in_stage = True


        # Dex
        player_has_purchased_card_bool = False
        for card in ABILITY_CARD_LIST:
            cardLocationName: str = get_card_location_name_str(card, True)
            if cardLocationName not in location_table: continue
            if location_table[cardLocationName] not in self.all_location_ids:
                continue
            if location_table[cardLocationName] in self.previous_location_checked:
                continue

            # Card dex location does exist if it made it past that.
            if self.handler.getDexCardData(card):
                # Card dex location is True. This is a check.
                new_locations.append(location_table[cardLocationName])
                player_has_purchased_card_bool = True

        # If there are new locations, send a message to the server
        # and add to the list of previously checked locations.
        if new_locations:
            # Since both of Nazrin's cards do not get unlocked at all past the Tutorial,
            # This is added so that it gets unlocked in the dex.
            # The Bullet Money variant is set to be unlocked at the start of a stage.
            # The Funds variant is set to be unlocked at the Market Card Reward selection.
            if player_has_found_card_in_stage:
                self.handler.setDexCardData(NAZRIN_CARD_1, True)
                cardLocationName: str = get_card_location_name_str(NAZRIN_CARD_1, True)
                if (location_table[cardLocationName] in self.all_location_ids
                        and location_table[cardLocationName] not in self.previous_location_checked):
                    new_locations.append(location_table[cardLocationName])

            if player_has_purchased_card_bool: await self.save_funds_to_server()

            self.previous_location_checked = self.previous_location_checked + new_locations
            await self.send_msgs([{"cmd": 'LocationChecks', "locations": new_locations}])

        # Finally, check for victory.
        if self.checkVictory() and not self.finished_game:
            self.finished_game = True
            await self.send_msgs([{"cmd": 'StatusUpdate', "status": 30}])

    async def get_custom_data_from_server(self):
        self.retrievedCustomData = True
        await self.send_msgs([{"cmd": 'Get', "keys": self.custom_data_keys_list}])
        await self.send_msgs([{"cmd": 'SetNotify', "keys": self.custom_data_keys_list}])

    async def load_save_data(self):
        """
        Load all save data as needed before location checking can begin.
        Should be carried out at the very first game connection.
        """
        self.load_save_data_bosses()
        self.load_save_data_stages()
        self.load_save_data_shop()
        self.load_save_data_dex()
        self.handler.setMenuFunds(self.menuFunds)
        return

    def load_save_data_bosses(self):
        # Assume that the game is in 100% locked mode.
        for location_id in self.previous_location_checked:
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
                                if boss_name not in full_location_name: continue
                                self.handler.setBossRecordHandler(STAGE_CHALLENGE_ID, BOSS_NAME_TO_ID[boss_name], True)
                                self.handler.setBossRecordGame(STAGE_CHALLENGE_ID, BOSS_NAME_TO_ID[boss_name], True)
                    else:
                        for boss_name in ALL_BOSSES_LIST[STAGE_NAME_TO_ID[stage_name]]:
                            if boss_name not in full_location_name: continue
                            record_type = ENCOUNTER_ID
                            if DEFEAT_TYPE_NAME in full_location_name: record_type = DEFEAT_ID
                            self.handler.setBossRecordHandler(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name], True, record_type)
                            self.handler.setBossRecordGame(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name], True)

    def load_save_data_stages(self):
        for stage_name in self.unlocked_stages:
            self.handler.stages_unlocked[stage_name] = True

        self.handler.updateStageList()

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
            self.try_unlock_card_in_shop(card_name)


    async def transfer_from_menu_to_stage(self):
        """
        Handles transferring from the menu to the game stage.
        Mainly for the Ability Card shop addresses.
        Previously checked locations are save data for Card Selection checks.
        """
        logger.info("Heading into a stage!")
        await self.save_funds_to_server()

        self.handler.setDexCardData(NAZRIN_CARD_2, True)

        menu_shop_card_list = ABILITY_CARD_LIST
        for invalid_card in ABILITY_CARD_CANNOT_EQUIP:
            if invalid_card in menu_shop_card_list: menu_shop_card_list.remove(invalid_card)

        # Clear out the records of the entire Card Shop in the memory.
        for card_string_id in menu_shop_card_list:
            self.handler.setCardShopRecordGame(card_string_id, False)

        # Go over the list of acquired checks and set as appropriate.
        for location_id in self.previous_location_checked:
            full_location_name = location_id_to_name[location_id]
            # If none of these locations talk about the Market Card Reward, discard and move on.
            if ENDSTAGE_CHOOSE_NAME not in full_location_name:
                continue

            # It does not really matter what value the records are set to aside from 0x00 and non-0x00.
            for card_string_id in menu_shop_card_list:
                if CARD_ID_TO_NAME[card_string_id] in full_location_name:
                    self.handler.setCardShopRecordGame(card_string_id, True)

    async def transfer_from_stage_to_menu(self):
        """
        Handles transferring from the game stage to the menu.
        Mainly for the Ability Card shop addresses.
        """
        logger.info("Heading back into the menu...")
        await self.save_funds_to_server()

        menu_shop_card_list = ABILITY_CARD_LIST
        for invalid_card in ABILITY_CARD_CANNOT_EQUIP:
            if invalid_card in menu_shop_card_list: menu_shop_card_list.remove(invalid_card)

        # Clear out the records of the entire Card Shop in the memory.
        for card_string_id in menu_shop_card_list:
            self.handler.setCardShopRecordGame(card_string_id, False)

        # For all cards that can be bought in the shop...
        for card_name in menu_shop_card_list:
            # Check if it's unlocked.
            if card_name in self.permashop_cards:
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
                try:
                    await ctx.get_custom_data_from_server()
                except Exception as e:
                    logger.error("Failed to retrieve save data.")
                    logger.error(traceback.format_exc())
                    ctx.inError = True

        # Trying to make first connection to the game
        if ctx.handler is None and not ctx.inError:
            logger.info(f"Awaiting connection to {SHORT_NAME}...")
            asyncio.create_task(ctx.connect_to_game())
            while ctx.handler is None and not ctx.exit_event.is_set():
                await asyncio.sleep(1)

        # Trying to reconnect to the game after an error
        if ctx.inError or (ctx.handler.gameController is None and not ctx.exit_event.is_set()) and ctx.retrievedCustomData:
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

            if not ctx.isGameRunning:
                ctx.isGameRunning = ctx.handler.gameController.check_if_in_game()
                await asyncio.sleep(1)
                continue

            if ctx.loadingDataSetup:
                logger.info(f"Found {SHORT_NAME} process! Loading previous save data and initiating game loops...")
                asyncio.create_task(ctx.load_save_data())
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
