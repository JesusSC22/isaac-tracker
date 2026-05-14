# Pestaña Cartas y Píldoras — Plan de implementación

> **Para agentes:** Usa la skill `superpowers:subagent-driven-development` (si hay subagentes) o `superpowers:executing-plans` para ejecutar este plan. Los pasos usan checkbox (`- [ ]`) para tracking.

**Goal:** Añadir una pestaña "Cartas y Píldoras" al tracker que muestre el progreso de colección con grid adaptativa, tooltip en hover y dos barras de progreso, mirror del patrón de Ítems.

**Architecture:** Extensión del parser binario actual con dos chunks nuevos (6 cartas, 10 píldoras con tratamiento tolerante), dos catálogos Python auto-generados, dos inline-JS análogos a `items_inline.js`, y una pestaña en `challenges.html` con su CSS y handlers JS, todo siguiendo el patrón existente (ver `tracker/save_parser.py`, `tracker/data/collectibles.py`, `tools/build_items_inline.py`, secciones de Ítems en `challenges.html`). El refactor de `_extract_chunks` a dict precede cualquier cambio funcional.

**Tech Stack:** Python 3.11 (parser, build scripts, PyInstaller), pytest, HTML/CSS/Vanilla JS (UI), PyWebView (runtime), optipng (assets).

**Spec:** `docs/superpowers/specs/2026-05-14-cards-pills-tab-design.md`

---

## Task 0: Refactor `_extract_chunks` a `dict[int, bytes]`

**Files:**
- Modify: `tracker/save_parser.py:158-200` (firma + body de `_extract_chunks`)
- Modify: `tracker/save_parser.py:108-145` (caller `parse_save`)
- Test: `tests/test_save_parser.py` (existentes)

**Pre-condición:** los tests existentes pasan en `main` antes de empezar.

- [ ] **Step 0.0: Verificar baseline**

```bash
cd C:\Users\jeiko\Downloads\isaac_challenges
.\.venv\Scripts\python.exe -m pytest tests/test_save_parser.py -v
```
Expected: todos en VERDE.

- [ ] **Step 0.1: Cambiar firma de `_extract_chunks`**

Reemplazar el cuerpo y la firma:

```python
def _extract_chunks(data: bytes, path: Path) -> dict[int, bytes]:
    """Walk the 10 fixed-size chunks and return {chunk_type: body_bytes}."""
    chunks: dict[int, bytes] = {}
    off = _HEADER_SIZE
    for i in range(10):
        if off + _CHUNK_HEADER_SIZE > len(data):
            raise SaveParseError(
                f"Partida truncada: se acabaron los bytes en la cabecera del bloque {i + 1}"
                f" (offset 0x{off:04X}, tamaño del archivo {len(data)}).",
                path=str(path),
            )
        chunk_type, _len_field, count = struct.unpack_from("<iii", data, off)
        body_start = off + _CHUNK_HEADER_SIZE
        body_len = count * _ENTRY_SIZES[i]
        body_end = body_start + body_len
        if body_end > len(data):
            raise SaveParseError(
                f"Partida truncada: el cuerpo del bloque {i + 1} se sale del archivo"
                f" (cuerpo 0x{body_start:04X}..0x{body_end:04X}, tamaño del archivo {len(data)}).",
                path=str(path),
            )
        chunks[chunk_type] = data[body_start:body_end]
        off = body_end

    for required, label in (
        (_CHUNK_ACHIEVEMENTS, "logros"),
        (_CHUNK_CHALLENGE_COUNTERS, "retos"),
        (_CHUNK_COLLECTIBLES, "ítems"),
    ):
        if required not in chunks:
            raise SaveParseError(f"No se encontró el bloque de {label} en la partida.", path=str(path))
    return chunks
```

- [ ] **Step 0.2: Actualizar `parse_save` para consumir el dict**

En `parse_save` (línea 131 aprox.), reemplazar:

```python
achievements, challenges, collectibles = _extract_chunks(data, path)
```

por:

```python
chunks = _extract_chunks(data, path)
achievements = chunks[_CHUNK_ACHIEVEMENTS]
challenges   = chunks[_CHUNK_CHALLENGE_COUNTERS]
collectibles = chunks[_CHUNK_COLLECTIBLES]
```

El resto de `parse_save` (las 4 llamadas `_extract_*`) queda igual.

- [ ] **Step 0.3: Re-ejecutar tests**

```bash
.\.venv\Scripts\python.exe -m pytest tests/test_save_parser.py -v
```
Expected: todos en VERDE, sin cambios funcionales. **GATE**: si algún test cae, revertir y replantear.

- [ ] **Step 0.4: Commit**

```bash
rtk git add tracker/save_parser.py
rtk git commit -m "refactor(parser): _extract_chunks devuelve dict[type, body] (sin cambio funcional)"
```

---

## Task 1: Catálogo `tracker/data/cards.py`

**Files:**
- Create: `tools/build_cards.py`
- Create: `tracker/data/cards.py` (auto-generado)
- Modify: none

**Pre-requisito conceptual:** la lista canónica de cartas Repentance+ con id/nombre/grupo. Fuente preferida: `Steam\steamapps\common\The Binding of Isaac Rebirth\resources\pocketitems.xml`. Fallback: tabla del wiki.

> **Nota — `desc_es=""` intencional en V1.** Las descripciones se rellenan en V2 extendiendo `tools/build_eid.py` (o creando `tools/build_eid_cards.py`). Spec ya marca esto como "Seguimiento posterior". No bloquea V1.

- [ ] **Step 1.1: Crear `tools/build_cards.py`**

Genera el dict siguiendo la forma de `tracker/data/collectibles.py`:

