# Pestaña "Estadísticas" (Bestiario + Stats Globales) — Plan de Implementación

> **Para workers agénticos:** REQUERIDO usar `superpowers:subagent-driven-development` (si hay subagentes) o `superpowers:executing-plans`. Los pasos usan checkboxes (`- [ ]`).

**Goal:** Añadir una pestaña "Estadísticas" que muestre kills por enemigo (bestiario con sprites) y stats globales agregados (kills/deaths/hits totales + donaciones), con base para añadir más contadores del chunk 2 en commits posteriores.

**Architecture:**
- **Backend Python**: nuevo decoder del chunk 11 en `tracker/save_parser.py`, catálogo `tracker/data/bestiary.py`, registro `tracker/data/stats_counters.py`, builder `_build_stats_state` en `state_mapper.py`.
- **Assets**: pipeline `tools/build_bestiary.py` que descarga sprites de `Derugon/TBoIR-resources`, los cropea al primer frame y genera `tracker/data/bestiary.py` + `tracker/assets/bestiary_inline.js`.
- **Frontend**: nueva pestaña `data-view="stats"` en `challenges.html` con HTML/CSS/JS para cards de stats y grid de enemigos.

**Tech Stack:** Python 3.11+, Pillow (crop/resize de sprites), pytest, vanilla JS, PyInstaller (.exe rebuild).

**Spec:** `docs/superpowers/specs/2026-05-17-bestiary-stats-tab-design.md`.

**Sub-skills relevantes durante ejecución:**
- `superpowers:test-driven-development` — orden test-first en toda tarea de parser/state.
- `superpowers:verification-before-completion` — correr tests + smoke-test del .exe antes de declarar completa cada fase.

---

## Mapa de archivos

**Crear:**
- `tracker/data/bestiary.py` — catálogo `(type, variant) → metadata` (generado por `tools/build_bestiary.py`).
- `tracker/data/stats_counters.py` — registro de índices confirmados del chunk 2.
- `tracker/assets/bestiary_inline.js` — sprites inline (generado).
- `tools/build_bestiary.py` — pipeline de extracción/crop/optimización.
- `tools/extract_bestiary_assets.py` — script auxiliar que descarga el árbol de sprites.
- `tools/diff_counters.py` — utilidad para identificar nuevos índices del chunk 2 (Fase D).
- `tests/test_bestiary_parser.py` — tests del decoder del chunk 11.
- `tests/test_bestiary_catalog.py` — tests del catálogo generado.
- `tests/test_stats_state.py` — tests del `_build_stats_state`.

**Modificar:**
- `tracker/save_parser.py` — añadir constantes del chunk 11, `_extract_bestiary`, campos en `ParsedSave`, integrar en `parse_save`.
- `tracker/state_mapper.py` — `_build_stats_state` + clave `stats_state` en `build_localstorage_state`.
- `tests/test_save_parser.py` — un test extra que valide que `ParsedSave` lleva los dicts del bestiario poblados desde el fixture real.
- `challenges.html` — botón de pestaña, contenedor `#stats-view`, CSS scoped, script de render.
- `build.spec` — añadir `tracker/assets/bestiary_inline.js` al bundle (verificar si ya cubre `tracker/assets/*`).

---

## Fase A — Parser del chunk 11 (bestiario)

### Task A1: Tests + decoder del chunk 11 desconectado

Construye el decoder como función pura (sin meterlo aún en `parse_save`) y validalo contra el fixture. Esta task descubre y fija la fórmula del packed entity id antes de comprometer nada.

**Files:**
- Create: `tests/test_bestiary_parser.py`
- Modify: `tracker/save_parser.py` (añadir `_extract_bestiary` privado)

- [ ] **Step 1: Test exploratorio de smoke**

Escribir `tests/test_bestiary_parser.py` con un primer test que solo verifica que el chunk 11 se puede leer del fixture y tiene 4 sub-records:

```python
from pathlib import Path
import struct

from tracker.save_parser import _extract_chunks


FIXTURE = Path(__file__).parent / "fixtures" / "sample_save_repentance_plus.dat"
CHUNK_BESTIARY = 11


def _read_bestiary_chunk_body(path):
    """Variante de _extract_chunks que NO se detiene en el chunk 10.
    Los primeros 10 chunks vienen como hoy; el 11 ocupa el resto del fichero
    menos los 4 bytes de checksum final.
    """
    data = path.read_bytes()
    from tracker.save_parser import _HEADER_SIZE, _CHUNK_HEADER_SIZE, _ENTRY_SIZES
    off = _HEADER_SIZE
    for i in range(10):
        chunk_type, _len, count = struct.unpack_from("<iii", data, off)
        body_start = off + _CHUNK_HEADER_SIZE
        body_len = count * _ENTRY_SIZES[i]
        off = body_start + body_len
    # chunk 11 header
    chunk_type, _len, count = struct.unpack_from("<iii", data, off)
    assert chunk_type == CHUNK_BESTIARY
    body_start = off + _CHUNK_HEADER_SIZE
    body_end = len(data) - 4  # menos AfterbirthChecksum
    return count, data[body_start:body_end]


def test_bestiary_chunk_has_four_subrecords():
    count, body = _read_bestiary_chunk_body(FIXTURE)
    assert count == 4
    assert len(body) > 0
```

- [ ] **Step 2: Correr test, debe pasar**

```
pytest tests/test_bestiary_parser.py::test_bestiary_chunk_has_four_subrecords -v
```

Expected: PASS. Si falla con `chunk_type != 11`, hay un problema en cómo asumimos el offset del chunk 11 — investigar antes de seguir.

- [ ] **Step 3: Test que itera los 4 sub-records y valida tipos**

```python
def test_bestiary_subrecords_have_known_types():
    _, body = _read_bestiary_chunk_body(FIXTURE)
    types_found = []
    off = 0
    for _ in range(4):
        rec_type, byte_len = struct.unpack_from("<ii", body, off)
        types_found.append(rec_type)
        off += 8 + byte_len
    # Per Kaitai schema: 1=hits, 2=deaths, 3=kills, 4=encounters
    assert sorted(types_found) == [1, 2, 3, 4]
```

Correr: `pytest tests/test_bestiary_parser.py::test_bestiary_subrecords_have_known_types -v` → PASS.

Si los tipos no son 1..4, dumpear sus valores reales en el `assert` y continuar el plan asumiendo los enteros descubiertos. Documentar la realidad en `tracker/PARSER_AUDIT.md` antes de avanzar.

- [ ] **Step 4: Helper de decodificación de entries (sin asumir fórmula del id aún)**

Implementar en `tracker/save_parser.py` (zona privada, después de `_extract_items_seen`):

