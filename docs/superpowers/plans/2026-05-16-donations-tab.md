# Donaciones — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir una pestaña "Donaciones" que muestra los contadores acumulados de la máquina de donación normal (0-1000) y de la Greed Donation Machine (0-999), junto con los ítems / personajes que se desbloquean en cada hito.

**Architecture:** Extender `save_parser` para extraer el chunk 2 (counters) que ya está estructurado pero no decodificado. Añadir dos campos a `ParsedSave`, propagar por `state_mapper`. Crear un módulo nuevo `tracker/data/donations.py` con las listas de hitos. En el frontend, añadir una séptima pestaña que renderiza dos secciones idénticas en estructura, alimentadas por el estado.

**Tech Stack:** Python (parser/state), pytest (tests), HTML/CSS/JS vanilla (frontend), PyWebView (host), Nuitka (build).

**Spec:** `docs/superpowers/specs/2026-05-16-greed-donations-design.md`

---

## Pre-Task 0: Investigación bloqueante

Esta investigación produce dos datos que **todas las tareas posteriores necesitan**. No avances sin esto.

### 0.1 — Identificar índices del chunk 2

**Files:**
- Read: `tracker/save_parser.py` (entender extracción de chunks)
- Read: `tests/fixtures/20260514.rep+persistentgamedata1.dat` (save real del usuario)

- [ ] **Step 1: Preguntar al usuario los valores actuales en el juego**

Mensaje exacto al usuario:

> Para identificar los contadores de donación en el save, abre Isaac y ve a Stats → busca "Donation Machine" y "Greed Donation Machine". Dime el valor exacto de cada uno. Si nunca has donado en alguna, dime 0.

Anotar los dos valores: `NORMAL_REAL` y `GREED_REAL`.

- [ ] **Step 2: Extraer el chunk 2 completo del fixture y buscar los valores**

Script ad-hoc (no commitear) para encontrar los offsets:

```python
import struct
from pathlib import Path

data = Path("tests/fixtures/20260514.rep+persistentgamedata1.dat").read_bytes()

# Saltar header + chunk 1 (achievements, 1 byte/entry).
off = 20  # header
chunk1_count = struct.unpack_from("<iii", data, off)[2]
off += 12 + chunk1_count * 1

# Ahora estamos en chunk 2 (counters, 4 bytes/entry).
chunk2_type, _len, chunk2_count = struct.unpack_from("<iii", data, off)
assert chunk2_type == 2, f"expected chunk type 2, got {chunk2_type}"
body_start = off + 12
counters = [
    struct.unpack_from("<i", data, body_start + i * 4)[0]
    for i in range(chunk2_count)
]

print(f"chunk 2 has {len(counters)} counters")
NORMAL_REAL = ...  # del Step 1
GREED_REAL = ...   # del Step 1
print(f"indices == NORMAL_REAL ({NORMAL_REAL}):", [i for i, v in enumerate(counters) if v == NORMAL_REAL])
print(f"indices == GREED_REAL  ({GREED_REAL}):",  [i for i, v in enumerate(counters) if v == GREED_REAL])
```

Run: `python -c "<script arriba>"`
Expected: Cada valor aparece típicamente en 1-3 índices. Si hay ambigüedad, pedir al usuario un segundo dato (ej. "deaths count") para descartar.

- [ ] **Step 3: Validar contra una segunda referencia**

Si el chunk 2 tiene varios índices con el mismo valor, buscar paralelamente otro contador conocido (deaths, mom kills, secret rooms found) en `achievements.json` (busca achievements con texto tipo "Mom kills") y triangula. Documentar el método en un comentario.

- [ ] **Step 4: Anotar los índices identificados**

Guardar en variables internas:
```
DONATION_NORMAL_INDEX = <int>
DONATION_GREED_INDEX = <int>
```

Estos van a constantes en `tracker/save_parser.py` en Task 2.

- [ ] **Step 5: Commit nada todavía** — esto es solo investigación.

### 0.2 — Compilar lista de hitos de Greed Donation Machine

**Files:**
- Read: `tracker/data/achievements.json`

