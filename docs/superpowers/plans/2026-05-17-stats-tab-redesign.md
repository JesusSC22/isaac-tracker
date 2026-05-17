# Rediseño de la pestaña Estadísticas — Plan de implementación

> **For agentic workers:** REQUIRED: Use superpowers-extended-cc:subagent-driven-development (if subagents available) or superpowers-extended-cc:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar la pestaña Estadísticas actual (cutre, con bug de conteo, sprites cortados y emojis) por el diseño aprobado en `docs/superpowers/specs/2026-05-17-stats-tab-redesign-design.md`: buscador estilo Ítems, panel de 13 big bosses con sprites reales de wiki, bestiario agrupado por capítulo del juego.

**Architecture:** Cambios en 3 capas — (1) data pipeline (`tools/build_bestiary.py` + nuevos módulos `chapters.py`, `big_bosses.py`); (2) backend Python (`tracker/state_mapper._build_stats_state` separa big_bosses, expone chapter, corrige bug 342/282); (3) frontend embebido en `challenges.html` (HTML + CSS + JS reescritos para `#stats-view`).

**Tech Stack:** Python 3 (pytest, PIL/Pillow para sprites), HTML + CSS + JS vanilla embebido en `challenges.html`, Nuitka para el bundle .exe.

---

## File Structure

**Files to create:**
- `tracker/data/chapters.py` — `ENEMY_TYPE_TO_CHAPTER: dict[int, int|str]`, `VARIANT_OVERRIDES: dict[tuple[int,int], int|str]`
- `tracker/data/big_bosses.py` — `BIG_BOSSES: list[BigBossEntry]` con los 13 big bosses (idx, name_es, name_en, sprite_id, bestiary_key)
- `tools/download_bestiary_sprites.py` — nuevo script que descarga sprites desde wiki a `tracker/assets/bestiary_icons/<type>_<variant>.png`
- `tests/test_chapters.py` — tests del mapeo de capítulos
- `tests/test_big_bosses.py` — tests del módulo big_bosses

**Files to modify:**
- `tools/build_bestiary.py` — incluir `chapter` en cada entrada generada
- `tracker/data/bestiary.py` — output regenerado (esta es la salida del build, no se edita a mano)
- `tracker/state_mapper.py:90-136` — `_build_stats_state` refactor completo
- `tracker/assets/bestiary_inline.js` — regenerado con sprites de wiki
- `challenges.html` (raíz) — bloque `#stats-view` (CSS líneas ~1935-2020, HTML ~2164-2195, JS ~6104-6298)
- `tracker/assets/challenges.html` — sync mirror (auto-sincronizado por `build_nuitka.py:_sync_root_assets`)
- `tests/test_stats_state.py` — tests nuevos + actualizar existentes
- `tests/test_bestiary_catalog.py` — test nuevo para campo `chapter`

**Files NOT touched:**
- Save parser (`tracker/save_parser.py`, `tracker/save_locator.py`) — los datos crudos ya son suficientes
- Otras pestañas (Desafíos, Personajes, Ítems, Trinkets, Cartas, Donaciones) — fuera de alcance

---

## Pre-flight check (single step)

- [ ] **Verifica que estás en main, sin cambios sin commitear que NO tengan que ver con esta feature.** Si los hay, stashear o commitear primero.

```bash
git status
```

---

## Task 1: Mapeo de capítulos por tipo de enemigo

**Tarea TaskList:** #1 (parcial — la parte del campo `chapter`)
**Files:**
- Create: `tracker/data/chapters.py`
- Create: `tests/test_chapters.py`

- [ ] **1.1 — Test inicial: tabla está bien formada y cubre rangos canónicos**

Crear `tests/test_chapters.py`:

```python
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
```

- [ ] **1.2 — Run tests, expect ImportError**

```bash
pytest tests/test_chapters.py -v
```

Expected: ImportError "No module named 'tracker.data.chapters'".

- [ ] **1.3 — Crear `tracker/data/chapters.py` con la tabla**

```python
"""Mapeo type-id → capítulo del juego para el bestiario.

Fuente canónica: bindingofisaacrebirth.wiki.gg/wiki/Monsters "Monsters by Floor".
Regla de desempate: enemigo que aparece en múltiples capítulos → el más bajo.
Las variantes (variant > 0) heredan del type base salvo VARIANT_OVERRIDES.
"""
from __future__ import annotations

# Cap 1 = Basement/Cellar/Burning Basement/Downpour/Dross
# Cap 2 = Caves/Catacombs/Flooded Caves/Mines/Ashpit
# Cap 3 = Depths/Necropolis/Dank Depths/Mausoleum/Gehenna
# Cap 4 = Womb/Utero/Scarred Womb/Corpse (no-Mother)
# Cap 5 = Sheol/Cathedral
# Cap 6 = Dark Room/Chest
# Cap 7 = Blue Womb/Void/Home + Mother (final)

ENEMY_TYPE_TO_CHAPTER: dict[int, int | str] = {
    # Bosses canónicos (definidos por el lore)
    45:  4,  # Mom
    78:  4,  # Mom's Heart / It Lives
    84:  5,  # Satan
    102: 5,  # Isaac (boss) — Cathedral
    110: 6,  # ??? (Blue Baby) — Dark Room/Chest
    273: 6,  # The Lamb — Dark Room
    406: "extra",  # Ultra Greed — Greed Mode (sin capítulo numerado)
    407: 7,  # Hush — Blue Womb
    412: 7,  # Delirium — Void
    908: 1,  # Baby Plum (mini)
    909: "extra",  # Scourge — alt route
    910: "extra",  # Chimera — alt route
    911: 4,  # Rotgut — Corpse alt boss
    912: 7,  # Mother — Corpse final
    950: 7,  # Dogma — Home
    951: 7,  # The Beast — Home
    903: 1,  # Visage (Downpour alt)
    904: 1,  # Siren (Downpour alt)
    905: 2,  # Heretic (Mines alt)
    906: 3,  # Hornfel (Mausoleum alt)
    907: 3,  # Gideon (Mausoleum alt)
    913: 1,  # Min Min (Downpour mini)
    914: 2,  # Clog (Mines mini)
    915: 3,  # Singe (Mausoleum mini)
    916: 2,  # Bumbino (Mines mini)
    917: 1,  # Colostomia (Dross alt)
    918: 1,  # Turdlet (Dross alt)
    919: 4,  # Raglich
    920: 3,  # Horny Boys
    921: 4,  # Clutch
    922: 4,  # Cadavra

    # Enemigos básicos
    # Cap 1
    10: 1,   # Gusher
    13: 1,   # Pooter
    14: 1,   # Clotty
    15: 1,   # Maw
    16: 1,   # Host
    17: 1,   # Chub (mini) — TODO check
    18: 1,   # Hopper
    19: 1,   # Boom Fly
    20: 1,   # Monstro (mini)
    21: 1,   # Pin (mini)
    24: 1,   # Globin
    25: 1,   # Boom Fly
    27: 1,   # Boil
    28: 1,   # Gurgle
    29: 1,   # Duke of Flies (mini, también Cap 2)
    30: 1,   # Mulligan
    39: 1,   # Gemini variants — mini
    44: 1,   # Hopper Leaper
    50: 1,   # Fatty
    51: 1,   # Gish
    54: 1,   # Mulligan dross
    57: 1,   # Mask of Infamy

    # Cap 2 (Caves family)
    22: 2,   # Hive
    23: 2,   # Charger
    33: 2,   # Mom's Hand
    34: 2,   # Eye
    35: 2,   # Buttlicker (Chad)
    37: 2,   # Vis
    41: 2,   # The Hollow
    42: 2,   # Loose Knight
    43: 2,   # Gurdy (mini)
    47: 2,   # The Wretched
    48: 2,   # Loki
    49: 2,   # Monstro II
    52: 2,   # War
    58: 2,   # Parabite
    59: 2,   # Daddy Long Legs
    60: 2,   # Bloat
    61: 2,   # Muliboom
    62: 2,   # Scolex (mini)
    63: 2,   # Blastocyst

    # Cap 3 (Depths family)
    36: 3,   # Husk
    40: 3,   # Scarred Guts
    65: 3,   # Knight
    66: 3,   # Conquest
    67: 3,   # Triachnid
    68: 3,   # Teratoma
    70: 3,   # It Lives variants
    71: 3,   # Loki II
    72: 3,   # The Fallen
    74: 3,   # Satan Leg (mini)
    75: 3,   # Leech
    79: 3,   # Spit
    81: 3,   # Headless Horseman
    82: 3,   # Krampus
    83: 3,   # The Haunt
    85: 3,   # Dangle

    # Cap 4 (Womb family)
    64: 4,   # Death
    100: 4,  # Famine extra forms
    101: 4,  # War variants

    # Cap 6/7 misc
    275: 7,  # Megasatan minions
    411: 7,  # Hush minions
    413: 7,  # Delirium minions

    # Sin atribución clara → "extra"
    0: "extra",  # Bodies/static
    80: "extra",  # Generic Spider
}


VARIANT_OVERRIDES: dict[tuple[int, int], int | str] = {
    # Variantes que pertenecen a un capítulo distinto del type base.
    # Ejemplo: si tuviéramos un "champion" que solo aparece en Cap 3:
    # (24, 100): 3,   # Cursed Globin
}


def resolve_chapter(type_id: int, variant: int) -> int | str:
    """Devuelve capítulo (1-7 o 'extra') para una (type, variant) del bestiario.

    Orden de búsqueda:
      1. VARIANT_OVERRIDES si existe la tupla exacta.
      2. ENEMY_TYPE_TO_CHAPTER por type_id.
      3. Fallback: "extra".
    """
    if (type_id, variant) in VARIANT_OVERRIDES:
        return VARIANT_OVERRIDES[(type_id, variant)]
    return ENEMY_TYPE_TO_CHAPTER.get(type_id, "extra")
```

