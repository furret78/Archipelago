"""
Variables: Meta data about the game.
"""

FILE_NAME = "th185.exe"
DISPLAY_NAME = "Black Market of Bulletphilia ~ 100th Black Market"
SHORT_NAME = "Touhou 18.5"

# Save data management
APPDATA_PATH = "\\ShanghaiAlice\\th185\\"
# Scorefile
SCOREFILE_NAME = "scoreth185.dat"
SCOREFILE_BACKUP_NAME = "scoreth185bak.dat"
# Last received item list
LAST_INDEX_FILE_NAME = "th185ap_"
JSON_EXTENSION = ".json"
JSON_SLOT_ITEMS = "items"

# Death Link
DEATH_LINK_TRIGGER_LIFE = 0
DEATH_LINK_TRIGGER_STAGE = 1

DEATH_LINK_LIFE_MSG1 = "hit a bullet."
DEATH_LINK_LIFE_MSG2 = "got sniped by a stray bullet."
DEATH_LINK_LIFE_MSG3 = "exploded."
DEATH_LINK_STAGE_MSG = "was kicked out of the Black Market."

# Energy Link
MAX_FUNDS = 999999
MAX_BULLET_MONEY = 4294967295
RATES_FUNDS_TO_JOULES = 5*(10**8)
RATES_BULLET_MONEY_TO_JOULES = 4*(10**7)
CURRENCY_FUNDS_ID = 0
CURRENCY_BULLET_MONEY_ID = 1
CURRENCY_FUNDS_ARGS_LIST: list[str] = ["f", "F", "funds", "Funds", "fund", "Fund"]
CURRENCY_BULLET_MONEY_ARGS_LIST: list[str] = ["b", "B", "bm", "Bm", "BM", "bullet", "Bullet", "bullet money", "Bullet Money", "bullet_money", "Bullet_Money"]
INTERACT_DEPOSIT_ARGS_LIST: list[str] = ["d", "D", "deposit", "Deposit"]
INTERACT_WITHDRAW_ARGS_LIST: list[str] = ["w", "W", "withdraw", "Withdraw"]
CURRENCY_NAME_FUNDS = "Funds"
CURRENCY_NAME_BULLET_MONEY = "Bullet Money"
INVALID_CURRENCY_STRING = "Invalid currency type!"