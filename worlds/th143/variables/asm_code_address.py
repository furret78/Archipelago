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
ADDR_STATIC_CHEAT_CODE = 0x00065EED
# Change to 0x10 to play the invalid sound since the cheat code is disabled.
ADDR_STATIC_CHEAT_SOUND = 0x00065EEC