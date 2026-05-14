# Pestaña "Cartas y Píldoras"

**Fecha:** 2026-05-14
**Archivos afectados:**

_Lógica de datos:_
- `tracker/save_parser.py` — extraer dos nuevos chunks (cartas y, condicionalmente, píldoras). Extender `ParsedSave`. Actualizar `parse_save` (caller de `_extract_chunks`).
- `tracker/data/cards.py` *(nuevo, auto-generado)* — id → name/sprite/removed/desc_es para cartas.
- `tracker/data/pills.py` *(nuevo, auto-generado)* — id → name/sprite/desc_es/horse para efectos de píldora.
- `tests/test_save_parser.py` — añadir aserciones para `cards_seen` y `pills_seen`.

_Tooling (espejo del pipeline de ítems ya en uso):_
- `tools/build_cards.py` *(nuevo)* — análogo a `tools/build_collectibles.py`.
- `tools/build_pills.py` *(nuevo)* — ídem.
- `tools/build_cards_inline.py` *(nuevo)* — análogo a `tools/build_items_inline.py`; produce `tracker/assets/cards_inline.js`.
- `tools/build_pills_inline.py` *(nuevo)* — ídem para `pills_inline.js`.
- `tools/extract_card_icons.py`, `tools/extract_pill_icons.py` *(nuevos)* — extracción + optimización de PNG (paralelo a `tools/convert_item_icons.py` + `tools/optimize_sprites.py`).
- `tools/build_eid.py` — extender para extraer también descripciones EID de cartas y píldoras (o crear `tools/build_eid_cards.py`/`tools/build_eid_pills.py`; decisión local en implementación).

_Assets y UI:_
- `tracker/assets/card_icons/` *(nuevo)* — PNG optimizados.
- `tracker/assets/pill_icons/` *(nuevo)* — PNG optimizados.
- `tracker/assets/cards_inline.js` *(nuevo, generado)*.
- `tracker/assets/pills_inline.js` *(nuevo, generado)*.
- `challenges.html` (raíz) — nueva pestaña, secciones, estilos, funciones `showCardTooltip` / `showPillTooltip` y los `render*` correspondientes.
- `tracker/assets/challenges.html` — espejo regenerado por `build.spec` al construir.

_Empaquetado:_
- `build.spec` — añadir las dos carpetas de iconos y los dos `*_inline.js` a `datas`.
- `build_linux.spec` — equivalente.

**Tipo:** Nueva funcionalidad (UI + parsing + assets).

## Contexto

El tracker ya tiene cinco pestañas: **Desafíos**, **Personajes**, **Logros**, **Ítems** y **Trinkets**. Faltan dos colecciones que el juego sí muestra en su Collection Page: **Cartas** (Tarot, Runas, cartas especiales, Objetos del Alma) y **Píldoras** (efectos identificados).

Los specs previos `2026-05-13-isaac-save-tracker-design.md` y `2026-05-13-isaac-achievements-tab-design.md` definen el patrón: parser binario del save → estado serializable → render en `challenges.html`. Este spec extiende ese patrón a dos colecciones más.

El usuario es no técnico y prefiere las descripciones en español, pero acepta una primera versión con descripciones en inglés desde el mod EID (mismo origen que se usó para ítems) y una segunda pasada de traducción posterior.

## Decisiones del brainstorming

| Pregunta | Decisión |
|---|---|
| ¿Pestañas separadas o combinada? | Una sola pestaña "Cartas y Píldoras" |
| ¿Estilo visual e interacción? | Igual que **Ítems**: cuadrícula adaptativa, tooltip en hover sobre el elemento `#tooltip` global con nombre + descripción + sprite. Ctrl+Click bloquea el tooltip abierto (mecánica `_ctrlLocked` ya existente). NO hay modal/panel lateral separado. |
| ¿Agrupación de cartas? | Por tipo, secciones en este orden de arriba abajo: *Tarot Mayor*, *Tarot Inverso*, *Runas*, *Cartas Especiales*, *Objetos del Alma* |
| ¿Barra de progreso? | Dos: "Cartas: X / Y" y "Píldoras: X / Y" |
| ¿Idioma de descripciones en V1? | Inglés desde EID. Traducción al español en una segunda iteración |
| ¿Píldoras: qué se muestra? | Los efectos identificados al menos una vez. La asignación color→efecto es per-run y no se guarda |
| ¿Ubicación de la pestaña? | Última, después de Trinkets |
| ¿Filtros / buscador? | Fuera de alcance (idea separada) |

