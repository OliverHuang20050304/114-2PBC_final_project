"""第二章分流。"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.app import GlobalStarApp


class Chapter2Mixin:
    """第二章：依第一章路線分流。"""

    def show_chapter2(self: GlobalStarApp) -> None:
        """第二章入口。"""
        route = self.player.get("route", "")
        if route == "rising":
            self._show_ch2a_tour()
        elif route == "stable":
            self._show_ch2b_album()
        elif route == "hidden":
            self._show_ch2c_viral()
        else:
            self.player["route"] = "stable"
            self._show_ch2b_album()
