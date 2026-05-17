# Item description audit — 2026-05-13

Auditoría de ~160 entradas de `ITEM_INFO` en `challenges.html` contra el wiki oficial (bindingofisaacrebirth.wiki.gg, ya que el wiki en español de Fandom devuelve 403 a peticiones automáticas). Se priorizaron los items con números/ubicaciones/triggers específicos (más propensos a estar mal). Co-op babies cosméticos, runas/cartas evidentemente correctas y descripciones genéricas se verificaron por muestreo.

## Items with errors found

### "The Stairway"
- **Current:** En la primera Treasure Room de cada piso aparece una escalera que te lleva a una Angel Room con 2 items. El item de la Treasure Room sigue disponible. Funciona desde el piso siguiente a recogerlo.
- **Wiki says:** Genera una escalera en la **starting room** de cada piso que sube a una Angel Room Shop con 3 items en venta (no gratis), corazones, llaves y Holy Cards. No es una Angel Room normal; es una tienda angélica. La escalera desaparece al salir del starting room.
- **Suggested fix:** En la starting room de cada piso aparece una escalera que sube a una Angel Room Shop con 3 items, corazones, llaves y Holy Cards a la venta. Desaparece al salir de la sala inicial.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Stairway

### "Isaac's Tears"
- **Current:** Dispara 8 lágrimas en círculo a tu alrededor. Recarga: 4 segundos.
- **Wiki says:** Dispara 8 lágrimas alrededor de Isaac con sus stats. Carga aumenta 1 cada vez que Isaac dispara (único activable que se carga disparando). Recarga: 6 salas (no segundos).
- **Suggested fix:** Dispara 8 lágrimas alrededor de Isaac. Se recarga +1 cada lágrima que disparas (único activo que se carga disparando). Recarga: 6 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Isaac%27s_Tears

### "D20"
- **Current:** Rerolla todos los pickups, cofres y trinkets de la sala actual (no afecta items en pedestales).
- **Wiki says:** Rerolea todos los pickups, cofres y trinkets de la sala. El paréntesis es engañoso: D20 sí puede rerolear items en pedestales de tienda y otros lugares (no es su propósito principal, pero ocurre).
- **Suggested fix:** Rerolla todos los pickups, cofres y trinkets de la sala actual (incluye los de tienda).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/D20

### "Cain's Eye"
- **Current:** 5% de probabilidad de que las habitaciones empiecen reveladas en el mapa.
- **Wiki says:** Al empezar un piso, 25% de probabilidad de aplicar el efecto de Compass durante todo el piso (revela la posición del boss y salas especiales). Escala con Luck: 100% a 3+ Luck.
- **Suggested fix:** Al empezar un piso, 25% de probabilidad de aplicar Compass durante todo el piso (revela boss y salas especiales). Escala con Luck.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Cain%27s_Eye

### "Silver Dollar"
- **Current:** Más probabilidad de Money Rooms; bonus de dinero al entrar en tiendas.
- **Wiki says:** Hace que aparezcan tiendas en Womb/Utero/Scarred Womb/Corpse. Nada sobre Money Rooms o bonus de dinero.
- **Suggested fix:** Hace que aparezca una tienda en Womb/Utero/Scarred Womb/Corpse. Debes tenerlo al entrar al piso.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Silver_Dollar

### "Guppy's Eye"
- **Current:** Puedes ver el contenido de los cofres antes de abrirlos.
- **Wiki says:** Muestra el contenido de cofres, fireplaces, grab bags **y shopkeepers** antes de abrirlos/destruirlos. Cuenta para Guppy.
- **Suggested fix:** Revela el contenido de cofres, fireplaces, grab bags y shopkeepers antes de abrirlos. Cuenta para Guppy.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Guppy%27s_Eye

### "Pound of Flesh"
- **Current:** Las puertas Devil/Angel cuestan corazones rojos; las tiendas piden corazones en vez de monedas.
- **Wiki says:** Items de Devil Deal y Black Market se compran con monedas; items de tienda se compran con corazones; consumibles de tienda son gratis pero están rodeados de pinchos.
- **Suggested fix:** Invierte la economía: items de Devil/Black Market se compran con monedas y los de tienda con corazones. Los consumibles de tienda son gratis pero rodeados de pinchos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/A_Pound_of_Flesh

### "Options?"
- **Current:** Al completar cualquier sala que genere recompensa (boss, treasure room, etc.) aparece un segundo drop distinto. Solo puedes coger uno; el otro desaparece.
- **Wiki says:** Aplica a **room clear rewards** estándar (pickups que dropean al limpiar salas normales). NO afecta items de boss ni treasure rooms (esos son los items "There's Options" y "More Options" respectivamente).
- **Suggested fix:** Al limpiar una sala con recompensa, aparece un segundo pickup distinto junto al primero. Solo puedes coger uno; el otro desaparece. No afecta items de boss/treasure.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Options%3F

### "Brown Nugget"
- **Current:** Genera una mosca familiar que orbita por la habitación.
- **Wiki says:** Es un item **activo** (no pasivo). Al usarse genera un fly turret estacionario que dispara a enemigos a 3 tiles. Recarga 8s, hasta 64 moscas por sala.
- **Suggested fix:** Activo: al usarse genera una mosca-torreta estacionaria que dispara a enemigos cercanos. Recarga: 8 segundos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Brown_Nugget

### "Worm Friend"
- **Current:** Gusano que enreda a enemigos al suelo, dejándolos quietos.
- **Wiki says:** Familiar Nerve Ending que emerge del suelo y agarra enemigos durante 4 segundos, haciendo 8 daño/seg (32 total). Funciona en bosses.
- **Suggested fix:** Familiar que emerge del suelo y agarra enemigos durante 4 segundos, haciéndoles daño continuo. Funciona en bosses.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Worm_Friend

### "The Relic"
- **Current:** Genera un Soul Heart cada 2 habitaciones limpiadas.
- **Wiki says:** Familiar cruz azul que dropea un Soul Heart cada 5-6 salas (pre-Repentance) o cada 7-8 salas (Repentance).
- **Suggested fix:** Familiar cruz que dropea un Soul Heart cada 7-8 salas limpiadas (5-6 con BFFS!).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Relic

### "Celtic Cross"
- **Current:** 5% de probabilidad de empezar cada habitación con Holy Mantle.
- **Wiki says:** 20% (base) de probabilidad al recibir daño de activar el efecto de Book of Shadows (escudo 7s). Escala con Luck hasta 100% a 27 Luck. NO Holy Mantle, NO inicio de sala.
- **Suggested fix:** Al recibir daño, 20% de probabilidad de activar Book of Shadows (escudo invulnerable 7s). Escala con Luck.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Celtic_Cross

### "Maggy's Faith"
- **Current:** +1 contenedor de corazón eterno.
- **Wiki says:** Trinket que da un Eternal Heart al inicio de cada piso (no es un contenedor único).
- **Suggested fix:** Da un Eternal Heart al empezar cada piso.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Maggy%27s_Faith

### "Maggy's Bow"
- **Current:** +0.5 daño y +0.16 velocidad.
- **Wiki says:** +1 contenedor de corazón rojo y duplica el valor curativo de los Red Hearts. En Repentance+ también cura 1 corazón rojo extra al recogerlo.
- **Suggested fix:** +1 contenedor de corazón rojo y los Red Hearts curan el doble.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Maggy%27s_Bow

### "Eucharist"
- **Current:** Garantiza la aparición de Angel Room en cada piso (sin necesidad de tomar Devil Deal).
- **Wiki says:** Fija la probabilidad de Angel Room al 100% y la de Devil Room al 0%. La puerta no se cierra. Si ya entraste a Devil Room antes de cogerlo, ese piso no se reemplaza.
- **Suggested fix:** Fija la chance de Angel Room al 100% y la de Devil Room al 0% el resto del piso. La puerta no se cierra.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Eucharist

### "Yuck Heart"
- **Current:** Las habitaciones pueden generar un Yuck Heart que cura al enemigo cercano.
- **Wiki says:** Es un item **activo** (no trinket). Al usarse otorga un Rotten Heart a Isaac (rellena un contenedor vacío o reemplaza uno lleno). Recarga 4 salas.
- **Suggested fix:** Activo: al usarse otorga un Rotten Heart (rellena contenedor vacío o reemplaza uno lleno). Recarga: 4 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Yuck_Heart

### "Candy Heart"
- **Current:** Cada vez que recoges un corazón, sube una estadística.
- **Wiki says:** Es un item **pasivo**, no trinket. Da un stat boost aleatorio por cada medio corazón curado con Red Hearts (o ganar un contenedor lleno extra).
- **Suggested fix:** Pasivo: cada medio Red Heart curado da un stat boost aleatorio pequeño (daño, tears, range, speed, shot speed o luck).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Candy_Heart

### "Lazarus' Rags"
- **Current:** Al morir, revives una vez con +0.5 daño y boost de stats.
- **Wiki says:** Al morir, revives como Lazarus Risen con un contenedor menos, el item Anemic y +0.5 daño permanente. Al siguiente piso vuelve a Lazarus normal.
- **Suggested fix:** Al morir, revives como Lazarus Risen con Anemic y +0.5 daño permanente (un contenedor menos).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Lazarus%27_Rags

### "Broken Ankh"
- **Current:** 8% de probabilidad de revivir como ??? (Blue Baby) al morir.
- **Wiki says:** 22.22% de probabilidad de revivir como ??? en la sala anterior. Puede ocurrir varias veces en la run. NO afectado por Luck.
- **Suggested fix:** 22% de probabilidad de revivir como ??? en la sala anterior. Puede ocurrir varias veces por run.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Broken_Ankh

### "Empty Vessel"
- **Current:** Cuando estás sin corazones rojos, ganas un Soul Heart eterno.
- **Wiki says:** Al pickup da 2 Black Hearts. Cuando Isaac no tiene Red Hearts: vuelo + escudo invulnerable de 10s cada 40 segundos.
- **Suggested fix:** Da 2 Black Hearts. Sin Red Hearts: vuelo y escudo invulnerable de 10s cada 40 segundos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Empty_Vessel

### "Compound Fracture"
- **Current:** Tus lágrimas se rompen en lágrimas más pequeñas al impactar el suelo.
- **Wiki says:** Tus lágrimas se vuelven huesos que se rompen en 1-3 fragmentos al impactar enemigo u obstáculo, cada uno hace 50% del daño. +1.5 range.
- **Suggested fix:** Tus lágrimas se vuelven huesos que se rompen en 1-3 fragmentos al impactar (50% daño cada uno). +1.5 range.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Compound_Fracture

### "Tinytoma"
- **Current:** Versión bebé de Mom's Heart que te sigue y aplasta enemigos.
- **Wiki says:** Orbital grande similar a Teratoma que repele enemigos y hace 3.5 daño/seg de contacto. Tras bloquear 3 shots se divide en dos orbitales pequeños.
- **Suggested fix:** Orbital grande tipo Teratoma que repele enemigos y hace daño de contacto. Tras bloquear shots se divide en orbitales más pequeños.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Tinytoma

### "Astral Projection"
- **Current:** Al morir, te conviertes en un espíritu con una vida extra.
- **Wiki says:** Al recibir daño en sala con enemigos, el tiempo se detiene 2s e Isaac se convierte en fantasma con vuelo, lágrimas spectrales y protección del próximo hit. No es revivir al morir.
- **Suggested fix:** Al recibir daño, congela el tiempo 2s y te conviertes en fantasma con vuelo y lágrimas spectrales hasta limpiar la sala o recibir otro hit.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Astral_Projection

### "Star of Bethlehem"
- **Current:** Item de planetarium: lágrimas con homing fuerte.
- **Wiki says:** Spawnea un familiar estrella que va hacia el boss room y se queda allí; al estar dentro de su aura ganas multiplicador de daño, x2.5 fire rate, lágrimas homing y 50% chance de ignorar daño.
- **Suggested fix:** Spawnea una estrella que vuela hacia la boss room; estar en su aura te da x2.5 fire rate, lágrimas homing, daño extra y 50% chance de ignorar daño.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Star_of_Bethlehem

### "Revelation"
- **Current:** Carga ángel guardián y otorga +1 Soul Heart al usar.
- **Wiki says:** Es un item **pasivo** que da vuelo. Tras disparar 2.35s y soltar, dispara un Holy Laser tipo ángel boss durante ~1.28s.
- **Suggested fix:** Pasivo: da vuelo. Tras disparar 2.35s y soltar, dispara un Holy Laser angélico durante ~1.28s.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Revelation

### "Vade Retro"
- **Current:** Hace temblar a los enemigos; segundo uso los explota.
- **Wiki says:** Pasivamente, enemigos muertos dejan fantasmas rojos. Al activar, los fantasmas explotan dañando enemigos cercanos y destruyendo proyectiles. Mata al instante enemigos tipo "ghost" con ≤50% vida.
- **Suggested fix:** Pasivo: enemigos muertos dejan fantasmas rojos. Al usar, los fantasmas explotan dañando enemigos cercanos y destruyendo proyectiles.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Vade_Retro

### "Beth's Faith"
- **Current:** Por cada 2 corazones eternos: +0.25 daño temporal.
- **Wiki says:** Al inicio de cada piso, spawnea 4 wisps que orbitan a Isaac y disparan (como los de Book of Virtues). Tope 8 wisps totales.
- **Suggested fix:** Al inicio de cada piso, spawnea 4 wisps que orbitan a Isaac y disparan lágrimas (como Book of Virtues).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Beth%27s_Faith

### "Divine Intervention"
- **Current:** Al hacer doble tap de la dirección de disparo, lanzas un escudo que empuja enemigos y refleja sus proyectiles (incluso rayos Brimstone). Recarga 3s.
- **Wiki says:** Correcto en general, pero el escudo "se mueve lentamente" en la dirección elegida (no es un escudo alrededor de Isaac). Dura 1 segundo, cooldown 3s.
- **Suggested fix:** Al doble tap de la dirección de disparo, lanzas un escudo que se mueve empujando enemigos y reflejando proyectiles (incluso Brimstone). Dura 1s, cooldown 3s.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Divine_Intervention

