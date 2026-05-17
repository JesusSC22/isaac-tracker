"""Traduce in-place las descripciones (campo `u`) de ACHIEVEMENTS_DATA al español.

Estrategia: aplica patrones regex (más específicos primero), luego reemplazos
de palabras/frases. Los nombres propios de bosses, personajes, items, trinkets
y challenges se mantienen en inglés porque así los conoce la comunidad y los
wikis. Solo traduce verbos y conectores.

Uso:
    .venv\\Scripts\\python.exe tools\\translate_achievements.py

Modifica `challenges.html` (raíz) directamente. Después correr build.spec.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "challenges.html"

# --- Patrones regex (orden importa: más específico primero) -----------------
PATTERNS = [
    # Defeat + boss + on Hard mode as character
    (r"^Defeat (.+?) on Hard mode as (.+)$",
     r"Derrota a \1 en modo Difícil con \2"),
    (r"^Defeat (.+?) on Normal mode as (.+)$",
     r"Derrota a \1 en modo Normal con \2"),

    # Defeat + boss + N times
    (r"^Defeat (.+?) (\d+) times$",
     r"Derrota a \1 \2 veces"),
    (r"^Defeat (.+?) for the 1st time$",
     r"Derrota a \1 por primera vez"),

    # Defeat + multi-boss + as character
    (r"^Defeat Isaac, \?\?\?, Satan and The Lamb as (.+)$",
     r"Derrota a Isaac, ???, Satan y The Lamb con \1"),
    (r"^Defeat Hush and Boss Rush as (.+)$",
     r"Derrota a Hush y Boss Rush con \1"),
    (r"^Defeat \?\?\? and The Lamb$",
     r"Derrota a ??? y The Lamb"),
    (r"^Defeat \?\?\? or The Lamb$",
     r"Derrota a ??? o The Lamb"),
    (r"^Defeat \?\?\? or The Lamb\. Possession of The Polaroid/ The Negative is required, barring getting to Dark Room through a Sacrifice Room\.$",
     r"Derrota a ??? o The Lamb. Necesitas The Polaroid o The Negative (excepto llegando a Dark Room por una Sacrifice Room)."),

    # Defeat + The Lamb especiales
    (r"^Defeat The Lamb in under 20 minutes$",
     r"Derrota a The Lamb en menos de 20 minutos"),
    (r"^Defeat The Lamb without taking hearts, coins, and bombs through an entire run$",
     r"Derrota a The Lamb sin recoger corazones, monedas ni bombas en toda la run"),

    # Defeat + N + plural
    (r"^Defeat (\d+) portals$",
     r"Derrota a \1 portales"),

    # Defeat + N specific
    (r"^Defeat all 5 Harbingers$",
     r"Derrota a los 5 Harbingers"),
    (r"^Defeat all 7 deadly sins$",
     r"Derrota a los 7 pecados capitales"),
    (r"^Defeat all bosses in Downpour$",
     r"Derrota a todos los jefes de Downpour"),
    (r"^Defeat all bosses in the Mausoleum$",
     r"Derrota a todos los jefes del Mausoleum"),
    (r"^Defeat all bosses in the Mines$",
     r"Derrota a todos los jefes de Mines"),
    (r"^Defeat a Harbinger$",
     r"Derrota a un Harbinger"),
    (r"^Defeat an Angel (\d+) times$",
     r"Derrota a un Ángel \1 veces"),

    # Defeat + boss + using item
    (r"^Defeat (.+?) using (.+)$",
     r"Derrota a \1 usando \2"),

    # Defeat genérico al final
    (r"^Defeat Mom, Mom's Heart or It Lives using The Bible$",
     r"Derrota a Mom, Mom's Heart o It Lives usando The Bible"),
    (r"^Defeat (.+?) as (.+)$",
     r"Derrota a \1 con \2"),
    (r"^Defeat (.+)$",
     r"Derrota a \1"),

    # Earn all Hard mode completion marks
    (r"^Earn all Hard mode completion marks as (.+)$",
     r"Consigue todas las marcas de modo Difícil con \1"),
    (r"^Earn all Hard mode completion marks for all non-tainted characters$",
     r"Consigue todas las marcas de modo Difícil con todos los personajes no-tainted"),
    (r"^Earn all Hard mode completion marks for all characters, including tainted ones$",
     r"Consigue todas las marcas de modo Difícil con todos los personajes (incluidos los tainted)"),
    (r"^Earn all 5 / 9 \(except the cent sign for Ultra Greed\) / 10 / 12 completion marks on Hard mode as The Lost$",
     r"Consigue todas las marcas (5 / 9 sin el signo de centavo de Ultra Greed / 10 / 12) en modo Difícil con The Lost"),

    # Complete + challenge
    (r"^Complete (.+?) \(challenge #(\d+)\)$",
     r"Completa \1 (reto #\2)"),
    (r"^Complete (.+?) \(challenge #(\d+)\) and defeat (.+)$",
     r"Completa \1 (reto #\2) y derrota a \3"),

    # Complete Boss Rush as X
    (r"^Complete Boss Rush as (.+)$",
     r"Completa Boss Rush con \1"),

    # Complete Victory Lap
    (r"^Complete (\d+) Victory Laps and start a (\d+)\w*$",
     r"Completa \1 Victory Laps y empieza una \2.ª"),
    (r"^Complete a Victory Lap, defeating The Lamb$",
     r"Completa una Victory Lap derrotando a The Lamb"),

    # Complete N daily challenges
    (r"^Complete (\d+) daily challenges \(by touching the trophy at the end\)$",
     r"Completa \1 retos diarios (tocando el trofeo al final)"),

    # Complete chapter
    (r"^Complete chapter (\d+) without taking damage$",
     r"Completa el capítulo \1 sin recibir daño"),
    (r"^Complete chapter (\d+)$",
     r"Completa el capítulo \1"),

    # Complete + condición floors
    (r"^Complete (\d+) floors in a row without taking damage$",
     r"Completa \1 pisos seguidos sin recibir daño"),
    (r"^Complete a Chapter \(floors I and II\) after The Basement, start-to-finish, with only half a heart of health \(can use The Lost\)$",
     r"Completa un capítulo (pisos I y II) después de The Basement, de principio a fin, con solo medio corazón de vida (puedes usar The Lost)"),

    # Beat chapter
    (r"^Beat chapter (\d+) without taking damage$",
     r"Pasa el capítulo \1 sin recibir daño"),
    (r"^Beat chapter (\d+) (\d+) times$",
     r"Pasa el capítulo \1 \2 veces"),
    (r"^Beat chapter (\d+)$",
     r"Pasa el capítulo \1"),

    # Beat The Basement / Caves / Depths
    (r"^Beat The Basement (\d+) times$",
     r"Pasa The Basement \1 veces"),
    (r"^Beat all The (.+?) bosses \(not restricted to beating bosses in The \1\)$",
     r"Derrota a todos los jefes de The \1 (no es necesario derrotarlos dentro de The \1)"),
    (r"^Beat (.+?) as (.+)$",
     r"Pasa \1 con \2"),
    (r"^Beat (.+?) without taking damage$",
     r"Pasa \1 sin recibir daño"),
    (r"^Beat (.+)$",
     r"Pasa \1"),

    # Become X
    (r"^Become (.+)$",
     r"Conviértete en \1"),

    # Kill X
    (r"^Kill (\d+) (.+)$",
     r"Mata a \1 \2"),
    (r"^Kill (.+?) before he can escape after breaking his minecart$",
     r"Mata a \1 antes de que escape tras romper su minecart"),
    (r"^Kill (.+)$",
     r"Mata a \1"),

    # Destroy X
    (r"^Destroy (\d+) Tinted Rocks and defeat Mom's Heart (\d+) times$",
     r"Destruye \1 Tinted Rocks y derrota a Mom's Heart \2 veces"),
    (r"^Destroy (\d+) Tinted Rocks$",
     r"Destruye \1 Tinted Rocks"),
    (r"^Destroy (\d+) rainbow poops$",
     r"Destruye \1 popós de arcoíris"),
    (r"^Destroy (\d+) poops$",
     r"Destruye \1 popós"),
    (r"^Destroy (\d+) rocks$",
     r"Destruye \1 rocas"),

    # Donate
    (r"^Donate (\d+) coin to the Greed Donation Machine$",
     r"Dona \1 moneda a la Greed Donation Machine"),
    (r"^Donate (\d+) coins to the Greed Donation Machine$",
     r"Dona \1 monedas a la Greed Donation Machine"),
    (r"^Donate (\d+) coins to the Donation Machine$",
     r"Dona \1 monedas a la Donation Machine"),
    (r"^Donate to several Battery Bums until they pay out with an item$",
     r"Dona a varios Battery Bums hasta que suelten un item"),

    # Visit + N + Arcades
    (r"^Visit (\d+) Arcades$",
     r"Visita \1 Arcades"),

    # Acquire X
    (r"^Acquire (.+?) (\d+) times$",
     r"Consigue \1 \2 veces"),
    (r"^Acquire both key pieces$",
     r"Consigue las dos Key Pieces"),
    (r"^Acquire (.+)$",
     r"Consigue \1"),

    # Open chests / things
    (r"^Open (\d+) Locked Chests$",
     r"Abre \1 Cofres Cerrados"),
    (r"^Open the large version of Mom's Box in Home$",
     r"Abre la versión grande de Mom's Box en Home"),

    # Pick up
    (r"^Pick up (\d+) familiars in a single run$",
     r"Recoge \1 familiars en una sola run"),
    (r"^Pick up both Key Pieces from the Angels in one run$",
     r"Recoge las dos Key Pieces de los Ángeles en una run"),
    (r"^Pick up any 2 of the following items in a single run: (.+)$",
     r"Recoge cualquier 2 de estos items en una sola run: \1"),
    (r"^Pick up any 3 of the following items/trinkets in a single run: (.+)$",
     r"Recoge cualquier 3 de estos items/trinkets en una sola run: \1"),
    (r"^Pick up two technology items in one run$",
     r"Recoge dos items de tecnología en una run"),
    (r"^Pick up (.+)$",
     r"Recoge \1"),

    # Use X while holding Y
    (r"^Use (.+?) while holding (.+)$",
     r"Usa \1 sosteniendo \2"),
    (r"^Use the Red Key or Cracked Key (.+)$",
     r"Usa la Red Key o Cracked Key \1"),
    (r"^Use (.+)$",
     r"Usa \1"),

    # Have X or more Y at one time
    (r"^Have (\d+) or more (.+?) at one time$",
     r"Ten \1 o más \2 a la vez"),
    (r"^Have (\d+) (.+?) at the same time$",
     r"Ten \1 \2 a la vez"),
    (r"^Have (.+?) in your collection$",
     r"Ten \1 en tu colección"),
    (r"^Have both (.+?) in your collection$",
     r"Ten ambos \1 en tu colección"),
    (r"^Have The Battery, 9 Volt, and Car Battery in your collection$",
     r"Ten The Battery, 9 Volt y Car Battery en tu colección"),

    # Sleep
    (r"^Sleep in (\d+) beds$",
     r"Duerme en \1 camas"),
    (r"^Sleep in a bed$",
     r"Duerme en una cama"),

    # Blow up
    (r"^Blow up (\d+) Shopkeepers$",
     r"Vuela a \1 Shopkeepers"),
    (r"^Blow up (\d+) Arcade machines$",
     r"Vuela \1 máquinas de Arcade"),
    (r"^Blow up The Siren's skull after defeating her$",
     r"Vuela el cráneo de The Siren tras derrotarla"),
    (r"^Blow up doors and Secret Room walls (\d+) times$",
     r"Vuela puertas y paredes de Secret Room \1 veces"),

    # Allow X
    (r"^Allow Baby Plum to escape instead of defeating her$",
     r"Permite a Baby Plum escapar en vez de derrotarla"),

    # Collect
    (r"^Collect (\d+) of either (.+)$",
     r"Recoge \1 de: \2"),
    (r"^Collect all non-DLC items in the game, unlock all of the secrets and endings minus The Lost and his 6 unlockable items$",
     r"Recoge todos los items sin DLC del juego, desbloquea todos los secretos y endings excepto The Lost y sus 6 items desbloqueables"),
    (r"^Collect every entry in the Bestiary$",
     r"Completa todas las entradas del Bestiario"),
    (r"^Collect every item in the game, unlock all secrets and endings, and complete the bestiary$",
     r"Recoge todos los items del juego, desbloquea todos los secretos y endings, y completa el bestiario"),
    (r"^Collect every non-DLC item and unlock every ending\.$",
     r"Recoge todos los items sin DLC y desbloquea todos los endings."),
    (r"^Collect three of the following in a single run: (.+)$",
     r"Recoge tres de los siguientes en una sola run: \1"),

    # Enter X
    (r"^Enter every Shop from chapter 1 through chapter 3 in one run$",
     r"Entra a todas las tiendas desde el capítulo 1 al 3 en una run"),
    (r"^Enter the Corpse for the first time$",
     r"Entra a Corpse por primera vez"),

    # Get
    (r"^Get a (\d+)-win streak$",
     r"Consigue una racha de \1 victorias"),
    (r"^Get a (\d+)-win streak in the daily challenges \( You must have a score of above 0 on the score screen\)$",
     r"Consigue una racha de \1 victorias en los retos diarios (con score mayor a 0)"),
    (r"^Get a (\d+)-win streak, using a different character for each win$",
     r"Consigue una racha de \1 victorias, usando un personaje distinto en cada una"),

    # Hold
    (r"^Hold (\d+) coins at one time$",
     r"Ten \1 monedas a la vez"),

    # Make
    (r"^Make (\d+) deals with the Devil in one run$",
     r"Haz \1 tratos con el Diablo en una run"),
    (r"^Make a Super Bandage Girl by picking up 4 Balls of Bandages in one run; see unlocking Super Meat Boy & Super Bandage Girl$",
     r"Crea una Super Bandage Girl recogiendo 4 Balls of Bandages en una run"),
    (r"^Make a Super Meat Boy by picking up Cube of Meat 4 times in one run; see methods to create a Super Meat Boy$",
     r"Crea un Super Meat Boy recogiendo Cube of Meat 4 veces en una run"),

    # Obtain
    (r"^Obtain (\d+) items on a run \(e\.g\., via two Steam Sale and Restock - Duplicate passives/familiars count towards the total, e\.g\., multiple Breakfast\)$",
     r"Consigue \1 items en una run (p. ej. con dos Steam Sale y Restock — los duplicados de pasivos/familiars cuentan, p. ej. varios Breakfast)"),
    (r"^Obtain (\d+) coins\. Then spend every single one of them in a single run$",
     r"Consigue \1 monedas y gástalas todas en una sola run"),
    (r"^Obtain three Yes Mother\? items in one run$",
     r"Consigue tres items Yes Mother? en una run"),

    # Play
    (r"^Play the Shell Game (\d+) times$",
     r"Juega al Shell Game \1 veces"),

    # Spawn / Spend
    (r"^Spawn three charmed enemies in the same room$",
     r"Genera tres enemigos charmed en la misma sala"),
    (r"^Spend (\d+)\+ coins in a single Shop$",
     r"Gasta más de \1 monedas en una sola tienda"),

    # Reset / Recharge / Purchase / Participate / Take
    (r"^Reset (\d+) times in a row$",
     r"Reinicia \1 veces seguidas"),
    (r"^Recharge using Lil' Batteries (\d+) times$",
     r"Recarga usando Lil' Batteries \1 veces"),
    (r"^Purchase from Shops, Devil deals or Black Markets (\d+) times$",
     r"Compra en Tiendas, Devil Deals o Black Markets \1 veces"),
    (r"^Participate in (\d+) daily challenges \(they don't have to be consecutive; it will still count if you die in the first room\)$",
     r"Participa en \1 retos diarios (no tienen que ser consecutivos; cuenta aunque mueras en la primera sala)"),
    (r"^Take (\d+) items from Angel Rooms$",
     r"Toma \1 items de Angel Rooms"),

    # Die
    (r"^Die (\d+) times$",
     r"Muere \1 veces"),
    (r"^Die in a Sacrifice Room while holding Missing Poster$",
     r"Muere en una Sacrifice Room sosteniendo Missing Poster"),
    (r"^Die to your own explosion from (.+)$",
     r"Muere por tu propia explosión de \1"),

    # Don't
    (r"^Don't pick up any hearts for (\d+) floors in a row$",
     r"No recojas ningún corazón durante \1 pisos seguidos"),

    # Take + Devil Rooms / deals
    (r"^Take (\d+) items from Devil Rooms$",
     r"Toma \1 items de Devil Rooms"),
    (r"^Take (\d+) Devil deals$",
     r"Acepta \1 Devil deals"),

    # Unlock
    (r"^Unlock all of the secrets and endings, and collect every item in the game$",
     r"Desbloquea todos los secretos y endings y recoge todos los items del juego"),
    (r"^Unlock all the other achievements and collect every item in the game$",
     r"Desbloquea el resto de logros y recoge todos los items del juego"),

    # Increase
    (r"^Increase in size (\d+) times in a single run\. Sources of increased size include \"One Makes you Larger\" pills, XI - Strength, and Magic Mushroom$",
     r"Aumenta de tamaño \1 veces en una sola run. Fuentes: pastillas \"One Makes you Larger\", XI - Strength y Magic Mushroom"),

    # Collect tears up
    (r"^Collect (\d+) \"tears up\" items or pills in one run$",
     r"Recoge \1 items o pastillas de \"tears up\" en una run"),

    # Frases sueltas
    (r"^It's complicated$",
     r"Es complicado"),
]

# --- Reemplazos de palabras dentro de la traducción ya hecha ---------------
# Se aplican después de los patrones, para términos que no se capturan.
WORD_REPLACEMENTS = [
    (" on Hard mode", " en modo Difícil"),
    (" on Normal mode", " en modo Normal"),
    (" Hard mode", " modo Difícil"),
]


def translate(unlock: str) -> str:
    original = unlock
    for pat, repl in PATTERNS:
        new = re.sub(pat, repl, unlock)
        if new != unlock:
            unlock = new
            break
    for src, dst in WORD_REPLACEMENTS:
        unlock = unlock.replace(src, dst)
    return unlock


def main():
    html = HTML.read_text(encoding="utf-8")
    # Match each ACHIEVEMENTS_DATA entry line: {i:NUM,c:"CAT",n:"NAME",u:"UNLOCK"}
    pat = re.compile(
        r'(\{i:\d+,c:"[^"]+",n:"(?:[^"\\]|\\.)*",u:")((?:[^"\\]|\\.)*)("\})'
    )

    total = 0
    translated = 0
    untranslated_examples = []

    def repl(m):
        nonlocal total, translated
        prefix, unlock, suffix = m.group(1), m.group(2), m.group(3)
        # Decode JS string escapes (just for \"  and \\)
        decoded = unlock.replace('\\"', '"').replace("\\\\", "\\")
        total += 1
        new = translate(decoded)
        if new != decoded:
            translated += 1
        else:
            if len(untranslated_examples) < 30:
                untranslated_examples.append(decoded)
        # Re-encode
        encoded = new.replace("\\", "\\\\").replace('"', '\\"')
        return prefix + encoded + suffix

    new_html = pat.sub(repl, html)
    HTML.write_text(new_html, encoding="utf-8")

    print(f"Total entries: {total}")
    print(f"Translated: {translated}")
    print(f"Untranslated: {total - translated}")
    if untranslated_examples:
        print("\nExamples of untranslated:")
        for u in untranslated_examples:
            print(f"  - {u}")


if __name__ == "__main__":
    main()
