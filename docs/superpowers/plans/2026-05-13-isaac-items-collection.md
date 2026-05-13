# Isaac Items Collection — Implementation Plan

> **For agentic workers:** REQUIRED: Use `superpowers:subagent-driven-development` (if subagents available) or `superpowers:executing-plans` to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an "Ítems" tab to IsaacTracker showing a grid of all ~700 collectible items with sprite + name + description tooltip; toggled color/grayscale based on whether the player has touched the item, sourced from the save's COLLECTIBLES chunk.

**Architecture:**
- Extend `tracker/save_parser.py` to read chunk 4 (COLLECTIBLES, 733 u1 bytes — one per item ID, value=1 means seen at least once).
- Build-time: `tools/build_collectibles.py` extracts `items.xml` and `gfx/items/collectibles/*.png` from the user's Isaac install (Steam default path or `ISAAC_PATH` env), writes `tracker/data/collectibles.py` (table) and copies sprites to `tracker/assets/item_icons/`.
- `tracker/state_mapper.py` exposes `items_state: {str(id): bool}` for non-removed items.
- `challenges.html` adds a new tab + view with adaptive grid + tooltip reusing existing `ITEM_INFO`.
- Removed items (placeholders) are excluded from the grid and the X/Y denominator.

**Tech Stack:** Python (parser, build script), HTML/CSS/JS (UI), pytest (tests), Nuitka/PyInstaller (bundle).

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `tools/build_collectibles.py` | Create | One-shot script: extract items.xml + sprites from Isaac install, generate `tracker/data/collectibles.py`, copy PNGs |
| `tracker/data/collectibles.py` | Create (generated) | Frozen table: `COLLECTIBLES: dict[int, dict]` with `{id, name, sprite, removed}` |
| `tracker/save_parser.py` | Modify | Add `items_seen: set[int]` to `ParsedSave`, parse chunk 4 |
| `tracker/state_mapper.py` | Modify | Add `items_state` to localstorage state |
| `tests/test_save_parser.py` | Modify | Test `items_seen` extraction from fixture |
| `tests/test_state_mapper.py` | Modify | Test `items_state` (empty + populated) |
| `challenges.html` | Modify | Add tab "Ítems", view-items, grid CSS, render JS, tooltip integration |
| `tracker/assets/item_icons/` | Create | Bundle directory for ~700 sprites |
| `tracker/data/items_inline.js` | Create (generated) | Inline JS table with item metadata (analog of `achievements_inline.js`) |
| `tools/build_items_inline.py` | Create | Generates `items_inline.js` from `collectibles.py` |
| `build.spec` | Modify | Include `tracker/assets/item_icons/` in PyInstaller bundle |
| `build_nuitka.py` | Modify | Idem for Nuitka build |

---

### Task 1: Build script — extract items.xml + sprites from Isaac install

**Files:**
- Create: `tools/build_collectibles.py`
- Create (output): `tracker/data/collectibles.py`
- Create (output): `tracker/assets/item_icons/collectible_NNN.png` (~733 files, ~5–10 MB total)

- [ ] **Step 1: Detect Isaac install path**

```python
# tools/build_collectibles.py
import os, sys, shutil, xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_STEAM_PATHS = [
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\The Binding of Isaac Rebirth"),
    Path(r"C:\Program Files\Steam\steamapps\common\The Binding of Isaac Rebirth"),
]

def find_isaac_root() -> Path:
    env = os.environ.get("ISAAC_PATH")
    if env and Path(env).is_dir():
        return Path(env)
    for p in DEFAULT_STEAM_PATHS:
        if (p / "resources" / "items.xml").exists():
            return p
    raise SystemExit(
        "Isaac not found. Set ISAAC_PATH env var to Isaac install root."
    )
```

- [ ] **Step 2: Parse items.xml and extract metadata**

```python
def parse_items_xml(items_xml: Path) -> list[dict]:
    """Return [{id, name, gfx, removed}] for every <item> entry."""
    root = ET.parse(items_xml).getroot()
    out = []
    for elem in root.findall("item"):
        if elem.get("id") is None:
            continue
        item_id = int(elem.get("id"))
        name = elem.get("name", f"Item {item_id}")
        gfx = elem.get("gfx", "")
        # "removed" if name starts with "REMOVED" or attribute removed="1"
        removed = (
            name.upper().startswith("REMOVED")
            or elem.get("removed") == "1"
            or not gfx
        )
        out.append({"id": item_id, "name": name, "gfx": gfx, "removed": removed})
    return out
```

