# Pestaña "Cartas y Píldoras"

**Fecha:** 2026-05-14
**Archivos afectados principales:**
- `challenges.html` (raíz) — añade pestaña, secciones, estilos y lógica de render
- `tracker/assets/challenges.html` — espejo del anterior, regenerado por el build
- `tracker/save_parser.py` — extrae el chunk de cartas (y el de píldoras, una vez identificado)
- `tracker/data/cards.py` (nuevo) — catálogo de cartas con id, nombre, grupo, descripción
- `tracker/data/pills.py` (nuevo) — catálogo de efectos de píldora
- `tools/extract_card_icons.py` y `tools/extract_pill_icons.py` (nuevos) — extracción y conversión de iconos
- `tracker/assets/card_icons/`, `tracker/assets/pill_icons/` (nuevas carpetas con PNG optimizados)
- `tracker/assets/cards_inline.js`, `tracker/assets/pills_inline.js` (nuevos, generados por `_build_inline.py`)
- `tests/test_save_parser.py` — añadir aserciones para los nuevos chunks
- `build.spec` y `build_linux.spec` — incluir las nuevas carpetas/archivos como `datas`

**Tipo:** Nueva funcionalidad (UI + parsing + assets).

## Contexto

El tracker ya tiene cinco pestañas: **Desafíos**, **Personajes**, **Logros**, **Ítems** y **Trinkets**. Faltan dos colecciones que el juego sí muestra en la Collection Page: **Cartas** (Tarot, Runas, cartas especiales, Objetos del Alma) y **Píldoras** (efectos identificados).

Los specs previos `2026-05-13-isaac-save-tracker-design.md` y `2026-05-13-isaac-achievements-tab-design.md` definen el patrón: parser binario del save → estado serializable → render en `challenges.html`. Este spec extiende ese patrón a dos colecciones más.

El usuario es no técnico y prefiere las descripciones en español, pero acepta una primera versión con descripciones en inglés desde el mod EID (mismo origen que se usó para ítems) y una segunda pasada de traducción posterior.

## Decisiones del brainstorming

| Pregunta | Decisión |
|---|---|
| ¿Pestañas separadas o combinada? | **Una sola pestaña** "Cartas y Píldoras" |
| ¿Estilo visual? | Igual que **Ítems**: cuadrícula adaptativa, hover con nombre, clic abre tarjeta lateral con descripción |
| ¿Agrupación de cartas? | Por tipo: *Tarot Mayor*, *Tarot Inverso*, *Runas*, *Cartas Especiales*, *Objetos del Alma* (orden de subsecciones de arriba hacia abajo) |
| ¿Barra de progreso? | Dos: "Cartas: X / Y" y "Píldoras: X / Y" |
| ¿Idioma de descripciones en V1? | Inglés de EID. Traducción al español en una segunda iteración |
| ¿Píldoras: qué se muestra? | Los efectos identificados al menos una vez, no la asignación color→efecto (esa es per-run y no se guarda) |
| ¿Ubicación de la pestaña? | Última, después de Trinkets |
| ¿Filtros / buscador? | **Fuera de alcance** (idea separada, se planteó pero no se decidió ahora) |

## Datos de origen — Save de Isaac

Inspección del fixture `tests/fixtures/sample_save_repentance_plus.dat` (archivo de un jugador con 617/733 ítems vistos, 400 logros desbloqueados):

| Chunk type | count | entry size | ones (bytes=1) | Identificación |
|---:|---:|---:|---:|---|
| 1 | 642 | 1 B | 400 | Achievements (ya parseado) |
| 2 | 523 | 4 B | — | Counters |
| 3 | 14 | 4 B | — | Special counters |
| 4 | 733 | 1 B | 617 | Collectibles / Ítems (ya parseado) |
| 5 | 7 | 1 B | 7 | Desconocido (todos a 1 — probablemente flags de eventos) |
| **6** | **104** | **1 B** | **97** | **Cartas vistas** (hipótesis fuerte: ~98 cartas en Repentance+) |
| 7 | 46 | 1 B | 30 | Challenges (ya parseado) |
| 8 | 27 | 4 B | — | Counters secundarios |
| 9 | 2 | 4 B | — | Desconocido |
| 10 | 80 | 1 B | 0 | Posible candidato a píldoras pero todos a 0 en este fixture |

