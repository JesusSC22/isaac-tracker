"""Descarga el arbol de sprites de bestiario de Derugon/TBoIR-resources.

Uso: `python tools/extract_bestiary_assets.py [--tag TAG]`

Default tag: 1.9.7.15.J374 (Repentance+ latest known at 2026-05-17).
Output: `tools/_bestiary_raw/` con la estructura espejo de:
    resources/gfx/bosses/...
    resources/gfx/monsters/...
    resources-dlc3/gfx/bosses/...
    resources-dlc3/gfx/monsters/...
+ MANIFEST.json. Carpeta gitignored.

Extrae tanto los sprites del juego base (`resources/gfx/...`) como los de
Repentance (`resources-dlc3/gfx/...`); ambos árboles contienen bosses
canónicos (Mom, Isaac, Satan, Lamb, Hush, Delirium, Mother, Beast, etc.) y
mobs regulares — sin el árbol base el tab de bestiario no muestra kills de
los bosses principales.

El MANIFEST.json tiene la forma:
    {
        "entries": [ {type, variant, name_en_slug, suffix, folder, filename, scheme}, ... ],
        "bare_name_pngs": [ {folder, filename}, ... ]
    }

`entries` contiene los PNGs cuyo nombre matchea alguno de los esquemas
soportados (Repentance `NNN.NNN_name.png`, classic `boss_NNN_name.png`,
classic `monster_NNN_name.png`). `bare_name_pngs` contiene los PNGs que
no tienen prefijo numérico (p.ej. `beast.png`, `thelamb.png`,
`mothers_shadow.png`); el siguiente paso de la pipeline (B2) los mapeará
a (type, variant) con una pequeña tabla slug→id.

`folder` registra la ruta completa relativa a la raíz del repo
(p.ej. `resources/gfx/bosses/classic` o `resources-dlc3/gfx/monsters/repentance`),
para que B2 pueda desambiguar de qué DLC procede cada sprite.

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
    "resources/gfx/bosses",
    "resources/gfx/monsters",
    "resources-dlc3/gfx/bosses",
    "resources-dlc3/gfx/monsters",
]
OUT = Path(__file__).parent / "_bestiary_raw"

# Filenames live in several historical schemes; try each in order, first match wins.
FILENAME_SCHEMES = [
    # Repentance scheme: 010.010_name.png or 010.010_name_suffix.png
    (
        "rep",
        re.compile(
            r"^(?P<type>\d+)\.(?P<variant>\d+)_(?P<name>[a-z0-9_]+?)"
            r"(?:_(?P<suffix>champion|gehenna|ashpit|corpse|gold|blue|red|black|white|green|yellow|grey|gray|downpour|dross|mines|mausoleum))?"
            r"\.png$",
            re.IGNORECASE,
        ),
    ),
    # Classic boss scheme: boss_054_mom.png or boss_054_mom_suffix.png
    (
        "boss",
        re.compile(
            r"^boss_(?P<type>\d+)_(?P<name>[a-z0-9_]+?)"
            r"(?:_(?P<suffix>champion|gehenna|ashpit|corpse|gold|blue|red|black|white|green|yellow|grey|gray|downpour|dross|mines|mausoleum))?"
            r"\.png$",
            re.IGNORECASE,
        ),
    ),
    # Classic monster scheme: monster_010_gaper.png (also with optional suffix)
    (
        "monster",
        re.compile(
            r"^monster_(?P<type>\d+)_(?P<name>[a-z0-9_ ]+?)"
            r"(?:_(?P<suffix>champion|gehenna|ashpit|corpse|gold|blue|red|black|white|green|yellow|grey|gray|downpour|dross|mines|mausoleum))?"
            r"\.png$",
            re.IGNORECASE,
        ),
    ),
]


def _parse_filename(fname: str):
    """Return (type:int, variant:int, name_slug:str, suffix:str, scheme:str) or None."""
    for scheme_name, regex in FILENAME_SCHEMES:
        m = regex.match(fname)
        if not m:
            continue
        gd = m.groupdict()
        variant = int(gd["variant"]) if gd.get("variant") else 0
        return (
            int(gd["type"]),
            variant,
            gd["name"].strip().replace(" ", "_").lower(),
            (gd["suffix"] or "").lower(),
            scheme_name,
        )
    return None


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
    bare_names: list[dict] = []
    written = 0
    skipped_unparseable = 0
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for info in z.infolist():
            if not info.filename.endswith(".png"):
                continue
            # info.filename is `<repo>-<tag>/<sp>/<tail>`; strip the leading repo dir.
            parts = info.filename.split("/", 1)
            if len(parts) < 2:
                continue
            rel = parts[1]  # path relative to repo root
            matched = None
            for sp in SUBPATHS:
                if rel.startswith(sp + "/"):
                    matched = sp
                    break
            if not matched:
                continue
            tail = rel[len(matched) + 1:]  # path inside the SUBPATH
            if "/" in tail:
                inner_dirs, fname = tail.rsplit("/", 1)
                folder = f"{matched}/{inner_dirs}"
            else:
                folder = matched
                fname = tail

            # Mirror the original layout (repo-relative) inside OUT.
            local = OUT / folder / fname
            local.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(local, "wb") as dst:
                dst.write(src.read())
            written += 1

            parsed = _parse_filename(fname)
            if parsed is None:
                skipped_unparseable += 1
                # Bare-name PNG (e.g. `beast.png`, `thelamb.png`): keep a side list
                # so the next pipeline step can map it via a slug→id table.
                print(f"  bare-name PNG: {folder}/{fname}")
                bare_names.append({"folder": folder, "filename": fname})
                continue
            type_id, variant, name_slug, suffix, scheme = parsed
            manifest.append({
                "type":         type_id,
                "variant":      variant,
                "name_en_slug": name_slug,
                "suffix":       suffix,
                "folder":       folder,
                "filename":     fname,
                "scheme":       scheme,
            })

    manifest.sort(key=lambda e: (e["type"], e["variant"], e["suffix"], e["folder"]))
    bare_names.sort(key=lambda e: (e["folder"], e["filename"]))

    manifest_data = {
        "entries":        manifest,
        "bare_name_pngs": bare_names,
    }
    out_path = OUT / "MANIFEST.json"
    out_path.write_text(
        json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    try:
        rel_out = out_path.relative_to(Path.cwd())
    except ValueError:
        rel_out = out_path
    print(f"Wrote {len(manifest)} parseable entries + {len(bare_names)} bare-name PNGs to {rel_out}")
    print(f"  PNGs extracted: {written}")
    print(f"  Skipped (filename unparseable, captured as bare-name): {skipped_unparseable}")
    print(f"  Unique (type, variant) pairs: {len({(e['type'], e['variant']) for e in manifest})}")
    schemes_used = {e["scheme"] for e in manifest}
    print(f"  Schemes used: {sorted(schemes_used)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
