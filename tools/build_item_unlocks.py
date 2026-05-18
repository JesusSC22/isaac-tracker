"""Construye tracker/data/item_unlocks.py mapeando item_id → (ach_id, unlock_es).

Estrategia:
  1. Carga `achievements.json` y filtra Reward == 'Item'.
  2. Empareja el Name del logro con un item de COLLECTIBLES (con tolerancia a
     prefijos "A "/"The "/"An " y a apóstrofes/puntos/exclamaciones distintos).
  3. Una tabla `HAND_MAP` cubre los pocos casos en los que el achievement Name
     y el collectible Name divergen demasiado (p. ej. "A Bag of Pennies" → 94
     "Sack of Pennies").
  4. Aplica los PATTERNS de tools/translate_achievements.py al campo Unlock
     para producir texto en español.
  5. Escribe `tracker/data/item_unlocks.py` con un dict ITEM_UNLOCKS y otro
     ACH_ID_BY_ITEM consumidos por build_items_inline.py.

Uso:
    .venv\\Scripts\\python.exe tools\\build_item_unlocks.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tracker.data.collectibles import COLLECTIBLES  # noqa: E402
from tools.translate_achievements import translate  # noqa: E402


# Reemplazos post-traducción que cubren huecos no manejados por los PATTERNS
# de translate_achievements.py. Se aplican a la frase ya traducida.
POST_FIXES: list[tuple[str, str]] = [
    # Pluralizaciones inglesas que se cuelan
    (" times", " veces"),
    # Casos específicos (antes que los conectores genéricos)
    ("Jacob and Esau", "Jacob & Esau"),  # Nombre canónico del personaje
    ("Use the Blood Donation Machine", "Usa la Blood Donation Machine"),
    ("Use XIII - Death", "Usa XIII - Death"),
    ("Defeat ", "Derrota a "),
    ("Derrota a a ", "Derrota a "),
    # Conectores genéricos (al final, no estropean nombres canónicos como "Jacob & Esau")
    (" or ", " o "),
    (" and ", " y "),
]


def _post_fix(text: str) -> str:
    out = text
    for src, dst in POST_FIXES:
        out = out.replace(src, dst)
    return out


# Achievement Name → collectible item_id. Solo hace falta para los casos donde
# el matcheo automático no funciona (apóstrofes, prefijos, plurales, etc.).
HAND_MAP: dict[str, int] = {
    "A Small Rock": 90,        # The Small Rock
    "Lil' Chubby": 88,         # Little Chubby
    "A Bandage": 92,           # Super Bandage
    "A Bag of Pennies": 94,    # Sack of Pennies
    "A Gamekid": 93,           # The Gamekid
    "A Halo": 101,             # The Halo
    "Mom's Contact": 110,      # Mom's Contacts (plural)
    "A Bag of Bombs": 131,     # Bomb Bag
    "Technology .5": 244,      # Tech.5
    "Lil' Chest": 362,         # Lil Chest
}

# Achievement Names que NO corresponden a ningún collectible (co-op babies,
# trinkets, etc.). Se documentan para que el script no los reporte como
# fallos.
KNOWN_NON_COLLECTIBLE = {
    "A Noose",          # Co-op baby
    "A Fetus in a Jar", # Co-op baby
    "A Cross",          # Co-op baby
    "The Razor",        # Razor Baby (co-op)
    "Blue Candle",      # Item de The Lost (collectible no en nuestra lista)
    "Blind Rage",       # Trinket (id 81)
    "Mega",             # Co-op baby Mega Baby
    "Fart Baby",        # Co-op baby (no confundir con "Farting Baby" id 404)
}


def _norm(s: str) -> str:
    s = s.lower().replace("'", "").replace(".", "").replace("!", "").strip()
    return re.sub(r"\s+", " ", s)


def _build_name_index() -> dict[str, int]:
    """Indexa nombres de collectibles (con variantes A/The) a su item_id."""
    idx: dict[str, int] = {}
    for iid, meta in COLLECTIBLES.items():
        if meta["removed"]:
            continue
        n = meta["name"]
        variants = [n]
        # Strip leading article
        if n.startswith("The "):
            variants.append(n[4:])
        elif n.startswith("A "):
            variants.append(n[2:])
        # Add leading article variants
        if not n.startswith(("A ", "The ", "An ")):
            variants.append("A " + n)
            variants.append("The " + n)
        for v in variants:
            key = _norm(v)
            if key and key not in idx:
                idx[key] = iid
    return idx


def main() -> int:
    ach_path = ROOT / "tracker" / "data" / "achievements.json"
    with ach_path.open(encoding="utf-8") as f:
        achs = json.load(f)
    item_achs = [a for a in achs if a["Reward"] == "Item"]

    name_idx = _build_name_index()
    unlocks: dict[int, dict] = {}  # item_id → {"ach_id", "unlock_es"}
    missing: list[tuple[int, str]] = []

    for a in item_achs:
        n = a["Name"]
        iid = HAND_MAP.get(n)
        if iid is None:
            candidates = [n]
            if n.startswith("A "):
                candidates.append(n[2:])
            elif n.startswith("The "):
                candidates.append(n[4:])
            elif n.startswith("An "):
                candidates.append(n[3:])
            for c in candidates:
                k = _norm(c)
                if k in name_idx:
                    iid = name_idx[k]
                    break
        if iid is None:
            if n not in KNOWN_NON_COLLECTIBLE:
                missing.append((a["Id"], n))
            continue
        # Translate the Unlock text, then aplica reemplazos extra.
        unlock_es = _post_fix(translate(a["Unlock"]))
        unlocks[iid] = {"ach_id": a["Id"], "unlock_es": unlock_es}

    # Sort by item_id for deterministic output
    out_lines = [
        '"""Auto-generado por tools/build_item_unlocks.py — no editar a mano."""',
        "from __future__ import annotations",
        "",
        "# item_id -> {ach_id, unlock_es}",
        "# Items que NO están en este diccionario son 'iniciales' (sin",
        "# logro de desbloqueo: disponibles desde el principio del juego).",
        "ITEM_UNLOCKS: dict[int, dict] = {",
    ]
    for iid in sorted(unlocks):
        v = unlocks[iid]
        # Use repr to escape correctly
        unlock_repr = repr(v["unlock_es"])
        out_lines.append(
            f"    {iid}: {{'ach_id': {v['ach_id']}, 'unlock_es': {unlock_repr}}},"
        )
    out_lines.append("}")
    out_lines.append("")

    out_path = ROOT / "tracker" / "data" / "item_unlocks.py"
    out_path.write_text("\n".join(out_lines), encoding="utf-8")

    print(f"[build_item_unlocks] {len(unlocks)} items mapped to achievements")
    print(f"[build_item_unlocks] wrote {out_path}")
    if missing:
        print(f"[build_item_unlocks] WARNING: {len(missing)} achievements with no collectible match:")
        for aid, nm in missing:
            print(f"    #{aid:>4} {nm}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
