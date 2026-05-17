# Pestaña "Estadísticas" — Bestiario + stats globales

**Fecha:** 2026-05-17
**Estado:** Aprobado por el usuario, pendiente de plan de implementación.

## Objetivo

Mostrar al jugador **cuántas veces ha matado a cada enemigo** del juego y los **stats globales** que Repentance+ va acumulando a lo largo de su trayectoria (kills, deaths, hits, encounters totales, y — a medida que se identifiquen — Mom kills, runs ganadas, monedas recogidas, etc.). Hoy esos datos sí se guardan en el save file (chunks 11 y 2) pero no aparecen en ninguna parte de la app.

Caso que motivó la feature: el usuario quiere ver, igual que el menú "Bestiary" / "Stats" del propio juego, el desglose de enemigos eliminados con sprite y contador, más un panel-resumen de su trayectoria global.

## Alcance

**Dentro:**

- Nueva pestaña **"Estadísticas"** en la barra principal (al final).
- **Sección superior — tarjetas de stats globales**:
  - 4 cards "garantizadas" desde el día 1, derivadas del bestiario:
    `total_kills`, `total_deaths_by_enemies`, `total_hits_taken`, `unique_enemies_encountered`.
  - 2 cards ya disponibles desde el chunk 2: `donations` y `greed_donations` (mismos datos que la pestaña Donaciones, vistos en agregado).
  - Cards adicionales según se vayan identificando índices del chunk 2 (Mom kills, runs ganadas, monedas recogidas, deaths totales, etc.). Cada una se añade sin tocar el resto.
- **Sección inferior — grid de enemigos con sprites**:
  - Filtros: `Vistos / Todos`, `Todos / Enemigos / Mini-bosses / Bosses`, buscador por nombre, selector de orden.
  - Orden por defecto: kills descendente. Otras opciones: alfabético, por tipo.
  - Cada celda: sprite + nombre + kills. Badge para mini-boss/boss.
  - Tooltip al pasar el ratón: nombre completo, kills, veces que te ha matado, hits que te ha hecho.

**Fuera (futuras iteraciones):**

- Traducción al 100% de los nombres de enemigos al español. Empezamos con los más conocidos en español y el resto en inglés; se va completando en pasadas.
- Sub-pestañas adicionales (ej. agrupar enemigos por planta del juego).
- Edición/reseteo de contadores.

## UX

### Posición en la barra de pestañas

Se añade como octava pestaña al final:

```
[Desafíos] [Personajes] [Logros] [Ítems] [Trinkets] [Cartas] [Donaciones] [Estadísticas]
```

### Estructura de la pestaña

Dos zonas verticales:

1. **Zona superior** — fila(s) de tarjetas de stats globales.
2. **Zona inferior** — grid de enemigos con barra de filtros encima.

### Zona superior: tarjetas de stats globales

Grid responsive de tarjetas. Cada tarjeta:

```
┌────────────────────────────┐
│ [icono pequeño]            │
│  {valor grande}            │
│  {etiqueta corta}          │
└────────────────────────────┘
```

**Cards confirmadas desde el día 1** (todas derivadas del bestiario o ya parseadas):

| Card                       | Valor                                                                                         | Icono                              |
|----------------------------|-----------------------------------------------------------------------------------------------|------------------------------------|
| Enemigos eliminados        | `sum(bestiary_kills.values())`                                                                | calavera                           |
| Veces que te han matado    | `sum(bestiary_deaths.values())`                                                               | lápida                             |
| Golpes recibidos           | `sum(bestiary_hits.values())`                                                                 | corazón roto                       |
| Enemigos distintos vistos  | `len({k for k,v in bestiary_encounters.items() if v>0})` y total `len(BESTIARY_CATALOG)`      | ojo                                |
| Donaciones (tienda)        | `donation_count` (ya existe en `ParsedSave`)                                                  | moneda                             |
| Donaciones (Greed)         | `greed_donation_count` (ya existe en `ParsedSave`)                                            | moneda dorada                      |

**Cards añadidas en fases posteriores** (chunk 2, según se identifiquen). Cada una solo aparece si su índice está confirmado en `tracker/data/stats_counters.py`; si no, simplemente no se renderiza (no se muestra un "0" engañoso). Lista de candidatos a identificar:

- Mom kills
- Runs completadas (totales)
- Win streak actual / mejor
- Monedas recogidas (acumulado)
- Bombas usadas
- Llaves usadas
- Rocas rotas
- Cofres abiertos
- Tiempo jugado total

### Zona inferior: grid de enemigos

**Barra de filtros** (encima del grid):

```
[ Vistos | Todos ]   [ Todos | Enemigos | Mini-bosses | Bosses ]
[ 🔎 Buscar nombre... ]   Orden: [ Kills ↓ | Kills ↑ | Alfabético | Por tipo ]
```

- "Vistos / Todos" por defecto en "Vistos" (los que tienen `kills>0` o `encounters>0`).
- Toggle a "Todos" → enseña también los enemigos no encontrados, en gris/silueta con kills `?`.
- Filtro de categoría afecta solo a qué celdas se muestran, no al orden.
- Buscador filtra por nombre (es + en, case-insensitive).

**Celda de enemigo:**

```
┌───────────────┐
│  [sprite 48]  │
│  Hopper       │  ← nombre (español, fallback inglés)
│  x 71         │  ← kills, número grande
│  [B] o [MB]   │  ← badge solo para boss / mini-boss
└───────────────┘
```

- Si `kills=0` y modo "Todos": sprite en gris al 30%, número `?` en lugar de kills.
- Badge boss/mini-boss: pequeña esquina superior derecha. Color distinto para boss vs mini-boss.

**Tooltip al pasar el ratón** (mismo estilo que pestaña Ítems):

```
Hopper                          (Mini-boss)
Kills:                                  71
Te ha matado:                            2
Hits recibidos:                          5
Encuentros:                             34
```

Solo aparecen las filas con valor > 0 (si no te ha matado nunca, no se muestra "Te ha matado: 0").

### Estados especiales

- **Save fresh (todos los contadores a 0):** cards muestran `0`, grid vacío con mensaje "Aún no has matado a nadie".
- **Modo "Vistos" con 0 vistos:** mensaje "Empieza a jugar para llenar el bestiario".
- **Sprite no disponible:** placeholder gris con `?` (debe ser raro tras la fase B).

## Datos

### Bestiario (chunk 11)

**Layout del chunk** (validado contra Kaitai schema de Zamiell `IsaacSaveFile.ksy`):

```
bestiary_counters_chunk:
  count:    u4               // siempre 4 sub-registros
  records:  4 × bestiary_record

bestiary_record:
  type:     s4               // 1=hits taken, 2=deaths by, 3=kills, 4=encounters
  byte_len: s4               // tamaño en bytes del body (count * 8)
  body:     (byte_len / 8) × entity_value

entity_value (8 bytes):
  entity:   s4               // id empaquetado de entidad (type/variant)
  value:    s4               // contador para ese enemigo
```

**Decodificación del `entity` packed id:** la fórmula exacta NO está documentada públicamente. Hipótesis principal: `entity = entity_type * 1000 + entity_variant` (consistente con cómo Isaac referencia entidades en el código de mods).

**Validación necesaria** (Fase A):
1. Parsear el chunk 11 del save fixture del usuario.
2. Tomar 2-3 entradas con valor alto.
3. Cross-validar el `(type, variant)` decodificado contra el filename de sprites (`Derugon/TBoIR-resources/.../010.010_rottengaper.png` → `type=10, variant=10`).
4. Si la fórmula no encaja, probar variantes (`type*10000+variant`, struct `(type:u2, variant:u2)`, etc.).

**Expuesto en `ParsedSave`:**

```python
bestiary_kills:       dict[tuple[int, int], int]   # (type, variant) -> kills
bestiary_deaths:      dict[tuple[int, int], int]
bestiary_hits:        dict[tuple[int, int], int]
bestiary_encounters:  dict[tuple[int, int], int]
```

### Catálogo de enemigos (sprites + nombres + categorías)

Fuente de sprites: **`Derugon/TBoIR-resources`** (rama de versión de Repentance+, p. ej. `1.9.7.15.J374`), carpetas:

- `resources-dlc3/gfx/monsters/classic/`
- `resources-dlc3/gfx/monsters/rebirth/`
- `resources-dlc3/gfx/monsters/repentance/`

Total ~372 PNGs con filename `TYPE.VARIANT_nombre[_sufijo].png`.

**Pipeline de construcción** (Fase B, herramienta `tools/build_bestiary.py`):