- [ ] **Step 1: Filtrar achievements por términos relacionados**

```bash
rtk grep -i "greed donation\|greed machine\|greed mode donation" tracker/data/achievements.json
```

Buscar también: "Ultra Greed", "Greedier", "donate" sin "donation" — el dataset es ruidoso.

- [ ] **Step 2: Construir la tabla manualmente cross-referencing con la wiki**

Para cada achievement candidato, comprobar que su descripción menciona "donate to the Greed Donation Machine" (o equivalente en español si el JSON está traducido). Anotar `amount`, `achievement_id`, `name`, `item_id` (si aplica).

- [ ] **Step 3: Si la lista no se puede construir con certeza**

Documentar como TBD y, en Task 1, dejar `GREED_DONATION_MILESTONES = []` con un comentario `# TODO: confirmar lista (ver spec, sección Riesgos)`. La sección de Greed en la UI muestra "Lista pendiente — solo contador" hasta que se resuelva.

- [ ] **Step 4: Commit nada** — esto entra en código en Task 1.

---

## Task 1: Módulo de datos `tracker/data/donations.py`

**Files:**
- Create: `tracker/data/donations.py`
- Test: `tests/test_donations_data.py`

- [ ] **Step 1: Escribir test fallido**

```python
# tests/test_donations_data.py
from tracker.data.donations import DONATION_MILESTONES, GREED_DONATION_MILESTONES


def test_donation_milestones_are_sorted_ascending():
    amounts = [m["amount"] for m in DONATION_MILESTONES]
    assert amounts == sorted(amounts), f"DONATION_MILESTONES not sorted: {amounts}"


def test_donation_milestones_have_required_fields():
    required = {"amount", "achievement_id", "name"}
    for m in DONATION_MILESTONES:
        assert required.issubset(m.keys()), f"missing fields in {m}"
        assert isinstance(m["amount"], int) and m["amount"] > 0
        assert isinstance(m["achievement_id"], int) and 0 <= m["achievement_id"] < 642


def test_donation_normal_has_known_milestones():
    by_amount = {m["amount"]: m["name"] for m in DONATION_MILESTONES}
    assert 1 in by_amount
    assert 879 in by_amount  # Holy Mantle para The Lost
    assert 1000 in by_amount  # Keeper


def test_greed_milestones_sorted_or_empty():
    # GREED_DONATION_MILESTONES puede estar vacío si Task 0.2 quedó TBD.
    if GREED_DONATION_MILESTONES:
        amounts = [m["amount"] for m in GREED_DONATION_MILESTONES]
        assert amounts == sorted(amounts)
```

- [ ] **Step 2: Verificar que falla**

Run: `pytest tests/test_donations_data.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'tracker.data.donations'`.

- [ ] **Step 3: Implementar el módulo**

```python
# tracker/data/donations.py
"""
Datos de las dos máquinas de donación de Repentance+.

`DONATION_MILESTONES`: máquina de donación normal (la de tiendas en runs
normales). Hitos confirmados contra tracker/data/achievements.json.

`GREED_DONATION_MILESTONES`: máquina de la Greed Donation Machine (modo
Greed). Lista confirmada en Task 0.2 del plan; puede estar vacía si esa
investigación quedó pendiente — la UI lo gestiona mostrando solo contador.
"""
from __future__ import annotations

DONATION_MILESTONES: list[dict] = [
    {"amount": 1,    "achievement_id": <FILL>, "name": "Lucky Pennies",                  "item_id": <FILL or None>},
    {"amount": 10,   "achievement_id": <FILL>, "name": "Special Hanging Shopkeepers",    "item_id": None},
    {"amount": 30,   "achievement_id": <FILL>, "name": "Wooden Nickel",                  "item_id": <FILL>},
    {"amount": 68,   "achievement_id": <FILL>, "name": "Cain holds Paperclip",           "item_id": None},
    {"amount": 111,  "achievement_id": <FILL>, "name": "Everything is Terrible 2!!!",    "item_id": None},
    {"amount": 234,  "achievement_id": <FILL>, "name": "Special Shopkeepers",            "item_id": None},
    {"amount": 439,  "achievement_id": <FILL>, "name": "Eve holds Razor Blade",          "item_id": None},
    {"amount": 500,  "achievement_id": <FILL>, "name": "Greedier!",                      "item_id": None},
    {"amount": 666,  "achievement_id": <FILL>, "name": "Store Key",                      "item_id": <FILL>},
    {"amount": 879,  "achievement_id": <FILL>, "name": "The Lost holds Holy Mantle",     "item_id": None},
    {"amount": 1000, "achievement_id": <FILL>, "name": "Keeper",                         "item_id": None},
]

GREED_DONATION_MILESTONES: list[dict] = [
    # Si Task 0.2 produjo lista: rellenar igual que arriba.
    # Si quedó TBD: dejar vacío con este comentario:
    # TODO: compilar contra achievements.json y wiki oficial.
]
```

