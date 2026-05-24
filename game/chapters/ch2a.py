"""第二章 A 流程。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from game.images import ch2a_image_path
from story import ch2a as story

if TYPE_CHECKING:
    from game.app import GlobalStarApp


class Chapter2AMixin:
    """第二章 A：爆紅路線。"""

    def _show_ch2a_tour(self: GlobalStarApp) -> None:
        """第二章 A：爆紅路線開場（016～018）與巡演抉擇。"""
        title = story.CH2A_TOUR_TITLE

        def show_tour_choice() -> None:
            self.show_visual_scene(
                "018",
                title,
                comments=story.CH2A_TOUR_CHOICE_COMMENTS,
                story_map=self._ch2a_stories,
                image_resolver=ch2a_image_path,
            )
            self.clear_choice_buttons()
            self.add_choice("高強度巡演", self._ch2a_pick_high)
            self.add_choice("精緻小型巡演", self._ch2a_pick_small)

        self._ch2a_play(
            ["016", "017"],
            title,
            social_at=story.CH2A_TOUR_OPEN_SOCIAL,
            on_finish=show_tour_choice,
        )

    def _ch2a_pick_high(self: GlobalStarApp) -> None:
        self.apply_effects(
            {"fame": 12, "money": 8, "health": -15, "controversy": 5, "identity": -3}
        )
        self.update_status_panel()
        self._ch2a_play(
            ["019", "020", "021", "022", "023"],
            story.CH2A_DEFAULT_TITLE,
            social_at=story.CH2A_HIGH_TOUR_SOCIAL,
            on_finish=self._show_ch2a_crisis,
        )

    def _ch2a_pick_small(self: GlobalStarApp) -> None:
        self.apply_effects(
            {"fame": 5, "image": 10, "health": -5, "identity": 5, "money": 3}
        )
        self.update_status_panel()
        self._ch2a_play(
            ["024", "025"],
            story.CH2A_DEFAULT_TITLE,
            social_at=story.CH2A_SMALL_TOUR_SOCIAL,
            on_finish=self._show_ch2a_crisis,
        )

    def _show_ch2a_crisis(self: GlobalStarApp) -> None:
        """第二章 A：公關危機（026～028）與危機處置抉擇。"""
        title = story.CH2A_CRISIS_TITLE

        def show_crisis_choice() -> None:
            self.clear_choice_buttons()
            self.add_choice(
                "承認表達不夠好，自己發文道歉", self._ch2a_pick_apology
            )
            self.add_choice("發正式聲明，否認指控", self._ch2a_pick_statement)
            self.add_choice("不回應，等待風波過去", self._ch2a_pick_silent)

        self._ch2a_play(
            ["026", "027", "028"],
            title,
            social_at=story.CH2A_CRISIS_SOCIAL,
            on_finish=show_crisis_choice,
            final_continue=False,
        )

    def _ch2a_pick_apology(self: GlobalStarApp) -> None:
        self.apply_effects({"image": 8, "controversy": -5, "identity": 3, "fame": 3})
        self.update_status_panel()
        self._ch2a_play(
            ["029"],
            story.CH2A_DEFAULT_TITLE,
            social_at=story.CH2A_APOLOGY_SOCIAL,
            on_finish=self.show_chapter3,
        )

    def _ch2a_pick_statement(self: GlobalStarApp) -> None:
        self.apply_effects({"image": -5, "controversy": 8, "fame": 5, "identity": -3})
        self.update_status_panel()
        self._ch2a_play(
            ["030"],
            story.CH2A_DEFAULT_TITLE,
            social_at=story.CH2A_STATEMENT_SOCIAL,
            on_finish=self.show_chapter3,
        )

    def _ch2a_pick_silent(self: GlobalStarApp) -> None:
        self.apply_effects({"image": -8, "controversy": 5, "health": -5, "fame": 3})
        self.update_status_panel()
        self._ch2a_play(
            ["031"],
            story.CH2A_DEFAULT_TITLE,
            social_at=story.CH2A_SILENT_SOCIAL,
            on_finish=self.show_chapter3,
        )