> **Nota para el implementador:** la tabla anterior cubre los EntityTypes más frecuentes pero NO es exhaustiva. Después de redactarla, **ejecuta `pytest tests/test_chapters.py::test_every_catalog_entry_resolvable -v`** y, para los que caigan en "extra" inesperadamente, consulta la wiki página por página y añade entradas. Es trabajo iterativo de 30-60 minutos. Está bien que algunos enemigos queden en "extra" si son genuinamente trans-capítulo (Spider, Fly genérico).

- [ ] **1.4 — Run tests, expect PASS**

```bash
pytest tests/test_chapters.py -v
```

Si algún canónico falla, ajustar la tabla. Si `test_every_catalog_entry_resolvable` falla porque una key no existe en `BESTIARY_CATALOG`, deja la tabla con lo que tienes y continúa (el test asegura cobertura, no ausencia de "extra").

- [ ] **1.5 — Commit**

```bash
git add tracker/data/chapters.py tests/test_chapters.py
git commit -m "feat(bestiary): mapeo type → capítulo del juego con resolve_chapter()"
```

---

## Task 2: Catálogo de big bosses

**Tarea TaskList:** #1 (parte big bosses)
**Files:**
- Create: `tracker/data/big_bosses.py`
- Create: `tests/test_big_bosses.py`

- [ ] **2.1 — Test inicial**

`tests/test_big_bosses.py`:

```python
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
        # bestiary_key puede ser None (event/transformation) o (type, variant)
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
```

- [ ] **2.2 — Run, expect ImportError**

```bash
pytest tests/test_big_bosses.py -v
```

- [ ] **2.3 — Crear `tracker/data/big_bosses.py`**

```python
"""Los 13 big bosses que aparecen en las marcas de completitud de cada personaje.

Esta lista debe estar alineada con MARK_BOSS_SPRITES en challenges.html.
"""
from __future__ import annotations

from typing import TypedDict


class BigBossEntry(TypedDict):
    idx: int                              # 0-12, mismo orden que MARK_BOSS_SPRITES
    name_es: str
    name_en: str
    sprite_url: str                       # URL wiki — bundleada por download_bestiary_sprites.py
    bestiary_key: tuple[int, int] | None  # (type, variant) si tiene entrada; None si event/transformation
    kind: str                             # "boss" | "event" | "transformation"


BIG_BOSSES: list[BigBossEntry] = [
    {"idx": 0, "name_es": "Corazón de Mamá", "name_en": "Mom's Heart",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Mom%27s_Heart_ingame.png",
     "bestiary_key": (78, 0), "kind": "boss"},
    {"idx": 1, "name_es": "Isaac",           "name_en": "Isaac",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Isaac_ingame.png",
     "bestiary_key": (102, 0), "kind": "boss"},
    {"idx": 2, "name_es": "Satán",           "name_en": "Satan",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Satan_ingame.png",
     "bestiary_key": (84, 0), "kind": "boss"},
    {"idx": 3, "name_es": "???",             "name_en": "??? (Blue Baby)",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_%3F%3F%3F_ingame.png",
     "bestiary_key": (110, 0), "kind": "boss"},
    {"idx": 4, "name_es": "El Cordero",      "name_en": "The Lamb",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_The_Lamb_ingame.png",
     "bestiary_key": (273, 0), "kind": "boss"},
    {"idx": 5, "name_es": "Boss Rush",       "name_en": "Boss Rush",
     "sprite_url": "",                       # se usa bossrush.png local
     "bestiary_key": None, "kind": "event"},
    {"idx": 6, "name_es": "Hush",            "name_en": "Hush",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Hush_ingame.png",
     "bestiary_key": (407, 0), "kind": "boss"},
    {"idx": 7, "name_es": "Mega Satán",      "name_en": "Mega Satan",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Mega_Satan_ingame.png",
     "bestiary_key": None, "kind": "boss"},  # No siempre catalogado; kills no rastreado
    {"idx": 8, "name_es": "Ultra Greed",     "name_en": "Ultra Greed",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Ultra_Greed_ingame.png",
     "bestiary_key": (406, 0), "kind": "boss"},
    {"idx": 9, "name_es": "Ultra Greedier",  "name_en": "Ultra Greedier",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Ultra_Greedier_ingame.png",
     "bestiary_key": None, "kind": "transformation"},
    {"idx": 10, "name_es": "Delirium",       "name_en": "Delirium",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Delirium_ingame.png",
     "bestiary_key": (412, 0), "kind": "boss"},
    {"idx": 11, "name_es": "Madre",          "name_en": "Mother",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Mother_Full_portrait.png",
     "bestiary_key": (912, 0), "kind": "boss"},
    {"idx": 12, "name_es": "La Bestia",      "name_en": "The Beast",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_The_Beast_ingame.png",
     "bestiary_key": (951, 0), "kind": "boss"},
]

BIG_BOSS_BESTIARY_KEYS: set[tuple[int, int]] = {
    e["bestiary_key"] for e in BIG_BOSSES if e["bestiary_key"] is not None
}
```

- [ ] **2.4 — Run tests, expect PASS**

```bash
pytest tests/test_big_bosses.py -v
```

Si `test_bestiary_keys_exist_in_catalog` falla para Mega Satan o algún otro, NO añadir manualmente — significa que ese big boss no está catalogado y debe quedarse con `bestiary_key=None`. Editar el módulo poniendo `bestiary_key=None` y `kind="boss"` (los unseen sin contador son OK).

