"""
Hitos de las dos máquinas de donación de Repentance+.

Todos los hitos están cross-validated contra
``tracker/data/achievements.json``. Cada entrada lleva el ``achievement_id``
correspondiente — la lógica de "hito desbloqueado" del state_mapper usa
fuente híbrida (counter >= amount OR achievement byte set), porque saves
upgraded desde Afterbirth+ tienen el counter a 0 pero los achievements
ya transferidos.

Ver: docs/superpowers/specs/2026-05-16-greed-donations-design.md
"""
from __future__ import annotations

# Greed Donation Machine — counters[19] del chunk 2 del save Repentance+.
GREED_DONATION_MILESTONES: list[dict] = [
    {"amount":    1, "achievement_id": 242, "name": "Lucky Pennies"},
    {"amount":   10, "achievement_id": 243, "name": "Special Hanging Shopkeepers"},
    {"amount":   30, "achievement_id": 244, "name": "Wooden Nickel"},
    {"amount":   68, "achievement_id": 245, "name": "Cain holds Paperclip"},
    {"amount":  111, "achievement_id": 246, "name": "Everything is Terrible 2!!!"},
    {"amount":  234, "achievement_id": 247, "name": "Special Shopkeepers"},
    {"amount":  439, "achievement_id": 248, "name": "Eve now holds Razor Blade"},
    {"amount":  666, "achievement_id": 249, "name": "Store Key"},
    {"amount":  879, "achievement_id": 250, "name": "Lost holds Holy Mantle"},
    {"amount": 1000, "achievement_id": 251, "name": "Keeper"},
]

# Donation Machine (normal, de tiendas) — counters[8] del chunk 2 del save Repentance+.
DONATION_MILESTONES: list[dict] = [
    {"amount":  10, "achievement_id": 134, "name": "Blue Map"},
    {"amount":  20, "achievement_id": 151, "name": "Store Upgrade lv.1"},
    {"amount":  50, "achievement_id": 135, "name": "There's Options"},
    {"amount": 100, "achievement_id": 152, "name": "Store Upgrade lv.2"},
    {"amount": 150, "achievement_id": 136, "name": "Black Candle"},
    {"amount": 200, "achievement_id": 153, "name": "Store Upgrade lv.3"},
    {"amount": 400, "achievement_id": 137, "name": "Red Candle"},
    {"amount": 600, "achievement_id": 154, "name": "Store Upgrade lv.4"},
    {"amount": 900, "achievement_id":  59, "name": "Blue Candle"},
    {"amount": 999, "achievement_id": 138, "name": "Stop Watch"},
]