- [ ] **Step 3: Copy sprites to assets/item_icons/**

```python
def copy_sprites(items: list[dict], isaac_root: Path, dest: Path) -> int:
    dest.mkdir(parents=True, exist_ok=True)
    src_root = isaac_root / "resources" / "gfx" / "items" / "collectibles"
    copied = 0
    for it in items:
        if it["removed"] or not it["gfx"]:
            continue
        src = src_root / it["gfx"]
        if not src.exists():
            print(f"[warn] sprite missing for id={it['id']}: {src.name}")
            continue
        dst = dest / f"collectible_{it['id']:03d}.png"
        shutil.copy2(src, dst)
        copied += 1
    return copied
```

- [ ] **Step 4: Generate `tracker/data/collectibles.py`**

```python
def write_collectibles_py(items: list[dict], path: Path) -> None:
    lines = [
        '"""Auto-generated by tools/build_collectibles.py. Do not edit by hand."""',
        "from __future__ import annotations",
        "",
        "COLLECTIBLES: dict[int, dict] = {",
    ]
    for it in items:
        sprite = f"collectible_{it['id']:03d}.png" if not it["removed"] else ""
        lines.append(
            f"    {it['id']}: {{'name': {it['name']!r}, "
            f"'sprite': {sprite!r}, 'removed': {it['removed']}}},"
        )
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
```

- [ ] **Step 5: Wire `main()` and run**

```python
def main() -> int:
    root = find_isaac_root()
    items_xml = root / "resources" / "items.xml"
    items = parse_items_xml(items_xml)
    project_root = Path(__file__).resolve().parents[1]
    icons_dir = project_root / "tracker" / "assets" / "item_icons"
    out_py = project_root / "tracker" / "data" / "collectibles.py"
    n = copy_sprites(items, root, icons_dir)
    write_collectibles_py(items, out_py)
    print(f"[build_collectibles] {len(items)} items, {n} sprites copied -> {icons_dir}")
    print(f"[build_collectibles] table -> {out_py}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run: `python tools/build_collectibles.py`
Expected: prints `~733 items, ~720 sprites copied`. `tracker/data/collectibles.py` exists. `tracker/assets/item_icons/collectible_*.png` populated.

- [ ] **Step 6: Commit**

```powershell
git add tools/build_collectibles.py tracker/data/collectibles.py tracker/assets/item_icons/
git commit -m "feat(items): build script extracts items.xml + sprites from Isaac install"
```

---

### Task 2: Extend save_parser for COLLECTIBLES chunk (TDD)

**Files:**
- Modify: `tracker/save_parser.py`
- Modify: `tests/test_save_parser.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_save_parser.py — append
def test_parser_extracts_items_seen(sample_save_path):
    parsed = parse_save(sample_save_path)
    assert isinstance(parsed.items_seen, set)
    # Fixture is a real save with many items touched
    assert len(parsed.items_seen) > 50, "expected >50 items seen in fixture"
    # Item ID 1 = The Sad Onion, basic shop item — likely seen in any non-empty save
    assert 1 in parsed.items_seen or 2 in parsed.items_seen
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_save_parser.py::test_parser_extracts_items_seen -v`
Expected: FAIL — `items_seen` attribute missing.

- [ ] **Step 3: Add `items_seen` field to ParsedSave**

```python
# tracker/save_parser.py — in @dataclass(frozen=True) class ParsedSave
items_seen: set[int] = field(default_factory=set)
```

Update class docstring to mention `items_seen`.

- [ ] **Step 4: Capture COLLECTIBLES chunk during walk**

```python
# tracker/save_parser.py — top-level constant
_CHUNK_COLLECTIBLES = 4
```

In `_extract_chunks()`, capture chunk 4 body alongside achievements/challenges:

```python
collectibles: bytes | None = None
# ... inside the loop:
elif chunk_type == _CHUNK_COLLECTIBLES:
    collectibles = body
# ... at end:
if collectibles is None:
    raise SaveParseError("No collectibles chunk found in save", path=str(path))
return achievements, challenges, collectibles
```

Update return type annotation and the unpacking call site in `parse_save()`.

- [ ] **Step 5: Add extraction function and wire it**

```python
def _extract_items_seen(collectibles_body: bytes) -> set[int]:
    """Return set of collectible IDs (byte indices) where byte == 1."""
    return {i for i, b in enumerate(collectibles_body) if b == 1}
```

In `parse_save()`:

```python
items_seen = _extract_items_seen(collectibles)
return ParsedSave(
    slot=slot,
    challenges_complete=challenges_complete,
    characters_unlocked=characters_unlocked,
    character_marks=character_marks,
    achievements_unlocked=achievements_unlocked,
    items_seen=items_seen,
)
```

- [ ] **Step 6: Run test**

Run: `python -m pytest tests/test_save_parser.py -v`
Expected: PASS for new test, no regressions.

- [ ] **Step 7: Commit**

```powershell
git add tracker/save_parser.py tests/test_save_parser.py
git commit -m "feat(parser): extract items_seen from COLLECTIBLES chunk"
```

---

### Task 3: Extend state_mapper for items_state (TDD)

**Files:**
- Modify: `tracker/state_mapper.py`
- Modify: `tests/test_state_mapper.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_state_mapper.py — append
def test_empty_save_produces_all_false_items():
    state = build_localstorage_state(_empty_parsed())
    items = state["items_state"]
    assert all(v is False for v in items.values())
    # All keys must be string ids of NON-removed items
    assert len(items) > 500  # ~720 expected after removing placeholders

def test_seen_items_marked_true():
    p = ParsedSave(
        slot=1,
        challenges_complete=set(),
        characters_unlocked=set(),
        character_marks={},
        achievements_unlocked=set(),
        items_seen={1, 33, 105},
        parsed_at=datetime(2026, 5, 13, tzinfo=timezone.utc),
    )
    state = build_localstorage_state(p)
    assert state["items_state"]["1"] is True
    assert state["items_state"]["33"] is True
    assert state["items_state"]["105"] is True
    assert state["items_state"]["2"] is False
```

Update `_empty_parsed()` to include `items_seen=set(), achievements_unlocked=set()`.

- [ ] **Step 2: Run tests to verify failure**

Run: `python -m pytest tests/test_state_mapper.py -v`
Expected: FAIL — `items_state` missing.

- [ ] **Step 3: Implement `_build_items_state`**

```python
# tracker/state_mapper.py — top
from tracker.data.collectibles import COLLECTIBLES

def _build_items_state(parsed: ParsedSave) -> dict[str, bool]:
    return {
        str(item_id): item_id in parsed.items_seen
        for item_id, meta in COLLECTIBLES.items()
        if not meta["removed"]
    }
```

In `build_localstorage_state()`:

```python
return {
    "challenges_state": _build_challenges(parsed),
    "characters_state": _build_characters(parsed),
    "achievements_unlocked": sorted(parsed.achievements_unlocked),
    "items_state": _build_items_state(parsed),
    "meta": {...},
}
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_state_mapper.py -v`
Expected: PASS, no regressions.

- [ ] **Step 5: Commit**

```powershell
git add tracker/state_mapper.py tests/test_state_mapper.py
git commit -m "feat(state): expose items_state from COLLECTIBLES table"
```

---

### Task 4: Add HTML "Ítems" tab + view + grid + render JS

**Files:**
- Modify: `challenges.html` (lines ~1361 tabs, ~1391 views, plus CSS + JS sections)

- [ ] **Step 1: Add tab button and view container**

In the `<div class="tabs">` block (around line 1361):

```html
<button class="tab" data-view="items">Ítems</button>
```

After `view-achievements` block (around line 1405), add:

```html
<div class="view" id="view-items">
  <div class="progress-bar-container">
    <div class="progress-bar" id="itemsProgressBar"></div>
  </div>
  <div class="progress-label" id="itemsProgressLabel">Ítems: 0 / 0</div>
  <div id="items-grid"></div>
</div>
```

- [ ] **Step 2: Add CSS for items grid**

In the `<style>` section (mirror `#view-achievements` grid CSS):

```css
#view-items {
  /* full width like Logros */
}
#view-items #items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(48px, 1fr));
  gap: 6px;
  padding: 8px 0;
}
#view-items .item-cell {
  position: relative;
  aspect-ratio: 1 / 1;
  background: #16213e;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.1s;
}
#view-items .item-cell:hover { transform: scale(1.08); z-index: 2; }
#view-items .item-cell img {
  width: 100%; height: 100%;
  object-fit: contain;
  image-rendering: pixelated;
  filter: grayscale(1) brightness(0.4);
  transition: filter 0.2s;
}
#view-items .item-cell.seen img {
  filter: none;
}
#view-items .progress-bar { background: #f39c12; }
```

- [ ] **Step 3: Add JS render functions**

In the `<script>` section (after the achievements renderer):

```js
// ITEMS_DATA is loaded from items_inline.js (Task 7) as a global:
// window.ITEMS_DATA = [{id:1, name:"The Sad Onion", sprite:"collectible_001.png"}, ...]
function renderItemsGrid() {
  const grid = document.getElementById('items-grid');
  if (!grid || !window.ITEMS_DATA) return;
  const seen = window._itemsState || {};
  grid.innerHTML = '';
  for (const it of window.ITEMS_DATA) {
    const cell = document.createElement('div');
    cell.className = 'item-cell' + (seen[String(it.id)] ? ' seen' : '');
    cell.dataset.itemId = it.id;
    cell.dataset.itemName = it.name;
    cell.innerHTML = `<img src="item_icons/${it.sprite}" alt="${escapeHtml(it.name)}">`;
    grid.appendChild(cell);
  }
  updateItemsProgress();
}