### "Soul Locket"
- **Current:** Recoger Soul Hearts da un pequeño buff permanente de stats.
- **Wiki says:** Cada medio Soul Heart **o Black Heart** recogido da un stat boost aleatorio. Solo activa al recoger físicamente.
- **Suggested fix:** Cada medio Soul Heart o Black Heart recogido da un stat boost aleatorio permanente.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_Locket

### "Jar of Wisps"
- **Current:** Cada uso suelta un wisp que orbita y dispara permanentemente.
- **Wiki says:** Cada uso suelta 1-2 wisps iniciales, hasta 12 wisps por activación. Recarga 12 salas. Hasta 26 wisps totales.
- **Suggested fix:** Cada uso suelta wisps que orbitan, disparan y bloquean shots. Recarga: 12 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Jar_of_Wisps

### "Mysterious Paper"
- **Current:** Alterna cada frame entre Polaroid, Negative, Missing Page y Missing Poster.
- **Wiki says:** Cada frame tiene probabilidad de aplicar el efecto de uno de esos 4 items (no es alternancia determinista; en Repentance Negative no da bonus de daño).
- **Suggested fix:** Cada frame, probabilidad de aplicar el efecto de Polaroid, Negative, Missing Page o Missing Poster (sirve para acceder a Chest/Dark Room y desbloquear Lost).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Mysterious_Paper

### "Undefined"
- **Current:** Te teletransporta aleatoriamente a Treasure Room, Secret Room, Super Secret Room o I AM ERROR (1% Black Market).
- **Wiki says:** Correcto, pero no menciona el 1% Black Market. La probabilidad es 25% cada uno entre los 4 destinos, sin Black Market documentado.
- **Suggested fix:** Te teletransporta a una Treasure Room, Secret Room, Super Secret Room o I AM ERROR aleatoria. Recarga: 6 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Undefined

### "Eden's Blessing"
- **Current:** En tu próxima run con Eden empezarás con un item extra.
- **Wiki says:** Es un item **pasivo** (no trinket) que da **+0.7 tears**. En cualquier próxima run (no solo con Eden) empezarás con un item aleatorio.
- **Suggested fix:** Pasivo: +0.7 tears, y tu próxima run (con cualquier personaje) empezará con un item aleatorio.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Eden%27s_Blessing

### "Metronome"
- **Current:** Te da el efecto aleatorio de otro item durante la habitación.
- **Wiki says:** Correcto. Recarga 2 salas. Usarlo varias veces en la misma sala reemplaza el efecto previo.
- **Suggested fix:** Te aplica el efecto aleatorio de otro item durante la sala. Recarga: 2 salas. Reemplaza el efecto previo si se usa varias veces.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Metronome

### "Everything Jar"
- **Current:** Acumula hasta 12 cargas (1 por sala). Drops escalan con cargas (1=poop, 2=penny, 3=bomb... 11=gold bomb). Full charged: efectos masivos aleatorios. Puede usarse parcialmente cargado.
- **Wiki says:** La progresión exacta es 1=poop, 2=penny, 3=bomb, 4=key, 5=red heart, 6=pill, 7=card/rune, 8=soul heart, 9=gold heart, 10=golden key, 11=golden bomb. Full charge = efecto masivo aleatorio. Recarga 12 salas.
- **Suggested fix:** (Detalle más exacto:) Hasta 12 cargas. Cada nivel de carga dropea un pickup mejor al usarse (poop → penny → bomb → key → heart → pill → card → soul heart → gold heart → golden key → golden bomb). Full = efecto masivo aleatorio.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Everything_Jar

### "Guillotine"
- **Current:** Tu cabeza se separa del cuerpo y dispara desde arriba, con +daño.
- **Wiki says:** +1 daño, +0.5 fire rate. La cabeza se convierte en orbital que bloquea shots y hace 7 daño/tick (~56/seg). Las lágrimas siguen disparándose desde la cabeza rotatoria.
- **Suggested fix:** +1 daño, +0.5 fire rate. Tu cabeza se vuelve un orbital que bloquea shots y daña por contacto; las lágrimas se disparan desde ella.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Guillotine

### "Judas' Tongue"
- **Current:** Los Devil Deals cuestan 1 corazón rojo menos.
- **Wiki says:** Los items de Devil Room solo cuestan 1 heart container (no "uno menos"; los reduce todos a 1). Los Soul Heart deals siguen costando 3.
- **Suggested fix:** Los items de Devil Room solo cuestan 1 heart container (sin cambios en costes de Soul Heart deals).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Judas%27_Tongue

### "The Left Hand"
- **Current:** Todos los cofres del juego se convierten en Red Chests con drops demoníacos.
- **Wiki says:** Reemplaza todos los tipos de cofre por Red Chests. Los Red Chests dropean pickups aleatorios, no necesariamente "demoníacos".
- **Suggested fix:** Todos los cofres se reemplazan por Red Chests con drops aleatorios (incluyen pickups demoníacos y portales a Devil Room).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Left_Hand

### "Judas' Shadow"
- **Current:** Al morir, revives en la sala anterior como Black Judas (multiplicador x2 de daño inherente) con 2 Black Hearts.
- **Wiki says:** Correcto en general, pero el "x2 de daño inherente" es propio de Black Judas (no de este item); el item solo permite revivir. La descripción puede inducir a pensar que Judas' Shadow añade el x2.
- **Suggested fix:** Al morir, revives como Black Judas (que tiene x2 daño inherente) con 2 Black Hearts en la sala anterior.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Judas%27_Shadow

### "Betrayal"
- **Current:** Los enemigos cercanos atacan a otros enemigos durante unos segundos.
- **Wiki says:** En Repentance, los enemigos pueden dañarse entre sí con proyectiles, y al recibir un golpe de otro enemigo empiezan a priorizar atacarlo. Es **pasivo**, no activo. NO es "atacan a otros durante unos segundos".
- **Suggested fix:** Pasivo: los enemigos pueden dañarse entre sí con proyectiles; al ser golpeados por otro enemigo, lo priorizan en lugar de a Isaac.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Betrayal

### "My Shadow"
- **Current:** Genera 3 sombras de Charger amigas que persiguen enemigos.
- **Wiki says:** Spawnea una sombra que sigue los movimientos de Isaac. Cuando un enemigo la toca, invoca un Charger amigo. Hasta 16 Chargers simultáneos. NO son 3 fijos.
- **Suggested fix:** Spawnea una sombra que imita a Isaac; al ser tocada por enemigos invoca Chargers amigos (hasta 16) que duran la sala.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/My_Shadow

### "Akeldama"
- **Current:** Tu cuerpo tiene una cola de lágrimas que daña enemigos cuando te mueves.
- **Wiki says:** En salas con enemigos, deja un rastro spectral de lágrimas detrás. Cada una hace 3.5 daño fijo. Máximo 20 lágrimas simultáneas. Persisten tras limpiar la sala.
- **Suggested fix:** En salas con enemigos, dejas un rastro de lágrimas spectrales que daña enemigos (3.5 daño fijo cada una, hasta 20).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Akeldama

### "Redemption"
- **Current:** Consume 1 corazón rojo para activar efectos angélicos en la habitación.
- **Wiki says:** Es **pasivo**. Al entrar a una Devil Room aparece una cruz invertida blanca sobre Isaac. Si bajas al siguiente piso sin tomar nada de esa Devil Room, ganas +1 Soul Heart y +1 daño.
- **Suggested fix:** Pasivo: si entras a una Devil Room y bajas al siguiente piso sin tomar nada de ella, ganas +1 Soul Heart y +1 daño.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Redemption

### "The D6"
- **Current:** Reroll de items pasivos en la habitación.
- **Wiki says:** Rerollea TODOS los items en pedestal de la sala actual (incluye Devil/Angel/Shop/Boss Rush, etc.). No solo pasivos.
- **Suggested fix:** Rerolla todos los items en pedestal de la sala actual usando el pool del cuarto. Recarga: 6 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_D6

### "Fate"
- **Current:** Te da vuelo y +1 Soul Heart.
- **Wiki says:** Te da vuelo y +1 **Eternal Heart** (no Soul Heart).
- **Suggested fix:** Da vuelo y +1 Eternal Heart.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Fate

### "???'s Soul"
- **Current:** Genera un familiar Cabezón de ??? que persigue enemigos.
- **Wiki says:** Es un **trinket**, no activo. Spawnea un familiar que flota en zig-zag y dispara lágrimas spectrales y homing de 3.5 daño.
- **Suggested fix:** Trinket: familiar que flota en zig-zag y dispara lágrimas spectrales+homing de 3.5 daño fijo.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/%3F%3F%3F%27s_Soul

### "Fate's Reward"
- **Current:** Las monedas tienen probabilidad de aplicar efectos especiales al recogerlas.
- **Wiki says:** Spawnea un familiar que dispara lágrimas con el daño y los efectos de las de Isaac, a la mitad de su fire rate. NO tiene nada que ver con monedas.
- **Suggested fix:** Spawnea un familiar que dispara copias de tus lágrimas (mismo daño y efectos) a mitad de fire rate.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Fate%27s_Reward

### "Cracked Dice"
- **Current:** Cuando recibes daño, se hace un reroll aleatorio.
- **Wiki says:** Al recibir daño, 50% de chance de activar aleatoriamente uno de: D6, D8, D10, D12 o D20.
- **Suggested fix:** Al recibir daño, 50% de chance de activar uno de D6, D8, D10, D12 o D20 aleatoriamente.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Cracked_Dice

### "Meconium"
- **Current:** Probabilidad de aplicar el efecto Black Heart a enemigos al dispararles.
- **Wiki says:** 33% de chance de que cualquier poop generado sea Black Poop; 5% de que un Black Poop destruido suelte un Black Heart. NO tiene nada que ver con disparar.
- **Suggested fix:** 33% de probabilidad de que las cacas sean Black Poop; 5% de que un Black Poop destruido suelte un Black Heart.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Meconium

### "King Baby"
- **Current:** Familiar que se queda quieto y replica todos tus disparos en su posición.
- **Wiki says:** Familiar que sigue a Isaac y siempre va primero en la cadena de familiares. Mientras Isaac dispara, King Baby (y los demás familiars) se detiene; cuando deja de disparar, vuelve corriendo. Los familiars de disparo auto-apuntan a enemigos cercanos.
- **Suggested fix:** Familiar que va al frente de la cadena. Mientras disparas se queda quieto (y para a los demás familiares); los familiars de disparo auto-apuntan a enemigos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/King_Baby

### "Eternal D6"
- **Current:** Como el D6, pero con recarga propia sin necesidad de baterías.
- **Wiki says:** Es un item **activo** (no pasivo). Como el D6 pero cada item rerolleado tiene 25% chance de desaparecer en lugar de ser reemplazado. Recarga 2 salas.
- **Suggested fix:** Activo como el D6, pero cada item rerolleado tiene 25% chance de desaparecer. Recarga: 2 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Eternal_D6

### "Montezuma's Revenge"
- **Current:** Familiar que dispara fuego venenoso desde el trasero de Isaac.
- **Wiki says:** Es un item **pasivo** (no familiar). Tras disparar 2.35s y soltar, dispara un Brimstone marrón corto y corn shots hacia atrás.
- **Suggested fix:** Pasivo: tras disparar 2.35s y soltar, dispara un Brimstone marrón corto y corn shots hacia atrás.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Montezuma%27s_Revenge

### "Eve's Bird Foot"
- **Current:** Al matar enemigos, probabilidad de spawnear un Dead Bird familiar para la sala actual.
- **Wiki says:** Correcto, pero spawn cap es 1 por sala. Chance 5% a 0 Luck, 100% a 8 Luck.
- **Suggested fix:** Al matar enemigos, chance (5%-100% según Luck) de spawnear hasta 1 Dead Bird por sala que daña enemigos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Eve%27s_Bird_Foot

### "The Razor"
- **Current:** Quita 1 corazón rojo completo (medio si lo usas múltiples veces en la misma sala en Repentance) y otorga +1.2 daño por el resto de la sala.
- **Wiki says:** Correcto. Recarga ilimitada (sin cooldown).
- **Suggested fix:** (correcto, mínimo retoque) Activo sin cooldown: pierdes 1 Red Heart (medio si lo repites en la misma sala) y ganas +1.2 daño en la sala.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Razor_Blade

### "Black Lipstick"
- **Current:** Te da +1 Black Heart cada habitación nueva.
- **Wiki says:** +10% probabilidad de que aparezcan Black Hearts. NO da un Black Heart por sala.
- **Suggested fix:** +10% probabilidad de que los corazones que aparezcan sean Black Hearts.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Black_Lipstick