```python
_BESTIARY_HITS = 1
_BESTIARY_DEATHS = 2
_BESTIARY_KILLS = 3
_BESTIARY_ENCOUNTERS = 4


def _extract_bestiary(data: bytes, after_chunk10_off: int, file_end: int) -> dict[int, dict[int, int]]:
    """Decodifica el chunk 11 a {record_type: {packed_entity_id: value}}.

    `after_chunk10_off` es el offset donde acaba el chunk 10 (= empieza la
    cabecera del chunk 11). `file_end` es len(data) menos el AfterbirthChecksum
    (4 bytes finales). El packed_entity_id se devuelve sin decodificar; la
    decodificación a (type, variant) la hace el consumidor.
    """
    import struct
    out: dict[int, dict[int, int]] = {1: {}, 2: {}, 3: {}, 4: {}}
    if after_chunk10_off + 12 > file_end:
        return out
    _chunk_type, _len, count = struct.unpack_from("<iii", data, after_chunk10_off)
    if count != 4:
        return out
    off = after_chunk10_off + 12  # tras la cabecera del chunk 11
    for _ in range(count):
        if off + 8 > file_end:
            break
        rec_type, byte_len = struct.unpack_from("<ii", data, off)
        off += 8
        body_end = off + byte_len
        if body_end > file_end or rec_type not in out:
            off = body_end
            continue
        n_entries = byte_len // 8
        for i in range(n_entries):
            entry_off = off + i * 8
            entity, value = struct.unpack_from("<ii", data, entry_off)
            out[rec_type][entity] = value
        off = body_end
    return out
```

- [ ] **Step 5: Test que el helper devuelve dicts no vacíos para kills/encounters**

```python
def test_extract_bestiary_returns_nonempty_dicts():
    from tracker.save_parser import (
        _extract_bestiary, _HEADER_SIZE, _CHUNK_HEADER_SIZE, _ENTRY_SIZES,
    )
    data = FIXTURE.read_bytes()
    off = _HEADER_SIZE
    for i in range(10):
        _t, _l, count = struct.unpack_from("<iii", data, off)
        off = off + _CHUNK_HEADER_SIZE + count * _ENTRY_SIZES[i]
    result = _extract_bestiary(data, off, len(data) - 4)
    assert len(result[3]) > 0, "kills dict must be non-empty in real save"
    assert len(result[4]) > 0, "encounters dict must be non-empty in real save"
    # sanity: all values >= 0
    for d in result.values():
        for v in d.values():
            assert v >= 0
```

Correr: `pytest tests/test_bestiary_parser.py -v` → 3 PASS.

- [ ] **Step 6: Validar fórmula del packed entity id**

Añade test que valida la hipótesis `entity = type * 1000 + variant`:

```python
def test_packed_entity_ids_match_type_times_1000():
    """Hipótesis: entity = type * 1000 + variant.
    Validación: el filename de sprites Derugon usa NNN.MMM_name.png; si la
    hipótesis es correcta, los packed ids del fixture deben descomponerse a
    (type, variant) donde type 0..1000 razonable y variant 0..999 razonable.
    """
    from tracker.save_parser import (
        _extract_bestiary, _HEADER_SIZE, _CHUNK_HEADER_SIZE, _ENTRY_SIZES,
    )
    data = FIXTURE.read_bytes()
    off = _HEADER_SIZE
    for i in range(10):
        _t, _l, count = struct.unpack_from("<iii", data, off)
        off = off + _CHUNK_HEADER_SIZE + count * _ENTRY_SIZES[i]
    kills = _extract_bestiary(data, off, len(data) - 4)[3]

    # Type IDs reales del juego están entre 10 (Fly) y ~950 (Beast).
    # Variantes raramente pasan de 200. Esta validación es laxa pero detecta
    # un packing distinto (ej. type:u2|variant:u2 daría ids enormes).
    valid = 0
    for packed in kills:
        type_ = packed // 1000
        variant = packed % 1000
        if 1 <= type_ <= 999 and 0 <= variant <= 999:
            valid += 1
    assert valid >= len(kills) * 0.95, (
        f"At least 95% of packed ids must decode to plausible (type, variant). "
        f"Got {valid}/{len(kills)}. Sample packed ids: {list(kills)[:10]}"
    )
```

Correr: `pytest tests/test_bestiary_parser.py::test_packed_entity_ids_match_type_times_1000 -v` → debe PASS.

**Si falla:**
- Volcar los 10 primeros packed ids al mensaje del `assert` y revisar a ojo.
- Probar alternativas: `(type:u2, variant:u2)` con `struct.unpack("<HH", struct.pack("<i", packed))`, o `type * 10000 + variant`.
- Cuando una fórmula funcione, ajustar el helper de decodificación que use el catálogo (Task B2) y este test para reflejarla.

- [ ] **Step 7: Commit**

```bash
git add tests/test_bestiary_parser.py tracker/save_parser.py
git commit -m "feat(parser): decoder del chunk 11 (bestiario)"
```

---

### Task A2: Integrar bestiario en `parse_save` + `ParsedSave`

Conecta el helper de Task A1 al flujo principal y expón los 4 dicts en el dataclass público.

**Files:**
- Modify: `tracker/save_parser.py` (campos en `ParsedSave`, llamada en `parse_save`, ajustar `_extract_chunks` para devolver también offset post-chunk-10)
- Modify: `tests/test_save_parser.py` (extender con assert de campos nuevos)

- [ ] **Step 1: Refactor mínimo de `_extract_chunks` para exponer el offset post-chunk-10**

Hoy `_extract_chunks` solo devuelve `dict[int, bytes]`. Cambiarlo para devolver `tuple[dict[int, bytes], int]` donde el segundo elemento es `off` al terminar el bucle (= inicio del chunk 11):

```python
def _extract_chunks(data: bytes, path: Path) -> tuple[dict[int, bytes], int]:
    chunks: dict[int, bytes] = {}
    off = _HEADER_SIZE
    for i in range(10):
        # ... idéntico al actual ...
    # validaciones de chunks requeridos como hoy
    return chunks, off
```

Actualizar la llamada en `parse_save`:

```python
chunks, post_chunk10_off = _extract_chunks(data, path)
```

- [ ] **Step 2: Añadir campos al dataclass `ParsedSave`**

```python
bestiary_kills:       dict[int, int] = field(default_factory=dict)
bestiary_deaths:      dict[int, int] = field(default_factory=dict)
bestiary_hits:        dict[int, int] = field(default_factory=dict)
bestiary_encounters:  dict[int, int] = field(default_factory=dict)
```

