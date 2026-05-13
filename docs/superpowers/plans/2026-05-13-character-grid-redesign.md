# Character Grid Redesign — Implementation Plan

> **For agentic workers:** Steps use checkbox (`- [ ]`) syntax for tracking. Project has no test infrastructure (single static HTML file). Verification is manual via browser. TDD is replaced by **VBC**: write the smallest change, open in browser, check expected behavior, commit. No test framework will be introduced — that would be unwarranted scope creep for this project.

**Goal:** Reemplazar la vista de Personajes (lista vertical agrupada por tier) por una rejilla 2D (personajes en columnas × marks en filas) con iconos de ítems desbloqueables, resaltado de prioridad fijo y toggle Normal/Tainted que sustituye la rejilla en vez de apilar.

**Architecture:** Mantener el patrón single-file del proyecto. Añadir dos constantes JS (`CHARACTER_UNLOCKS`, `MARK_BOSS_SPRITES`) con datos extraídos de `bindingofisaac.es`. Sustituir `renderCharacters()` por `renderCharacterGrid()`. Preservar todas las claves de localStorage existentes.

**Tech Stack:** HTML5, CSS3, vanilla JS, localStorage. Sin frameworks, sin build, sin tests automatizados.

**Spec de referencia:** `docs/superpowers/specs/2026-05-13-character-grid-redesign-design.md`

---

## Estructura de archivos

Solo se modifica un archivo:

- **Modify:** `challenges.html` — único archivo del proyecto.

Subzonas dentro de `challenges.html` que se tocan:
- CSS bloque `<style>` (líneas ~7-361): añadir reglas del grid, eliminar reglas de la lista actual.
- DOM `#view-characters` (líneas ~384-397): reemplazar contenedores `vanilla-list`/`tainted-list` por `#character-grid`.
- JS bloque `<script>` (líneas ~402-1454):
  - Después de `CHARACTERS` array (línea ~710): añadir `CHARACTER_UNLOCKS` y `MARK_BOSS_SPRITES`.
  - Reemplazar `renderCharacters()` y `renderGroup()` (líneas ~1295-1419) por `renderCharacterGrid()`.
  - Actualizar `setTaintedVisible()` (líneas ~1439-1444) para que invoque `renderCharacterGrid()` en vez de toggle de visibilidad.
  - `updateCharProgress()` (líneas ~1111-1130) se mantiene; solo cambia el cálculo de "visible" para reflejar el nuevo modo.

---

## Task 0: Preparación y backup

**Files:**
- Read: `challenges.html`
- Create: `challenges.html.backup` (copia de seguridad antes de cambios)

- [ ] **Step 1: Crear backup del archivo actual**

```bash
cp "challenges.html" "challenges.html.backup"
```

- [ ] **Step 2: Identificar y anotar las líneas exactas a modificar/eliminar**

Localizar y verificar offsets actuales (pueden haber cambiado):
- DOM `view-characters`: buscar `id="view-characters"`.
- `CHARACTERS` array: buscar `const CHARACTERS = [`.
- `COMPLETION_MARKS`: buscar `const COMPLETION_MARKS = [`.
- `renderCharacters`: buscar `function renderCharacters()`.
- `setTaintedVisible`: buscar `function setTaintedVisible`.

Documentar el rango exacto de cada uno antes de tocar nada.

- [ ] **Step 3: Verificar que la app actual abre bien en el navegador**

Abrir `challenges.html` en navegador. Comprobar:
- Pestaña Desafíos: lista visible, checkboxes funcionan.
- Pestaña Personajes: lista vertical, toggle Tainted funciona.
- Progress bars actualizan al hacer click.

Snapshot mental del comportamiento actual para comparar después.

---

## Task 1: Recolectar sprites de los 12 jefes (marks)

**Files:**
- No modifica archivos; produce datos para Task 5.

- [ ] **Step 1: Identificar URLs de los 12 sprites de jefes**

Para cada mark, fetch a la wiki o usar nombres conocidos:
- 0 — Mom's Heart / It Lives
- 1 — Isaac
- 2 — Satan
- 3 — ??? (Blue Baby)
- 4 — The Lamb
- 5 — Boss Rush
- 6 — Hush
- 7 — Mega Satan
- 8 — Ultra Greed (Greedier)
- 9 — Delirium
- 10 — Mother
- 11 — The Beast