function updateItemsProgress() {
  const seen = window._itemsState || {};
  const total = window.ITEMS_DATA ? window.ITEMS_DATA.length : 0;
  const done = Object.values(seen).filter(Boolean).length;
  const pct = total ? Math.round((done / total) * 100) : 0;
  const bar = document.getElementById('itemsProgressBar');
  const lbl = document.getElementById('itemsProgressLabel');
  if (bar) bar.style.width = pct + '%';
  if (lbl) lbl.textContent = `Ítems: ${done} / ${total}  (${pct}%)`;
}
```

- [ ] **Step 4: Open challenges.html in browser, click "Ítems" tab**

Expected: empty grid (Task 7 wires data); tab switches; no JS errors in console.

- [ ] **Step 5: Commit**

```powershell
git add challenges.html
git commit -m "feat(ui): add Items tab skeleton + grid CSS + render functions"
```

---

### Task 5: Item tooltip (rich, reusing ITEM_INFO)

**Files:**
- Modify: `challenges.html`

- [ ] **Step 1: Add tooltip handler**

In the JS section, attach to `#items-grid`:

```js
function showItemTooltip(cell) {
  const name = cell.dataset.itemName;
  const info = (typeof ITEM_INFO !== 'undefined' && ITEM_INFO[name]) || {};
  const type = info.type || '';
  const desc = info.description || 'Sin descripción aún.';
  const html = `
    <div class="tt-card-header tier-c">
      <div class="tt-head-row">
        <div class="tt-head-text">
          <span class="tt-title">${escapeHtml(name)}</span>
          <div class="tt-meta">${escapeHtml(type)}</div>
        </div>
      </div>
    </div>
    <div class="tt-body">
      <div class="tt-block effect">
        <div class="tt-block-label">💫 Efecto</div>
        <div class="tt-block-body">${escapeHtml(desc)}</div>
      </div>
    </div>`;
  const tt = document.getElementById('tooltip');
  tt.innerHTML = html;
  tt.classList.add('visible');
  positionTooltip(cell);
}

document.getElementById('items-grid').addEventListener('mouseover', e => {
  const cell = e.target.closest('.item-cell');
  if (cell) showItemTooltip(cell);
});
document.getElementById('items-grid').addEventListener('mouseout', e => {
  if (e.target.closest('.item-cell')) hideTooltip();
});
```

