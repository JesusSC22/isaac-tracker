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

# Slugs del catálogo → nombres reales en la wiki.
# El generador del catálogo produce algunos slugs compactos (Larryjr, Dukeofflies)
# que la wiki espera con underscores (Larry_Jr, Duke_of_Flies). Esta tabla los corrige
# antes de probar los patrones genéricos.
NAME_WIKI_OVERRIDES: dict[str, str] = {
    # === Bosses con nombre compactado ===
    "Larryjr": "Larry_Jr.",
    "Dukeofflies": "Duke_of_Flies",
    "Gurdyjr": "Gurdy_Jr.",
    "Blightedovum": "Blighted_Ovum",
    "Thehollow": "The_Hollow_(Boss)",
    "Thewretched": "The_Wretched",
    "Thefallen": "The_Fallen_(Boss)",
    "Monstroii": "Monstro_II",
    "Maskofinfamy": "Mask_of_Infamy",
    "Daddylonglegs": "Daddy_Long_Legs",
    "Headlesshorseman": "Headless_Horseman",
    "Itlives": "It_Lives_(Boss)",
    "Lokii": "Lokii",          # wiki usa exactamente "Lokii"
    "Megamaw2": "Mega_Maw",
    "Fatty2": "Conjoined_Fatty",
    "Camillojr": "Camillo_Jr.",
    # === Enemies con nombre compactado ===
    "Flaminggaper": "Flaming_Gaper",
    "Rottengaper": "Rotten_Gaper",
    "Grilledclotty": "Grilled_Clotty",
    "Drownedhive": "Drowned_Hive",
    "Dankcharger": "Dank_Charger",
    "Drownedcharger": "Drowned_Charger",
    "Dankglobin": "Dank_Globin",
    "Drownedboomfly": "Drowned_Boomfly",
    "Dragonfly": "Dragon_Fly",
    "Sickboomfly": "Sick_Boom_Fly",
    "Hardhost": "Hard_Host",
    "Scarreddoublevis": "Scarred_Double_Vis",
    "Scarredguts": "Scarred_Guts",
    "Looseknight": "Loose_Knight",
    "Blackknight": "Black_Knight",
    "Hopperleaper": "Hopper_Leaper",
    "Scaredparabite Scarred": "Scarred_Parabite",
    "Muliboom": "Muli_Boom",
    "Mamafly": "Mama_Fly",
    "Lblob": "L_Blob",
    "Redboomfly": "Red_Boom_Fly",
    "Redhost": "Red_Host",
    "Psychicmaw": "Psychic_Maw",
    "Selflessknight": "Selfless_Knight",
    "Angelicbaby": "Angelic_Baby",
    "Membrain": "Membrain",    # wiki usa "Membrain" (una palabra)
    "Mamaguts": "Mama_Guts",
    "Kamikazeleech": "Kamikaze_Leech",
    "Holyleech": "Holy_Leech",
    "Cagevis": "Cage_Vis",
    "Maskandheart": "Mask_+_Heart",
    "Eviltwin": "Evil_Twin",
    "Brimstoneeye": "Brimstone_Eye",
    "Constantstoneshooter": "Constant_Stone_Shooter",
    "Flamingfatty": "Flaming_Fatty",
    "Dankdeathshead": "Dank_Death's_Head",
    "Deathshead": "Death's_Head",
    "Level2fly": "Level_2_Fly",
    "Danksquirt": "Dank_Squirt",
    "Blackmaw": "Black_Maw",
    "Nerveending2": "Nerve_Ending_2",
    "Gapingmaw": "Gaping_Maw",
    "Wallcreep": "Wall_Creep",
    "Soicreep": "Soi_Creep",
    "Ragecreep": "Rage_Creep",
    "Blindcreep": "Blind_Creep",
    "Nullbody": "Null_Body",
    "Psytumer": "Psy-Tumor",
    "Nightcrawler": "Night_Crawler",
    "Dartfly": "Dart_Fly",
    "Conjoinedfatty": "Conjoined_Fatty",
    "Blueconjoinedfatty": "Blue_Conjoined_Fatty",
    "Lilhaunt": "Lil'_Haunt",
    "Blackglobin": "Black_Globin",
    "Blackglobinhead": "Black_Globin_(Head)",
    "Blackglobinbody": "Black_Globin_(Body)",
    "Megaclotty": "Mega_Clotty",
    "Boneknight": "Bone_Knight",
    "Redghost": "Red_Ghost_(Enemy)",
    "Fleshdeathshead": "Flesh_Death's_Head",
    "Ultragreedcoins": "Ultra_Greed_(Coins)",
    "Ultragreeddoor": "Ultra_Greed_(Door_Portal)",
    "Mushroomman": "Mushroom_Man",
    "Poisonmind": "Poison_Mind",
    "Thething": "The_Thing",
    "Blindbat": "Blind_Bat",
    "Rockgrimace": "Rock_Grimace",
    "Bombgrimace": "Bomb_Grimace",
    "Deepgaper": "Deep_Gaper",
    "Subhorf": "Sub_Horf",
    "Rockspider": "Rock_Spider",
    "Tintedrockspider": "Tinted_Rock_Spider",
    "Flybomb": "Fly_Bomb",
    "Redflybomb": "Red_Fly_Bomb",
    "Coalboy": "Coal_Boy",
    "Grilledgyro": "Grilled_Gyro",
    "Fireworm": "Fire_Worm",
    "Echobat": "Echo_Bat",
    "Mullighoul": "Mulli_Ghoul",
    "Adultleech": "Adult_Leech",
    "Floatinghost": "Floating_Host",
    "Armyfly": "Army_Fly",
    "Visversa": "Vis_Versa",
    "Blicker": "Blicker",      # wiki usa "Blicker" (una palabra)
    "Dople": "Dople",          # wiki usa "Dople"
    "Hanger": "Hanger",        # wiki usa "Hanger"
    "Homunculus": "Homunculus",
    "Splasher": "Splasher",
    "Roundworm": "Round_Worm",
    "Swapper": "Swapper_(Enemy)",
    "Strifer": "Strifer",
    "Revenant": "Revenant",
    "Nightwatch": "Night_Watch",
    "Spikeball": "Spike_Ball",
    "Cohort": "Cohort",
    "Vessel": "Vessel_(Enemy)",
    "Unborn": "Unborn_(Enemy)",
    # === Repentance bosses ===
    "Visage": "Visage",
    "Heretic": "Heretic",
    "Hornfel": "Hornfel",
    "Gideon": "Gideon_(Boss)",
    "Scourge": "Scourge",
    "Singe": "Singe",
    "Colostomia": "Colostomia",
    "Raglich": "Raglich",
    "Cadavra": "Cadavra",
    # === Bosses con nombre ambiguo (solo los que dan 404 en el fallback) ===
    "Husk": "Husk_(Boss)",
    "Gish": "Gish_(Boss)",
    "Loki": "Loki_(Boss)",
    "Haunt": "Haunt_(Boss)",
    "Hush": "Hush_(Boss)",
    # === Enemies con nombre ambiguo o distinto en la wiki ===
    "Bodies": "Flesh_(Posthumous_Fate)",
    "Satan Leg": "Satan_(Leg_of)",
    "Blue Baby": "Blue_Baby_(Boss)",
    "Lump Corpse2": "Lump",
    "Brimstone Head": "Brimstone_Head_(Enemy)",
    "Dip Corn": "Dip_Corn",
    "Boney Body": "Boney",
    "Wall Hugger": "Wallhugger",
    "Level2spider Small": "Level_2_Spider",
    "Moms Hand": "Mom's_Hand",
    "Mother's Shadow": "Mother's_Shadow_(Boss)",
    "Ultra Greed": "Ultra_Greed_(Boss)",
    "Horny Boys": "Horny_Boys",
    # === Enemies con nombre compuesto sin underscore en wiki ===
    "Boomfly": "Boom_Fly",
    "Codworm": "Cod_Worm",
    "Roundy": "Roundy_(Enemy)",
    "Canary": "Canary",
    "Foreigner": "Foreigner",
    "Wraith": "Wraith",
    "Gyro": "Gyro",
    "Faceless": "Faceless",
    "Necromancer": "Necromancer",
    "Coal": "Coal_(Enemy)",
    "Bouncer": "Bouncer_(Enemy)",
}


def candidate_urls(name_en: str, category: str) -> list[str]:
    """Patrones de naming en la wiki para sprites de enemigos."""
    if category == "boss":
        suffixes = ["_ingame.png", ".png", "_appear.png"]
    elif category == "miniboss":
        suffixes = ["_ingame.png", ".png"]
    else:
        suffixes = [".png", "_appear.png"]

    def _variants_for(wiki_name: str) -> list[str]:
        no_apos = re.sub(r"['']", "", wiki_name)
        variants = list(dict.fromkeys([wiki_name, no_apos]))
        result = []
        for v in variants:
            for suf in suffixes:
                result.append(BASE_FILE + urllib.parse.quote(v + suf, safe=""))
                if category in {"boss", "miniboss"}:
                    result.append(BASE_FILE + urllib.parse.quote(f"Boss_{v}{suf}", safe=""))
        return result

    candidates = []

    # 1) Intentar primero el override conocido de la wiki
    if name_en in NAME_WIKI_OVERRIDES:
        candidates.extend(_variants_for(NAME_WIKI_OVERRIDES[name_en]))

    # 2) Fallback genérico: nombre tal como está en el catálogo
    base = name_en.strip().replace(" ", "_")
    candidates.extend(_variants_for(base))

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
