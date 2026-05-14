"""Extract card and pill icons from EID mod's eid_cardspills.png + .anm2.

Cards (97): one PNG per card id (1..97).
Pills (50): vanilla ids 0-13 from EID; ids 14-49 use a placeholder.
"""
from __future__ import annotations
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tracker.data.cards import CARDS  # noqa: E402
from tracker.data.pills import PILLS  # noqa: E402

EID_DIR = Path(
    "C:/Program Files (x86)/Steam/steamapps/common/The Binding of Isaac Rebirth/"
    "mods/external item descriptions_836319872/resources/gfx"
)
SPRITESHEET = EID_DIR / "eid_cardspills.png"
ANM2 = EID_DIR / "eid_cardspills.anm2"

CARD_OUT = ROOT / "tracker" / "assets" / "card_icons"
PILL_OUT = ROOT / "tracker" / "assets" / "pill_icons"


def get_animation_frames(animation_name: str) -> list[tuple[int, int, int, int]]:
    """Return [(XCrop, YCrop, Width, Height), ...] for each Frame in the named Animation."""
    tree = ET.parse(ANM2)
    for anim in tree.iter("Animation"):
        if anim.get("Name") == animation_name:
            return [
                (
                    int(f.get("XCrop")),
                    int(f.get("YCrop")),
                    int(f.get("Width")),
                    int(f.get("Height")),
                )
                for la in anim.iter("LayerAnimation")
                for f in la.findall("Frame")
            ]
    raise SystemExit(f"Animation {animation_name!r} not found in {ANM2}")


def make_placeholder_pill(reference_png: Path, out_path: Path) -> None:
    """Save a desaturated, slightly darkened version of a real pill PNG as the placeholder."""
    im = Image.open(reference_png).convert("LA").convert("RGBA")
    im.save(out_path, optimize=True)


def main() -> int:
    sheet = Image.open(SPRITESHEET).convert("RGBA")

    CARD_OUT.mkdir(parents=True, exist_ok=True)
    PILL_OUT.mkdir(parents=True, exist_ok=True)

    # Cards: frame i -> id i+1.
    card_frames = get_animation_frames("Cards")
    active = sum(1 for m in CARDS.values() if not m["removed"])
    print(f"Cards animation has {len(card_frames)} frames; CARDS has {active} active.")
    cards_written = 0
    for i, (x, y, w, h) in enumerate(card_frames):
        cid = i + 1
        if cid not in CARDS or CARDS[cid]["removed"]:
            print(f"  WARN frame {i}: card id {cid} not in CARDS or removed; skipping")
            continue
        icon = sheet.crop((x, y, x + w, y + h))
        icon.save(CARD_OUT / f"card_{cid:03d}.png", optimize=True)
        cards_written += 1

    # Pills: frame i -> id i (vanilla 0-13).
    pill_frames = get_animation_frames("Pills")
    pills_real = 0
    for i, (x, y, w, h) in enumerate(pill_frames):
        icon = sheet.crop((x, y, x + w, y + h))
        icon.save(PILL_OUT / f"pill_{i:03d}.png", optimize=True)
        pills_real += 1

    # Pill ids 14-49: copy a desaturated placeholder.
    reference_pill = PILL_OUT / "pill_000.png"
    placeholder = PILL_OUT / "_placeholder.png"
    make_placeholder_pill(reference_pill, placeholder)
    pills_placeholder = 0
    for pid in range(14, max(PILLS) + 1):
        if pid not in PILLS:
            continue
        target = PILL_OUT / f"pill_{pid:03d}.png"
        target.write_bytes(placeholder.read_bytes())
        pills_placeholder += 1
    placeholder.unlink()  # delete the temp _placeholder.png

    print(f"\nCards: {cards_written} written")
    print(
        f"Pills: {pills_real} from EID + {pills_placeholder} placeholders "
        f"= {pills_real + pills_placeholder} total"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
