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

Los 13 big bosses son exactamente los que ya están en `MARK_BOSS_SPRITES` en
`challenges.html` (las mismas casillas que aparecen en las marcas de
completitud de cada personaje):

| Idx | Nombre |
|-----|--------|
| 0 | Mom's Heart / It Lives |
| 1 | Isaac |
| 2 | Satan |
| 3 | ??? (Blue Baby) |
| 4 | The Lamb |
| 5 | Boss Rush |
| 6 | Hush |
| 7 | Mega Satan |
| 8 | Ultra Greed |
| 9 | Ultra Greedier |
| 10 | Delirium |
| 11 | Mother |
| 12 | The Beast |

Estos NO aparecen en el bestiario por capítulo de abajo — solo en el panel
"Bosses derrotados" arriba.

### 3.3 Mapeo capítulo del juego

`tools/build_bestiary.py` se amplía con una tabla `FLOOR_TO_CHAPTER` que
mapea cada tipo de enemigo a su capítulo. La asignación se hace por el piso
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

La asignación detallada por (type, variant) se hará durante la
implementación cruzando el catálogo actual contra la wiki. Donde haya
ambigüedad (un enemigo aparece en múltiples capítulos), se usa el primero.

### 3.4 Fuente de sprites

Wiki oficial (`bindingofisaacrebirth.wiki.gg`), idéntico patrón al que ya
usamos para sprites de boss-marks en personajes. Pipeline:

1. `tools/download_bestiary_sprites.py` construye URLs por nombre, descarga
   PNGs a `tracker/assets/bestiary_icons/<type>_<variant>.png`.
2. Si la wiki devuelve hoja de animación, recortar al primer frame
   (`width = height` típico de Isaac).
3. `tracker/data/_build_inline.py` regenera `tracker/assets/bestiary_inline.js`
   con cada PNG como base64 (igual que items/trinkets).
4. El bundler Nuitka ya incluye `bestiary_inline.js` — verificado en commit
   `7a72855`.

Esto sustituye la fuente actual que produce sprites cortados.

### 3.5 Corrección del bug 342/282

Causa probable: el conteo de "vistos" itera sobre `bestiary_kills` (mapa por
(type, variant)) sumando 1 por cada entrada vista, mientras que el total
`282` está hardcodeado o cuenta por `type` solamente.

Solución: en `_build_stats_state`, los dos números se calculan ambos sobre
**la misma colección** — el catálogo `BESTIARY_CATALOG`. El numerador es
`sum(1 for e in catalog if e.seen)`, el denominador es `len(catalog)`. Test
en `tests/test_stats_state.py` verifica la invariante `seen <= total`.

### 3.6 Contrato `stats_state` actualizado

```python
stats_state = {
    "globals": [
        {"icon": "skull",      "label_es": "Enemigos eliminados", "value": int, "max": None},
        {"icon": "tombstone",  "label_es": "Te han matado",       "value": int, "max": None},
        {"icon": "heart_broken","label_es": "Golpes recibidos",   "value": int, "max": None},
        {"icon": "eye",        "label_es": "Bestiario",           "value": int, "max": int},
        # nuevo:
        {"icon": "boss",       "label_es": "Bosses derrotados",   "value": int, "max": 13},
    ],
    "big_bosses": [
        {
            "sprite_id": "boss_moms_heart",
            "name_es": "Corazón de Mamá",
            "name_en": "Mom's Heart",
            "kills": int, "deaths": int, "hits": int, "encounters": int,
            "seen": bool,
        },
        # … 13 entradas total
    ],
    "bestiary": [
        {
            "sprite_id": "...",
            "name_es": "...", "name_en": "...",
            "category": "enemy" | "miniboss" | "boss",  # ya no "big_boss"
            "chapter": 1 | 2 | 3 | 4 | 5 | 6 | 7 | "extra",
            "kills": int, "deaths": int, "hits": int, "encounters": int,
            "seen": bool,
        },
        # …
    ],
}
```

El campo `icon` de globals ya **no** mapea a emojis — se ignora en frontend
o se usa para clases CSS. La constante `STATS_ICONS` se elimina.

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