Los keys son **packed entity ids** (`int`), no `(type, variant)` aún. La descomposición se hace en `state_mapper.py` usando la fórmula validada en A1 Step 6. Mantener packed simplifica el dataclass y deja la fórmula localizada.

Actualizar el docstring de `ParsedSave` describiendo los 4 campos nuevos.

- [ ] **Step 3: Llamar al decoder en `parse_save`**

```python
bestiary_raw = _extract_bestiary(data, post_chunk10_off, len(data) - 4)

return ParsedSave(
    # ... resto igual ...
    bestiary_hits=bestiary_raw[_BESTIARY_HITS],
    bestiary_deaths=bestiary_raw[_BESTIARY_DEATHS],
    bestiary_kills=bestiary_raw[_BESTIARY_KILLS],
    bestiary_encounters=bestiary_raw[_BESTIARY_ENCOUNTERS],
)
```

- [ ] **Step 4: Test de integración en `test_save_parser.py`**

```python
def test_parser_extracts_bestiary_counts(sample_save_path):
    parsed = parse_save(sample_save_path)
    assert isinstance(parsed.bestiary_kills, dict)
    assert isinstance(parsed.bestiary_encounters, dict)
    # Save real → debe haber al menos un enemigo encontrado.
    assert len(parsed.bestiary_encounters) > 0
    # Sanity: si has matado a X enemigos, deberías haberlos encontrado.
    assert set(parsed.bestiary_kills.keys()).issubset(parsed.bestiary_encounters.keys())
```

- [ ] **Step 5: Correr toda la suite del parser**

```
pytest tests/test_save_parser.py tests/test_bestiary_parser.py -v
```

Expected: todo PASS, ningún test regresado.

- [ ] **Step 6: Commit**

```bash
git add tracker/save_parser.py tests/test_save_parser.py
git commit -m "feat(parser): exponer bestiario en ParsedSave"
```

---

## Fase B — Catálogo y sprites

### Task B1: Script `tools/extract_bestiary_assets.py` (descarga + lista)

Descarga el subárbol `resources-dlc3/gfx/monsters/` de `Derugon/TBoIR-resources` a `tools/_bestiary_raw/` y genera un manifest JSON con `(type, variant, name_en, suffix, source_path)` para cada PNG.

**Files:**
- Create: `tools/extract_bestiary_assets.py`
- Create: `tools/_bestiary_raw/MANIFEST.json` (artefacto, gitignored)

- [ ] **Step 1: Esqueleto del script**

```python
"""Descarga el árbol de sprites de bestiario de Derugon/TBoIR-resources.

Uso: `python tools/extract_bestiary_assets.py [--tag TAG]`

Default tag: 1.9.7.15.J374. Output: tools/_bestiary_raw/ con la estructura
classic/, rebirth/, repentance/ + MANIFEST.json.
"""
from __future__ import annotations
import argparse, json, re, sys, zipfile, io, urllib.request
from pathlib import Path

REPO = "Derugon/TBoIR-resources"
DEFAULT_TAG = "1.9.7.15.J374"
SUBPATH = "resources-dlc3/gfx/monsters"
OUT = Path(__file__).parent / "_bestiary_raw"

FILENAME_RE = re.compile(
    r"^(?P<type>\d+)\.(?P<variant>\d+)_(?P<name>[a-z0-9_]+?)(?:_(?P<suffix>champion|gehenna|ashpit|corpse|.*))?\.png$",
    re.IGNORECASE,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default=DEFAULT_TAG)
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    archive_url = f"https://github.com/{REPO}/archive/refs/tags/{args.tag}.zip"
    print(f"Downloading {archive_url}")
    with urllib.request.urlopen(archive_url) as r:
        zip_bytes = r.read()
    print(f"  {len(zip_bytes)} bytes")

    manifest = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for info in z.infolist():
            if SUBPATH not in info.filename or not info.filename.endswith(".png"):
                continue
            rel = info.filename.split(SUBPATH + "/", 1)[1]
            folder, fname = rel.split("/", 1) if "/" in rel else ("misc", rel)
            local = OUT / folder / fname
            local.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(local, "wb") as dst:
                dst.write(src.read())
            m = FILENAME_RE.match(fname)
            if not m:
                print(f"  SKIP (filename unparseable): {fname}")
                continue
            manifest.append({
                "type": int(m["type"]),
                "variant": int(m["variant"]),
                "name_en_slug": m["name"],
                "suffix": m["suffix"] or "",
                "folder": folder,
                "filename": fname,
            })

    (OUT / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote {len(manifest)} entries to MANIFEST.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Añadir entradas a `.gitignore`**

```
# bestiario — assets crudos descargados (regenerables)
tools/_bestiary_raw/
```

- [ ] **Step 3: Ejecutar el script y verificar manifest**

```
python tools/extract_bestiary_assets.py
```

Expected: ≥ 350 entradas en `tools/_bestiary_raw/MANIFEST.json`. Si la URL del tag cambia, ajustar `DEFAULT_TAG`.

- [ ] **Step 4: Commit (sin los assets, solo el script)**

```bash
git add tools/extract_bestiary_assets.py .gitignore
git commit -m "tools: descarga assets de bestiario de Derugon"
```

---

### Task B2: Script `tools/build_bestiary.py` (crop + catálogo + inline)

Lee `MANIFEST.json`, cropea el primer frame de cada PNG, lo escala a 48×48, lo optimiza y genera dos artefactos: `tracker/data/bestiary.py` y `tracker/assets/bestiary_inline.js`.

**Files:**
- Create: `tools/build_bestiary.py`
- Create: `tracker/data/bestiary.py` (generado)
- Create: `tracker/assets/bestiary_inline.js` (generado)

- [ ] **Step 1: Listas de categorías hard-coded**

Al inicio del script:

```python
# Bosses canónicos (entity_type → True). Si type == valor, category=boss.
BOSS_TYPES = {
    19,   # Mom
    18,   # Larry Jr. (semi-boss pero el juego lo trata como boss)
    20,   # Monstro
    21,   # Pin
    25,   # Famine
    26,   # Pestilence
    27,   # War
    28,   # Death
    29,   # Duke of Flies
    36,   # Husk
    38,   # Mom's Heart / Mom's Foot dependiendo de variante (manejar abajo)
    39,   # Gemini
    43,   # Gurdy
    45,   # Daddy Long Legs
    50,   # Steven (mini-boss en planta, pero boss-room en algunos)
    54,   # Isaac
    62,   # Satan
    63,   # The Lamb
    71,   # Mega Maw / Mega Fatty
    100,  # Hush
    273,  # Delirium
    900,  # Mother
    951,  # The Beast
    406,  # Ultra Greed / Greedier
    # (lista no exhaustiva; se completa iterativamente — ver verificación abajo)
}