- [ ] **Step 2: Manual check**

Open in browser, hover an item cell. Tooltip appears with name + (description or "Sin descripción aún").

- [ ] **Step 3: Commit**

```powershell
git add challenges.html
git commit -m "feat(ui): rich tooltip for items reusing ITEM_INFO"
```

---

### Task 6: Wire items_state into applyIsaacState

**Files:**
- Modify: `challenges.html`

- [ ] **Step 1: Find `window.applyIsaacState`**

Search for existing handler (the function pywebview calls with the Python state dict).

- [ ] **Step 2: Persist items_state to localStorage and re-render**

```js
// inside applyIsaacState(state):
if (state && state.items_state) {
  window._itemsState = state.items_state;
  // (optional: localStorage.setItem('items_state', JSON.stringify(state.items_state));)
  renderItemsGrid();
}
```

Also call `renderItemsGrid()` once on initial pywebview load.

- [ ] **Step 3: Run app from source to verify live update**

Run: `python -m tracker.app`
Expected: Ítems tab shows real seen/unseen state from your save. Modify save (or play a run) → grid updates without restart.

- [ ] **Step 4: Commit**

```powershell
git add challenges.html
git commit -m "feat(ui): apply items_state on push and initial load"
```

---

### Task 7: Generate items_inline.js + update build