Buscar en `bindingofisaac.es` la página de cada jefe (ej. `https://bindingofisaac.es/moms-heart/`). Si no hay página directa, usar la página de Isaac (`/isaac/`) que listamos antes — pero esa página muestra los **ítems desbloqueados**, no necesariamente los iconos de los jefes mismos.

Plan B si no hay sprites de jefes en la wiki: usar emojis/símbolos Unicode como fallback inicial (♥, 👶, 👹, ???, 🐑, ⏱, 💜, 😈, 💰, 🌀, 🤰, 🐍) y luego sustituir.

- [ ] **Step 2: Validar cada URL con un fetch ligero**

Para cada URL identificada, verificar HTTP 200 + content-type image/*. Si alguna falla, marcarla y resolver (Plan B emoji o buscar URL alternativa).

- [ ] **Step 3: Producir el objeto MARK_BOSS_SPRITES**

```js
const MARK_BOSS_SPRITES = {
  0: "https://bindingofisaac.es/.../moms-heart.png",
  1: "https://bindingofisaac.es/.../isaac.png",
  // ... 0..11
};
```

Guardar en un archivo temporal `_data-marks.txt` (no commiteado) o pegarlo directamente en el editor para Task 5.

---

## Task 2: Recolectar unlocks de los 17 personajes Normal

**Files:**
- No modifica archivos; produce datos para Task 5.

- [ ] **Step 1: Fetch en paralelo de las 17 páginas de personajes Normal**

Slugs Normal (en orden por tier S→D según `CHARACTERS`):
- **S:** isaac, cain, apollyon
- **A:** magdalene, lazarus, bethany, eden
- **B:** judas, blue-baby, eve
- **C:** samson, azazel, the-forgotten, lilith, jacob-and-esau
- **D:** the-lost, keeper

URL base: `https://bindingofisaac.es/<slug>/`. **Excepción**: `blue-baby` puede no existir como slug; probar `???` o `??? (Blue Baby)` y buscar la URL canónica.

Disparar fetches en paralelo (lotes de 4-5) extrayendo para cada uno los 12 marks y el ítem desbloqueado.

- [ ] **Step 2: Para cada personaje, normalizar a 12 entradas**

Por personaje, producir array de 12 elementos (mark 0..11):
```js
{ mark: N, name: "Item Name", sprite: "https://.../item.png", priority: false }
```

Si una mark no tiene ítem: `{ mark: N, name: null, sprite: null, priority: false }`.

Si la wiki devuelve nombre pero no imagen (caso "Isaac's Tears" para Isaac): `{ mark: N, name: "Isaac's Tears", sprite: null, priority: false }`.

- [ ] **Step 3: Validar consistencia**

Para cada slug, verificar que el array tiene exactamente 12 entradas. Comprobar que los slugs locales coinciden con los de la wiki — si hay variantes, anotarlas (ej. `the-forgotten` vs `forgotten`).

- [ ] **Step 4: Guardar datos en archivo temporal**

`_data-normal.txt` con el dict de los 17 personajes. No commiteado.

---

## Task 3: Recolectar unlocks de los 17 personajes Tainted

**Files:**
- No modifica archivos; produce datos para Task 5.

- [ ] **Step 1: Fetch en paralelo de las 17 páginas Tainted**

Slugs (de `CHARACTERS`):
- tainted-isaac, tainted-cain, tainted-apollyon, tainted-magdalena, tainted-lazarus, tainted-bethany, tainted-eden, tainted-judas, tainted-blue-baby, tainted-eve, tainted-samson, tainted-azazel, tainted-forgotten, tainted-lilith, tainted-jacob-and-esau, tainted-the-lost, tainted-keeper.

URL base: `https://bindingofisaac.es/<slug>/`. Cuidado con `tainted-magdalena` (puede ser `tainted-magdalene` en la wiki).

- [ ] **Step 2: Normalizar a 12 entradas por personaje**

Igual que Task 2 Step 2. Todos los Tainted tienen `priority: false` por decisión del usuario.

- [ ] **Step 3: Validar slugs y consistencia**

Cruzar slugs locales con los de la wiki. Para cada discrepancia, usar el slug LOCAL como clave en `CHARACTER_UNLOCKS` (debe coincidir con `CHARACTERS[i].slug`).

- [ ] **Step 4: Guardar datos en archivo temporal**

`_data-tainted.txt` con el dict de los 17 Tainted. No commiteado.

---

## Task 4: Identificar ítems prioritarios desde la imagen de referencia

**Files:**
- No modifica archivos; produce datos para Task 5.

- [ ] **Step 1: Releer la imagen de referencia**

Imagen: `C:\Users\jeiko\Desktop\my-what-should-i-unlock-first-list-for-the-normal-and-v0-3qnrbkhykzr91.jpg`.

Identificar todas las celdas con resaltado amarillo. Tomar nota de la posición (personaje × mark) y, si es identificable, el nombre del ítem.

- [ ] **Step 2: Cruzar con los datos de Task 2**

Para cada celda amarilla identificada en la imagen, marcar `priority: true` en el entry correspondiente de `_data-normal.txt`. Si el ítem identificado en la imagen no coincide con el nombre devuelto por la wiki, anotar la discrepancia (puede ser un cambio reciente del juego o un dato erróneo de la wiki).

- [ ] **Step 3: Listar todas las marcas de prioridad para revisión rápida**

Producir una lista en texto plano:
```
isaac × Satan → Mom's Knife (priority)
cain × Hush   → Anti-Gravity (priority)
...
```

Esta lista ayuda a debugear visualmente cuando se rendrice el grid.

---

## Task 5: Inyectar CHARACTER_UNLOCKS y MARK_BOSS_SPRITES en challenges.html

**Files:**
- Modify: `challenges.html` (después de `COMPLETION_MARKS`, antes de `TIER_LABEL_CHAR`)

- [ ] **Step 1: Localizar el punto de inserción**

Después del bloque `const COMPLETION_MARKS = [ ... ];` y antes de `const TIER_LABEL_CHAR = ...`. Aproximadamente línea 726.

- [ ] **Step 2: Insertar MARK_BOSS_SPRITES**

```js
  const MARK_BOSS_SPRITES = {
    0: "url-mom-heart",
    1: "url-isaac",
    2: "url-satan",
    3: "url-blue-baby",
    4: "url-lamb",
    5: "url-boss-rush",
    6: "url-hush",
    7: "url-mega-satan",
    8: "url-ultra-greed",
    9: "url-delirium",
    10: "url-mother",
    11: "url-beast",
  };
```

Sustituir cada `url-xxx` por las URLs reales producidas en Task 1.

- [ ] **Step 3: Insertar CHARACTER_UNLOCKS**

```js
  const CHARACTER_UNLOCKS = {
    "isaac": [
      { mark: 0, name: "Lost Baby", sprite: "...", priority: false },
      // ... 12 entradas
    ],
    // ... 34 slugs
  };
```

Pegar los datos producidos en Tasks 2 + 3 + 4 (con prioridades aplicadas).

- [ ] **Step 4: Validar sintaxis con el navegador**

Abrir `challenges.html` en navegador. Abrir consola. Debe cargar sin errores. La vista de Personajes seguirá mostrando la lista antigua (aún no la hemos cambiado) — eso es esperado.

Si hay error de sintaxis, fix antes de commit.

- [ ] **Step 5: Commit**

```bash
cp "challenges.html" "challenges.html.tmp" && mv "challenges.html.tmp" "challenges.html"
# Sin git commit: el repo no es git (notar en CHANGELOG mental)
```

(No hay git en este proyecto. "Commit" en este plan significa: punto estable de progreso, guardar.)

---

## Task 6: Añadir CSS para la rejilla

**Files:**
- Modify: `challenges.html` dentro del bloque `<style>`, justo después de las reglas existentes de `#tainted-list` (~línea 360).

- [ ] **Step 1: Añadir estilos del grid**

```css
    /* Character grid */
    #character-grid {
      overflow-x: auto;
      margin-bottom: 16px;
    }

    .char-grid {
      border-collapse: collapse;
      background: #1f2a44;
      margin: 0 auto;
    }

    .char-grid th, .char-grid td {
      border: 1px solid #0f1325;
      padding: 0;
      box-sizing: border-box;
    }

    .char-grid-corner {
      width: 64px;
      font-size: 0.65rem;
      color: #aaa;
      text-align: center;
      letter-spacing: 0.5px;
      padding: 4px;
      line-height: 1.2;
      background: #16213e;
    }

    .char-grid-col-header {
      width: 52px;
      height: 60px;
      background: #2a3854;
      text-align: center;
      vertical-align: middle;
      cursor: pointer;
      position: relative;
    }
    .char-grid-col-header img {
      width: 40px;
      height: 48px;
      object-fit: contain;
      image-rendering: pixelated;
    }
    .char-grid-col-header.locked img {
      opacity: 0.45;
    }
    .char-grid-col-header.locked::after {
      content: "🔒";
      position: absolute;
      right: 2px;
      bottom: 2px;
      font-size: 12px;
      pointer-events: none;
    }
    .char-grid-col-header.tier-sep {
      border-left: 2px solid #1a1a2e;
    }

    .char-grid-row-header {
      width: 64px;
      height: 44px;
      background: #16213e;
      vertical-align: middle;
      text-align: left;
      padding-left: 4px;
      white-space: nowrap;
    }
    .char-grid-row-header img {
      width: 28px;
      height: 28px;
      object-fit: contain;
      vertical-align: middle;
      margin-right: 4px;
    }
    .char-grid-row-header .mark-abbr {
      font-size: 0.7rem;
      color: #ccc;
      vertical-align: middle;
    }

    .char-grid-cell {
      width: 44px;
      height: 44px;
      background: #3a4a6e;
      text-align: center;
      vertical-align: middle;
      cursor: pointer;
      position: relative;
    }
    .char-grid-cell.tier-sep {
      border-left: 2px solid #1a1a2e;
    }
    .char-grid-cell img {
      width: 32px;
      height: 32px;
      object-fit: contain;
      image-rendering: pixelated;
      transition: opacity 0.15s;
    }
    .char-grid-cell.priority {
      box-shadow: inset 0 0 0 3px #f5b73a, 0 0 6px rgba(245,183,58,0.4);
    }
    .char-grid-cell.done img {
      opacity: 0.3;
      filter: grayscale(0.4);
    }
    .char-grid-cell.empty {
      cursor: default;
    }
    .char-grid-cell:hover:not(.empty) {
      outline: 2px solid #e94560;
      outline-offset: -2px;
    }

    .char-grid-col-cells.locked {
      /* aplicado vía JS: añade overlay a las celdas de la columna */
    }
    .char-grid-cell.col-locked::before {
      content: "";
      position: absolute;
      inset: 0;
      background: rgba(0,0,0,0.18);
      pointer-events: none;
    }