MINIBOSS_TYPES = {
    78,   # Gurglings
    81,   # Adversary
    82,   # Gluttony
    83,   # The Cage
    84,   # The Bloat
    85,   # The Carrion Queen
    # ... idem, refinable
}
```

> **Nota:** estas listas no son canónicas al 100% — la fuente final es el `EntityType` de Repentance+. Tarea aceptable: cubrir los conocidos y dejar el resto como `"enemy"`. Si un boss conocido sale como enemy, refinar la lista en commits posteriores. No bloquea.

- [ ] **Step 2: Pipeline de crop + resize**

```python
from PIL import Image

TARGET_SIZE = 48

def crop_first_frame(img: Image.Image) -> Image.Image:
    """Heurística: si el PNG es claramente un atlas (ancho >= 2 × alto y
    ancho múltiplo de alto), recorta el primer frame cuadrado del lado izq.
    Si no, devuelve la imagen tal cual (será un sprite simple)."""
    w, h = img.size
    if w >= 2 * h and w % h == 0:
        return img.crop((0, 0, h, h))
    # Algunos atlas son verticales (alto >= 2 × ancho).
    if h >= 2 * w and h % w == 0:
        return img.crop((0, 0, w, w))
    return img


def process_sprite(src: Path) -> bytes:
    img = Image.open(src).convert("RGBA")
    frame = crop_first_frame(img)
    frame = frame.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
    import io
    buf = io.BytesIO()
    frame.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
```

- [ ] **Step 3: Construcción del catálogo y deduplicación**

Por cada entrada del manifest:
1. Calcular sprite key: `f"{type:03d}.{variant:03d}"`.
2. Si el `(type, variant)` ya existe en catálogo y el `suffix` actual es `""` (= sprite base), sustituir. Las versiones con suffix (`champion`, `gehenna`, etc.) **se ignoran en esta primera iteración** — solo se incluye el sprite base. Documentar esta decisión en el header del script.
3. Determinar categoría con `BOSS_TYPES` / `MINIBOSS_TYPES`.
4. `name_en`: title-case del `name_en_slug` con `_` → espacio (`rotten_gaper` → `Rotten Gaper`).
5. `name_es`: inicialmente igual que `name_en`. Una traducción inicial corta de ~30 enemigos conocidos se carga desde una constante hard-coded `NAME_TRANSLATIONS_ES` en el script.

- [ ] **Step 4: Escribir `tracker/data/bestiary.py`**

```python
"""Catálogo de enemigos del bestiario — GENERADO por tools/build_bestiary.py.
NO editar a mano. Para añadir traducciones, edita NAME_TRANSLATIONS_ES en
tools/build_bestiary.py y reejecuta.
"""
from __future__ import annotations

BESTIARY_CATALOG: dict[tuple[int, int], dict] = {
    (10, 10): {"name_en": "Rotten Gaper", "name_es": "Rotten Gaper", "category": "enemy"},
    # ... ~372 entradas
}
```

- [ ] **Step 5: Escribir `tracker/assets/bestiary_inline.js`**

Base64-encoded PNGs en un mapa `{ "010.010": "data:image/png;base64,...", ... }`:

```javascript
window.BESTIARY_SPRITES = {
  "010.010": "data:image/png;base64,iVBORw0KGgoAA...",
  // ... resto
};
```

Tamaño esperado: < 1.2 MB. Si supera 2 MB, optimizar con `pngquant` o bajar TARGET_SIZE a 40.

- [ ] **Step 6: Smoke-test del script**

```
python tools/build_bestiary.py
```

Expected: imprime `Wrote N entries to bestiary.py` con N ≥ 200 y `Wrote N sprites to bestiary_inline.js` con tamaño < 2 MB.

- [ ] **Step 7: Tests del catálogo (`tests/test_bestiary_catalog.py`)**

```python
def test_bestiary_catalog_has_entries():
    from tracker.data.bestiary import BESTIARY_CATALOG
    assert len(BESTIARY_CATALOG) >= 200


def test_bestiary_catalog_no_duplicates():
    from tracker.data.bestiary import BESTIARY_CATALOG
    # dict ya garantiza unicidad de keys; este test valida que la generación
    # no perdió datos por overwriting silencioso. Aseguramos que cada entrada
    # tiene los 3 campos.
    for key, meta in BESTIARY_CATALOG.items():
        assert isinstance(key, tuple) and len(key) == 2
        assert {"name_en", "name_es", "category"} <= set(meta.keys())
        assert meta["category"] in {"enemy", "miniboss", "boss"}


def test_known_bosses_marked_as_boss():
    from tracker.data.bestiary import BESTIARY_CATALOG
    # Mom = type 19, variant 0. Si no es boss, refinar BOSS_TYPES en el script.
    if (19, 0) in BESTIARY_CATALOG:
        assert BESTIARY_CATALOG[(19, 0)]["category"] == "boss"
    # The Beast = type 951 (canónico).
    boss_types = {t for (t, _v), meta in BESTIARY_CATALOG.items() if meta["category"] == "boss"}
    # Al menos 5 bosses distintos en el catálogo final.
    assert len(boss_types) >= 5
```

Correr: `pytest tests/test_bestiary_catalog.py -v` → 3 PASS. Si falla por una lista de bosses incompleta, ampliar `BOSS_TYPES` en `build_bestiary.py` y regenerar.

- [ ] **Step 8: Commit (script + artefactos generados)**

```bash
git add tools/build_bestiary.py tracker/data/bestiary.py tracker/assets/bestiary_inline.js tests/test_bestiary_catalog.py
git commit -m "feat(bestiary): catálogo generado + sprites inline"
```

---

## Fase C — UI: pestaña Estadísticas

### Task C1: `state_mapper._build_stats_state` + tests

Construye el bloque `stats_state` que la UI lee desde localStorage.

**Files:**
- Create: `tracker/data/stats_counters.py`
- Modify: `tracker/state_mapper.py` (añadir `_build_stats_state` + clave en `build_localstorage_state`)
- Create: `tests/test_stats_state.py`

- [ ] **Step 1: `tracker/data/stats_counters.py` inicial**

```python
"""Índices del chunk 2 (counters) confirmados en saves reales.

Cada entrada se añade SOLO cuando ha sido validada mediante diff de saves
(jugar → guardar → comparar). NO añadir índices sin validar; mostrar
contadores erróneos es peor que no mostrarlos.

Ver: tools/diff_counters.py para el protocolo de identificación.
"""
from __future__ import annotations

