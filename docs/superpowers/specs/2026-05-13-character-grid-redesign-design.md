# Rediseño de la vista de Personajes — Rejilla de marks

**Fecha:** 2026-05-13
**Archivo afectado:** `challenges.html` (único archivo del proyecto)
**Imagen de referencia:** `C:\Users\jeiko\Desktop\my-what-should-i-unlock-first-list-for-the-normal-and-v0-3qnrbkhykzr91.jpg`

## Contexto

`challenges.html` es un tracker self-contained (un único archivo HTML con CSS y JS inline) para *The Binding of Isaac: Repentance*. Tiene dos pestañas:

- **Desafíos** — lista lineal de 45 desafíos con checkbox y agrupación por tier. Esta vista no se toca.
- **Personajes** — lista vertical agrupada por tier (S/A/B/C/D). Cada personaje tiene checkbox de "desbloqueado", sprite, nombre, chip de tier, botón desplegable con 12 completion marks (Mom's Heart, Isaac, Satan, ???, Lamb, Boss Rush, Hush, Mega Satan, Ultra Greed, Delirium, Mother, Beast), wiki link y tooltip al hover. Vanilla y Tainted están separados con un toggle que muestra/oculta los Tainted debajo.

El usuario quiere rediseñar la vista de Personajes a una rejilla 2D al estilo de la imagen de referencia ("what should I unlock first list"): personajes en columnas, marks en filas, celdas con el ítem que se desbloquea.

## Objetivo

Sustituir la lista vertical por una rejilla densa que permita ver de un vistazo:
- Qué personaje está desbloqueado (cabecera de columna).
- Qué ítems desbloquea cada combinación personaje × mark (celda).
- Qué ítems son prioritarios (resaltado amarillo, fijo).
- Qué marks ha completado el usuario (opacidad reducida en la celda).

Sin perder ninguna funcionalidad existente: progress bar, tooltips, persistencia, reset, toggle Tainted, tabs.

## Decisiones de alcance

| Pregunta | Decisión |
|---|---|
| Contenido de celdas | Icono del ítem + estado de completado |
| Fuente de datos | Wiki `bindingofisaac.es/<slug>/` |
| Personajes incluidos | 17 Normal (default) + 17 Tainted (toggle que **sustituye** la rejilla, oculto por defecto) |
| Significado del amarillo | Prioridad fija (no progreso) |
| Marca de progreso | Click toggle + opacidad reducida del icono |
| Toggle de unlock del pj | Click en sprite de cabecera |
| Layout | Desktop-first, sin esfuerzo en móvil |
| Columna izquierda | Sprites oficiales de jefes (extraídos de la wiki) |
| Orden de columnas | Por tier S → D, con separadores tenues |
| Tooltip sprite pj | Mantiene el actual (tier, unlock, prioridad, wiki link) |
| Tooltip celda | Pequeño: nombre del ítem + pj × mark |
| Prioridad Tainted | Sin prioridad (todos `false`) |
| Implementación de datos | Hardcodeados como objeto JS dentro de `challenges.html` (URLs remotas a sprites del wiki) |

## Diseño

### Layout visual

```
┌─────────┬─[Isaac]─[Cain]─[Apol]─[Magd]─ ... ─[Keeper]─┐
│ NORMAL  │  (S tier)        (A tier)    ...           │
│  CHAR.  │                                            │
├─────────┼────────────────────────────────────────────┤
│ [♥] MH  │ [Lost  ]  [Money ]  [Void  ]   ___   ...   │
│ [☠] IS  │ [Tears ]    ___     [item ]  [item]  ...   │
│ [👹] SA │ [Knife*]  [item*]   [item ]   ___    ...   │   * = priority (yellow)
│  ...    │                                            │   12 filas total
│ [🐲] BE │                                            │
└─────────┴────────────────────────────────────────────┘
                  ↓ [👁 Mostrar Tainted]
```

- Tabla con cabecera de columna (sprites de personajes) y columna izquierda (sprites de jefes + abreviatura).
- Celdas: 44×44 px. Sprite de ítem dentro: 32×32 px.
- Cabecera columna: 52×56 px. Sprite pj: 40×48 px.
- Cabecera fila: 52×44 px. Sprite jefe: 32×32 px + texto "MH"/"IS"/... 0.7rem.
- Separador `border-left: 2px solid #1a1a2e` entre tiers (cuando el tier de la columna actual difiere del anterior).
- Esquina superior-izquierda: rótulo "NORMAL CHARACTERS" / "TAINTED CHARACTERS" según el toggle.

### Modelo de datos

Dos constantes nuevas en el bloque `<script>` de `challenges.html`:

```js
const CHARACTER_UNLOCKS = {
  "isaac": [
    { mark: 0,  name: "Lost Baby",     sprite: "https://bindingofisaac.es/.../Lost-Baby.png", priority: false },
    { mark: 1,  name: "Isaac's Tears", sprite: null,                                          priority: false },
    { mark: 2,  name: "Mom's Knife",   sprite: "https://.../Moms-Knife.png",                  priority: true  },
    // ... mark 3..11
  ],
  "cain":     [ /* 12 entradas */ ],
  // ... 34 slugs (17 normal + 17 tainted)
};

const MARK_BOSS_SPRITES = {
  0: "https://bindingofisaac.es/.../moms-heart.png",   // Mom's Heart / It Lives
  1: "https://bindingofisaac.es/.../isaac.png",        // Isaac
  // ... 0..11
};
```

**Reglas**:
- `sprite: null` significa "no hay imagen disponible" — la celda muestra solo el nombre del ítem como texto a 0.6rem.
- Si un personaje no desbloquea ítem en cierta mark, la entrada existe pero con `name: null, sprite: null`. La celda se renderiza vacía y no es clickeable (sí guarda el estado del mark si se completa por otro medio, pero la UI no expone ese click — para mantenerlo, se permite click incluso en celdas vacías).
- Los `priority: true` solo se marcan en los 17 personajes Normal, según la imagen de referencia. Todos los Tainted llevan `priority: false`.

**Persistencia**: las claves de `localStorage` son las mismas que ahora (`${slug}_unlocked`, `${slug}_mark_${id}`). El progreso existente del usuario se preserva.

### Interacción

| Evento | Acción |
|---|---|
| Click en celda | Toggle `${slug}_mark_${id}` en localStorage. Actualiza opacidad de la celda y progress bar. |
| Click en sprite pj | Toggle `${slug}_unlocked`. Actualiza opacidad de la columna y progress bar. |
| Hover en sprite pj | Tooltip con nombre, tier chip, condición de unlock, descripción de prioridad y wiki link (reutiliza `showCharTooltip`). |
| Hover en icono jefe (columna izq.) | Tooltip simple con nombre completo del mark (de `COMPLETION_MARKS[i].name`). |
| Hover en celda | Tooltip pequeño: "`<item>` — `<character>` × `<mark>`". |
| Toggle "Mostrar Tainted" | Sustituye `CHARACTERS.filter(c => !c.tainted)` por `CHARACTERS.filter(c => c.tainted)` y re-renderiza la rejilla. Persiste en `TAINTED_VISIBLE_KEY`. |
| Reset | `resetAll('characters')` sin cambios. |

### Estilo visual

| Elemento | Estilo |
|---|---|
| Fondo grid | `#1f2a44` |
| Celda fondo | `#3a4a6e`, borde `1px solid #2a3854` |
| Celda hover | outline `2px solid #e94560` |
| Celda priority | `border: 3px solid #f5b73a` inset + leve box-shadow amarillo |
| Celda completada | sprite con `opacity: 0.3; filter: grayscale(0.4)` |
| Celda vacía | fondo plano, sin borde extra, cursor default |
| Sprite pj bloqueado | `opacity: 0.45` + emoji 🔒 (12px) en esquina inferior-derecha |
| Columna bloqueada | overlay `rgba(0,0,0,0.15)` sobre toda la columna |
| Separador tier | `border-left: 2px solid #1a1a2e` |
| Texto esquina | "NORMAL CHARACTERS" / "TAINTED CHARACTERS", 0.7rem, `#aaa` |

Paleta coherente con el resto de la app: fondo `#1a1a2e`, acento `#e94560`, tier-S `#ffd700`, etc.

### Estructura DOM

```html
<div class="view" id="view-characters">
  <div class="progress-bar-container">
    <div class="progress-bar" id="charProgressBar"></div>
  </div>
  <div class="progress-label" id="charProgressLabel"></div>

  <div id="character-grid"></div>   <!-- nuevo, único contenedor -->

  <button class="tainted-toggle" id="taintedToggle">👁 Mostrar Tainted</button>
  <button class="reset-btn" onclick="resetAll('characters')">Resetear personajes</button>
</div>
```

La rejilla en sí se construye en JS como una `<table>` con:
- `<thead>`: una fila con cabecera vacía (rótulo) + N celdas con sprites de personajes.
- `<tbody>`: 12 filas; primera celda = cabecera de mark; siguientes = celdas de ítem.

### Lógica de renderizado

```js
function renderCharacterGrid() {
  const taintedMode = document.getElementById('character-grid').dataset.tainted === '1';
  const chars = CHARACTERS
    .filter(c => c.tainted === taintedMode)
    .sort((a, b) => TIER_ORDER.indexOf(a.tier) - TIER_ORDER.indexOf(b.tier));
  // construir <table>, asignar listeners de click/hover, aplicar clases done/locked/priority
  // ...
  updateCharProgress();
}
```

### Cleanup

Se elimina del HTML actual:
- CSS de `.char-marks-toggle`, `.marks-row`, `.mark`, `.char-sprite` (se sustituye), `.section-title` solo cuando se usa en la lista de personajes (mantener para Desafíos).
- DOM: `<div id="vanilla-list">` y `<div id="tainted-list">`.
- JS: función `renderCharacters()` y su helper `renderGroup()`.

Se preserva:
- Vista de Desafíos completa.
- Sistema de tabs, `switchTab`.
- `CHARACTERS`, `COMPLETION_MARKS`, `TIER_LABEL_CHAR`, `TIER_ORDER`.
- `loadState`/`saveState`, `updateCharProgress`, `resetAll`, `showCharTooltip`, `positionTooltip`, `hideTooltip`.

## Riesgos y consideraciones

- **Variaciones de slug**: los slugs locales (`tainted-magdalena`) pueden no coincidir con las URLs de la wiki (`tainted-magdalene`). Se valida cada slug al extraer datos.
- **URLs remotas**: los sprites de ítems se cargan desde `bindingofisaac.es`. Si la wiki cae o cambia URLs, las imágenes se rompen. Mitigación: si esto pasa, migrar a base64 embebido (Enfoque B). No es bloqueante.
- **Marks sin ítem**: algunos personajes pueden no desbloquear ítem en ciertas marks. Se representan como celdas vacías pero clickeables (para mantener tracking del mark).
- **Densidad visual**: 17×12 = 204 celdas. En desktop estándar (>=1024px ancho) cabe cómodo. En pantallas pequeñas, scroll horizontal.
- **Producción de datos**: extraer 34×12 = 408 entradas + 12 sprites de jefes requiere fetch a 34 páginas de la wiki + identificación visual de prioridades en la imagen. Esta es la tarea más laboriosa de la implementación.

## Aceptación

El diseño está terminado cuando:
- La vista de Personajes muestra una rejilla 17×12 (Normal por defecto) con sprites de personajes en cabecera y sprites de jefes en columna izquierda.
- Cada celda con ítem muestra su sprite; las prioritarias tienen borde amarillo.
- Click en celda alterna el estado de la mark (opacidad reducida si completada).
- Click en sprite de personaje alterna desbloqueado (sprite atenuado + candado si bloqueado).
- Toggle "Mostrar Tainted" sustituye la rejilla por los 17 Tainted (sin prioridad).
- Tooltips funcionan: en sprite pj (info completa + wiki), en jefe (nombre mark), en celda (item — char × mark).
- Progress bar y `resetAll` siguen funcionando.
- La vista de Desafíos no se ve afectada.
- El progreso previo del usuario (localStorage) se preserva.
