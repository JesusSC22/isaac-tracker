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


def test_cards_state_unlocked_by_achievement():
    """A card is 'unlocked' when its achievement byte is set in the save, or
    when it has no achievement gate at all (always-available)."""
    from tracker.data.cards import CARDS
    # Find one always-available card and one gated card to drive the test.
    always = next(cid for cid, m in CARDS.items()
                  if not m["removed"] and m.get("achievement_id") is None)
    gated_id, gated_meta = next(
        (cid, m) for cid, m in CARDS.items()
        if not m["removed"] and m.get("achievement_id") is not None
    )
    gated_ach = gated_meta["achievement_id"]

    # Save with only the gated card's achievement set.
    p = ParsedSave(
        slot=1,
        challenges_complete=set(),
        characters_unlocked=set(),
        character_marks={},
        achievements_unlocked={gated_ach},
        parsed_at=datetime(2026, 5, 14, tzinfo=timezone.utc),
    )
    state = build_localstorage_state(p)
    assert state["cards_state"][str(always)] is True, "always-available card must be unlocked"
    assert state["cards_state"][str(gated_id)] is True, "gated card with its achievement set must be unlocked"

    # And the same card with NO achievement set: locked.
    p2 = ParsedSave(
        slot=1,
        challenges_complete=set(),
        characters_unlocked=set(),
        character_marks={},
        achievements_unlocked=set(),
        parsed_at=datetime(2026, 5, 14, tzinfo=timezone.utc),
    )
    state2 = build_localstorage_state(p2)
    assert state2["cards_state"][str(gated_id)] is False, "gated card without achievement must be locked"
    assert state2["cards_state"][str(always)] is True, "always-available card stays unlocked regardless"


def test_cards_state_excludes_removed_entries():
    p = ParsedSave(
        slot=1,
        challenges_complete=set(),
        characters_unlocked=set(),
        character_marks={},
        achievements_unlocked=set(),
        parsed_at=datetime(2026, 5, 14, tzinfo=timezone.utc),
    )
    state = build_localstorage_state(p)
    # id 0 is removed sentinel in CARDS, must not appear in the state dict.
    assert "0" not in state["cards_state"]


def test_donations_state_exposes_counters_and_milestones():
    """El estado del frontend expone contadores e hitos con flag unlocked."""
    from tracker.save_parser import ParsedSave
    from tracker.state_mapper import build_localstorage_state

    parsed = ParsedSave(
        slot=1,
        donation_count=500,
        greed_donation_count=50,
        achievements_unlocked=set(),
    )
    state = build_localstorage_state(parsed)
    donations = state["donations_state"]
    assert donations["normal"]["count"] == 500
    assert donations["greed"]["count"] == 50

    by_amount_normal = {m["amount"]: m for m in donations["normal"]["milestones"]}
    assert by_amount_normal[400]["unlocked"] is True
    assert by_amount_normal[600]["unlocked"] is False


def test_donations_state_uses_achievement_as_fallback_source_of_truth():
    """Si el counter es 0 pero el achievement está set, el hito aparece
    desbloqueado. Caso saves migrados desde Afterbirth+."""
    from tracker.save_parser import ParsedSave
    from tracker.state_mapper import build_localstorage_state

    parsed = ParsedSave(
        slot=1,
        donation_count=0,
        greed_donation_count=0,
        achievements_unlocked={250, 138},  # 879 Greed, 999 normal.
    )
    state = build_localstorage_state(parsed)
    by_g = {m["amount"]: m for m in state["donations_state"]["greed"]["milestones"]}
    by_n = {m["amount"]: m for m in state["donations_state"]["normal"]["milestones"]}
    assert by_g[879]["unlocked"] is True
    assert by_g[666]["unlocked"] is False
    assert by_n[999]["unlocked"] is True
    assert by_n[900]["unlocked"] is False


def test_donations_visible_count_bumps_to_biggest_unlocked():
    """Si el counter raw es 0 pero el ach del hito 879 está set, el counter
    visible debe ser >=879 para que la barra de progreso sea coherente con
    los hitos verdes."""
    from tracker.save_parser import ParsedSave
    from tracker.state_mapper import build_localstorage_state

    parsed = ParsedSave(
        slot=1,
        donation_count=0,
        greed_donation_count=0,
        achievements_unlocked={250},  # 879 Greed.
    )
    state = build_localstorage_state(parsed)
    assert state["donations_state"]["greed"]["count"] == 879
    assert state["donations_state"]["normal"]["count"] == 0


def test_donations_visible_count_uses_max_of_raw_and_unlocked():
    """Si el counter raw está más alto que el ach más alto unlocked, el
    visible es el counter raw."""
    from tracker.save_parser import ParsedSave
    from tracker.state_mapper import build_localstorage_state

    parsed = ParsedSave(
        slot=1,
        donation_count=750,
        greed_donation_count=0,
        achievements_unlocked={134},  # 10 normal — counter raw es más alto.
    )
    state = build_localstorage_state(parsed)
    assert state["donations_state"]["normal"]["count"] == 750