Resolver cada `<FILL>` buscando el achievement por `name` en `tracker/data/achievements.json`. Ejemplo:
```bash
rtk grep -n '"name": "Lucky Pennies"' tracker/data/achievements.json
```

- [ ] **Step 4: Verificar que pasa**

Run: `pytest tests/test_donations_data.py -v`
Expected: 4 PASS (o 3 PASS + 1 con `GREED_DONATION_MILESTONES` vacío todavía pasa por la guarda `if`).

- [ ] **Step 5: Commit**

```bash
rtk git add tracker/data/donations.py tests/test_donations_data.py
rtk git commit -m "feat(data): añadir tabla de hitos de máquinas de donación"
```

---

## Task 2: Extender parser para extraer chunk 2

**Files:**
- Modify: `tracker/save_parser.py`
- Test: `tests/test_save_parser.py`

- [ ] **Step 1: Escribir test fallido**

```python
# Añadir a tests/test_save_parser.py
def test_parser_extracts_donation_counters(sample_save_path):
    """El parser debe exponer los dos contadores de donación como ints."""
    from tracker.save_parser import parse_save
    parsed = parse_save(sample_save_path)
    assert isinstance(parsed.donation_count, int)
    assert isinstance(parsed.greed_donation_count, int)
    # Rango sano: ambos contadores son <= 1000.
    assert 0 <= parsed.donation_count <= 1000
    assert 0 <= parsed.greed_donation_count <= 999
```

- [ ] **Step 2: Verificar que falla**

Run: `pytest tests/test_save_parser.py::test_parser_extracts_donation_counters -v`
Expected: FAIL con `AttributeError: ... 'donation_count'`.

- [ ] **Step 3: Implementar la extracción**

Editar `tracker/save_parser.py`:

```python
# Añadir constantes cerca de las existentes (alrededor de L103-105):
_CHUNK_COUNTERS = 2
_DONATION_NORMAL_INDEX = <índice de Task 0.1>  # validado en task 0.1
_DONATION_GREED_INDEX = <índice de Task 0.1>

# Añadir campos al dataclass ParsedSave (L75-81):
@dataclass(frozen=True)
class ParsedSave:
    slot: int
    challenges_complete: set[int] = field(default_factory=set)
    characters_unlocked: set[int] = field(default_factory=set)
    character_marks: dict[int, set[int]] = field(default_factory=dict)
    achievements_unlocked: set[int] = field(default_factory=set)
    items_seen: set[int] = field(default_factory=set)
    donation_count: int = 0
    greed_donation_count: int = 0
    parsed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

# Añadir helper:
def _extract_donation_counters(counters_body: bytes) -> tuple[int, int]:
    """Lee los dos contadores de donación del chunk 2 (4 bytes LE por entry).

    Los índices DONATION_NORMAL_INDEX y DONATION_GREED_INDEX fueron
    validados contra un save real con valores conocidos (ver
    docs/superpowers/plans/2026-05-16-donations-tab.md, Task 0.1).
    """
    def read_at(idx: int) -> int:
        off = idx * 4
        if off + 4 > len(counters_body):
            return 0  # save antiguo / corto; defaultear a 0.
        return struct.unpack_from("<i", counters_body, off)[0]
    return read_at(_DONATION_NORMAL_INDEX), read_at(_DONATION_GREED_INDEX)

# En parse_save (L115+), extender:
counters = chunks.get(_CHUNK_COUNTERS, b"")
donation_count, greed_donation_count = _extract_donation_counters(counters)

return ParsedSave(
    slot=slot,
    challenges_complete=challenges_complete,
    characters_unlocked=characters_unlocked,
    character_marks=character_marks,
    achievements_unlocked=achievements_unlocked,
    items_seen=items_seen,
    donation_count=donation_count,
    greed_donation_count=greed_donation_count,
)
```