```

- [ ] **Step 2: Verificar en navegador**

Recargar. No debe romper nada visualmente; las nuevas reglas no se aplican aún porque no existe el DOM correspondiente.

---

## Task 7: Reemplazar DOM de #view-characters

**Files:**
- Modify: `challenges.html` líneas ~384-397.

- [ ] **Step 1: Reemplazar el bloque actual**

Buscar:
```html
  <div class="view" id="view-characters">
    <div class="progress-bar-container">
      <div class="progress-bar" id="charProgressBar"></div>
    </div>
    <div class="progress-label" id="charProgressLabel"></div>

    <div id="vanilla-list"></div>

    <button class="tainted-toggle" id="taintedToggle">👁 Mostrar Tainted</button>

    <div id="tainted-list"></div>

    <button class="reset-btn" onclick="resetAll('characters')">Resetear personajes</button>
  </div>
```

Sustituir por:
```html
  <div class="view" id="view-characters">
    <div class="progress-bar-container">
      <div class="progress-bar" id="charProgressBar"></div>
    </div>
    <div class="progress-label" id="charProgressLabel"></div>

    <div id="character-grid" data-tainted="0"></div>

    <button class="tainted-toggle" id="taintedToggle">👁 Mostrar Tainted</button>

    <button class="reset-btn" onclick="resetAll('characters')">Resetear personajes</button>
  </div>
