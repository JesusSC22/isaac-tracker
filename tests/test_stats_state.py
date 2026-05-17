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


def test_bestiary_list_includes_all_catalog_except_big_bosses():
    from tracker.data.bestiary import BESTIARY_CATALOG
    from tracker.data.big_bosses import BIG_BOSS_BESTIARY_KEYS
    state = _build_stats_state(_parsed())
    expected = len(BESTIARY_CATALOG) - len(BIG_BOSS_BESTIARY_KEYS & set(BESTIARY_CATALOG.keys()))
    assert len(state["bestiary"]) == expected
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


def test_unique_seen_never_exceeds_catalog():
    """Bug 342/282: el numerador no puede pasarse del catálogo."""
    # Simula save con variantes del save que NO están en el catálogo.
    state = _build_stats_state(_parsed(bestiary_kills={
        0x02D00000: 5,        # Mom (45, 0) — sí está en catálogo
        0x7FFFFFF0: 3,        # variante inventada — NO en catálogo
        0x7EEEEEF0: 2,        # otra inventada
    }))
    by_key = {g["key"]: g for g in state["globals"]}
    seen = by_key["unique_seen"]["value"]
    total = by_key["unique_seen"]["max"]
    assert seen <= total, f"seen={seen} > total={total} — bug 342/282 vuelve"


def test_big_bosses_array_has_13():
    state = _build_stats_state(_parsed())
    assert "big_bosses" in state
    assert len(state["big_bosses"]) == 13


def test_big_bosses_indices_0_12():
    state = _build_stats_state(_parsed())
    for i, e in enumerate(state["big_bosses"]):
        assert e["idx"] == i


def test_big_bosses_excluded_from_bestiary():
    """Los (type, variant) ocupados por big bosses no aparecen en bestiary_list."""
    from tracker.data.big_bosses import BIG_BOSS_BESTIARY_KEYS
    state = _build_stats_state(_parsed())
    bestiary_keys = {(e["type"], e["variant"]) for e in state["bestiary"]}
    overlap = bestiary_keys & BIG_BOSS_BESTIARY_KEYS
    assert not overlap, f"big bosses fugados al bestiario: {overlap}"


def test_every_bestiary_entry_has_chapter():
    state = _build_stats_state(_parsed())
    valid = {1, 2, 3, 4, 5, 6, 7, "extra"}
    for e in state["bestiary"]:
        assert "chapter" in e, f"missing chapter in {e}"
        assert e["chapter"] in valid


def test_bosses_defeated_global():
    """Hay un nuevo global 'bosses_defeated' con max=13."""
    state = _build_stats_state(_parsed())
    by_key = {g["key"]: g for g in state["globals"]}
    assert "bosses_defeated" in by_key
    assert by_key["bosses_defeated"]["max"] == 13
    assert by_key["bosses_defeated"]["value"] == 0  # empty save
