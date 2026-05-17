"""Tests del módulo de big bosses (los 13 que aparecen en marcas de personaje)."""
from __future__ import annotations


def test_module_imports_and_has_13_entries():
    from tracker.data.big_bosses import BIG_BOSSES
    assert len(BIG_BOSSES) == 13


def test_indices_zero_to_twelve_in_order():
    from tracker.data.big_bosses import BIG_BOSSES
    for expected_idx, entry in enumerate(BIG_BOSSES):
        assert entry["idx"] == expected_idx


def test_entry_shape():
    from tracker.data.big_bosses import BIG_BOSSES
    required = {"idx", "name_es", "name_en", "sprite_url", "bestiary_key", "kind"}
    for e in BIG_BOSSES:
        assert required <= set(e.keys()), f"missing keys in {e}"
        assert e["kind"] in {"boss", "event", "transformation"}
        if e["bestiary_key"] is not None:
            assert isinstance(e["bestiary_key"], tuple) and len(e["bestiary_key"]) == 2


def test_boss_rush_and_ultra_greedier_are_eventlike():
    from tracker.data.big_bosses import BIG_BOSSES
    boss_rush = BIG_BOSSES[5]
    assert boss_rush["kind"] == "event"
    assert boss_rush["bestiary_key"] is None

    ultra_greedier = BIG_BOSSES[9]
    assert ultra_greedier["kind"] == "transformation"


def test_bestiary_keys_exist_in_catalog():
    """Los big bosses con bestiary_key != None deben existir en BESTIARY_CATALOG."""
    from tracker.data.bestiary import BESTIARY_CATALOG
    from tracker.data.big_bosses import BIG_BOSSES
    for e in BIG_BOSSES:
        if e["bestiary_key"] is not None:
            assert e["bestiary_key"] in BESTIARY_CATALOG, (
                f"big boss idx {e['idx']} ({e['name_en']}) "
                f"has bestiary_key {e['bestiary_key']} not in catalog"
            )
