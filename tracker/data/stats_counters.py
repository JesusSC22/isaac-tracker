"""Índices del chunk 2 (counters) confirmados en saves reales.

Cada entrada se añade SOLO cuando ha sido validada mediante diff de saves
(jugar → guardar → comparar). NO añadir índices sin validar.
"""
from __future__ import annotations

GLOBAL_STAT_COUNTERS: list[dict] = [
    {"index": 8,  "key": "donations_normal", "label_es": "Donaciones (tienda)", "icon": "coin"},
    {"index": 19, "key": "donations_greed",  "label_es": "Donaciones (Greed)",  "icon": "coin_gold"},
]
