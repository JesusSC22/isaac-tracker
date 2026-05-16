# Donaciones — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir una pestaña "Donaciones" que muestra los contadores acumulados de la máquina de donación normal (chunk 2 índice 8) y de la Greed Donation Machine (chunk 2 índice 19), junto con los ítems / personajes que se desbloquean en cada hito. Soporta saves "upgraded" desde Afterbirth+ donde el counter es 0 pero los achievements ya están desbloqueados (fuente de verdad híbrida).

**Architecture:** Extender `save_parser` para extraer el chunk 2 (counters) que ya está estructurado pero no decodificado. Añadir dos campos a `ParsedSave`, propagar por `state_mapper`. Crear un módulo nuevo `tracker/data/donations.py` con las listas de hitos (cada uno con `achievement_id` para soportar la fuente híbrida). En el frontend, añadir una séptima pestaña que renderiza dos secciones idénticas en estructura.

**Tech Stack:** Python (parser/state), pytest (tests), HTML/CSS/JS vanilla (frontend), PyWebView (host), Nuitka (build).

**Spec:** `docs/superpowers/specs/2026-05-16-greed-donations-design.md`

**Investigación previa:** Los índices del chunk 2 (`[8]` normal, `[19]` Greed) ya están identificados y confirmados contra el save fixture y el save 100% completado de Zamiell/isaac-save-installer. No queda investigación bloqueante.

---

## Task 1: Módulo de datos `tracker/data/donations.py`

**Files:**
- Create: `tracker/data/donations.py`
- Test: `tests/test_donations_data.py`

- [ ] **Step 1: Escribir test fallido**

```python
# tests/test_donations_data.py
from tracker.data.donations import DONATION_MILESTONES, GREED_DONATION_MILESTONES


def test_donation_milestones_sorted_ascending():
    amounts = [m["amount"] for m in DONATION_MILESTONES]
    assert amounts == sorted(amounts), f"DONATION_MILESTONES not sorted: {amounts}"


def test_greed_milestones_sorted_ascending():
    amounts = [m["amount"] for m in GREED_DONATION_MILESTONES]
    assert amounts == sorted(amounts), f"GREED_DONATION_MILESTONES not sorted: {amounts}"


def test_donation_milestones_have_required_fields():
    required = {"amount", "achievement_id", "name"}
    for m in DONATION_MILESTONES + GREED_DONATION_MILESTONES:
        assert required.issubset(m.keys()), f"missing fields in {m}"
        assert isinstance(m["amount"], int) and m["amount"] > 0
        assert isinstance(m["achievement_id"], int) and 0 <= m["achievement_id"] < 642


def test_known_milestones_present():
    by_amount_greed = {m["amount"]: m for m in GREED_DONATION_MILESTONES}
    by_amount_normal = {m["amount"]: m for m in DONATION_MILESTONES}
    assert by_amount_greed[879]["name"] == "Lost holds Holy Mantle"
    assert by_amount_greed[879]["achievement_id"] == 250
    assert by_amount_greed[1000]["name"] == "Keeper"
    assert by_amount_greed[1000]["achievement_id"] == 251
    assert by_amount_normal[999]["name"] == "Stop Watch"
    assert by_amount_normal[999]["achievement_id"] == 138
```

- [ ] **Step 2: Verificar que falla**

Run: `pytest tests/test_donations_data.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implementar el módulo**

```python
# tracker/data/donations.py
"""
Hitos de las dos máquinas de donación de Repentance+.

Todos los hitos están cross-validated contra
``tracker/data/achievements.json``. Cada entrada lleva el ``achievement_id``
correspondiente — la lógica de "hito desbloqueado" del state_mapper usa
fuente híbrida (counter >= amount OR achievement byte set), porque saves
upgraded desde Afterbirth+ tienen el counter a 0 pero los achievements
ya transferidos.

Ver: docs/superpowers/specs/2026-05-16-greed-donations-design.md
"""
from __future__ import annotations