- [ ] **2.5 — Commit**

```bash
git add tracker/data/big_bosses.py tests/test_big_bosses.py
git commit -m "feat(bestiary): catálogo de los 13 big bosses con bestiary_key opcional"
```

---

## Task 3: Refactor `_build_stats_state`

**Tarea TaskList:** #3
**Depende de:** Tasks 1 y 2
**Files:**
- Modify: `tracker/state_mapper.py:90-136`
- Modify: `tests/test_stats_state.py`

- [ ] **3.1 — Test del bug 342/282 (fail first)**

Añadir a `tests/test_stats_state.py` después de la última función:

```python
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
```

También **actualizar** `test_bestiary_list_includes_all_catalog`:

```python
def test_bestiary_list_includes_all_catalog_except_big_bosses():
    from tracker.data.bestiary import BESTIARY_CATALOG
    from tracker.data.big_bosses import BIG_BOSS_BESTIARY_KEYS
    state = _build_stats_state(_parsed())
    expected = len(BESTIARY_CATALOG) - len(BIG_BOSS_BESTIARY_KEYS & set(BESTIARY_CATALOG.keys()))
    assert len(state["bestiary"]) == expected
    assert all(e["seen"] is False for e in state["bestiary"])
```

- [ ] **3.2 — Run, expect failures**

```bash
pytest tests/test_stats_state.py -v
```

Expected: nuevos tests fallan (KeyError "big_bosses", etc.), el de `unique_seen` puede fallar dependiendo del save.

- [ ] **3.3 — Reescribir `_build_stats_state`**

Reemplaza el cuerpo de la función en `tracker/state_mapper.py:90-136` por:

```python
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
            seen = False  # se actualizará abajo si hay mark
        mark_completed = entry["idx"] in parsed.character_marks_global \
            if hasattr(parsed, "character_marks_global") else False
        # Si no podemos derivar mark_completed del parsed, intentar por character_marks
        if not mark_completed and hasattr(parsed, "character_marks"):
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
```

> **Nota:** la lógica de `mark_completed` asume que `ParsedSave` expone `character_marks: dict[char_slug, set[int]]`. **Verifica antes con `grep -n character_marks tracker/save_parser.py`** y ajusta el acceso si el shape difiere. Si tu parser no expone marks indexadas por idx, deja `mark_completed = False` y crea un TODO comment — el test `test_bosses_defeated_global` con save vacío seguirá pasando.

- [ ] **3.4 — Run tests, todos pasan**

```bash
pytest tests/test_stats_state.py tests/test_chapters.py tests/test_big_bosses.py -v
```

Si algún test falla, leer el output y ajustar. NO seguir si no están todos en verde.

- [ ] **3.5 — Commit**

```bash
git add tracker/state_mapper.py tests/test_stats_state.py
git commit -m "feat(stats): separar big bosses + corregir bug 342/282 + chapter por entrada"
```

---

## Task 4: Descargar sprites del bestiario desde la wiki

**Tarea TaskList:** #2
**Depende de:** Task 1 y 2 (para tener big_bosses con sprite_url, y bestiary regenerable)
**Files:**
- Create: `tools/download_bestiary_sprites.py`
- Modify: `tools/build_bestiary.py` (sólo si hace falta inyectar sprites descargados sobre los actuales)

- [ ] **4.1 — Crear `tools/download_bestiary_sprites.py`**

Copiar la estructura de `tools/download_trinket_icons.py` y adaptar. La función crítica es generar URLs estilo wiki para los enemigos del bestiario y los 13 big bosses:

```python
"""Descarga sprites del bestiario desde bindingofisaacrebirth.wiki.gg.

Para los 13 big bosses, usa BIG_BOSSES[i].sprite_url directamente.
Para el resto del bestiario, prueba varios patrones de URL.
"""
from __future__ import annotations

import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "tracker" / "assets" / "bestiary_icons"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
from tracker.data.bestiary import BESTIARY_CATALOG  # noqa: E402
from tracker.data.big_bosses import BIG_BOSSES  # noqa: E402

BASE_FILE = "https://bindingofisaacrebirth.wiki.gg/wiki/Special:FilePath/"
USER_AGENT = "isaac-tracker-bestiary-fetcher/1.0"


def candidate_urls(name_en: str, category: str) -> list[str]:
    """Patrones de naming en la wiki para sprites de enemigos."""
    base = name_en.strip().replace(" ", "_")
    no_apos = re.sub(r"['’]", "", base)

    suffixes = []
    if category == "boss":
        suffixes = ["_ingame.png", ".png", "_appear.png"]
    elif category == "miniboss":
        suffixes = ["_ingame.png", ".png"]
    else:
        suffixes = [".png", "_appear.png"]

    candidates = []
    for variant in (base, no_apos):
        for suf in suffixes:
            candidates.append(BASE_FILE + urllib.parse.quote(variant + suf, safe=""))
            # Variant con prefijo "Boss_" para bosses
            if category in {"boss", "miniboss"}:
                candidates.append(BASE_FILE + urllib.parse.quote(f"Boss_{variant}{suf}", safe=""))

    # Dedup manteniendo orden
    seen = set()
    out = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def try_download(url: str, out: Path) -> tuple[bool, int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) < 100 or data[:8] != b"\x89PNG\r\n\x1a\n":
            return False, len(data), "not-a-png"
        out.write_bytes(data)
        return True, len(data), ""
    except urllib.error.HTTPError as e:
        return False, 0, f"http-{e.code}"
    except Exception as e:
        return False, 0, type(e).__name__


def download_big_bosses() -> tuple[int, list]:
    failures = []
    ok = 0
    for entry in BIG_BOSSES:
        if not entry["sprite_url"]:
            continue  # Boss Rush usa bossrush.png local
        out = OUT_DIR / f"bigboss_{entry['idx']:02d}.png"
        if out.exists() and out.stat().st_size > 100:
            ok += 1
            continue
        success, size, err = try_download(entry["sprite_url"], out)
        if success:
            print(f"  OK  big_boss[{entry['idx']:2d}] {entry['name_en']:25s} ({size}B)")
            ok += 1
        else:
            failures.append((entry["idx"], entry["name_en"], err))
            print(f"  FAIL big_boss[{entry['idx']:2d}] {entry['name_en']:25s} err={err}")
        time.sleep(0.25)
    return ok, failures


def download_bestiary() -> tuple[int, list]:
    failures = []
    ok = 0
    for (t, v), meta in BESTIARY_CATALOG.items():
        out = OUT_DIR / f"{t:03d}_{v:03d}.png"
        if out.exists() and out.stat().st_size > 100:
            ok += 1
            continue
        success = False
        last_err = "no-candidates"
        for url in candidate_urls(meta["name_en"], meta["category"]):
            s, _size, err = try_download(url, out)
            if s:
                success = True
                last_err = ""
                break
            last_err = err
            time.sleep(0.1)
        if success:
            ok += 1
        else:
            failures.append((t, v, meta["name_en"], last_err))
        time.sleep(0.2)
    return ok, failures


def main() -> None:
    print("=== Big bosses ===")
    bb_ok, bb_fail = download_big_bosses()
    print(f"  Total OK: {bb_ok} / {sum(1 for e in BIG_BOSSES if e['sprite_url'])}")

    print("=== Bestiario ===")
    bes_ok, bes_fail = download_bestiary()
    print(f"  Total OK: {bes_ok} / {len(BESTIARY_CATALOG)}")

    if bb_fail or bes_fail:
        log = ROOT / "tools" / "bestiary_sprite_review.log"
        with log.open("w", encoding="utf-8") as f:
            f.write("=== Big bosses failures ===\n")
            for idx, name, err in bb_fail:
                f.write(f"  idx={idx} name={name} err={err}\n")
            f.write("\n=== Bestiary failures ===\n")
            for t, v, name, err in bes_fail:
                f.write(f"  ({t},{v}) name={name} err={err}\n")
        print(f"\nFallos volcados a: {log}")


if __name__ == "__main__":
    main()
```