GLOBAL_STAT_COUNTERS: list[dict] = [
    {"index": 8,  "key": "donations_normal", "label_es": "Donaciones (tienda)",
     "icon": "coin"},
    {"index": 19, "key": "donations_greed",  "label_es": "Donaciones (Greed)",
     "icon": "coin_gold"},
    # Pendientes de identificar (no incluir hasta validar):
    # - Mom kills
    # - Runs completadas
    # - Monedas recogidas (acumulado)
    # - Bombas/llaves usadas
    # - Tiempo jugado
]
```

- [ ] **Step 2: Función `_build_stats_state` en `state_mapper.py`**

```python
from tracker.data.bestiary import BESTIARY_CATALOG


def _decode_packed_entity(packed: int) -> tuple[int, int]:
    """Hipótesis validada en tests/test_bestiary_parser.py."""
    return (packed // 1000, packed % 1000)


def _build_stats_state(parsed: ParsedSave) -> dict:
    # Re-empaquetar por (type, variant)
    def by_tv(d: dict[int, int]) -> dict[tuple[int, int], int]:
        return {_decode_packed_entity(k): v for k, v in d.items()}

    kills_tv = by_tv(parsed.bestiary_kills)
    deaths_tv = by_tv(parsed.bestiary_deaths)
    hits_tv = by_tv(parsed.bestiary_hits)
    encounters_tv = by_tv(parsed.bestiary_encounters)

    # Globals derivados del bestiario (siempre disponibles)
    globals_list = [
        {"key": "total_kills",          "label_es": "Enemigos eliminados",
         "value": sum(kills_tv.values()), "icon": "skull"},
        {"key": "total_deaths_by",      "label_es": "Veces que te han matado",
         "value": sum(deaths_tv.values()), "icon": "tombstone"},
        {"key": "total_hits",           "label_es": "Golpes recibidos",
         "value": sum(hits_tv.values()), "icon": "heart_broken"},
        {"key": "unique_encountered",   "label_es": "Enemigos distintos vistos",
         "value": sum(1 for v in encounters_tv.values() if v > 0),
         "max":   len(BESTIARY_CATALOG),
         "icon": "eye"},
    ]

    # Globals desde el chunk 2 confirmados
    from tracker.data.stats_counters import GLOBAL_STAT_COUNTERS
    # Para este patch los dos únicos índices ya tienen acceso directo en ParsedSave.
    # Cuando se identifiquen más, exponer el chunk 2 entero en ParsedSave y leer
    # desde aquí por índice.
    by_key = {"donations_normal": parsed.donation_count,
              "donations_greed":  parsed.greed_donation_count}
    for entry in GLOBAL_STAT_COUNTERS:
        if entry["key"] in by_key:
            globals_list.append({
                "key": entry["key"], "label_es": entry["label_es"],
                "value": by_key[entry["key"]], "icon": entry["icon"],
            })

    # Lista de bestiario incluye todos los enemigos del catálogo
    bestiary_list = []
    for (t, v), meta in sorted(BESTIARY_CATALOG.items()):
        kills = kills_tv.get((t, v), 0)
        deaths = deaths_tv.get((t, v), 0)
        hits = hits_tv.get((t, v), 0)
        enc = encounters_tv.get((t, v), 0)
        bestiary_list.append({
            "type": t, "variant": v,
            "name_es": meta["name_es"], "name_en": meta["name_en"],
            "category": meta["category"],
            "kills": kills, "deaths": deaths, "hits": hits, "encounters": enc,
            "sprite_id": f"{t:03d}.{v:03d}",
            "seen": kills > 0 or enc > 0,
        })

    return {"globals": globals_list, "bestiary": bestiary_list}
```

Añadir clave a `build_localstorage_state`:

```python
"stats_state": _build_stats_state(parsed),
```

- [ ] **Step 3: Tests `tests/test_stats_state.py`**

```python
from datetime import datetime, timezone
from tracker.save_parser import ParsedSave
from tracker.state_mapper import _build_stats_state


def _parsed(**kwargs):
    base = dict(
        slot=1, challenges_complete=set(), characters_unlocked=set(),
        character_marks={}, achievements_unlocked=set(), items_seen=set(),
        donation_count=0, greed_donation_count=0,
        bestiary_kills={}, bestiary_deaths={}, bestiary_hits={},
        bestiary_encounters={},
        parsed_at=datetime(2026, 5, 17, tzinfo=timezone.utc),
    )
    base.update(kwargs)
    return ParsedSave(**base)


def test_empty_save_produces_zero_globals():
    state = _build_stats_state(_parsed())
    by_key = {g["key"]: g for g in state["globals"]}
    assert by_key["total_kills"]["value"] == 0
    assert by_key["total_deaths_by"]["value"] == 0
    assert by_key["unique_encountered"]["value"] == 0


def test_kills_sum_into_total():
    # packed ids: 10010 = (10, 10), 19000 = (19, 0)
    state = _build_stats_state(_parsed(bestiary_kills={10010: 5, 19000: 3}))
    by_key = {g["key"]: g for g in state["globals"]}
    assert by_key["total_kills"]["value"] == 8


def test_bestiary_list_has_all_catalog_entries():
    from tracker.data.bestiary import BESTIARY_CATALOG
    state = _build_stats_state(_parsed())
    assert len(state["bestiary"]) == len(BESTIARY_CATALOG)
    # todos unseen
    assert all(e["seen"] is False for e in state["bestiary"])


def test_seen_flag_flips_when_encountered():
    # (19, 0) = Mom
    state = _build_stats_state(_parsed(bestiary_encounters={19000: 1}))
    mom = next(e for e in state["bestiary"] if (e["type"], e["variant"]) == (19, 0))
    assert mom["seen"] is True
    assert mom["encounters"] == 1


def test_donation_counters_appear_in_globals():
    state = _build_stats_state(_parsed(donation_count=120, greed_donation_count=450))
    by_key = {g["key"]: g for g in state["globals"]}
    assert by_key["donations_normal"]["value"] == 120
    assert by_key["donations_greed"]["value"] == 450
```

- [ ] **Step 4: Correr tests**

```
pytest tests/test_stats_state.py tests/test_state_mapper.py -v
```

Expected: nuevos tests PASS + ningún test existente roto.

- [ ] **Step 5: Commit**

```bash
git add tracker/data/stats_counters.py tracker/state_mapper.py tests/test_stats_state.py
git commit -m "feat(state): exponer stats_state con bestiario y globales"
```

---

### Task C2: Esqueleto HTML de la pestaña Estadísticas

**Files:**
- Modify: `challenges.html`

- [ ] **Step 1: Botón de pestaña en la barra**

Tras el botón de Donaciones (línea ~1958), añadir:

```html
<button class="tab" data-view="stats">Estadísticas</button>
```

- [ ] **Step 2: Contenedor de la pestaña**

Localizar el contenedor de la pestaña Donaciones (`<div id="donations-view" class="view">…</div>`) — debe haber uno por cada `data-view`. Añadir, después de él:

```html
<div id="stats-view" class="view">
  <section class="stats-globals">
    <h2>Trayectoria global</h2>
    <div class="stats-cards" id="statsCards"></div>
  </section>
  <section class="bestiary">
    <h2>Bestiario</h2>
    <div class="bestiary-toolbar">
      <div class="filter-group" id="bestiarySeenFilter">
        <button class="chip active" data-filter="seen">Vistos</button>
        <button class="chip" data-filter="all">Todos</button>
      </div>
      <div class="filter-group" id="bestiaryCategoryFilter">
        <button class="chip active" data-cat="all">Todos</button>
        <button class="chip" data-cat="enemy">Enemigos</button>
        <button class="chip" data-cat="miniboss">Mini-bosses</button>
        <button class="chip" data-cat="boss">Bosses</button>
      </div>
      <input type="search" id="bestiarySearch" placeholder="Buscar enemigo…">
      <select id="bestiarySort">
        <option value="kills_desc">Kills (más → menos)</option>
        <option value="kills_asc">Kills (menos → más)</option>
        <option value="alpha">Alfabético</option>
        <option value="category">Por tipo</option>
      </select>
    </div>
    <div class="bestiary-grid" id="bestiaryGrid"></div>
    <p class="bestiary-empty hidden" id="bestiaryEmpty">
      Empieza a jugar para llenar el bestiario.
    </p>
  </section>
</div>
```

- [ ] **Step 3: Importar el JS de sprites inline**

Localizar el `<script src="items_inline.js"></script>` o equivalente. Añadir junto:

```html
<script src="tracker/assets/bestiary_inline.js"></script>
```

(Si la ruta inline existente usa otra base, calcar la convención exacta — Donaciones es el patrón más reciente.)

- [ ] **Step 4: Verificación visual mínima**

Lanzar la app local (`python -m tracker.app`) y comprobar que el botón "Estadísticas" aparece en la barra, que al pulsarlo se ve el contenedor (aún vacío) sin romper otras pestañas.

- [ ] **Step 5: Commit**

```bash
git add challenges.html
git commit -m "feat(ui): esqueleto HTML de la pestaña Estadísticas"
```

---

### Task C3: CSS de la pestaña Estadísticas

**Files:**
- Modify: `challenges.html` (bloque `<style>`)

- [ ] **Step 1: Localizar la zona del CSS de la pestaña Donaciones** (referencia visual). Añadir un bloque nuevo encadenado:

```css
/* ===== Pestaña Estadísticas ===== */
#stats-view .stats-globals { margin-bottom: 1.5rem; }
#stats-view .stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0.75rem;
}
#stats-view .stats-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px;
  padding: 0.85rem;
  display: flex; flex-direction: column; align-items: flex-start;
}
#stats-view .stats-card .value {
  font-size: 1.7rem; font-weight: 700; color: #f3f3f3;
  margin-top: 0.25rem;
}
#stats-view .stats-card .label { font-size: 0.85rem; opacity: 0.75; }
#stats-view .stats-card .icon { width: 22px; height: 22px; opacity: 0.7; }

