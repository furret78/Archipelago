EVENT_ITEM_SCENE_CLEAR_NAME = "Event: Scene Cleared"
EVENT_ITEM_SCENE_UNLOCK_NAME = "Event: Scene Accessible"

CONST_ITEM_NAMES = [
    "Nimble Fabric",
    "Tengu's Toy Camera",
    "Gap Folding Umbrella",
    "Ghastly Send-Off Lantern",
    "Bloodthirsty Yin-Yang Orb",
    "Four-Foot Magic Bomb",
    "Substitute Jizo",
    "Cursed Decoy Doll",
    "Miracle Mallet (Replica)"
]
CONST_ITEM_SHORT_TO_ID = {
    "fabric": 0,
    "camera": 1,
    "umbrella": 2,
    "lantern": 3,
    "yinyang": 4,
    "bomb": 5,
    "jizo": 6,
    "doll": 7,
    "mallet": 8,
    "none": 9
}

CONST_SUBITEM_SLOT_NAME = "Sub-Item Equip Slot"
CONST_PROGRESSIVE_DAY = "Progressive Day"
CONST_PROGRESSIVE_SCENE = "Progressive Scene"
CONST_REMOVE_LEVEL_CAP = "Progressive Items: Remove Level Cap"
CONST_ITEM_STAT_NAMES = [
    "Through Time",
    "Photography Range",
    "Hidden Time",
    "Ghost Time",
    "",
    "Range",
    "Invincible Time",
    "Appearance Time",
    "Damage Output"
]
CONST_SCENE_SKIP_NAME = "Scene Skip"

# Actual ID starts from 0.
CONST_DAY_TO_ID = {
    "Day 1": 0,
    "Day 2": 1,
    "Day 3": 2,
    "Day 4": 3,
    "Day 5": 4,
    "Day 6": 5,
    "Day 7": 6,
    "Day 8": 7,
    "Day 9": 8,
    "Final Day": 9
}

# Index is Day # - 1, Scene # - 1
CONST_SPELLCARD_NAMES = [
    [
        "Nonspell - Yatsuhashi Tsukumo",
        "Water Sign \"Lunatic Red Slap\"",
        "Ice Sign \"Perfect Glacialist\"",
        "Tide Sign \"Tidal Wave of the Lake\"",
        "Ice King \"Frost King\"",
        "Fish Sign \"School of Fish\"",
    ],
    [
        "Scream \"Primal Scream\"",
        "Flying Neck \"Extreme Long Neck\"",
        "Piercing Sound \"Piercing Circle\"",
        "Glinting Eyes \"Hell's Ray\"",
        "Sutra \"Infinite Nenbutsu\"",
        "Flying Neck \"Twin Rokuro Head\""
    ],
    [
        "Nonspell - Kagerou Imaizumi",
        "Full Moon \"Full Moon Roar\"",
        "\"20XX: An Afterlife Odyssey\"",
        "Regretful Life \"Immortality's Reckless Sacrifice\"",
        "Wolf Fang \"Bloodthirsty Wolf Fang\"",
        "Great Fire \"Flower of Edo\"",
        "\"Fire Bird -Legend of Immortality-\""
    ],
    [
        "Nonspell - Yuyuko Saigyouji",
        "Demonify \"Excessive Zouhuo Rumo\"",
        "Butterfly Sign \"Flower, Butterfly, Wind and Moon\"",
        "Poison Nail \"Zombie Claw\"",
        "Hermit Arts \"Wall Runner\"",
        "Cherry Blossom \"Lovely Cherry Blossom Blizzard\"",
        "Hermit Arts \"Wall-Phasing Wormhole\""
    ],
    [
        "Nonspell - Raiko Horikawa",
        "Koto Sign \"Ame no Norigoto\"",
        "Noise Sign \"Biwa of Euphoric Song\"",
        "Thunder Sign \"Den-Den Daiko of Rage\"",
        "Elegy \"Human and Koto Die Together\"",
        "Score \"Score Web\"",
        "Taiko \"Fantastic Woofer\"",
        "Double Chant \"Song of Falling Stars\""
    ],
    [
        "Nonspell - Mamizou Futatsuiwa",
        "Photography \"Quick-Shooting Tengu Scoop\"",
        "Photography \"Full Panoramic Shot\"",
        "Waterfall Sign \"Shiraito Falls\"",
        "Fang Sign \"Chewing Satisfaction\"",
        "Waterfall Sign \"Kegon Gun\"",
        "Photography \"Secluded Paparazzi\"",
        "\"Instant Shot Journalist\""
    ],
    [
        "Love Sign \"Wide Master\"",
        "Time Sign \"Time Stopper Sakuya\"",
        "Light Sign \"Light Flash of the Netherworld\"",
        "Snake Sign \"Bind Snake Come On\"",
        "Love Sign \"Machine Gun Spark\"",
        "Time Sign \"Changeling Magic\"",
        "Higan Sword \"Hacking Slashes of Hell and Paradise\"",
        "Snake Sign \"Red Snake Come On\""
    ],
    [
        "Nonspell - Shinmyoumaru Sukuna",
        "Mikuji \"Rule Violation Barrier\"",
        "\"If the Cuckoo Does Not Sing, Wait For It to Cry\"",
        "\"Inchlings' Hell\"",
        "\"Persuasion Needle\"",
        "\"Humans Are Nice!\"",
        "Shining Needle \"Oni-Slaying, Eye-Stabbing Needle\""
    ],
    [
        "Onbashira \"Rising Onbashira\"",
        "Green Stone \"Jade Break\"",
        "Old Boat \"Ancient Ship\"",
        "Oni Crowd \"Imp Swarm\"",
        "\"Sacred Authority of the Gods\"",
        "Frog Sign \"Bloody Mound of Red Frogs\"",
        "Heat Dragon \"Blazing Dragon Veins\"",
        "Oni Crowd \"Hundred Oni Kaburo\""
    ],
    [
        "\"Binding Laws of Hari\"",
        "\"My Way is Truly That of Heaven!\"",
        "\"Sky of Scarlet Perception of All Youkaikind\"",
        "\"Fitful Nightmare\"",
        "\"Impossible Danmaku Barrier\"",
        "\"Eyes of Brahma\"",
        "\"Seventeen-Article Constitution Bombs\"",
        "\"Kashima Protection\"",
        "\"Duck, Duck, Bat!\"",
        "\"Casebook of Luck, Resilience and Perseverance\""
    ]
]

