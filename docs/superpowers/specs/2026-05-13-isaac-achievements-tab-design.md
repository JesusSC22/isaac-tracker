# Pestaña "Logros" — vista total hacia el 100% (641)

**Fecha:** 2026-05-13
**Archivos afectados:** `challenges.html`, `tracker/assets/challenges.html`, `tracker/save_parser.py` (lectura extendida), `tracker/state_mapper.py` (mapeo de achievements al frontend).

## Contexto

El tracker actual tiene dos pestañas:

- **Desafíos** — lista de 45 retos con tracking automático del save file.
- **Personajes** — rejilla 17×13 (Normal y Tainted) con tracking automático.

El parser (`save_parser.py`) ya lee el "chunk" de achievements del save file (es la fuente de verdad para las marcas de personaje actuales). Cada byte del chunk representa un logro individual: `0` = bloqueado, `1` = desbloqueado.

El usuario quiere una tercera pestaña que muestre los 641 logros totales de Repentance como una lista única, agrupada por categoría, con tracking automático del progreso global hacia el 100%.

## Objetivo

Vista plana de los 641 logros del juego, con:
- Agrupación visual por categoría (Personajes, Items, Bosses, Retos, Transformaciones, etc.).
- Contador global y per-categoría (`247 / 641` arriba; `10 / 17` por categoría).
- Estado individual (✓ desbloqueado / ✕ pendiente) auto-actualizado al guardar la partida.
- Nombre + condición corta de desbloqueo por cada logro.

Las pestañas Desafíos y Personajes **no se tocan** — siguen siendo vistas detalladas con tooltips, estrategia, prioridad. La pestaña Logros es la vista bird's-eye.

## Decisiones de alcance

| Pregunta | Decisión |
|---|---|
| Solapamiento con Retos / Personajes | Intencional. Logros incluye los 45 retos y las 442 marcas de personaje. |
| Auto-track vs manual | Auto-track del save file (consistente con el resto). |
| Datos de los 641 | Hardcodeados como array JS en `challenges.html` (objeto `ACHIEVEMENTS_DATA`). |
| Compilación de datos | Por fases (ver sección "Fases"). |
| Categorización | 8 categorías visibles (Personajes, Marcas, Items, Trinkets, Retos, Bosses, Transformaciones, Otros). |
| Orden dentro de cada categoría | Alfabético por nombre del logro. |
| Filtro / buscador | No en v1. La agrupación por categoría se considera suficiente. |
| Mostrar logros bloqueados sin spoiler | No. Se muestran todos con nombre + condición (igual que las demás pestañas). |
| Tooltip al hover | Opcional; en v1 no se añade (texto siempre visible). |
| Wiki links | Sí (igual que en personajes/retos). |

## Diseño

### Layout visual

```
┌─ Tabs ──────────────────────────────────────────────┐
│ [Desafíos] [Personajes] [Logros]                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│   LOGROS: 247 / 641 (38%)                           │
│   ████████░░░░░░░░░░░░░░░░░░                        │
│                                                     │
│   ▼ PERSONAJES (10/17)                              │
│     ✓ Magdalene       Derrota el Heart 2 veces      │
│     ✓ Cain            Sostén 55¢ a la vez           │
│     ✕ Eve             2 pisos consecutivos sin curar│
│     ...                                             │
│                                                     │
│   ▼ MARCAS DE PERSONAJE (180/442)                   │
│     ✓ Isaac · Mom's Heart                           │
│     ✓ Isaac · Isaac (boss)                          │
│     ✕ Isaac · Satan                                 │
│     ...                                             │
│                                                     │
│   ▼ ITEMS (45/188)                                  │
│     ✓ Mom's Knife     Derrota Satan como Isaac      │
│     ✕ D Infinity      Derrota Delirium              │
│     ...                                             │
│                                                     │
│   [...]                                             │
└─────────────────────────────────────────────────────┘
```

### Estructura de datos

```js
const ACHIEVEMENTS_DATA = [
  { id: 1,   category: "personajes",       name: "Magdalene",
    unlock: "Derrota Mom's Heart 2 veces (con cualquier personaje)." },
  { id: 2,   category: "personajes",       name: "Cain",
    unlock: "Sostén 55 monedas a la vez en una sola partida." },
  // ...
  { id: 247, category: "items",            name: "Mom's Knife",
    unlock: "Derrota Satan como Isaac." },
  // ...
];

const CATEGORIES = [
  { id: "personajes",       label: "Personajes",            order: 1 },
  { id: "marcas",           label: "Marcas de personaje",   order: 2 },
  { id: "items",            label: "Items",                 order: 3 },
  { id: "trinkets",         label: "Trinkets / Cards / Runes", order: 4 },
  { id: "retos",            label: "Retos",                 order: 5 },
  { id: "bosses",           label: "Bosses (primera vez)",  order: 6 },
  { id: "transformaciones", label: "Transformaciones",      order: 7 },
  { id: "otros",            label: "Misceláneo",            order: 8 },
];
```