## Datos de origen — Save de Isaac

Inspección del fixture `tests/fixtures/sample_save_repentance_plus.dat` (jugador con 617/733 ítems vistos, 400 logros desbloqueados):

| Chunk type | count | entry size | ones (bytes=1) | Identificación |
|---:|---:|---:|---:|---|
| 1 | 642 | 1 B | 400 | Achievements (ya parseado) |
| 2 | 523 | 4 B | — | Counters |
| 3 | 14 | 4 B | — | Special counters |
| 4 | 733 | 1 B | 617 | Collectibles / Ítems (ya parseado) |
| 5 | 7 | 1 B | 7 | Desconocido (probable flags de eventos) |
| **6** | **104** | **1 B** | **97** | **Cartas vistas** (hipótesis fuerte: ~98 cartas en Repentance+) |
| 7 | 46 | 1 B | 30 | Challenges (ya parseado) |
| 8 | 27 | 4 B | — | Counters secundarios |
| 9 | 2 | 4 B | — | Desconocido |
| **10** | **80** | **1 B** | **0** | **Candidato a píldoras** (verificación pendiente — todos a 0 es sospechoso) |

`_ENTRY_SIZES` en `save_parser.py:93` ya cubre los tamaños de los chunks 6 y 10 (ambos 1 B). **No se toca esa tupla.**

### Verificación de chunks (gate antes de codificar UI)

**Cartas (chunk 6) — criterio:** generar la lista canónica de cartas desde el archivo `entities2.xml`/`pocketitems.xml` del juego o desde EID, comprobar que `len(CARDS) ∈ {97, 98, 99, 100, 104}` (margen para parches), y validar que `set(i for i,b in enumerate(chunk6_body) if b==1)` contiene los índices de al menos 5 cartas que el usuario confirme haber tocado (p.ej. The Fool, Death, Cracked Key, Soul of Isaac, Rune of Hagalaz). Si OK → chunk 6 = cartas.

**Píldoras (chunk 10) — criterio:** pedir al usuario un save donde haya identificado N píldoras concretas (mínimo 3 distintas, con sus nombres). Comprobar que `set(i for i,b in enumerate(chunk10_body) if b==1)` mapea a esos N efectos esperados (orden EID por id). Si OK → chunk 10 = píldoras. **Si NO se puede verificar** (no se consigue save adecuado, o el mapping no encaja), V1 entrega:
- Cartas funcional al 100%.
- Sección Píldoras visible con todos los efectos en gris y nota corta: *"Pendiente de verificación con un save con píldoras identificadas."*
- `_extract_pills_seen` retorna `set()` y no llama a la lógica de chunk 10 hasta verificación.

## Cambios en el parser

1. **Constantes nuevas** en `tracker/save_parser.py`:
   ```python
   _CHUNK_CARDS = 6
   _CHUNK_PILLS = 10
   ```

2. **Refactor previo de `_extract_chunks` a dict** (tarea independiente, antes de añadir chunks nuevos):
   ```python
   def _extract_chunks(data, path) -> dict[int, bytes]:
       """Return {chunk_type: body_bytes} for chunks we care about."""
   ```
   Devuelve `{1: ach, 4: items, 7: challenges, ...}`. `parse_save` se adapta a consumir el dict. **Gate:** los tests existentes (`test_save_parser.py` actuales) deben pasar sin cambios funcionales antes de tocar nada nuevo. Si esto introduce regresiones, se revierte y se vuelve al patrón de tupla extendida.

3. **Una vez aprobado el refactor**, el dict pasa a incluir también `{6: cards, 10: pills_or_None}`.

4. **Contrato de error** (consistencia explícita):
   - Chunks **1, 4, 6, 7**: si falta o está truncado → `SaveParseError` con mensaje en español (igual que los actuales).
   - Chunk **10**: tratamiento tolerante. Si falta o llega vacío → `pills_seen = set()`, `pills_verified = False` y se loguea con `print` (no se rompe el parse). Razón: durante el periodo de verificación queremos que la app abra aunque el chunk no esté disponible.