- [ ] **Step 4: Verificar que pasa**

Run: `pytest tests/test_save_parser.py -v`
Expected: PASS (incluyendo el test nuevo y los existentes — no romper nada).

- [ ] **Step 5: Commit**

```bash
rtk git add tracker/save_parser.py tests/test_save_parser.py
rtk git commit -m "feat(parser): extraer contadores de máquinas de donación (chunk 2)"
```

---

## Task 3: Propagar contadores por state_mapper

**Files:**
- Modify: `tracker/state_mapper.py`
- Test: `tests/test_state_mapper.py`

- [ ] **Step 1: Escribir test fallido**

```python
# Añadir a tests/test_state_mapper.py
def test_donations_state_exposes_counters_and_milestones():
    """El estado del frontend debe exponer cuántos donations llevas y qué
    hitos están desbloqueados / pendientes, para cada máquina."""
    from tracker.save_parser import ParsedSave
    from tracker.state_mapper import build_localstorage_state

    parsed = ParsedSave(slot=1, donation_count=500, greed_donation_count=50)
    state = build_localstorage_state(parsed)

    donations = state["donations_state"]
    assert donations["normal"]["count"] == 500
    assert donations["greed"]["count"] == 50

    # Cada hito debe tener su flag desbloqueado/pendiente.
    normal_milestones = donations["normal"]["milestones"]
    assert isinstance(normal_milestones, list)
    # En el spec hay un hito a 500 ("Greedier!") — con count=500, debe estar unlocked.
    by_amount = {m["amount"]: m for m in normal_milestones}
    assert by_amount[500]["unlocked"] is True
    # 666 todavía no.
    assert by_amount[666]["unlocked"] is False
```

- [ ] **Step 2: Verificar que falla**

Run: `pytest tests/test_state_mapper.py::test_donations_state_exposes_counters_and_milestones -v`
Expected: FAIL con `KeyError: 'donations_state'`.

- [ ] **Step 3: Implementar**

Editar `tracker/state_mapper.py`:

```python
# Añadir import en cabecera:
from tracker.data.donations import DONATION_MILESTONES, GREED_DONATION_MILESTONES

# Añadir builder:
def _build_donations_state(parsed: ParsedSave) -> dict:
    def section(count: int, milestones: list[dict]) -> dict:
        return {
            "count": count,
            "milestones": [
                {**m, "unlocked": count >= m["amount"]}
                for m in milestones
            ],
        }
    return {
        "normal": section(parsed.donation_count, DONATION_MILESTONES),
        "greed":  section(parsed.greed_donation_count, GREED_DONATION_MILESTONES),
    }

# En build_localstorage_state, añadir la entrada:
def build_localstorage_state(parsed: ParsedSave) -> dict:
    return {
        "challenges_state": _build_challenges(parsed),
        "characters_state": _build_characters(parsed),
        "achievements_unlocked": sorted(parsed.achievements_unlocked),
        "items_state": _build_items_state(parsed),
        "cards_state": _build_cards_state(parsed),
        "donations_state": _build_donations_state(parsed),
        "meta": {
            "slot": parsed.slot,
            "parsed_at": parsed.parsed_at.isoformat(),
        },
    }
```

- [ ] **Step 4: Verificar que pasa**

Run: `pytest tests/test_state_mapper.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add tracker/state_mapper.py tests/test_state_mapper.py
rtk git commit -m "feat(state): exponer donations_state al frontend"
```

---

## Task 4: HTML de la pestaña Donaciones

