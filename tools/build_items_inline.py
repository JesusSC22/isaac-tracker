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
        items.append({
            "id": item_id,
            "name": meta["name"],
            "sprite": meta["sprite"],
            "desc": desc,
        })
    out = ROOT / "tracker" / "assets" / "items_inline.js"
    payload = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    out.write_text(f"window.ITEMS_DATA = {payload};\n", encoding="utf-8")
    print(f"[build_items_inline] wrote {len(items)} items "
          f"({eid_used} with EID rich desc) -> {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
