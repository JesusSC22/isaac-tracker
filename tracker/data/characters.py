"""
Character -> achievement mappings for The Binding of Isaac: Repentance+.

The `CHARACTERS_ACHIEVEMENTS` table is copied verbatim from agusaenz's
isaac-save-auto-editor-steam repo (MIT-licensed) and re-shaped into a list of
rows. Each row has the form `[name, mark0, mark1, ..., mark12]` where the
mark IDs are indices into the save file's achievements chunk (chunk 1, 642
bytes for Repentance+, one byte per achievement: 0 = locked, 1 = unlocked).

The mark order INSIDE the agusaenz table ("save order") is:
    [Mom's Heart, Isaac, Satan, Boss Rush, ???, The Lamb, Mega Satan,
     Ultra Greed, Ultra Greedier, Hush, Delirium, Mother, The Beast]

This is the order from `agusaenz/constants.py`'s `checklist_order` comment
block, NOT the order used by the tracker's HTML UI. The HTML uses:
    [0:Mom's Heart, 1:Isaac, 2:Satan, 3:???, 4:Lamb, 5:Boss Rush, 6:Hush,
     7:Mega Satan, 8:Ultra Greed, 9:Ultra Greedier, 10:Delirium,
     11:Mother, 12:Beast]

The parser uses `SAVE_TO_HTML_MARK` (below) to translate.

Tainted-character caveat (from agusaenz README): Tainted characters share
several Steam achievements (e.g. "kill Mom's Heart with any tainted
character" is a single achievement, reused across all tainted rows). The
table reflects this with duplicate IDs in some tainted rows. As a result,
flipping one mark in-game may appear to flip several in our output. This
matches what Repentance+ itself displays on the in-game post-it notes, so
it is the desired behavior.

Source: https://github.com/agusaenz/isaac-save-auto-editor-steam (MIT licensed)
Backup mirror: https://github.com/DanielG3/isaac-save-edit-steam-achievements
"""
from __future__ import annotations

# Each row: name + 13 achievement IDs in agusaenz save order.
# Length = 34 rows (17 Repentance baseline + 17 Tainted equivalents).
CHARACTERS_ACHIEVEMENTS: list[list[int | str]] = [
    ["Isaac",         167, 106,  43,  70,  49, 149, 205, 192, 296, 179, 282, 440, 441],
    ["Magdalene",     168,  20,  45, 109,  50,  71, 206, 193, 297, 180, 283, 442, 443],
    ["Cain",          171,  21,  46, 110,  75,  51, 207, 194, 298, 181, 284, 444, 445],
    ["Judas",         170, 107,  72, 108,  77,  52, 208, 195, 299, 182, 285, 446, 447],
    ["???",           174,  29,  48, 114, 113,  73, 209, 196, 300, 183, 286, 448, 449],
    ["Eve",           169,  76,  44, 112,  53, 111, 210, 197, 302, 184, 288, 450, 451],
    ["Samson",        177,  54,  56, 115,  55,  74, 211, 198, 301, 185, 287, 452, 453],
    ["Azazel",        173, 126, 127,   9, 128,  47, 212, 199, 304, 186, 290, 454, 455],
    ["Lazarus",       172, 116, 117, 105, 118, 119, 213, 200, 305, 187, 291, 456, 457],
    ["Eden",          176, 121, 122, 125, 123, 124, 214, 201, 303, 188, 289, 458, 459],
    ["The Lost",      175, 129, 130, 133, 131, 132, 215, 202, 307, 189, 293, 460, 461],
    ["Lilith",        223, 218, 220, 222, 219, 221, 216, 203, 306, 190, 292, 462, 463],
    ["Keeper",        241, 236, 237, 240, 238, 239, 217, 204, 308, 191, 294, 464, 465],
    ["Apollyon",      318, 310, 311, 314, 312, 313, 317, 316, 309, 315, 295, 466, 467],
    ["Forgotten",     392, 393, 394, 397, 395, 396, 403, 399, 400, 398, 401, 468, 469],
    ["Bethany",       416, 417, 418, 421, 419, 420, 427, 422, 424, 423, 425, 470, 471],
    ["Jacob & Esau",  428, 429, 430, 433, 431, 432, 439, 434, 436, 435, 437, 472, 473],
    ["T Isaac",       548, 548, 548, 618, 548, 548, 601, 541, 541, 618, 584, 549, 491],
    ["T Magdalene",   550, 550, 550, 619, 550, 550, 602, 530, 530, 619, 585, 551, 492],
    ["T Cain",        552, 552, 552, 620, 552, 552, 603, 534, 534, 620, 586, 553, 493],
    ["T Judas",       554, 554, 554, 621, 554, 554, 604, 525, 525, 621, 587, 555, 494],
    ["T ???",         556, 556, 556, 622, 556, 556, 605, 528, 528, 622, 588, 557, 495],
    ["T Eve",         558, 558, 558, 623, 558, 558, 606, 527, 527, 623, 589, 559, 496],
    ["T Samson",      560, 560, 560, 624, 560, 560, 607, 535, 535, 624, 590, 561, 497],
    ["T Azazel",      562, 562, 562, 625, 562, 562, 608, 539, 539, 625, 591, 563, 498],
    ["T Lazarus",     564, 564, 564, 626, 564, 564, 609, 543, 543, 626, 592, 565, 499],
    ["T Eden",        566, 566, 566, 627, 566, 566, 610, 544, 544, 627, 593, 567, 500],
    ["T Lost",        568, 568, 568, 628, 568, 568, 611, 524, 524, 628, 594, 569, 501],
    ["T Lilith",      570, 570, 570, 629, 570, 570, 612, 526, 526, 629, 595, 571, 502],
    ["T Keeper",      572, 572, 572, 630, 572, 572, 613, 536, 536, 630, 596, 573, 503],
    ["T Apollyon",    574, 574, 574, 631, 574, 574, 614, 540, 540, 631, 597, 575, 504],
    ["T Forgotten",   576, 576, 576, 632, 576, 576, 615, 537, 537, 632, 598, 577, 505],
    ["T Bethany",     578, 578, 578, 633, 578, 578, 616, 529, 529, 633, 599, 579, 506],
    ["T Jacob",       580, 580, 580, 634, 580, 580, 617, 542, 542, 634, 600, 581, 507],
]