1. Clonar/descargar las tres carpetas de sprites.
2. Para cada PNG:
   - Parsear filename → `(type, variant, name_en, suffix)`.
   - Cropear primer frame del atlas. Estrategia: leer dimensiones, asumir frame de tamaño fijo (típicamente 64×64 o 80×80 — usar heurística por enemigo: ancho del PNG `% 64 == 0` → frame 64; etc.). Si la heurística falla, log de warning y dejar el atlas completo (se arregla manual).
   - Escalar a 48×48 (`Pillow` `Image.resize` con `LANCZOS`).
   - Optimizar (`PIL` PNG optimize, `pngquant` opcional).
3. Generar dos artefactos:
   - **`tracker/assets/bestiary_inline.js`** — base64 de los 372 sprites, mismo formato que `items_inline.js`.
   - **`tracker/data/bestiary.py`** — tabla:
     ```python
     BESTIARY_CATALOG: dict[tuple[int, int], dict] = {
         (10, 10): {"name_en": "Rotten Gaper", "name_es": "Rotten Gaper", "category": "enemy"},
         (19, 0):  {"name_en": "Mom",          "name_es": "Mom",         "category": "boss"},
         # ...
     }
     ```
   - `category`: `"enemy"` | `"miniboss"` | `"boss"`. Determinado por:
     - Lista hard-coded de bosses (Mom, Mom's Heart, Isaac, ???, Satan, The Lamb, Hush, Delirium, Mother, The Beast, Ultra Greed, etc. — type IDs conocidos).
     - Lista hard-coded de mini-bosses (Gemini, Steven, Larry Jr., etc.).
     - El resto: `"enemy"`.

**Traducción de nombres:**
- `name_es` arranca igual que `name_en` salvo para una lista corta de los más conocidos (`Mom`, `Mom's Heart`, `The Lamb`, `???` → "Blue Baby", etc.). Se irá completando en commits posteriores.

### Stats globales (chunk 2)

Igual que en el spec de Donaciones, el chunk 2 tiene 523 enteros s32 LE. Hoy solo están identificados los índices 8 y 19.

**Nuevo módulo `tracker/data/stats_counters.py`:**

```python
# Solo entradas confirmadas. Las no confirmadas NO se incluyen hasta validar
# mediante diff de saves (jugar → guardar → comparar).
GLOBAL_STAT_COUNTERS: list[dict] = [
    {"index": 8,  "key": "donations_normal",  "label_es": "Donaciones (tienda)", "icon": "coin"},
    {"index": 19, "key": "donations_greed",   "label_es": "Donaciones (Greed)",  "icon": "coin_gold"},
    # Pendientes de identificar:
    # - Mom kills
    # - Runs completadas
    # - Monedas recogidas (acumulado)
    # - ...
]
```

**Protocolo de identificación de nuevos índices (Fase D):**

1. El usuario juega una run con un comportamiento conocido (p. ej. mata a Mom una vez más).
2. Se copia el save antes y después.
3. Script `tools/diff_counters.py` muestra qué índices del chunk 2 cambiaron y por cuánto.
4. Se etiqueta el índice en `GLOBAL_STAT_COUNTERS` y se añade su card.

Cada identificación es un commit pequeño e independiente. No bloquea el resto de la pestaña.

### Estado expuesto al frontend

En `state_mapper.py`, nuevo bloque `stats_state`:

```python
{
    "globals": [
        {"key": "total_kills",      "label_es": "Enemigos eliminados",    "value": int, "icon": "skull"},
        {"key": "total_deaths",     "label_es": "Veces que te han matado","value": int, "icon": "tombstone"},
        {"key": "total_hits",       "label_es": "Golpes recibidos",        "value": int, "icon": "heart_broken"},
        {"key": "unique_encountered", "label_es": "Enemigos distintos vistos", "value": int, "max": int, "icon": "eye"},
        {"key": "donations_normal", "label_es": "Donaciones (tienda)",    "value": int, "icon": "coin"},
        {"key": "donations_greed",  "label_es": "Donaciones (Greed)",     "value": int, "icon": "coin_gold"},
        # + cualquier card identificada en GLOBAL_STAT_COUNTERS
    ],
    "bestiary": [
        {
            "type": 10, "variant": 10,
            "name_es": "Rotten Gaper", "name_en": "Rotten Gaper",
            "category": "enemy",  # "enemy" | "miniboss" | "boss"
            "kills": 71, "deaths": 0, "hits": 5, "encounters": 34,
            "sprite_id": "010.010",  # clave en bestiary_inline.js
            "seen": True              # encounters>0 OR kills>0
        },
        # ... una entrada por enemigo del catálogo
    ]
}
```

Importante: la lista `bestiary` incluye **todos los enemigos del catálogo**, incluso los no vistos (con `kills=deaths=hits=encounters=0` y `seen=False`). El filtro "Vistos / Todos" se aplica en frontend.

## Arquitectura / componentes nuevos

- **`tracker/save_parser.py`** — añadir decoder del chunk 11 y campos nuevos en `ParsedSave`.
- **`tracker/data/bestiary.py`** — catálogo `BESTIARY_CATALOG` generado.
- **`tracker/data/stats_counters.py`** — registro de índices del chunk 2 confirmados.
- **`tracker/state_mapper.py`** — `_build_stats_state` que une bestiario + globales.
- **`tracker/assets/bestiary_inline.js`** — sprites inline (generado).
- **`tools/build_bestiary.py`** — descarga sprites + cropea + genera artefactos.
- **`tools/diff_counters.py`** — utilidad para identificar nuevos índices del chunk 2.
- **`challenges.html`** — pestaña `data-view="stats"` con HTML + CSS + JS para cards y grid.
- **Sincronización del mirror del .exe** (ya automatizado por scripts existentes).

## Tests

- **Parser:**
  - Dado el save fixture del usuario, `parse_save` devuelve `bestiary_kills`, `bestiary_deaths`, `bestiary_hits`, `bestiary_encounters` no vacíos.
  - Total `sum(bestiary_kills.values())` > 0 (sanity).
  - El packed id de al menos 3 enemigos conocidos del fixture decodifica a un `(type, variant)` presente en `BESTIARY_CATALOG`.
- **State mapper:**
  - Dado un `ParsedSave` con bestiario poblado, `stats_state["globals"]` contiene las 6 cards garantizadas con valores correctos.
  - `stats_state["bestiary"]` tiene una entrada por cada `(type, variant)` del catálogo.
  - Para un enemigo no presente en los dicts del parser → `seen=False`, todos los contadores a 0.
- **Catálogo:**
  - `BESTIARY_CATALOG` tiene al menos 200 entradas (sanity).
  - Todos los bosses conocidos (Mom, ???, Satan, Lamb, Hush, Delirium, Mother, Beast, Ultra Greed) están presentes con `category="boss"`.
  - Ningún `(type, variant)` duplicado.
- **No se testea la UI** (consistente con el resto del proyecto).

## Riesgos

- **Decodificación del packed entity id:** la fórmula `type*1000+variant` es una hipótesis. Si no encaja, la Fase A se alarga 1-2 días para probar variantes y validar contra el save real. Mitigación: arrancar con dump bruto del chunk 11 y elegir la fórmula que más entries decodifique a `(type, variant)` válidos del catálogo.
- **Crop del primer frame:** sprites con animaciones de tamaño no estándar pueden quedar parcialmente cortados. Mitigación: heurística + log de warnings + arreglo manual de los visualmente feos (estimación: <30 sobre 372).
- **Stats globales incompletos:** la lista de cards "extra" del chunk 2 dependerá de cuántos índices se logren identificar. Mitigación: hacerlo visible al usuario que esta zona crece con el tiempo; no mostrar `0` para índices no confirmados.
- **Tamaño del .exe:** 372 sprites @ 48×48 optimizados ≈ 800 KB-1 MB extra. Aceptable, consistente con cómo embebemos iconos de ítems.
- **Cambios en filenames de sprites:** Derugon a veces renombra archivos entre versiones del juego. El catálogo queda fijo una vez generado; futuras versiones del juego no requieren regenerar salvo enemigos nuevos.

## Después de esta iteración

La pestaña queda diseñada para crecer en estas direcciones, sin que ninguna de estas requiera tocar las otras:

- **Identificar más índices del chunk 2** → cada nuevo índice añade una card sin cambiar el resto.
- **Traducir al español los nombres restantes** del bestiario → solo toca `bestiary.py`.
- **Sub-vistas del bestiario** (agrupar por planta del juego, p. ej. Basement vs Womb) → filtro adicional.
- **Visualización de progreso** (% del bestiario completado, badges por hitos) → tarjeta nueva.

Ninguna de estas se implementa ahora.
