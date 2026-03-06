from .boss_and_stage import *

DEATH_LINK_LIFE_MSGS: list[str] = [
    " flew too close to a bullet.",
    " can't dodge very well.",
    " has a big hitbox.",
    " thought the bullets were made of candy."
]

DEATH_LINK_STAGE_MSGS: list[str] = [
    " got kicked out of the Black Market.",
    " got kicked off the premises.",
    " fumbled their run.",
    " got folded like a deck of Ability Cards."
]

DEATH_LINK_GENERIC_MSGS: list[str] = [
    " pichuun'd.",
    " fell through a gap.",
    " got spirited away."
]

# Used specifically only when a boss kicked a player out of a stage.
DEATH_LINK_BOSS_STAGE: list[str] = [
    " was chased out of ",
    " by "
]

STAGE_ID_TO_DEATHLINK_LOCATION: dict[int, str] = {
    TUTORIAL_ID: "the Youkai Mountain foothills",
    STAGE1_ID: "Secret Heaven Cliff",
    STAGE2_ID: "the Misty Lake",
    STAGE3_ID: "Sai no Kawara",
    STAGE4_ID: "the Moriya Shrine",
    STAGE5_ID: "Youkai Mountain",
    STAGE6_ID: "the Rainbow Dragon Cave",
    STAGE_CHIMATA_ID: "the Lunar Rainbow Market",
    STAGE_CHALLENGE_ID: "the Lunar Rainbow Black Market"
}

# Death Link messages specific to bosses.
# Ideally this always gets called upon death at the hands of a boss.
# Uses the boss ID as keys.
DEATH_LINK_BOSS_MSGS: dict[int, list[str]] = {
    BOSS_MIKE: [
        " hit Mike Goutokuji's koban coins."
    ],
    BOSS_MINORIKO: [
        " shared sweet potatoes with Minoriko Aki."
    ],
    BOSS_ETERNITY: [
        " snorted Eternity Larva's pollen.",
        " took too many butterfly scales to the face."
    ],
    BOSS_NEMUNO: [
        " had some tea with Nemuno Sakata.",
        " got chopped into mince by Nemuno Sakata."
    ],

    BOSS_CIRNO: [
        " was frozen by Cirno."
    ],
    BOSS_WAKASAGI: [
        " got slapped by Wakasagihime's tail."
    ],
    BOSS_URUMI: [
        " held Urumi Ushizaki's stone baby and fell into the water."
    ],
    BOSS_SEKIBANKI: [
        " didn't see Sekibanki's head coming."
    ],

    BOSS_EBISU: [
        " was stoned to death by Eika Ebisu."
    ],
    BOSS_KUTAKA: [
        " got a rude wake-up call from Kutaka Niwatari."
    ],
    BOSS_NARUMI: [
        " got stomped by Narumi Yatadera."
    ],
    BOSS_KOMACHI: [
        " was reaped by Komachi Onozuka."
    ],

    BOSS_SANAE: [
        " received a miracle from Sanae Kochiya."
    ],
    BOSS_SAKUYA: [
        " got knife'd by Sakuya Izayoi."
    ],
    BOSS_YOUMU: [
        " got slashed by Youmu Konpaku."
    ],
    BOSS_REIMU: [
        " took several amulets to the face from Reimu Hakurei.",
        " forgot to donate to the Hakurei Shrine."
    ],
    BOSS_NITORI: [
        " got blasted with water by Nitori Kawashiro."
    ],

    BOSS_TSUKASA: [
        " got folded by Tsukasa Kudamaki."
    ],
    BOSS_MEGUMU: [
        " saw Megumu Iizunamaru cast too many stars."
    ],
    BOSS_CLOWNPIECE: [
        " took a look at Clownpiece's torch."
    ],
    BOSS_TENSHI: [
        " took Tenshi Hinanawi's keystone to the knee."
    ],

    BOSS_SUIKA: [
        " downed a cup of saké with Suika Ibuki."
    ],
    BOSS_MAMIZOU: [
        " got bamboozled by Mamizou Futatsuiwa."
    ],
    BOSS_SAKI: [
        " couldn't handle Saki Kurokoma's strength."
    ],
    BOSS_MOMOYO: [
        " took Momoyo Himemushi's pickaxe to the face.",
        " was mistaken for diamonds by Momoyo Himemushi."
    ],
    BOSS_TAKANE: [
        " got wrecked by Takane Yamashiro.",
    ],

    BOSS_CHIMATA: [
        " couldn't handle Chimata Tenkyuu's markets."
    ]
}