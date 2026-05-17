# Rediseño de la pestaña Estadísticas

**Fecha:** 2026-05-17
**Estado:** Diseño aprobado, pendiente de plan de implementación.

## 1. Problema

La pestaña Estadísticas actual es funcional pero pobre. Auditoría rápida sobre
el save real del usuario:

- **Bug de conteo**: la card "Enemigos distintos vistos" muestra `342 / 282`.
  El numerador supera al denominador, lo cual es lógicamente imposible. El
  numerador está sumando entradas a nivel (type, variant) mientras que el
  denominador parece contar a nivel `type`.
- **Sprites rotos**: muchos enemigos (Dangle, Mulligan, Pin, Dinga, Scolex,
  Headlesshorseman, Hopperleaper, Fatty, Floating Knight…) se muestran como
  rectángulos largos porque se está sirviendo la hoja de animación entera en
  vez de un frame único.
- **Filtros duplicados visuales**: las dos filas de chips (Vistos/Todos y
  All/Enemigos/Mini-bosses/Bosses) muestran dos botones "Todos" pegados, lo
  cual es confuso.
- **Cards globales secas**: solo 4 números, sin contexto, sin progreso
  visualizado, sin destacados. La info detallada por enemigo (deaths, hits,
  encounters) está enterrada en un tooltip al hover.
- **Sin jerarquía**: un boss del juego (Mom) y un enemigo común (Fly) ocupan
  el mismo tamaño y peso visual.
- **Sin segmentación**: el bestiario es un grid plano gigante sin agrupación
  por capítulo del juego.
- **Estética inconsistente**: paleta azul desalineada con el resto del tracker
  (Ítems/Trinkets/Cartas usan paleta naranja).
- **Emojis**: la constante `STATS_ICONS` usa emojis unicode (💀, 🪦, 💔, 👁)
  que el usuario considera ruido visual.

## 2. Alcance

Rediseño completo del `#stats-view` aplicado a `challenges.html` (raíz), su
copia `tracker/assets/challenges.html`, y el productor de datos
`tracker/state_mapper.py:_build_stats_state`. Cambios paralelos en
`tools/build_bestiary.py`, `tracker/data/bestiary.py`, y nuevos sprites
descargados desde la wiki a `tracker/assets/bestiary_icons/` y bundleados
inline (mismo patrón que `items_inline.js` y `trinkets_inline.js`).

Fuera de alcance: cambios en el parser del save (`tracker/save_locator.py`,
`tracker/parser_*`) — los datos que ya extraemos son suficientes.

## 3. Diseño

### 3.1 Layout final de la pestaña

De arriba abajo:

1. **Buscador "Ir al enemigo"** — copia exacta del componente `items-jump-row`
   con su CSS: label "Ir al enemigo:", input naranja con `<datalist>` para
   autocomplete, botón "Buscar" con gradiente naranja, hint "o pulsa Enter".
   Comportamiento: al confirmar, hace `scrollIntoView` + clase `.jump-highlight`
   sobre la celda destino (igual que la pestaña Ítems).

2. **Bloque superior en dos columnas** (`iso-top`, `grid-template-columns: 1fr 2fr`):
   - **Izquierda — Trayectoria global**: 4 cards apiladas en columna:
     - "Enemigos eliminados" (kills totales)
     - "Te han matado" (deaths totales)
     - "Golpes recibidos" (hits totales)
     - "Bestiario" con valor `N / M` + texto "faltan X enemigos" + barra de
       progreso naranja.
   - **Derecha — Bosses derrotados**: cabecera "Bosses derrotados X / 13" +
     grid (~78px por celda) con los 13 big bosses. Cada celda muestra:
     sprite de wiki (48px), nombre en es/en, kills en naranja + deaths
     pequeño en rojo. Big boss nunca derrotado → opacidad reducida, sprite
     placeholder "?", solo nombre.

3. **Bestiario completo**:
   - Toolbar: chips Vistos/Todos + separador + chips Enemigos/Mini-bosses +
     separador + `<select>` con orden ("Por capítulo" default · "Por kills" ·
     "Alfabético").
   - Grid agrupado por capítulo del juego cuando el sort es "Por capítulo".
     Cada cabecera de capítulo: badge "CAP N" + lista de pisos incluidos en
     gris + contador "X / Y" + línea separadora + mini-barra de progreso.
     Otros sorts (kills/alfabético) aplanan los grupos.
   - Cada celda enemigo: sprite (40px), nombre, fila pequeña con kills
     (naranja) y deaths (rojo) visibles sin hover.
   - Mini-bosses se marcan con tag "MB" amarillo en la esquina superior
     derecha.
   - Tooltip al hover sigue mostrando kills + deaths + hits + encounters
     (idéntico al actual).

