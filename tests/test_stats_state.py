from datetime import datetime, timezone

from tracker.save_parser import ParsedSave
from tracker.state_mapper import _build_stats_state, _decode_packed_entity


def _parsed(**kw):
    base = dict(
        slot=1, challenges_complete=set(), characters_unlocked=set(),
        character_marks={}, achievements_unlocked=set(), items_seen=set(),
        donation_count=0, greed_donation_count=0,
        bestiary_kills={}, bestiary_deaths={}, bestiary_hits={}, bestiary_encounters={},
        parsed_at=datetime(2026, 5, 17, tzinfo=timezone.utc),
    )
    base.update(kw)
    return ParsedSave(**base)


def test_decode_packed_entity_formula():
    # 010.010 → packed = (10<<20) | (10<<4) = 0x00A000A0
    assert _decode_packed_entity(0x00A000A0) == (10, 10)
    assert _decode_packed_entity(0x05500000) == (85, 0)
    assert _decode_packed_entity(0x02D00000) == (45, 0)  # Mom


def test_empty_save_produces_zero_globals():
    state = _build_stats_state(_parsed())
    by_key = {g["key"]: g for g in state["globals"]}
    assert by_key["total_kills"]["value"] == 0
    assert by_key["total_deaths_by"]["value"] == 0
    assert by_key["total_hits"]["value"] == 0
    assert by_key["unique_seen"]["value"] == 0


def test_kills_sum_into_total():
    state = _build_stats_state(_parsed(bestiary_kills={0x00A000A0: 5, 0x02D00000: 3}))
    by_key = {g["key"]: g for g in state["globals"]}
    assert by_key["total_kills"]["value"] == 8


def test_bestiary_list_includes_all_catalog():
    from tracker.data.bestiary import BESTIARY_CATALOG
    state = _build_stats_state(_parsed())
    assert len(state["bestiary"]) == len(BESTIARY_CATALOG)
    assert all(e["seen"] is False for e in state["bestiary"])


def test_seen_flag_from_kills_or_encounters():
    # 010.010 = Rotten Gaper. Pongo solo kills.
    state = _build_stats_state(_parsed(bestiary_kills={0x00A000A0: 1}))
    rg = next(e for e in state["bestiary"] if (e["type"], e["variant"]) == (10, 10))
    assert rg["seen"] is True
    # 045.000 = Mom. Pongo solo encounters.
    state2 = _build_stats_state(_parsed(bestiary_encounters={0x02D00000: 1}))
    mom = next(e for e in state2["bestiary"] if (e["type"], e["variant"]) == (45, 0))
    assert mom["seen"] is True


def test_donations_not_in_stats_globals():
    # Las donaciones se muestran en la pestaña de Donaciones, no en Estadísticas.
    state = _build_stats_state(_parsed(donation_count=120, greed_donation_count=450))
    keys = {g["key"] for g in state["globals"]}
    assert "donations_normal" not in keys
    assert "donations_greed" not in keys
