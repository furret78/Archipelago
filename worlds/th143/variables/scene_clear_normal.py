#
# First number is Day, second is Scene (tuple), both indexed from 1.
#
# Item clears without Sub-items.
NORMAL_CLEAR_NO_ITEM_SET = (
	(1, (1, 2, 3, 6)), (2, (2)), (3, (1, 2, 5)),
	(4, (4, 5, 7)), (5, (1, 6, 7)), (6, (1, 3)),
	(7, (5)), (8, (1, 3))
)
NORMAL_CLEAR_FABRIC_SET = (
	(1, (4, 5)), (2, (1, 3, 4)), (3, (3, 7)),
	(4, (2)), (5, (3)), (6, (2, 5, 7, 8)),
	(7, (3, 4)), (8, (4)), (9, (1, 5))
)
NORMAL_CLEAR_CAMERA_SET = (
	(1, (4, 5)), (2, (1, 3, 5, 6)), (3, (3, 6)),
	(4, (1, 2, 6)), (5, (3, 4, 8)), (7, (1, 2)),
	(8, (2, 4)), (9, (5, 6, 7))
)
NORMAL_CLEAR_UMBRELLA_SET = (
	(1, (4, 5)), (2, (5)), (3, (3, 4, 7)),
	(4, (3)), (5, (3, 4)), (6, (8)), (7, (1)), (9, (1))
)
NORMAL_CLEAR_LANTERN_SET = (
	(1, (4, 5)), (2, (1, 3, 4, 6)), (3, (3, 4, 6, 7)),
	(4, (2, 6)), (5, (4, 5, 8)), (6, (5, 7, 8)),
	(7, (1, 2, 3, 4, 8)), (8, (2)), (9, (3, 7)), (10, (10))
)
NORMAL_CLEAR_YINYANG_SET = (
	(1, (4, 5)), (2, (1, 4, 6)), (3, (3)),
	(5, (3, 4)), (7, (1, 2)), (8, (4)), (10, (5))
)
NORMAL_CLEAR_BOMB_SET = (
	(1, (4, 5)), (2, (1, 3, 5, 6)), (3, (3, 6, 7)),
	(4, (1, 2, 3, 6)), (5, (3, 4, 5, 8)), (6, (4, 5, 6, 7)),
	(7, (1, 4, 8))
)
NORMAL_CLEAR_JIZO_SET = (
	(1, (4, 5)), (2, (1, 3, 4, 5, 6)), (3, (3, 4, 6, 7)),
	(4, (1, 2, 3, 6)), (5, (3, 4, 5, 8)), (6, (2, 4, 5, 6, 7, 8)),
	(7, (1, 2, 3, 4, 6, 7, 8)), (8, (2, 4, 5)), (9, (2, 3, 4, 5, 6, 7, 8)),
	(10, (2, 5, 9, 10))
)
NORMAL_CLEAR_DOLL_SET = (
	(2, (4, 5, 6)), (3, (3, 4)), (5, (2)), (6, (2, 6, 7, 8)),
	(7, (1, 2, 6)), (8, (5, 6, 7)), (9, (1, 3, 4, 6)), (10, (3))
)
NORMAL_CLEAR_MALLET_SET = (
	(1, (4, 5)), (2, (1, 3, 4, 6)), (3, (6)), (4, (2)),
	(5, (4, 5, 8)), (7, (1, 2, 3, 8)), (8, (2)), (10, (9))
)

#
# Specific item combinations.
#
# Clears using the Cursed Decoy Doll as a Sub-item and no Main Item.
# This counts as a No-Item clear since no Main Items are used.
NORMAL_CLEAR_DOLL_SUB_SET = (
	(4, (2)), (7, (2, 8)), (8, (5)), (9, (4, 8)), (10, (10))
)
# Clears using Jizo (Main) and Doll (Sub).
NORMAL_CLEAR_JIZO_DOLL_SET = (
	(5, (2)), (8, (6, 7)), (9, (1)), (10, (1, 3, 4, 6, 7, 8))
)
# Clears using Lantern (Main) and Doll (Sub).
NORMAL_CLEAR_LANTERN_DOLL_SET = (
	(2, (5)), (4, (1, 3)), (5, (2, 3)), (6, (2, 4, 6)),
	(7, (6, 7)), (8, (4, 6, 7)), (9, (1, 2, 5, 6)), (10, (1, 3, 4, 5))
)
# Clears using Mallet (Main) and Jizo (Sub).
NORMAL_CLEAR_MALLET_JIZO_SET = (
	(3, (3, 4)), (5, (2, 3)), (6, (2, 4, 6, 7, 8)), (7, (7)),
	(8, (6)), (9, (2, 3, 7))
)