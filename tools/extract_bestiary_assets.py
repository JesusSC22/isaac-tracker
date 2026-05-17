"""Descarga el arbol de sprites de bestiario de Derugon/TBoIR-resources.

Uso: `python tools/extract_bestiary_assets.py [--tag TAG]`

Default tag: 1.9.7.15.J374 (Repentance+ latest known at 2026-05-17).
Output: `tools/_bestiary_raw/` con la estructura:
    monsters/{classic,rebirth,repentance}/...
    bosses/...
+ MANIFEST.json. Carpeta gitignored.

Extrae tanto `resources-dlc3/gfx/monsters/` (mobs regulares) como
`resources-dlc3/gfx/bosses/` (bosses canónicos: Mom, Isaac, Satan, Lamb,
Hush, Delirium, Mother, Beast, etc.) — sin la segunda carpeta el tab de
bestiario no muestra kills de los bosses principales.

El MANIFEST contiene una entrada por PNG con:
    type, variant, name_en_slug, suffix, folder, filename

donde `folder` es la ruta relativa a `gfx/` (p.ej. `monsters/repentance`,
`bosses`). Consumido por `tools/build_bestiary.py` (siguiente paso).

URL scheme: probamos en orden
    1. https://github.com/<REPO>/archive/refs/tags/<TAG>.zip
    2. https://github.com/<REPO>/archive/refs/heads/<TAG>.zip  (fallback rama)
    3. https://codeload.github.com/<REPO>/zip/refs/tags/<TAG>
    4. https://codeload.github.com/<REPO>/zip/refs/heads/<TAG>
    5. https://github.com/<REPO>/archive/<TAG>.zip
"""
from __future__ import annotations
import argparse
import io
import json
import re
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

REPO = "Derugon/TBoIR-resources"
DEFAULT_TAG = "1.9.7.15.J374"
SUBPATHS = [
    "resources-dlc3/gfx/monsters",
    "resources-dlc3/gfx/bosses",
]
OUT = Path(__file__).parent / "_bestiary_raw"

# Filenames look like:
#   010.010_rotten_gaper.png
#   041.012_black_knight_champion.png
#   025.100_dragonfly.png
# Older `classic/` and `rebirth/` folders use other schemes; we parse the
# Repentance scheme strictly and fall back to "unparseable" for the rest
# (the catalog builder will handle those separately if needed).
FILENAME_RE = re.compile(
    r"^(?P<type>\d+)\.(?P<variant>\d+)_(?P<name>[a-z0-9_]+?)"
    r"(?:_(?P<suffix>champion|gehenna|ashpit|corpse|gold|blue|red|black|white|green|yellow|grey|gray))?"
    r"\.png$",
    re.IGNORECASE,
)


def _try_download(urls: list[str]) -> bytes:
    last_err: Exception | None = None
    for url in urls:
        print(f"Downloading {url}")
        try:
            with urllib.request.urlopen(url) as r:
                data = r.read()
            print(f"  Downloaded {len(data):,} bytes")
            return data
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print(f"  failed: {e}")
            last_err = e
    raise RuntimeError(f"All download URLs failed; last error: {last_err}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default=DEFAULT_TAG,
                        help=f"Tag/branch del repo Derugon/TBoIR-resources (default: {DEFAULT_TAG})")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    urls = [
        f"https://github.com/{REPO}/archive/refs/tags/{args.tag}.zip",
        f"https://github.com/{REPO}/archive/refs/heads/{args.tag}.zip",
        f"https://codeload.github.com/{REPO}/zip/refs/tags/{args.tag}",
        f"https://codeload.github.com/{REPO}/zip/refs/heads/{args.tag}",
        f"https://github.com/{REPO}/archive/{args.tag}.zip",
    ]
    zip_bytes = _try_download(urls)

    manifest: list[dict] = []
    written = 0
    skipped_unparseable = 0
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for info in z.infolist():
            if not info.filename.endswith(".png"):
                continue
            matched = None
            for sp in SUBPATHS:
                if sp in info.filename:
                    matched = sp
                    break
            if not matched:
                continue
            # Path inside the zip is `<root>/<matched>/<tail>`.
            tail = info.filename.split(matched + "/", 1)[1]
            sp_root = matched.split("/")[-1]  # 'monsters' or 'bosses'
            if "/" in tail:
                folder_inner, fname = tail.split("/", 1)
                folder = f"{sp_root}/{folder_inner}"
                # nested subdir support
                if "/" in fname:
                    folder = folder + "/" + "/".join(fname.split("/")[:-1])
                    fname = fname.split("/")[-1]
            else:
                folder = sp_root
                fname = tail
            local = OUT / folder / fname
            local.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(local, "wb") as dst:
                dst.write(src.read())
            written += 1
            m = FILENAME_RE.match(fname)
            if not m:
                skipped_unparseable += 1
                continue
            manifest.append({
                "type":          int(m["type"]),
                "variant":       int(m["variant"]),
                "name_en_slug":  m["name"],
                "suffix":        m["suffix"] or "",
                "folder":        folder,
                "filename":      fname,
            })

    manifest.sort(key=lambda e: (e["type"], e["variant"], e["suffix"]))
    out_path = OUT / "MANIFEST.json"
    out_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    try:
        rel = out_path.relative_to(Path.cwd())
    except ValueError:
        rel = out_path
    print(f"Wrote {len(manifest)} entries to {rel}")
    print(f"  PNGs extracted: {written}")
    print(f"  Skipped (filename unparseable): {skipped_unparseable}")
    print(f"  Unique (type, variant) pairs: {len({(e['type'], e['variant']) for e in manifest})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
