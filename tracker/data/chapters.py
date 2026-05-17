"""Mapeo type-id → capítulo del juego para el bestiario.

Fuente canónica: bindingofisaacrebirth.wiki.gg/wiki/Monsters "Monsters by Floor".
Regla de desempate: enemigo que aparece en múltiples capítulos → el más bajo.
Las variantes (variant > 0) heredan del type base salvo VARIANT_OVERRIDES.

Capítulos:
  1 = Basement / Cellar / Burning Basement / Downpour / Dross
  2 = Caves / Catacombs / Flooded Caves / Mines / Ashpit
  3 = Depths / Necropolis / Dank Depths / Mausoleum / Gehenna
  4 = Womb / Utero / Scarred Womb / Corpse
  5 = Sheol / Cathedral
  6 = Dark Room / Chest
  7 = Blue Womb / Void / Home
  "extra" = multi-chapter recurring, no clear attribution, or special (e.g. Ultra Greed)
"""
from __future__ import annotations

__all__ = ["ENEMY_TYPE_TO_CHAPTER", "VARIANT_OVERRIDES", "resolve_chapter"]

ENEMY_TYPE_TO_CHAPTER: dict[int, int | str] = {
    # ── Cap 1: Basement / Cellar / Burning Basement / Downpour / Dross ──
    0: 1,    # Bodies (generic floor enemy)
    17: 1,   # Gaper
    28: 1,   # Gurgle
    54: 1,   # Mulligan
    61: 1,   # Muliboom
    80: 1,   # Spider
    96: 1,   # Boomfly
    105: 1,  # Maggot
    113: 1,  # Charger
    153: 1,  # Blicker
    155: 1,  # Baby
    161: 1,  # Globin
    189: 1,  # Poky
    213: 1,  # Level2fly (Pooter)
    214: 1,  # Level2spider (Big Spider)
    217: 1,  # Wall Hugger
    222: 1,  # Dinga
    276: 1,  # Roundy
    300: 1,  # Mushroomman (Downpour)
    301: 1,  # Poisonmind (Downpour)
    803: 1,  # Blindbat (Downpour/Dross)
    806: 1,  # Bubbles (Downpour)
    810: 1,  # Small Leech (Downpour)
    811: 1,  # Deepgaper (Dross)
    812: 1,  # Subhorf (Downpour/Dross)
    813: 1,  # Blurb (Downpour)
    816: 1,  # Polty (Downpour)
    817: 1,  # Prey (Dross)
    850: 1,  # Barfy (Dross)
    853: 1,  # Small Maggot

    # ── Cap 1 bosses ──
    1: 1,    # Larryjr
    4: 1,    # Monstro
    7: 1,    # Duke of Flies
    10: 1,   # Gemini
    13: 1,   # Steven
    14: 1,   # Famine (Horseman — first appearance)
    16: 1,   # Widow
    19: 1,   # Pin
    21: 1,   # Gurdy Jr
    908: 1,  # Baby Plum (Downpour boss)

    # ── Cap 2: Caves / Catacombs / Flooded Caves / Mines / Ashpit ──
    29: 2,   # Horf
    44: 2,   # Hopper / Leaper
    79: 2,   # Spit
    115: 2,  # Spitty
    122: 2,  # Host
    127: 2,  # Red Host
    130: 2,  # Hive
    141: 2,  # Maw
    142: 2,  # Red Maw
    144: 2,  # Psychic Maw
    152: 2,  # Keeper
    172: 2,  # Leech
    174: 2,  # Kamikaze Leech
    183: 2,  # Hanger
    191: 2,  # Swarmer
    199: 2,  # Parabite
    219: 2,  # Squirt
    220: 2,  # Cod Worm
    221: 2,  # Swinger
    238: 2,  # Splasher — appears in Flooded Caves (2) and Corpse (4); lowest = 2
    239: 2,  # Grub
    243: 2,  # Conjoined Spitty
    244: 2,  # Roundworm
    246: 2,  # Ragling
    247: 2,  # Flesh Mobile Host
    248: 2,  # Psychic Horf
    249: 2,  # Full Fly (Flooded Caves)
    250: 2,  # Ticking Spider
    255: 2,  # Nightcrawler
    256: 2,  # Dartfly (Flooded Caves)
    302: 2,  # Stoney
    814: 2,  # Strider (Mines)
    818: 2,  # Rockspider (Mines/Ashpit)
    819: 2,  # Flybomb (Ashpit)
    820: 2,  # Danny (Mines)
    821: 2,  # Blaster (Mines)
    822: 2,  # Bouncer (Mines)
    823: 2,  # Quakey (Mines)
    824: 2,  # Gyro (Ashpit)
    825: 2,  # Fireworm (Ashpit)
    826: 2,  # Hardy (Mines)
    827: 2,  # Faceless (Mines)
    828: 2,  # Echobat (Ashpit)
    829: 2,  # Mole (Mines)
    851: 2,  # Twitchy (Mines/Ashpit)
    852: 2,  # Spikeball (Mines)
    854: 2,  # Adult Leech (Flooded Caves/Ashpit)
    868: 2,  # Armyfly (Ashpit)

    # ── Cap 2 bosses ──
    24: 2,   # Blighted Ovum
    25: 2,   # Fistula
    27: 2,   # Peep
    30: 2,   # Gurdy
    32: 2,   # Chub
    35: 2,   # Chad
    36: 2,   # Pestilence (Horseman)
    38: 2,   # Husk
    41: 2,   # The Hollow
    49: 2,   # Monstro II
    62: 2,   # Scolex
    63: 2,   # Blastocyst — appears in Caves (2) and Womb (4); lowest = 2
    67: 2,   # Triachnid
    909: 2,  # Scourge (Ashpit boss)
    910: 2,  # Chimera (Mines boss)
    913: 2,  # Min Min (Mines boss)
    914: 2,  # Clog (Flooded Caves boss)
    915: 2,  # Singe (Ashpit boss)
    916: 2,  # Bumbino (Mines boss)

    # ── Cap 3: Depths / Necropolis / Dank Depths / Mausoleum / Gehenna ──
    23: 3,   # Dank Charger (Dank Depths)
    87: 3,   # Boil
    145: 3,  # Knight
    150: 3,  # Selfless Knight
    154: 3,  # Embryo
    158: 3,  # Brain
    160: 3,  # Membrain
    175: 3,  # Holy Leech
    176: 3,  # Cage Vis
    181: 3,  # Chubber
    187: 3,  # Mask and Heart
    192: 3,  # Dople
    193: 3,  # Evil Twin
    194: 3,  # Eye
    197: 3,  # Fred
    201: 3,  # Brimstone Eye
    202: 3,  # Constant Stone Shooter
    203: 3,  # Brimstone Head
    205: 3,  # Baby Long Legs
    206: 3,  # Crazy Long Legs
    211: 3,  # Deathshead
    215: 3,  # Migraine
    223: 3,  # Oob
    224: 3,  # Black Maw
    229: 3,  # Tumor
    240: 3,  # Wall Creep
    241: 3,  # Rage Creep
    242: 3,  # Blind Creep
    251: 3,  # Begotten
    252: 3,  # Null Body
    253: 3,  # Psy Tumor
    254: 3,  # Floating Knight
    257: 3,  # Conjoined Fatty
    259: 3,  # Imp (Mausoleum)
    283: 3,  # Bone Knight (Mausoleum)
    285: 3,  # Red Ghost (Mausoleum) — appears in Mausoleum (3) and Cathedral area (5/6); lowest = 3
    286: 3,  # Flesh Deathshead (Mausoleum)
    830: 3,  # Big Bony (Mausoleum/Gehenna)
    831: 3,  # Necromancer (Mausoleum/Gehenna)
    832: 3,  # Exorcist (Mausoleum/Gehenna)
    833: 3,  # Candler (Mausoleum/Gehenna)
    834: 3,  # Whipper/Snapper/Lunatic Body (Gehenna)
    835: 3,  # Swapper (Gehenna)
    836: 3,  # Visversa (Mausoleum/Gehenna)
    837: 3,  # Graverobber (Mausoleum)
    839: 3,  # Strifer (Gehenna)
    840: 3,  # Pon (Gehenna)
    841: 3,  # Revenant (Mausoleum)
    842: 3,  # Nightwatch (Mausoleum/Gehenna)
    843: 3,  # Canary (Gehenna)

    # ── Cap 3 bosses ──
    47: 3,   # The Wretched
    48: 3,   # Loki
    51: 3,   # Gish
    52: 3,   # War (Horseman)
    57: 3,   # Mask of Infamy
    59: 3,   # Daddy Long Legs
    66: 3,   # Conquest
    68: 3,   # Teratoma
    71: 3,   # Lokii
    85: 3,   # Dangle
    88: 3,   # Mega Maw (Megamaw2)
    89: 3,   # Fatty (boss, same type as enemy below)
    903: 3,  # Visage (Mausoleum boss)
    904: 3,  # Siren (Mausoleum boss)
    905: 3,  # Heretic (Mausoleum boss)
    906: 3,  # Hornfel (Mausoleum boss, Cap 3 alt route)
    907: 3,  # Gideon (Mausoleum boss, Cap 3 alt route)
    919: 3,  # Raglich (Gehenna boss)
    920: 3,  # Horny Boys (Gehenna boss)
    921: 3,  # Clutch (Mausoleum boss)
    922: 3,  # Cadavra (Gehenna boss)

    # ── Cap 4: Womb / Utero / Scarred Womb / Corpse ──
    15: 4,   # Grilled Clotty (Scarred Womb)
    22: 4,   # Drowned Hive (Flooded) — actually Womb adjacent, keep 4
    40: 4,   # Scarred Guts (Scarred Womb)
    65: 4,   # Clotty
    75: 4,   # L'Blob
    164: 4,  # Guts
    170: 4,  # Mama Guts
    198: 4,  # Lump (Corpse2)
    207: 4,  # Fatty (Womb enemy)
    208: 4,  # Fat Sack
    209: 4,  # Blubber
    210: 4,  # Half Sack
    212: 4,  # Mom's Hand / Dank Deathshead
    216: 4,  # Dip Corn
    227: 4,  # Boney Body (Corpse)
    228: 4,  # Homunculus (Corpse)
    230: 4,  # Camillo Jr (Corpse)
    231: 4,  # Nerve Ending 2 (Corpse)
    235: 4,  # Gaping Maw (Corpse)
    236: 4,  # Broken Gaping Maw (Corpse)
    237: 4,  # Gurgling Hands (Corpse boss room)
    288: 4,  # Dukie
    289: 4,  # Ulcer
    290: 4,  # Meatball
    291: 4,  # Pitfall
    303: 4,  # Blister (Corpse)
    304: 4,  # The Thing (Corpse)
    305: 4,  # Ministro (Corpse)
    856: 4,  # Gasbag (Corpse)
    857: 4,  # Cohort (Corpse)
    858: 4,  # Vessel (Corpse)
    859: 4,  # Floating Host (Corpse)
    860: 4,  # Unborn (Corpse)
    861: 4,  # Pustule (Corpse)
    862: 4,  # Cyst (Corpse)
    865: 4,  # Evis (Corpse)

    # ── Cap 4 bosses ──
    39: 4,   # Scarred Double Vis (Scarred Womb)
    45: 4,   # Mom
    60: 4,   # Bloat
    70: 4,   # It Lives
    78: 4,   # Mom's Heart
    90: 4,   # Fatty (boss variant 2 = Womb)
    911: 4,  # Rotgut (Corpse boss)
    917: 4,  # Colostomia (Corpse boss)
    918: 4,  # Turdlet (Corpse boss)
    912: 7,  # Mother (Corpse II — post-Corpse final boss) → Cap 7 per plan

    # ── Cap 5: Sheol / Cathedral ──
    64: 5,   # Death (Horseman)
    72: 5,   # The Fallen
    74: 5,   # Satan Leg
    82: 5,   # Krampus (Cathedral/Sheol devil)
    83: 5,   # Haunt (Cathedral)
    84: 5,   # Satan
    102: 5,  # Isaac (boss, Cathedral)
    157: 5,  # Angelic Baby (Cathedral)
    260: 5,  # Lil Haunt (Cathedral)
    278: 5,  # Black Globin (Sheol)
    279: 5,  # Black Globin Head (Sheol)
    280: 5,  # Black Globin Body (Sheol)
    282: 5,  # Mega Clotty (Sheol)
    804: 5,  # Rock Grimace (Cathedral)
    805: 5,  # Bishop (Cathedral)
    807: 5,  # Wraith (Sheol)
    808: 5,  # Willo (Cathedral)
    809: 5,  # Bomb Grimace (Cathedral)

    # ── Cap 6: Dark Room / Chest ──
    81: 6,   # Headless Horseman (Dark Room)
    101: 6,  # Red Boomfly (Chest)
    110: 6,  # Blue Baby / ??? (Chest)
    273: 6,  # The Lamb (Dark Room)

    # ── Cap 7: Blue Womb / Void / Home ──
    407: 7,  # Hush (Blue Womb)
    406: "extra",  # Ultra Greed (Greed Mode — no numbered chapter)
    412: 7,  # Delirium (Void)
    951: 7,  # The Beast (Home)
    # 912 already set above (Mother → 7)
}

