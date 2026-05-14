"""Extract EID (External Item Descriptions) Spanish descriptions.

Reads the Lua files shipped with the EID mod the user has installed, parses
the relevant tables in each, and writes Python dicts under `tracker/data/`:

- `eid_descriptions.py`  -> collectibles (items)
- `eid_cards.py`         -> cards/runes/soul stones
- `eid_pills.py`         -> pill effects (NOT horse pills)

Discovery:
- ISAAC_PATH env var, then Steam default paths.
- EID mod folder: `mods/external item descriptions_*` (workshop folder).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

DEFAULT_ROOTS = [
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\The Binding of Isaac Rebirth"),
    Path(r"C:\Program Files\Steam\steamapps\common\The Binding of Isaac Rebirth"),
]


def find_isaac_root() -> Path:
    env = os.environ.get("ISAAC_PATH")
    if env and Path(env).is_dir():
        return Path(env)
    for p in DEFAULT_ROOTS:
        if p.is_dir():
            return p
    sys.exit("Could not locate Isaac install. Set ISAAC_PATH env var.")


def find_eid_mod(isaac_root: Path) -> Path:
    mods = isaac_root / "mods"
    if not mods.is_dir():
        sys.exit(f"No mods folder at {mods}")
    for p in mods.iterdir():
        if p.is_dir() and "external item descriptions" in p.name.lower():
            return p
    sys.exit(
        "EID mod not found in mods/. Subscribe to 'External Item Descriptions' "
        "on Workshop and re-run."
    )


# Two entry formats appear in EID lua files:
#   A) [56] = { "56", "Name", "Desc" }    (rep+/spa.lua)
#   B) { "56", "Name", "Desc" }            (ab+/spa.lua — id comes from 1st string)
# Both wrap a 3-tuple of strings. We accept either and read the id from the
# first string literal.
_ENTRY_RE = re.compile(
    r"""(?:\[(?:\d+)\]\s*=\s*)?           # optional [id] = prefix (case A)
        \{\s*
        "(?P<id>\d+)"\s*,\s*              # first string is the id
        "(?P<name>(?:[^"\\]|\\.)*)"\s*,\s*
        "(?P<desc>(?:[^"\\]|\\.)*)"\s*
        (?:,\s*"(?:[^"\\]|\\.)*"\s*)?     # optional fourth field
        \}""",
    re.VERBOSE,
)

# Names of the lua tables that hold collectible descriptions. EID splits
# entries per DLC (rep, rep+) and also uses the bare name in ab+/spa.lua.
_COLLECTIBLE_TABLE_NAMES = (
    "collectibles",
    "repCollectibles",
    "repPlusCollectibles",
    "rep_PlusCollectibles",
    "repplusCollectibles",
    "rgonCollectibles",
)

# Card tables. `ab+/spa.lua` declares them via the path form
# `EID.descriptions[languageCode].cards={...}` — the table-header regex
# extracts just the trailing identifier (`cards`). `rep/spa.lua` uses
# `local repCards={...}`. `rep+/spa.lua` overrides via `local cards = {...}`.
# Variants are listed defensively in case future EID releases rename.
_CARD_TABLE_NAMES = (
    "cards",
    "repCards",
    "repPlusCards",
    "rep_PlusCards",
    "repplusCards",
)

# Pill effect tables. Same shape as cards. NOTE: `horsepills` is EXCLUDED on
# purpose — its id-to-effect mapping in EID is shifted (horse pill variants)
# and is not what the tracker's pill ids point to.
_PILL_TABLE_NAMES = (
    "pillEffects",
    "pills",
    "repPills",
    "repPlusPills",
    "rep_PlusPills",
    "repplusPills",
)

# EID inline tag, e.g. {{Coin}} {{Tears}} {{Warning}}. Most are sprite glyphs.
# We replace with a short emoji/text equivalent so the tooltip stays readable.
_TAG_MAP = {
    "Coin": "🪙",
    "Bomb": "💣",
    "Key": "🗝",
    "Heart": "❤",
    "RedHeart": "❤",
    "SoulHeart": "🤍",
    "BlackHeart": "🖤",
    "EternalHeart": "💠",
    "GoldHeart": "💛",
    "BoneHeart": "🦴",
    "Card": "🃏",
    "Pill": "💊",
    "Rune": "🔣",
    "Trinket": "🔱",
    "Tears": "💧",
    "Damage": "⚔",
    "Speed": "👟",
    "Range": "🎯",
    "Shotspeed": "🚀",
    "Luck": "🍀",
    "ShotSpeed": "🚀",
    "Health": "❤",
    "Warning": "⚠",
    "Battery": "🔋",
    "Fly": "🦟",
    "Poison": "☠",
    "Burning": "🔥",
    "Slow": "🐌",
    "Freezing": "❄",
    "Confusion": "💫",
    "Fear": "😱",
    "Charm": "💘",
    "Devil": "😈",
    "Angel": "👼",
    "Curse": "🌀",
    "Player": "👤",
    "Boss": "👹",
    "Question": "❓",
    "ArrowUp": "↑",
    "ArrowDown": "↓",
    "Blank": "",
    "AngelChance": "👼%",
    "DevilChance": "😈%",
    "PlanetariumChance": "🪐%",
}


def _strip_eid_markup(s: str) -> str:
    """Convert EID inline tags + line separators to plain text.

    `#` becomes a newline (EID uses `#` to start a new line).
    `{{Foo}}` becomes the mapped emoji/text (or is dropped if unknown).
    Lua escape sequences (\\n, \\\", etc.) are evaluated.
    """
    # Handle Lua escapes first.
    s = s.replace('\\"', '"').replace("\\n", "\n")
    # Replace inline tags. Unknown tags get stripped to keep the text readable.
    def _sub(m):
        tag = m.group(1)
        # Some tags are `Collectible123` etc — strip those silently.
        if tag in _TAG_MAP:
            return _TAG_MAP[tag]
        if tag.startswith("Collectible") or tag.startswith("Trinket") or tag.startswith("Card") or tag.startswith("Pill"):
            return ""
        return ""
    s = re.sub(r"\{\{([^}]+)\}\}", _sub, s)
    # EID line break.
    s = s.replace("#", "\n")
    # Collapse multiple spaces, trim each line.
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in s.split("\n")]
    return "\n".join(ln for ln in lines if ln)


def _table_header_positions(text: str) -> list[tuple[int, str]]:
    """Return (offset, table_name) for every `<name> = {` declaration.

    Used as a coarse map: an entry at offset X belongs to the latest header
    that appears before X. We don't try to parse balanced braces (EID lua has
    `}` characters inside `--` comments which would confuse a brace counter).
    """
    pat = re.compile(r"(?<![A-Za-z_])([A-Za-z_]\w*)\s*=\s*\{")
    return [(m.start(), m.group(1)) for m in pat.finditer(text)]


def parse_eid_file(
    path: Path, allowed_tables: tuple[str, ...] = _COLLECTIBLE_TABLE_NAMES
) -> dict[int, dict[str, str]]:
    """Return {id: {name, desc}} from one EID Spanish lua file.

    Strategy: build a position-sorted list of all `<name> = {` declarations,
    then for each `{ "id", "name", "desc" }` entry, find the nearest preceding
    declaration. Only entries whose host table is in `allowed_tables` are
    emitted. This avoids needing balanced-brace block extraction (EID lua
    has `}` inside `--` comments which would mis-balance a naive scan).
    """
    text = path.read_text(encoding="utf-8")
    headers = _table_header_positions(text)
    if not headers:
        return {}
    header_offsets = [h[0] for h in headers]
    header_names = [h[1] for h in headers]

    out: dict[int, dict[str, str]] = {}
    for m in _ENTRY_RE.finditer(text):
        # Find the host table for this entry: the latest header whose offset
        # is <= the entry's start.
        import bisect
        idx = bisect.bisect_right(header_offsets, m.start()) - 1
        if idx < 0:
            continue
        host = header_names[idx]
        if host not in allowed_tables:
            continue
        item_id = int(m.group("id"))
        name = _strip_eid_markup(m.group("name"))
        desc = _strip_eid_markup(m.group("desc"))
        out[item_id] = {"name": name, "desc": desc}
    return out


def write_eid_py(
    merged: dict[int, dict[str, str]], path: Path, var_name: str = "EID_DESCRIPTIONS"
) -> None:
    lines = [
        '"""Auto-generated by tools/build_eid.py — do not edit by hand."""',
        "from __future__ import annotations",
        "",
        "# id -> {name (EID Spanish), desc (EID Spanish, # → newline)}",
        f"{var_name}: dict[int, dict] = {{",
    ]
    for cid in sorted(merged):
        meta = merged[cid]
        lines.append(
            f"    {cid}: {{'name': {meta['name']!r}, 'desc': {meta['desc']!r}}},"
        )
    lines.append("}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_one(
    files: list[Path],
    allowed_tables: tuple[str, ...],
    label: str,
) -> dict[int, dict[str, str]]:
    """Merge one logical category (collectibles / cards / pills) across DLC files.

    Order of `files` matters: later files OVERRIDE earlier ones for the same id
    (Repentance+ should be last to take precedence over base game).
    """
    merged: dict[int, dict[str, str]] = {}
    for f in files:
        if not f.exists():
            print(f"[build_eid] skip (missing): {f}")
            continue
        partial = parse_eid_file(f, allowed_tables)
        merged.update(partial)
        print(f"[build_eid] {label}: {f.parent.name}/{f.name}: {len(partial)} entries")
    return merged


def main() -> int:
    isaac_root = find_isaac_root()
    eid_root = find_eid_mod(isaac_root)
    print(f"[build_eid] EID mod: {eid_root}")

    # Order matters: later files override earlier ones for the same id.
    # Repentance+ is the newest, so it goes last to take precedence.
    files = [
        eid_root / "descriptions" / "ab+" / "spa.lua",
        eid_root / "descriptions" / "rep" / "spa.lua",
        eid_root / "descriptions" / "rep+" / "spa.lua",
    ]

    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "tracker" / "data"

    # 1) Collectibles (items) — original behavior.
    collectibles = _build_one(files, _COLLECTIBLE_TABLE_NAMES, "collectibles")
    print(f"[build_eid] {len(collectibles)} unique collectibles after merge")
    out_items = data_dir / "eid_descriptions.py"
    write_eid_py(collectibles, out_items, var_name="EID_DESCRIPTIONS")
    print(f"[build_eid] wrote table -> {out_items}")

    # 2) Cards / runes / soul stones.
    cards = _build_one(files, _CARD_TABLE_NAMES, "cards")
    print(f"[build_eid] {len(cards)} unique cards after merge")
    out_cards = data_dir / "eid_cards.py"
    write_eid_py(cards, out_cards, var_name="EID_CARDS")
    print(f"[build_eid] wrote table -> {out_cards}")

    # 3) Pill effects (NOT horse pills).
    pills = _build_one(files, _PILL_TABLE_NAMES, "pills")
    print(f"[build_eid] {len(pills)} unique pills after merge")
    out_pills = data_dir / "eid_pills.py"
    write_eid_py(pills, out_pills, var_name="EID_PILLS")
    print(f"[build_eid] wrote table -> {out_pills}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