### 3.2 Definición de "big boss"

Los 13 big bosses son los mismos que ya están en `MARK_BOSS_SPRITES` en
`challenges.html` — las casillas que aparecen en las marcas de completitud de
cada personaje. **No todos tienen una entrada `(type, variant)` en
`BESTIARY_CATALOG`**: Boss Rush es un evento de juego, Ultra Greedier es una
transformación de Ultra Greed, y Mega Satan no está catalogado actualmente.
Estos casos se resuelven con un mapeo explícito definido durante la
implementación de la tarea 1:

| Idx | Nombre | Fuente de datos |
|-----|--------|-----------------|
| 0 | Mom's Heart / It Lives | `(78, 0)` en BESTIARY_CATALOG |
| 1 | Isaac (boss) | `(102, 0)` o equivalente — verificar en build |
| 2 | Satan | catalog lookup |
| 3 | ??? (Blue Baby) | catalog lookup |
| 4 | The Lamb | catalog lookup |
| 5 | Boss Rush | **evento** — kills/deaths no aplican; se muestra como "completado" usando `parsed.character_marks` (mark 5) sin counter numérico |
| 6 | Hush | catalog lookup |
| 7 | Mega Satan | si no está en catálogo, añadir entrada manual al build con kills=0 hasta que se confirme su (type, variant) real |
| 8 | Ultra Greed | catalog lookup |
| 9 | Ultra Greedier | **transformación** — se muestra como "completado" usando `parsed.character_marks` (mark 9) sin counter numérico independiente |
| 10 | Delirium | catalog lookup |
| 11 | Mother | catalog lookup |
| 12 | The Beast | catalog lookup |

El build de la tarea 1 produce una constante `BIG_BOSS_TO_BESTIARY` en
`tracker/data/big_bosses.py` (módulo nuevo) con el mapeo idx → (type, variant)
o `None`. Para los `None`, el frontend renderiza la celda con:
- Sprite tomado directamente de `MARK_BOSS_SPRITES[idx]` (URL local
  bundleada o ya inline; sin contadores numéricos).
- Etiqueta "✓ Completado" si la mark correspondiente está en
  `parsed.character_marks` para algún personaje; vacío si no.

Los big bosses que **sí** tienen entrada en BESTIARY_CATALOG no aparecen
adicionalmente en el bestiario por capítulo de abajo — son excluidos de
`bestiary_list` por su `(type, variant)` cuando se construye la respuesta.

### 3.3 Mapeo capítulo del juego

`tools/build_bestiary.py` se amplía con una tabla `ENEMY_TYPE_TO_CHAPTER` que
mapea cada `type` de enemigo a su capítulo. La asignación se hace por el piso
canónico donde aparece el enemigo por primera vez:

| Cap | Pisos incluidos |
|-----|-----------------|
| 1 | Basement, Cellar, Burning Basement, Downpour, Dross |
| 2 | Caves, Catacombs, Flooded Caves, Mines, Ashpit |
| 3 | Depths, Necropolis, Dank Depths, Mausoleum, Gehenna |
| 4 | Womb, Utero, Scarred Womb, Corpse |
| 5 | Sheol, Cathedral |
| 6 | Dark Room, Chest |
| 7 | Void, Home |
| extra | Mini-bosses recurrentes, bosses no big-boss, enemigos sin piso canónico |

**Fuente canónica**: la wiki oficial (`bindingofisaacrebirth.wiki.gg/wiki/Monsters`)
publica una lista "Monsters by Floor" — esa página se usa como input para
generar el mapeo. La tarea 1 incluye un script auxiliar
(`tools/scrape_chapter_mapping.py`, o tabla escrita a mano si la wiki es
demasiado volátil) que produce `ENEMY_TYPE_TO_CHAPTER: dict[int, int|str]`
en `tracker/data/chapters.py` (módulo nuevo).

**Reglas de desempate** cuando un enemigo aparece en múltiples capítulos:
1. Se asigna al capítulo más bajo en el que aparece (primer encuentro
   esperado del jugador).
2. Las variantes (`variant > 0`) heredan el capítulo del `type` base salvo
   override explícito en una tabla `VARIANT_OVERRIDES: dict[tuple[int,int], int|str]`
   en el mismo módulo.

**Entradas sin mapeo** caen automáticamente en `"extra"` y se muestran al
final del bestiario en una sección "Otros" — ningún enemigo se pierde.

### 3.4 Fuente de sprites

