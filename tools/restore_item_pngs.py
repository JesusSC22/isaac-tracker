"""Revert item_icons WebP optimization: restore PNGs from backup and rewrite
items_inline.js to point to .png again."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "tracker" / "assets" / "item_icons"
BACKUP = ROOT / "tracker" / "assets" / "item_icons_png_backup"
ITEMS_JS = ROOT / "tracker" / "assets" / "items_inline.js"

if not BACKUP.exists():
    raise SystemExit(f"No existe {BACKUP}; no se puede revertir")

# Remove all .webp files we generated
for p in ICONS.glob("*.webp"):
    p.unlink()

# Restore PNG originals
restored = 0
for p in BACKUP.glob("*.png"):
    shutil.copy2(p, ICONS / p.name)
    restored += 1
print(f"Restaurados {restored} PNGs")

# Rewrite items_inline.js — .webp → .png
raw = ITEMS_JS.read_text(encoding="utf-8")
assert raw.startswith("window.ITEMS_DATA = ")
data_text = raw[len("window.ITEMS_DATA = "):].rstrip()
if data_text.endswith(";"):
    data_text = data_text[:-1]
items = json.loads(data_text)
for it in items:
    s = it.get("sprite", "")
    if s.endswith(".webp"):
        it["sprite"] = s[:-5] + ".png"
ITEMS_JS.write_text(
    "window.ITEMS_DATA = "
    + json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    + ";\n",
    encoding="utf-8",
)
print(f"Reescrito {ITEMS_JS}")
