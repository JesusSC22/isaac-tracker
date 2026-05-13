from __future__ import annotations

from tracker.data.collectibles import COLLECTIBLES
from tracker.save_parser import ParsedSave

CHALLENGE_IDS = range(1, 46)  # Repentance/Repentance+: 45 challenges, IDs 1..45.

MARK_IDS = range(0, 13)  # 0..12 inclusive — HTML COMPLETION_MARKS order.

# The 34 characters in challenges.html, in the order they appear in CHARACTERS
# (L759-1066). DO NOT normalize quirky spellings — these are the exact
# localStorage keys the HTML reads.
EXPECTED_CHARACTER_SLUGS: list[str] = [
    # Normal (17) — challenges.html L761..L905
    "isaac", "cain", "apollyon", "magdalene", "lazarus", "bethany", "eden",
    "judas", "blue-baby", "eve", "samson", "azazel", "the-forgotten",
    "lilith", "jacob-and-esau", "the-lost", "keeper",
    # Tainted (17) — challenges.html L914..L1058
    "tainted-cain", "tainted-isaac", "tainted-magdalena", "tainted-bethany",
    "tainted-apollyon", "tainted-judas", "tainted-lazarus", "tainted-forgotten",
    "tainted-jacob-and-esau", "tainted-eve", "tainted-azazel",
    "tainted-blue-baby", "tainted-samson", "tainted-lilith", "tainted-eden",
    "tainted-the-lost", "tainted-keeper",
]

# Maps Isaac PlayerType internal IDs to the slug used in challenges.html
# localStorage keys. PlayerType IDs come from the save_parser (which sources
# them from tracker.data.characters AGUSAENZ_INDEX_TO_PLAYERTYPE).
CHARACTER_ID_TO_SLUG: dict[int, str] = {
    0:  "isaac",
    1:  "magdalene",
    2:  "cain",
    3:  "judas",
    4:  "blue-baby",
    5:  "eve",
    6:  "samson",
    7:  "azazel",
    8:  "lazarus",
    9:  "eden",
    10: "the-lost",
    13: "lilith",
    14: "keeper",
    15: "apollyon",
    16: "the-forgotten",
    19: "bethany",
    20: "jacob-and-esau",
    21: "tainted-isaac",
    22: "tainted-magdalena",
    23: "tainted-cain",
    24: "tainted-judas",
    25: "tainted-blue-baby",
    26: "tainted-eve",
    27: "tainted-samson",
    28: "tainted-azazel",
    29: "tainted-lazarus",
    30: "tainted-eden",
    31: "tainted-the-lost",
    32: "tainted-lilith",
    33: "tainted-keeper",
    34: "tainted-apollyon",
    35: "tainted-forgotten",
    36: "tainted-bethany",
    37: "tainted-jacob-and-esau",
}

SLUG_TO_CHARACTER_ID: dict[str, int] = {v: k for k, v in CHARACTER_ID_TO_SLUG.items()}

# Import-time sanity: every expected slug must be mappable.
_missing = set(EXPECTED_CHARACTER_SLUGS) - set(SLUG_TO_CHARACTER_ID.keys())
if _missing:
    raise RuntimeError(
        f"CHARACTER_ID_TO_SLUG missing slugs: {_missing}. "
        "Fix the table — every slug in EXPECTED_CHARACTER_SLUGS must have a PlayerType ID."
    )
_extra = set(SLUG_TO_CHARACTER_ID.keys()) - set(EXPECTED_CHARACTER_SLUGS)
if _extra:
    raise RuntimeError(
        f"CHARACTER_ID_TO_SLUG has extra slugs not in HTML: {_extra}"
    )


def build_localstorage_state(parsed: ParsedSave) -> dict:
    return {
        "challenges_state": _build_challenges(parsed),
        "characters_state": _build_characters(parsed),
        "achievements_unlocked": sorted(parsed.achievements_unlocked),
        "items_state": _build_items_state(parsed),
        "meta": {
            "slot": parsed.slot,
            "parsed_at": parsed.parsed_at.isoformat(),
        },
    }


def _build_items_state(parsed: ParsedSave) -> dict[str, bool]:
    """Map every non-removed collectible id (as a string) to whether the
    player has seen it. Keys are strings to survive JSON round-tripping
    cleanly on the JS side (Object keys are always strings anyway)."""
    return {
        str(item_id): item_id in parsed.items_seen
        for item_id, meta in COLLECTIBLES.items()
        if not meta["removed"]
    }


def _build_challenges(parsed: ParsedSave) -> dict[str, bool]:
    return {f"c_{i}": (i in parsed.challenges_complete) for i in CHALLENGE_IDS}


def _build_characters(parsed: ParsedSave) -> dict[str, bool]:
    out: dict[str, bool] = {}
    for slug in EXPECTED_CHARACTER_SLUGS:
        char_id = SLUG_TO_CHARACTER_ID[slug]
        out[f"{slug}_unlocked"] = char_id in parsed.characters_unlocked
        marks = parsed.character_marks.get(char_id, set())
        for mark_id in MARK_IDS:
            out[f"{slug}_mark_{mark_id}"] = mark_id in marks
    return out