# Greed Donation Machine — counters[19] del chunk 2 del save Repentance+.
GREED_DONATION_MILESTONES: list[dict] = [
    {"amount":    1, "achievement_id": 242, "name": "Lucky Pennies"},
    {"amount":   10, "achievement_id": 243, "name": "Special Hanging Shopkeepers"},
    {"amount":   30, "achievement_id": 244, "name": "Wooden Nickel"},
    {"amount":   68, "achievement_id": 245, "name": "Cain holds Paperclip"},
    {"amount":  111, "achievement_id": 246, "name": "Everything is Terrible 2!!!"},
    {"amount":  234, "achievement_id": 247, "name": "Special Shopkeepers"},
    {"amount":  439, "achievement_id": 248, "name": "Eve now holds Razor Blade"},
    {"amount":  666, "achievement_id": 249, "name": "Store Key"},
    {"amount":  879, "achievement_id": 250, "name": "Lost holds Holy Mantle"},
    {"amount": 1000, "achievement_id": 251, "name": "Keeper"},
]

# Donation Machine (normal, de tiendas) — counters[8] del chunk 2 del save Repentance+.
DONATION_MILESTONES: list[dict] = [
    {"amount":  10, "achievement_id": 134, "name": "Blue Map"},
    {"amount":  20, "achievement_id": 151, "name": "Store Upgrade lv.1"},
    {"amount":  50, "achievement_id": 135, "name": "There's Options"},
    {"amount": 100, "achievement_id": 152, "name": "Store Upgrade lv.2"},
    {"amount": 150, "achievement_id": 136, "name": "Black Candle"},
    {"amount": 200, "achievement_id": 153, "name": "Store Upgrade lv.3"},
    {"amount": 400, "achievement_id": 137, "name": "Red Candle"},
    {"amount": 600, "achievement_id": 154, "name": "Store Upgrade lv.4"},
    {"amount": 900, "achievement_id":  59, "name": "Blue Candle"},
    {"amount": 999, "achievement_id": 138, "name": "Stop Watch"},
]
```

- [ ] **Step 4: Verificar que pasa**

Run: `pytest tests/test_donations_data.py -v`
Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
rtk git add tracker/data/donations.py tests/test_donations_data.py
rtk git commit -m "feat(data): añadir tabla de hitos de máquinas de donación"
```

---

## Task 2: Extender parser para extraer chunk 2

**Files:**
- Modify: `tracker/save_parser.py`
- Modify: `tests/test_save_parser.py`

- [ ] **Step 1: Escribir test fallido**

```python
# Añadir a tests/test_save_parser.py
def test_parser_extracts_donation_counters(sample_save_path):
    """El parser debe exponer los dos contadores de donación como ints."""
    from tracker.save_parser import parse_save
    parsed = parse_save(sample_save_path)
    assert isinstance(parsed.donation_count, int)
    assert isinstance(parsed.greed_donation_count, int)
    # Ambos contadores son enteros >=0. El fixture es un save migrado de
    # Afterbirth+, por lo que ambos deberían ser 0 — pero el test no
    # asume eso, solo asume rango sano.
    assert parsed.donation_count >= 0
    assert parsed.greed_donation_count >= 0


def test_parser_donation_counters_default_zero_on_short_chunk():
    """Si el chunk 2 es más corto de lo esperado, los contadores caen a 0."""
    from tracker.save_parser import _extract_donation_counters
    # 5 entradas (< índice 8 y 19) — debe defaultear ambos a 0.
    body = b"\x00" * (5 * 4)
    normal, greed = _extract_donation_counters(body)
    assert normal == 0 and greed == 0
```

- [ ] **Step 2: Verificar que falla**

Run: `pytest tests/test_save_parser.py::test_parser_extracts_donation_counters -v`
Expected: FAIL con `AttributeError: ... 'donation_count'`.

- [ ] **Step 3: Implementar la extracción**

Editar `tracker/save_parser.py`:

```python
# Añadir constantes cerca de las existentes (alrededor de L103-105):
_CHUNK_COUNTERS = 2
_DONATION_NORMAL_INDEX = 8   # Donation Machine (tiendas) en chunk 2 de Repentance+
_DONATION_GREED_INDEX  = 19  # Greed Donation Machine en chunk 2 de Repentance+

# Añadir campos al dataclass ParsedSave (justo después de items_seen):
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
    """Lee los dos contadores de donación del chunk 2 (4 bytes s32 LE por
    entry).

    Los índices están confirmados contra el save fixture de Repentance+
    y un save 100% completado externo (Zamiell/isaac-save-installer). Ver
    docs/superpowers/specs/2026-05-16-greed-donations-design.md sección
    "Datos" para el detalle de la identificación.
    """
    def read_at(idx: int) -> int:
        offset = idx * 4
        if offset + 4 > len(counters_body):
            return 0
        return struct.unpack_from("<i", counters_body, offset)[0]
    return read_at(_DONATION_NORMAL_INDEX), read_at(_DONATION_GREED_INDEX)

# En _extract_chunks (alrededor de L192-198): añadir CHUNK 2 a la lista
# de chunks requeridos, junto a achievements/challenges/collectibles.
# Si ya no está, agregarlo a la tupla `for required, label in (...)`:
#   (_CHUNK_COUNTERS, "contadores"),

# En parse_save (alrededor de L142): obtener counters y extraer contadores.
# Justo después de la línea `collectibles = chunks[_CHUNK_COLLECTIBLES]`:
counters = chunks[_CHUNK_COUNTERS]
donation_count, greed_donation_count = _extract_donation_counters(counters)

# Y al construir ParsedSave (alrededor de L148-155), añadir los dos campos:
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
Expected: PASS (incluyendo los tests nuevos y los existentes — no romper nada).

- [ ] **Step 5: Commit**

```bash
rtk git add tracker/save_parser.py tests/test_save_parser.py
rtk git commit -m "feat(parser): extraer contadores de máquinas de donación (chunk 2)"
```

---

## Task 3: Propagar contadores y aplicar fuente híbrida en state_mapper

**Files:**
- Modify: `tracker/state_mapper.py`
- Modify: `tests/test_state_mapper.py`

- [ ] **Step 1: Escribir test fallido**

```python
# Añadir a tests/test_state_mapper.py
def test_donations_state_exposes_counters_and_milestones():
    """El estado del frontend expone contadores e hitos con flag unlocked."""
    from tracker.save_parser import ParsedSave
    from tracker.state_mapper import build_localstorage_state

    parsed = ParsedSave(
        slot=1,
        donation_count=500,
        greed_donation_count=50,
        achievements_unlocked=set(),
    )
    state = build_localstorage_state(parsed)
    donations = state["donations_state"]
    assert donations["normal"]["count"] == 500
    assert donations["greed"]["count"] == 50

    by_amount_normal = {m["amount"]: m for m in donations["normal"]["milestones"]}
    # Counter normal=500: hitos hasta 400 desbloqueados, 600+ no.
    assert by_amount_normal[400]["unlocked"] is True
    assert by_amount_normal[600]["unlocked"] is False


def test_donations_state_uses_achievement_as_fallback_source_of_truth():
    """Si el counter es 0 pero el achievement está set, el hito aparece
    desbloqueado. Cubre el caso de saves upgraded desde Afterbirth+."""
    from tracker.save_parser import ParsedSave
    from tracker.state_mapper import build_localstorage_state

    parsed = ParsedSave(
        slot=1,
        donation_count=0,
        greed_donation_count=0,
        # ach 250 = Lost holds Holy Mantle, 879 Greed.
        # ach 138 = Stop Watch, 999 normal.
        achievements_unlocked={250, 138},
    )
    state = build_localstorage_state(parsed)
    by_g = {m["amount"]: m for m in state["donations_state"]["greed"]["milestones"]}
    by_n = {m["amount"]: m for m in state["donations_state"]["normal"]["milestones"]}
    # Solo los achievements 250 y 138 están set; los demás hitos quedan locked
    # (counter=0 y ach byte=0).
    assert by_g[879]["unlocked"] is True
    assert by_g[666]["unlocked"] is False
    assert by_n[999]["unlocked"] is True
    assert by_n[900]["unlocked"] is False


def test_donations_visible_count_bumps_to_biggest_unlocked():
    """Si el counter raw es 0 pero el ach del hito 879 está set, el counter
    visible debe ser ≥879 para que la barra de progreso sea coherente con
    los hitos verdes."""
    from tracker.save_parser import ParsedSave
    from tracker.state_mapper import build_localstorage_state

    parsed = ParsedSave(
        slot=1,
        donation_count=0,
        greed_donation_count=0,
        achievements_unlocked={250},  # 879 Greed
    )
    state = build_localstorage_state(parsed)
    assert state["donations_state"]["greed"]["count"] == 879
    # Normal no tiene ningún ach set ni counter — visible debe ser 0.
    assert state["donations_state"]["normal"]["count"] == 0