CONST_NICKNAME_NAME = [
    # Scene clear nicknames
    "Danmaku Amanojaku",
    "Fledgling Amanojaku",
    "Experienced Amanojaku",
    "Full-Fledged Amanojaku",
    "Invincible Amanojaku",
    "Indestructible Amanojaku",
    "Legendary Amanojaku",
    "Mythical Amanojaku",
    # Specific scene clears
    "Amanojaku, Enemy of All",
    "Escapee Amanojaku",
    "First Amanojaku",
    "New Item User",
    "Miraculous, Mysterious Tool User",
    "Hey, You've Got a Free Hand",
    # Playtime nicknames
    "How About Some Tea",
    "Watch Out For Dry Eyes",
    "Achieve Enlightenment!",
    # Death count nicknames
    "I Don't Feel Pain Anymore",
    "Could This Be Pleasure?",
    "Over Her Dead Body",
    # Day all-clears
    "First Day Master",
    "2nd Day Master",
    "3rd Day Master",
    "4th Day Master",
    "5th Day Master",
    "6th Day Master",
    "7th Day Master",
    "8th Day Master",
    "9th Day Master",
    "Last Day Master",
    # Clear 3 scenes with items and no-item
    "Miss Nimble",
    "Camera Kid",
    "Closed Umbrella",
    "A Passing Spirit",
    "Ball User",
    "Handheld Fireworks",
    "Ojizou-san",
    "Doll Shop Owner",
    "Strike Physically",
    "Cheat Hater",
    # Clear 10 scenes instead
    "Nimble-ster",
    "Camera Adult",
    "Favorite Umbrella",
    "Perhaps a Vengeful Spirit?",
    "Ball Craftsman",
    "Miss Starmine",
    "Ksitigarbha",
    "Doll Collector",
    "Pikopiko Hammer",
    "Fair Player",
    # Clear 20 scenes instead
    "Nimble Master",
    "Camera Gentleman",
    "Umbrella House",
    "Splendid Spirit Body",
    "Ball Hermit",
    "Crazy Bomber",
    "Just Like A Jizou",
    "Doll Prototyper",
    "Mallet Smash!",
    "Conserving Spirit"
    # Hidden nicknames / Clear all scenes
    "Nimble Space God",
    "Camera Demon",
    "Umbrella Paradise",
    "A Born Ghost",
    "Co-egg-cidental Tester",
    "Firework Mandala",
    "The World Revolves Around Jizou",
    "Cursed Doll Make-Up",
    "Brainy Kintoki",
    "Ultimate Cheating Life Form"
]

CONST_MUSIC_ROOM_NAMES = [
    "Raise the Signal Fire of Cheating",
    "Cheat Against the Impossible Danmaku",
    "Midnight Spell Card",
    "Romantic Escape Flight",
    "Eternal Transient Reign",
    "Mermaid from the Uncharted Land",
    "Reverse Ideology",
    "Illusionary Joururi",
    "Youkai Mountain ~ Mysterious Mountain"
]

# Temporary Filler items that will disable the Save Replay button if received during a scene.
CONST_TEMP_PREFIX = "Temporary: "
CONST_FILLER_NAME = {
    "freeze": "Freeze Trap",
    "null_sub": "Nullify Sub-Item Trap",
    "count_down": "-1 Item Use Count Trap",
    "count_down2": "-2 Item Use Count Trap",
    "invinc": "3-Second Invincibility",
    "invinc2": "5-Second Invincibility",
    "invinc3": "10-Second Invincibility",
    "count_up": "+1 Item Use Count",
    "count_up2": "+2 Item Use Count"
}

# Items exclusively for Treasure Hunt mode.
# Second entry is an Event item given at the start.
# Third entry is an Event rewarded upon completing this goal.
CONST_TREASURE_ITEM_NAMES = [
    "Treasure: Koban Coin",
    "Miracle Mallet (Real)",
    "Hakurei Shrine's Donation Box"
]

# Goofy Filler items that do nothing.
CONST_FILLER_USELESS_PREFIX = "Filler"
CONST_FILLER_USELESS_NAMES = (
    "HELP ME EIRINNNNNNNNN!!",
    "⑨. バカ",
    "\"Now, bitch, get out of the way!\"",
    "Gunpowder-stuffed Doll",
    "Common Sense",
    "Sumireko's Smartphone"
)