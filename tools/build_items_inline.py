"""Generate tracker/assets/items_inline.js from tracker/data/collectibles.py.

Run after `build_collectibles.py`. The .js is loaded by challenges.html via
`<script src="items_inline.js">` and assigns `window.ITEMS_DATA` (sorted by id,
removed items excluded).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tracker.data.collectibles import COLLECTIBLES  # noqa: E402
try:
    from tracker.data.eid_descriptions import EID_DESCRIPTIONS  # noqa: E402
except ImportError:
    EID_DESCRIPTIONS = {}  # gracefully degrade if EID build hasn't been run
try:
    from tracker.data.item_unlocks import ITEM_UNLOCKS  # noqa: E402
except ImportError:
    ITEM_UNLOCKS = {}  # gracefully degrade if unlocks build hasn't been run


def main() -> int:
    items = []
    eid_used = 0
    for item_id, meta in sorted(COLLECTIBLES.items()):
        if meta["removed"]:
            continue
        # Description priority: EID rich Spanish > stringtable short Spanish.
        eid = EID_DESCRIPTIONS.get(item_id, {})
        desc = eid.get("desc") or meta.get("desc_es", "")
        if eid.get("desc"):
            eid_used += 1
        entry = {
            "id": item_id,
            "name": meta["name"],
            "sprite": meta["sprite"],
            "desc": desc,
        }
        # Optional rich metadata — included only when present so the JS bundle
        # stays small. The tooltip code checks for `undefined` before rendering.
        kind = meta.get("kind")
        if kind:
            entry["kind"] = kind
        if meta.get("max_charges") is not None:
            entry["maxCharges"] = meta["max_charges"]
        if meta.get("quality") is not None:
            entry["quality"] = meta["quality"]
        if meta.get("craft_quality") is not None:
            entry["craftQuality"] = meta["craft_quality"]
        if meta.get("tags"):
            entry["tags"] = meta["tags"]
        if meta.get("pools"):
            entry["pools"] = meta["pools"]
        # Unlock info: si hay logro de desbloqueo, embedemos achId y texto en
        # español; si no, marcamos el item como inicial.
        unlock_meta = ITEM_UNLOCKS.get(item_id)
        if unlock_meta:
            entry["achId"] = unlock_meta["ach_id"]
            entry["unlock"] = unlock_meta["unlock_es"]
        else:
            entry["achId"] = None
            entry["unlock"] = "Inicial - disponible desde el principio"
        items.append(entry)
    out = ROOT / "tracker" / "assets" / "items_inline.js"
    payload = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    out.write_text(f"window.ITEMS_DATA = {payload};\n", encoding="utf-8")
    n_unlocks = sum(1 for it in items if it.get("achId") is not None)
    print(f"[build_items_inline] wrote {len(items)} items "
          f"({eid_used} with EID rich desc, {n_unlocks} with unlock data) "
          f"-> {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