# Post-processing corrections for entries that cannot be expressed cleanly in the literal.
# Fatty boss (89) → Depths (3); Fatty (90) = "Fatty2" boss variant — also Depths (3).
# Type 90 is listed in Cap 4 block by position but belongs to Cap 3 → correct here.
_CORRECTIONS: dict[int, int | str] = {
    90: 3,
}
for _t, _ch in _CORRECTIONS.items():
    ENEMY_TYPE_TO_CHAPTER[_t] = _ch

VARIANT_OVERRIDES: dict[tuple[int, int], int | str] = {
    # Dank Charger (23,0) → Cap 3 (Dank Depths); Drowned Charger (23,1) → Cap 2 (Flooded Caves)
    (23, 1): 2,
    # Dank Globin (24,2) → Cap 3; base type 24 = Blighted Ovum → Cap 2
    (24, 2): 3,
    # Grilled Clotty (15,100) → Cap 4 (Scarred Womb); base type 15 overrides not needed, type set
    # Scarred Double Vis (39,3) → Cap 4; base type 39 already set to 4
    # Loose Knight (41,10), Black Knight (41,12) → Cap 3 (Necropolis); base 41 = Hollow → Cap 2
    (41, 10): 3,
    (41, 12): 3,
    # Drowned Boomfly (25,2) → Cap 2 (Flooded Caves); base type 25 = Fistula → Cap 2. Same.
    # Flaming Gaper (10,2), Rotten Gaper (10,10) → Cap 1; base type 10 = Gemini → Cap 1. Same.
    # Dank Deathshead (212,1) → Cap 3 (Dank Depths); base type 212 = Mom's Hand → Cap 4
    (212, 1): 3,
    # Smoky (212,100) → Cap 3 (Dank Depths)
    (212, 100): 3,
    # Scarred Guts (40,1) → Cap 4 (Scarred Womb); type 40 not in base table (set via variant)
    (40, 1): 4,
    # Coal (818,2) → Cap 2 (Ashpit), same as base
    # Tinted Rock Spider (818,1) → Cap 2, same as base
    # Mullighoul (817,1) → Cap 1 (Dross), same as base
    # Coalboy (820,1) → Cap 2 (Mines), same as base
    # Grilledgyro (824,1) → Cap 2, same as base
    # Foreigner (843,1) → Cap 3 (Gehenna), same as base
    # Fanatic (832,1) → Cap 3 (Mausoleum/Gehenna), same as base
    # Whipper/Snapper/Lunatic Body variants (834,0/1/2) → Cap 3, same as base
    # Blueconjoinedfatty (257,1) → Cap 3, same as base
    # Flaming Fatty (207,2) → Cap 4 (Womb), same as base
    # Drowned Hive (22,1) → Cap 4; base type 22 set to 4 above
    # Corpse Eater (239,100) → Cap 4 (Corpse); base type 239 = Grub → Cap 2
    (239, 100): 4,
    # Soicreep (240,100) → Cap 4 (Womb/Corpse); base type 240 = Wall Creep → Cap 3
    (240, 100): 4,
    # Cursed Globin (24,100) → Cap 3/4 cursed floors → "extra"
    (24, 100): "extra",
    # Dragonfly (25,100) → various shops/special → "extra"
    (25, 100): "extra",
    # Sick Boomfly (25,101) → "extra" (cursed floors)
    (25, 101): "extra",
    # Hard Host (27,100) → varies → "extra"
    (27, 100): "extra",
    # Ink (61,100) → Devil Room / special → "extra"
    (61, 100): "extra",
    # Mama Fly (61,101) → boss rush/special → "extra"
    (61, 101): "extra",
    # Scared Parabite Scarred (58,1) → Mausoleum/Gehenna variant → Cap 3
    (58, 1): 3,
    # Lil Haunt (260,10) → Cathedral → Cap 5; base type 260 set to 5
}


def resolve_chapter(type_id: int, variant: int) -> int | str:
    """Devuelve capítulo (1-7 o 'extra') para una (type, variant) del bestiario."""
    if (type_id, variant) in VARIANT_OVERRIDES:
        return VARIANT_OVERRIDES[(type_id, variant)]
    return ENEMY_TYPE_TO_CHAPTER.get(type_id, "extra")