def test_donations_visible_count_uses_max_of_raw_and_unlocked():
    """Si el counter raw está más alto que el ach más alto unlocked, el
    visible es el counter raw."""
    from tracker.save_parser import ParsedSave
    from tracker.state_mapper import build_localstorage_state

    parsed = ParsedSave(
        slot=1,
        donation_count=750,
        greed_donation_count=0,
        achievements_unlocked={134},  # 10 normal — el counter raw es más alto.
    )
    state = build_localstorage_state(parsed)
    assert state["donations_state"]["normal"]["count"] == 750
```

- [ ] **Step 2: Verificar que fallan**

Run: `pytest tests/test_state_mapper.py -v`
Expected: FAIL con `KeyError: 'donations_state'`.

- [ ] **Step 3: Implementar**

Editar `tracker/state_mapper.py`:

```python
# Añadir import en cabecera:
from tracker.data.donations import DONATION_MILESTONES, GREED_DONATION_MILESTONES

# Añadir builder:
def _build_donations_state(parsed: ParsedSave) -> dict:
    def section(raw_count: int, milestones: list[dict]) -> dict:
        enriched = [
            {
                **m,
                "unlocked": raw_count >= m["amount"]
                            or m["achievement_id"] in parsed.achievements_unlocked,
            }
            for m in milestones
        ]
        # Counter visible = max(raw, mayor amount entre hitos unlocked).
        # Esto hace que la barra y el contador sean coherentes con los
        # hitos en verde para saves migrados desde Afterbirth+ (raw=0
        # pero achievements unlocked).
        biggest_unlocked = max(
            (m["amount"] for m in enriched if m["unlocked"]),
            default=0,
        )
        visible_count = max(raw_count, biggest_unlocked)
        return {"count": visible_count, "milestones": enriched}

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
Expected: PASS (tests nuevos y existentes).

- [ ] **Step 5: Commit**

```bash
rtk git add tracker/state_mapper.py tests/test_state_mapper.py
rtk git commit -m "feat(state): exponer donations_state con fuente híbrida counter/achievement"
```

---

## Task 4: HTML de la pestaña Donaciones

**Files:**
- Modify: `challenges.html` (raíz; el mirror se sincroniza en Task 7)

- [ ] **Step 1: Añadir el botón en la barra de tabs**

Localizar L1832-1838 (barra de tabs). Añadir botón al final:

```html
    <button class="tab" data-view="donations">Donaciones</button>
```

- [ ] **Step 2: Añadir el contenedor de la vista**

Localizar el cierre del último `<div class="view" id="view-cards">` (search `view-cards` para situarte). Después de ese cierre `</div>` y antes del cierre del bloque general de vistas, añadir:

```html
  <div class="view" id="view-donations">
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

    <section class="donation-section" id="donation-normal">
      <header class="donation-header">
        <div class="donation-icon" data-machine="normal"></div>
        <div class="donation-title">Máquina de donación</div>
        <div class="donation-counter"><span id="donationNormalCount">0</span> / 999</div>
        <div class="donation-progress-container">
          <div class="donation-progress" id="donationNormalBar"></div>
        </div>
        <div class="donation-summary" id="donationNormalSummary"></div>
      </header>
      <ul class="donation-milestones" id="donationNormalMilestones"></ul>
    </section>
  </div>
```

- [ ] **Step 3: Verificación manual**

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

Localizar `function switchTab(view)` (L5778). Justo encima añadir:

```javascript
// ===== Donaciones =====
function renderDonations(state) {
  if (!state || !state.donations_state) return;
  renderDonationSection('normal', state.donations_state.normal, 999);
  renderDonationSection('greed',  state.donations_state.greed,  999);
}

function renderDonationSection(key, section, max) {
  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
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
    summaryEl.textContent = `Has desbloqueado ${unlocked} de ${milestones.length} ítems`;
  }

  listEl.innerHTML = '';
  for (const m of milestones) {
    const li = document.createElement('li');
    li.className = 'donation-milestone ' + (m.unlocked ? 'unlocked' : 'locked');
    const remaining = Math.max(0, m.amount - count);
    const statusText = m.unlocked ? '✓ Desbloqueado' : `Faltan ${remaining}`;
    li.innerHTML = `
      <div class="ms-icon"></div>
      <div class="ms-name">${escapeHtmlDon(m.name)}</div>
      <div class="ms-amount">${m.amount}</div>
      <div class="ms-status">${statusText}</div>
    `;
    listEl.appendChild(li);
  }
}

function escapeHtmlDon(s) {
  return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}
```

