"""Probe each of the 8 rows of the 32x32 grid."""
from PIL import Image
from pathlib import Path

SRC = r"C:\Program Files (x86)\Steam\steamapps\common\The Binding of Isaac Rebirth\extracted_resources\resources\gfx\ui\ui_cardspills.png"
OUT = Path(r"C:\Users\jeiko\Downloads\isaac_challenges\tools")

im = Image.open(SRC).convert("RGBA")
W, H = im.size

# 32x32 grid -> 16 cols x 8 rows
CW, CH = 32, 32
COLS, ROWS = W // CW, H // CH
print(f"Grid: {COLS} cols x {ROWS} rows = {COLS*ROWS} cells")

# Per cell: count how many pixels are non-transparent
def cell_content(r, c):
    crop = im.crop((c * CW, r * CH, (c + 1) * CW, (r + 1) * CH))
    px = crop.load()
    visible = sum(1 for y in range(CH) for x in range(CW) if px[x, y][3] > 0)
    return visible

print("\nVisible-pixel count per cell (0 = empty):")
for r in range(ROWS):
    row_counts = [cell_content(r, c) for c in range(COLS)]
    print(f"  row {r}: {row_counts}")

# Save one sample crop per row (col 0)
for r in range(ROWS):
    crop = im.crop((0, r * CH, CW, (r + 1) * CH))
    crop.save(OUT / f"_probe_row{r}_c0.png")

# Save the entire row 0 stitched (sanity)
for r in range(ROWS):
    row_img = im.crop((0, r * CH, W, (r + 1) * CH))
    row_img.save(OUT / f"_probe_row{r}_full.png")