**Plan de identificación final (durante implementación, no en este spec):**
1. **Cartas:** asumir chunk 6 (count 104, 97 ones encaja con ~98 cartas existentes). Verificar contrastando byte[index]=1 con cartas que el jugador del fixture confirme haber tocado.
2. **Píldoras:** chunk 10 (80 entradas) es el candidato más probable por descarte, pero todos los bytes están a 0 en el fixture (lo que es raro). Si no podemos verificarlo con certeza, se hace fallback:
   - **Fallback aceptable:** entregar la pestaña con **Cartas funcional** y la sección de **Píldoras visible pero marcada "pendiente de identificar"** (todas en gris), con una nota en el texto. La traducción y el chunk de píldoras se completan en una iteración posterior cuando consigamos un save con identificaciones.

> Importante: la decisión de qué chunk es cuál se valida en la primera tarea de implementación con datos reales, no se asume aquí. Si el chunk 6 no fuese cartas, se prueba el 10 antes de bloquear el progreso.

## Catálogo de datos (Python)

### `tracker/data/cards.py`

Estructura por carta:

```python
@dataclass(frozen=True)
class Card:
    id: int            # índice en el chunk de cartas del save
    name: str          # ej: "0 - The Fool"
    group: str         # "tarot_mayor" | "tarot_inverso" | "runas" | "especiales" | "objetos_alma"
    description: str   # en inglés (EID) en V1; en español en V2
    sprite: str        # nombre de fichero relativo a card_icons/

CARDS: tuple[Card, ...] = (...)  # ~98 entradas
```

Fuente de la lista: el mod EID exporta las cartas con id, nombre y descripción. Mismo flujo que `tracker/data/eid_descriptions.py` ya usado para ítems.

### `tracker/data/pills.py`

```python
@dataclass(frozen=True)
class PillEffect:
    id: int            # índice en el chunk de píldoras
    name: str          # ej: "Health Up"
    description: str   # en inglés (EID) en V1
    sprite: str        # nombre de fichero relativo a pill_icons/
    horse: bool        # True para la variante Horse Pill

PILLS: tuple[PillEffect, ...] = (...)
```

## Cambios en el parser

En `tracker/save_parser.py`:

1. Añadir constantes:
   ```python
   _CHUNK_CARDS = 6
   _CHUNK_PILLS = 10   # tentativo, validar en implementación
   ```
2. Ampliar `_extract_chunks` para que devuelva también `cards_body` y `pills_body` (manteniendo los retornos existentes — se cambia la firma; es código privado del parser).
3. Añadir `_extract_cards_seen(cards_body) -> set[int]` y `_extract_pills_seen(pills_body) -> set[int]`, ambos con la misma lógica byte==1 que `_extract_items_seen`.
4. Extender el dataclass `ParsedSave`:
   ```python
   cards_seen: set[int] = field(default_factory=set)
   pills_seen: set[int] = field(default_factory=set)
   ```
5. Tests en `tests/test_save_parser.py`:
   - Smoke test: contar bytes==1 en chunks 6 y 10 del fixture y verificar que `len(cards_seen)`/`len(pills_seen)` coinciden (97 y 0 con los números actuales).
   - Robustez: chunk faltante o truncado debe levantar `SaveParseError` con mensaje en español, como los chunks existentes.

## Cambios en la UI (`challenges.html`)

### Botón de pestaña

```html
<button class="tab" data-view="cards">Cartas y Píldoras</button>
```

Añadir al final del bloque `.tabs`.

### Vista

```html
<div class="view" id="view-cards">
  <!-- Sección Cartas -->
  <div class="progress-bar-container">
    <div class="progress-bar" id="cardsProgressBar"></div>
  </div>
  <div class="progress-label" id="cardsProgressLabel">Cartas: 0 / 0</div>

  <div id="cards-grouped">
    <!-- Renderizado por JS, una sección por grupo -->
    <!-- Estructura por grupo:
      <div class="section-title">Tarot Mayor</div>
      <div class="cards-grid">
        <div class="card-cell seen|unseen" data-card-id="0">
          <img src="card_icons/the_fool.png">
        </div>
        ...
      </div>
    -->
  </div>

  <!-- Sección Píldoras -->
  <div class="progress-bar-container" style="margin-top:24px;">
    <div class="progress-bar" id="pillsProgressBar"></div>
  </div>
  <div class="progress-label" id="pillsProgressLabel">Píldoras: 0 / 0</div>

  <div class="section-title">Efectos de píldora</div>
  <div id="pills-grid"></div>
</div>
```

### Estilos

Reutilizar las reglas existentes de `.items-grid` / `.trinket-cell`:

```css
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
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  position: relative;
}
.card-cell img, .pill-cell img {
  width: 80%; height: 80%;
  image-rendering: pixelated;
  filter: grayscale(100%) brightness(0.4);
  transition: filter 0.15s;
}
.card-cell.seen img, .pill-cell.seen img {
  filter: none;
}
.card-cell:hover, .pill-cell:hover { background: #1f2a4a; }
```

### Tarjeta lateral / modal de detalle

Reutilizar el componente que ya muestra detalle de ítems al hacer clic. Solo cambia la fuente de datos (`CARDS_DATA`/`PILLS_DATA` en vez de `ITEMS_DATA`). Si el componente actual está acoplado a ítems, se factoriza en una función `showDetail({title, sprite, description})` y se llama desde las tres pestañas (Ítems, Cartas, Píldoras).

### Carga de datos

`cards_inline.js` y `pills_inline.js`, generados por `tracker/data/_build_inline.py`, exportan `window.CARDS_DATA` y `window.PILLS_DATA` desde los Python `cards.py`/`pills.py`. Se incluyen vía `<script src=...>` al final del HTML, como `items_inline.js`.

## Assets — iconos

1. **Cartas** (~98 PNG):
   - Origen: archivos del juego en `Steam/steamapps/common/The Binding of Isaac Rebirth/resources/gfx/ui/cards/`.
   - Script `tools/extract_card_icons.py`: copia los `.png` originales, los recorta al área visible si hace falta, los optimiza con `optipng` igual que `tools/optimize_sprites.py`.
   - Destino: `tracker/assets/card_icons/<nombre_kebab>.png`.

2. **Píldoras** (~50 PNG):
   - Origen: `Steam/steamapps/common/The Binding of Isaac Rebirth/resources/gfx/items/pills/`.
   - Misma idea con `tools/extract_pill_icons.py`.

3. **Empaquetado del .exe:**
   - En `build.spec` añadir `('tracker/assets/card_icons/*', 'tracker/assets/card_icons')` y `('tracker/assets/pill_icons/*', 'tracker/assets/pill_icons')` a `datas`.
   - En `build_linux.spec` la misma adición.

## Flujo de actualización completo (resumen)

1. Parser lee el save → produce `ParsedSave` con `cards_seen` y `pills_seen` añadidos.
2. La GUI llama al parser, serializa los sets a JSON, inyecta en `window.SAVE_STATE` (mecanismo ya existente).
3. El JS de `challenges.html` lee `SAVE_STATE.cards_seen` y `SAVE_STATE.pills_seen` y aplica clases `.seen` a las celdas correspondientes.

## Qué NO entra en V1

- **Traducción al español de las descripciones** (segunda iteración, ya acordada con el usuario).
- **Filtros / buscador en cartas o píldoras** (idea separada).
- **Estadísticas de uso** (cuántas veces se ha usado cada carta) — el save no expone eso por carta concreta de forma fiable.
- **Distinción visual Horse Pill vs regular** en la cuadrícula. Si en V2 se quiere, se añade un badge.
- **Píldoras con datos reales si el chunk no se verifica.** Si tras la fase de identificación seguimos sin certeza sobre el chunk de píldoras, la sección de píldoras se ENTREGA visible pero con todos los efectos en gris y una nota corta: *"Pendiente de verificación con un save con píldoras identificadas."* Cartas no depende de eso y sí se entrega completo.

## Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| El chunk 6 no es cartas | Probar chunk 10 antes de bloquear. Si ninguno encaja, contrastar con un nuevo save con cartas identificadas conocidas (igual que se hizo para items). |
| EID no exporta cartas con la misma estructura que items | Procesar el `.lua` del mod manualmente o usar el wiki como respaldo. La lista canónica son solo ~98 entradas; aceptable poblarla a mano si toca. |
| Iconos del juego con fondos o paddings inconsistentes | Reutilizar `tools/optimize_sprites.py` y el flujo ya conocido de items/trinkets. |
| Crecimiento del `.exe` por +150 PNG | Pesan poco (~30-60 KB cada uno tras optimizar); coste despreciable comparado con los 717 PNG de ítems ya empaquetados. |

## Seguimiento posterior (NO en este spec)

- Traducción al español de descripciones de cartas y píldoras (segunda iteración, similar al commit `51d3169` para ítems).
- Identificación definitiva del chunk de píldoras si V1 entrega solo cartas.
- Posible buscador / filtros transversales para Ítems / Cartas / Píldoras (idea pendiente del usuario).
