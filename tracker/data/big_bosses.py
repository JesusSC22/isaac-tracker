"""Los 13 big bosses que aparecen en las marcas de completitud de cada personaje.

Esta lista debe estar alineada con MARK_BOSS_SPRITES en challenges.html.
"""
from __future__ import annotations

from typing import TypedDict


class BigBossEntry(TypedDict):
    idx: int
    name_es: str
    name_en: str
    sprite_url: str
    bestiary_key: tuple[int, int] | None
    kind: str  # "boss" | "event" | "transformation"


BIG_BOSSES: list[BigBossEntry] = [
    {"idx": 0, "name_es": "Corazón de Mamá", "name_en": "Mom's Heart",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Mom%27s_Heart_ingame.png",
     "bestiary_key": (78, 0), "kind": "boss"},
    {"idx": 1, "name_es": "Isaac",           "name_en": "Isaac",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Isaac_ingame.png",
     "bestiary_key": (102, 0), "kind": "boss"},
    {"idx": 2, "name_es": "Satán",           "name_en": "Satan",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Satan_ingame.png",
     "bestiary_key": None, "kind": "boss"},  # (84, 0) no está en BESTIARY_CATALOG
    {"idx": 3, "name_es": "???",             "name_en": "??? (Blue Baby)",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_%3F%3F%3F_ingame.png",
     "bestiary_key": (110, 0), "kind": "boss"},
    {"idx": 4, "name_es": "El Cordero",      "name_en": "The Lamb",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_The_Lamb_ingame.png",
     "bestiary_key": (273, 0), "kind": "boss"},
    {"idx": 5, "name_es": "Boss Rush",       "name_en": "Boss Rush",
     "sprite_url": "bossrush.png",  # local asset bundled with the app (no wiki URL — es un evento, no un enemigo)
     "bestiary_key": None, "kind": "event"},
    {"idx": 6, "name_es": "Hush",            "name_en": "Hush",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Hush_ingame.png",
     "bestiary_key": (407, 0), "kind": "boss"},
    {"idx": 7, "name_es": "Mega Satán",      "name_en": "Mega Satan",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Mega_Satan_ingame.png",
     "bestiary_key": None, "kind": "boss"},  # Mega Satan no está en BESTIARY_CATALOG
    {"idx": 8, "name_es": "Ultra Greed",     "name_en": "Ultra Greed",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Ultra_Greed_ingame.png",
     "bestiary_key": (406, 0), "kind": "boss"},
    {"idx": 9, "name_es": "Ultra Greedier",  "name_en": "Ultra Greedier",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Ultra_Greedier_ingame.png",
     "bestiary_key": None, "kind": "transformation"},
    {"idx": 10, "name_es": "Delirium",       "name_en": "Delirium",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Delirium_ingame.png",
     "bestiary_key": (412, 0), "kind": "boss"},
    {"idx": 11, "name_es": "Madre",          "name_en": "Mother",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_Mother_Full_portrait.png",
     "bestiary_key": (912, 0), "kind": "boss"},  # catalogado como "Mother's Shadow"
    {"idx": 12, "name_es": "La Bestia",      "name_en": "The Beast",
     "sprite_url": "https://bindingofisaacrebirth.wiki.gg/images/Boss_The_Beast_ingame.png",
     "bestiary_key": (951, 0), "kind": "boss"},
]

BIG_BOSS_BESTIARY_KEYS: set[tuple[int, int]] = {
    e["bestiary_key"] for e in BIG_BOSSES if e["bestiary_key"] is not None
}
