"""Convert tracker/assets/item_icons/*.png to .webp lossless.

Saves ~50% per file. Updates items_inline.js to point to the new extension.
PNG originals are moved to a backup folder so the bundled .exe ships only the
.webp files.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "tracker" / "assets" / "item_icons"
BACKUP = ROOT / "tracker" / "assets" / "item_icons_png_backup"
ITEMS_JS = ROOT / "tracker" / "assets" / "items_inline.js"

# Backup originals
if not BACKUP.exists():
    BACKUP.mkdir(parents=True)
    for p in ICONS.glob("*.png"):
        shutil.copy2(p, BACKUP / p.name)
    print(f"Backup en {BACKUP}")

before_total = after_total = processed = 0
for p in sorted(ICONS.glob("*.png")):
    before_total += p.stat().st_size
    img = Image.open(p)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    webp = p.with_suffix(".webp")
    img.save(webp, format="WEBP", lossless=True, quality=100, method=6)
    after_total += webp.stat().st_size
    p.unlink()  # remove PNG so the bundle only carries .webp
    processed += 1

print(f"Procesados: {processed}")
print(f"PNG total:  {before_total/1024:.1f} KB")
print(f"WebP total: {after_total/1024:.1f} KB")
saved = before_total - after_total
print(f"Ahorro:     {saved/1024:.1f} KB ({saved*100/before_total:.1f}%)")

# Rewrite items_inline.js — swap collectible_NNN.png → collectible_NNN.webp.
raw = ITEMS_JS.read_text(encoding="utf-8")
assert raw.startswith("window.ITEMS_DATA = ")
# Parse the JSON payload and re-serialize so we don't risk a brittle regex
# over freeform JS.
data_text = raw[len("window.ITEMS_DATA = "):].rstrip()
if data_text.endswith(";"):
    data_text = data_text[:-1]
items = json.loads(data_text)
for it in items:
    s = it.get("sprite", "")
    if s.endswith(".png"):
        it["sprite"] = s[:-4] + ".webp"
ITEMS_JS.write_text(
    "window.ITEMS_DATA = "
    + json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    + ";\n",
    encoding="utf-8",
)
print(f"Reescrito {ITEMS_JS}")