#stats-view .bestiary-toolbar {
  display: flex; flex-wrap: wrap; gap: 0.6rem;
  align-items: center; margin: 0.5rem 0 1rem;
}
#stats-view .filter-group { display: inline-flex; gap: 0.3rem; }
#stats-view .chip {
  background: rgba(255,255,255,0.05); color: #ddd;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 999px; padding: 0.3rem 0.8rem;
  cursor: pointer; font-size: 0.85rem;
}
#stats-view .chip.active { background: #5b8def; border-color: #5b8def; color: #fff; }
#stats-view #bestiarySearch {
  background: rgba(255,255,255,0.05); color: #fff;
  border: 1px solid rgba(255,255,255,0.1); border-radius: 4px;
  padding: 0.35rem 0.6rem; min-width: 180px;
}
#stats-view #bestiarySort {
  background: rgba(255,255,255,0.05); color: #fff;
  border: 1px solid rgba(255,255,255,0.1); border-radius: 4px;
  padding: 0.3rem 0.5rem;
}

#stats-view .bestiary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 0.5rem;
}
#stats-view .enemy-cell {
  background: rgba(255,255,255,0.03);
  border-radius: 4px; padding: 0.5rem 0.3rem;
  display: flex; flex-direction: column; align-items: center;
  position: relative;
  cursor: default;
}
#stats-view .enemy-cell.unseen { opacity: 0.3; }
#stats-view .enemy-cell img { width: 48px; height: 48px; image-rendering: pixelated; }
#stats-view .enemy-cell .name {
  font-size: 0.7rem; text-align: center;
  margin-top: 0.25rem; max-width: 100%;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
#stats-view .enemy-cell .kills {
  font-size: 1rem; font-weight: 700; color: #ffcd5b;
}
#stats-view .enemy-cell .badge {
  position: absolute; top: 2px; right: 2px;
  font-size: 0.6rem; padding: 1px 4px; border-radius: 3px;
  font-weight: 700;
}
#stats-view .enemy-cell .badge.boss     { background: #e74c3c; color: #fff; }
#stats-view .enemy-cell .badge.miniboss { background: #f39c12; color: #000; }