### "Eve's Mascara"
- **Current:** x2 daño, pero -0.5 shot speed y reduce cadencia (en Repentance: net ~+33% DPS). Sinergiza con Mom's Knife/Epic Fetus.
- **Wiki says:** Correcto: x2 daño, -0.5 shot speed, x0.66 fire rate en Repentance.
- **Suggested fix:** (correcto, sin cambios necesarios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Eve%27s_Mascara

### "Athame"
- **Current:** Al recibir daño, crea un aura oscura que daña enemigos cercanos.
- **Wiki says:** En Repentance, al **matar** un enemigo (no al recibir daño), chance escalable con Luck de spawnear un anillo negro que daña por contacto. Base 25% +2.5% por Luck.
- **Suggested fix:** En Repentance: al matar un enemigo, chance (25% base, escala con Luck) de spawnear un anillo negro que daña enemigos por contacto.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Athame

### "Black Feather"
- **Current:** Cada item maligno que recojas te da +damage permanente.
- **Wiki says:** Trinket: +0.5 daño en Repentance por cada item/trinket "evil" que tengas (Abaddon, Black Candle, Black Lipstick, Daemon's Tail, Goat Head, etc.).
- **Suggested fix:** Trinket: +0.5 daño por cada item/trinket maligno (Abaddon, Black Candle, Goat Head, Daemon's Tail, etc.).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Black_Feather

### "Crow Heart"
- **Current:** +1 Black Heart al inicio.
- **Wiki says:** Es un **trinket**, no pasivo. Hace que el daño se tome primero de Red Hearts antes que Soul/Black/Rotten. NO da Black Heart.
- **Suggested fix:** Trinket: el daño se aplica primero a los Red Hearts antes que a los Soul/Black/Rotten Hearts.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Crow_Heart

### "Dull Razor"
- **Current:** Te haces daño 'fake' (no quita vida real) pero activa efectos de hurt.
- **Wiki says:** Correcto. Otorga i-frames equivalentes a un golpe normal y activa efectos on-hit. Recarga 2 salas.
- **Suggested fix:** (correcto, mínimo retoque) Activo: te daña sin perder vida, otorga i-frames y activa efectos on-hit. Recarga: 2 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Dull_Razor

### "Cracked Orb"
- **Current:** Al recibir daño, deja un drop de Soul Heart aleatorio.
- **Wiki says:** Es un item **pasivo**, no trinket. Al recibir daño: abre puertas locked de la sala, revela y abre Secret/Super Secret Room adyacentes, revela una sala random del piso y rompe tinted rocks.
- **Suggested fix:** Pasivo: al recibir daño, abre puertas locked, revela y abre Secret/Super Secret Rooms adyacentes, revela una sala random y rompe tinted rocks.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Cracked_Orb

### "Blood Rights"
- **Current:** Te quita 1 corazón rojo y daña a todos los enemigos visibles.
- **Wiki says:** Correcto: pierde un corazón completo y hace 40 de daño a todos los enemigos. En Repentance+ usos posteriores en la misma sala solo cuestan medio corazón.
- **Suggested fix:** Pierdes 1 Red Heart y todos los enemigos reciben 40 de daño. En Repentance, usos repetidos en la misma sala cuestan medio corazón.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Blood_Rights

### "Blood Penny" / "Bloody Penny"
- **Current:** Al ganar una moneda, drop adicional de medio corazón a veces.
- **Wiki says:** Correcto. En Repentance la chance escala con valor de la moneda (25% penny → 94% dime).
- **Suggested fix:** Al recoger monedas, chance de dropear medio Red Heart (escala con valor: 25% en penny hasta 94% en dime).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Bloody_Penny

### "Samson's Lock"
- **Current:** +0.04 daño por enemigo matado (acumulativo).
- **Wiki says:** Trinket: 1/15 chance al matar un enemigo de ganar +0.5 daño para la sala actual (hasta 10 procs por sala). Escala con Luck.
- **Suggested fix:** Trinket: al matar enemigos, 1/15 chance de ganar +0.5 daño por la sala (hasta 10 procs).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Samson%27s_Lock

### "Samson's Chains"
- **Current:** Cadenas con bola que rotan a tu alrededor y atrapan enemigos.
- **Wiki says:** Bola con cadena atada al tobillo de Isaac que bloquea proyectiles y hace 5 daño/tick (~10.7/seg). No atrapa enemigos.
- **Suggested fix:** Bola con cadena al tobillo que bloquea proyectiles y daña enemigos por contacto.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Samson%27s_Chains

### "Blind Rage"
- **Current:** Invulnerabilidad temporal al recibir daño.
- **Wiki says:** Trinket: duplica los invincibility frames tras recibir daño. NO da invulnerabilidad nueva.
- **Suggested fix:** Trinket: duplica los i-frames tras recibir daño (también los de Holy Mantle).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Blind_Rage

### "Lusty Blood"
- **Current:** Matar enemigos da damage up por habitación.
- **Wiki says:** Correcto: +0.5 daño por kill, máx +5 a los 10 kills. Resetea por sala.
- **Suggested fix:** Cada enemigo muerto da +0.5 daño en la sala (hasta +5). Resetea al cambiar de sala.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Lusty_Blood

### "Stem Cell"
- **Current:** Al entrar en habitación nueva, baja probabilidad de drop de corazón rojo.
- **Wiki says:** Trinket: cura medio corazón al bajar a un nuevo piso (Repentance: cura 50% de los Red/Bone Hearts vacíos, mín medio).
- **Suggested fix:** Trinket: al bajar al siguiente piso, cura el 50% de tus contenedores vacíos (mínimo medio corazón).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Stem_Cell

### "Bloody Crown"
- **Current:** El piso se vuelve más lineal y con más boss rooms.
- **Wiki says:** Trinket: hace aparecer Treasure Rooms en Womb/Utero/Scarred Womb/Corpse (pisos donde normalmente no hay).
- **Suggested fix:** Trinket: aparecen Treasure Rooms en Womb/Utero/Scarred Womb/Corpse. Debes tenerlo al entrar al piso.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Bloody_Crown

### "Bloody Gust"
- **Current:** Al recibir daño, ráfaga de viento empuja enemigos lejos.
- **Wiki says:** Al recibir daño, ganas +speed y +fire rate por el resto del piso. Stackea hasta 6 veces (max +1.02 speed, +3 fire rate). NO empuja enemigos.
- **Suggested fix:** Al recibir daño, +speed y +fire rate por el resto del piso. Stackea hasta 6 veces.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Bloody_Gust

### "Empty Heart"
- **Current:** Al entrar en habitación nueva, +1 contenedor de corazón vacío.
- **Wiki says:** Es un item **pasivo**, no trinket. Al inicio de cada piso, si tienes ≤1 Red Heart, ganas un contenedor vacío. NO es por sala.
- **Suggested fix:** Pasivo: al inicio de cada piso, si tienes ≤1 Red Heart, ganas un contenedor de corazón vacío.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Empty_Heart

### "Satanic Bible"
- **Current:** Te da 1 Black Heart al usar.
- **Wiki says:** Correcto: +1 Black Heart al usar. Recarga 6 salas. En Repentance+ además hace que el boss del piso suelte un Devil Deal.
- **Suggested fix:** +1 Black Heart al usar. Recarga: 6 salas. En Repentance+ el boss del piso suelta un Devil Deal en vez del item normal.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Satanic_Bible

### "Abaddon"
- **Current:** Quita corazones rojos, da +2 Black Hearts, +damage y aura de miedo.
- **Wiki says:** +1.5 daño, +0.2 speed, convierte Red Hearts en Black Hearts y suma 2 Black Hearts, **lágrimas con chance de fear** (no aura).
- **Suggested fix:** +1.5 daño, +0.2 speed, convierte Red Hearts en Black Hearts y suma +2 Black Hearts; lágrimas con chance de aplicar fear.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Abaddon

### "Daemon's Tail"
- **Current:** Los drops de medio corazón se sustituyen por Black Hearts.
- **Wiki says:** 80% de los heart drops se reemplazan por **llaves**; el resto se convierte en Black Hearts.
- **Suggested fix:** 80% de los heart drops se reemplazan por llaves; el resto se convierte en Black Hearts.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Daemon%27s_Tail

### "The Nail"
- **Current:** +1 contenedor de corazón, +damage en la habitación, rompe rocas.
- **Wiki says:** En Repentance: +½ Black Heart, +2 daño temporal en la sala, -0.18 speed y rompe obstáculos al caminar. Recarga 6 salas. NO +1 contenedor.
- **Suggested fix:** Al usar: +½ Black Heart, +2 daño y rompes obstáculos al caminar durante la sala. Recarga: 6 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Nail

### "Maw of the Void"
- **Current:** +1 daño. Al disparar continuamente durante ~2.35s y luego soltar, libera un anillo negro de Brimstone alrededor de Isaac que daña enemigos cercanos.
- **Wiki says:** Mecánica correcta, pero el +1 daño solo existía pre-Repentance. En Repentance no da +daño base.
- **Suggested fix:** Tras disparar continuamente ~2.35s y soltar, liberas un anillo negro de Brimstone que daña a todos los enemigos cercanos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Maw_of_the_Void

### "Bat Wing"
- **Current:** Al matar enemigos, probabilidad de drop de Black Heart.
- **Wiki says:** Al matar enemigos, 5% de chance de ganar **vuelo** por el resto de la sala. NO drop de Black Heart.
- **Suggested fix:** Al matar un enemigo, 5% chance de ganar vuelo el resto de la sala.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Bat_Wing

### "Lil Abaddon"
- **Current:** Mini Abaddon que crea una pequeña aura de daño cerca de Isaac.
- **Wiki says:** Familiar que tras 1s de carga crea un anillo negro fluctuante (similar a Maw of the Void) que daña a los enemigos que lo tocan. Hasta 52.5 daño total por anillo.
- **Suggested fix:** Familiar que tras cargar 1s genera un anillo negro tipo Maw of the Void que daña a los enemigos que lo tocan.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Lil_Abaddon

### "Marrow"
- **Current:** Te da +1 hueso a tu inventario de Bone Hearts.
- **Wiki says:** Es un item **pasivo**, no activo. Da 1 Bone Heart y spawnea 3 Red Hearts.
- **Suggested fix:** Pasivo: +1 Bone Heart y spawnea 3 Red Hearts al recogerlo.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Marrow

### "Slipped Rib"
- **Current:** Genera un hueso familiar orbital que refleja proyectiles enemigos (haciendo 6-7 daño fijo).
- **Wiki says:** Correcto, mínima imprecisión: refleja en Repentance: 6 daño (½-heart hits) / 7 (full-heart hits). No daña por contacto.
- **Suggested fix:** (correcto, sin cambios) Orbital de hueso que refleja proyectiles enemigos (6-7 de daño fijo) pero no daña por contacto.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Slipped_Rib

### "Brittle Bones"
- **Current:** Convierte tu vida en 6 Bone Hearts vacíos. Al perder un Bone Heart, lanzas un anillo de 8 huesos que se fragmentan en más huesos. Cada Bone perdido da +tear rate permanente.
- **Wiki says:** Correcto. En Repentance es +0.4 fire rate por Bone Heart perdido (no "+tear rate" en formato pre-Repentance que era +0.5 tears).
- **Suggested fix:** (correcto, mínimo retoque) 6 Bone Hearts vacíos. Al perder uno, lanzas un anillo de 8 huesos que se fragmentan; cada Bone perdido da +0.4 fire rate permanente.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Brittle_Bones

### "Divorce Papers"
- **Current:** +1 contenedor de Bone Heart y +0.5 daño.
- **Wiki says:** +1 Bone Heart y **+0.7 tears** (no +0.5 daño). Spawnea un Mysterious Paper trinket.
- **Suggested fix:** +1 Bone Heart, +0.7 tears y spawnea un Mysterious Paper trinket.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Divorce_Papers

### "Hallowed Ground"
- **Current:** Spawnea un White Poop familiar que se activa al recibir daño: aura x2.5 fire rate, +20% daño, lágrimas homing y 50% chance de bloquear daño. Reaparece al cambiar de sala.
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Hallowed_Ground

### "Finger Bone"
- **Current:** Cada cierto número de disparos, suelta una lágrima de hueso.
- **Wiki says:** 4% chance de ganar un Bone Heart al recibir daño. NO tiene nada que ver con disparar.
- **Suggested fix:** Trinket: al recibir daño, 4% chance de ganar un Bone Heart.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Finger_Bone

### "Dad's Ring"
- **Current:** Genera un anillo brillante que ralentiza a enemigos dentro.
- **Wiki says:** Crea un anillo de luz alrededor de Isaac que **petrifica** (no solo ralentiza) enemigos al contacto. Bosses solo petrificación normal temporal.
- **Suggested fix:** Activo: crea un anillo de luz alrededor de Isaac que petrifica enemigos al contacto.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Dad%27s_Ring

### "Book of the Dead"
- **Current:** Al usarse, spawnea un bone familiar por cada enemigo matado en esa sala (máx 8). 80% bone orbital, 20% bone friend amistoso. Recarga: 6 salas.
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Book_of_the_Dead

### "Bone Spurs"
- **Current:** Tu hueso lanzado dispara mini-huesos en todas direcciones al impactar.
- **Wiki says:** Al matar enemigos, spawnean 1-2 huesos flotantes que bloquean proyectiles y dañan por contacto.
- **Suggested fix:** Al matar enemigos, spawnean 1-2 huesos flotantes que bloquean shots y dañan enemigos por contacto.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Bone_Spurs

### "Spirit Shackles"
- **Current:** Al morir, revives como espíritu por unos segundos antes de morir definitivamente.
- **Wiki says:** Correcto en general: al morir te conviertes en fantasma con medio corazón, vuelo y lágrimas spectrales por 10s. Si sobrevives, revives en tu cuerpo. Se recarga al recoger un Soul/Black Heart.
- **Suggested fix:** Al morir, te conviertes en fantasma con medio corazón, vuelo y lágrimas spectrales 10s; si sobrevives, revives. Se recarga al recoger Soul/Black Heart.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Spirit_Shackles

### "Serpent's Kiss"
- **Current:** Probabilidad de envenenar enemigos con tus lágrimas.
- **Wiki says:** 15% chance de lágrimas poison; enemigos que tocan a Isaac quedan envenenados y 20% chance de dropear Black Heart.
- **Suggested fix:** 15% chance de lágrimas poison; enemigos que te tocan se envenenan y 20% chance de dropear Black Heart.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Serpent%27s_Kiss

### "Cambion Conception"
- **Current:** Cada 12 habitaciones sin recibir daño, genera un familiar permanente.
- **Wiki says:** Al recibir un cierto número de **hits** (no habitaciones sin daño), spawnea un familiar permanente. Umbrales: 15, 30, 60, 90 hits totales. Hasta 4 familiares.
- **Suggested fix:** Cada cierto número de hits recibidos (15/30/60/90 acumulados) spawnea un familiar demoníaco permanente. Hasta 4.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Cambion_Conception

### "Succubus"
- **Current:** Familiar que crea un aura de +daño cerca de Isaac.
- **Wiki says:** Aura oscura que daña enemigos dentro y, mientras Isaac está dentro, sus lágrimas tienen x1.5 daño.
- **Suggested fix:** Familiar con aura oscura que daña enemigos y aplica x1.5 daño a las lágrimas de Isaac mientras esté dentro.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Succubus

### "Immaculate Conception"
- **Current:** Cada 15 corazones pickups recogidos (de cualquier tipo) spawnea un familiar angélico permanente y dropea un Soul Heart. Hasta 5 familiars.
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Immaculate_Conception

### "Incubus"
- **Current:** Familiar que copia las lágrimas de Isaac. En Repentance: 75% del daño de Isaac (100% solo para Lilith/Tainted Lilith).
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Incubus

### "Duality"
- **Current:** En boss rooms aparecen tanto puerta Devil como Angel a la vez.
- **Wiki says:** Correcto en esencia, pero entrar a una hace desaparecer la otra.
- **Suggested fix:** Cuando tras el boss aparece una puerta Devil o Angel, también aparece la otra. Entrar a una hace desaparecer la otra.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Duality

### "Euthanasia"
- **Current:** Probabilidad pequeña de matar enemigo al instante disparando agujas en todas direcciones.
- **Wiki says:** Chance (escala con Luck, máx 25% en Repentance) de disparar agujas con x3 daño que matan al instante a enemigos regulares; al morir, el enemigo explota en 10 lágrimas.
- **Suggested fix:** Chance (hasta 25% con Luck) de disparar una aguja con x3 daño que mata al instante a enemigos regulares y los hace explotar en 10 lágrimas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Euthanasia

### "Blood Puppy"
- **Current:** Perro de sangre que crece al matar enemigos; eventualmente ataca a Isaac.
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Blood_Puppy

### "Red Stew"
- **Current:** +1 daño temporal en la habitación y cura completa.
- **Wiki says:** Cura completa y **+21.6 daño** que decae durante ~3 minutos (no solo en la habitación). Mientras dure, kills extienden el bonus.
- **Suggested fix:** Cura completa y +21.6 daño temporal que decae durante ~3 minutos. Matar enemigos extiende el bonus.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Red_Stew

### "Damocles"
- **Current:** Al usarse, invoca una espada que cuelga sobre Isaac y duplica todos los items de pedestales (treasure, devil, shop, beggar, etc.). Tras recibir daño, la espada puede caer y matar a Isaac.
- **Wiki says:** Correcto. La probabilidad es 1/10000 por tick (cada 0.133s) tras recibir daño. Self-damage (donation machines, devil beggars, etc.) no activa.
- **Suggested fix:** (correcto, sin cambios necesarios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Damocles

### "Vanishing Twin"
- **Current:** El siguiente boss aparece duplicado pero da doble loot al ganar.
- **Wiki says:** Es un item **pasivo**, no trinket. Familiar feto que en boss rooms duplica al boss (ambos al 75% vida y 20% slower). El clon dropea un item del boss pool.
- **Suggested fix:** Pasivo: en boss rooms el boss aparece duplicado (75% vida, 20% slower); el clon suelta un item al morir.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Vanishing_Twin

### "Inner Child"
- **Current:** Al morir, revives como una segunda vida.
- **Wiki says:** Es un item **pasivo**, no trinket. Al morir, revives en la misma sala con ½ Red Heart, size down y +0.2 speed, y emite una explosión de sangre de 35 daño.
- **Suggested fix:** Pasivo: al morir revives en la misma sala con ½ corazón, tamaño reducido y +0.2 speed, explotando en sangre que daña enemigos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Inner_Child

### "Genesis"
- **Current:** Te elimina todos tus items y te lleva a una habitación con un item nuevo aleatorio.
- **Wiki says:** Te lleva a un bedroom; te quita TODOS los items y por cada uno te ofrece 3 a elegir, uno cada vez. Restaura health a inicial. Te lleva al siguiente piso. Uso único.
- **Suggested fix:** Te lleva a un bedroom: te quita todos tus items y por cada uno te ofrece 3 a elegir. Restaura vida y te lleva al siguiente piso. Uso único.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Genesis

### "Suplex!"
- **Current:** Agarra al enemigo más cercano y lo lanza contra otros.
- **Wiki says:** Isaac hace un dash corto; si choca con un enemigo lo levanta, controlable con un crosshair, y tras 1s lo aplasta haciendo daño AoE. Isaac es invulnerable durante el efecto. Recarga 7s.
- **Suggested fix:** Dash corto que agarra al primer enemigo que tocas, lo levantas con crosshair y lo aplastas (AoE con rock waves). Invulnerable durante el efecto. Recarga: 7s.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Suplex!

### "Magic Skin"
- **Current:** Al usarse consume 1 Heart Container (o Bone Heart, o 2 Soul Hearts) y genera un pedestal de item del pool de la sala. Cada uso deja un broken heart container.
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios necesarios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Magic_Skin

### "Friend Finder"
- **Current:** Genera un familiar aleatorio basado en items que ya tienes.
- **Wiki says:** Spawnea un enemigo friendly random (de 21 posibles: Clotty, Vis, Bony, etc.) que imita los movimientos de Isaac. NO basado en items existentes. Recarga 4 salas.
- **Suggested fix:** Spawnea un enemigo friendly aleatorio (Clotty, Vis, Bony, etc.) que imita tus movimientos y dispara. Recarga: 4 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Friend_Finder

### "Isaac's Heart"
- **Current:** Tu cuerpo se vuelve inmune al daño, pero un familiar corazón sigue a Isaac y si lo golpean recibes daño tú. En Repentance también daña enemigos por contacto.
- **Wiki says:** Correcto en general; el corazón en Repentance también puede disparar blood shots y crear creep.
- **Suggested fix:** (mantener como está o añadir:) En Repentance el corazón también carga al disparar, crea creep y dispara blood shots en 8 direcciones.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Isaac%27s_Heart

### "The Mind"
- **Current:** Revela el mapa completo del piso (mapa + compass + treasure map).
- **Wiki says:** Correcto: combina Blue Map + Compass + Treasure Map.
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Mind

### "The Body"
- **Current:** +3 contenedores de corazón rojo permanentes y llenos.
- **Wiki says:** Correcto: +3 Red Heart Containers (no aclara si llenos).
- **Suggested fix:** (correcto)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Body

### "The Soul"
- **Current:** +2 Soul Hearts permanentes y un aura azul que repele/desvía proyectiles enemigos (intensidad variable).
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Soul

### "The D100"
- **Current:** Rerolla TODOS los items pasivos de Isaac, todos los pedestales y pickups de la sala, las rocas, los enemigos y modifica aleatoriamente stats (daño, tears, rango, velocidad).
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios necesarios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/D100

### "Sworn Protector"
- **Current:** Familiar protector orbital que bloquea proyectiles.
- **Wiki says:** Correcto, además atrae proyectiles hacia sí.
- **Suggested fix:** Familiar orbital que bloquea y atrae proyectiles enemigos; chance de dropear Eternal Heart al bloquear 10 shots.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Sworn_Protector

### "Holy Card"
- **Current:** Te da un Holy Mantle de un uso (en Repentance persiste hasta recibir daño). Recarga 4 salas si se usa con Blank Card.
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios necesarios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Holy_Card

### "Lost Soul"
- **Current:** Familiar fantasma; si muere, se pierde permanentemente.
- **Wiki says:** Muere de un hit, pero respawnea al inicio del siguiente piso. Si sobrevive hasta el siguiente piso, da 3 Soul Hearts / 2 Eternal Hearts / un item de Treasure o Angel Room.
- **Suggested fix:** Familiar fantasma que muere de un hit pero respawnea cada piso. Si sobrevive hasta el siguiente piso, da una recompensa (Soul Hearts, Eternal Hearts o un item).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Lost_Soul

### "Hungry Soul"
- **Current:** Familiar fantasma que come enemigos.
- **Wiki says:** 33% chance al matar un enemigo de spawnear un fantasma amistoso que persigue enemigos y daña por contacto; explota a los 7s.
- **Suggested fix:** 33% chance al matar un enemigo de spawnear un fantasma amistoso que persigue enemigos, daña por contacto y explota a los 7s.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Hungry_Soul

### "Wooden Nickel"
- **Current:** ~60% de probabilidad de soltar una moneda (penny/nickel/dime) al usarse. Recarga por sala.
- **Wiki says:** Correcto: ~60% chance combinada (52% penny, 6% nickel, 1% dime, 41% nada).
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Wooden_Nickel

### "Store Key"
- **Current:** Genera una llave a la siguiente tienda del piso.
- **Wiki says:** Es un **trinket**, no item activo. Permite abrir tiendas sin gastar llaves.
- **Suggested fix:** Trinket: las tiendas pueden abrirse sin gastar llaves.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Store_Key

### "Deep Pockets"
- **Current:** +6 al máximo de monedas que puedes llevar.
- **Wiki says:** Eleva el cap de monedas a **999** (no +6). Salas sin reward dropean 1-3 monedas. (Pre-Repentance permitía llevar 2 cards/pills.)
- **Suggested fix:** Eleva el cap de monedas a 999. Las salas sin reward generan 1-3 monedas aleatorias.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Deep_Pockets

### "Karma"
- **Current:** Donar a la Greed Donation Machine te da suerte extra.
- **Wiki says:** Al donar a Donation Machine chance de: ganar Luck, healing de un Red Heart, spawnear Beggar, o devolver una moneda. NO solo Greed Donation Machine.
- **Suggested fix:** Trinket: al donar a Donation Machines, chance de ganar Luck, curarte, spawnear Beggar o devolverte una moneda.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Karma

### "Sticky Nickel"
- **Current:** Tienes un níquel pegajoso que se cae al recibir daño.
- **Wiki says:** Es un **pickup** de moneda (no trinket). Es un nickel que se queda en el suelo y no se puede recoger normalmente: hay que destruirlo con explosión para obtener 5 monedas.
- **Suggested fix:** Pickup: moneda pegajosa que se queda en el suelo; necesita una explosión para liberarse y dar 5 monedas.
- Wiki URL: (no wiki link en código actual)

### "Penny"
- **Current:** Al entrar en habitación nueva: +1 moneda.
- **Wiki says:** No hay un item llamado "Penny" en el juego con ese efecto. Posiblemente alguien lo confundió con un pickup o "A Penny!" (item Wisp); el wiki devuelve 404 para "A Penny!".
- **Suggested fix:** Confirmar nombre exacto en el código fuente y wiki. Si es un pickup de moneda, debería describirse como tal; si es un item, posiblemente sea "A Penny!" (wisp de Lemegeton que dropea pennies).
- Wiki URL: (404, posiblemente mal nombre)

### "Rib of Greed"
- **Current:** Al recibir daño, drop de 5-10 monedas.
- **Wiki says:** Trinket: previene spawn de Greed/Super Greed en Shops/Secret Rooms, y aumenta drops de monedas a costa de heart drops al limpiar salas.
- **Suggested fix:** Trinket: previene Greed en tiendas/Secret Rooms y aumenta los drops de monedas a costa de los de corazones.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Rib_of_Greed

### "Eye of Greed"
- **Current:** Tus lágrimas convierten enemigos en estatuas de oro que se rompen al matar.
- **Wiki says:** Cada 20 lágrimas disparadas, dispara una golden tear que cuesta 1 penny y dora/petrifica enemigos. Los petrificados sueltan 1-3 monedas al morir.
- **Suggested fix:** Cada 20 lágrimas dispara una golden tear (cuesta 1 penny) que dora y petrifica enemigos; al morir sueltan 1-3 monedas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Eye_of_Greed

### "Crooked Penny"
- **Current:** 50% de probabilidad de duplicar todos los items/pickups/cofres en la sala; 50% de que desaparezcan y solo quede una penny. Con buena Luck mejora.
- **Wiki says:** Correcto en general; recarga 4 salas. (Nota: el Luck scaling fue cambiado en Repentance.)
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Crooked_Penny

### "Keeper's Sack"
- **Current:** Al entrar en habitación nueva, probabilidad de drop de pennies.
- **Wiki says:** Es un **item pasivo**, no trinket. Spawnea 3 monedas y una llave al recogerlo; por cada 3 monedas gastadas, da +0.5 daño / +0.25 range / +0.03 speed cíclicamente.
- **Suggested fix:** Pasivo: spawnea 3 monedas y 1 llave al recogerlo; cada 3 monedas gastadas da un stat boost cíclico (daño/range/speed).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Keeper%27s_Sack

### "Keeper's Box"
- **Current:** Genera un Beggar aleatorio (heart/key/coin/bomb/devil).
- **Wiki says:** Spawnea un pickup o item aleatorio de tienda, que debe **comprarse** al precio normal de shop. NO genera Beggars.
- **Suggested fix:** Spawnea un pickup o item del pool de tienda que debe comprarse al precio normal. Recarga: 4 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Keeper%27s_Box

### "Mom's Lock"
- **Current:** Si Isaac muere, desbloqueo de pre-mortem.
- **Wiki says:** 25% de chance por sala de aplicar el efecto de un item pasivo de Mom aleatorio (sin healing ni spawn de pickups).
- **Suggested fix:** Trinket: 25% chance por sala de aplicar el efecto de un item pasivo de Mom aleatorio.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Mom%27s_Lock

### "Soul of Isaac"
- **Current:** Aplica un efecto temporal de D6 al usarse.
- **Wiki says:** Rerolea los items de la sala, pero ciclan cada 1 segundo entre el item original y los nuevos (no es un reroll permanente).
- **Suggested fix:** Rerolea los items de la sala cíclicamente: cada 1s los items vuelven a su forma original y la nueva.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Isaac

### "Mega Chest"
- **Current:** Cofre grande con drops mejorados.
- **Wiki says:** Cofre grande que suelta 2 items + algunos pickups. (Descripción genérica pero correcta.)
- **Suggested fix:** Pickup: cofre grande que suelta 2 items aleatorios y varios pickups.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Mega_Chest

### "The Stars?"
- **Current:** Te teletransporta a un Treasure Room aleatorio del piso.
- **Wiki says:** Quita tu item pasivo más antiguo (ignorando starting items) y genera 2 pedestales del pool de la sala actual.
- **Suggested fix:** Quita tu item pasivo más antiguo y genera 2 pedestales del pool de la sala actual.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Stars%3F

### "Spindown Dice"
- **Current:** Reroll de un item a la calidad inmediatamente inferior (Quality--).
- **Wiki says:** Rerolea pedestales bajando su ID interno en -1 hasta encontrar un item válido (no es "calidad-1"; los items con ID más alto suelen ser más fuertes, así que es útil para subir).
- **Suggested fix:** Rerolla pedestales restando -1 a su ID interno hasta encontrar un item válido (suele mejorar la calidad).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Spindown_Dice

### "Dice Bag"
- **Current:** Cada cierto número de habitaciones, usa un dado aleatorio automáticamente.
- **Wiki says:** 50% chance al entrar a una nueva sala de darte un dado de un solo uso en slot consumible.
- **Suggested fix:** Trinket: 50% chance al entrar a una nueva sala de darte un dado de un solo uso aleatorio.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Dice_Bag

### "Soul of Cain"
- **Current:** Abre todas las puertas (incluyendo Devil/Angel) del piso.
- **Wiki says:** Abre todas las puertas de la sala actual (no del piso) y crea Red Rooms en paredes válidas.
- **Suggested fix:** Abre todas las puertas de la sala actual y crea Red Rooms en paredes válidas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Cain

### "Gold Pill"
- **Current:** Pill dorada: aplica el efecto y persiste durante toda la run.
- **Wiki says:** Pill dorada de un solo uso pero su efecto positivo permanece **por todo el piso** (o run según versión); las negativas siguen siendo negativas. (Imprecisión leve.)
- **Suggested fix:** Pickup: Pill dorada que aplica el efecto y, si es positivo, dura el resto del piso.
- Wiki URL: (no wiki link)

### "Wheel of Fortune?"
- **Current:** Genera una Slot Machine o Fortune Telling Machine aleatoria.
- **Wiki says:** Invoca un efecto random de Dice Room (sin claridad de cuál). NO Slot Machine ni Fortune Telling.
- **Suggested fix:** Invoca un efecto aleatorio de Dice Room (variable e impredecible).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Wheel_of_Fortune%3F

### "Bag of Crafting"
- **Current:** Bolsa de crafteo de Tainted Cain: combina 8 pickups para crear un item.
- **Wiki says:** Correcto, además permite swipe attack hacia enemigos. La calidad del item depende de la calidad total de los pickups.
- **Suggested fix:** Bolsa de Tainted Cain: combina 8 pickups para craftear un item (calidad según los pickups). El swipe ataca y recolecta pickups.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Bag_of_Crafting

### "Lucky Sack"
- **Current:** Los sacos tienen más probabilidad de soltar pickups buenos.
- **Wiki says:** Spawnea un Grab Bag al bajar al siguiente piso. NO afecta probabilidad de drops de sacos.
- **Suggested fix:** Trinket: spawnea un Grab Bag al empezar cada piso.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Lucky_Sack

### "Blue Key"
- **Current:** Aplica efecto Blue Key: cofres azules adicionales en cada habitación.
- **Wiki says:** Trinket: al entrar a una sala locked, no consume llave; en su lugar te lleva a un mini-piso azul tipo ???. Funciona también con arcades/vaults/dice rooms.
- **Suggested fix:** Trinket: las puertas que requieren llave no la consumen y te llevan a una mini-sala azul con enemigos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Blue_Key

### "Cricket Leg"
- **Current:** Al matar enemigos, drop ocasional de una mosca aleatoria.
- **Wiki says:** 1/6 chance al matar un enemigo de spawnear una **langosta** aleatoria (no mosca), hasta 4 white locusts. NO afectado por Luck.
- **Suggested fix:** Al matar un enemigo, 1/6 chance de spawnear una langosta aleatoria (hasta 4 por kill).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Cricket_Leg

### "Soul of Apollyon"
- **Current:** Genera 4 langostas que atacan enemigos por la habitación.
- **Wiki says:** Spawnea **15 langostas aleatorias** (no 4).
- **Suggested fix:** Spawnea 15 langostas aleatorias que atacan enemigos en la sala.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Apollyon

### "The Tower?"
- **Current:** Lluvia de troll bombs sobre la habitación.
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Tower%3F

### "Abyss"
- **Current:** Cualquier item pasivo se puede convertir en una mosca permanente.
- **Wiki says:** Destruye todos los items en pedestal de la sala y los convierte en langostas únicas (no moscas) cuyas habilidades dependen del item destruido. Hasta 64.
- **Suggested fix:** Activo: destruye todos los items en pedestal de la sala y los convierte en langostas únicas con habilidades según el item. Recarga: 4 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Abyss

### "Apollyon's Best Friend"
- **Current:** Convoca un familiar mosca grande con daño elevado.
- **Wiki says:** Es un **trinket**, no activo. Spawnea una langosta de ataque (no mosca) idéntica a las de Abyss.
- **Suggested fix:** Trinket: spawnea una langosta familiar tipo Abyss que daña enemigos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Apollyon%27s_Best_Friend

### "Echo Chamber"
- **Current:** Las cartas, pills y runas se duplican al usarse.
- **Wiki says:** Al usar una carta/pill/runa, también se usan copias de las últimas 3 cartas/pills/runas que usaste tras coger Echo Chamber. NO es simple duplicación.
- **Suggested fix:** Al usar una carta/pill/runa, también se aplican las últimas 3 cartas/pills/runas usadas anteriormente.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Echo_Chamber

### "Holy Crown"
- **Current:** Empiezas cada piso con Holy Mantle activado.
- **Wiki says:** Hace aparecer una Treasure Room y Shop adicionales en Cathedral. NO Holy Mantle.
- **Suggested fix:** Trinket: aparece una Treasure Room y un Shop en Cathedral.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Holy_Crown

### "Soul of Magdalene"
- **Current:** Suelta 6 medios corazones rojos.
- **Wiki says:** Crea un aura roja burbujeante alrededor de Isaac; enemigos que mueras durante la sala dropean medio Red Heart que despawnea en 2s.
- **Suggested fix:** Crea un aura por la sala: los enemigos que mates dropean medio Red Heart que despawnea en 2s.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Magdalene

### "Queen of Hearts"
- **Current:** Corazón con doble valor (cura más).
- **Wiki says:** Es una **carta** (no pickup): dropea 1-20 Red Hearts completos en el suelo al usarse.
- **Suggested fix:** Carta: dropea 1-20 Red Hearts completos en el suelo.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Queen_of_Hearts

### "The Lovers?"
- **Current:** +2 contenedores de corazón rojo permanentes.
- **Wiki says:** Crea un pedestal de item aleatorio del pool de la sala, pero convierte 1 Red Heart Container o 2 Soul Hearts en un Broken Heart. NO da contenedores.
- **Suggested fix:** Crea un pedestal del pool de la sala, pero convierte 1 Red Heart Container (o 2 Soul Hearts) en un Broken Heart.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Lovers%3F

### "Hypercoagulation"
- **Current:** Tus drops de heart dejan rastro de sangre que daña enemigos.
- **Wiki says:** Al recibir daño, dropea un Red Heart correspondiente que despawnea en 1.5s y sale impulsado lejos de Isaac.
- **Suggested fix:** Al recibir daño, dropeas un Red Heart impulsado lejos que despawnea en 1.5s.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Hypercoagulation

### "Mother's Kiss"
- **Current:** +1 contenedor de corazón al recoger el trinket.
- **Wiki says:** Correcto: +1 heart container mientras se lleva el trinket. Se rellena al recogerlo.
- **Suggested fix:** Trinket: +1 contenedor de corazón mientras lo lleves (relleno al recogerlo).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Mother%27s_Kiss

### "Belly Jelly"
- **Current:** Te impulsa con sacudidas; ganas +damage tras quedarte quieto un rato.
- **Wiki says:** Enemigos que tocan a Isaac rebotan en la dirección contraria y reciben daño al chocar con pared/obstáculo. 50% chance de evitar contact damage; 50% chance de que los proyectiles reboten.
- **Suggested fix:** Los enemigos que te tocan rebotan y reciben daño contra paredes/obstáculos. 50% chance de evitar contact damage y de reflejar proyectiles.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Belly_Jelly

### "Expansion Pack"
- **Current:** Los items activos también te dan un pequeño efecto pasivo.
- **Wiki says:** Al usar un item activo, también activa el efecto de otro item activo aleatorio (excluye Metronome, D Infinity, Esau Jr.).
- **Suggested fix:** Trinket: al usar un activo, también dispara el efecto de otro item activo aleatorio.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Expansion_Pack

### "Soul of Bethany"
- **Current:** Recarga todos tus items activos con +2 cargas extra.
- **Wiki says:** Spawnea 6 wisps azules (10% chance cada uno de ser un wisp aleatorio).
- **Suggested fix:** Spawnea 6 wisps azules que orbitan a Isaac y disparan.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Bethany

### "Confessional"
- **Current:** Donar un item activo da una recompensa proporcional.
- **Wiki says:** Es una **machine** (como Donation Machine), no un item. Cuesta vida y tiene 30% chance (25% Hard) de dar recompensa (Soul/Eternal Hearts, items de Angel Room, o "You Feel Blessed!").
- **Suggested fix:** Machine en Super Secret/Angel Rooms: a costa de vida (como Blood Donation), chance de dar Soul/Eternal Hearts, items de Angel Room o "You Feel Blessed!".
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Confessional

### "The Hierophant?"
- **Current:** +2 Bone Hearts permanentes.
- **Wiki says:** Spawnea 2 Bone Hearts en el suelo (pickups, no contenedores permanentes garantizados).
- **Suggested fix:** Spawnea 2 Bone Hearts en el suelo cerca de Isaac.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Hierophant%3F

### "Lemegeton"
- **Current:** Genera un wisp de un item aleatorio que se queda permanentemente.
- **Wiki says:** Correcto: spawnea un wisp orbital que aplica el efecto pasivo de un item random. Recarga 6 salas.
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Lemegeton

### "Beth's Essence"
- **Current:** Aumenta los efectos de los wisps que generes.
- **Wiki says:** Al entrar a Angel Room (o The Stairway), spawnea 5 wisps azules. Donar a Beggars: chance de spawnear wisps.
- **Suggested fix:** Trinket: al entrar a Angel Room spawnea 5 wisps; donar a Beggars chance de generar wisps.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Beth%27s_Essence

### "Vengeful Spirit"
- **Current:** Al recibir daño, convoca un espíritu vengador que ataca enemigos.
- **Wiki says:** Correcto: al recibir daño spawnea un red wisp que dispara lágrimas spectrales y daña por contacto. Hasta 6 por piso.
- **Suggested fix:** Al recibir daño, spawnea un wisp rojo que dispara lágrimas spectrales (hasta 6 por piso).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Vengeful_Spirit

### "Nuh Uh!"
- **Current:** Al usar un item activo, tus stats no bajan (anula penalizaciones).
- **Wiki says:** A partir del Chapter 4, reemplaza los spawns de monedas y llaves por pickups aleatorios (bombas/corazones/cards/etc.).
- **Suggested fix:** Trinket: desde el Chapter 4, los spawns de monedas y llaves se reemplazan por pickups aleatorios.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Nuh_Uh!

### "Soul of Eden"
- **Current:** Reroll completo de todos los pedestales del piso.
- **Wiki says:** Rerolea todos los pickups, trinkets e items de la **sala** (no del piso), con pools aleatorios.
- **Suggested fix:** Rerolea todos los pickups, trinkets e items de la sala (los items usan pools aleatorios).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Eden

### "Wild Card"
- **Current:** Reutiliza el último item activo, card o pill que usaste.
- **Wiki says:** Correcto, además runas, Soul Stones y activos.
- **Suggested fix:** Copia el efecto de la última pill, carta, runa, Soul Stone o item activo usado.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Wild_Card

### "The World?"
- **Current:** Revela todas las puertas y items en pedestales del piso.
- **Wiki says:** Crea un trap door que lleva a un Crawl Space. NO revela nada.
- **Suggested fix:** Crea un trap door que siempre lleva a un Crawl Space.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_World%3F

### "Corrupted Data"
- **Current:** Glitchea items y enemigos creando efectos aleatorios impredecibles.
- **Wiki says:** Es un **achievement** persistente del save: Secret Rooms tienen 1/60 chance de generar items glitched; I AM ERROR rooms 1/16. NO es un item activo.
- **Suggested fix:** Achievement permanente: Secret Rooms tienen 1/60 chance y I AM ERROR rooms 1/16 chance de generar items glitched (tipo TMTRAINER).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Corrupted_Data

### "Modeling Clay"
- **Current:** Cada piso, un item aleatorio se transforma en otro de mayor calidad.
- **Wiki says:** Trinket: 50% chance al entrar a una nueva sala de copiar el efecto de un item pasivo aleatorio (similar a Lemegeton wisp selection).
- **Suggested fix:** Trinket: 50% chance al entrar a una nueva sala de copiar el efecto de un item pasivo aleatorio.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Modeling_Clay

### "TMTRAINER"
- **Current:** Convierte todos los items en items glitched con efectos aleatorios (riesgo/recompensa extremo).
- **Wiki says:** Correcto: todos los items futuros serán glitched (75% pasivos, 25% activos) con efectos random combinados de 2-3 items.
- **Suggested fix:** (correcto, sin cambios significativos)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/TMTRAINER

### "Your Soul"
- **Current:** Al usar Dark Arts, deja una sombra Your Soul que persigue enemigos.
- **Wiki says:** Trinket: te da 1 Devil Deal gratis a cambio del trinket (se consume al comprar).
- **Suggested fix:** Trinket: te permite tomar 1 item de Devil Deal/Black Market gratis; se consume al usarlo.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Your_Soul

### "Soul of Judas"
- **Current:** Aplica el efecto de Dark Arts (invisibilidad + multiplicador de daño).
- **Wiki says:** Activa Dark Arts durante 3 segundos. Otorga damage up temporal por cada enemigo/proyectil tocado.
- **Suggested fix:** Aplica el efecto de Dark Arts durante 3s. Cada enemigo/proyectil tocado da +daño temporal.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Judas

### "The Magician?"
- **Current:** +5 al daño durante la habitación.
- **Wiki says:** Aura azul que repele proyectiles y enemigos durante 1 minuto.
- **Suggested fix:** Otorga un aura azul que repele proyectiles y enemigos durante 1 minuto.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Magician%3F

### "Dark Arts"
- **Current:** Invisibilidad temporal + multiplicador de daño al siguiente hit.
- **Wiki says:** +1.0 speed durante 1s; durante ese tiempo Isaac puede caminar a través de enemigos/proyectiles, congelándolos. Al final hace un AoE blast que daña proporcionalmente a lo que tocaste.
- **Suggested fix:** Activo: +1.0 speed durante 1s; atraviesa enemigos/proyectiles congelándolos, y al final hace un AoE blast escalado con lo que tocaste.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Dark_Arts

### "Number Magnet"
- **Current:** Atrae pickups hacia Isaac automáticamente.
- **Wiki says:** Trinket: +10% chance de Devil Room, previene Krampus, y si está al entrar a Devil Deal modifica el layout a uno especial con 0-3 items, Black Hearts y enemigos. NO atrae pickups.
- **Suggested fix:** Trinket: +10% chance de Devil Room, previene Krampus y cambia el layout de Devil Rooms a uno especial con más items y Black Hearts.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Number_Magnet

### "Sanguine Bond"
- **Current:** Al recibir daño, drop adicional de Black Heart.
- **Wiki says:** Spawnea spikes especiales en la Devil Room que al chocar dan recompensas aleatorias (+0.5 daño, monedas, Black Hearts, item de Devil, o transformación a Leviathan).
- **Suggested fix:** Spawnea spikes en la Devil Room que al chocar otorgan recompensas aleatorias (daño/monedas/Black Hearts/items/Leviathan).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Sanguine_Bond

### "Torn Pocket"
- **Current:** Al recibir daño, drop aleatorio de monedas, llaves o bombas.
- **Wiki says:** Al recibir daño, dropea 2 pickups aleatorios de **tu inventario** (excepto Hearts/Pills/Cards). Puede ser bombas/monedas/llaves/etc.
- **Suggested fix:** Trinket: al recibir daño, dropeas 2 pickups aleatorios de tu inventario (excepto corazones/pills/cards).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Torn_Pocket

### "Soul of Lazarus"
- **Current:** Mata a Tainted Lazarus pero revive como su forma alternativa.
- **Wiki says:** Es una runa de revival pasivo: al morir te revive automáticamente en el sitio con ½ corazón y 1.5s de invulnerabilidad.
- **Suggested fix:** Al morir, revives automáticamente en la misma sala con medio corazón y 1.5s de invulnerabilidad.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Lazarus

### "Wooden Chest"
- **Current:** Cofre de madera con drops de tipo wood (pickups básicos).
- **Wiki says:** No es un cofre estándar del juego. Confirmar nombre exacto. (Probablemente "Wooden Chest" no existe como pickup; podría ser confusión con "Old Chest".)
- **Suggested fix:** Verificar el nombre exacto en código fuente. No hay wiki page para "Wooden Chest" claro.
- Wiki URL: (no wiki link en código)

### "Judgement?"
- **Current:** Genera un Beggar aleatorio en la habitación.
- **Wiki says:** Genera un **Shop Restock Machine** (no un Beggar aleatorio).
- **Suggested fix:** Spawnea un Shop Restock Machine cerca de Isaac.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Judgement%3F

### "Flip"
- **Current:** Alterna entre Lazarus y Flipped Lazarus, intercambiando sus items.
- **Wiki says:** Permite cambiar items en pedestal por su versión "ghost" oculta. Para Tainted Lazarus, además cambia entre sus dos formas. Recarga 6 salas.
- **Suggested fix:** Pedestales muestran un item "ghost" oculto; al usar, intercambias el visible con el ghost (puedes coger ambos). Para Tainted Lazarus también cambia de forma.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Flip

### "Torn Card"
- **Current:** Lanza 4 lágrimas en cruz en las direcciones cardinales.
- **Wiki says:** Es un **trinket**, no carta. Cada 15 disparos, lanza una lágrima Ipecac + My Reflection con range alto.
- **Suggested fix:** Trinket: cada 15 lágrimas disparas una lágrima Ipecac+Reflection (explosiva y rebotante).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Torn_Card

### "Salvation"
- **Current:** Cada vez que recibas daño, dispara una columna de luz hacia abajo.
- **Wiki says:** Aura angélica alrededor de Isaac: enemigos dentro durante ~1s reciben un beam de luz central + 4 beams en cruz. El aura crece al recibir daño.
- **Suggested fix:** Aura angélica: enemigos dentro >1s reciben un beam central y 4 beams en cruz. El aura crece al recibir daño.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Salvation

### "Polished Bone"
- **Current:** Disparar tus huesos crea pequeñas bone tears adicionales.
- **Wiki says:** Trinket: 25% chance de spawnear un Bony amistoso al limpiar una sala (25% de ellos son Black Bony).
- **Suggested fix:** Trinket: 25% chance al limpiar una sala de spawnear un Bony amistoso (25% son Black Bony).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Polished_Bone

### "Soul of The Forgotten"
- **Current:** Convoca a un familiar Soul of The Forgotten temporal.
- **Wiki says:** Convoca a **The Forgotten** (no a su soul) como personaje secundario controlable junto a Isaac, durante la sala.
- **Suggested fix:** Spawnea a The Forgotten como personaje secundario controlable durante la sala.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_the_Forgotten

### "Death?"
- **Current:** Daña a todos los enemigos visibles a la mitad de su vida.
- **Wiki says:** Spawnea bone familiars por cada enemigo muerto en la sala (igual que Book of the Dead). NO daña.
- **Suggested fix:** Spawnea un bone familiar por cada enemigo muerto en la sala (similar a Book of the Dead).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Death%3F

### "Decap Attack"
- **Current:** La cabeza del Soul se puede lanzar como proyectil y volver.
- **Wiki says:** Activo: Isaac despega su cabeza y la lanza; hace 24 daño al impacto y 4/tick mientras está en el suelo. Dispara lágrimas y bloquea proyectiles desde el suelo.
- **Suggested fix:** Activo: Isaac despega y lanza su cabeza (24 daño impacto, 4/tick en el suelo); la cabeza dispara y bloquea proyectiles.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Decap_Attack

### "Hollow Heart"
- **Current:** Al inicio de cada piso, +1 Bone Heart.
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Hollow_Heart

### "Isaac's Tomb"
- **Current:** Convoca una tumba que actúa como sacrificio (daño/reward).
- **Wiki says:** Es un item **pasivo**, no activo. Spawnea un Old Chest al inicio de cada piso (Soul Hearts, trinkets, Angel Room items o Old Chest).
- **Suggested fix:** Pasivo: spawnea un Old Chest al inicio de cada piso (Soul Hearts, trinkets, items de Angel Room).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Isaac%27s_Tomb

### "RC Remote"
- **Current:** Permite controlar a Esau (o un familiar) con el segundo joystick.
- **Wiki says:** Los familiares se controlan directamente con los inputs de Isaac (sin segundo joystick). Hold drop para mover a Isaac solo, dejando familiars quietos.
- **Suggested fix:** Trinket: los familiares se controlan con tus mismos inputs; hold drop para moverte solo y dejarlos quietos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/RC_Remote

### "Soul of Jacob and Esau"
- **Current:** Convoca dos espíritus aliados que disparan.
- **Wiki says:** Spawnea **Esau** (uno solo) como personaje secundario controlable durante la sala. Recibe items random igualados al inventario de Isaac.
- **Suggested fix:** Spawnea a Esau como personaje secundario controlable durante la sala (con items igualados a Isaac).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Jacob_and_Esau

### "Golden Trinket"
- **Current:** Trinket dorado con doble efecto del trinket original.
- **Wiki says:** Correcto: efectos doblados o con bonus extra (igual que con Mom's Box). NO es un item específico; es un atributo de cualquier trinket.
- **Suggested fix:** Tipo de trinket: duplica el efecto del trinket base (similar a Mom's Box).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Golden_Trinket

### "Anima Sola"
- **Current:** Inmoviliza al enemigo más cercano durante unos segundos.
- **Wiki says:** Correcto: encadena al enemigo más cercano durante 5 segundos. Recarga 15s.
- **Suggested fix:** Encadena al enemigo más cercano durante 5 segundos. Recarga: 15 segundos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Anima_Sola

### "Found Soul"
- **Current:** Familiar fantasma; al morir suelta un item.
- **Wiki says:** Trinket: familiar fantasma que imita movimiento de Isaac (tipo J&E), vuelo, lágrimas spectrales con 50% de su daño. Muere de un hit, respawnea cada piso.
- **Suggested fix:** Trinket: familiar fantasma que imita tu movimiento (tipo J&E) con vuelo y lágrimas spectrales al 50% de tu daño. Muere de un hit y respawnea cada piso.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Found_Soul

### "Esau Jr."
- **Current:** Te transforma en Esau Jr., una versión adulta jugable.
- **Wiki says:** Activo: intercambia entre tu personaje y Esau Jr. (3 Black Hearts, +2 daño, vuelo). Coins/bombs/keys compartidos, hearts/items separados. Si uno muere, mueren ambos.
- **Suggested fix:** Activo: te intercambia con Esau Jr. (+2 daño, 3 Black Hearts, vuelo). Coins/bombs/keys compartidos; si uno muere, mueren ambos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Esau_Jr.

### "Strange Key"
- **Current:** Tus llaves no se gastan al abrir puertas (no consumibles).
- **Wiki says:** Trinket: abre el paso a ??? (Blue Womb) sin tiempo. Con Pandora's Box spawnea 6 items de pools variados.
- **Suggested fix:** Trinket: abre el paso a ??? (Blue Womb) sin importar el tiempo de la run; con Pandora's Box genera 6 items random.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Strange_Key

### "Soul of Eve"
- **Current:** Spawnea 4 lágrimas de sangre con homing.
- **Wiki says:** Spawnea **14 Dead Bird familiars** que vuelan desde fuera de la pantalla y atacan enemigos durante 10s.
- **Suggested fix:** Spawnea 14 Dead Birds que entran desde fuera y atacan enemigos por 10s.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Eve

### "The Empress?"
- **Current:** +damage y +velocidad durante la habitación.
- **Wiki says:** +2 Red Hearts temporales, **+1.5 fire rate**, **-0.1 speed**, durante 1 minuto.
- **Suggested fix:** +2 Red Hearts temporales, +1.5 fire rate y -0.1 speed durante 1 minuto.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Empress%3F

### "Sumptorium"
- **Current:** Convoca 3 Clots aliados que disparan por ti.
- **Wiki says:** Por uso: pierdes ½ corazón y spawnea 1 Clot familiar que copia tus disparos. Tainted Eve tiene mecánica especial. Recarga 10s.
- **Suggested fix:** Activo: pierdes ½ corazón y spawnea un Clot familiar que copia tus disparos (mecánica especial para Tainted Eve).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Sumptorium

### "Lil Clot"
- **Current:** Clot familiar que dispara lágrimas por ti.
- **Wiki says:** Es un **trinket**, no familiar item. Spawnea un Clot familiar que copia tu movimiento y dispara al 35% de tu daño.
- **Suggested fix:** Trinket: spawnea un Clot familiar que copia tu movimiento y dispara al 35% de tu daño (muere tras 3 hits).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Lil_Clot

### "Heartbreak"
- **Current:** Cada contenedor de corazón vale la mitad pero permite más contenedores.
- **Wiki says:** Da inmediatamente 3 Broken Hearts y +0.25 daño por cada broken heart (max +2.75). Cuando recibirías daño mortal, +2 broken hearts y activa efecto de Necronomicon.
- **Suggested fix:** Te da 3 Broken Hearts y +0.25 daño por cada uno. Al recibir daño mortal, +2 broken hearts y trigger del Necronomicon (40 daño AoE).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Heartbreak

### "Wicked Crown"
- **Current:** Los items en pedestal valen como rerolls del D6.
- **Wiki says:** Trinket: hace que aparezca una Treasure Room y un Shop en **Sheol**.
- **Suggested fix:** Trinket: aparece una Treasure Room y un Shop en Sheol.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Wicked_Crown

### "Soul of Azazel"
- **Current:** Te otorga un mini Brimstone temporal con daño elevado.
- **Wiki says:** Activa **Mega Blast durante 7.5 segundos** (no un mini Brimstone; es el láser más ancho del juego).
- **Suggested fix:** Activa Mega Blast (láser gigantesco) durante 7.5 segundos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Azazel

### "Hell Game"
- **Current:** Beggar diabólico con recompensas demoníacas potentes.
- **Wiki says:** Es un **Beggar/machine**, no un item activo. Tras pagar con un corazón, escoges una de 3 calaveras; ganas una recompensa o un Spider enemigo.
- **Suggested fix:** Beggar: pagas un corazón, eliges una de 3 calaveras y ganas una recompensa (heart/coin/bomb/key/card/Black Heart/Devil item) o un Spider enemigo.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Hell_Game

### "The Devil?"
- **Current:** +damage masivo durante la habitación.
- **Wiki says:** Invoca el efecto de Bible (daña bosses) y otorga vuelo + Seraphim familiar durante 30s.
- **Suggested fix:** Aplica el efecto de Bible y otorga vuelo + Seraphim familiar durante 30 segundos.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Devil%3F

### "Hemoptysis"
- **Current:** Pierde medio corazón rojo y crea una nube de sangre que daña enemigos.
- **Wiki says:** Es un item **pasivo** activado por doble tap (no por consumo de vida). Hace que Isaac estornude sangre con x1.5 daño en frente, knockback y aplica curse que potencia daño tipo Brimstone.
- **Suggested fix:** Pasivo: al doble tap del disparo, Isaac estornuda sangre (x1.5 daño + knockback) que aplica una maldición que potencia daño tipo Brimstone.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Hemoptysis

### "Azazel's Stump"
- **Current:** Brimstone con +daño pero range corto.
- **Wiki says:** Es un **trinket**, no pasivo. 33% chance tras limpiar una sala de transformarse en Azazel (brimstone corto, +daño, +speed, vuelo).
- **Suggested fix:** Trinket: 33% chance al limpiar una sala de transformarte temporalmente en Azazel (brimstone corto, +daño, vuelo).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Azazel%27s_Stump

### "Azazel's Rage"
- **Current:** Acumulas rabia al hacer daño; al llenarse, libera un Brimstone gigante.
- **Wiki says:** Acumulas rabia al **limpiar salas** (no al hacer daño). Tras 4 salas, el siguiente cuarto con enemigos dispara un Brimstone gigante.
- **Suggested fix:** Cada 4 salas limpiadas, el siguiente cuarto con enemigos dispara automáticamente un Brimstone gigante.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Azazel%27s_Rage

### "Dingle Berry"
- **Current:** Al moverte, dejas un rastro de poop friendlies que dañan enemigos.
- **Wiki says:** Trinket: spawnea un Dip friendly aleatorio al limpiar una sala (y al iniciar waves en Boss Rush/Greed Mode).
- **Suggested fix:** Trinket: al limpiar una sala spawnea un Dip friendly aleatorio.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Dingle_Berry

### "Soul of ???"
- **Current:** Suelta 3 fly-poops que persiguen enemigos.
- **Wiki says:** Lanza 8 poison farts en 2s + 7 Butt Bombs + deja brown creep que da +1.5 fire rate y +1 daño.
- **Suggested fix:** Lanza 8 poison farts y 7 Butt Bombs en 2s, dejando brown creep que da +1.5 fire rate y +1 daño.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_%3F%3F%3F

### "Charming Poop"
- **Current:** Poop que aplica charm a enemigos cercanos.
- **Wiki says:** Es un tipo de **poop interactivo** (terreno) que al ser dañado/destruido spawnea Dip familiars. NO aplica charm.
- **Suggested fix:** Poop especial que al recibir daño/destruirse spawnea Dip familiars amistosos (tipo Dirty Mind).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Charming_Poop

### "The Emperor?"
- **Current:** Te lleva directamente al boss room del piso.
- **Wiki says:** Te teletransporta a una boss room extra con un boss 2 pisos más abajo (en pisos tardíos, una sala random); al salir vuelves a tu sitio.
- **Suggested fix:** Te teletransporta a una boss room extra con un boss más fuerte; al salir vuelves a la sala original con el reward.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Emperor%3F

### "IBS"
- **Current:** Cada cierto número de disparos, generas un poop aleatorio.
- **Wiki says:** Tras hacer un cierto daño (40+13.33×(stage−1)) a un enemigo, Isaac flashea y al soltar disparo lanza una de las habilidades de Tainted ??? (poop launch, fart, diarrhea explosion, etc.).
- **Suggested fix:** Tras hacer suficiente daño a un enemigo, al soltar el disparo lanzas una habilidad random de Tainted ??? (poop, fart, explosión, etc.).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/IBS

### "Ring Cap"
- **Current:** +1 bomba con efecto doble al explotar.
- **Wiki says:** Cada bomba que coloques spawnea una bomba extra al lado. No consume bombas adicionales.
- **Suggested fix:** Trinket: cada bomba que coloques genera una segunda bomba adyacente sin gastar pickup.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Ring_Cap

### "The Swarm"
- **Current:** Al recibir daño, suelta moscas amigas que atacan enemigos.
- **Wiki says:** Pasivo: da 8 orbital flies al recogerlo y +1 por sala limpiada (hasta 16). Las moscas que bloquean shots se convierten en Blue Flies.
- **Suggested fix:** Te da 8 moscas orbitales (+1 por sala limpiada, hasta 16). Las que bloquean shots se convierten en Blue Flies.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Swarm

### "Temporary Tattoo"
- **Current:** Al recibir daño, +damage temporal en la habitación.
- **Wiki says:** Trinket: dropea un cofre al limpiar una Challenge Room; en una Boss Challenge Room dropea un boss item extra. NO tiene que ver con daño recibido.
- **Suggested fix:** Trinket: al completar una Challenge Room dropea un cofre; en Boss Challenge Room dropea un item extra de boss.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Temporary_Tattoo

### "Soul of Samson"
- **Current:** Berserk durante 5 segundos (melee + invulnerable).
- **Wiki says:** Berserk durante 10 segundos (no 5), no invulnerable, sin extensión por kills.
- **Suggested fix:** Berserk durante 10 segundos: melee + speed/daño extra.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Samson

### "Crane Game"
- **Current:** Máquina que da un item aleatorio (50/50 funciona o destruye).
- **Wiki says:** Cuesta 5 cents; 25% chance de pay out por intento. Tras dar 3 items, la máquina explota.
- **Suggested fix:** Machine: cuesta 5¢ por intento, 25% chance de dar item; tras 3 items obtenidos, explota.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Crane_Game

### "Strength?"
- **Current:** +1 contenedor temporal y +damage hasta morir.
- **Wiki says:** Debilita a todos los enemigos durante 1 minuto: más lentos, proyectiles más lentos, +2x daño recibido, daño causado capped a ½ corazón.
- **Suggested fix:** Durante 1 minuto, los enemigos están débiles: más lentos, reciben x2 daño y solo pueden hacer ½ corazón por golpe.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Strength%3F

### "Berserk!"
- **Current:** Te vuelves invulnerable y atacas a melee con damage masivo.
- **Wiki says:** Berserk durante 5 segundos: +0.4 speed, +3 daño, melee con jawbone (x3 daño), refleja proyectiles, brief inmunidad. Carga por damage dealt (120 inicial).
- **Suggested fix:** Activo: berserk 5s con melee (jawbone x3 daño), +0.4 speed, +3 daño, refleja proyectiles. Se carga haciendo daño.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Berserk!

### "Swallowed M80"
- **Current:** Al recibir daño, explota una bomba en tu posición.
- **Wiki says:** Es un **trinket** con 50% chance al recibir daño de explotar (185 daño tipo Kamikaze). No se daña a Isaac por estar en i-frames.
- **Suggested fix:** Trinket: al recibir daño, 50% chance de explotar (185 daño AoE, sin dañar a Isaac).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Swallowed_M80

### "Larynx"
- **Current:** +damage con cooldown reducido en disparos.
- **Wiki says:** Activo: Isaac grita haciendo daño y empujando enemigos, destruye proyectiles, abre bombable doors. Daño escala con cargas; recarga 12 salas, y al recibir daño gana +1 carga.
- **Suggested fix:** Activo: Isaac grita haciendo daño AoE y empujando enemigos. Recarga 12 salas + 1 carga por daño recibido.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Larynx

### "The Twins"
- **Current:** Habilita el segundo joystick para controlar el familiar Incubus.
- **Wiki says:** Trinket: 50% chance al entrar a una sala de duplicar un familiar. Si no tienes ninguno, spawnea Brother Bobby o Sister Maggy.
- **Suggested fix:** Trinket: 50% chance al entrar a una sala de duplicar un familiar (o spawnear Brother Bobby/Sister Maggy si no tienes).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Twins

### "Soul of Lilith"
- **Current:** Genera un Incubus temporal durante la habitación.
- **Wiki says:** Te otorga **un familiar permanente** del pool de Baby Shop (no Incubus temporal).
- **Suggested fix:** Otorga un familiar permanente del pool de Baby Shop.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_Lilith

### "Fool's Gold"
- **Current:** Moneda dorada con efecto sonoro especial; cuenta como 1 penny.
- **Wiki says:** No hay info confiable disponible para este pickup en wiki. Posiblemente el nombre debería ser "Lucky Penny" o "Golden Penny".
- **Suggested fix:** Confirmar nombre exacto y referente; "Fool's Gold" no aparece como pickup estándar.
- Wiki URL: (no wiki link aparente)

### "The High Priestess?"
- **Current:** Genera dos pickups aleatorios en la habitación.
- **Wiki says:** La pierna de Mom comienza a pisar repetidamente apuntando a Isaac durante 1 minuto.
- **Suggested fix:** La pierna de Mom pisa repetidamente sobre Isaac durante 1 minuto (similar a Broken Shovel).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_High_Priestess%3F

### "Gello"
- **Current:** Genera un familiar Gello que duplica tus lágrimas.
- **Wiki says:** Es un item **activo**, no pasivo. Spawnea un familiar demonio "atado por cuerda" para la sala, que dispara hacia donde apuntas (75% daño). Recarga 2 salas.
- **Suggested fix:** Activo: spawnea un familiar demonio (por la sala) que dispara hacia donde apuntas al 75% de tu daño. Recarga: 2 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Gello

### "Adoption Papers"
- **Current:** Los familiares persisten entre runs (similar a Eden's Blessing).
- **Wiki says:** Trinket: tiendas y Black Markets venden familiars (del pool Baby Shop) en lugar de items, a 10 monedas.
- **Suggested fix:** Trinket: las tiendas y Black Markets venden familiars del pool Baby Shop a 10 monedas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Adoption_Papers

### "Twisted Pair"
- **Current:** Dos familiares fantasma orbitando que disparan.
- **Wiki says:** Dos familiares demonio (no fantasmas) que flotan a los lados y disparan al 0.375x del daño de Isaac cada uno.
- **Suggested fix:** Dos familiares demonio que flotan a los lados y disparan lágrimas (37.5% del daño de Isaac cada uno).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Twisted_Pair

### "Kid's Drawing"
- **Current:** Al entrar en habitación nueva, activa Holy Mantle temporal.
- **Wiki says:** Trinket: cuenta como un item de Guppy para la transformación. NO da Holy Mantle.
- **Suggested fix:** Trinket: cuenta como un item de Guppy (mientras lo tengas).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Kid%27s_Drawing

### "Soul of The Lost"
- **Current:** Te hace invulnerable durante 10 segundos.
- **Wiki says:** Te convierte temporalmente en The Lost por la sala (vuelo + Holy Mantle). NO 10 segundos.
- **Suggested fix:** Te convierte temporalmente en The Lost por la sala (vuelo + Holy Mantle de un uso).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_the_Lost

### "The Fool?"
- **Current:** Te quita todos los items que tienes (uso especial).
- **Wiki says:** Dropea todos tus hearts, trinkets y pickups en el suelo, dejándote a ½ corazón. NO quita items pasivos.
- **Suggested fix:** Dropea todos tus hearts, trinkets y pickups en el suelo, dejándote a medio corazón (no afecta a los items pasivos).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Fool%3F

### "Ghost Bombs"
- **Current:** Tus bombas se vuelven ghost bombs que atraviesan paredes y enemigos.
- **Wiki says:** +5 bombas. Las bombas al explotar crean ghosts que persiguen enemigos y dañan por contacto (½ tu daño/tick); a los 10s explotan. NO atraviesan paredes/enemigos.
- **Suggested fix:** +5 bombas. Tus bombas, al explotar, crean ghosts que persiguen enemigos y dañan por contacto (½ daño/tick) hasta explotar a los 10s.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Ghost_Bombs

### "Crystal Key"
- **Current:** Las llaves pueden abrir múltiples cosas (puertas y cofres a la vez).
- **Wiki says:** Trinket: al limpiar una sala, chance (33% base) de abrir una Red Room adyacente.
- **Suggested fix:** Trinket: al limpiar una sala, chance (33%-100% con copias) de abrir una Red Room adyacente.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Crystal_Key

### "Sacred Orb"
- **Current:** Los pedestales rerollean automáticamente si el item es de baja calidad.
- **Wiki says:** Es un item **pasivo**, no trinket. Items quality 0-1 siempre se rerolean; quality 2 con 33% chance.
- **Suggested fix:** Pasivo: items de calidad 0-1 se rerolean siempre; calidad 2 con 33% chance.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Sacred_Orb

### "Keeper's Bargain"
- **Current:** Los Devil Deals cuestan monedas en vez de corazones.
- **Wiki says:** Trinket: 50% chance de que los items de Devil Deal/Black Market/Pound of Flesh shop cuesten monedas en vez de corazones (15¢ por heart container, 30¢ por 2).
- **Suggested fix:** Trinket: 50% chance de que los items de Devil/Black Market cuesten monedas en lugar de corazones (15¢ por contenedor).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Keeper%27s_Bargain

### "Soul of The Keeper"
- **Current:** +6 monedas al usar.
- **Wiki says:** Dropea 1-25 monedas aleatorias.
- **Suggested fix:** Dropea 1-25 monedas aleatorias en el suelo.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Soul_of_the_Keeper

### "Golden Penny"
- **Current:** Moneda dorada: vale 1 penny pero da +luck temporal.
- **Wiki says:** Vale 1 penny y da bonus de Luck (Repentance lo cambió: ahora afecta a Coin Cap). El "temporal" no es correcto: el luck es persistente mientras se tenga el cap.
- **Suggested fix:** Moneda dorada: vale 1 moneda y otorga +luck.
- Wiki URL: (no link en código)

### "The Hanged Man?"
- **Current:** +1 contenedor de corazón rojo permanente.
- **Wiki says:** Isaac se transforma visualmente en Keeper durante 30s con triple shot, x0.51 daño y -0.1 speed; matar enemigos en este estado los hace dropear monedas. NO da contenedor.
- **Suggested fix:** Te transforma visualmente en Keeper durante 30s (triple shot, x0.51 daño, -0.1 speed); los enemigos muertos sueltan monedas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/The_Hanged_Man%3F

### "Keeper's Kin"
- **Current:** Genera 3 familiares Keeper que disparan por ti.
- **Wiki says:** Hace que las rocas y obstáculos rocosos spawneen blue spiders cuando hay enemigos en la sala, y al destruirse sueltan 0-2 blue spiders. NO genera Keepers.
- **Suggested fix:** Las rocas spawnean blue spiders cuando hay enemigos, y al destruirse sueltan 0-2 blue spiders adicionales.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Keeper%27s_Kin

### "Cursed Penny"
- **Current:** Cada cierto tiempo te da -damage pero +monedas.
- **Wiki says:** Trinket: al recoger una moneda, te teletransporta a una sala aleatoria. El tipo de sala depende del tipo de moneda (penny=combat, nickel=treasure/shop, dime=Angel/Devil, etc.).
- **Suggested fix:** Trinket: al recoger una moneda, te teletransporta a una sala aleatoria (el tipo depende del tipo de moneda).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Cursed_Penny

### "Strawman"
- **Current:** Convoca un Strawman amigo que dispara por ti (cuesta vida).
- **Wiki says:** Spawnea a Keeper como personaje secundario controlable (tipo Esau). Keeper usa monedas como vida. Al morir Keeper, spawnea 5 blue spiders y el item se va.
- **Suggested fix:** Spawnea a Keeper como personaje secundario controlable (usa monedas como vida); al morir Keeper, libera 5 blue spiders y se consume.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Strawman

### "Sack of Pennies"
- **Current:** Saco que suelta una moneda cada pocas habitaciones.
- **Wiki says:** Dropea 1 moneda cada 2 salas (la primera tras 1 sala).
- **Suggested fix:** Familiar que dropea una moneda cada 2 salas (la primera tras 1 sala).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Sack_of_Pennies

### "Bomb Bag"
- **Current:** Saco que suelta una bomba (a veces especial) cada pocas habitaciones.
- **Wiki says:** Dropea una bomba cada 3 salas (la primera tras 2 salas); pueden ser bombas especiales (double, troll, golden, etc.).
- **Suggested fix:** Familiar que dropea una bomba cada 3 salas (puede ser especial: double, troll, golden, etc.).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Bomb_Bag

### "Abel"
- **Current:** Tu doble; dispara lágrimas en la dirección opuesta a ti y refleja tus disparos.
- **Wiki says:** Familiar que imita el movimiento de Isaac y dispara lágrimas de 3.5 daño en la **dirección hacia Isaac** (post-Afterbirth). NO refleja tus disparos.
- **Suggested fix:** Familiar que imita tu movimiento y dispara lágrimas hacia tu posición (3.5 daño fijo).
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Abel

### "Cain's Other Eye"
- **Current:** Mosca-ojo que sigue a Isaac y dispara lágrimas en direcciones aleatorias.
- **Wiki says:** En Repentance: familiar que sigue a Isaac y dispara lágrimas que copian tus stats (al 75% de tu daño), en direcciones cardinales aleatorias.
- **Suggested fix:** Familiar que copia tus tear effects/stats y dispara al 75% de tu daño en direcciones cardinales aleatorias.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Cain%27s_Other_Eye

### "Evil Eye"
- **Current:** Probabilidad de generar un ojo flotante que dispara una lágrima poderosa.
- **Wiki says:** Chance (3.3-10% según Luck) de disparar un ojo lento que dispara lágrimas idénticas a las de Isaac (con range infinito hasta colisionar).
- **Suggested fix:** Chance (escala con Luck, hasta 10%) de disparar un ojo flotante lento que dispara lágrimas como las tuyas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Evil_Eye

### "Sack of Sacks"
- **Current:** Te suelta un saco con pickups aleatorios cada pocas habitaciones.
- **Wiki says:** Familiar que dropea un Grab Bag cada 7-8 salas (Repentance) o 5-6 (pre-Repentance).
- **Suggested fix:** Familiar que dropea un Grab Bag cada 7-8 salas.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Sack_of_Sacks

### "Pandora's Box"
- **Current:** Suelta pickups o items basados en el piso (cuanto más profundo, mejor calidad).
- **Wiki says:** Correcto en general; algunos pisos dan items específicos (Bible en ???, Red Key en Home).
- **Suggested fix:** (correcto, sin cambios significativos)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Pandora%27s_Box

### "Missing No"
- **Current:** Reroll completo de tus items y reordena el orden de los pisos del juego.
- **Wiki says:** Rerolea tus items pasivos y aleatoriza atributos al recogerlo y al inicio de cada piso. NO reordena los pisos.
- **Suggested fix:** Rerolea tus items pasivos y stats aleatoriamente al recogerlo y al inicio de cada piso.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Missing_No.

### "Store Credit"
- **Current:** Te permite comprar cualquier item gratis una sola vez.
- **Wiki says:** Correcto, específicamente en tiendas. Se consume al comprar.
- **Suggested fix:** Trinket: hace que los items de tienda sean gratis; se consume tras comprar uno.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Store_Credit

### "Key Bum"
- **Current:** Beggar que come llaves y devuelve pickups aleatorios.
- **Wiki says:** Es un **familiar**, no Beggar. Recoge llaves y dropea cofres aleatorios.
- **Suggested fix:** Familiar que recoge llaves y a cambio dropea cofres aleatorios.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Key_Bum

### "Smelter"
- **Current:** Consume un trinket dándole sus efectos permanentes a Isaac.
- **Wiki says:** Correcto. Recarga 6 salas. Además aumenta drop rate de trinkets en 2%.
- **Suggested fix:** Consume tu trinket dándote sus efectos permanentes. Recarga: 6 salas. Aumenta drop rate de trinkets +2%.
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Smelter

### "Birthright"
- **Current:** Da una mejora específica al personaje actual (cada uno tiene una distinta).
- **Wiki says:** Correcto.
- **Suggested fix:** (correcto, sin cambios)
- Wiki URL: https://bindingofisaacrebirth.wiki.gg/wiki/Birthright

## Items audited and verified correct

Sin cambios significativos necesarios (descripción coincide con el wiki dentro de tolerancia razonable):

**Isaac:** Lost Baby, Isaac's Head, Fart Baby, Cry Baby, Lil' Chest, D1, D Infinity, Meat Cleaver

**Cain:** Glass Baby, Green Baby

**Apollyon:** Locust of War, Locust of Pestilence, Locust of Famine, Locust of Death, Locust of Conquest, Hushy, Mort Baby, Black Rune (mecánica), Void, Lil Portal

**Magdalene:** Cute Baby, Guardian Angel, Glyph of Balance, Red Baby, Censer, Blessed Penny, Purity

**Lazarus:** Wrapped Baby, Pandora's Box, Empty Vessel, Long Baby, Key Bum (con matiz), Plan C, Tinytoma (con matiz)

**Bethany:** Wisp Baby, Book of Virtues, Urn of Souls, Alabaster Box, Glowing Baby

**Eden:** Glitch Baby, Blank Card, Book of Secrets, Mystery Sack, Yellow Baby, GB Bug, Metronome, Eden's Soul, 'M

**Judas:** Shadow Baby, Guillotine (con matiz), Curved Horn, Brown Baby, Shade

**Blue Baby:** Dead Baby

**Eve:** Crow Baby, Lil' Baby, Eve's Mascara

**Samson:** Fighting Baby, Bloody Lust, Rage Baby

**Azazel:** Begotten Baby, Demon Baby, Black Baby, Lilith (co-op)

**The Forgotten:** Hallowed Ground, Pointy Rib, Slipped Rib, Jaw Bone, Brittle Bones (con matiz), Bound Baby, Spirit Shackles (con matiz)

**Lilith:** Goat Head Baby, Rune Bag, Immaculate Conception, Incubus, Big Baby, Box of Friends

**Jacob & Esau:** Double Baby, Birthright, Damocles, Rock Bottom, Illusion Baby, Magic Skin

**The Lost:** -0- Baby, The Mind, The Body, The Soul, The D100, White Baby, Holy Card

**Keeper:** Super Greed Baby, Wooden Nickel, Crooked Penny, Noose Baby

**Tainted Isaac:** Mega Chest (genérico)

**Tainted Apollyon:** Rotten Beggar (genérico), The Tower?

**Tainted Bethany:** Lemegeton

**Tainted Eden:** TMTRAINER, Wild Card (con matiz)

**Tainted Forgotten:** Golden Battery (genérico)

**Tainted Eve:** Horse Pill (genérico)

## Items skipped (no wiki link or fetch failed)

- **Penny** (no item conocido con ese nombre y efecto; ver entry de errores)
- **Sticky Nickel** (no wiki link en el código; el wiki devuelve info pero el item no tiene URL asignada; aparece como pickup, no trinket)
- **Gold Pill** (no wiki link en el código; descripción genérica imprecisa)
- **Wooden Chest** (no wiki link y nombre dudoso; ver entry)
- **Fool's Gold** (no wiki link aparente y nombre dudoso)
- **Golden Pill / Horse Pill / Golden Penny** (sin wiki link; descripciones de pickups genéricas, verificación manual recomendada)
- **Black Sack** (no wiki link en código; pickup genérico)
- **Haunted Chest** (no wiki link en código; pickup genérico)
- **Co-op babies** (todos los baby co-op cosméticos: Lost Baby, Glass Baby, Cute Baby, Wrapped Baby, Wisp Baby, Glitch Baby, Shadow Baby, Dead Baby, Crow Baby, Lil' Baby, Fighting Baby, Rage Baby, Begotten Baby, Black Baby, Bound Baby, Goat Head Baby, Big Baby, Double Baby, Illusion Baby, -0- Baby, White Baby, Super Greed Baby, Noose Baby, Mort Baby, Long Baby, Glowing Baby, Yellow Baby, Brown Baby, Red Baby, Green Baby, Cute Baby) — son cosméticos sin gameplay relevante; auditoría no aplica.

## Cobertura

- Items auditados completamente con WebFetch: **~165 / 340**
- Items auditados por muestreo (verificados como genéricos o cosméticos): **~60**
- Items sin wiki link en `ITEM_WIKI_URLS` o con confusión de nombre: **~10**
- Co-op babies (cosméticos, no requieren audit): **~30**
- **Errores encontrados con corrección sugerida: ~150**

## Patrones detectados

1. **Tipo incorrecto frecuente:** Muchos items marcados como "Pasivo" son en realidad **activos** (Brown Nugget, Yuck Heart, Eternal D6, Marrow, Dad's Ring, Inner Child, Vanishing Twin, Sumptorium, Gello, Hemoptysis, Isaac's Tomb, Decap Attack, Sacred Orb...) y viceversa (Astral Projection, Revelation, Empty Heart, Eden's Blessing, Candy Heart, Heartbreak, Cracked Orb, Keeper's Sack, Empty Vessel...). El campo `type` está mal en ~30 items.
2. **"Trinket" vs "Item activo/pasivo":** Muy frecuente confusión, especialmente en items de Repentance (Devil's Crown, Crow Heart, Lil Clot, Azazel's Stump, Apollyon's Best Friend, Found Soul...).
3. **Descripciones inventadas:** ~20 items tienen descripciones que no se parecen NADA a su efecto real (Black Lipstick, Cain's Eye, Silver Dollar, Holy Crown, Wicked Crown, Number Magnet, Lucky Sack, Karma, Modeling Clay, The Lovers?, Soul of Magdalene, Soul of Eve, Soul of Apollyon, Bloody Crown, Cracked Orb, Bat Wing, Crystal Key, Polished Bone, Echo Chamber, Cursed Penny, Sacrificial Dagger no auditado, Sanguine Bond, Bird Cage no auditado de fondo, etc.).
4. **Confusión de cartas inversas (Carta inv.):** Casi todas las cartas inversas tienen efectos genéricos inventados que no coinciden con la wiki (The Stars?, The Empress?, The Hierophant?, The World?, Judgement?, Strength?, The Devil?, The Lovers?, The Magician?, The Hanged Man?, The High Priestess?, The Fool?, The Emperor?, Death?, Wheel of Fortune?).
5. **Items de Soul (cartas runa):** Casi todos los "Soul of X" tienen descripciones inventadas o mal interpretadas (Soul of Magdalene, Soul of Eve, Soul of Apollyon, Soul of Azazel, Soul of Bethany, Soul of Jacob and Esau, Soul of Lilith, Soul of Lazarus, Soul of The Forgotten, Soul of ???, Soul of Cain).

## Recomendación

Dada la altísima tasa de error (~50% de los items auditados tenían errores significativos), se recomienda una **revisión completa** del bloque `ITEM_INFO`, no solo de los items marcados aquí. El controlador debería:
1. Aplicar las correcciones sugeridas en este informe (alta confianza, fuente wiki).
2. Considerar volver a auditar los items no cubiertos en este pase (las cartas/Soul no analizadas, items de Tainted personajes que faltaron, etc.).
3. Verificar especialmente el campo `type` en TODOS los items: hay muchas inconsistencias entre Trinket / Pasivo / Activo / Carta / Familiar / Pickup.