**Files:**
- Modify: `challenges.html` (raíz) y `tracker/assets/challenges.html` (mirror — usar `cp` desde la raíz al final, o editar ambos)

- [ ] **Step 1: Añadir el botón en la barra de tabs**

Localizar L1832-1839 (la barra de tabs). Añadir botón al final:

```html
    <button class="tab" data-view="donations">Donaciones</button>
```

- [ ] **Step 2: Añadir el contenedor de la vista**

Después de la última `<div class="view" id="view-cards">` (buscar `view-cards` para localizar) y antes del cierre del bloque de vistas, añadir:

```html
  <div class="view" id="view-donations">
    <section class="donation-section" id="donation-normal">
      <header class="donation-header">
        <div class="donation-icon" data-machine="normal"></div>
        <div class="donation-title">Máquina de donación</div>
        <div class="donation-counter"><span id="donationNormalCount">0</span> / 1000</div>
        <div class="donation-progress-container">
          <div class="donation-progress" id="donationNormalBar"></div>
        </div>
        <div class="donation-summary" id="donationNormalSummary"></div>
      </header>
      <ul class="donation-milestones" id="donationNormalMilestones"></ul>
    </section>

    <section class="donation-section" id="donation-greed">
      <header class="donation-header">
        <div class="donation-icon" data-machine="greed"></div>
        <div class="donation-title">Máquina de Greed</div>
        <div class="donation-counter"><span id="donationGreedCount">0</span> / 999</div>
        <div class="donation-progress-container">
          <div class="donation-progress" id="donationGreedBar"></div>
        </div>
        <div class="donation-summary" id="donationGreedSummary"></div>
      </header>
      <ul class="donation-milestones" id="donationGreedMilestones"></ul>
    </section>
  </div>
```

- [ ] **Step 3: Verificar manualmente**

Abrir `challenges.html` directamente en un navegador. Click en "Donaciones" — debería cambiar de pestaña pero estar vacía (sin CSS ni JS aún).

- [ ] **Step 4: Commit**

```bash
rtk git add challenges.html
rtk git commit -m "feat(ui): añadir esqueleto HTML de la pestaña Donaciones"
```

---

## Task 5: CSS de la pestaña

**Files:**
- Modify: `challenges.html` (bloque `<style>`)

- [ ] **Step 1: Añadir reglas CSS**

Localizar el bloque `<style>` (busca `.tab.active {` cerca de L666 para situarte). Al final del bloque, antes de `</style>`, añadir:

```css
/* ===== Pestaña Donaciones ===== */
#view-donations {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 16px 0;
}
.donation-section {
  background: #181818;
  border: 1px solid #2c2c2c;
  border-radius: 8px;
  padding: 16px;
}
.donation-header {
  display: grid;
  grid-template-columns: 64px 1fr auto;
  grid-template-areas:
    "icon title counter"
    "icon progress progress"
    "icon summary summary";
  gap: 8px 16px;
  align-items: center;
}
.donation-icon {
  grid-area: icon;
  width: 64px;
  height: 64px;
  background: #2c2c2c;
  border-radius: 6px;
  /* TODO: sprite real si existe; por ahora placeholder gris */
}
.donation-title {
  grid-area: title;
  font-size: 18px;
  font-weight: bold;
  color: #ffd766;
}
.donation-counter {
  grid-area: counter;
  font-size: 24px;
  font-weight: bold;
  color: #ffd766;
}
.donation-progress-container {
  grid-area: progress;
  height: 10px;
  background: #2c2c2c;
  border-radius: 5px;
  overflow: hidden;
}
.donation-progress {
  height: 100%;
  background: linear-gradient(90deg, #ffd766, #ffa500);
  width: 0%;
  transition: width 200ms ease;
}
.donation-summary {
  grid-area: summary;
  font-size: 13px;
  color: #aaa;
}
.donation-milestones {
  list-style: none;
  padding: 0;
  margin: 16px 0 0 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.donation-milestone {
  display: grid;
  grid-template-columns: 32px 1fr 60px 120px;
  gap: 12px;
  align-items: center;
  padding: 6px 8px;
  border-radius: 4px;
  background: #1f1f1f;
}
.donation-milestone .ms-icon {
  width: 32px;
  height: 32px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}
.donation-milestone.locked .ms-icon { filter: grayscale(1) brightness(0.5); }
.donation-milestone .ms-name { color: #ddd; }
.donation-milestone.locked .ms-name { color: #777; }
.donation-milestone .ms-amount {
  text-align: right;
  color: #aaa;
  font-variant-numeric: tabular-nums;
}
.donation-milestone .ms-status {
  text-align: right;
  font-size: 12px;
  font-weight: bold;
}
.donation-milestone.unlocked .ms-status { color: #6cd66c; }
.donation-milestone.locked .ms-status { color: #c08a3e; }
.donation-section.full .donation-summary { color: #6cd66c; font-weight: bold; }
```