#stats-view .bestiary-empty {
  text-align: center; padding: 2rem; opacity: 0.6;
}
.hidden { display: none; }
```

- [ ] **Step 2: Smoke-test visual**

Recargar la app, navegar a la pestaña → verificar que la toolbar y el grid vacío respetan el layout esperado. Aún no hay datos; basta con que la sección no esté reventada (sin overflow, sin colores rotos).

- [ ] **Step 3: Commit**

```bash
git add challenges.html
git commit -m "feat(ui): CSS de la pestaña Estadísticas"
```

---

### Task C4: Render de cards globales

**Files:**
- Modify: `challenges.html` (bloque `<script>` o `_bind_view_handlers()`)

- [ ] **Step 1: Iconos**

Los iconos de las cards globales (`skull`, `tombstone`, `heart_broken`, `eye`, `coin`, `coin_gold`) — usar emojis Unicode inicialmente (`💀`, `🪦`, `💔`, `👁️`, `🪙`, `💰`) hasta que tengamos sprites limpios. Sí, emoji por defecto suele evitarse, pero aquí es una opción intencional para arrancar sin pipeline extra de iconos — está alineado con el "no añadir pasos de pipeline más de lo necesario".

Mapa en JS:

```javascript
const STATS_ICONS = {
  skull: "💀", tombstone: "🪦", heart_broken: "💔", eye: "👁️",
  coin: "🪙", coin_gold: "💰",
};
```

- [ ] **Step 2: Render de cards**

Localizar la función que se ejecuta cuando se activa una pestaña (`switchView`, `renderView`, similar). Añadir un caso/handler para `stats`:

```javascript
function renderStatsTab() {
  const state = loadStateOrNull();
  if (!state || !state.stats_state) return;
  const cardsEl = document.getElementById("statsCards");
  cardsEl.innerHTML = "";
  for (const g of state.stats_state.globals) {
    const valueText = g.max != null
      ? `${g.value} / ${g.max}`
      : `${g.value.toLocaleString("es-ES")}`;
    const card = document.createElement("div");
    card.className = "stats-card";
    card.innerHTML = `
      <span class="icon">${STATS_ICONS[g.icon] || "•"}</span>
      <span class="value">${valueText}</span>
      <span class="label">${g.label_es}</span>
    `;
    cardsEl.appendChild(card);
  }
  renderBestiaryGrid();  // C5
}
```

- [ ] **Step 3: Bind a la pestaña**

Donde se activan handlers por pestaña, añadir:

```javascript
if (view === "stats") renderStatsTab();
```

- [ ] **Step 4: Smoke-test visual**

Cargar un save real (o usar el fixture). Navegar a la pestaña Estadísticas. Las 6 cards deben renderizarse con valores plausibles.

- [ ] **Step 5: Commit**

```bash
git add challenges.html
git commit -m "feat(ui): render de cards globales en Estadísticas"
```

---

### Task C5: Render del grid del bestiario + filtros + tooltip

**Files:**
- Modify: `challenges.html`

- [ ] **Step 1: Render base del grid**

```javascript
const BESTIARY_STATE = {
  filter: "seen",       // "seen" | "all"
  category: "all",      // "all" | "enemy" | "miniboss" | "boss"
  search: "",
  sort: "kills_desc",
};

