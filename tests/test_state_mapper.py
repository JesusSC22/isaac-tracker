from datetime import datetime, timezone

from tracker.save_parser import ParsedSave
from tracker.state_mapper import build_localstorage_state, EXPECTED_CHARACTER_SLUGS


def _empty_parsed(slot=1):
    return ParsedSave(
        slot=slot,
        challenges_complete=set(),
        characters_unlocked=set(),
        character_marks={},
        parsed_at=datetime(2026, 5, 13, tzinfo=timezone.utc),
    )


def test_empty_save_produces_all_false_challenges():
    state = build_localstorage_state(_empty_parsed())
    challenges = state["challenges_state"]
    assert set(challenges.keys()) == {f"c_{i}" for i in range(1, 46)}
    assert all(v is False for v in challenges.values())


def test_completed_challenges_marked_true():
    p = ParsedSave(
        slot=1,
        challenges_complete={1, 9, 30, 45},
        characters_unlocked=set(),
        character_marks={},
        parsed_at=datetime(2026, 5, 13, tzinfo=timezone.utc),
    )
    state = build_localstorage_state(p)
    assert state["challenges_state"]["c_1"] is True
    assert state["challenges_state"]["c_9"] is True
    assert state["challenges_state"]["c_30"] is True
    assert state["challenges_state"]["c_45"] is True
    assert state["challenges_state"]["c_2"] is False


def test_meta_block_present():
    state = build_localstorage_state(_empty_parsed(slot=2))
    assert state["meta"]["slot"] == 2
    assert "parsed_at" in state["meta"]


def test_characters_state_has_all_34_slugs():
    state = build_localstorage_state(_empty_parsed())
    chars = state["characters_state"]
    for slug in EXPECTED_CHARACTER_SLUGS:
        assert f"{slug}_unlocked" in chars
        for mark_id in range(13):
            assert f"{slug}_mark_{mark_id}" in chars


def test_characters_state_empty_save_all_false():
    state = build_localstorage_state(_empty_parsed())
    assert all(v is False for v in state["characters_state"].values())


def test_isaac_unlocked_with_marks():
    # Isaac is PlayerType 0. He has marks 0 (MH) and 1 (Isaac kill).
    p = ParsedSave(
        slot=1,
        challenges_complete=set(),
        characters_unlocked={0},
        character_marks={0: {0, 1}},
        parsed_at=datetime(2026, 5, 13, tzinfo=timezone.utc),
    )
    state = build_localstorage_state(p)
    assert state["characters_state"]["isaac_unlocked"] is True
    assert state["characters_state"]["isaac_mark_0"] is True
    assert state["characters_state"]["isaac_mark_1"] is True
    assert state["characters_state"]["isaac_mark_2"] is False
    assert state["characters_state"]["cain_unlocked"] is False


def test_tainted_magdalena_spelling_preserved():
    # SPEC LOCK-IN: tainted-magdalena (Spanish a), NOT tainted-magdalene.
    state = build_localstorage_state(_empty_parsed())
    assert "tainted-magdalena_unlocked" in state["characters_state"]
    assert "tainted-magdalene_unlocked" not in state["characters_state"]


def test_tainted_forgotten_no_the_prefix():
    state = build_localstorage_state(_empty_parsed())
    assert "tainted-forgotten_unlocked" in state["characters_state"]
    assert "tainted-the-forgotten_unlocked" not in state["characters_state"]


def test_tainted_the_lost_keeps_the():
    state = build_localstorage_state(_empty_parsed())
    assert "tainted-the-lost_unlocked" in state["characters_state"]
    assert "tainted-lost_unlocked" not in state["characters_state"]


def test_character_count_is_34():
    state = build_localstorage_state(_empty_parsed())
    unlocked_keys = [k for k in state["characters_state"] if k.endswith("_unlocked")]
    assert len(unlocked_keys) == 34


def test_empty_save_produces_all_false_items():
    state = build_localstorage_state(_empty_parsed())
    items = state["items_state"]
    assert isinstance(items, dict)
    assert len(items) > 500  # ~721 non-removed collectibles
    assert all(v is False for v in items.values())
    # Keys are string ids
    assert all(isinstance(k, str) for k in items.keys())


def test_seen_items_marked_true():
    p = ParsedSave(
        slot=1,
        challenges_complete=set(),
        characters_unlocked=set(),
        character_marks={},
        achievements_unlocked=set(),
        items_seen={1, 33, 105},
        parsed_at=datetime(2026, 5, 13, tzinfo=timezone.utc),
    )
    state = build_localstorage_state(p)
    assert state["items_state"]["1"] is True
    assert state["items_state"]["33"] is True
    assert state["items_state"]["105"] is True
    assert state["items_state"]["2"] is False


def test_items_state_excludes_removed_placeholders():
    """Removed/placeholder ids must NOT appear in items_state."""
    from tracker.data.collectibles import COLLECTIBLES
    state = build_localstorage_state(_empty_parsed())
    items = state["items_state"]
    for item_id, meta in COLLECTIBLES.items():
        if meta["removed"]:
            assert str(item_id) not in items, f"removed id {item_id} leaked into items_state"
        else:
            assert str(item_id) in items