- [ ] **Step 2: Conectar al ciclo de actualización de estado**

Localizar `window.applyIsaacState` (search ese identificador en el archivo). Identificar dónde se aplican los demás estados (items, cards, characters). Justo después de la última de esas llamadas añadir:

```javascript
renderDonations(state);
```

Si no hay un único `applyIsaacState` definido, conectar también en el bootstrap inicial que carga el estado tras `pywebviewready` (search `get_initial_state` o `_state` para localizar).

- [ ] **Step 3: Verificación manual**

```powershell
rtk python -m tracker.app
```

Abrir Donaciones — deberías ver:
- Contador `999 / 999` arriba en ambas secciones (porque el visible_count bumpea al cap cuando todos los hitos están unlocked, aunque el counter raw del save sea 0).
- Todos los hitos en verde "✓ Desbloqueado" (por fuente híbrida — los achievements están set).
- Barra de progreso llena, summary "Máquina llena".

Si el contador raw fuera >0 y solo algunos hitos están unlocked, la barra refleja el max(raw, biggest unlocked) y los hitos pendientes muestran "Faltan X".

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

Verificar que `dist/IsaacTracker.exe` se crea correctamente y abrir el ejecutable.

- [ ] **Step 3: Verificación manual en el .exe**

- La pestaña "Donaciones" aparece como séptima en la barra.
- Ambas secciones rellenan con los contadores reales del save.
- Cambiar de pestaña y volver mantiene el render.
- Las pestañas existentes (Desafíos, Personajes, etc.) siguen funcionando.

- [ ] **Step 4: Commit**

```bash
rtk git add tracker/assets/challenges.html
rtk git commit -m "build: sincronizar mirror HTML y rebuildear IsaacTracker.exe"
```

---

## Task 8: Verificación final

- [ ] **Step 1: Ejecutar suite completa**

```bash
rtk pytest -q
```

Expected: todos PASS.

- [ ] **Step 2: Smoke test manual del flujo completo**

Abrir `dist/IsaacTracker.exe`:

1. La app levanta sin error.
2. Pestañas existentes siguen funcionando (Desafíos, Personajes, Logros, Ítems, Trinkets, Cartas).
3. Donaciones muestra las dos secciones con datos coherentes:
   - Greed: contador real, hitos según fuente híbrida.
   - Normal: contador real, hitos según fuente híbrida.

- [ ] **Step 3: Sin más commits si todo OK.**

Si algo falla, parar y reportar el problema al humano en lugar de seguir.

---

## Self-Review (autoejecutado al terminar de escribir el plan)

**Spec coverage:**

- ✅ Pestaña nueva "Donaciones" en barra (Task 4).
- ✅ Sección Greed primero, normal después (Task 4 — orden confirmado en spec).
- ✅ Cabecera: icono + contador + barra + resumen (Task 5, 6).
- ✅ Lista con icono + nombre + cantidad + estado (Task 5, 6).
- ✅ Estados especiales (0, max) — Task 6.
- ✅ Datos del chunk 2 con índices identificados [8] y [19] — Task 2.
- ✅ Fuente híbrida (counter OR achievement) — Task 3.
- ✅ Lista de hitos completa — Task 1.
- ✅ Tests parser, state mapper, donations data — Tasks 1, 2, 3.

**Placeholder scan:**

- No quedan `<FILL>` ni TBD.

**Type consistency:**

- `ParsedSave.donation_count` / `greed_donation_count` consistentes entre Tasks 2 y 3.
- `donations_state.normal` / `donations_state.greed` consistentes entre Task 3 y 6.
- `milestone.amount` / `unlocked` / `name` / `achievement_id` consistentes entre Tasks 1, 3 y 6.
- `_DONATION_NORMAL_INDEX = 8`, `_DONATION_GREED_INDEX = 19` — coherente con spec.

**Notas adicionales:**

- Tooltips ricos sobre los iconos (estilo pestaña Ítems) quedan fuera de esta primera versión. Si se piden tras la implementación, añadir como follow-up.
- El cap visual de ambas máquinas es 999 en el spec. Si la realidad del juego es 1000 para Greed, la barra solo subirá hasta el 99.9% en el caso edge — aceptable.