- [ ] **Step 2: Verificación manual**

Abrir `challenges.html` en navegador, click "Donaciones": deberías ver dos tarjetas con cabeceras pero milestones vacías (todavía sin JS).

- [ ] **Step 3: Commit**

```bash
rtk git add challenges.html
rtk git commit -m "feat(ui): añadir CSS de la pestaña Donaciones"
```

---

## Task 6: JS que renderiza las dos secciones

**Files:**
- Modify: `challenges.html` (bloque `<script>`)

- [ ] **Step 1: Añadir la función de renderizado**

Localizar `function switchTab(view)` (L5778). Justo encima o debajo añadir:

```javascript
// ===== Donaciones =====
function renderDonations(state) {
  if (!state || !state.donations_state) return;
  renderDonationSection('normal', state.donations_state.normal, 1000);
  renderDonationSection('greed',  state.donations_state.greed,  999);
}

function renderDonationSection(key, section, max) {
  const counterEl = document.getElementById(`donation${cap(key)}Count`);
  const barEl     = document.getElementById(`donation${cap(key)}Bar`);
  const summaryEl = document.getElementById(`donation${cap(key)}Summary`);
  const listEl    = document.getElementById(`donation${cap(key)}Milestones`);
  const sectionEl = document.getElementById(`donation-${key}`);
  if (!counterEl) return;

  const count = section.count || 0;
  const milestones = section.milestones || [];
  const unlocked = milestones.filter(m => m.unlocked).length;

  counterEl.textContent = count;
  barEl.style.width = `${Math.min(100, (count / max) * 100)}%`;

  if (count >= max) {
    summaryEl.textContent = "Máquina llena";
    sectionEl.classList.add('full');
  } else {
    sectionEl.classList.remove('full');
    summaryEl.textContent = milestones.length === 0
      ? "Lista de hitos pendiente — solo contador"
      : `Has desbloqueado ${unlocked} de ${milestones.length} ítems`;
  }

  listEl.innerHTML = '';
  for (const m of milestones) {
    const li = document.createElement('li');
    li.className = 'donation-milestone ' + (m.unlocked ? 'unlocked' : 'locked');
    const remaining = Math.max(0, m.amount - count);
    const statusText = m.unlocked ? '✓ Desbloqueado' : `Faltan ${remaining}`;
    const iconStyle = m.item_id
      ? `style="background-image: url('item_icons/collectibles_${String(m.item_id).padStart(3, '0')}.png');"`
      : '';
    li.innerHTML = `
      <div class="ms-icon" ${iconStyle}></div>
      <div class="ms-name">${escapeHtml(m.name)}</div>
      <div class="ms-amount">${m.amount}</div>
      <div class="ms-status">${statusText}</div>
    `;
    listEl.appendChild(li);
  }
}

function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}
```

- [ ] **Step 2: Conectar al ciclo de actualización de estado**

Localizar `window.applyIsaacState` (search "applyIsaacState"). Después de que aplique los demás estados, añadir:

```javascript
renderDonations(state);
```

Si no existe ese punto explícito, conectar en el mismo sitio donde se renderiza la grid de items.

- [ ] **Step 3: Verificación manual**

```powershell
rtk python -m tracker.app
```

