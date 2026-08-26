# Addresses to disable forced item upgrades.
ADDR_OFFSET_ITEM_UPGRADES = (
    # Nimble Fabric
    0x566e4, 0x566fe, 0x56718, 0x56732, 0x5674c, 0x56766,
    # Tengu's Toy Camera
    0x56803, 0x5681d, 0x56837, 0x56851, 0x4586b, 0x56885,
    # Gap Folding Umbrella
    0x56916, 0x56930, 0x5694a, 0x56964, 0x5697e,
    # Ghastly Send-Off Lantern
    0x56a08, 0x56a22, 0x56a3c, 0x56a56,
    # Bloodthirsty Yin-yang Orb
    0x56aed, 0x56b07, 0x56b21,
    # Four-Foot Magic Bomb
    0x56bb2, 0x56bcc, 0x56be6, 0x56c00, 0x56c1a,
    # Substitute Jizo
    0x56cab, 0x56cc5, 0x56cdf, 0x56cf9, 0x56d13,
    # Cursed Decoy Doll
    0x56da1, 0x56dbb, 0x56dd5, 0x56def,
    # Miracle Mallet Replica
    0x56e85, 0x56e9f, 0x56eb9
)

# Cheat code disabling.
# 18 bytes of 0x90 (NOP).
ADDR_STATIC_CHEAT_CODE = 0x65EED
# Change to 0x10 to play the invalid sound since the cheat code is disabled.
ADDR_STATIC_CHEAT_SOUND = 0x65EEC

# Disabling saving replays if a scene was cleared successfully.
# Original opcodes are 7e, 0a. Change to 90, 90.
ADDR_STATIC_SAVE_REPLAY = 0x4AB90
# Disabling Next Scene button.
# Original opcodes are 7c, 29. Change to 90, 90 to ensure it is always locked.
ADDR_STATIC_NEXT_SCENE = 0x4ABAF
# Disabling unlocking the next Day. Change to EB to always skip unlock.
ADDR_STATIC_UNLOCK_DAY = 0x62559

# Set playtime requirements for achievements.
# Written in little endian encoding/least significant byte first.
ADDR_STATIC_PLAYTIME_REQ = [0x338AA, 0x338CE, 0x338F2]

# Disable special Scene 1 alerts.
ADDR_STATIC_SCENE_ONE = [
    # 2 bytes
    (0x33d19, 0x33da6, 0x33e2f),
    # 6 bytes,
    (0x33d1b, 0x33d33, 0x33d39, 0x33d4a, 0x33d50, 0x33d61,
     0x33da8, 0x33dc0, 0x33dc6, 0x33dd7, 0x33ddd, 0x33dee, 0x33e42),
    # 7 bytes
    (0x33d21, 0x33dae),
    # 11 bytes
    (0x33d28, 0x33d3f, 0x33d56, 0x33db5, 0x33dcc, 0x33de3, 0x33e37)
]