# Maps the agusaenz row index (0..33) to the tracker's internal PlayerType ID.
# The tracker uses Isaac's in-engine PlayerType numbering (see state_mapper.py
# Task 7 — `CHARACTER_ID_TO_SLUG`). IDs 11/12 are sub-forms of Lazarus and IDs
# 17/18 are sub-forms of Forgotten, so they are skipped. The 34 keys below are
# exactly the 34 IDs the tracker UI exposes.
AGUSAENZ_INDEX_TO_PLAYERTYPE: dict[int, int] = {
    0: 0,    # Isaac
    1: 1,    # Magdalene
    2: 2,    # Cain
    3: 3,    # Judas
    4: 4,    # ??? (Blue Baby)
    5: 5,    # Eve
    6: 6,    # Samson
    7: 7,    # Azazel
    8: 8,    # Lazarus
    9: 9,    # Eden
    10: 10,  # The Lost
    11: 13,  # Lilith (PT 11/12 are skipped sub-forms)
    12: 14,  # Keeper
    13: 15,  # Apollyon
    14: 16,  # Forgotten
    15: 19,  # Bethany (PT 17/18 are skipped sub-forms)
    16: 20,  # Jacob & Esau
    17: 21,  # Tainted Isaac
    18: 22,  # Tainted Magdalene
    19: 23,  # Tainted Cain
    20: 24,  # Tainted Judas
    21: 25,  # Tainted ???
    22: 26,  # Tainted Eve
    23: 27,  # Tainted Samson
    24: 28,  # Tainted Azazel
    25: 29,  # Tainted Lazarus
    26: 30,  # Tainted Eden
    27: 31,  # Tainted Lost
    28: 32,  # Tainted Lilith
    29: 33,  # Tainted Keeper
    30: 34,  # Tainted Apollyon
    31: 35,  # Tainted Forgotten
    32: 36,  # Tainted Bethany
    33: 37,  # Tainted Jacob (& Esau)
}

# Translates a save-order mark index (0..12, as stored in
# CHARACTERS_ACHIEVEMENTS columns 1..13) to the HTML-order mark index (0..12)
# used by the tracker UI's COMPLETION_MARKS list.
#
# Save order (per agusaenz/constants.py checklist_order):
#     0: Mom's Heart       7: Ultra Greed
#     1: Isaac             8: Ultra Greedier
#     2: Satan             9: Hush
#     3: Boss Rush        10: Delirium
#     4: ???              11: Mother
#     5: Lamb             12: Beast
#     6: Mega Satan
#
# HTML order (per docs/HTML_AUDIT.md / COMPLETION_MARKS in tracker UI):
#     0: Mom's Heart       7: Mega Satan
#     1: Isaac             8: Ultra Greed
#     2: Satan             9: Ultra Greedier
#     3: ???              10: Delirium
#     4: Lamb             11: Mother
#     5: Boss Rush        12: Beast
#     6: Hush
SAVE_TO_HTML_MARK: dict[int, int] = {
    0: 0,    # Mom's Heart -> Mom's Heart
    1: 1,    # Isaac -> Isaac
    2: 2,    # Satan -> Satan
    3: 5,    # Boss Rush -> Boss Rush (save 3, HTML 5)
    4: 3,    # ??? -> ??? (save 4, HTML 3)
    5: 4,    # Lamb -> Lamb (save 5, HTML 4)
    6: 7,    # Mega Satan -> Mega Satan (save 6, HTML 7)
    7: 8,    # Ultra Greed -> Ultra Greed (save 7, HTML 8)
    8: 9,    # Ultra Greedier -> Ultra Greedier (save 8, HTML 9)
    9: 6,    # Hush -> Hush (save 9, HTML 6)
    10: 10,  # Delirium -> Delirium
    11: 11,  # Mother -> Mother
    12: 12,  # Beast -> Beast
}
