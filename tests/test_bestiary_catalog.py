"""Tests del catálogo de bestiario generado por tools/build_bestiary.py."""
from __future__ import annotations


def test_bestiary_catalog_has_at_least_100_entries():
    from tracker.data.bestiary import BESTIARY_CATALOG
    assert len(BESTIARY_CATALOG) >= 100, f"got {len(BESTIARY_CATALOG)}"


def test_bestiary_catalog_entries_well_formed():
    from tracker.data.bestiary import BESTIARY_CATALOG
    for key, meta in BESTIARY_CATALOG.items():
        assert isinstance(key, tuple) and len(key) == 2
        assert {"name_en", "name_es", "category"} <= set(meta.keys())
        assert meta["category"] in {"enemy", "miniboss", "boss"}


def test_canonical_bosses_in_catalog():
    """Mom, Beast, Lamb, Hush deben estar en el catálogo como bosses."""
    from tracker.data.bestiary import BESTIARY_CATALOG
    canonical = {
        (45, 0): "Mom",
        (951, 0): "Beast",
        (273, 0): "Lamb",
        (407, 0): "Hush",
    }
    missing = []
    wrong_category = []
    for key, name in canonical.items():
        if key not in BESTIARY_CATALOG:
            missing.append((key, name))
        elif BESTIARY_CATALOG[key]["category"] != "boss":
            wrong_category.append((key, name, BESTIARY_CATALOG[key]["category"]))
    assert not missing, f"missing canonical bosses: {missing}"
    assert not wrong_category, f"wrong category: {wrong_category}"


def test_at_least_five_distinct_bosses():
    from tracker.data.bestiary import BESTIARY_CATALOG
    boss_types = {t for (t, _v), meta in BESTIARY_CATALOG.items() if meta["category"] == "boss"}
    assert len(boss_types) >= 5, f"got {len(boss_types)}"
