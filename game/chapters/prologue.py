"""序章流程。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from story import prologue as story

if TYPE_CHECKING:
    from game.app import GlobalStarApp


class PrologueMixin:
    """序章：城市與風格選擇。"""

    def show_start(self: GlobalStarApp) -> None:
        """序章開始畫面。"""
        self.player = self._new_player_reset()
        self._album_type = ""
        self.update_status_panel()
        self.update_social_reactions(story.PROLOGUE_START_COMMENTS)
        self.show_scene(
            story.PROLOGUE_START_TITLE,
            story.PROLOGUE_START_BODY,
            story.PROLOGUE_START_COMMENTS,
        )
        self.clear_choice_buttons()
        self.add_choice("開始遊戲", self.show_city_selection)

    def show_city_selection(self: GlobalStarApp) -> None:
        """序章：選擇發展城市。"""
        self.show_scene(
            story.PROLOGUE_CITY_TITLE,
            story.PROLOGUE_CITY_BODY,
            story.PROLOGUE_CITY_COMMENTS,
        )
        self.clear_choice_buttons()

        def pick(city: str) -> None:
            self.player["city"] = city
            self.apply_effects(story.CITY_EFFECTS[city])
            self.update_status_panel()
            self.show_style_selection()

        self.add_choice("洛杉磯", lambda: pick("洛杉磯"))
        self.add_choice("倫敦", lambda: pick("倫敦"))
        self.add_choice("紐約", lambda: pick("紐約"))

    def show_style_selection(self: GlobalStarApp) -> None:
        """序章：選擇出道風格。"""
        self.show_scene(
            story.PROLOGUE_STYLE_TITLE,
            story.PROLOGUE_STYLE_BODY,
            story.PROLOGUE_STYLE_COMMENTS,
        )
        self.clear_choice_buttons()

        def pick(style: str) -> None:
            self.player["style"] = style
            self.apply_effects(story.STYLE_EFFECTS[style])
            self.update_status_panel()
            self.show_chapter1()

        for label in story.STYLE_EFFECTS:
            self.add_choice(label, lambda s=label: pick(s))
