"""Generate tracker/assets/cards_inline.js from tracker/data/cards.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tracker.data.cards import CARDS  # noqa: E402


def main() -> int:
    cards = []
    for cid, meta in sorted(CARDS.items()):
        if meta["removed"]:
            continue
        cards.append({
            "id": cid,
            "name": meta["name"],
            "sprite": meta["sprite"],
            "desc": meta.get("desc_es", ""),
            "group": meta.get("group", "especiales"),
        })
    out = ROOT / "tracker" / "assets" / "cards_inline.js"
    payload = json.dumps(cards, ensure_ascii=False, separators=(",", ":"))
    out.write_text(f"window.CARDS_DATA = {payload};\n", encoding="utf-8")
    print(f"[build_cards_inline] wrote {len(cards)} cards -> {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
