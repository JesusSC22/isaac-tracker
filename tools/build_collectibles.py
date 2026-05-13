"""Extract collectibles metadata + sprites from a local Isaac install.

Usage:
    python tools/build_collectibles.py

Discovery:
    1. ISAAC_PATH env var (root of "The Binding of Isaac Rebirth")
    2. Steam default paths

The Isaac install must have been unpacked at least once with
`tools/ResourceExtractor/ResourceExtractor.exe`. The script first looks for
extracted assets under `extracted_resources/resources/`, then falls back to
`resources/` (older / pre-Repentance unpacks).

Outputs:
    tracker/data/collectibles.py    — table  {id: {name, sprite, removed}}
    tracker/assets/item_icons/      — copied PNGs (collectible_NNN.png)
"""
from __future__ import annotations

import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_ROOTS = [
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\The Binding of Isaac Rebirth"),
    Path(r"C:\Program Files\Steam\steamapps\common\The Binding of Isaac Rebirth"),
]


def find_isaac_root() -> Path:
    env = os.environ.get("ISAAC_PATH")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
        sys.exit(f"ISAAC_PATH={env} is not a directory")
    for p in DEFAULT_ROOTS:
        if p.is_dir():
            return p
    sys.exit(
        "Could not locate Isaac install. Set ISAAC_PATH to the install root, e.g.:\n"
        "  $env:ISAAC_PATH = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\The Binding of Isaac Rebirth'"
    )


def find_resources_dir(isaac_root: Path) -> Path:
    """Return the dir that holds items.xml after extraction."""
    candidates = [
        isaac_root / "extracted_resources" / "resources",
        isaac_root / "resources",
    ]
    for c in candidates:
        if (c / "items.xml").exists():
            return c
    sys.exit(
        f"items.xml not found. Run the bundled extractor first:\n"
        f'  & "{isaac_root}\\tools\\ResourceExtractor\\ResourceExtractor.exe"\n'
        f"and re-run this script."
    )


_NAME_KEY_RE = re.compile(r"^#?(.+?)_NAME$")
_FILENAME_RE = re.compile(r"^Collectibles_(\d+)_(.+)\.png$", re.IGNORECASE)

# stringtable.sta is an XML file. Each <key> has up to 8 <string> children, one
# per game language, in this fixed order (confirmed against THE_SAD_ONION_NAME):
_LANG_ORDER = ["en", "jp", "kr", "zh", "ru", "de", "es", "fr"]
_LANG_INDEX = {lang: i for i, lang in enumerate(_LANG_ORDER)}


def humanize_filename(filename: str) -> str:
    """`Collectibles_001_TheSadOnion.png` -> `The Sad Onion`. Fallback only."""
    m = _FILENAME_RE.match(filename)
    if not m:
        return filename
    camel = m.group(2)
    spaced = re.sub(r"(?<=[a-z0-9])([A-Z])", r" \1", camel)
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", spaced)
    return spaced.strip()


def humanize_name_key(name_attr: str) -> str:
    """Fallback when no gfx attr: `#THE_SAD_ONION_NAME` -> `The Sad Onion`."""
    if not name_attr:
        return ""
    key = name_attr.lstrip("#")
    m = _NAME_KEY_RE.match(key)
    base = m.group(1) if m else key
    parts = base.split("_")
    return " ".join(p.capitalize() for p in parts)


def parse_stringtable(stringtable_xml: Path) -> dict[str, dict[str, str]]:
    """Return {key_name: {lang_code: translated_string}}.

    Skips entries without enough <string> children for the language we want.
    """
    root = ET.parse(stringtable_xml).getroot()
    out: dict[str, dict[str, str]] = {}
    for key_elem in root.iter("key"):
        name = key_elem.get("name")
        if not name:
            continue
        strings = [s.text or "" for s in key_elem.findall("string")]
        translations = {}
        for lang, i in _LANG_INDEX.items():
            if i < len(strings) and strings[i]:
                translations[lang] = strings[i]
        out[name] = translations
    return out


_COLLECTIBLE_TAGS = {"passive", "active", "familiar"}


def _strip_key(attr_value: str) -> str:
    """`#THE_SAD_ONION_NAME` -> `THE_SAD_ONION_NAME`."""
    return (attr_value or "").lstrip("#")