El campo `id` corresponde al **índice de byte en el chunk de achievements del save file** (1-based, igual que el numerado interno del juego). Eso permite al state_mapper consultar directamente si el logro está desbloqueado: `achievements_chunk[id - 1] != 0`.

### Flujo de datos (auto-track)

1. `save_parser.py` ya extrae el chunk de achievements. Se expone el array crudo (641 bytes) al `state_mapper`.
2. `state_mapper.py` añade un campo nuevo al estado serializado: `achievements_unlocked: list[int]` (lista de IDs desbloqueados).
3. El frontend en `challenges.html` recibe esa lista vía `window.applyIsaacState` y la cruza con `ACHIEVEMENTS_DATA` para renderizar la pestaña.
4. Al cambiar el save file (watchdog ya activo), el frontend re-renderiza la lista con el nuevo estado.

### Persistencia

No hay estado local (toda la verdad viene del save file). Esto es **distinto** de Desafíos/Personajes, que tienen toggle manual además del auto. Para Logros: pura lectura.

### Renderizado

- Sección colapsable por categoría (header con flecha ▼ / ►). Por defecto todas expandidas.
- Cada logro es un `<li>` con sprite (icono pequeño 16×16 cuando sea posible — items y trinkets sí, retos no), nombre, condición.
- Color verde apagado para desbloqueados (`#5fc882` similar al actual), gris para pendientes.
- Click en un logro abre la wiki en navegador externo (si existe URL para él).

## Fases

### Fase 1 (esta sesión)
- Tab "Logros" con la UI completa (header, categorías colapsables, contador global y per-cat).
- `state_mapper` extendido para exponer `achievements_unlocked`.
- Frontend renderizando categorías con la data poblada de **4 categorías "fáciles"** (≈ 87 entradas):
  - Personajes (17)
  - Retos (45) — ya tenemos los nombres en el array `CHALLENGES`.
  - Transformaciones (13)
  - Bosses primera vez (12)
- Las otras 4 categorías (Marcas, Items, Trinkets, Otros) muestran el header con su counter (calculado del total esperado) pero la lista interna sale con un placeholder "Por compilar — fase siguiente".

### Fase 2 (siguiente sesión)
- Items unlocks (~100 entradas, compiladas de la wiki).
- Trinkets / Cards / Runes / Pills (~25 entradas).

### Fase 3
- Marcas de personaje (442) — generación automática cruzando `CHARACTER_UNLOCKS` con el array de bosses ya existente.

### Fase 4
- Misceláneo / story milestones / Greed Mode / etc., hasta sumar 641.
- Validación: la suma de las longitudes por categoría debe dar exactamente 641.

## Implementación de Fase 1

### Cambios en backend (`tracker/`)

1. `save_parser.py`: el `parse_save` ya devuelve `achievements`. Asegurar que se expone como bytes/list y no se descarta tras extraer las marcas de personaje.
2. `state_mapper.py`: añadir `achievements_unlocked` al diccionario de estado: lista de índices 1-based donde el byte es != 0.

### Cambios en frontend (`challenges.html`)

1. Nuevo botón de tab `<button class="tab" data-view="achievements">Logros</button>`.
2. Nueva sección `<section id="view-achievements">` con la estructura indicada.
3. `ACHIEVEMENTS_DATA` poblado con las 87 entradas iniciales.
4. `CATEGORIES_EXPECTED_TOTALS` con los totales por categoría (para mostrar `X/Y` aunque no haya data poblada todavía).
5. Función `renderAchievementsView(state)` que toma `state.achievements_unlocked` y renderiza la lista agrupada.
6. Hook en `window.applyIsaacState` para re-renderizar Logros cuando llegue un update.

### Compilación de datos Fase 1

Las 87 entradas iniciales se obtienen de:
- **Retos (45):** ya tenemos los nombres en el array `CHALLENGES` del HTML. Cruzar con los achievement IDs de la wiki.
- **Personajes (17):** ya tenemos los slugs y los unlock conditions en `CHARACTER_PRIORITY` (texto largo) — extraer la condición corta.
- **Transformaciones (13):** Guppy, Lord of the Flies, Conjoined, Leviathan, Oh Crap, Bob, Spun, Yes Mother?, Seraphim, Fun Guy, Beelzebub, Mom, Stompy. Condición: "Recoge 3 items del grupo X" (a compilar de la wiki).
- **Bosses primera vez (12):** Mom, Mom's Heart/It Lives, Isaac (boss), Satan, ???, Lamb, Boss Rush, Hush, Mega Satan, Ultra Greed, Delirium, Mother (los achievement-bosses; Beast tiene su propio achievement aparte).

## Riesgo / Out-of-scope

- **Mapeo byte → achievement name**: la wiki ordena los achievements por nombre, no por byte index. Hay que cruzar nuestro array con la "Achievement List" oficial donde sí está el index. Si encuentro discrepancias, las marco para revisar.
- **Sprites de logros**: los logros no tienen sprite propio; reusamos el sprite del item/personaje/boss asociado cuando proceda.
- **Performance**: 641 elementos del DOM no es nada para WebView. No se considera.
- **Móvil**: no se considera (igual que el resto del proyecto).
