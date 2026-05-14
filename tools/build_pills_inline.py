"""Generate tracker/assets/pills_inline.js from tracker/data/pills.py."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tracker.data.pills import PILLS

def main() -> int:
    pills = []
    for pid, meta in sorted(PILLS.items()):
        if meta.get("removed", False):
            continue
        pills.append({
            "id": pid,
            "name": meta["name"],
            "sprite": meta["sprite"],
            "desc": meta.get("desc_es", ""),
            "horse": meta.get("horse", False),
        })
    out = ROOT / "tracker" / "assets" / "pills_inline.js"
    payload = json.dumps(pills, ensure_ascii=False, separators=(",", ":"))
    out.write_text(f"window.PILLS_DATA = {payload};\n", encoding="utf-8")
    print(f"[build_pills_inline] wrote {len(pills)} pills -> {out} ({out.stat().st_size} bytes)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