def parse_items_xml(items_xml: Path, strings: dict[str, dict[str, str]]) -> list[dict]:
    """Return [{id, name, sprite_file, removed, desc_es}] for every collectible.

    Names come from stringtable.sta's English entry (canonical, with apostrophes).
    desc_es comes from the Spanish entry of the description key.
    Falls back to filename heuristics if a string lookup misses.
    """
    root = ET.parse(items_xml).getroot()
    out: list[dict] = []
    for elem in root:
        if elem.tag not in _COLLECTIBLE_TAGS:
            continue
        id_attr = elem.get("id")
        if id_attr is None:
            continue
        try:
            item_id = int(id_attr)
        except ValueError:
            continue
        gfx = elem.get("gfx") or ""
        name_key = _strip_key(elem.get("name") or "")
        desc_key = _strip_key(elem.get("description") or "")
        hidden = elem.get("hidden") == "true"

        # Canonical name: English from stringtable; fallback to filename humanize.
        name_en = strings.get(name_key, {}).get("en") or humanize_filename(gfx) or humanize_name_key(name_key)
        # Spanish in-game description (the pickup blurb).
        desc_es = strings.get(desc_key, {}).get("es") or ""

        removed = not gfx or name_en.upper().startswith("REMOVED") or hidden
        out.append({
            "id": item_id,
            "name": name_en,
            "gfx_filename": gfx,
            "removed": removed,
            "desc_es": desc_es,
        })
    return out


def fill_id_gaps_as_removed(items: list[dict]) -> list[dict]:
    """The save's COLLECTIBLES chunk is indexed 0..N. Any id that the XML
    skips is a removed/placeholder slot — keep it in the table marked removed
    so downstream consumers can iterate by id without holes."""
    by_id = {it["id"]: it for it in items}
    if not by_id:
        return items
    max_id = max(by_id)
    out = []
    for i in range(0, max_id + 1):
        if i in by_id:
            out.append(by_id[i])
        else:
            out.append({
                "id": i, "name": "", "gfx_filename": "",
                "removed": True, "desc_es": "",
            })
    return out


def copy_sprites(items: list[dict], resources_dir: Path, dest: Path) -> int:
    """Copy each non-removed sprite to dest as collectible_NNN.png."""
    dest.mkdir(parents=True, exist_ok=True)
    src_root = resources_dir / "gfx" / "items" / "collectibles"
    if not src_root.is_dir():
        sys.exit(f"Sprite folder missing: {src_root}")
    copied = 0
    missing = 0
    src_lc = {p.name.lower(): p for p in src_root.iterdir() if p.is_file()}
    for it in items:
        if it["removed"] or not it["gfx_filename"]:
            continue
        src = src_lc.get(it["gfx_filename"].lower())
        if src is None:
            print(f"[warn] sprite missing for id={it['id']}: {it['gfx_filename']}")
            missing += 1
            continue
        dst = dest / f"collectible_{it['id']:03d}.png"
        shutil.copy2(src, dst)
        copied += 1
    if missing:
        print(f"[warn] {missing} sprites missing — those items will render with broken icons")
    return copied


def write_collectibles_py(items: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '"""Auto-generated by tools/build_collectibles.py — do not edit by hand."""',
        "from __future__ import annotations",
        "",
        "# id -> {name, sprite, removed, desc_es}",
        "# `sprite` is the filename under tracker/assets/item_icons/ (empty if removed).",
        "# `desc_es` is the in-game Spanish pickup description (empty for removed).",
        "COLLECTIBLES: dict[int, dict] = {",
    ]
    for it in items:
        sprite = f"collectible_{it['id']:03d}.png" if not it["removed"] else ""
        desc = it.get("desc_es", "")
        lines.append(
            f"    {it['id']}: {{"
            f"'name': {it['name']!r}, "
            f"'sprite': {sprite!r}, "
            f"'removed': {it['removed']}, "
            f"'desc_es': {desc!r}"
            f"}},"
        )
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    isaac_root = find_isaac_root()
    print(f"[build_collectibles] isaac root: {isaac_root}")
    resources_dir = find_resources_dir(isaac_root)
    print(f"[build_collectibles] resources: {resources_dir}")

    stringtable_path = resources_dir / "stringtable.sta"
    if not stringtable_path.exists():
        sys.exit(f"stringtable.sta missing at {stringtable_path}")
    strings = parse_stringtable(stringtable_path)
    print(f"[build_collectibles] {len(strings)} stringtable keys")

    items_raw = parse_items_xml(resources_dir / "items.xml", strings)
    items = fill_id_gaps_as_removed(items_raw)
    real = sum(1 for it in items if not it["removed"])
    holes = len(items) - real
    with_desc = sum(1 for it in items if not it["removed"] and it.get("desc_es"))
    print(f"[build_collectibles] {len(items)} entries ({real} real, {holes} removed/placeholder)")
    print(f"[build_collectibles] {with_desc} items have a Spanish in-game description")

    project_root = Path(__file__).resolve().parents[1]
    icons_dir = project_root / "tracker" / "assets" / "item_icons"
    out_py = project_root / "tracker" / "data" / "collectibles.py"

    n = copy_sprites(items, resources_dir, icons_dir)
    write_collectibles_py(items, out_py)

    print(f"[build_collectibles] copied {n} sprites -> {icons_dir}")
    print(f"[build_collectibles] wrote table -> {out_py}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