```

- [ ] **Step 2: Verificar en navegador**

Recargar. La vista de Personajes debe estar VACÍA ahora (sin rejilla aún). Esto es esperado: aún no hemos implementado el renderizado.

La pestaña Desafíos sigue funcionando intacta.

---

## Task 8: Implementar renderCharacterGrid()

**Files:**
- Modify: `challenges.html` — sustituir `renderCharacters()` (~líneas 1295-1419).

- [ ] **Step 1: Eliminar renderCharacters() y renderGroup()**

Borrar el bloque entero de `function renderCharacters() { ... }` y su helper interno `renderGroup`.

- [ ] **Step 2: Implementar renderCharacterGrid()**

```js
  function renderCharacterGrid() {
    const container = document.getElementById('character-grid');
    const taintedMode = container.dataset.tainted === '1';
    const state = loadState(CHAR_STORAGE_KEY);

    const chars = CHARACTERS
      .filter(c => c.tainted === taintedMode)
      .sort((a, b) => TIER_ORDER.indexOf(a.tier) - TIER_ORDER.indexOf(b.tier));

    const table = document.createElement('table');
    table.className = 'char-grid';

    // Cabecera: esquina + sprites de personajes
    const thead = document.createElement('thead');
    const headRow = document.createElement('tr');
    const corner = document.createElement('th');
    corner.className = 'char-grid-corner';
    corner.textContent = taintedMode ? 'TAINTED CHARACTERS' : 'NORMAL CHARACTERS';
    headRow.appendChild(corner);

    let prevTier = null;
    chars.forEach(c => {
      const th = document.createElement('th');
      th.className = 'char-grid-col-header';
      if (prevTier !== null && c.tier !== prevTier) th.classList.add('tier-sep');
      prevTier = c.tier;

      const img = document.createElement('img');
      img.src = c.sprite;
      img.alt = c.name;
      th.appendChild(img);

      const isUnlocked = !!state[`${c.slug}_unlocked`];
      if (!isUnlocked) th.classList.add('locked');

      th.dataset.slug = c.slug;
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    // Filas: una por mark
    const tbody = document.createElement('tbody');
    COMPLETION_MARKS.forEach(m => {
      const tr = document.createElement('tr');
      const rh = document.createElement('td');
      rh.className = 'char-grid-row-header';
      rh.title = m.name;

      if (MARK_BOSS_SPRITES[m.id]) {
        const bossImg = document.createElement('img');
        bossImg.src = MARK_BOSS_SPRITES[m.id];
        bossImg.alt = m.name;
        rh.appendChild(bossImg);
      }
      const abbr = document.createElement('span');
      abbr.className = 'mark-abbr';
      abbr.textContent = m.short;
      rh.appendChild(abbr);
      tr.appendChild(rh);

      let prevTier2 = null;
      chars.forEach(c => {
        const td = document.createElement('td');
        td.className = 'char-grid-cell';
        if (prevTier2 !== null && c.tier !== prevTier2) td.classList.add('tier-sep');
        prevTier2 = c.tier;

        const unlocks = (CHARACTER_UNLOCKS[c.slug] || [])[m.id] || null;
        const stateKey = `${c.slug}_mark_${m.id}`;
        const isDone = !!state[stateKey];

        if (unlocks && unlocks.priority) td.classList.add('priority');
        if (isDone) td.classList.add('done');

        if (unlocks && unlocks.sprite) {
          const img = document.createElement('img');
          img.src = unlocks.sprite;
          img.alt = unlocks.name || '';
          td.appendChild(img);
        } else if (unlocks && unlocks.name) {
          td.textContent = unlocks.name;
          td.style.fontSize = '0.55rem';
          td.style.color = '#ccc';
        } else {
          td.classList.add('empty');
        }

        // Columna locked overlay
        if (!state[`${c.slug}_unlocked`]) td.classList.add('col-locked');

        td.dataset.slug = c.slug;
        td.dataset.mark = m.id;
        td.dataset.itemName = unlocks ? (unlocks.name || '') : '';
        td.dataset.charName = c.name;
        td.dataset.markName = m.name;

        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    container.innerHTML = '';
    container.appendChild(table);

    attachGridListeners();
    updateCharProgress();
  }
```

- [ ] **Step 3: Verificar en navegador**

Recargar. La rejilla debe aparecer con la cabecera de personajes y las 12 filas de marks. Los listeners aún no funcionan (Step 8.4), pero la pintura debe ser correcta:
- Sprites de personajes visibles en cabecera.
- 12 filas con jefe + abreviatura a la izquierda.
- Celdas pintadas, prioritarias con borde amarillo.

Si algún personaje aparece con celdas vacías en TODOS los marks: probable mismatch de slug entre `CHARACTERS` y `CHARACTER_UNLOCKS`. Debug en consola.

- [ ] **Step 4: Implementar attachGridListeners()**

```js
  function attachGridListeners() {
    const grid = document.getElementById('character-grid');

    // Click en sprite personaje (cabecera): toggle unlocked
    grid.querySelectorAll('.char-grid-col-header').forEach(th => {
      th.addEventListener('click', () => {
        const slug = th.dataset.slug;
        const s = loadState(CHAR_STORAGE_KEY);
        const key = `${slug}_unlocked`;
        s[key] = !s[key];
        saveState(s, CHAR_STORAGE_KEY);
        th.classList.toggle('locked', !s[key]);
        // Toggle col-locked en todas las celdas de la columna
        const colIdx = Array.from(th.parentNode.children).indexOf(th);
        grid.querySelectorAll('tbody tr').forEach(tr => {
          const cell = tr.children[colIdx];
          if (cell) cell.classList.toggle('col-locked', !s[key]);
        });
        updateCharProgress();
      });

      // Hover: tooltip personaje
      th.addEventListener('mouseenter', () => {
        const c = CHARACTERS.find(x => x.slug === th.dataset.slug);
        if (c) showCharTooltip(c, th);
      });
      th.addEventListener('mouseleave', hideTooltip);
    });

    // Click en celda: toggle mark
    grid.querySelectorAll('.char-grid-cell').forEach(td => {
      td.addEventListener('click', () => {
        const slug = td.dataset.slug;
        const mark = parseInt(td.dataset.mark, 10);
        const s = loadState(CHAR_STORAGE_KEY);
        const key = `${slug}_mark_${mark}`;
        s[key] = !s[key];
        saveState(s, CHAR_STORAGE_KEY);
        td.classList.toggle('done', s[key]);
        updateCharProgress();
      });

      // Hover: tooltip celda (item — char × mark)
      td.addEventListener('mouseenter', () => {
        const itemName = td.dataset.itemName;
        if (!itemName) return;
        showSimpleTooltip(`${itemName} — ${td.dataset.charName} × ${td.dataset.markName}`, td);
      });
      td.addEventListener('mouseleave', hideTooltip);
    });
  }
```

- [ ] **Step 5: Añadir showSimpleTooltip() (helper nuevo)**

Buscar la función `showCharTooltip` existente. Justo antes o después de ella, añadir:

```js
  function showSimpleTooltip(text, anchor) {
    tooltipEl.innerHTML = `<div style="padding:2px 4px; font-size:0.78rem">${text}</div>`;
    tooltipEl.classList.add('visible');
    positionTooltip(anchor);
  }
```

- [ ] **Step 6: Verificar interacción en navegador**

Recargar. Probar:
- Click en celda con ítem: opacidad cambia, progress bar actualiza.
- Click en sprite personaje: candado aparece/desaparece + columna se atenúa.
- Hover sprite: tooltip con info completa.
- Hover celda: tooltip "Item — Char × Mark".
- Hover icono jefe (col izq): tooltip nativo del navegador con `title`.

---

## Task 9: Actualizar toggle Tainted (sustituir en vez de apilar)

**Files:**
- Modify: `challenges.html` función `setTaintedVisible` (~líneas 1439-1444).

- [ ] **Step 1: Reescribir setTaintedVisible**

Sustituir:
```js
  function setTaintedVisible(visible) {
    taintedList.classList.toggle('visible', visible);
    taintedBtn.textContent = visible ? '🙈 Ocultar Tainted' : '👁 Mostrar Tainted';
    localStorage.setItem(TAINTED_VISIBLE_KEY, visible ? '1' : '0');
    updateCharProgress();
  }
```

Por:
```js
  function setTaintedVisible(visible) {
    const grid = document.getElementById('character-grid');
    grid.dataset.tainted = visible ? '1' : '0';
    taintedBtn.textContent = visible ? '🙈 Ocultar Tainted (volver a Normal)' : '👁 Mostrar Tainted';
    localStorage.setItem(TAINTED_VISIBLE_KEY, visible ? '1' : '0');
    renderCharacterGrid();
  }
```

- [ ] **Step 2: Eliminar la referencia obsoleta a taintedList**

Buscar `const taintedList = document.getElementById('tainted-list');` y eliminar la línea (ya no existe ese elemento).

- [ ] **Step 3: Ajustar el listener del botón**

Buscar:
```js
  taintedBtn.addEventListener('click', () => {
    setTaintedVisible(!taintedList.classList.contains('visible'));
  });
```

Sustituir por:
```js
  taintedBtn.addEventListener('click', () => {
    const grid = document.getElementById('character-grid');
    setTaintedVisible(grid.dataset.tainted !== '1');
  });
```

- [ ] **Step 4: Verificar en navegador**

Recargar. Click en "Mostrar Tainted": la rejilla se reemplaza por la de Tainted con la esquina diciendo "TAINTED CHARACTERS". Click de nuevo: vuelve a Normal. La preferencia se persiste al recargar.

---

## Task 10: Ajustar updateCharProgress() para el modo actual

**Files:**
- Modify: `challenges.html` función `updateCharProgress` (~líneas 1111-1130).

- [ ] **Step 1: Sustituir la lógica de "visible"**

La función actual depende de `document.getElementById('tainted-list').classList.contains('visible')` para decidir qué personajes contar. Cambiar a leer `data-tainted` del grid.

Sustituir:
```js
  function updateCharProgress() {
    const state = loadState(CHAR_STORAGE_KEY);
    const taintedVisible = document.getElementById('tainted-list').classList.contains('visible');
    const visible = taintedVisible ? CHARACTERS : CHARACTERS.filter(c => !c.tainted);
    // ...
  }
```

Por:
```js
  function updateCharProgress() {
    const state = loadState(CHAR_STORAGE_KEY);
    const grid = document.getElementById('character-grid');
    const taintedMode = grid && grid.dataset.tainted === '1';
    const visible = CHARACTERS.filter(c => c.tainted === taintedMode);
    let unlocked = 0, doneMarks = 0;
    const totalUnlocks = visible.length;
    const totalMarks = visible.length * COMPLETION_MARKS.length;
    visible.forEach(c => {
      if (state[`${c.slug}_unlocked`]) unlocked++;
      COMPLETION_MARKS.forEach(m => {
        if (state[`${c.slug}_mark_${m.id}`]) doneMarks++;
      });
    });
    const totalAll = totalUnlocks + totalMarks;
    const doneAll = unlocked + doneMarks;
    const pct = totalAll ? Math.round((doneAll / totalAll) * 100) : 0;
    document.getElementById('charProgressBar').style.width = pct + '%';
    document.getElementById('charProgressLabel').textContent =
      `${unlocked}/${totalUnlocks} desbloqueados · ${doneMarks}/${totalMarks} marks (${pct}%)`;
  }
```

Nota: ahora el progreso muestra solo el set actualmente visible (Normal o Tainted), no ambos sumados. Esto es coherente con el toggle de "switch" en vez de apilar.

- [ ] **Step 2: Actualizar resetAll('characters')**

Buscar:
```js
    } else if (scope === 'characters') {
      if (!confirm('¿Resetear el progreso de personajes?')) return;
      saveState({}, CHAR_STORAGE_KEY);
      renderCharacters();
    }
```

Sustituir `renderCharacters()` por `renderCharacterGrid()`.

- [ ] **Step 3: Verificar**

Recargar. Click en celdas: progress label se actualiza con conteos correctos. Toggle Tainted: el conteo refleja solo el set Tainted. Reset: limpia el grid actual y el progreso queda en 0.

---

## Task 11: Inicialización al cargar

**Files:**
- Modify: `challenges.html` bloque de inicialización al final del script (~líneas 1449-1452).

- [ ] **Step 1: Localizar el bloque de init**

Buscar:
```js
  // Init
  // ...
  renderCharacters();
```

- [ ] **Step 2: Sustituir llamada inicial**

Cambiar `renderCharacters();` por `renderCharacterGrid();`.

- [ ] **Step 3: Verificar que el estado del toggle Tainted se respeta al cargar**

Confirmar que justo antes de `renderCharacterGrid()` ya se ha leído `TAINTED_VISIBLE_KEY` y aplicado a `setTaintedVisible(...)`. Si esa secuencia ya está en el código actual antes de `renderCharacters()`, no hay que tocar nada extra. Si no, mover el bloque para que se ejecute primero.

- [ ] **Step 4: Verificar persistencia entre recargas**

Activar Tainted. Click en algunas celdas. Recargar. Debe abrir en modo Tainted con los marks marcados.

---

## Task 12: Limpieza de código y CSS obsoletos

**Files:**
- Modify: `challenges.html` (varios bloques de CSS y JS).

- [ ] **Step 1: Eliminar CSS de la lista antigua**

Buscar y eliminar (o vaciar si compartidas con otros usos) las reglas:
- `.char-marks-toggle` y sus variantes
- `.marks-row` y `.marks-row.expanded`
- `.mark` y `.mark.done`
- `.char-sprite` (si era exclusiva del listado antiguo — verificar que no se usa en el tooltip; si se usa, mantener)
- `#tainted-list { display: none }` y `#tainted-list.visible` (ya no existe el elemento)

- [ ] **Step 2: Verificar que no quedan referencias a vanilla-list / tainted-list**

Buscar en el archivo: `vanilla-list`, `tainted-list`. Deben quedar 0 ocurrencias (excepto en TAINTED_VISIBLE_KEY que es solo el nombre de la clave de localStorage).

- [ ] **Step 3: Verificar que `renderCharacters` ya no aparece**

Buscar `renderCharacters`. Solo debe aparecer dentro del nombre `renderCharacterGrid` o nada.

- [ ] **Step 4: Verificar en navegador**

Recargar. Todo debe seguir funcionando. La consola del navegador no debe mostrar errores.

---

## Task 13: QA visual final

**Files:**
- Read only.

- [ ] **Step 1: Checklist visual con la rejilla Normal**

Abrir `challenges.html` en navegador (modo Normal por defecto, con progreso reseteado vía `localStorage.clear()` en consola).

Comprobar:
- [ ] Rejilla 17 columnas × 12 filas + 1 columna izq (jefes) + 1 fila sup (personajes).
- [ ] Esquina sup-izq dice "NORMAL CHARACTERS".
- [ ] Personajes ordenados por tier S→D con separadores visibles entre tiers.
- [ ] Iconos de jefes visibles a la izquierda (o emojis fallback si no había URLs).
- [ ] Celdas con ítem muestran sprite; algunas tienen borde amarillo (priority).
- [ ] Celdas vacías (sin ítem) están sin contenido y no son clickeables.

- [ ] **Step 2: Checklist interactivo**

- [ ] Click en celda con ítem: se atenúa el icono.
- [ ] Click otra vez: vuelve a opaco.
- [ ] Click en sprite personaje (cabecera): aparece candado + columna se atenúa.
- [ ] Hover sprite: aparece tooltip con tier/unlock/prioridad/wiki link.
- [ ] Hover celda con ítem: tooltip pequeño "Item — Char × Mark".
- [ ] Progress bar y label se actualizan en cada click.

- [ ] **Step 3: Checklist toggle Tainted**

- [ ] Click "Mostrar Tainted": rejilla cambia a Tainted.
- [ ] Esquina dice "TAINTED CHARACTERS".
- [ ] 17 sprites Tainted visibles, todos con `priority: false`.
- [ ] Click "Ocultar Tainted (volver a Normal)": vuelve a Normal.
- [ ] Preferencia persiste tras F5.

- [ ] **Step 4: Checklist preservación**

- [ ] Vista de Desafíos sigue funcionando idéntica.
- [ ] Tabs cambian correctamente.
- [ ] `resetAll('characters')` limpia el grid actual.
- [ ] Tras un `localStorage.clear()` + recarga, todo arranca en estado limpio.

- [ ] **Step 5: Eliminar backup**

Si todo funciona y el usuario lo aprueba:
```bash
rm "challenges.html.backup"
rm -f "_data-marks.txt" "_data-normal.txt" "_data-tainted.txt"
```

(O moverlos a un directorio `_scratch/` si se quieren mantener para depuración.)

- [ ] **Step 6: Informar al usuario**

Mostrar resumen: archivo modificado, líneas aproximadas añadidas/eliminadas, comportamientos preservados, próximas mejoras opcionales (móvil, embed base64 si la wiki cae, etc.).

---

## Notas para el ejecutor

- **Sin tests automatizados**: el proyecto no los tiene y crearlos sería sobre-ingeniería para un archivo HTML estático. La verificación es manual en cada paso vía navegador.
- **No hay git**: el directorio no es repo. Los "commits" del plan son puntos lógicos de progreso, no commits reales. Mantener `challenges.html.backup` como red de seguridad hasta el QA final.
- **YAGNI**: si una task añade complejidad innecesaria (ej. animaciones, transiciones extra), simplificar.
- **DRY**: si dos tasks producen código repetido, refactorizar en una helper antes de avanzar.
- **Wiki rate limit**: no abusar con paralelismo extremo (lotes de 4-5 fetches está bien). Si la wiki devuelve 429, esperar y reintentar.
- **Discrepancias de slug**: el slug local (en `CHARACTERS`) manda. Si la wiki usa otro slug, mapear localmente en la extracción.
- **Sprites null**: aceptables. La celda muestra el nombre como texto pequeño en lugar del icono.
- **Si las URLs de la wiki rompen** en algún momento futuro: migrar a Enfoque B (base64) sin tocar la lógica.