function renderBestiaryGrid() {
  const state = loadStateOrNull();
  if (!state || !state.stats_state) return;
  const all = state.stats_state.bestiary;
  let items = all.filter(e => {
    if (BESTIARY_STATE.filter === "seen" && !e.seen) return false;
    if (BESTIARY_STATE.category !== "all" && e.category !== BESTIARY_STATE.category) return false;
    if (BESTIARY_STATE.search) {
      const q = BESTIARY_STATE.search.toLowerCase();
      if (!e.name_es.toLowerCase().includes(q) && !e.name_en.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const sorters = {
    kills_desc: (a, b) => b.kills - a.kills || a.name_es.localeCompare(b.name_es),
    kills_asc:  (a, b) => a.kills - b.kills || a.name_es.localeCompare(b.name_es),
    alpha:      (a, b) => a.name_es.localeCompare(b.name_es),
    category:   (a, b) => {
      const order = {boss: 0, miniboss: 1, enemy: 2};
      return order[a.category] - order[b.category] || b.kills - a.kills;
    },
  };
  items.sort(sorters[BESTIARY_STATE.sort]);

  const grid = document.getElementById("bestiaryGrid");
  const empty = document.getElementById("bestiaryEmpty");
  grid.innerHTML = "";
  if (items.length === 0) { empty.classList.remove("hidden"); return; }
  empty.classList.add("hidden");

  const sprites = window.BESTIARY_SPRITES || {};
  for (const e of items) {
    const cell = document.createElement("div");
    cell.className = "enemy-cell" + (e.seen ? "" : " unseen");
    cell.dataset.type = e.type;
    cell.dataset.variant = e.variant;
    const badge = e.category === "boss"
      ? '<span class="badge boss">B</span>'
      : e.category === "miniboss" ? '<span class="badge miniboss">MB</span>' : '';
    const sprite = sprites[e.sprite_id];
    const img = sprite
      ? `<img src="${sprite}" alt="${e.name_en}">`
      : `<div style="width:48px;height:48px;background:#333;display:flex;align-items:center;justify-content:center;">?</div>`;
    cell.innerHTML = `
      ${badge}
      ${img}
      <span class="name" title="${e.name_es}">${e.name_es}</span>
      <span class="kills">${e.seen ? "× " + e.kills : "?"}</span>
    `;
    cell.addEventListener("mouseenter", ev => showBestiaryTooltip(ev, e));
    cell.addEventListener("mouseleave", hideBestiaryTooltip);
    grid.appendChild(cell);
  }
}
```

- [ ] **Step 2: Binds de filtros y buscador**

```javascript
function bindBestiaryControls() {
  document.querySelectorAll("#bestiarySeenFilter .chip").forEach(b => {
    b.addEventListener("click", () => {
      document.querySelectorAll("#bestiarySeenFilter .chip").forEach(x => x.classList.remove("active"));
      b.classList.add("active");
      BESTIARY_STATE.filter = b.dataset.filter;
      renderBestiaryGrid();
    });
  });
  document.querySelectorAll("#bestiaryCategoryFilter .chip").forEach(b => {
    b.addEventListener("click", () => {
      document.querySelectorAll("#bestiaryCategoryFilter .chip").forEach(x => x.classList.remove("active"));
      b.classList.add("active");
      BESTIARY_STATE.category = b.dataset.cat;
      renderBestiaryGrid();
    });
  });
  document.getElementById("bestiarySearch").addEventListener("input", ev => {
    BESTIARY_STATE.search = ev.target.value;
    renderBestiaryGrid();
  });
  document.getElementById("bestiarySort").addEventListener("change", ev => {
    BESTIARY_STATE.sort = ev.target.value;
    renderBestiaryGrid();
  });
}
```

Llamar `bindBestiaryControls()` una sola vez en el bootstrap (igual que se hace con otras pestañas).

- [ ] **Step 3: Tooltip de enemigo**

Reutilizar el mecanismo de tooltip existente (la pestaña Ítems ya tiene uno). Si no es trivial reutilizar, implementar tooltip mínimo:

```javascript
let _bestiaryTooltipEl = null;
function showBestiaryTooltip(ev, e) {
  if (!_bestiaryTooltipEl) {
    _bestiaryTooltipEl = document.createElement("div");
    _bestiaryTooltipEl.style.cssText = "position:fixed;background:#111;color:#fff;padding:0.5rem 0.7rem;border:1px solid #444;border-radius:4px;font-size:0.8rem;z-index:9999;pointer-events:none;";
    document.body.appendChild(_bestiaryTooltipEl);
  }
  const catLabel = {enemy: "", miniboss: "(Mini-boss)", boss: "(Boss)"}[e.category];
  const rows = [];
  rows.push(`<strong>${e.name_es}</strong> ${catLabel}`);
  if (e.kills > 0)      rows.push(`Kills: ${e.kills}`);
  if (e.deaths > 0)     rows.push(`Te ha matado: ${e.deaths}`);
  if (e.hits > 0)       rows.push(`Hits recibidos: ${e.hits}`);
  if (e.encounters > 0) rows.push(`Encuentros: ${e.encounters}`);
  _bestiaryTooltipEl.innerHTML = rows.join("<br>");
  _bestiaryTooltipEl.style.left = (ev.clientX + 12) + "px";
  _bestiaryTooltipEl.style.top  = (ev.clientY + 12) + "px";
  _bestiaryTooltipEl.style.display = "block";
}
function hideBestiaryTooltip() {
  if (_bestiaryTooltipEl) _bestiaryTooltipEl.style.display = "none";
}
```

- [ ] **Step 4: Smoke-test visual completo**

Cargar el save real:
- La pestaña muestra cards con valores reales.
- El grid muestra los enemigos vistos por defecto, ordenados por kills desc.
- Cambiar a "Todos" → aparecen siluetas grises de los no vistos.
- Filtrar por "Bosses" → solo bosses.
- Buscar "mom" → solo enemigos con "mom" en el nombre.
- Hover sobre un enemigo → tooltip con kills/deaths/hits/encounters.

- [ ] **Step 5: Commit**

```bash
git add challenges.html
git commit -m "feat(ui): grid de bestiario con filtros, orden y tooltip"
```

---

### Task C6: Sincronizar mirror, rebuild y verificación en .exe

**Files:**
- Modify: `build.spec` si fuera necesario para incluir `bestiary_inline.js`
- (la sincronización del mirror HTML/JS al bundle es automática vía scripts existentes — verificar)

- [ ] **Step 1: Comprobar que `bestiary_inline.js` está dentro del bundle**

Inspeccionar `build.spec`. Si el `datas` incluye `('tracker/assets/*', ...)` o `('tracker/assets', ...)`, el inline ya está cubierto. Si no, añadirlo explícitamente.

- [ ] **Step 2: Rebuild del .exe**

```
pyinstaller build.spec
```

o el comando equivalente del proyecto. Verificar que termina sin errores.

- [ ] **Step 3: Smoke-test del .exe**

Lanzar `dist/IsaacTracker.exe`. Navegar a la pestaña Estadísticas. Verificar:
- Cards aparecen con valores.
- Grid se renderiza con sprites (no placeholders grises masivos).
- Filtros funcionan.
- Tooltips funcionan.

Si el .exe muestra placeholders en lugar de sprites, el `bestiary_inline.js` no está siendo embebido — revisar `build.spec`.

- [ ] **Step 4: Commit del sync de mirror si hubo cambios**

```bash
git add build.spec build/<mirror si aplica>
git commit -m "build: incluir bestiario en bundle del .exe"
```

---

## Fase D — Stats globales adicionales (post-merge, iterativo)

**No bloquea el merge.** Cada índice identificado se hace en commits sueltos sin tocar la UI base.

### Task D1: Utilidad `tools/diff_counters.py`

**Files:**
- Create: `tools/diff_counters.py`

- [ ] **Step 1: Esqueleto del diff**

```python
"""Diff de chunk 2 (counters) entre dos saves.

Uso: python tools/diff_counters.py before.dat after.dat

Imprime los índices donde el valor cambió, con (before → after, delta).
"""
import struct, sys
from pathlib import Path
from tracker.save_parser import _extract_chunks


def counters(path):
    data = Path(path).read_bytes()
    chunks, _post = _extract_chunks(data, Path(path))
    body = chunks[2]
    return [struct.unpack_from("<i", body, i * 4)[0] for i in range(len(body) // 4)]


def main():
    a, b = sys.argv[1], sys.argv[2]
    ca, cb = counters(a), counters(b)
    n = min(len(ca), len(cb))
    for i in range(n):
        if ca[i] != cb[i]:
            print(f"  [{i:>3}] {ca[i]:>8}  →  {cb[i]:>8}   (Δ {cb[i]-ca[i]:+})")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Documentar protocolo en el docstring** y en `tracker/data/stats_counters.py`:

```
1. Copiar el save actual a `tools/_diff/before.dat`.
2. Jugar una run conocida (p. ej. matar a Mom una vez más, ganar una run con Greed mode).
3. Esperar al guardado (volver al menú).
4. Copiar el save a `tools/_diff/after.dat`.
5. `python tools/diff_counters.py tools/_diff/before.dat tools/_diff/after.dat`.
6. Anotar el índice cuyo cambio coincide con la acción y añadirlo a GLOBAL_STAT_COUNTERS.
```

- [ ] **Step 3: Commit**

```bash
git add tools/diff_counters.py tracker/data/stats_counters.py
git commit -m "tools: utilidad de diff para identificar counters del chunk 2"
```

### Tasks D2..DN: Identificación de contadores específicos

Una task pequeña por contador identificado. Plantilla:

- [ ] Capturar before/after del usuario para la acción concreta.
- [ ] Correr `tools/diff_counters.py`.
- [ ] Confirmar el índice (cambio = magnitud esperada).
- [ ] Añadir entrada a `GLOBAL_STAT_COUNTERS`.
- [ ] Si requiere lectura desde el chunk 2 además de los dos índices fijos actuales, ampliar `ParsedSave` (campo genérico `counters: list[int]`).
- [ ] Ajustar `_build_stats_state` para usar el nuevo índice.
- [ ] Commit individual.

Candidatos (orden sugerido por probabilidad de éxito):
1. Mom kills (matar 1× a Mom y diff).
2. Runs completadas (terminar una run cualquiera).
3. Monedas recogidas (recoger una moneda en una run).
4. Tiempo jugado (esperar 5 minutos y diff).
5. Mejor win-streak (puede no existir como counter; aceptar si no aparece).

---

## Verificación final antes de declarar la feature completa

(Usar `superpowers:verification-before-completion`.)

- [ ] `pytest tests/ -v` → todos los tests PASS.
- [ ] Lanzar `dist/IsaacTracker.exe` con un save real del usuario.
- [ ] Validar que las 6 cards tienen valores coherentes con lo que el menú in-game de Isaac muestra (cuando sea contrastable).
- [ ] Validar que la pestaña no rompe ninguna otra pestaña existente (clicar en Desafíos, Personajes, Logros, Ítems, Trinkets, Cartas, Donaciones → todas funcionan).
- [ ] Tamaño del .exe aumenta < 1.5 MB respecto al baseline previo.
- [ ] El usuario revisa visualmente el grid con un save real y reporta enemigos mal-clasificados / sprites cortados / nombres feos. Cada bug se anota como task de seguimiento, no bloquea el merge a menos que sea grave.