Wiki oficial (`bindingofisaacrebirth.wiki.gg`), idéntico patrón al que ya
usamos para sprites de boss-marks en personajes. Pipeline:

1. `tools/download_bestiary_sprites.py` construye URLs por nombre, descarga
   PNGs a `tracker/assets/bestiary_icons/<type>_<variant>.png`.
2. Recorte de hoja de animación al primer frame:
   - Si la imagen es cuadrada (`width == height`), se usa tal cual.
   - Si es horizontal y `width % height == 0`, se asume `width / height`
     frames y se recorta al primer frame de `height × height`.
   - Si es vertical o el ratio no encaja, se conserva la imagen entera y se
     marca para revisión manual en un `bestiary_sprite_review.log`.
3. `tracker/data/_build_inline.py` regenera `tracker/assets/bestiary_inline.js`
   con cada PNG como base64 (igual que items/trinkets).
4. El bundler Nuitka ya incluye `bestiary_inline.js` — verificado en commit
   `7a72855`.

Esto sustituye la fuente actual que produce sprites cortados. Para entradas
sin sprite descargable (404 en wiki), se conserva el sprite actual como
fallback y se loggea para revisión.

### 3.5 Corrección del bug 342/282

Causa real (confirmada leyendo `tracker/state_mapper.py:104-117`): el
numerador `len(all_seen_tv)` es `len(set(kills_tv) | set(encounters_tv))`,
que incluye `(type, variant)` que **están en el save pero no en el
catálogo** (variantes que no hemos cubierto al generar `BESTIARY_CATALOG`).
El denominador `len(BESTIARY_CATALOG)` es 282; el numerador puede subir
hasta 342 porque el save trackea variantes adicionales.

Solución: filtrar el numerador a la intersección con el catálogo:

```python
all_seen_in_catalog = (set(kills_tv) | set(encounters_tv)) & set(BESTIARY_CATALOG.keys())
unique_seen_count = len(all_seen_in_catalog)
```

Y propagar `all_seen_in_catalog` (no `all_seen_tv`) al cálculo de `seen`
por entrada en `bestiary_list`. Test nuevo en `tests/test_stats_state.py`:

```python
def test_unique_seen_never_exceeds_catalog():
    # Simula save con variantes fuera del catálogo
    state = _build_stats_state(_parsed(bestiary_kills={
        0x02D00000: 5,  # Mom (sí en catálogo)
        0xFFFFFFF0: 3,  # variante inventada (no en catálogo)
    }))
    by_key = {g["key"]: g for g in state["globals"]}
    assert by_key["unique_seen"]["value"] <= by_key["unique_seen"]["max"]
```

### 3.6 Contrato `stats_state` actualizado

Se mantienen los nombres de keys actuales en `globals` (para no romper
tests existentes ni el frontend que indiza por `key`); se añade un global
nuevo `bosses_defeated` y se renombra solo la `label_es` de `unique_seen`
a "Bestiario". El campo `icon` se conserva como dato, pero el frontend
**ya no lo mapea a emoji** — se ignora o se usa como clase CSS opcional.
La constante `STATS_ICONS` en `challenges.html` se elimina.

```python
stats_state = {
    "globals": [
        {"key": "total_kills",      "label_es": "Enemigos eliminados",
         "value": int, "icon": "skull"},
        {"key": "total_deaths_by",  "label_es": "Te han matado",
         "value": int, "icon": "tombstone"},
        {"key": "total_hits",       "label_es": "Golpes recibidos",
         "value": int, "icon": "heart_broken"},
        {"key": "unique_seen",      "label_es": "Bestiario",
         "value": int, "max": int, "icon": "eye"},
        # nuevo:
        {"key": "bosses_defeated",  "label_es": "Bosses derrotados",
         "value": int, "max": 13, "icon": "boss"},
    ],
    "big_bosses": [
        {
            "idx": 0,                              # alineado con MARK_BOSS_SPRITES
            "sprite_id": "boss_moms_heart",        # clave en bestiary_inline.js o URL de MARK_BOSS_SPRITES
            "name_es": "Corazón de Mamá",
            "name_en": "Mom's Heart",
            "kills": int | None,                   # None si es evento (Boss Rush) o transformación (Ultra Greedier)
            "deaths": int | None,
            "hits": int | None,
            "encounters": int | None,
            "seen": bool,                          # True si kills>0, encounters>0, o mark presente
            "mark_completed": bool,                # True si algún personaje tiene la mark
        },
        # … 13 entradas total, en orden de idx
    ],
    "bestiary": [
        {
            "type": int, "variant": int,
            "sprite_id": "...",
            "name_es": "...", "name_en": "...",
            "category": "enemy" | "miniboss" | "boss",
            "chapter": 1 | 2 | 3 | 4 | 5 | 6 | 7 | "extra",
            "kills": int, "deaths": int, "hits": int, "encounters": int,
            "seen": bool,
        },
        # … BESTIARY_CATALOG menos los (type,variant) ocupados por big bosses
    ],
}
```