Abrir Donaciones — deberías ver los contadores y la lista de hitos. Validar que:
- Contadores muestran los valores reales del save.
- Hitos por debajo del contador están en verde ("✓ Desbloqueado").
- Hitos por encima están en gris con "Faltan X".
- Hover sobre un hito con icono muestra el sprite del ítem.

- [ ] **Step 4: Commit**

```bash
rtk git add challenges.html
rtk git commit -m "feat(ui): renderizar contadores e hitos de donaciones"
```

---

## Task 7: Sincronizar mirror del HTML y rebuildear .exe

**Files:**
- Modify: `tracker/assets/challenges.html` (mirror)
- Build: `dist/IsaacTracker.exe`

- [ ] **Step 1: Copiar challenges.html al mirror del bundle**

```powershell
Copy-Item challenges.html tracker/assets/challenges.html -Force
```

- [ ] **Step 2: Rebuildear el .exe**

```powershell
rtk python build_nuitka.py
```
o el script de build que el repo use. Verificar que `dist/IsaacTracker.exe` aparece y abrir el ejecutable.

- [ ] **Step 3: Verificación manual en el .exe**

- La pestaña "Donaciones" aparece.
- Ambas secciones rellenan con los contadores reales.
- Cambiar de pestaña y volver mantiene el render.

- [ ] **Step 4: Commit**

```bash
rtk git add tracker/assets/challenges.html
rtk git commit -m "build: sincronizar mirror HTML y rebuildear IsaacTracker.exe"
```

---

## Task 8: Verificación final y limpieza

- [ ] **Step 1: Ejecutar suite completa**

```bash
rtk pytest -q
```
Expected: todos PASS.

- [ ] **Step 2: Smoke test manual del flujo completo**

Abrir `dist/IsaacTracker.exe`:
1. La app levanta sin error.
2. Pestañas existentes siguen funcionando (Desafíos, Personajes, Logros, Ítems, Trinkets, Cartas).
3. Donaciones muestra ambas secciones con datos coherentes.
4. Si la lista de Greed está vacía (TBD), aparece el mensaje "Lista de hitos pendiente — solo contador" y el contador sí se ve.

- [ ] **Step 3: Si todo OK, no hay commit final.**

Si algo falla, parar y abrir issue / pedir review en lugar de seguir.

---

## Self-Review (autoejecutado al terminar de escribir el plan)

**Spec coverage:**

- ✅ Pestaña nueva "Donaciones" en barra (Task 4).
- ✅ Sección normal con cabecera + lista (Task 4, 5, 6).
- ✅ Sección Greed con cabecera + lista (Task 4, 5, 6).
- ✅ Cabecera: icono + contador + barra + resumen (Task 5, 6).
- ✅ Lista con icono + nombre + cantidad + estado (Task 5, 6).
- ✅ Tooltips reutilizando estilo de Ítems — **NO cubierto explícitamente**. Falta una task que conecte el hover sobre `.ms-icon` al `showItemTooltip` existente. Lo dejo como nota: si el usuario lo pide tras la primera implementación, añadir como Task 6.5.
- ✅ Estados especiales (0, max) — Task 6.
- ✅ Datos del chunk 2 — Task 0.1, Task 2.
- ✅ Lista de hitos — Task 0.2, Task 1.
- ✅ Tests parser, state mapper, donations data — Tasks 1, 2, 3.

**Placeholder scan:**

- `<FILL>` en Task 1: intencional — se resuelve buscando en `achievements.json` durante esa task. Cada `<FILL>` tiene un comando concreto para encontrarlo. Aceptable.
- `<índice de Task 0.1>` en Task 2: intencional — depende de la investigación. Aceptable.

**Type consistency:**

- `ParsedSave.donation_count` / `greed_donation_count` consistentes entre Tasks 2 y 3.
- `donations_state.normal` / `donations_state.greed` consistentes entre Task 3 y 6.
- `milestone.amount` / `unlocked` / `name` / `item_id` consistentes entre Tasks 1, 3 y 6.

**Tooltip gap:** lo añado al spec como nota de iteración futura, no como bloqueador.
