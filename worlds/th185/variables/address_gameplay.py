"""
Variables: Memory addresses used during stage gameplay.
"""
# Combine the below with the base game address.

# All of the below uses 4-byte decimals.
# These are offsets to a static base address.
# Read from them as is to get their values.
ADDR_CURRENT_STAGE_PTR = 0x000D7B0C # If pointer is valid, game is in stage. If not, game is not.
ADDR_GAME_FUNDS_PTR = 0x000D106C
ADDR_BULLET_MONEY_PTR = 0x000D1070
ADDR_BULLET_MONEY_2_PTR = 0x000D1074
ADDR_LIVES_PTR = 0x000D10BC
ADDR_ANTICHEAT = 0x000744A6
BYTES_ANTICHEAT_ORIGINAL = bytes([0x75, 0x35, 0x8B, 0x35, 0x58, 0xF2, 0x4A, 0x00])