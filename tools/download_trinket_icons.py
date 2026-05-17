"""Descarga los 188 iconos de trinkets desde bindingofisaacrebirth.wiki.gg
y los guarda en tracker/assets/trinket_icons/{id}.png

Usa el endpoint Special:FilePath del MediaWiki, que redirige al archivo real.
Para nombres con caracteres especiales o variantes en el wiki, intenta
múltiples candidatos.
"""
from __future__ import annotations

import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "tracker" / "assets" / "trinket_icons"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
from tools.build_trinkets import TRINKETS  # noqa: E402

BASE = "https://bindingofisaacrebirth.wiki.gg/wiki/Special:FilePath/"


def _strip_punct(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9 \-_]", "", s)


def candidate_names(name: str) -> list[str]:
    """Genera varias variantes del nombre de archivo de icono.
    Las wikis a veces normalizan apóstrofes, símbolos y caracteres especiales
    de forma inconsistente, así que probamos varias formas."""
    base = name.strip()
    variants: list[str] = []

    # 1) Nombre tal cual con espacios → underscore.
    variants.append(base.replace(" ", "_"))
    # 2) Sin apóstrofes (Monkey's Paw → Monkeys Paw → Monkeys_Paw).
    no_apos = base.replace("'", "")
    if no_apos != base:
        variants.append(no_apos.replace(" ", "_"))
    # 3) Sin "'s" (Monkey's Paw → Monkey Paw → Monkey_Paw).
    no_apos_s = re.sub(r"'s\b", "", base).replace("'", "")
    if no_apos_s != base and no_apos_s != no_apos:
        variants.append(no_apos_s.replace(" ", "_").replace("__", "_"))
    # 4) Sin signos extras (Nuh Uh! → Nuh_Uh).
    stripped = _strip_punct(base)
    if stripped != base:
        variants.append(stripped.replace(" ", "_"))
    # 5) Reemplazar guion por underscore (Baby-Bender → Baby_Bender).
    if "-" in base:
        variants.append(base.replace(" ", "_").replace("-", "_"))

    # Quitar duplicados, manteniendo orden.
    seen: set[str] = set()
    unique: list[str] = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            unique.append(v)
    return unique


def try_download(filename: str, out: Path) -> tuple[bool, int, str]:
    url = BASE + urllib.parse.quote(f"Trinket_{filename}_icon.png", safe="")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "isaac-tracker-icon-fetcher/1.0"},
    )
    last_err = ""
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
            last_err = f"http-{e.code}"
            time.sleep(0.5 * (attempt + 1))
        except Exception as e:
            last_err = type(e).__name__
            time.sleep(0.5 * (attempt + 1))
    return False, 0, last_err


def main() -> None:
    failures: list[tuple[int, str]] = []
    successes = 0
    for tid, name, _ach, _unlock, _desc in TRINKETS:
        out_path = OUT_DIR / f"{tid}.png"
        if out_path.exists() and out_path.stat().st_size > 100:
            successes += 1
            continue
        ok = False
        last_size = 0
        last_err = ""
        for variant in candidate_names(name):
            ok, last_size, last_err = try_download(variant, out_path)
            if ok:
                print(f"  OK  #{tid:3d} {name:30s} ({last_size}B, '{variant}')")
                break
            time.sleep(0.2)
        if not ok:
            failures.append((tid, name))
            print(f"  FAIL #{tid:3d} {name:30s} err={last_err} tried={candidate_names(name)}")
        else:
            successes += 1
        time.sleep(0.2)

    print()
    print(f"Total:    {len(TRINKETS)}")
    print(f"OK:       {successes}")
    print(f"Failures: {len(failures)}")
    if failures:
        print("Fallos para reintentar manualmente:")
        for tid, name in failures:
            print(f"  #{tid:3d} {name}")


if __name__ == "__main__":
    main()
