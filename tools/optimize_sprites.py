"""Convierte los PNG de tracker/assets/ach_icons a WebP lossless.

WebP lossless mantiene transparencia y calidad exacta de los pixel-art
de Isaac, pero suele reducir entre 30-50% el tamaño respecto al PNG.

Mantiene los PNG originales como backup en ach_icons_png_backup/ por si
algo falla; al final se pueden borrar a mano cuando confirmemos que todo
se ve bien.
"""
from pathlib import Path
from PIL import Image
import shutil

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "tracker" / "assets" / "ach_icons"
BACKUP = ROOT / "tracker" / "assets" / "ach_icons_png_backup"

# Backup PNG originales si no existe ya
if not BACKUP.exists():
    BACKUP.mkdir(parents=True)
    for p in ICONS.glob("*.png"):
        shutil.copy2(p, BACKUP / p.name)
    print(f"Backup creado en {BACKUP}")
else:
    print(f"Backup ya existe en {BACKUP}, no se sobrescribe")

before_total = 0
after_total = 0
processed = 0

for p in sorted(ICONS.glob("*.png")):
    before = p.stat().st_size
    before_total += before
    img = Image.open(p)
    # Convertir a RGBA para que WebP preserve transparencia
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    webp_path = p.with_suffix(".webp")
    img.save(webp_path, format="WEBP", lossless=True, quality=100, method=6)
    after = webp_path.stat().st_size
    after_total += after
    processed += 1

print(f"Procesados: {processed}")
print(f"PNG total:  {before_total / 1024:.1f} KB")
print(f"WebP total: {after_total / 1024:.1f} KB")
diff = before_total - after_total
print(f"Ahorro:     {diff / 1024:.1f} KB ({diff*100/before_total:.1f}%)")
