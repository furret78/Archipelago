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

    def _cmd_refresh_scorefile(self):
        """Delete scorefile and substitute in a fresh, locked scorefile."""

    def _cmd_help(self):
        logger.info("Touhou 18.5")


class TouhouHBMContext(CommonContext):
    """Touhou 18.5 Game Context"""

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
        self.handler = None
        self.game = DISPLAY_NAME
        self.items_handling = 0b111  # Item from starting inventory, own world and other world
        self.command_processor = TouhouHBMClientProcessor
        self.is_in_menu = False
        self.no_card_unlocked = False
        self.traps = []

        # Set to True in order to prevent the client from looking for checks.
        # Mainly to set proper values for the Permanent Card Shop between
        # the stage part and the menu part before scanning can resume.
        self.disable_check_scanning = True

        self.receivedItemQueue = [] # All items freshly arrived. Will be filtered for wrong IDs as it's processed.
        self.menuItemQueue = [] # Items received but not yet executed because game is in a stage.
        self.gameItemQueue = [] # Items received but not yet executed because game is in the menu.
        # Note: Funds do not go in here, but they have separate functions to execute
        # depending on whether the game is in the menu or not instead.

        self.reset()

    def reset(self):
        self.previous_location_checked = []
        self.all_location_ids = []
        self.handler = None  # gameHandler
        self.no_card_unlocked = False

        self.is_in_menu = False
        self.disable_check_scanning = True
        self.inError = False

        # List of items/locations
        self.previous_location_checked = None
        self.is_connected = False

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
        for stage, boss_data in self.handler.bosses_beaten:
            for boss_name, defeat_check in boss_data:
                if not defeat_check: return False
        return True

    def checkFullClear(self) -> bool:
        return self.checkAllCards() and self.checkAllBosses()

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
        if self.client_recieved_initial_server_data():
            return

        logger.info("Waiting for connect from server...")
        while not self.client_recieved_initial_server_data() and not self.exit_event.is_set():
            await asyncio.sleep(1)

    async def connect_to_game(self):
        """
        Connect the client to the game process.
        """
        self.handler = None
        while not self.handler:
            try:
                self.handler = GameHandler()
            except Exception as e:
                await asyncio.sleep(2)

    async def reconnect_to_game(self):
        """
        Reconnect to the game without resetting everything
        """

        while not self.handler.gameController:
            try:
                self.handler.reconnect()
            except Exception as e:
                await asyncio.sleep(2)

    async def main_loop(self):
        """
        Main loop. Responsible for general management of Items and scanning locations for checks.
        """
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
                        case _: self.handler.handleValidItem(current_item_id)

            self.receivedItemQueue.pop(-1)


    async def game_loop(self):
        """
        Game loop. Responsible for handling resources during gameplay.
        """
        # Handles items that go only into stages.
        if not self.handler.isGameInStage(): return

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


    async def menu_loop(self):
        """
        Menu-only loop. Responsible for handling menu-exclusive things.
        Mainly here to fiddle with the Permanent Card Shop since it has 2 checks in 1,
        split between the gameplay section and the menu section.
        """
        if not self.no_card_unlocked:
            self.handler.unlockNoCard()
            self.no_card_unlocked = True

        if self.handler.isGameInStage(): return




    async def update_locations_checked(self):
        """
        Check if any locations has been checked since this was last called.
        If there is, send a message and update the checked location list.
        """
        new_locations = []

        # If scanning is disabled, return.
        if self.disable_check_scanning: return

        # Check bosses first.
        for stage_name in STAGE_LIST:
            for boss_name in ALL_BOSSES_LIST:
                # Encounters
                # Get the location name first, convert that to ID,
                # and then append if it is not in previously checked locations.
                if self.handler.getBossRecordGame(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name]):
                    locationName: str = get_boss_location_name_str(STAGE_NAME_TO_ID[stage_name], boss_name)
                    if location_table[locationName] not in self.previous_location_checked and location_table[locationName] in self.all_location_ids:
                        self.handler.setBossRecordHandler(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name], True)
                        new_locations.append(location_table[locationName])
                # Defeat
                if self.handler.getBossRecordGame(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name], 1):
                    locationName: str = get_boss_location_name_str(STAGE_NAME_TO_ID[stage_name], boss_name, True)
                    if location_table[locationName] not in self.previous_location_checked and location_table[locationName] in self.all_location_ids:
                        self.handler.setBossRecordHandler(STAGE_NAME_TO_ID[stage_name], BOSS_NAME_TO_ID[boss_name], True, 1)
                        new_locations.append(location_table[locationName])

        # Check Ability Cards.
        # Split into stage-exclusive and dex.
        # First step is checking if the card location exists in the big location table.


        # Stage-exclusive.
        # Not yet implemented.

        # Dex
        else:
            for card in ABILITY_CARD_LIST:
                cardLocationName: str = get_card_location_name_str(card, True)
                if location_table[cardLocationName] not in self.all_location_ids and location_table[cardLocationName] not in self.previous_location_checked: continue

                # Card dex location does exist if it made it past that.
                if self.handler.getDexCardData(card):
                    # Card dex location is True. This is a check.
                    new_locations.append(location_table[cardLocationName])

        # If there are new locations, send a message to the server
        # and add to the list of previously checked locations.
        if new_locations:
            self.previous_location_checked = self.previous_location_checked + new_locations
            await self.send_msgs([{"cmd": 'LocationChecks', "locations": new_locations}])

        # Finally, check for victory.
        if self.checkVictory() and not self.finished_game:
            self.finished_game = True
            await self.send_msgs([{"cmd": 'StatusUpdate', "status": 30}])

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

        # First connection to the game
        if ctx.handler is None and not ctx.inError:
            logger.info(f"Awaiting connection to {SHORT_NAME}...")
            asyncio.create_task(ctx.connect_to_game())

        # Trying to reconnect to the game after an error
        if ctx.inError:
            logger.info(f"Connection lost. Trying to reconnect...")
            ctx.handler.gameController = None

            asyncio.create_task(ctx.reconnect_to_game())
            await asyncio.sleep(1)
            while ctx.handler.gameController is None and not ctx.exit_event.is_set():
                await asyncio.sleep(1)

        # No connection issues. Start loops.
        if ctx.handler and ctx.handler.gameController:
            ctx.inError = False
            logger.info(f"Found {SHORT_NAME} process! Initiating game loops...")

            # Start the different loops.
            loops = []
            loops.append(asyncio.create_task(ctx.main_loop())) # TODO
            loops.append(asyncio.create_task(ctx.menu_loop()))  # TODO
            loops.append(asyncio.create_task(ctx.game_loop())) # TODO

            await ctx.update_locations_checked() # TODO
            ctx.update_stage_list()

            # Potential Death Link implementation here.

            # Infinitely loop if there is no error.
            # If there is, exit to restart the connection.
            while not ctx.exit_event.is_set() and ctx.server and not ctx.inError:
                await asyncio.sleep(1)

            # Stop all loops if possible at this phase.
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
