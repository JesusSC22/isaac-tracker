"""
Hitos de las dos máquinas de donación de Repentance+.

Todos los hitos están cross-validated contra
``tracker/data/achievements.json``. Cada entrada lleva el ``achievement_id``
correspondiente — la lógica de "hito desbloqueado" del state_mapper usa
fuente híbrida (counter >= amount OR achievement byte set), porque saves
upgraded desde Afterbirth+ tienen el counter a 0 pero los achievements
ya transferidos.

Las descripciones (campo ``description``) están en español y resumen el
efecto del item/personaje/mejora desbloqueado, contrastadas contra la
wiki oficial de Repentance.

Ver: docs/superpowers/specs/2026-05-16-greed-donations-design.md
"""
from __future__ import annotations

# Greed Donation Machine — counters[19] del chunk 2 del save Repentance+.
GREED_DONATION_MILESTONES: list[dict] = [
    {"amount":    1, "achievement_id": 242, "name": "Lucky Pennies",
     "description": "Variante verde de moneda: vale 1 céntimo y otorga +1 de suerte al recogerla."},
    {"amount":   10, "achievement_id": 243, "name": "Special Hanging Shopkeepers",
     "description": "Aparecen tenderos colgantes con monedas en los ojos que sueltan varios céntimos al destruirlos."},
    {"amount":   30, "achievement_id": 244, "name": "Wooden Nickel",
     "description": "Activo de 1 carga: ~60% de probabilidad de soltar una moneda (penny, nickel o dime)."},
    {"amount":   68, "achievement_id": 245, "name": "Cain holds Paperclip",
     "description": "Trinket: permite abrir cofres cerrados sin gastar llaves."},
    {"amount":  111, "achievement_id": 246, "name": "Everything is Terrible 2!!!",
     "description": "Modo Greed se vuelve más difícil: las oleadas y Ultra Greed avanzan más rápido."},
    {"amount":  234, "achievement_id": 247, "name": "Special Shopkeepers",
     "description": "Aparecen tenderos especiales con monedas en los ojos que sueltan céntimos al reventarlos."},
    {"amount":  439, "achievement_id": 248, "name": "Eve now holds Razor Blade",
     "description": "Activo: te quita medio corazón rojo a cambio de +1.2 de daño durante la sala actual."},
    {"amount":  666, "achievement_id": 249, "name": "Store Key",
     "description": "Trinket: permite entrar a todas las tiendas sin gastar una llave."},
    {"amount":  879, "achievement_id": 250, "name": "Lost holds Holy Mantle",
     "description": "Escudo sagrado: anula el primer impacto recibido en cada sala."},
    {"amount": 1000, "achievement_id": 251, "name": "Keeper",
     "description": "Personaje que usa monedas como vida: empieza con 2 corazones-moneda y se cura recogiendo monedas."},
]

# Donation Machine (normal, de tiendas) — counters[8] del chunk 2 del save Repentance+.
DONATION_MILESTONES: list[dict] = [
    {"amount":  10, "achievement_id": 134, "name": "Blue Map",
     "description": "Revela en el mapa la ubicación de la Sala Secreta y la Super Secreta del piso."},
    {"amount":  20, "achievement_id": 151, "name": "Store Upgrade lv.1",
     "description": "La tienda pasa a tener más slots con artículos en venta en cada planta."},
    {"amount":  50, "achievement_id": 135, "name": "There's Options",
     "description": "Tras matar al jefe aparecen dos objetos en vez de uno, pero solo puedes llevarte uno."},
    {"amount": 100, "achievement_id": 152, "name": "Store Upgrade lv.2",
     "description": "Segunda ampliación de la tienda: aún más slots de artículos disponibles por planta."},
    {"amount": 150, "achievement_id": 136, "name": "Black Candle",
     "description": "Inmunidad a maldiciones del piso, otorga un corazón negro y +15% a la chance de Devil/Angel Room."},
    {"amount": 200, "achievement_id": 153, "name": "Store Upgrade lv.3",
     "description": "Tercera ampliación de la tienda: las paredes se llenan con todavía más artículos en venta."},
    {"amount": 400, "achievement_id": 137, "name": "Red Candle",
     "description": "Activo recargable: lanza una llama roja persistente que daña enemigos y bloquea proyectiles."},
    {"amount": 600, "achievement_id": 154, "name": "Store Upgrade lv.4",
     "description": "Cuarta y última ampliación: la tienda alcanza su capacidad máxima de artículos por planta."},
    {"amount": 900, "achievement_id":  59, "name": "Blue Candle",
     "description": "Activo gratuito: dispara una llama azul que hace 23 de daño por tick durante unos 2 segundos."},
    {"amount": 999, "achievement_id": 138, "name": "Stop Watch",
     "description": "Ralentiza a todos los enemigos al 80% de su velocidad de movimiento y ataque, y da +0.3 de velocidad."},
]
