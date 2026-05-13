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


def main() -> int:
    items = [
        {
            "id": item_id,
            "name": meta["name"],
            "sprite": meta["sprite"],
            "desc": meta.get("desc_es", ""),
        }
        for item_id, meta in sorted(COLLECTIBLES.items())
        if not meta["removed"]
    ]
    out = ROOT / "tracker" / "assets" / "items_inline.js"
    payload = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
    out.write_text(f"window.ITEMS_DATA = {payload};\n", encoding="utf-8")
    print(f"[build_items_inline] wrote {len(items)} items -> {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