- [ ] **4.2 — Ejecutar el download**

```bash
python tools/download_bestiary_sprites.py
```

Es lento (~5-10 min porque hay ~280 entradas + 12 big bosses, con `time.sleep` entre cada uno). Lee el output: si más del 40% del bestiario falla, parar y revisar los patrones de URL antes de seguir. Big bosses deben fallar 0 (las URLs ya son válidas en el módulo).

- [ ] **4.3 — Verificar manualmente 5 sprites problemáticos**

Abre con explorador `tracker/assets/bestiary_icons/`. Verifica que estos están bien (no rectángulos largos):
- `bigboss_00.png` (Mom's Heart)
- `bigboss_01.png` (Isaac)
- `085_000.png` (Dangle)
- `054_000.png` (Mulligan)
- `019_000.png` (Pin)

Si alguno se ve mal (extracción parcial, hoja en lugar de frame único), añadir entry manual o bajar el sprite manualmente y dejarlo en su lugar.

- [ ] **4.4 — Modificar `tools/build_bestiary.py` para preferir sprites descargados**

En `tools/build_bestiary.py`, justo después de la función `process_sprite`, añadir una función helper que carga desde `tracker/assets/bestiary_icons/<t>_<v>.png` si existe, y solo cae a `process_sprite(path)` (sprite extraído del juego) si no hay versión wiki:

```python
DOWNLOADED_ICONS_DIR = ROOT / "tracker" / "assets" / "bestiary_icons"


def resolve_sprite_for_entity(type_id: int, variant: int, fallback_path: Path) -> str:
    """Prefiere el sprite descargado de la wiki, cae al extraído del juego.

    Devuelve data URI base64.
    """
    wiki_path = DOWNLOADED_ICONS_DIR / f"{type_id:03d}_{variant:03d}.png"
    if wiki_path.exists() and wiki_path.stat().st_size > 100:
        return process_sprite(wiki_path)  # ya recorta + resize si hace falta
    return process_sprite(fallback_path)
```

Y donde el script construye el diccionario de sprites (busca `BESTIARY_SPRITES` o el sitio donde itera entries y llama `process_sprite`), sustituir la llamada por `resolve_sprite_for_entity(t, v, path_actual)`.

> **Localización exacta**: busca en `tools/build_bestiary.py` el sitio donde se construye el dict que luego se vuelca a `bestiary_inline.js` (probablemente cerca del final, en `main()` o equivalente). Si no encuentras el sitio en 2 minutos, lee el archivo entero — el script no es muy largo.

- [ ] **4.5 — Regenerar el catálogo + inline JS**

```bash
python tools/build_bestiary.py
```

Esto regenera `tracker/data/bestiary.py` y `tracker/assets/bestiary_inline.js`.

- [ ] **4.6 — Re-run tests del catálogo (no debe romper nada)**

```bash
pytest tests/test_bestiary_catalog.py tests/test_chapters.py tests/test_big_bosses.py -v
```

- [ ] **4.7 — Commit (en 2 commits si el download es grande)**

```bash
git add tools/download_bestiary_sprites.py tools/build_bestiary.py
git add tracker/assets/bestiary_icons/
git commit -m "feat(bestiary): pipeline para descargar sprites de wiki + preferencia sobre extraídos"

git add tracker/data/bestiary.py tracker/assets/bestiary_inline.js
git commit -m "build: regenerar catálogo y sprites inline con fuente wiki"
```

---

## Task 5: HTML + CSS del `#stats-view`

**Tarea TaskList:** #4
**Files:**
- Modify: `challenges.html` (raíz) — CSS líneas ~1935-2020, HTML ~2164-2195

- [ ] **5.1 — Sustituir CSS del bloque `/* ===== Pestaña Estadísticas ===== */`**

Localizar en `challenges.html` el bloque que empieza con `/* ===== Pestaña Estadísticas ===== */` (línea ~1935) y termina antes de `</style>` (línea ~2020). Reemplazarlo entero por:

```css
    /* ===== Pestaña Estadísticas ===== */
    .hidden { display: none; }

    /* Buscador "Ir al enemigo" — copia exacta de .items-jump-row */
    #stats-view .stats-jump-row {
      display: flex; align-items: center; gap: 8px;
      justify-content: center; margin: 0 0 18px;
      flex-wrap: wrap; font-size: 0.92rem; color: #cfd5e8;
    }
    #stats-view .stats-jump-row label { font-weight: 600; }
    #stats-view .stats-jump-row input[type="text"] {
      background: #16213e; color: #fff;
      border: 1px solid rgba(243,156,18,0.45); border-radius: 6px;
      padding: 5px 10px; width: 280px; max-width: 60vw; font-size: 0.95rem;
    }
    #stats-view .stats-jump-row input[type="text"]:focus {
      outline: none; border-color: #f39c12;
      box-shadow: 0 0 0 2px rgba(243,156,18,0.25);
    }
    #stats-view .stats-jump-row button {
      background: linear-gradient(135deg, #f39c12, #f5b041);
      color: #1a1a2e; border: none; border-radius: 6px;
      padding: 5px 14px; font-weight: 700; cursor: pointer; font-size: 0.9rem;
    }
    #stats-view .stats-jump-row button:hover { filter: brightness(1.08); }
    #stats-view .stats-jump-row .hint { color: #8893a8; font-size: 0.82rem; }

    /* Top — 2 columnas */
    #stats-view .stats-top {
      display: grid; grid-template-columns: 1fr 2fr;
      gap: 1rem; margin-bottom: 1.5rem;
    }
    @media (max-width: 900px) {
      #stats-view .stats-top { grid-template-columns: 1fr; }
    }
    #stats-view .stats-block-title {
      font-size: 0.95rem; color: #cfd5e8; font-weight: 600;
      margin: 0 0 0.6rem; padding-bottom: 0.3rem;
      border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    #stats-view .stats-block-title .ratio { opacity: 0.55; font-weight: 400; font-size: 0.8rem; margin-left: 0.5rem; }

    /* Cards trayectoria */
    #stats-view .stat-card {
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 6px; padding: 0.7rem 0.85rem;
      margin-bottom: 0.5rem;
    }
    #stats-view .stat-card .lab {
      font-size: 0.72rem; opacity: 0.65;
      text-transform: uppercase; letter-spacing: 0.5px;
    }
    #stats-view .stat-card .val {
      font-size: 1.4rem; font-weight: 700; color: #fff; margin-top: 0.2rem;
    }
    #stats-view .stat-card .sub { font-size: 0.7rem; opacity: 0.55; margin-top: 0.2rem; }
    #stats-view .stat-card .bar {
      height: 6px; background: rgba(255,255,255,0.1);
      border-radius: 3px; overflow: hidden; margin-top: 0.4rem;
    }
    #stats-view .stat-card .bar > div {
      height: 100%; background: linear-gradient(90deg, #f39c12, #f5b041);
    }

    /* Big bosses panel */
    #stats-view .bigboss-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(78px, 1fr));
      gap: 6px;
    }
    #stats-view .bigboss {
      background: linear-gradient(135deg, #1f2c4a 0%, #283759 100%);
      border-radius: 6px; padding: 0.5rem 0.3rem;
      display: flex; flex-direction: column; align-items: center;
      box-shadow: inset 0 0 0 1px rgba(243,156,18,0.35);
      cursor: help; transition: transform 0.1s;
      position: relative;
    }
    #stats-view .bigboss:hover { transform: scale(1.05); }
    #stats-view .bigboss.unseen {
      opacity: 0.35; background: #16213e;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06);
    }
    #stats-view .bigboss img {
      width: 48px; height: 48px; object-fit: contain;
      image-rendering: pixelated;
    }
    #stats-view .bigboss .name {
      font-size: 0.7rem; text-align: center; margin-top: 0.3rem;
      white-space: nowrap; overflow: hidden; max-width: 100%;
      text-overflow: ellipsis;
    }
    #stats-view .bigboss .k {
      font-size: 0.78rem; color: #f5b041; font-weight: 700; margin-top: 0.1rem;
    }
    #stats-view .bigboss .k .d {
      color: #e74c3c; font-weight: 500; font-size: 0.7rem; margin-left: 4px;
    }
    #stats-view .bigboss .mark-tag {
      position: absolute; top: 2px; right: 2px;
      background: #6cd66c; color: #1a1a2e;
      font-size: 0.55rem; font-weight: 700;
      padding: 1px 4px; border-radius: 2px;
    }

    /* Toolbar filtros */
    #stats-view .bestiary-toolbar {
      display: flex; gap: 0.4rem; margin: 0.5rem 0 0.8rem;
      align-items: center; flex-wrap: wrap;
    }
    #stats-view .chip {
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.1);
      color: #ddd; font-size: 0.78rem; padding: 4px 12px;
      border-radius: 999px; cursor: pointer;
    }
    #stats-view .chip.active {
      background: #f39c12; border-color: #f39c12;
      color: #1a1a2e; font-weight: 600;
    }
    #stats-view .toolbar-sep {
      width: 1px; height: 18px;
      background: rgba(255,255,255,0.12); margin: 0 4px;
    }
    #stats-view #bestiarySort {
      background: #16213e; color: #fff;
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 6px; padding: 4px 10px; font-size: 0.8rem;
    }

    /* Bloques por capítulo */
    #stats-view .chapter-block { margin-top: 1rem; }
    #stats-view .chapter-header {
      display: flex; align-items: center; gap: 0.6rem;
      font-size: 0.85rem; color: #cfd5e8;
      margin-bottom: 0.4rem; font-weight: 600;
    }
    #stats-view .chapter-header .num {
      background: rgba(243,156,18,0.18); color: #f5b041;
      padding: 2px 8px; border-radius: 4px;
      font-size: 0.7rem; font-weight: 700;
    }
    #stats-view .chapter-header .floors {
      opacity: 0.6; font-weight: 400; font-size: 0.75rem;
    }
    #stats-view .chapter-header .count {
      opacity: 0.55; font-size: 0.75rem; font-weight: 400;
    }
    #stats-view .chapter-header .line {
      flex: 1; height: 1px; background: rgba(255,255,255,0.08);
    }
    #stats-view .chapter-header .prog {
      height: 4px; width: 80px;
      background: rgba(255,255,255,0.08);
      border-radius: 2px; overflow: hidden;
    }
    #stats-view .chapter-header .prog > div { height: 100%; background: #f5b041; }

    /* Enemy grid */
    #stats-view .enemy-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(76px, 1fr));
      gap: 5px;
    }
    #stats-view .enemy {
      background: rgba(255,255,255,0.03);
      border-radius: 4px; padding: 0.4rem 0.2rem;
      display: flex; flex-direction: column; align-items: center;
      cursor: help; position: relative;
    }
    #stats-view .enemy.unseen { opacity: 0.3; }
    #stats-view .enemy img {
      width: 40px; height: 40px; object-fit: contain;
      image-rendering: pixelated;
    }
    #stats-view .enemy .placeholder {
      width: 40px; height: 40px; background: #333;
      display: flex; align-items: center; justify-content: center;
      color: #888; font-size: 1rem;
    }
    #stats-view .enemy .name {
      font-size: 0.65rem; text-align: center; margin-top: 0.25rem;
      white-space: nowrap; overflow: hidden;
      max-width: 100%; text-overflow: ellipsis;
    }
    #stats-view .enemy .stats {
      display: flex; gap: 0.3rem; font-size: 0.6rem; margin-top: 0.15rem;
    }
    #stats-view .enemy .stats .kk { color: #f5b041; font-weight: 700; }
    #stats-view .enemy .stats .dd { color: #e74c3c; }
    #stats-view .enemy .mb-tag {
      position: absolute; top: 2px; right: 2px;
      background: #d4922a; color: #1a1a2e;
      font-size: 0.55rem; font-weight: 700;
      padding: 1px 4px; border-radius: 2px;
    }

    /* Highlight de jump-to */
    #stats-view .enemy.jump-highlight,
    #stats-view .bigboss.jump-highlight {
      box-shadow: 0 0 0 3px rgba(243,156,18,0.95), 0 0 18px 6px rgba(243,156,18,0.55);
      transform: scale(1.15); z-index: 3;
      transition: box-shadow 0.25s, transform 0.25s;
    }

    /* Empty + tooltip */
    #stats-view .bestiary-empty { text-align: center; padding: 2rem; opacity: 0.6; }
    #bestiaryTooltip {
      position: fixed; background: #111; color: #fff;
      padding: 0.5rem 0.7rem; border: 1px solid #444; border-radius: 4px;
      font-size: 0.8rem; z-index: 9999; pointer-events: none; display: none;
    }
```

- [ ] **5.2 — Sustituir el HTML de `#stats-view`**

Localizar en `challenges.html` (línea ~2164) el bloque `<div id="stats-view" class="view"> … </div>` (~líneas 2164-2195). Reemplazar entero por:

```html
  <div id="stats-view" class="view">

    <div class="stats-jump-row">
      <label for="bestiaryJumpInput">Ir al enemigo:</label>
      <input type="text" id="bestiaryJumpInput"
             list="bestiaryNameOptions"
             placeholder="empieza a escribir un nombre"
             autocomplete="off" />
      <datalist id="bestiaryNameOptions"></datalist>
      <button type="button" id="bestiaryJumpBtn">Buscar</button>
      <span class="hint">o pulsa Enter</span>
    </div>

    <div class="stats-top">
      <section>
        <h3 class="stats-block-title">Trayectoria global</h3>
        <div id="statsCards"></div>
      </section>
      <section>
        <h3 class="stats-block-title">
          Bosses derrotados <span class="ratio" id="bossesRatio"></span>
        </h3>
        <div class="bigboss-grid" id="bigBossesGrid"></div>
      </section>
    </div>

    <section>
      <h3 class="stats-block-title">Bestiario</h3>
      <div class="bestiary-toolbar">
        <div id="bestiarySeenFilter" style="display:inline-flex;gap:0.3rem">
          <button class="chip active" data-filter="seen">Vistos</button>
          <button class="chip" data-filter="all">Todos</button>
        </div>
        <span class="toolbar-sep"></span>
        <div id="bestiaryCategoryFilter" style="display:inline-flex;gap:0.3rem">
          <button class="chip active" data-cat="all">Todos</button>
          <button class="chip" data-cat="enemy">Enemigos</button>
          <button class="chip" data-cat="miniboss">Mini-bosses</button>
        </div>
        <span class="toolbar-sep"></span>
        <select id="bestiarySort">
          <option value="chapter">Por capítulo</option>
          <option value="kills_desc">Por kills</option>
          <option value="alpha">Alfabético</option>
        </select>
      </div>
      <div id="bestiaryContainer"></div>
      <p class="bestiary-empty hidden" id="bestiaryEmpty">
        Empieza a jugar para llenar el bestiario.
      </p>
    </section>

  </div>
```

> Nota: la lógica de los chips Vistos/Todos y los chips de categoría reutilizamos el HTML existente con los mismos IDs (`bestiarySeenFilter`, `bestiarySeenFilter`). Eliminamos el chip "Bosses" del filtro de categoría porque los big bosses ya están arriba en su panel propio.

- [ ] **5.3 — Smoke test visual del CSS/HTML**

```bash
# Abre el HTML directamente en navegador para confirmar que no rompió nada de las otras pestañas
start challenges.html  # Windows
```

Verifica visualmente:
- Las otras pestañas (Desafíos, Ítems, Logros…) siguen funcionando como antes.
- La pestaña Estadísticas se ve "vacía" (sin JS aún rellenándola) PERO renderiza el buscador, los dos títulos de sección y la toolbar de chips sin emojis.

- [ ] **5.4 — Commit**

```bash
git add challenges.html
git commit -m "feat(stats): nuevo HTML+CSS para la pestaña Estadísticas (sin emojis, paleta naranja)"
```

---

## Task 6: JS de renderizado

**Tarea TaskList:** #5
**Depende de:** Task 3 (stats_state schema) y Task 5 (markup nuevo)
**Files:**
- Modify: `challenges.html` bloque `/* ====== Pestaña Estadísticas ====== */` (líneas ~6104-6298)

- [ ] **6.1 — Reemplazar el bloque JS entero**

Localizar `/* ====== Pestaña Estadísticas ====== */` (línea ~6104) y todo lo que sigue hasta `bindBestiaryControls();` (línea ~6286, inclusive). Sustituir por:

```js
  /* ====== Pestaña Estadísticas ====== */

  const BESTIARY_FILTER_STATE = {
    filter: "seen", category: "all", sort: "chapter",
  };

  const CHAPTER_LABELS = {
    1: "Basement · Cellar · Burning Basement · Downpour · Dross",
    2: "Caves · Catacombs · Flooded Caves · Mines · Ashpit",
    3: "Depths · Necropolis · Dank Depths · Mausoleum · Gehenna",
    4: "Womb · Utero · Scarred Womb · Corpse",
    5: "Sheol · Cathedral",
    6: "Dark Room · Chest",
    7: "Blue Womb · Void · Home",
    "extra": "Otros",
  };

  let _bestiaryTooltipEl = null;

  function _loadStatsStateOrNull() {
    if (window._statsState) return window._statsState;
    try {
      const raw = localStorage.getItem("isaac_tracker_state") || localStorage.getItem("state");
      if (raw) {
        const obj = JSON.parse(raw);
        if (obj && obj.stats_state) return obj.stats_state;
      }
    } catch {}
    if (window.__APP_STATE__ && window.__APP_STATE__.stats_state) {
      return window.__APP_STATE__.stats_state;
    }
    return null;
  }

  function renderStatsCards(stats) {
    const el = document.getElementById("statsCards");
    if (!el) return;
    el.innerHTML = "";
    const skipKeys = new Set(["bosses_defeated"]);  // se muestra como ratio del header
    for (const g of stats.globals) {
      if (skipKeys.has(g.key)) continue;
      const card = document.createElement("div");
      card.className = "stat-card";
      const valText = g.max != null
        ? `${g.value.toLocaleString("es-ES")} / ${g.max.toLocaleString("es-ES")}`
        : g.value.toLocaleString("es-ES");
      const subText = (g.max != null)
        ? `<div class="sub">faltan ${Math.max(0, g.max - g.value)}</div>
           <div class="bar"><div style="width:${g.max ? Math.round(100*g.value/g.max) : 0}%"></div></div>`
        : "";
      card.innerHTML = `
        <div class="lab">${g.label_es}</div>
        <div class="val">${valText}</div>
        ${subText}
      `;
      el.appendChild(card);
    }
  }

  function renderBigBossesPanel(stats) {
    const grid = document.getElementById("bigBossesGrid");
    const ratio = document.getElementById("bossesRatio");
    if (!grid) return;
    grid.innerHTML = "";
    let defeated = 0;
    const sprites = (window.BESTIARY_SPRITES) || {};
    for (const b of stats.big_bosses) {
      if (b.seen) defeated++;
      const cell = document.createElement("div");
      cell.className = "bigboss" + (b.seen ? "" : " unseen");
      cell.dataset.bigbossIdx = b.idx;
      const spriteKey = `bigboss_${String(b.idx).padStart(2, "0")}`;
      const src = sprites[spriteKey] || b.sprite_url || "";
      const img = src
        ? `<img src="${src}" alt="${b.name_en}">`
        : `<div class="placeholder">?</div>`;
      const k = b.kills == null ? "—" : `×${b.kills.toLocaleString("es-ES")}`;
      const d = (b.deaths == null || b.deaths === 0) ? "" : `<span class="d">/${b.deaths}</span>`;
      const markTag = b.mark_completed ? '<span class="mark-tag">✓</span>' : '';
      cell.innerHTML = `
        ${markTag}
        ${img}
        <span class="name" title="${b.name_es}">${b.name_es}</span>
        <span class="k">${k}${d}</span>
      `;
      cell.addEventListener("mouseenter", ev => showBigBossTooltip(ev, b));
      cell.addEventListener("mousemove", ev => positionBestiaryTooltip(ev));
      cell.addEventListener("mouseleave", hideBestiaryTooltip);
      grid.appendChild(cell);
    }
    if (ratio) ratio.textContent = `${defeated} / ${stats.big_bosses.length}`;
  }

  function _filterAndSortBestiary(stats) {
    let items = stats.bestiary.filter(e => {
      if (BESTIARY_FILTER_STATE.filter === "seen" && !e.seen) return false;
      if (BESTIARY_FILTER_STATE.category !== "all"
          && e.category !== BESTIARY_FILTER_STATE.category) return false;
      return true;
    });
    const sorters = {
      kills_desc: (a, b) => b.kills - a.kills || a.name_es.localeCompare(b.name_es),
      alpha:      (a, b) => a.name_es.localeCompare(b.name_es),
      chapter:    (a, b) => {
        const ord = ch => (ch === "extra" ? 99 : ch);
        return (ord(a.chapter) - ord(b.chapter)) || (b.kills - a.kills);
      },
    };
    items.sort(sorters[BESTIARY_FILTER_STATE.sort] || sorters.chapter);
    return items;
  }

  function _renderEnemyCell(e) {
    const cell = document.createElement("div");
    cell.className = "enemy" + (e.seen ? "" : " unseen");
    cell.dataset.spriteId = e.sprite_id;
    const sprites = (window.BESTIARY_SPRITES) || {};
    const src = sprites[e.sprite_id];
    const img = src
      ? `<img src="${src}" alt="${e.name_en}">`
      : `<div class="placeholder">?</div>`;
    const mb = e.category === "miniboss" ? '<span class="mb-tag">MB</span>' : '';
    const kills = e.seen ? `<span class="kk">×${e.kills.toLocaleString("es-ES")}</span>` : `<span class="kk">×?</span>`;
    const deaths = (e.seen && e.deaths > 0) ? `<span class="dd">/${e.deaths}</span>` : '';
    cell.innerHTML = `
      ${mb}
      ${img}
      <span class="name" title="${e.name_es}">${e.name_es}</span>
      <span class="stats">${kills}${deaths}</span>
    `;
    cell.addEventListener("mouseenter", ev => showBestiaryTooltip(ev, e));
    cell.addEventListener("mousemove", ev => positionBestiaryTooltip(ev));
    cell.addEventListener("mouseleave", hideBestiaryTooltip);
    return cell;
  }

  function renderBestiaryContainer(stats) {
    const container = document.getElementById("bestiaryContainer");
    const empty = document.getElementById("bestiaryEmpty");
    if (!container) return;
    container.innerHTML = "";

    const items = _filterAndSortBestiary(stats);
    if (items.length === 0) {
      empty && empty.classList.remove("hidden");
      return;
    }
    empty && empty.classList.add("hidden");

    if (BESTIARY_FILTER_STATE.sort !== "chapter") {
      const grid = document.createElement("div");
      grid.className = "enemy-grid";
      for (const e of items) grid.appendChild(_renderEnemyCell(e));
      container.appendChild(grid);
      return;
    }

    // Agrupar por capítulo
    const groups = {};
    for (const e of items) {
      const ch = e.chapter;
      if (!groups[ch]) groups[ch] = [];
      groups[ch].push(e);
    }
    // Totales por capítulo SOBRE EL CATÁLOGO COMPLETO (para "X/Y" honesto, no filtrado)
    const totalsByChapter = {};
    for (const e of stats.bestiary) {
      const ch = e.chapter;
      if (!totalsByChapter[ch]) totalsByChapter[ch] = { total: 0, seen: 0 };
      totalsByChapter[ch].total++;
      if (e.seen) totalsByChapter[ch].seen++;
    }

    const order = [1, 2, 3, 4, 5, 6, 7, "extra"];
    for (const ch of order) {
      if (!groups[ch]) continue;
      const block = document.createElement("div");
      block.className = "chapter-block";
      const t = totalsByChapter[ch] || { total: 0, seen: 0 };
      const pct = t.total ? Math.round(100 * t.seen / t.total) : 0;
      const numLabel = (ch === "extra") ? "EXTRA" : `CAP ${ch}`;
      block.innerHTML = `
        <div class="chapter-header">
          <span class="num">${numLabel}</span>
          <span class="floors">${CHAPTER_LABELS[ch] || ""}</span>
          <span class="count">${t.seen} / ${t.total}</span>
          <span class="line"></span>
          <div class="prog"><div style="width:${pct}%"></div></div>
        </div>
        <div class="enemy-grid"></div>
      `;
      const grid = block.querySelector(".enemy-grid");
      for (const e of groups[ch]) grid.appendChild(_renderEnemyCell(e));
      container.appendChild(block);
    }
  }

  function ensureBestiaryTooltip() {
    if (_bestiaryTooltipEl) return _bestiaryTooltipEl;
    _bestiaryTooltipEl = document.createElement("div");
    _bestiaryTooltipEl.id = "bestiaryTooltip";
    document.body.appendChild(_bestiaryTooltipEl);
    return _bestiaryTooltipEl;
  }

  function showBestiaryTooltip(ev, e) {
    const el = ensureBestiaryTooltip();
    const catLabel = {enemy: "", miniboss: "(Mini-boss)", boss: "(Boss)"}[e.category] || "";
    const rows = [`<strong>${e.name_es}</strong> ${catLabel}`];
    if (e.kills > 0)      rows.push(`Kills: ${e.kills.toLocaleString("es-ES")}`);
    if (e.deaths > 0)     rows.push(`Te ha matado: ${e.deaths.toLocaleString("es-ES")}`);
    if (e.hits > 0)       rows.push(`Hits recibidos: ${e.hits.toLocaleString("es-ES")}`);
    if (e.encounters > 0) rows.push(`Encuentros: ${e.encounters.toLocaleString("es-ES")}`);
    if (rows.length === 1) rows.push("<em>Sin datos en el save</em>");
    el.innerHTML = rows.join("<br>");
    el.style.display = "block";
    positionBestiaryTooltip(ev);
  }

  function showBigBossTooltip(ev, b) {
    const el = ensureBestiaryTooltip();
    const rows = [`<strong>${b.name_es}</strong>`];
    if (b.kind === "event")          rows.push("<em>Evento del juego</em>");
    else if (b.kind === "transformation") rows.push("<em>Transformación</em>");
    if (b.kills != null && b.kills > 0)         rows.push(`Kills: ${b.kills.toLocaleString("es-ES")}`);
    if (b.deaths != null && b.deaths > 0)       rows.push(`Te ha matado: ${b.deaths.toLocaleString("es-ES")}`);
    if (b.hits != null && b.hits > 0)           rows.push(`Hits recibidos: ${b.hits.toLocaleString("es-ES")}`);
    if (b.encounters != null && b.encounters > 0) rows.push(`Encuentros: ${b.encounters.toLocaleString("es-ES")}`);
    if (b.mark_completed) rows.push("✓ Completado por algún personaje");
    if (!b.seen) rows.push("<em>Aún no derrotado</em>");
    el.innerHTML = rows.join("<br>");
    el.style.display = "block";
    positionBestiaryTooltip(ev);
  }

  function positionBestiaryTooltip(ev) {
    if (!_bestiaryTooltipEl) return;
    _bestiaryTooltipEl.style.left = (ev.clientX + 12) + "px";
    _bestiaryTooltipEl.style.top  = (ev.clientY + 12) + "px";
  }
  function hideBestiaryTooltip() {
    if (_bestiaryTooltipEl) _bestiaryTooltipEl.style.display = "none";
  }

  function populateBestiaryDatalist(stats) {
    const dl = document.getElementById("bestiaryNameOptions");
    if (!dl) return;
    dl.innerHTML = "";
    const all = [...stats.big_bosses, ...stats.bestiary];
    for (const e of all) {
      const opt = document.createElement("option");
      opt.value = e.name_es;
      dl.appendChild(opt);
    }
  }

  function _findAndHighlight(name) {
    const target = String(name || "").trim().toLowerCase();
    if (!target) return false;
    const candidates = document.querySelectorAll("#stats-view .enemy, #stats-view .bigboss");
    let found = null;
    candidates.forEach(c => {
      const lab = (c.querySelector(".name")?.textContent || "").trim().toLowerCase();
      if (!found && lab === target) found = c;
      else if (!found && lab.includes(target)) found = c;
    });
    if (!found) return false;
    found.scrollIntoView({behavior: "smooth", block: "center"});
    found.classList.add("jump-highlight");
    setTimeout(() => found.classList.remove("jump-highlight"), 1800);
    return true;
  }

  function bindBestiaryJumpTo() {
    const input = document.getElementById("bestiaryJumpInput");
    const btn = document.getElementById("bestiaryJumpBtn");
    if (input && !input.dataset.bound) {
      input.dataset.bound = "1";
      input.addEventListener("keydown", ev => {
        if (ev.key === "Enter") {
          ev.preventDefault();
          _findAndHighlight(input.value);
        }
      });
    }
    if (btn && !btn.dataset.bound) {
      btn.dataset.bound = "1";
      btn.addEventListener("click", () => _findAndHighlight(input.value));
    }
  }

  function renderStatsTab() {
    const stats = _loadStatsStateOrNull();
    if (!stats) return;
    renderStatsCards(stats);
    renderBigBossesPanel(stats);
    renderBestiaryContainer(stats);
    populateBestiaryDatalist(stats);
  }

  function bindBestiaryControls() {
    const f = document.getElementById("bestiarySeenFilter");
    if (f && !f.dataset.bound) {
      f.dataset.bound = "1";
      f.querySelectorAll(".chip").forEach(b => {
        b.addEventListener("click", () => {
          f.querySelectorAll(".chip").forEach(x => x.classList.remove("active"));
          b.classList.add("active");
          BESTIARY_FILTER_STATE.filter = b.dataset.filter;
          renderStatsTab();
        });
      });
    }
    const c = document.getElementById("bestiaryCategoryFilter");
    if (c && !c.dataset.bound) {
      c.dataset.bound = "1";
      c.querySelectorAll(".chip").forEach(b => {
        b.addEventListener("click", () => {
          c.querySelectorAll(".chip").forEach(x => x.classList.remove("active"));
          b.classList.add("active");
          BESTIARY_FILTER_STATE.category = b.dataset.cat;
          renderStatsTab();
        });
      });
    }
    const o = document.getElementById("bestiarySort");
    if (o && !o.dataset.bound) {
      o.dataset.bound = "1";
      o.addEventListener("change", ev => {
        BESTIARY_FILTER_STATE.sort = ev.target.value;
        renderStatsTab();
      });
    }
    bindBestiaryJumpTo();
  }
  bindBestiaryControls();
```

- [ ] **6.2 — Confirma que NO queda nada de `STATS_ICONS` en el archivo**

```bash
grep -n "STATS_ICONS" challenges.html
```

Expected: nada. Si aparece, borrar la línea correspondiente.

- [ ] **6.3 — Smoke test: abre el HTML en navegador con un state mockeado**

Opción mínima — crear `/tmp` html que llame `renderStatsTab()` con un stats_state inventado. Más fácil: meterle al localStorage el state real:

```js
// Abre devtools en challenges.html, console:
localStorage.setItem("isaac_tracker_state", JSON.stringify({
  stats_state: {
    globals: [
      {key:"total_kills", label_es:"Enemigos eliminados", value: 11003, icon:"skull"},
      {key:"total_deaths_by", label_es:"Te han matado", value: 387320, icon:"tombstone"},
      {key:"total_hits", label_es:"Golpes recibidos", value: 404675, icon:"heart_broken"},
      {key:"unique_seen", label_es:"Bestiario", value: 246, max: 282, icon:"eye"},
      {key:"bosses_defeated", label_es:"Bosses derrotados", value: 8, max: 13, icon:"boss"},
    ],
    big_bosses: [
      {idx:0, name_es:"Corazón de Mamá", name_en:"Mom's Heart", sprite_url:"", kind:"boss",
       kills:84, deaths:12, hits:50, encounters:90, seen:true, mark_completed:true},
      // … resto rellenable con seen:false
    ],
    bestiary: [
      {type:85, variant:0, name_es:"Dangle", name_en:"Dangle", category:"boss", chapter:3,
       kills:1066, deaths:0, hits:5, encounters:80, sprite_id:"085.000", seen:true},
    ],
  },
}));
location.reload();
```

Verifica que: trayectoria muestra 4 cards, panel de bosses tiene la celda de Mom's Heart con sprite, bestiario muestra Dangle bajo "CAP 3". El buscador autocompleta nombres. Pulsar Enter en "Dangle" hace scroll + highlight.

- [ ] **6.4 — Commit**

```bash
git add challenges.html
git commit -m "feat(stats): nuevo JS de renderizado (big bosses panel, bestiario por capítulo, jump-to)"
```

---

## Task 7: Sync + rebuild del .exe + verificación E2E

**Tarea TaskList:** #6
**Depende de:** Tasks 4, 5, 6
**Files:**
- Modify: `tracker/assets/challenges.html` (auto-sync vía `build_nuitka.py`)
- Build: `dist/IsaacTracker.exe`

- [ ] **7.1 — Verifica que `build_nuitka.py` sincroniza automáticamente**

`build_nuitka.py:23-40` ya tiene `_sync_root_assets()`. Solo lo confirmamos:

```bash
grep -n "challenges.html" build_nuitka.py
```

Expected: línea ~26 con `(ROOT / "challenges.html", ASSETS / "challenges.html")`.

- [ ] **7.2 — Lanzar build**

```bash
python build_nuitka.py
```

Esto tarda 3-10 minutos. El binary acaba en `dist/IsaacTracker.exe`.

- [ ] **7.3 — Test E2E manual: abrir `dist/IsaacTracker.exe`**

Doble click. Verifica:

1. La app abre y lee el save real.
2. Pestaña **Estadísticas**:
   - [ ] **Trayectoria global**: 4 cards a la izquierda (kills/deaths/hits/bestiario).
   - [ ] La card "Bestiario" muestra `N / M` con **N ≤ M** (bug 342/282 corregido).
   - [ ] **Panel "Bosses derrotados X / 13"** a la derecha con los 13 big bosses. Los seen tienen sprite real de wiki, los unseen están apagados.
   - [ ] **Bestiario abajo agrupado por capítulo** (CAP 1, CAP 2, …, EXTRA si aplica). Cada cabecera con `seen/total` y barrita naranja.
   - [ ] Sprites problemáticos del bug original (**Dangle, Mulligan, Pin, Scolex**) ya NO se ven cortados.
   - [ ] Cada celda muestra kills + deaths en colores (naranja/rojo).
   - [ ] **Tooltip al hover** muestra kills/deaths/hits/encounters como antes.
   - [ ] **Buscador**: escribir "Dangle" → autocomplete → Enter → scroll a la celda + highlight naranja brillante 1.5 seg.
   - [ ] **Filtros**: cambiar entre Vistos / Todos. Cambiar entre Enemigos / Mini-bosses. Cambiar entre los tres `<option>` del sort. Todo responde sin pestañear.
   - [ ] **Ningún emoji** (💀, 🪦, 💔, 👁, 🏠, …) visible en la pestaña.
3. Otras pestañas (Desafíos, Personajes, Logros, Ítems, Trinkets, Cartas, Donaciones): **siguen funcionando**, no se han roto los textos ni el layout.

- [ ] **7.4 — Si algo falla en 7.3, volver al task correspondiente y corregir**

Bugs típicos esperados:
- Algún sprite de wiki no se descargó: revisar `tools/bestiary_sprite_review.log` y bajarlos manualmente o ajustar `candidate_urls`.
- `mark_completed` siempre False: revisar la lectura de `parsed.character_marks` en `_build_stats_state` (Task 3, nota).
- Bestiario aparece pero sin agrupar por capítulo: probablemente `chapters.resolve_chapter` devuelve "extra" para todo → revisar la tabla.

- [ ] **7.5 — Commit final**

```bash
# Sync ya hecha por build_nuitka.py; este commit pilla el sync.
git add tracker/assets/challenges.html
git commit -m "build: sync de challenges.html → tracker/assets para el bundle"
```

- [ ] **7.6 — Marcar todas las tasks como completed en TaskList**

```
TaskUpdate {taskId: 1, status: completed}
TaskUpdate {taskId: 2, status: completed}
TaskUpdate {taskId: 3, status: completed}
TaskUpdate {taskId: 4, status: completed}
TaskUpdate {taskId: 5, status: completed}
TaskUpdate {taskId: 6, status: completed}
```

---

## Notas finales

- **DRY**: el patrón de buscador-con-datalist se duplica con `itemJumpInput`/`trinketJumpInput`/`cardJumpInput`. Aceptable porque cada uno tiene matchers de nombre diferentes. Si en el futuro tenemos un quinto buscador, refactor.
- **YAGNI**: no añadir highlights de "tu peor verdugo" / "tu top kill" — descartado en brainstorming por el usuario al elegir la opción C.
- **Frecuencia de commits**: 8-9 commits en total. Si vas a tirar de subagentes paralelos, cada task es 1 unidad de trabajo independiente.
- **Compatibilidad backwards**: el campo `key` se preserva en `globals` para no romper `tests/test_stats_state.py` existentes y posibles consumers externos del state.