5. **`_extract_cards_seen` y `_extract_pills_seen`** con la misma lógica que `_extract_items_seen` (byte==1 → id en el set). `_extract_pills_seen` se ejecuta siempre que el chunk 10 esté presente; el flag `pills_verified` lo controla `parse_save` según el resultado del gate de verificación (sección anterior).

6. **`ParsedSave`** se extiende:
   ```python
   cards_seen: set[int] = field(default_factory=set)
   pills_seen: set[int] = field(default_factory=set)
   pills_verified: bool = False   # True solo si pasó el gate de verificación de chunk 10
   ```
   `pills_verified` se serializa también en `window.SAVE_STATE` y la UI lo consulta para mostrar la nota "pendiente de verificación".

6. **Tests en `tests/test_save_parser.py`:**
   - `test_cards_seen_from_fixture`: `len(parsed.cards_seen) == 97` con el fixture actual.
   - `test_pills_seen_from_fixture`: `parsed.pills_seen == set()` con el fixture (todos a 0).
   - `test_cards_chunk_truncated_raises`: cortar el archivo dentro del chunk 6 → `SaveParseError`.
   - `test_pills_chunk_truncated_returns_empty`: cortar dentro del chunk 10 → `pills_seen == set()`, no excepción.

## Catálogos de datos

### `tracker/data/cards.py` (auto-generado por `tools/build_cards.py`)

Forma idéntica a `collectibles.py`:

```python
CARDS: dict[int, dict] = {
    0: {'name': '', 'sprite': '', 'removed': True, 'desc_es': '', 'group': ''},
    1: {'name': '0 - The Fool', 'sprite': 'card_001.png', 'removed': False,
        'desc_es': 'Te teletransporta a la primera habitación del piso.',
        'group': 'tarot_mayor'},
    ...
}
```

`group ∈ {'tarot_mayor', 'tarot_inverso', 'runas', 'especiales', 'objetos_alma'}`.

`tools/build_cards.py` construye este dict combinando:
- Lista canónica de IDs y nombres del juego (XML del juego o tabla del wiki).
- Descripciones en español (V2): de EID. En V1 quedan vacías y el inline JS hace fallback a inglés.

### `tracker/data/pills.py` (auto-generado por `tools/build_pills.py`)

```python
PILLS: dict[int, dict] = {
    1: {'name': 'Bad Trip', 'sprite': 'pill_bad_trip.png', 'desc_es': '',
        'horse': False},
    ...
}
```

Mismo patrón que `cards.py`.

## Assets — iconos

1. **Cartas** (~98 PNG):
   - Origen: `Steam/steamapps/common/The Binding of Isaac Rebirth/resources/gfx/ui/cards/`.
   - Script `tools/extract_card_icons.py`: copia los PNG originales, los renombra a `card_<id>.png` (zero-padded), los optimiza con `optipng` igual que el flujo de items.
   - Destino: `tracker/assets/card_icons/`.

2. **Píldoras** (~50 PNG):
   - Origen: `resources/gfx/items/pills/` del juego.
   - Mismo flujo en `tools/extract_pill_icons.py`.
   - Destino: `tracker/assets/pill_icons/`.

## Inline JS (consumido por `challenges.html`)

`tools/build_cards_inline.py` produce `tracker/assets/cards_inline.js`:

```js
window.CARDS_DATA = [
  {id:1, name:"0 - The Fool", sprite:"card_001.png", desc:"...", group:"tarot_mayor"},
  ...
];
```

`tools/build_pills_inline.py` produce `tracker/assets/pills_inline.js`:

```js
window.PILLS_DATA = [
  {id:1, name:"Bad Trip", sprite:"pill_bad_trip.png", desc:"...", horse:false},
  ...
];
```

Ambos siguen el formato compacto de `items_inline.js` ya en producción.

## Cambios en `challenges.html`

### Pestaña

```html
<button class="tab" data-view="cards">Cartas y Píldoras</button>
```

### Vista

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
  <div id="pills-pending-note" hidden>
    Pendiente de verificación con un save con píldoras identificadas.
  </div>