```python
"""Generate tracker/data/cards.py from pocketitems.xml.

Usage:
  python tools/build_cards.py <path_to_pocketitems.xml>
or, if the XML lives next to the executable, set ISAAC_GAME_DIR env var.
"""
from __future__ import annotations
import os, sys, xml.etree.ElementTree as ET
from pathlib import Path

# Grupos: clasificación por id range (Repentance+ canónica).
# 1-22 = tarot mayor; 23-54 = especiales clásicas; 55-77 = runas + cartas-de-objeto;
# 78-... = Repentance/Repentance+ adiciones. Ajustar tras inspección del XML.
def classify_group(card_id: int, name: str) -> str:
    if 1 <= card_id <= 22:
        return "tarot_mayor"
    if name.lower().startswith("rune of") or name.lower() in {"hagalaz", "jera", "ehwaz", "dagaz", "ansuz", "perthro", "berkano", "algiz", "blank rune", "black rune"}:
        return "runas"
    if name.lower().startswith("soul of") or name.lower().startswith("alma de"):
        return "objetos_alma"
    if "?" in name or "reverse" in name.lower():
        return "tarot_inverso"
    return "especiales"

# parsing del XML aquí; rellenar campos: id, name, sprite, removed, desc_es, group
```

(Implementación completa: leer el XML, mapear cada `<card id="N" name="..." />`, derivar `sprite = f"card_{N:03d}.png"`, classificar grupo, `desc_es = ""` en V1.)

- [ ] **Step 1.2: Ejecutar el script**

```bash
.\.venv\Scripts\python.exe tools/build_cards.py "C:/Program Files (x86)/Steam/steamapps/common/The Binding of Isaac Rebirth/resources/pocketitems.xml"
```
Expected output: `[build_cards] wrote N cards -> tracker/data/cards.py` con N ≈ 98-104.

- [ ] **Step 1.3: Verificar manualmente**

Abrir `tracker/data/cards.py` y confirmar a ojo:
- id 1 = "0 - The Fool" (o "The Fool"), grupo `tarot_mayor`
- aparece "Cracked Key", "Soul of Isaac"
- ningún `name` vacío salvo el id 0 sentinel

- [ ] **Step 1.4: Commit**

```bash
rtk git add tools/build_cards.py tracker/data/cards.py
rtk git commit -m "feat(cards): catálogo cards.py auto-generado desde pocketitems.xml"
```

---

## Task 2: Iconos de cartas

**Files:**
- Create: `tools/extract_card_icons.py`
- Create: `tracker/assets/card_icons/card_NNN.png` (~98 archivos)

- [ ] **Step 2.0: Confirmar el naming de los archivos fuente**

El naming en `resources/gfx/ui/cards/` no es estable entre versiones. Antes de escribir el extractor, listar:

```bash
.\.venv\Scripts\python.exe -c "
from pathlib import Path
src = Path('C:/Program Files (x86)/Steam/steamapps/common/The Binding of Isaac Rebirth/resources/gfx/ui/cards')
for f in sorted(src.glob('*.png'))[:30]:
    print(f.name)
"
```
Observar el patrón real (¿`Card_001_The_Fool.png`? ¿`tarotcard_01.png`? ¿slug?) y ajustar el `glob` del script en step 2.1 a lo que se vea. **GATE**: si la carpeta no existe o está vacía, parar y consultar al usuario (puede que el juego empaquete los sprites en un `.anm2` y haya que extraerlos de otra forma).

- [ ] **Step 2.1: Crear `tools/extract_card_icons.py`**

```python
"""Copy and optimize card PNGs from the game's resources/gfx/ui/cards/ folder.

Output filename convention: card_NNN.png (zero-padded to 3).
"""
from __future__ import annotations
import shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tracker.data.cards import CARDS

def main(game_resources_dir: Path) -> int:
    src_dir = game_resources_dir / "gfx" / "ui" / "cards"
    dst_dir = ROOT / "tracker" / "assets" / "card_icons"
    dst_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for cid, meta in sorted(CARDS.items()):
        if meta["removed"] or not meta["sprite"]:
            continue
        # Source filename in game files: typically Card<NNN>_<name>.png; resolve by id.
        src_match = next(src_dir.glob(f"*{cid:04d}*.png"), None)
        if src_match is None:
            print(f"WARN: no source for card id {cid} ({meta['name']})")
            continue
        dst = dst_dir / meta["sprite"]
        shutil.copy2(src_match, dst)
        subprocess.run(["optipng", "-quiet", "-o2", str(dst)], check=False)
        written += 1
    print(f"[extract_card_icons] wrote {written} icons -> {dst_dir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
```

> Si el patrón `*{cid:04d}*` no encaja con el naming real del juego, ajustar a lo que se observe en la carpeta. Verificación visual obligatoria en step 2.3.

- [ ] **Step 2.2: Ejecutar**

```bash
.\.venv\Scripts\python.exe tools/extract_card_icons.py "C:/Program Files (x86)/Steam/steamapps/common/The Binding of Isaac Rebirth/resources"
```
Expected: `wrote ~98 icons -> tracker/assets/card_icons`.

- [ ] **Step 2.3: Verificación visual**

Abrir `tracker/assets/card_icons/` en el explorador. Comprobar:
- ~98 archivos PNG presentes
- Tamaños similares (~1-5 KB tras optipng)
- Spot-check abrir `card_001.png` → debe ser The Fool

- [ ] **Step 2.4: Commit**

```bash
rtk git add tools/extract_card_icons.py tracker/assets/card_icons/
rtk git commit -m "feat(cards): iconos PNG extraídos y optimizados desde el juego"
```

---

## Task 3: `cards_inline.js`

**Files:**
- Create: `tools/build_cards_inline.py`
- Create: `tracker/assets/cards_inline.js`

- [ ] **Step 3.1: Crear `tools/build_cards_inline.py`**

Copia exacta de `tools/build_items_inline.py` adaptada:

```python
"""Generate tracker/assets/cards_inline.js from tracker/data/cards.py."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tracker.data.cards import CARDS

def main() -> int:
    cards = []
    for cid, meta in sorted(CARDS.items()):
        if meta["removed"]:
            continue
        cards.append({
            "id": cid,
            "name": meta["name"],
            "sprite": meta["sprite"],
            "desc": meta.get("desc_es", ""),
            "group": meta.get("group", "especiales"),
        })
    out = ROOT / "tracker" / "assets" / "cards_inline.js"
    payload = json.dumps(cards, ensure_ascii=False, separators=(",", ":"))
    out.write_text(f"window.CARDS_DATA = {payload};\n", encoding="utf-8")
    print(f"[build_cards_inline] wrote {len(cards)} cards -> {out} ({out.stat().st_size} bytes)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3.2: Ejecutar**

```bash
.\.venv\Scripts\python.exe tools/build_cards_inline.py
```
Expected: `wrote ~98 cards -> tracker/assets/cards_inline.js`.

- [ ] **Step 3.3: Verificar el JS**

```bash
rtk read tracker/assets/cards_inline.js
```
Confirmar que arranca con `window.CARDS_DATA = [{...}, ...];` y que todos los grupos están representados.

- [ ] **Step 3.4: Commit**

```bash
rtk git add tools/build_cards_inline.py tracker/assets/cards_inline.js
rtk git commit -m "feat(cards): cards_inline.js generado desde cards.py"
```

---

## Task 4: Parser — chunk 6 (cartas, estricto)

**Files:**
- Modify: `tracker/save_parser.py`
- Modify: `tests/test_save_parser.py`

- [ ] **Step 4.1: Test que falla**

Añadir al final de `tests/test_save_parser.py`:

```python
def test_cards_seen_from_fixture():
    fixture = Path(__file__).parent / "fixtures" / "sample_save_repentance_plus.dat"
    parsed = parse_save(fixture)
    # Fixture: chunk 6 tiene 97 bytes==1 sobre 104 entradas.
    assert len(parsed.cards_seen) == 97
    assert all(isinstance(i, int) and 0 <= i < 104 for i in parsed.cards_seen)
```

- [ ] **Step 4.2: Verificar que falla**

```bash
.\.venv\Scripts\python.exe -m pytest tests/test_save_parser.py::test_cards_seen_from_fixture -v
```
Expected: FAIL con `AttributeError: 'ParsedSave' object has no attribute 'cards_seen'`.

- [ ] **Step 4.3: Implementar**

En `tracker/save_parser.py`:

1. Añadir constante:
```python
_CHUNK_CARDS = 6
```

2. Añadir extractor (después de `_extract_items_seen`):
```python
def _extract_cards_seen(cards_body: bytes) -> set[int]:
    """Return the set of card IDs (byte indices) whose byte is 1."""
    return {i for i, b in enumerate(cards_body) if b == 1}
```

3. Extender `ParsedSave` con:
```python
cards_seen: set[int] = field(default_factory=set)
```

4. En `_extract_chunks`, añadir cartas a la lista de "required":
```python
for required, label in (
    (_CHUNK_ACHIEVEMENTS, "logros"),
    (_CHUNK_CHALLENGE_COUNTERS, "retos"),
    (_CHUNK_COLLECTIBLES, "ítems"),
    (_CHUNK_CARDS, "cartas"),
):
    ...
```

5. En `parse_save`, después de extraer collectibles:
```python
cards_body = chunks[_CHUNK_CARDS]
cards_seen = _extract_cards_seen(cards_body)
```
y pasarlo al constructor de `ParsedSave`.

- [ ] **Step 4.4: Verificar que pasa**

```bash
.\.venv\Scripts\python.exe -m pytest tests/test_save_parser.py -v
```
Expected: TODOS en verde, incluido el nuevo.

- [ ] **Step 4.5: Commit**

```bash
rtk git add tracker/save_parser.py tests/test_save_parser.py
rtk git commit -m "feat(parser): extraer cards_seen del chunk 6 del save"
```

---

## Task 5: Verificación de chunk 6 = cartas (GATE)

**Files:** ninguno (solo verificación).

Este es un gate de validación. NO se sigue al Task 6 hasta que esto pase.

- [ ] **Step 5.1: Spot-check de IDs**

```bash
.\.venv\Scripts\python.exe -c "
from pathlib import Path
from tracker.save_parser import parse_save
from tracker.data.cards import CARDS
p = parse_save(Path('tests/fixtures/sample_save_repentance_plus.dat'))
seen_names = sorted(CARDS[i]['name'] for i in p.cards_seen if i in CARDS and CARDS[i]['name'])
print(f'Total cartas vistas: {len(seen_names)}')
for n in seen_names[:10]: print('  -', n)
print('...')
for n in seen_names[-5:]: print('  -', n)
"
```
Expected: lista de ~97 nombres de cartas reales (no IDs sin nombre). **GATE**: si los nombres son galimatías o `None`, el chunk 6 NO es cartas → ir a step 5.2.

- [ ] **Step 5.2: Fallback si chunk 6 no es cartas**

1. Revertir el commit de Task 4 para no dejar parser en estado inconsistente:
   ```bash
   rtk git revert HEAD --no-edit
   ```
2. Volver a probar con chunk 10 swap en una rama local:
   ```python
   # en parser temporalmente: _CHUNK_CARDS = 10
   ```
   Re-ejecutar el spot-check. Si tampoco encaja, **PARAR y pedir al usuario** que confirme in-game qué cartas tiene marcadas como "vistas" en su Collection Page, y contrastar manualmente con los índices `byte==1` de cada chunk 1-byte (5, 6, 10).
3. Solo cuando se identifique el chunk correcto, reaplicar Task 4 con la constante correcta y commit fresco.

- [ ] **Step 5.3: Confirmar y commit** (si pasa el gate sin cambios)

```bash
rtk git commit --allow-empty -m "verify(cards): chunk 6 confirmado como cartas (97/104 en fixture)"
```

---

## Task 6: Catálogo `tracker/data/pills.py`

Mismo patrón que Task 1. Fuente: `pocketitems.xml` (sección de pills) o tabla del wiki.

**Files:**
- Create: `tools/build_pills.py`
- Create: `tracker/data/pills.py`

- [ ] **Step 6.1: Crear `tools/build_pills.py`**

Estructura paralela a `build_cards.py`. Output:
```python
PILLS: dict[int, dict] = {
    1: {'name': 'Bad Trip', 'sprite': 'pill_001.png', 'removed': False, 'desc_es': '', 'horse': False},
    ...
}
```

- [ ] **Step 6.2: Ejecutar**

```bash
.\.venv\Scripts\python.exe tools/build_pills.py "C:/Program Files (x86)/Steam/steamapps/common/The Binding of Isaac Rebirth/resources/pocketitems.xml"
```
Expected: ~14-50 efectos según parser. Verificar manualmente que aparecen "Health Up", "Bad Trip", "Range Up".

- [ ] **Step 6.3: Commit**

```bash
rtk git add tools/build_pills.py tracker/data/pills.py
rtk git commit -m "feat(pills): catálogo pills.py auto-generado"
```

---

## Task 7: Iconos de píldoras

**Files:**
- Create: `tools/extract_pill_icons.py`
- Create: `tracker/assets/pill_icons/pill_NNN.png`

- [ ] **Step 7.0: Confirmar naming en `resources/gfx/items/pills/`**

```bash
.\.venv\Scripts\python.exe -c "
from pathlib import Path
src = Path('C:/Program Files (x86)/Steam/steamapps/common/The Binding of Isaac Rebirth/resources/gfx/items/pills')
for f in sorted(src.glob('*.png'))[:30]: print(f.name)
"
```
Ajustar el `glob` del script al patrón real. Posibles formatos: `pill_<color>.png`, `pill_<effectname>.png`, o por id. Si la carpeta no existe (algunas builds las empaquetan en `pickup_xxx.png` bajo otra ruta), pedir confirmación al usuario.

- [ ] **Step 7.1: Crear `tools/extract_pill_icons.py`**

```python
"""Copy and optimize pill PNGs from resources/gfx/items/pills/ → tracker/assets/pill_icons/.

Output filename convention: pill_NNN.png (zero-padded), where NNN matches PILLS[id].sprite.
"""
from __future__ import annotations
import shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tracker.data.pills import PILLS

