"""Build el catálogo del bestiario + JS inline con sprites en base64.

Lee `tools/_bestiary_raw/MANIFEST.json` (generado por
`tools/extract_bestiary_assets.py`) y produce:

    tracker/data/bestiary.py          - dict {(type, variant): {name_en, name_es, category}}
    tracker/assets/bestiary_inline.js - window.BESTIARY_SPRITES = {"TTT.VVV": "data:image/png;base64,..."}

Estrategia de keys (type, variant):
  - scheme "rep" (filename `NNN.NNN_...`) → (type, variant) directos.
  - scheme "boss"/"monster" → buscar slug en SLUG_TO_ENTITY_TYPE. Si está
    presente y no es None, usar ese EntityType con variant=0. Si está como None
    saltar. Si no está, fallback al type del filename con uncertain=True.
  - bare_name_pngs → buscar slug en SLUG_TO_ENTITY_TYPE. Saltar si no está
    o es None.

Sprite processing:
  - PIL.open → crop heurístico al primer frame de la spritesheet.
  - Resize a TARGET_SIZE×TARGET_SIZE (LANCZOS).
  - PNG optimizado → base64 data URI.

Salida pensada para uso desde el frontend en HTML inline.
"""
from __future__ import annotations

import base64
import io
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "tools" / "_bestiary_raw"
MANIFEST_PATH = RAW_DIR / "MANIFEST.json"
OUT_CATALOG = ROOT / "tracker" / "data" / "bestiary.py"
OUT_INLINE = ROOT / "tracker" / "assets" / "bestiary_inline.js"

TARGET_SIZE = 32

# --------------------------------------------------------------------------- #
# Lookup tables                                                               #
# --------------------------------------------------------------------------- #

# Slug → EntityType (variant=0). Valor None ⇒ excluir del catálogo (FX, BG, etc.).
SLUG_TO_ENTITY_TYPE: dict[str, int | None] = {
    # Bosses sin prefijo numérico en filename
    "beast":           951,
    "beast_bg":        None,    # background, no enemigo
    "beast_ray":       None,    # FX
    "beast_souls":     None,    # FX
    "thelamb":         273,
    "the_lamb":        273,
    "mothers_shadow":  912,
    "mother":          912,
    "delirium":        412,
    "ultragreed":      406,
    "ultra_greed":     406,
    "hush":            407,
    "isaac":           102,
    "boss_isaac":      102,
    "satan":           84,
    "mom":             45,
    "momleg":          45,
    "moms_heart":      78,
    "moms_foot":       45,
    "blue_baby":       110,
    "blue_baby_isaac": 110,
    "dogma":           950,
    "babyplum":        908,
    "baby_plum":       908,
    "rotgut":          911,
    "scourge":         909,
    "chimera":         910,
    "min_min":         913,
    "minmin":          913,
    "clog":            914,
    "singe":           915,
    "colostomia":      917,
    "turdlet":         918,
    "raglich":         919,
    "horni_bois":      920,
    "horny_boys":      920,
    "clutch":          921,
    "cadavra":         922,
    "hornfel":         906,
    "siren":           904,
    "heretic":         905,
    "gideon":          907,
    "visage":          903,
    "bumbino":         916,
    "witness":         912,
    # Aliases adicionales encontrados en filenames del unpack
    "momsheart":       78,
    "moms_guts":       78,
    "momsguts":        78,
    "boss_hush":       407,
    "boss_mom":        45,
    "boss_isaac_isaac": 102,
    "bluebaby":        110,
    "bluebabyisaac":   110,
    # No-enemigos / FX / partes-de
    "ball_of_flies":   None,
    "big_flies":       None,
    "beelzeblub_dross": None,
}

# Mini-bosses canónicos por EntityType (heurística para categoría)
MINIBOSS_ENTITY_TYPES = {
    19,   # Larry Jr.
    20,   # Monstro
    21,   # Pin
    29,   # Duke of Flies
    36,   # Husk
    39,   # Gemini
    43,   # Gurdy
    71,   # Mega Maw
    81,   # The Bloat
    82,   # The Cage
    83,   # The Adversary
    85,   # Carrion Queen
    90,   # The Wretched
    91,   # Pride
    101,  # The Pride / Sin
}

