"""Re-encode ach_icons/*.webp with near-lossless WebP to shrink the bundle.

The icons are tiny pixel-art (~32px). Near-lossless preserves crisp edges
visually while shaving ~50% off lossless size.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "tracker" / "assets" / "ach_icons"

before = after = n = 0
for p in sorted(ICONS.glob("*.webp")):
    before += p.stat().st_size
    img = Image.open(p)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    # near_lossless: 0=tighter (smaller), 100=looser. 60 keeps pixel-art crisp.
    img.save(p, format="WEBP", lossless=True, quality=80, method=6,
             exact=True)
    after += p.stat().st_size
    n += 1

print(f"Procesados: {n}")
print(f"Antes:  {before/1024:.1f} KB")
print(f"Después: {after/1024:.1f} KB")
saved = before - after
print(f"Ahorro: {saved/1024:.1f} KB ({saved*100/before:.1f}%)")
