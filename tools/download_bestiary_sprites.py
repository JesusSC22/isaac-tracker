"""Descarga sprites del bestiario desde bindingofisaacrebirth.wiki.gg.

Para los big bosses, usa BIG_BOSSES[i].sprite_url directamente.
Para el resto del bestiario, prueba varios patrones de URL.
"""
from __future__ import annotations

import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "tracker" / "assets" / "bestiary_icons"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
from tracker.data.bestiary import BESTIARY_CATALOG  # noqa: E402
from tracker.data.big_bosses import BIG_BOSSES  # noqa: E402

BASE_FILE = "https://bindingofisaacrebirth.wiki.gg/wiki/Special:FilePath/"
USER_AGENT = "isaac-tracker-bestiary-fetcher/1.0"


def candidate_urls(name_en: str, category: str) -> list[str]:
    """Patrones de naming en la wiki para sprites de enemigos."""
    base = name_en.strip().replace(" ", "_")
    no_apos = re.sub(r"['']", "", base)

    if category == "boss":
        suffixes = ["_ingame.png", ".png", "_appear.png"]
    elif category == "miniboss":
        suffixes = ["_ingame.png", ".png"]
    else:
        suffixes = [".png", "_appear.png"]

    candidates = []
    for variant in dict.fromkeys([base, no_apos]):  # dedup preserving order
        for suf in suffixes:
            candidates.append(BASE_FILE + urllib.parse.quote(variant + suf, safe=""))
            if category in {"boss", "miniboss"}:
                candidates.append(BASE_FILE + urllib.parse.quote(f"Boss_{variant}{suf}", safe=""))

    # Dedup manteniendo orden
    seen: set[str] = set()
    out: list[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def try_download(url: str, out: Path) -> tuple[bool, int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            if len(data) < 100 or data[:8] != b"\x89PNG\r\n\x1a\n":
                return False, len(data), "not-a-png"
            out.write_bytes(data)
            return True, len(data), ""
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False, 0, "404"
            err = f"http-{e.code}"
            time.sleep(0.5 * (attempt + 1))
        except Exception as e:
            err = type(e).__name__
            time.sleep(0.5 * (attempt + 1))
    return False, 0, err  # type: ignore[possibly-undefined]


def download_big_bosses() -> tuple[int, list]:
    failures = []
    ok = 0
    for entry in BIG_BOSSES:
        url = entry["sprite_url"]
        if not url or not url.startswith("http"):
            continue  # Boss Rush usa bossrush.png local
        out = OUT_DIR / f"bigboss_{entry['idx']:02d}.png"
        if out.exists() and out.stat().st_size > 100:
            print(f"  SKIP big_boss[{entry['idx']:2d}] {entry['name_en']:30s} (already exists)")
            ok += 1
            continue
        success, size, err = try_download(url, out)
        if success:
            print(f"  OK  big_boss[{entry['idx']:2d}] {entry['name_en']:30s} ({size}B)")
            ok += 1
        else:
            failures.append((entry["idx"], entry["name_en"], err))
            print(f"  FAIL big_boss[{entry['idx']:2d}] {entry['name_en']:30s} err={err}")
        time.sleep(0.25)
    return ok, failures


def download_bestiary() -> tuple[int, list]:
    failures = []
    ok = 0
    total = len(BESTIARY_CATALOG)
    for i, ((t, v), meta) in enumerate(BESTIARY_CATALOG.items(), 1):
        out = OUT_DIR / f"{t:03d}_{v:03d}.png"
        if out.exists() and out.stat().st_size > 100:
            ok += 1
            continue
        success = False
        last_err = "no-candidates"
        urls = candidate_urls(meta["name_en"], meta["category"])
        for url in urls:
            s, size, err = try_download(url, out)
            if s:
                success = True
                last_err = ""
                print(f"  OK  ({t:3d},{v:3d}) {meta['name_en']:30s} ({size}B) [{i}/{total}]")
                break
            last_err = err
            time.sleep(0.1)
        if success:
            ok += 1
        else:
            failures.append((t, v, meta["name_en"], last_err))
            print(f"  FAIL ({t:3d},{v:3d}) {meta['name_en']:30s} err={last_err} [{i}/{total}]")
        time.sleep(0.2)
    return ok, failures


def main() -> None:
    print("=== Big bosses ===")
    bb_ok, bb_fail = download_big_bosses()
    expected_bb = sum(1 for e in BIG_BOSSES if e["sprite_url"].startswith("http"))
    print(f"  Total OK: {bb_ok} / {expected_bb}")

    print("\n=== Bestiario ===")
    bes_ok, bes_fail = download_bestiary()
    print(f"  Total OK: {bes_ok} / {len(BESTIARY_CATALOG)}")

    if bb_fail or bes_fail:
        log = ROOT / "tools" / "bestiary_sprite_review.log"
        with log.open("w", encoding="utf-8") as f:
            f.write("=== Big bosses failures ===\n")
            for idx, name, err in bb_fail:
                f.write(f"  idx={idx} name={name} err={err}\n")
            f.write("\n=== Bestiary failures ===\n")
            for t, v, name, err in bes_fail:
                f.write(f"  ({t},{v}) name={name} err={err}\n")
        print(f"\nFallos volcados a: {log}")

    print(f"\n=== Resumen final ===")
    print(f"  Big bosses: {bb_ok} OK / {len(bb_fail)} FAIL")
    print(f"  Bestiario:  {bes_ok} OK / {len(bes_fail)} FAIL")


if __name__ == "__main__":
    main()