**Files:**
- Create: `tools/build_items_inline.py`
- Create (output): `tracker/data/items_inline.js`
- Modify: `challenges.html` (add `<script src="items_inline.js"></script>` ref or inline)
- Modify: `build.spec`
- Modify: `build_nuitka.py`

- [ ] **Step 1: Create items_inline.js generator**

```python
# tools/build_items_inline.py
from pathlib import Path
import json
from tracker.data.collectibles import COLLECTIBLES

def main() -> int:
    items = [
        {"id": k, "name": v["name"], "sprite": v["sprite"]}
        for k, v in sorted(COLLECTIBLES.items())
        if not v["removed"]
    ]
    out = Path(__file__).resolve().parents[1] / "tracker" / "data" / "items_inline.js"
    out.write_text(
        f"window.ITEMS_DATA = {json.dumps(items, ensure_ascii=False)};\n",
        encoding="utf-8",
    )
    print(f"[build_items_inline] wrote {len(items)} items -> {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

Run: `python tools/build_items_inline.py`

- [ ] **Step 2: Reference items_inline.js in challenges.html**

Mirror the pattern of `achievements_inline.js`. Either inline-paste the contents at build time (preferred — matches existing pattern) via an injection step in `build.spec` / `build_nuitka.py`, or reference as `<script src="items_inline.js"></script>` and bundle the file.

Decision: inline-paste, matching `achievements_inline.js` handling. If the existing pattern uses a `_build_inline.py` script, extend it; if it copies a file, add `items_inline.js` to the copy list.

- [ ] **Step 3: Update build.spec to bundle item_icons**

In `build.spec` `datas=[...]` add:

```python
('tracker/assets/item_icons', 'assets/item_icons'),
```

- [ ] **Step 4: Update build_nuitka.py**

Nuitka already uses `--include-data-dir={ASSETS.as_posix()}=assets` which recursively includes all of `tracker/assets/`, so adding `item_icons/` under that path is enough — no flag change needed. Verify by listing dist contents after build.

- [ ] **Step 5: Commit**

```powershell
git add tools/build_items_inline.py tracker/data/items_inline.js challenges.html build.spec build_nuitka.py
git commit -m "build(items): inline items table + bundle item_icons in exe"
```

---

### Task 8: Rebuild .exe + smoke test

**Files:** none (verification only)

- [ ] **Step 1: Rebuild**

Run: `python build_nuitka.py`
Expected: builds without errors; `dist/IsaacTracker.exe` updated; size grew by ~5–10 MB.

- [ ] **Step 2: Launch and verify**

Run: `dist\IsaacTracker.exe`
Verify:
- Ítems tab appears between Logros and the others.
- Counter `Ítems: X / ~720` is plausible vs. how complete your collection is.
- Sprites render (not all gray boxes).
- Items you know you've touched are in color; items you've never seen are gray/dim.
- Hover any item → tooltip appears with name + description (or "Sin descripción aún" for ~540 items).
- Other tabs (Desafíos, Personajes, Logros) still work — no regressions.

- [ ] **Step 3: If all green, commit any final fixes**

```powershell
git add -A
git commit -m "chore: post-rebuild fixes for items tab" # only if needed
```

If any check fails, debug per `superpowers:systematic-debugging` — do NOT mark complete.

---

## Notes for the implementer

- **DRY:** mirror existing patterns (achievements rendering, tooltip system, build scripts) — don't invent new structures.
- **YAGNI:** no filters, no search, no grouping. Plain grid + tooltip. (User explicitly chose this.)
- **TDD:** tasks 2 and 3 are TDD; the UI tasks are manual-verify because they're DOM/visual.
- **Frequent commits:** one per task minimum, or per logical step inside a task.
- **Removed items:** never appear in the grid or in `items_state` — keeps the X/Y honest.
- **Sprites missing locally:** if `tools/build_collectibles.py` warns about missing sprites, those items render with a broken-image placeholder; acceptable for now.
- **Re-running build_collectibles.py:** safe and idempotent. Run it whenever Isaac is patched and adds/removes items.