# Bosses canónicos por EntityType (override de categoría — algunos pueden caer
# en monsters/ folder por accidente del unpack)
CANONICAL_BOSS_TYPES = {
    45,    # Mom
    78,    # Mom's Heart
    84,    # Satan
    102,   # Isaac (boss)
    110,   # Blue Baby (???)
    273,   # The Lamb
    406,   # Ultra Greed
    407,   # Hush
    412,   # Delirium
    903,   # Visage
    904,   # Siren
    905,   # Heretic
    906,   # Hornfel
    907,   # Gideon
    908,   # Baby Plum
    909,   # Scourge
    910,   # Chimera
    911,   # Rotgut
    912,   # Mother / Witness
    913,   # Min Min
    914,   # Clog
    915,   # Singe
    916,   # Bumbino
    917,   # Colostomia
    918,   # Turdlet
    919,   # Raglich
    920,   # Horny Boys
    921,   # Clutch
    922,   # Cadavra
    950,   # Dogma
    951,   # Beast
}

# Traducciones ES sólo para los más icónicos.
NAME_TRANSLATIONS_ES = {
    "Mom":              "Mamá",
    "Moms Heart":       "Corazón de Mamá",
    "Mom's Heart":      "Corazón de Mamá",
    "The Lamb":         "El Cordero",
    "Lamb":             "El Cordero",
    "Isaac":            "Isaac (Boss)",
    "Satan":            "Satán",
    "Hush":             "Hush",
    "Ultra Greed":      "Ultra Greed",
    "Delirium":         "Delirium",
    "Mother":           "Madre",
    "Mothers Shadow":   "Sombra de Madre",
    "Beast":            "La Bestia",
    "Dogma":            "Dogma",
    "Fly":              "Mosca",
    "Pooter":           "Pooter",
    "Spider":           "Araña",
    "Big Spider":       "Araña Grande",
    "Larry Jr":         "Larry Jr.",
    "Monstro":          "Monstro",
    "Gurdy":            "Gurdy",
    "Gaper":            "Gaper",
    "Rotten Gaper":     "Gaper Podrido",
    "Horf":             "Horf",
    "Boom Fly":         "Boom Fly",
}

# Suffixes que indican variantes (no queremos sustituir el sprite base por estos)
IGNORE_SUFFIXES = {
    "champion", "gehenna", "dross", "husk", "bony", "blue", "red",
}

