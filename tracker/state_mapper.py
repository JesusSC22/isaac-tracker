from __future__ import annotations

from tracker.data.bestiary import BESTIARY_CATALOG
from tracker.data.cards import CARDS
from tracker.data.collectibles import COLLECTIBLES
from tracker.data.donations import DONATION_MILESTONES, GREED_DONATION_MILESTONES
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


def _decode_packed_entity(packed: int) -> tuple[int, int]:
    """packed → (type, variant). Fórmula validada en tests/test_bestiary_parser.py."""
    return (packed >> 20, (packed >> 4) & 0xFFF)


def _build_stats_state(parsed: ParsedSave) -> dict:
    from tracker.data.big_bosses import BIG_BOSSES, BIG_BOSS_BESTIARY_KEYS
    from tracker.data.chapters import resolve_chapter

    def by_tv(d: dict[int, int]) -> dict[tuple[int, int], int]:
        out: dict[tuple[int, int], int] = {}
        for k, v in d.items():
            tv = _decode_packed_entity(k)
            out[tv] = out.get(tv, 0) + v
        return out

    kills_tv = by_tv(parsed.bestiary_kills)
    deaths_tv = by_tv(parsed.bestiary_deaths)
    hits_tv = by_tv(parsed.bestiary_hits)
    encounters_tv = by_tv(parsed.bestiary_encounters)

    catalog_keys = set(BESTIARY_CATALOG.keys())
    # Bug 342/282 fix: el numerador SOLO cuenta entradas del catálogo.
    all_seen_tv = (set(kills_tv) | set(encounters_tv)) & catalog_keys

    # Excluir big bosses del bestiario normal de abajo.
    big_boss_keys_in_catalog = BIG_BOSS_BESTIARY_KEYS & catalog_keys

    # ---- Big bosses panel ----
    big_bosses_list = []
    bosses_defeated_count = 0
    for entry in BIG_BOSSES:
        bkey = entry["bestiary_key"]
        if bkey is not None and bkey in catalog_keys:
            k = kills_tv.get(bkey, 0)
            d = deaths_tv.get(bkey, 0)
            h = hits_tv.get(bkey, 0)
            e = encounters_tv.get(bkey, 0)
            seen = bkey in all_seen_tv
        else:
            k = d = h = e = None
            seen = False
        # parsed.character_marks: dict[int, set[int]] (verificado en save_parser.py:96)
        # mark_completed = True si CUALQUIER personaje tiene esta mark.
        mark_completed = False
        for char_marks in parsed.character_marks.values():
            if entry["idx"] in char_marks:
                mark_completed = True
                break
        seen = seen or mark_completed
        if seen:
            bosses_defeated_count += 1
        big_bosses_list.append({
            "idx": entry["idx"],
            "name_es": entry["name_es"],
            "name_en": entry["name_en"],
            "sprite_url": entry["sprite_url"],
            "kind": entry["kind"],
            "kills": k, "deaths": d, "hits": h, "encounters": e,
            "seen": seen,
            "mark_completed": mark_completed,
        })

    # ---- Globals ----
    globals_list = [
        {"key": "total_kills",      "label_es": "Enemigos eliminados",
         "value": sum(kills_tv.values()),  "icon": "skull"},
        {"key": "total_deaths_by",  "label_es": "Te han matado",
         "value": sum(deaths_tv.values()), "icon": "tombstone"},
        {"key": "total_hits",       "label_es": "Golpes recibidos",
         "value": sum(hits_tv.values()),   "icon": "heart_broken"},
        {"key": "unique_seen",      "label_es": "Bestiario",
         "value": len(all_seen_tv),
         "max":   len(BESTIARY_CATALOG),
         "icon":  "eye"},
        {"key": "bosses_defeated",  "label_es": "Bosses derrotados",
         "value": bosses_defeated_count, "max": 13, "icon": "boss"},
    ]

    # ---- Bestiary (excluyendo big bosses) ----
    bestiary_list = []
    for (t, v), meta in sorted(BESTIARY_CATALOG.items()):
        if (t, v) in big_boss_keys_in_catalog:
            continue
        k = kills_tv.get((t, v), 0)
        d = deaths_tv.get((t, v), 0)
        h = hits_tv.get((t, v), 0)
        e = encounters_tv.get((t, v), 0)
        bestiary_list.append({
            "type": t, "variant": v,
            "name_es": meta["name_es"],
            "name_en": meta["name_en"],
            "category": meta["category"],
            "chapter": resolve_chapter(t, v),
            "kills": k, "deaths": d, "hits": h, "encounters": e,
            "sprite_id": f"{t:03d}.{v:03d}",
            "seen": (t, v) in all_seen_tv,
        })

    return {
        "globals": globals_list,
        "big_bosses": big_bosses_list,
        "bestiary": bestiary_list,
    }


def build_localstorage_state(parsed: ParsedSave) -> dict:
    return {
        "challenges_state": _build_challenges(parsed),
        "characters_state": _build_characters(parsed),
        "achievements_unlocked": sorted(parsed.achievements_unlocked),
        "items_state": _build_items_state(parsed),
        "cards_state": _build_cards_state(parsed),
        "donations_state": _build_donations_state(parsed),
        "stats_state": _build_stats_state(parsed),
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


def _build_cards_state(parsed: ParsedSave) -> dict[str, bool]:
    """Return {card_id_str: unlocked?} for every real (non-removed) card.

    A card is "unlocked" when:
      - it has no achievement gate (achievement_id is None) — always available, or
      - its achievement byte is set in the save's achievements chunk.

    Isaac's save file does not contain a per-card "seen" bitfield, so this
    achievement-based view is the most accurate signal we can give the player
    about what is/isn't in their card pool. See tracker/PARSER_AUDIT.md.
    """
    out: dict[str, bool] = {}
    for cid, meta in CARDS.items():
        if meta["removed"]:
            continue
        ach_id = meta.get("achievement_id")
        unlocked = ach_id is None or ach_id in parsed.achievements_unlocked
        out[str(cid)] = unlocked
    return out


def _build_donations_state(parsed: ParsedSave) -> dict:
    def section(raw_count: int, milestones: list[dict]) -> dict:
        enriched = [
            {
                **m,
                "unlocked": raw_count >= m["amount"]
                            or m["achievement_id"] in parsed.achievements_unlocked,
            }
            for m in milestones
        ]
        biggest_unlocked = max(
            (m["amount"] for m in enriched if m["unlocked"]),
            default=0,
        )
        visible_count = max(raw_count, biggest_unlocked)
        return {"count": visible_count, "milestones": enriched}

    return {
        "normal": section(parsed.donation_count, DONATION_MILESTONES),
        "greed":  section(parsed.greed_donation_count, GREED_DONATION_MILESTONES),
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
