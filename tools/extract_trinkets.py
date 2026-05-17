"""Extract trinket achievements from challenges.html and emit a JS data array
for the Baratijas tab.

The HTML's `c:"trinkets"` category is a grab-bag: it actually contains real
trinkets PLUS cards, runes, pills, keys/hearts/coins pickups, and a few plain
in-game milestones. We filter to real trinkets only and attach a Spanish
effect description (best-effort from in-game knowledge).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "challenges.html"

PATTERN = re.compile(
    r'\{i:(\d+),c:"trinkets",n:"((?:[^"\\]|\\.)*)",u:"((?:[^"\\]|\\.)*)"\}'
)

# Achievement IDs incorrectly bucketed as "trinkets" in challenges.html.
# These are cards, runes, pills, pickups (keys/hearts/coins/bombs/chests/sacks)
# or plain milestones — NOT trinkets.
NOT_TRINKETS = {
    # Runes
    89, 90, 91, 92, 93, 94, 95, 96, 233, 309,
    # Cards (Chaos / Credit / Rules / Card Against Humanity / Suicide King /
    # Get out of Jail Free / Holy / Ancient Recall / Era Walk / Wild / Queen
    # of Hearts / Tarot Major Arcana / Soul cards)
    97, 98, 99, 100, 120, 225, 293, 362, 363, 524, 525, 526, 527, 528, 529,
    530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544,
    602, 610, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630,
    631, 632, 633, 634,
    # Pills (2 new pills × 2, Gold Pill, Horse Pill)
    227, 228, 603, 606,
    # Pickups: special hearts, keys, coins, bombs, chests, sacks, batteries
    224,  # Gold Heart
    226,  # Gold Bomb
    249,  # Store Key
    333,  # Charged Key
    391,  # Bone Heart
    411,  # Rotten Heart
    415,  # Red Key
    493,  # Blue Key
    569,  # Crystal Key (Repentance)
    601,  # Mega Chest
    604,  # Black Sack
    609,  # Wooden Chest
    611,  # Haunted Chest
    613,  # Golden Penny
    615,  # Golden Battery
    # Plain milestones (no item — just an achievement notch)
    321, 322, 324, 325, 326, 327, 328, 329, 330, 336,
}

# Spanish effect description for each real trinket, keyed by exact name as it
# appears in challenges.html. Kept terse — one or two lines max.
TRINKET_DESC: dict[str, str] = {
    "Swallowed Penny":      "Al recibir daño sueltas 1 moneda.",
    "Petrified Poop":       "↑ Suerte +1 para que las cacas suelten mejores premios.",
    "AAA Battery":          "Si tu objeto activo está a 1 carga de poder usarse, se carga del todo.",
    "Broken Remote":        "Tu objeto activo teletransporta a Isaac a una sala aleatoria al usarse.",
    "Purple Heart":         "Los corazones malignos (negros/eternos/etc.) aparecen el doble de veces.",
    "Broken Magnet":        "Atrae bombas y baterías hacia Isaac.",
    "Rosary Bead":          "Las salas pueden contener una Bible al limpiarlas.",
    "Cartridge":            "Convierte la partida en un minijuego 8-bit estilo Game Boy al entrar a una sala.",
    "Pulse Worm":           "Tus lágrimas se mueven en ondas senoidales (zigzag).",
    "Wiggle Worm":           "Tus lágrimas se mueven en zigzag (movimiento serpenteante).",
    "Ring Worm":             "Tus lágrimas se mueven en espiral.",
    "Flat Worm":             "↑ Daño +1.2 y ↓ Alcance −1 (lágrimas anchas y planas).",
    "Store Credit":          "La próxima vez que entres a una tienda, un item de la tienda es gratis.",
    "Callus":               "No te hace daño caer en agujeros ni en pinchos del suelo.",
    "Lucky Rock":           "Las rocas pueden soltar monedas al destruirse.",
    "Mom's Toenail":        "Una vez por sala, el pie de mamá aplasta un enemigo aleatorio.",
    "Black Lipstick":       "Los corazones negros aparecen más a menudo.",
    "Bible Tract":          "Las salas pueden contener un Soul Heart al limpiarlas.",
    "Paper Clip":           "Abre cofres dorados sin necesidad de llave.",
    "Monkey's Paw":         "Cada vez que llegas a medio corazón, recibes un Black Heart (máx. 3 veces por run).",
    "Mysterious Paper":     "Cada piso te aplica al azar A Missing Page, A Polaroid, A Negative o Missing Poster.",
    "Daemon's Tail":        "Los corazones rojos que aparezcan son corazones negros.",
    "Missing Poster":       "Si mueres en una Sacrifice Room llevándolo, renaces como The Lost (y lo desbloqueas).",
    "Butt Penny":           "Al recibir daño tiras un montón de monedas al suelo.",
    "Mysterious Candy":     "Cada 10 segundos al azar te tiras un pedo, sueltas una caca, lloras o disparas una lágrima.",
    "Hook Worm":            "Tus lágrimas viajan en zigzag rectangular.",
    "Whip Worm":            "↑ Velocidad de lágrimas +0.75.",
    "Broken Ankh":          "33% de probabilidad de revivir como ??? al morir.",
    "Fish Head":            "Una mosca azul te orbita y te defiende. Sueltas más moscas al recibir daño.",
    "Pinky Eye":            "Tus lágrimas envenenan a los enemigos al azar.",
    "Push Pin":             "Tus lágrimas tienen piercing al azar.",
    "Liberty Cap":          "Cada piso recibes al azar un efecto temporal de seta (Magic Mushroom, Mini Mush, etc.).",
    "Umbilical Cord":       "Al bajar a medio corazón, spawnea Little Steven como familiar.",
    "Child's Heart":        "Los corazones aparecen más a menudo en las salas.",
    "Curved Horn":          "↑ Daño +1.",
    "Rusted Key":           "Las salas pueden contener una Key al limpiarlas.",
    "Goat Hoof":            "↑ Velocidad +0.15.",
    "Mom's Pearl":           "Los corazones de alma (soul hearts) aparecen el doble de veces.",
    "Cancer":               "↑ Cadencia de disparo +0.7 (tear delay −1).",
    "Red Patch":            "Al recibir daño, 30% de probabilidad de subir el daño esa run (+0.5).",
    "Match Stick":          "Las salas pueden contener una Bomb al limpiarlas.",
    "Lucky Toe":            "↑ Suerte +1.",
    "Cursed Skull":         "Al llegar a medio corazón, te teletransportas a una sala aleatoria.",
    "Safety Cap":            "Las salas pueden contener una Pill al limpiarlas.",
    "Ace of Spades":         "Las salas pueden contener una Card al limpiarlas.",
    "Isaac's Fork":         "Las salas pueden contener un corazón rojo extra.",
    "Maggy's Faith":        "↑ Suerte +1.",
    "Tape Worm":            "↑ Alcance +0.75 (lágrimas vuelan más lejos).",
    "Lazy Worm":            "↓ Velocidad de lágrimas (las lágrimas viajan más lento pero caen al suelo más rápido).",
    "Cracked Dice":         "Al recibir daño, te aplica un efecto aleatorio de D6, D8, D10 o D20.",
    "Super Magnet":         "Atrae cualquier pickup (monedas, llaves, bombas, corazones, baterías) hacia Isaac.",
    "Faded Polaroid":       "Te vuelve invisible a la mayoría de enemigos hasta que disparas.",
    "Louse":                "Tus lágrimas tienen 25% de probabilidad de sangrado (slowing + bleed).",
    "Bogo Bombs":           "Las bombas que recojas tienen una probabilidad de duplicarse.",
    "Bogo Coins":           "Las monedas que recojas tienen una probabilidad de duplicarse.",
    "Bag Lunch":            "Da una racion de comida (curación con efecto Lunch). Se consume al usar.",
    "Lost Cork":            "Las píldoras tienen el doble de efecto.",
    "Crow Heart":           "Los corazones rojos que recoges se convierten en black hearts (corazones negros).",
    "Walnut":               "Si te haces daño 5 veces con él, se rompe y suelta un objeto pasivo.",
    "Distant Admiration":   "Llevarlo encima añade una mosca-langosta familiar adicional.",
    "Bloody Crown":         "Cada piso, una sala normal extra se convierte en sala de jefe (más opciones de boss).",
    "Maggy's Bow":          "Recoger corazones rojos cura el doble.",
    "Cain's Eye":           "Al entrar a un piso, 25% de probabilidad de aplicar Compass todo el piso.",
    "Eve's Bird Foot":      "Spawnea Dead Birds al limpiar salas (al azar).",
    "The Left Hand":        "Los Golden Chests se convierten en Red Chests (cofres del diablo).",
    "Counterfeit Coin":     "Al usarlo, hace daño en área. Limitado.",
    "Burnt Penny":          "Las salas pueden contener una Coin al limpiarlas.",
    "Blood Penny":          "Las salas pueden contener un Half Heart al limpiarlas.",
    "Isaac's Head":         "Familiar: disparas la cabeza de Isaac que dispara lágrimas durante 4s, luego se recarga.",
    "Judas' Tongue":         "Los items del Devil Room cuestan la mitad de corazones.",
    "???'s Soul":           "Familiar volador que da vueltas alrededor de Isaac e inflige daño por contacto.",
    "Samson's Lock":        "Al limpiar una sala, 12% de probabilidad de subir el daño esa run (+0.5).",
    "Apollyon's Best Friend": "Si tienes Void, los items absorbidos sueltan un Locust friend.",
    "Forgotten Lullaby":    "Convierte tu objeto activo en disparable en cada sala sin necesidad de recargarlo manualmente.",
    "Lucky Pennies":        "Las monedas que recojas tienen probabilidad de ser Lucky Pennies (suben tu suerte +1 temporal).",
    "Filigree Feather":     "Las Angel Statues drop más items.",
    "Door Stop":            "Las puertas voladas o llaves no se cierran tras pasar (no se regenera la pared).",
    "Extension Cord":       "Si tienes The Battery, 9 Volt y Car Battery, tu activo se sobrecarga (++cargas).",
    "Rotten Penny":         "Al recoger una moneda, 25% de probabilidad de spawnear una Blue Fly amiga.",
    "Baby-Bender":          "Si usas I-The Magician o Telepathy mientras tienes lágrimas homing, los enemigos se vuelven amigos un rato.",
    "Finger Bone":          "Al matar enemigos hay probabilidad de spawnear un Bone Heart.",
    "Hairpin":              "Recargas tu activo +1 al recoger una batería (Lil' Battery).",
    "Wooden Cross":         "+1 contenedor de corazón al inicio de cada capítulo.",
    "Butter!":              "Tus trinkets se caen con frecuencia al recibir daño (juega con varios trinkets).",
    "Huge Growth":          "↑ Tamaño de Isaac +1 paso, ↑ Daño +1.",
    "Ancient Recall":       "Spawnea 3 cards al usar tu activo.",
    "Era Walk":             "Al usar tu activo, ralentiza todo durante 10s.",
    "Once More with Feeling!": "Logro general (no es trinket).",
    "Hat trick!":            "Logro general (no es trinket).",
    "Sin collector":         "Logro general (no es trinket).",
    "Dedication":            "Logro general (no es trinket).",
    "ZIP!":                  "Logro general (no es trinket).",
    "It's the Key":          "Logro general (no es trinket).",
    "Mr. Resetter!":         "Logro general (no es trinket).",
    "Living on the edge":    "Logro general (no es trinket).",
    "U Broke It!":           "Logro general (no es trinket).",
    "The Marathon":          "Logro general (no es trinket).",
    "Rib of Greed":         "Al recoger una moneda, 25% de probabilidad de soltar un Black Heart.",
    "Cracked Dice":         "Al recibir daño, te aplica un D6/D8/D10/D20 aleatorio.",
    "Black Feather":        "↑ Daño +0.16 por cada item maligno (Devil/Dark) que tengas.",
    "Karma":                "Donar a la Greed Donation Machine te da items extra.",
    "Sticky Nickels":        "Las monedas se pegan a las paredes y a veces se transforman en Mimic enemy.",
    "Silver Dollar":        "Hace que aparezca una shop en Womb / Corpse. Debes tenerlo al entrar al piso.",
    "Bloody Crown":         "Cada piso, una sala normal extra se convierte en sala de jefe (más opciones de boss).",
    "Meconium":             "10% de probabilidad de Black Heart al matar enemigos.",
    "Stem Cell":            "Cada habitación, cura 1/2 corazón si te falta vida.",
    "Crow Heart":            "Los corazones rojos que recoges se convierten en corazones negros.",
    "Bat Wing":             "Cada vez que matas a un enemigo, 10% de probabilidad de un Black Heart.",
    "Locust of Wrath":      "Al entrar a sala con enemigos, spawnea una langosta roja que hace explosión.",
    "Locust of Pestilence": "Al entrar a sala con enemigos, spawnea una langosta verde que envenena.",
    "Locust of Famine":     "Al entrar a sala con enemigos, spawnea una langosta amarilla que ralentiza.",
    "Locust of Death":      "Al entrar a sala con enemigos, spawnea una langosta negra (Death) que inflige mucho daño.",
    "Locust of Conquest":   "Al entrar a sala con enemigos, spawnea 1–4 langostas blancas con 2× tu daño.",
    "Poker Chip":           "El primer pedestal de cada piso suelta un segundo item al recogerlo.",
    "Stud Finder":          "Las salas pueden contener un nickel (5¢) al limpiarlas.",
    "Counterfeit Coin":     "Sale gratis al gastarla, pero el comerciante se enfada.",
    "Old Capacitor":        "Convierte el daño que recibes en cargas para tu activo.",
    "Mom's Lock":           "Las llaves se duplican al recogerlas a veces.",
    "Dice Bag":             "Cada habitación, hay probabilidad de spawnear un dado aleatorio (D6, D20, etc.) en el suelo.",
    "Holy Crown":           "Las Angel Rooms están garantizadas en cada piso si no entras a Devil.",
    "Mother's Kiss":        "↑ +1 contenedor de corazón al inicio de cada capítulo.",
    "Gilded Key":           "Cofres dorados sueltan items extra.",
    "Lucky Sack":           "Las bolsas (Grab Bags) sueltan el doble de pickups.",
    "Your Soul":            "Al morir, te da una segunda vida (revives como The Lost una vez).",
    "Number Magnet":        "Atrae las monedas hacia Isaac (rango grande).",
    "Dingle Berry":         "Cada piso, 50% de probabilidad de spawnear un Dip familiar.",
    "Ring Cap":             "Las bombas hacen +1 de daño extra y suenan más fuerte.",
    "Strange Key":          "Abre cofres con llaves coloreadas sin gastar la llave.",
    "Lil Clot":             "Cada vez que recibes daño, suelta sangre que cura medio corazón si la recoges.",
    "Temporary Tattoo":     "+0.5 daño durante la primera sala de cada piso.",
    "Swallowed M80":        "Al recibir daño, explotas haciendo daño en área.",
    "Wicked Crown":         "Los jefes sueltan más drops (corazones, monedas, etc.).",
    "Azazel's Stump":       "Lanza brimstone corto en cada sala (auto-aimed).",
    "Torn Pocket":          "Sueltas 1 moneda cada vez que recibes daño.",
    "Torn Card":            "Cada 15 enemigos matados, una card aleatoria spawnea en el suelo.",
    "Nuh Uh!":              "Al recibir daño, 50% de probabilidad de no perder vida.",
    "Modeling Clay":        "Te concede el efecto de un item pasivo aleatorio durante el piso.",
    "The Twins":            "Si tienes un familiar, hay probabilidad de duplicarlo cada sala.",
    "Adoption Papers":      "Tus familiares hacen +50% más de daño.",
    "Keeper's Bargain":      "Devil Deals cuestan 1 moneda en lugar de corazones (sólo para Keeper).",
    "Cursed Penny":         "Al recoger una moneda, 25% de probabilidad de aplicarte una maldición esa sala.",
    "Cricket Leg":          "↑ Daño +0.3, ↑ Lágrimas +0.7.",
    "Polished Bone":        "Cada sala spawnea un Bony familiar aliado.",
    "Hollow Heart":         "↑ +1 Bone Heart al inicio de cada capítulo.",
    "Expansion Pack":        "Tu activo gana un segundo uso al cargarse.",
    "Beth's Essence":       "Convierte tu segunda alma en otra Bethany al recoger Wisp.",
    "RC Remote":            "Tu objeto activo se puede usar a distancia con un botón extra.",
    "Found Soul":           "Familiar fantasmal que dispara lágrimas con efecto.",
    "Beth's Faith":         "Las Wisps blancas tienen tu daño multiplicado.",
    "Devil's Crown":        "Convierte los items del Treasure Room en items del Devil Room a precio de monedas.",
    "M":                    "Al usar tu objeto activo, ejecuta un efecto random (como D Infinity).",
    "Charged Penny":        "Tu activo se carga al recoger monedas.",
    "Cain's Eye":           "Al entrar a un piso, 25% de probabilidad de aplicar Compass todo el piso.",
    "Brokenankh":           "Revive como ??? con 33% de probabilidad al morir.",
    "Blessed Penny":        "Las salas pueden contener un soul heart o half soul heart al limpiarlas.",
    "Bone Heart":            "Pickup (no es trinket).",
    "Sigil of Baphomet":    "Al limpiar una sala, 5% de probabilidad de spawnear Black Heart o item demoníaco.",
    "Broken Glasses":       "Tus lágrimas tienen probabilidad de duplicarse y rebotar.",
    "Ice Cube":             "Tus lágrimas tienen probabilidad de congelar a los enemigos.",
    "Kid's Drawing":        "Spawnea un familiar 'Imaginary Friend' que ataca enemigos.",
}


def main() -> None:
    text = HTML.read_text(encoding="utf-8")
    seen_ach: set[int] = set()
    entries: list[dict] = []
    skipped = 0
    for m in PATTERN.finditer(text):
        ach_id = int(m.group(1))
        if ach_id in NOT_TRINKETS:
            skipped += 1
            continue
        if ach_id in seen_ach:
            continue
        seen_ach.add(ach_id)
        name = m.group(2).replace('\\"', '"')
        unlock = m.group(3).replace('\\"', '"')
        desc = TRINKET_DESC.get(name, "")
        entry: dict = {"achId": ach_id, "name": name, "unlock": unlock}
        if desc:
            entry["desc"] = desc
        entries.append(entry)

    entries.sort(key=lambda e: e["achId"])
    print(f"Extracted {len(entries)} real trinkets (skipped {skipped} non-trinkets)")
    described = sum(1 for e in entries if e.get("desc"))
    print(f"Descriptions filled for {described}/{len(entries)} trinkets")

    lines = ["window.TRINKETS_DATA = ["]
    for e in entries:
        lines.append(
            "  "
            + json.dumps(e, ensure_ascii=False, separators=(",", ":"))
            + ","
        )
    lines.append("];")
    out = "\n".join(lines)

    out_path = ROOT / "tracker" / "assets" / "trinkets_inline.js"
    out_path.write_text(out + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