</div>
```

### Estilos

Reutilizar el patrón de `.item-cell`. Añadir:

```css
#view-cards .cards-grid,
#view-cards #pills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(64px, 1fr));
  gap: 6px;
}
.card-cell, .pill-cell { /* mismo box-model que .item-cell */ }
.card-cell img, .pill-cell img {
  filter: grayscale(100%) brightness(0.4);
  transition: filter 0.15s;
}
.card-cell.seen img, .pill-cell.seen img { filter: none; }
```

### Lógica JS

Mirror **exacto** de `showItemTooltip(cell)` y `showTrinketTooltip(cell)`:

```js
function showCardTooltip(cell) { /* lee CARDS_DATA por data-card-id, rellena #tooltip */ }
function showPillTooltip(cell) { /* lee PILLS_DATA por data-pill-id, rellena #tooltip */ }
```

Cada celda al renderizarse:
```js
cell.addEventListener('mouseenter', () => showCardTooltip(cell));
cell.addEventListener('mouseleave', hideTooltip);
```

Ctrl+Click ya está cubierto por el listener global del `#tooltip`.

### Render

```js
function renderCardsGrouped() {
  const grid = document.getElementById('cards-grouped');
  const groups = ['tarot_mayor','tarot_inverso','runas','especiales','objetos_alma'];
  // por grupo → <div class="section-title"> + <div class="cards-grid"> con celdas
}
function renderPillsGrid() { /* similar, sin grupos */ }
```

Las celdas reciben clase `.seen` si `SAVE_STATE.cards_seen.has(id)` / `SAVE_STATE.pills_seen.has(id)`.

Si `SAVE_STATE.pills_verified === false` (gate del parser), `#pills-pending-note` se hace visible y todas las celdas se renderizan como `.unseen`.

## Empaquetado (PyInstaller)

Añadir a `datas` en `build.spec` y `build_linux.spec`, siguiendo el formato existente (directorio destino bajo `assets/...`, no `tracker/assets/...`):

```python
('tracker/assets/card_icons', 'assets/card_icons'),
('tracker/assets/pill_icons', 'assets/pill_icons'),
('tracker/assets/cards_inline.js', 'assets'),
('tracker/assets/pills_inline.js', 'assets'),
```

## Flujo runtime completo

1. `parse_save(path)` → `ParsedSave(cards_seen=..., pills_seen=...)`.
2. `tracker/app.py` serializa los sets a JSON e inyecta en `window.SAVE_STATE` (mecanismo ya existente para `items_seen`).
3. `challenges.html` al cambiar a la pestaña "Cartas y Píldoras" llama a `renderCardsGrouped()` y `renderPillsGrid()`, que aplican `.seen` y actualizan las dos barras de progreso.

## Qué NO entra en V1

- Traducción al español de descripciones de cartas y píldoras (segunda iteración).
- Filtros / buscador (idea separada).
- Estadísticas de uso por carta o píldora.
- Distinción visual Horse Pill vs regular en la cuadrícula.
- Pills funcional si el gate de verificación falla → se entrega solo cartas, píldoras en gris con la nota.

## Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| Chunk 6 no es cartas | Probar chunk 10. Si ninguno encaja, pedir al usuario verificar in-game qué cartas tiene "vistas" en la Collection Page y contrastar índices. |
| Chunk 10 no es píldoras | Fallback ya definido (sección en gris + nota). |
| EID no incluye cartas/píldoras de forma uniforme | Procesar el `.lua` del mod manualmente o caer al texto del juego. Lista canónica son ~98 + ~50 entradas, manejable a mano. |
| Crecimiento del `.exe` | Iconos pesan poco tras `optipng`; coste despreciable frente a los 717 PNG ya empaquetados. |
| Regresión en pestañas existentes al refactorizar `_extract_chunks` a dict | Tests existentes deben seguir pasando antes de mergear; añadir test de regresión que verifique items/challenges/achievements sin cambios. |

## Seguimiento posterior (NO en este spec)

- Traducción al español de descripciones de cartas y píldoras (equivalente al commit `51d3169` para ítems).
- Si V1 entrega píldoras en fallback: identificación definitiva del chunk en una iteración posterior cuando consigamos un save con identificaciones conocidas.
- Posible buscador / filtros transversales (Ítems / Cartas / Píldoras).
