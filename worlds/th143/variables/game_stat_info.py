CONST_DAY_SCENE_COUNT = [6, 6, 7, 7, 8, 8, 8, 7, 8, 10]
# A List containing Lists on item stats
# Each item is marked according to their order in CONST_ITEM_NAMES
# All items start at 0 for everything.
# Presumably this will only get used for items that had at least 1 Progressive item.
# CONST_ITEM_UPGRADE_STAT[item_id][level_count - 1]["specific_stat"]
CONST_ITEM_UPGRADE_STAT = [
	# Nimble Fabric (6 max vanilla)
	{
		"level": [1, 2, 3, 4, 5, 6],
		"count": [5, 5, 6, 6, 7, 7],
		"stat": [60, 84, 84, 106, 106, 120]
	},
	# Tengu's Toy Camera (6 max vanilla)
	{
		"level": [1, 2, 3, 4, 5, 6],
		"count": [4, 5, 5, 6, 6, 7],
		"stat": [100, 100, 120, 120, 140, 140]
	},
	# Gap Folding Umbrella (5 max vanilla)
	{
		"level": [1, 2, 3, 4, 5],
		"count": [7, 7, 7, 7, 7],
		"stat": [30, 60, 90, 120, 150]
	},
	# Ghastly Send-Off Lantern (4 max vanilla)
	{
		"level": [1, 2, 3, 4],
		"count": [1, 1, 1, 1],
		"stat": [480, 540, 600, 660]
	},
	# Bloodthirsty Yin-yang Orb (3 max vanilla)
	{
		"level": [1, 2, 3],
		"count": [5, 6, 7],
		"stat": [60, 60, 60]
	},
	# Four-Foot Magic Bomb (5 max vanilla)
	{
		"level": [1, 2, 3, 4, 5],
		"count": [3, 3, 3, 3, 4],
		"stat": [128, 154, 179, 205, 205]
	},
	# Substitute Jizo (5 max vanilla)
	{
		"level": [1, 2, 3, 4, 5],
		"count": [3, 3, 3, 3, 4],
		"stat": [60, 90, 120, 180, 180]
	},
	# Cursed Decoy Doll (4 max vanilla)
	{
		"level": [1, 2, 3, 4],
		"count": [2, 2, 2, 3],
		"stat": [720, 900, 1080, 1080]
	},
	# Miracle Mallet Replica (3 max vanilla)
	{
		"level": [1, 2, 3],
		"count": [3, 4, 5],
		"stat": [400, 400, 400]
	}
]

CONST_PLAYTIME_REQUIRE = [
	# Vanilla (1 hour, 5 hours, 10 hours)
	[bytes([0x40, 0x73, 0x05]), bytes([0x40, 0x77, 0x1b]), bytes([0x80, 0xee, 0x36])],
	# Half
	[bytes([0x20, 0xbf, 0x02]), bytes([0xa0, 0xbb, 0x0d]), bytes([0x40, 0x77, 0x1b])],
	# Fifth
	[bytes([0x40, 0x19, 0x01]), bytes([0x40, 0x73, 0x05]), bytes([0x80, 0xfc, 0x0a])]
]