**Test updates obligatorios** en `tests/test_stats_state.py`:
- `test_bestiary_list_includes_all_catalog` se actualiza para esperar
  `len(BESTIARY_CATALOG) - len(big_bosses_in_catalog)`.
- Nuevo `test_big_bosses_has_13_entries`.
- Nuevo `test_big_bosses_excluded_from_bestiary`.
- Nuevo `test_every_bestiary_entry_has_chapter`.
- Nuevo `test_unique_seen_never_exceeds_catalog` (ver §3.5).

### 3.7 Estilos

Paleta: la misma que `#view-items` (naranjas `#f39c12` / `#f5b041`, fondos
`#16213e` / `#1f2c4a`). Cero emojis en markup. Selectores nuevos:
`.iso-jumprow`, `.iso-top`, `.iso-stat-card`, `.iso-boss-grid`, `.iso-boss`,
`.iso-chapter`, `.iso-chapter-header`, `.iso-enemy-grid`, `.iso-enemy`.

Se eliminan: `#stats-view .stats-cards`, `#stats-view .stats-card`,
`#stats-view .bestiary-toolbar`, `#stats-view .chip`, `#stats-view
.bestiary-grid`, `#stats-view .enemy-cell`, `#stats-view #bestiarySearch`,
`#stats-view #bestiarySort`, `#bestiaryTooltip` (reemplazo equivalente con
naming nuevo).

## 4. Estrategia de implementación

Las tareas siguen este orden (registradas como tasks 1-6 en TaskList):

1. **Catálogo + bug 342/282** — añade `chapter`, identifica big bosses, fija
   el conteo.
2. **Sprites de wiki** — descarga, recorta, regenera inline.
3. **Backend `_build_stats_state`** — separa big bosses, expone chapter, añade
   global `bosses_defeated`.
4. **HTML + CSS** — markup nuevo del `#stats-view`, estilos naranjas.
5. **JS de renderizado** — `renderStatsCards`, nuevo `renderBigBossesPanel`,
   `renderBestiaryByChapter`, `bindBestiaryJumpTo`.
6. **Sync `tracker/assets/challenges.html` + rebuild .exe** — verificación
   manual end-to-end.

Dependencias: 2→1, 3→1, 5→3, 6→{2,4,5}. 4 puede ir en paralelo a 2/3.

## 5. Verificación

Cobertura mínima antes de declarar terminada la tarea 6:

- Tests automáticos:
  - `tests/test_stats_state.py` verifica invariante `bestiary_seen <= bestiary_total`.
  - Test verifica que `big_bosses` tiene 13 elementos y que ninguno aparece en `bestiary`.
  - Test verifica que cada entrada de `bestiary` tiene `chapter` válido.
- Manual sobre `dist/IsaacTracker.exe`:
  - La card "Bestiario" muestra `N / M` con `N <= M`.
  - El panel "Bosses derrotados" muestra los 13 big bosses con sprites reales.
  - El bestiario está agrupado por capítulo con barras de progreso.
  - El buscador navega y destaca el enemigo (igual que en Ítems).
  - El tooltip al hover sigue mostrando kills/deaths/hits/encounters.
  - Ningún sprite aparece como rectángulo cortado (revisar al menos Dangle,
    Mulligan, Pin, Scolex).
  - Ningún emoji unicode visible en la pestaña.

## 6. Decisiones y trade-offs notables

- **Mapeo por capítulo en build-time, no runtime**: simplifica el frontend y
  permite test estático. Trade-off: cualquier cambio futuro requiere
  regenerar el catálogo.
- **Sprites bundleados, no URL directa a wiki**: el .exe debe funcionar sin
  internet. Coste: ~few MB añadidos al bundle.
- **Big bosses fijos a 13**: si en una futura expansión salen más, hay que
  ampliar `MARK_BOSS_SPRITES` y este catálogo a la vez. Aceptable: ya pasa lo
  mismo con las marcas de personaje.
- **Buscador "jump-to" en vez de "filter"**: copiamos el comportamiento de
  Ítems explícitamente porque el usuario lo pidió. Filtrar se sigue haciendo
  con los chips Vistos/Todos y Enemigos/Mini-bosses.