def main(game_resources_dir: Path) -> int:
    src_dir = game_resources_dir / "gfx" / "items" / "pills"
    dst_dir = ROOT / "tracker" / "assets" / "pill_icons"
    dst_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for pid, meta in sorted(PILLS.items()):
        if meta.get("removed") or not meta["sprite"]:
            continue
        # Ajustar este glob según el resultado de step 7.0.
        # Patrón inicial: el script de build_pills.py debería haber dejado en
        # meta un campo `source_filename` con el archivo origen exacto. Si no,
        # caer a búsqueda por id zero-padded.
        candidates = list(src_dir.glob(f"*{pid:03d}*.png"))
        if not candidates:
            print(f"WARN: no source for pill id {pid} ({meta['name']})")
            continue
        dst = dst_dir / meta["sprite"]
        shutil.copy2(candidates[0], dst)
        subprocess.run(["optipng", "-quiet", "-o2", str(dst)], check=False)
        written += 1
    print(f"[extract_pill_icons] wrote {written} icons -> {dst_dir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
```

- [ ] **Step 7.2: Ejecutar**

```bash
.\.venv\Scripts\python.exe tools/extract_pill_icons.py "C:/Program Files (x86)/Steam/steamapps/common/The Binding of Isaac Rebirth/resources"
```
Expected: `wrote ~14-50 icons -> tracker/assets/pill_icons`.

- [ ] **Step 7.3: Verificación visual** en `tracker/assets/pill_icons/`. Abrir un par de PNG y confirmar que son efectivamente píldoras (sprites pequeños, fondo transparente).

- [ ] **Step 7.4: Commit**

```bash
rtk git add tools/extract_pill_icons.py tracker/assets/pill_icons/
rtk git commit -m "feat(pills): iconos PNG extraídos y optimizados"
```

---

## Task 8: `pills_inline.js`

**Files:**
- Create: `tools/build_pills_inline.py`
- Create: `tracker/assets/pills_inline.js`

- [ ] **Step 8.1: Crear `tools/build_pills_inline.py`**

```python
"""Generate tracker/assets/pills_inline.js from tracker/data/pills.py."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tracker.data.pills import PILLS

def main() -> int:
    pills = []
    for pid, meta in sorted(PILLS.items()):
        if meta.get("removed", False):
            continue
        pills.append({
            "id": pid,
            "name": meta["name"],
            "sprite": meta["sprite"],
            "desc": meta.get("desc_es", ""),
            "horse": meta.get("horse", False),
        })
    out = ROOT / "tracker" / "assets" / "pills_inline.js"
    payload = json.dumps(pills, ensure_ascii=False, separators=(",", ":"))
    out.write_text(f"window.PILLS_DATA = {payload};\n", encoding="utf-8")
    print(f"[build_pills_inline] wrote {len(pills)} pills -> {out} ({out.stat().st_size} bytes)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 8.2: Ejecutar**

```bash
.\.venv\Scripts\python.exe tools/build_pills_inline.py
```
Expected: `wrote ~14-50 pills -> tracker/assets/pills_inline.js`.

- [ ] **Step 8.3: Verificar el JS**

```bash
rtk read tracker/assets/pills_inline.js
```
Confirmar que arranca con `window.PILLS_DATA = [...]` y que aparecen efectos conocidos (Bad Trip, Health Up, Range Up).

- [ ] **Step 8.4: Commit**

```bash
rtk git add tools/build_pills_inline.py tracker/assets/pills_inline.js
rtk git commit -m "feat(pills): pills_inline.js generado"
```

---

## Task 9: Parser — chunk 10 (píldoras, tolerante) + `pills_verified`

**Files:**
- Modify: `tracker/save_parser.py`
- Modify: `tests/test_save_parser.py`

- [ ] **Step 9.1: Tests**

```python
def test_pills_seen_empty_in_fixture():
    """Fixture has chunk 10 todos a cero → set vacío, sin excepción."""
    fixture = Path(__file__).parent / "fixtures" / "sample_save_repentance_plus.dat"
    parsed = parse_save(fixture)
    assert parsed.pills_seen == set()
    assert parsed.pills_verified is False  # gate aún no superado

def test_pills_chunk_missing_returns_empty(tmp_path):
    """Si el chunk 10 no estuviera en el save, no debe romper el parse."""
    # Smoke: usar el fixture tal cual. Como sí está pero a cero, vale para verificar
    # que la rama tolerante no levanta excepción ni cuando hay datos.
    fixture = Path(__file__).parent / "fixtures" / "sample_save_repentance_plus.dat"
    parsed = parse_save(fixture)
    assert isinstance(parsed.pills_seen, set)
```

- [ ] **Step 9.2: Implementar**

1. Constante:
```python
_CHUNK_PILLS = 10
```

2. Extractor:
```python
def _extract_pills_seen(pills_body: bytes | None) -> set[int]:
    if pills_body is None:
        return set()
    return {i for i, b in enumerate(pills_body) if b == 1}
```

3. Extender `ParsedSave`:
```python
pills_seen: set[int] = field(default_factory=set)
pills_verified: bool = False
```

4. **No** añadir `_CHUNK_PILLS` a la lista de "required" en `_extract_chunks` (queda tolerante).

5. En `parse_save`:
```python
pills_body = chunks.get(_CHUNK_PILLS)
pills_seen = _extract_pills_seen(pills_body)
# pills_verified queda en False por defecto; se activa cuando el Task 10 lo confirme.
```

- [ ] **Step 9.3: Tests verdes.**

- [ ] **Step 9.4: Commit**

```bash
rtk git add tracker/save_parser.py tests/test_save_parser.py
rtk git commit -m "feat(parser): chunk 10 (pills) tolerante + flag pills_verified"
```

---

## Task 10: Verificación de chunk 10 = píldoras (GATE)

**Files:** ninguno por defecto. Solo si pasa la verificación, modificar `parse_save` para poner `pills_verified = True`.

- [ ] **Step 10.1: Pedir save al usuario**

Mensaje al usuario: *"Para activar la sección de píldoras necesito un save donde hayas identificado al menos 3 efectos. Dame el nombre de 3 píldoras concretas que hayas usado (Health Up, Bad Trip, etc.) y déjame el archivo en `tests/fixtures/sample_save_pills_verified.dat`."*

- [ ] **Step 10.2: Inspeccionar el save proporcionado**

```bash
.\.venv\Scripts\python.exe -c "
import struct
data = open('tests/fixtures/sample_save_pills_verified.dat', 'rb').read()
off = 20
for i, es in enumerate([1,4,4,1,1,1,1,4,4,1]):
    t, l, c = struct.unpack_from('<iii', data, off)
    body = data[off+12:off+12+c*es]
    if t == 10:
        ones = [j for j, b in enumerate(body) if b == 1]
        print('chunk 10 ones:', ones)
    off += 12 + c*es
"
```
Cruzar la lista de IDs con `PILLS` (sacar `PILLS[i]['name']`) y comparar con los 3 efectos que el usuario reportó haber identificado. Si los nombres coinciden → encaja. Si los IDs apuntan a píldoras que el usuario NO recuerda haber visto → NO encaja.

- [ ] **Step 10.3a: Si encaja — activar verificación**

Añadir constante a nivel de módulo en `tracker/save_parser.py` (cerca del resto de constantes):

```python
# Activa cuando el chunk 10 ha sido verificado como pills_effects vs un save
# con identificaciones conocidas. Ver docs/superpowers/specs/...cards-pills...
_PILLS_CHUNK_VERIFIED = True
```

Y en `parse_save`, donde se construye `ParsedSave`:

```python
pills_verified = _PILLS_CHUNK_VERIFIED
```

Añadir test:
```python
def test_pills_seen_matches_known_save():
    fixture = Path(__file__).parent / "fixtures" / "sample_save_pills_verified.dat"
    if not fixture.exists():
        import pytest; pytest.skip("verified pills fixture not present")
    parsed = parse_save(fixture)
    assert parsed.pills_verified is True
    # Sustituir con los IDs reales de las píldoras que el usuario confirmó:
    expected_subset = {ID_HEALTH_UP, ID_BAD_TRIP, ID_RANGE_UP}
    assert expected_subset <= parsed.pills_seen
```

Commit:
```bash
rtk git add tracker/save_parser.py tests/test_save_parser.py tests/fixtures/sample_save_pills_verified.dat
rtk git commit -m "verify(pills): chunk 10 confirmado como pills_effects + fixture"
```

- [ ] **Step 10.3b: Si NO encaja — fallback definitivo en V1**

Dejar `_PILLS_CHUNK_VERIFIED = False` permanente en V1. La UI mostrará la nota de pendiente. Documentar en `docs/superpowers/specs/2026-05-14-cards-pills-tab-design.md` (sección "Seguimiento posterior") el resultado de la verificación.

Commit:
```bash
rtk git commit --allow-empty -m "verify(pills): chunk 10 no verificado, V1 entrega cartas + nota de pendiente"
```

---

## Task 11: `state_mapper` — añadir cartas y píldoras a `SAVE_STATE`

**Files:**
- Modify: `tracker/state_mapper.py`
- Test: `tests/test_state_mapper.py` (si existe; si no, omitir o crear smoke test)

- [ ] **Step 11.1: Tests**

`tests/test_state_mapper.py` ya existe y usa el helper `_empty_parsed()` (no hay fixture `parsed_factory`). Seguir ese patrón. Añadir tests:

```python
def test_cards_state_marks_seen_true():
    p = ParsedSave(
        slot=1,
        challenges_complete=set(),
        characters_unlocked=set(),
        character_marks={},
        cards_seen={1, 3, 5},
        parsed_at=datetime(2026, 5, 14, tzinfo=timezone.utc),
    )
    state = build_localstorage_state(p)
    assert state["cards_state"]["1"] is True
    assert state["cards_state"]["2"] is False
    assert state["cards_state"]["3"] is True

def test_pills_state_and_verified_flag():
    p = ParsedSave(
        slot=1,
        challenges_complete=set(),
        characters_unlocked=set(),
        character_marks={},
        pills_seen={2},
        pills_verified=False,
        parsed_at=datetime(2026, 5, 14, tzinfo=timezone.utc),
    )
    state = build_localstorage_state(p)
    assert state["pills_state"]["2"] is True
    assert state["pills_verified"] is False
```

- [ ] **Step 11.2: Implementar**

En `tracker/state_mapper.py`:

```python
from tracker.data.cards import CARDS
from tracker.data.pills import PILLS

def build_localstorage_state(parsed: ParsedSave) -> dict:
    return {
        "challenges_state": _build_challenges(parsed),
        "characters_state": _build_characters(parsed),
        "achievements_unlocked": sorted(parsed.achievements_unlocked),
        "items_state": _build_items_state(parsed),
        "cards_state": _build_cards_state(parsed),
        "pills_state": _build_pills_state(parsed),
        "pills_verified": parsed.pills_verified,
        "meta": {
            "slot": parsed.slot,
            "parsed_at": parsed.parsed_at.isoformat(),
        },
    }

def _build_cards_state(parsed: ParsedSave) -> dict[str, bool]:
    return {
        str(cid): cid in parsed.cards_seen
        for cid, meta in CARDS.items()
        if not meta["removed"]
    }

def _build_pills_state(parsed: ParsedSave) -> dict[str, bool]:
    return {
        str(pid): pid in parsed.pills_seen
        for pid, meta in PILLS.items()
        if not meta.get("removed", False)
    }
```

- [ ] **Step 11.3: Tests verdes.**

- [ ] **Step 11.4: Commit**

```bash
rtk git add tracker/state_mapper.py tests/test_state_mapper.py
rtk git commit -m "feat(state): exponer cards_state, pills_state y pills_verified a la UI"
```

---

## Task 12: HTML — pestaña, secciones, contenedores

**Files:**
- Modify: `challenges.html` (raíz; el build sincroniza la copia de `tracker/assets/challenges.html`)

- [ ] **Step 12.1: Botón de pestaña**

Localizar el `<button class="tab" data-view="trinkets">Trinkets</button>` y añadir justo después:

```html
<button class="tab" data-view="cards">Cartas y Píldoras</button>
```

- [ ] **Step 12.2: Vista**

Localizar el bloque `<div class="view" id="view-trinkets">…</div>` (cierre incluido) y añadir justo después:

```html
<div class="view" id="view-cards">
  <div class="progress-bar-container">
    <div class="progress-bar" id="cardsProgressBar"></div>
  </div>
  <div class="progress-label" id="cardsProgressLabel">Cartas: 0 / 0</div>

  <div id="cards-grouped"><!-- render JS, una sección por grupo --></div>

  <div class="progress-bar-container" style="margin-top:24px;">
    <div class="progress-bar" id="pillsProgressBar"></div>
  </div>
  <div class="progress-label" id="pillsProgressLabel">Píldoras: 0 / 0</div>

  <div class="section-title">Efectos de píldora</div>
  <div id="pills-grid"></div>
  <div id="pills-pending-note" hidden style="color:#aaa; font-size:0.85rem; margin-top:12px;">
    Pendiente de verificación con un save con píldoras identificadas.
  </div>
</div>
```

- [ ] **Step 12.3: Cargar los inline JS**

Localizar los `<script src="items_inline.js">` y `<script src="trinkets_inline.js">` y añadir junto a ellos:

```html
<script src="cards_inline.js"></script>
<script src="pills_inline.js"></script>
```

- [ ] **Step 12.4: Verificación visual rápida**

Abrir `challenges.html` directamente en el navegador. Click en la pestaña "Cartas y Píldoras". Debe aparecer la vista vacía con las dos barras de progreso a 0 (los grids aún no se rellenan — eso es Task 14).

- [ ] **Step 12.5: Commit**

```bash
rtk git add challenges.html
rtk git commit -m "feat(ui): añadir pestaña Cartas y Píldoras (estructura)"
```

---

## Task 13: CSS — `.card-cell` y `.pill-cell`

**Files:**
- Modify: `challenges.html` (sección `<style>`, junto a las reglas de `#view-trinkets`)

- [ ] **Step 13.1: Reglas CSS**

Localizar el comentario CSS `/* ==== Trinkets tab — Cuadrícula adaptativa ... ==== */` y añadir, inmediatamente después del bloque de reglas de `.trinket-cell`:

```css
#view-cards .progress-bar-container,
#view-cards .progress-label { /* mismas reglas que items */ }

#view-cards #cards-grouped .section-title { margin-top: 16px; }

#view-cards .cards-grid,
#view-cards #pills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(64px, 1fr));
  gap: 6px;
  margin-bottom: 12px;
}

.card-cell, .pill-cell {
  aspect-ratio: 1;
  background: #16213e;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  transition: background 0.15s;
}
.card-cell:hover, .pill-cell:hover { background: #1f2a4a; }

.card-cell img, .pill-cell img {
  width: 80%;
  height: 80%;
  image-rendering: pixelated;
  filter: grayscale(100%) brightness(0.4);
  transition: filter 0.15s;
}
.card-cell.seen img, .pill-cell.seen img { filter: none; }
```

- [ ] **Step 13.2: Commit**

```bash
rtk git add challenges.html
rtk git commit -m "style(ui): estilos para card-cell y pill-cell (mirror de item-cell)"
```

---

## Task 14: JS — render + tooltips de cartas

**Files:**
- Modify: `challenges.html` (sección de JS, junto a `renderItemsGrid`/`showItemTooltip`)

- [ ] **Step 14.1: Funciones de render**

Después de `updateItemsProgress()`:

```js
const CARD_GROUPS = [
  { key: "tarot_mayor", label: "Tarot Mayor" },
  { key: "tarot_inverso", label: "Tarot Inverso" },
  { key: "runas", label: "Runas" },
  { key: "especiales", label: "Cartas Especiales" },
  { key: "objetos_alma", label: "Objetos del Alma" },
];

function renderCardsGrouped() {
  const root = document.getElementById('cards-grouped');
  if (!root || !window.CARDS_DATA) return;
  const seen = (window._cardsState || {});
  root.innerHTML = '';
  for (const grp of CARD_GROUPS) {
    const inGroup = window.CARDS_DATA.filter(c => c.group === grp.key);
    if (inGroup.length === 0) continue;
    const title = document.createElement('div');
    title.className = 'section-title';
    title.textContent = grp.label;
    root.appendChild(title);
    const grid = document.createElement('div');
    grid.className = 'cards-grid';
    for (const c of inGroup) {
      const cell = document.createElement('div');
      cell.className = 'card-cell' + (seen[String(c.id)] ? ' seen' : '');
      cell.dataset.cardId = c.id;
      cell.dataset.cardName = c.name;
      cell.dataset.cardDesc = c.desc || '';
      cell.dataset.cardGroup = c.group;
      const img = document.createElement('img');
      img.src = 'card_icons/' + c.sprite;
      img.alt = c.name;
      img.loading = 'lazy';
      img.style.pointerEvents = 'none';
      cell.appendChild(img);
      cell.addEventListener('mouseenter', () => showCardTooltip(cell));
      cell.addEventListener('mouseleave', hideTooltip);
      grid.appendChild(cell);
    }
    root.appendChild(grid);
  }
  updateCardsProgress();
}

function updateCardsProgress() {
  const seen = window._cardsState || {};
  const total = window.CARDS_DATA ? window.CARDS_DATA.length : 0;
  let done = 0;
  if (total) for (const c of window.CARDS_DATA) if (seen[String(c.id)]) done++;
  const pct = total ? Math.round((done / total) * 100) : 0;
  const bar = document.getElementById('cardsProgressBar');
  const lbl = document.getElementById('cardsProgressLabel');
  if (bar) bar.style.width = pct + '%';
  if (lbl) lbl.textContent = `Cartas: ${done} / ${total}  (${pct}%)`;
}

function showCardTooltip(cell) {
  if (_ctrlLocked) return;
  const name = cell.dataset.cardName || '';
  const desc = cell.dataset.cardDesc || 'Sin descripción.';
  const seen = cell.classList.contains('seen');
  const tierClass = seen ? 'tier-s' : 'tier-c';
  const statusChip = seen
    ? '<span class="tt-diff tier-s">✔ Vista</span>'
    : '<span class="tt-diff tier-c">✗ Te falta</span>';
  tooltipEl.innerHTML = `
    <div class="tt-card-header ${tierClass}">
      <div class="tt-head-row">
        <div class="tt-head-text">
          <span class="tt-title">${escapeHtml(name)}</span>
          <div class="tt-meta">Carta ${statusChip}</div>
        </div>
      </div>
    </div>
    <div class="tt-body">
      <div class="tt-block effect">
        <div class="tt-block-label">💫 Efecto</div>
        <div class="tt-block-body">${_descToHtml(desc)}</div>
      </div>
    </div>`;
  cancelHideTooltip();
  tooltipEl.classList.add('visible');
  positionTooltip(cell);
}
```

- [ ] **Step 14.2: Wire al cambio de pestaña**

En la función `switchTab` (o donde se gestione el cambio de view), añadir el caso `'cards'`:

```js
if (view === 'cards') { renderCardsGrouped(); renderPillsGrid(); }
```

(Si no existe un switch así, basta con llamar `renderCardsGrouped()` y `renderPillsGrid()` al arrancar como ya se hace con items/trinkets.)

- [ ] **Step 14.3: Hidratación de `_cardsState`**

Donde la app aplica `SAVE_STATE` (función `applyIsaacState` o equivalente que ya consume `items_state`), añadir:

```js
window._cardsState = state.cards_state || {};
window._pillsState = state.pills_state || {};
window._pillsVerified = !!state.pills_verified;
renderCardsGrouped();
renderPillsGrid();
```

- [ ] **Step 14.4: Smoke test en navegador**

Abrir `challenges.html` directo en Chrome/Edge → pestaña Cartas → debe verse la cuadrícula con grupos y todas las cartas en gris (no hay save aplicado todavía).

- [ ] **Step 14.5: Commit**

```bash
rtk git add challenges.html
rtk git commit -m "feat(ui): render + tooltip de cartas, agrupadas por tipo"
```

---

## Task 15: JS — render + tooltips de píldoras + nota de pendiente

**Files:**
- Modify: `challenges.html`

- [ ] **Step 15.1: Funciones de render** (paralelas a las de cartas, pero sin agrupar):

```js
function renderPillsGrid() {
  const grid = document.getElementById('pills-grid');
  const note = document.getElementById('pills-pending-note');
  if (!grid || !window.PILLS_DATA) return;
  const verified = !!window._pillsVerified;
  const seen = window._pillsState || {};
  grid.innerHTML = '';
  for (const p of window.PILLS_DATA) {
    const cell = document.createElement('div');
    const isSeen = verified && seen[String(p.id)];
    cell.className = 'pill-cell' + (isSeen ? ' seen' : '');
    cell.dataset.pillId = p.id;
    cell.dataset.pillName = p.name;
    cell.dataset.pillDesc = p.desc || '';
    const img = document.createElement('img');
    img.src = 'pill_icons/' + p.sprite;
    img.alt = p.name;
    img.loading = 'lazy';
    img.style.pointerEvents = 'none';
    cell.appendChild(img);
    cell.addEventListener('mouseenter', () => showPillTooltip(cell));
    cell.addEventListener('mouseleave', hideTooltip);
    grid.appendChild(cell);
  }
  if (note) note.hidden = verified;
  updatePillsProgress();
}

function updatePillsProgress() {
  const verified = !!window._pillsVerified;
  const seen = window._pillsState || {};
  const total = window.PILLS_DATA ? window.PILLS_DATA.length : 0;
  let done = 0;
  if (verified && total) for (const p of window.PILLS_DATA) if (seen[String(p.id)]) done++;
  const pct = total ? Math.round((done / total) * 100) : 0;
  const bar = document.getElementById('pillsProgressBar');
  const lbl = document.getElementById('pillsProgressLabel');
  if (bar) bar.style.width = pct + '%';
  if (lbl) lbl.textContent = `Píldoras: ${done} / ${total}  (${pct}%)`;
}

function showPillTooltip(cell) {
  if (_ctrlLocked) return;
  const name = cell.dataset.pillName || '';
  const desc = cell.dataset.pillDesc || 'Sin descripción.';
  const seen = cell.classList.contains('seen');
  const tierClass = seen ? 'tier-s' : 'tier-c';
  const statusChip = seen
    ? '<span class="tt-diff tier-s">✔ Identificada</span>'
    : '<span class="tt-diff tier-c">✗ No identificada</span>';
  tooltipEl.innerHTML = `
    <div class="tt-card-header ${tierClass}">
      <div class="tt-head-row">
        <div class="tt-head-text">
          <span class="tt-title">${escapeHtml(name)}</span>
          <div class="tt-meta">Efecto de píldora ${statusChip}</div>
        </div>
      </div>
    </div>
    <div class="tt-body">
      <div class="tt-block effect">
        <div class="tt-block-label">💊 Efecto</div>
        <div class="tt-block-body">${_descToHtml(desc)}</div>
      </div>
    </div>`;
  cancelHideTooltip();
  tooltipEl.classList.add('visible');
  positionTooltip(cell);
}
```

- [ ] **Step 15.2: Smoke test en navegador**

Tras step 15.1, en la pestaña Cartas y Píldoras debe verse la cuadrícula pequeña de píldoras (todas en gris) y la nota de pendiente visible si Task 10 no verificó el chunk.

- [ ] **Step 15.3: Commit**

```bash
rtk git add challenges.html
rtk git commit -m "feat(ui): render + tooltip de píldoras + nota de chunk pendiente"
```

---

## Task 16: Empaquetado — actualizar `build.spec` y `build_linux.spec`

**Files:**
- Modify: `build.spec`
- Modify: `build_linux.spec`

- [ ] **Step 16.1: `build.spec`**

Localizar el parámetro `datas=[…]` dentro del `Analysis(...)` y añadir las 4 entradas nuevas, manteniendo el formato `('source', 'dest')` que ya usa:

```python
datas=[
    ('tracker/assets/challenges.html', 'assets'),
    ('tracker/assets/bossrush.png', 'assets'),
    ('tracker/assets/marks', 'assets/marks'),
    ('tracker/assets/ach_icons', 'assets/ach_icons'),
    ('tracker/assets/icons', 'assets/icons'),
    ('tracker/assets/item_icons', 'assets/item_icons'),
    ('tracker/assets/card_icons', 'assets/card_icons'),      # NUEVO
    ('tracker/assets/pill_icons', 'assets/pill_icons'),      # NUEVO
    ('tracker/assets/items_inline.js', 'assets'),
    ('tracker/assets/trinkets_inline.js', 'assets'),
    ('tracker/assets/cards_inline.js', 'assets'),            # NUEVO
    ('tracker/assets/pills_inline.js', 'assets'),            # NUEVO
],
```

- [ ] **Step 16.2: `build_linux.spec`**

Aplicar exactamente los mismos cambios.

- [ ] **Step 16.3: Commit**

```bash
rtk git add build.spec build_linux.spec
rtk git commit -m "build: empaquetar card_icons, pill_icons y los inline JS nuevos"
```

---

## Task 17: Build .exe y smoke test final

**Files:** ninguno (acción).

- [ ] **Step 17.1: Build**

```bash
.\.venv\Scripts\pyinstaller.exe --noconfirm build.spec
```
Expected: `dist/IsaacTracker.exe` se genera sin errores. Tamaño ~150-200 MB.

- [ ] **Step 17.2: Lanzar y verificar**

```bash
.\dist\IsaacTracker.exe
```
Checklist manual:
- [ ] La pestaña "Cartas y Píldoras" aparece después de "Trinkets".
- [ ] Al hacer clic, se ven los grupos de cartas y la sección de píldoras.
- [ ] Las cartas vistas (del save real del usuario) aparecen en color.
- [ ] Las no vistas en gris.
- [ ] Hover sobre una carta → tooltip con nombre y efecto.
- [ ] Si `pills_verified=False`: la nota "Pendiente de verificación..." es visible.
- [ ] Si `pills_verified=True`: las píldoras identificadas en color, el resto en gris.
- [ ] Otras pestañas (Desafíos, Personajes, Logros, Ítems, Trinkets) siguen funcionando sin regresión.

- [ ] **Step 17.3: Commit final (si hay sync de assets HTML)**

```bash
rtk git add tracker/assets/challenges.html  # regenerado por build.spec
rtk git commit -m "build: sync assets HTML tras pestaña Cartas y Píldoras"
```

---

## Tarea de seguimiento (NO en este plan)

- **Traducción al español de descripciones de cartas y píldoras**: integrar EID es decir, extender `tools/build_eid.py` (o un equivalente `build_eid_cards.py`/`build_eid_pills.py`) para poblar `desc_es` en `cards.py` y `pills.py`. Igual que se hizo para ítems en commit `51d3169`.
- **Si chunk 10 no se verificó en V1**: cuando se consiga un save con píldoras identificadas, reabrir el gate del Task 10.

---

## Referencias

- Skill: `superpowers:test-driven-development`
- Skill: `superpowers:verification-before-completion`
- Skill: `superpowers:requesting-code-review`
- Spec: `docs/superpowers/specs/2026-05-14-cards-pills-tab-design.md`
