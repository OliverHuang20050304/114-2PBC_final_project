"""玩家狀態與數值計算。"""

from __future__ import annotations

from typing import Any, Dict


def clamp_player(player: Dict[str, Any]) -> None:
    """將數值型屬性限制在 0 到 100 之間。"""
    for key in ("fame", "image", "health", "money", "identity", "controversy"):
        if key in player:
            val = int(player[key])
            player[key] = max(0, min(100, val))


def new_player() -> Dict[str, Any]:
    """建立新的玩家狀態字典。"""
    return {
        "city": "",
        "style": "",
        "fame": 30,
        "image": 50,
        "health": 80,
        "money": 20,
        "identity": 70,
        "controversy": 0,
        "hidden_producer": False,
        "route": "",
    }


def apply_deltas(player: Dict[str, Any], deltas: Dict[str, int]) -> None:
    """套用數值變化（不含 hidden_producer 布林）。"""
    for key, delta in deltas.items():
        if key in player and isinstance(player[key], (int, float)):
            player[key] += delta
    clamp_player(player)