# Regex para limpiar bare-name PNGs ("babyplum_dross.png" → "babyplum")
_BARE_SUFFIX_RE = re.compile(
    r"_(dross|husk|champion|bony|gehenna|blue|red|head|body|tail|left|right|bg|ray|souls)$",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #

# Slugs compactos sin separadores → nombre humano legible.
_COMPACT_SLUG_TITLES = {
    "thelamb":         "The Lamb",
    "momsheart":       "Mom's Heart",
    "momsguts":        "Mom's Guts",
    "ultragreed":      "Ultra Greed",
    "babyplum":        "Baby Plum",
    "bluebaby":        "Blue Baby",
    "bluebabyisaac":   "Blue Baby",
    "boss_isaac":      "Isaac",
    "boss_hush":       "Hush",
    "boss_mom":        "Mom",
    "minmin":          "Min Min",
    "min_min":         "Min Min",
    "horni_bois":      "Horny Boys",
    "mothers_shadow":  "Mother's Shadow",
}


def slug_to_title(slug: str) -> str:
    """`rotten_gaper` → `Rotten Gaper`, `mom` → `Mom`, `momleg` → `Momleg`."""
    if slug in _COMPACT_SLUG_TITLES:
        return _COMPACT_SLUG_TITLES[slug]
    parts = slug.replace("-", "_").split("_")
    return " ".join(p[:1].upper() + p[1:] for p in parts if p)


def folder_priority(folder: str) -> int:
    """Higher = preferido. Repentance > afterbirthplus > afterbirth > classic.

    Además los dlc3 priman sobre los no-dlc3 (es la versión más reciente extraída).
    """
    score = 0
    if "dlc3" in folder:
        score += 1
    if "repentance" in folder:
        score += 8
    elif "afterbirthplus" in folder:
        score += 4
    elif "afterbirth" in folder:
        score += 2
    return score


def classify_category(entity_type: int, folder: str) -> str:
    """Determina la categoría según folder + tipo."""
    if entity_type in CANONICAL_BOSS_TYPES:
        return "boss"
    if "/bosses/" in folder.replace("\\", "/"):
        return "boss"
    if entity_type in MINIBOSS_ENTITY_TYPES:
        return "miniboss"
    return "enemy"


def crop_first_frame(img: Image.Image) -> Image.Image:
    """Heurística simple: si el sheet parece NxM frames de uno, recortar a (0,0,h,h) o (0,0,w,w)."""
    w, h = img.size
    if w >= 2 * h and w % h == 0:
        return img.crop((0, 0, h, h))
    if h >= 2 * w and h % w == 0:
        return img.crop((0, 0, w, w))
    return img


def process_sprite(path: Path) -> str:
    """Carga PNG, recorta, redimensiona a 48x48, devuelve data URI base64."""
    with Image.open(path) as im:
        im = im.convert("RGBA")
        im = crop_first_frame(im)
        if im.size != (TARGET_SIZE, TARGET_SIZE):
            im = im.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        data = buf.getvalue()
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


# --------------------------------------------------------------------------- #
# Main build                                                                  #
# --------------------------------------------------------------------------- #

def build_catalog() -> tuple[dict[tuple[int, int], dict], dict[str, str]]:
    """Devuelve (catalog, sprites) donde sprites: {"TTT.VVV": data_uri}."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    # Per (type, variant): {meta_dict, folder, src_path, priority}
    chosen: dict[tuple[int, int], dict] = {}

    # Tiers de autoridad (más alto gana):
    #   3 = rep scheme (authoritative)
    #   2 = boss/monster con slug en SLUG_TO_ENTITY_TYPE (authoritative)
    #   2 = bare-name PNG con slug en SLUG_TO_ENTITY_TYPE (authoritative)
    #   1 = boss/monster con slug NO mapeado (uncertain fallback al filename type)
    def consider(key: tuple[int, int], src_path: Path, folder: str, slug: str, tier: int) -> None:
        prio = (tier, folder_priority(folder))
        existing = chosen.get(key)
        if existing is None or prio > existing["priority"]:
            chosen[key] = {
                "src": src_path,
                "folder": folder,
                "slug": slug,
                "priority": prio,
                "tier": tier,
            }

    # ---- Pase 1: entries con scheme rep ------------------------------------ #
    for e in manifest["entries"]:
        if e["suffix"]:  # ignorar variantes (champion, gehenna, etc.)
            continue
        scheme = e["scheme"]
        src = RAW_DIR / e["folder"] / e["filename"]
        if not src.exists():
            continue
        if scheme == "rep":
            key = (e["type"], e["variant"])
            consider(key, src, e["folder"], e["name_en_slug"], tier=3)
        elif scheme in ("boss", "monster"):
            slug = e["name_en_slug"]
            etype = SLUG_TO_ENTITY_TYPE.get(slug, "NOTFOUND")
            if etype is None:
                continue  # explicitamente excluido
            if etype == "NOTFOUND":
                # fallback al type del filename — incierto, tier bajo
                key = (e["type"], 0)
                consider(key, src, e["folder"], slug, tier=1)
            else:
                key = (etype, 0)
                consider(key, src, e["folder"], slug, tier=2)

    # ---- Pase 2: bare-name PNGs (bosses sin prefijo numérico) -------------- #
    for e in manifest["bare_name_pngs"]:
        fn = e["filename"]
        if not fn.lower().endswith(".png"):
            continue
        stem = fn[:-4]
        # quitar sufijos del tipo _dross, _husk, etc.
        cleaned = _BARE_SUFFIX_RE.sub("", stem).lower()
        # Probar varias formas del slug: tal cual, sin `boss_NNN_` prefix,
        # sin `boss_` prefix, normalizado a snake_case (espacios → _).
        candidates = [cleaned]
        m = re.match(r"^boss_\d+_(.+)$", cleaned)
        if m:
            candidates.append(m.group(1))
        if cleaned.startswith("boss_"):
            candidates.append(cleaned[5:])
        if cleaned.startswith("monster_"):
            candidates.append(cleaned[8:])
        # espacios → _
        candidates.extend(c.replace(" ", "_").replace("-", "_") for c in list(candidates))
        # quitar _ → ''
        candidates.extend(c.replace("_", "") for c in list(candidates))

        etype = None
        chosen_slug = candidates[0]
        for cand in candidates:
            if cand in SLUG_TO_ENTITY_TYPE:
                mapped = SLUG_TO_ENTITY_TYPE[cand]
                if mapped is None:
                    etype = None
                    break
                etype = mapped
                chosen_slug = cand
                break
        if etype is None:
            continue
        src = RAW_DIR / e["folder"] / fn
        if not src.exists():
            continue
        key = (etype, 0)
        consider(key, src, e["folder"], chosen_slug, tier=2)

    # ---- Construir catálogo + sprites -------------------------------------- #
    catalog: dict[tuple[int, int], dict] = {}
    sprites: dict[str, str] = {}
    failures = 0
    for key, info in sorted(chosen.items()):
        try:
            data_uri = process_sprite(info["src"])
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"  [warn] failed to process {info['src']}: {exc}", file=sys.stderr)
            continue
        name_en = slug_to_title(info["slug"])
        name_es = NAME_TRANSLATIONS_ES.get(name_en, name_en)
        category = classify_category(key[0], info["folder"])
        catalog[key] = {
            "name_en": name_en,
            "name_es": name_es,
            "category": category,
        }
        sprite_id = f"{key[0]:03d}.{key[1]:03d}"
        sprites[sprite_id] = data_uri

    if failures:
        print(f"[build_bestiary] {failures} sprite(s) failed to process", file=sys.stderr)
    return catalog, sprites


def emit_catalog(catalog: dict[tuple[int, int], dict]) -> None:
    lines = [
        '"""Catálogo de enemigos del bestiario — GENERADO por tools/build_bestiary.py.',
        "",
        "NO editar a mano. Para añadir traducciones, edita NAME_TRANSLATIONS_ES en",
        "tools/build_bestiary.py y reejecuta.",
        '"""',
        "from __future__ import annotations",
        "",
        "BESTIARY_CATALOG: dict[tuple[int, int], dict] = {",
    ]
    for (t, v), meta in sorted(catalog.items()):
        name_en = meta["name_en"].replace('"', '\\"')
        name_es = meta["name_es"].replace('"', '\\"')
        lines.append(
            f'    ({t}, {v}): '
            f'{{"name_en": "{name_en}", "name_es": "{name_es}", "category": "{meta["category"]}"}},'
        )
    lines.append("}")
    lines.append("")
    OUT_CATALOG.write_text("\n".join(lines), encoding="utf-8")
    print(f"[build_bestiary] wrote {len(catalog)} entries -> {OUT_CATALOG}")


def emit_inline(sprites: dict[str, str]) -> None:
    payload = json.dumps(sprites, ensure_ascii=False, separators=(",", ":"))
    OUT_INLINE.write_text(f"window.BESTIARY_SPRITES = {payload};\n", encoding="utf-8")
    size = OUT_INLINE.stat().st_size
    print(f"[build_bestiary] wrote {len(sprites)} sprites -> {OUT_INLINE} ({size} bytes)")


def main() -> int:
    if not MANIFEST_PATH.exists():
        sys.exit(f"manifest not found: {MANIFEST_PATH}")
    catalog, sprites = build_catalog()
    emit_catalog(catalog)
    emit_inline(sprites)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
