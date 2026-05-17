"""Tests del mapeo type → chapter del bestiario."""
from __future__ import annotations


def test_chapter_table_imports():
    from tracker.data.chapters import ENEMY_TYPE_TO_CHAPTER, VARIANT_OVERRIDES
    assert isinstance(ENEMY_TYPE_TO_CHAPTER, dict)
    assert isinstance(VARIANT_OVERRIDES, dict)


def test_canonical_bosses_chapters():
    """Bosses canónicos están en su capítulo del lore."""
    from tracker.data.chapters import ENEMY_TYPE_TO_CHAPTER as M
    assert M.get(45) == 4,   "Mom → Cap 4 (Womb)"
    assert M.get(78) == 4,   "Mom's Heart → Cap 4 (Womb)"
    assert M.get(84) == 5,   "Satan → Cap 5 (Sheol)"
    assert M.get(102) == 5,  "Isaac (boss) → Cap 5 (Cathedral)"
    assert M.get(110) == 6,  "Blue Baby (???) → Cap 6 (Dark Room/Chest)"
    assert M.get(273) == 6,  "The Lamb → Cap 6 (Dark Room)"
    assert M.get(407) == 7,  "Hush → Cap 7 (Blue Womb)"
    assert M.get(412) == 7,  "Delirium → Cap 7 (Void)"
    assert M.get(951) == 7,  "The Beast → Cap 7 (Home)"
    assert M.get(912) == 7,  "Mother → Cap 7 (Corpse final)"


def test_chapter_values_are_valid():
    """Cada capítulo es 1-7 o 'extra'."""
    from tracker.data.chapters import ENEMY_TYPE_TO_CHAPTER, VARIANT_OVERRIDES
    valid = {1, 2, 3, 4, 5, 6, 7, "extra"}
    for type_id, ch in ENEMY_TYPE_TO_CHAPTER.items():
        assert ch in valid, f"type {type_id} has invalid chapter {ch}"
    for key, ch in VARIANT_OVERRIDES.items():
        assert ch in valid, f"variant {key} has invalid chapter {ch}"


def test_every_catalog_entry_resolvable():
    """Toda entrada del bestiario debe resolverse a un capítulo (caída a 'extra' OK)."""
    from tracker.data.bestiary import BESTIARY_CATALOG
    from tracker.data.chapters import resolve_chapter
    for (t, v) in BESTIARY_CATALOG.keys():
        ch = resolve_chapter(t, v)
        assert ch in {1, 2, 3, 4, 5, 6, 7, "extra"}, f"({t},{v}) → {ch}"
