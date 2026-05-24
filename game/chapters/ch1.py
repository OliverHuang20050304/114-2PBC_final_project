"""第一章流程。"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Dict, List

from game.story_io import format_narrative
from story import ch1 as story

if TYPE_CHECKING:
    from game.app import GlobalStarApp


class Chapter1Mixin:
    """第一章：第一首歌的代價。"""

    def show_chapter1(self: GlobalStarApp) -> None:
        """第一章開場（引言 000～002）。"""
        self._show_ch1_intro("000")

    def _show_ch1_intro(self: GlobalStarApp, scene_id: str) -> None:
        """第一章引言段落（000～002）。"""
        title = format_narrative(story.CH1_INTRO_TITLE, self.player)
        comments = story.CH1_INTRO_COMMENTS.get(scene_id, story.CH1_INTRO_COMMENTS["000"])

        if scene_id == "000":
            nxt = lambda: self._show_ch1_intro("001")
        elif scene_id == "001":
            nxt = lambda: self._show_ch1_intro("002")
        else:
            nxt = None

        self.show_visual_scene(
            scene_id,
            title,
            comments=comments,
            on_continue=nxt,
        )
        if scene_id == "002":
            self.clear_choice_buttons()
            self.add_choice("交給公司製作", self._ch1_route_a)
            self.add_choice("自己創作（成功或失敗隨機）", self._ch1_route_b_start)
            self.add_choice("與神秘製作人合作", self._ch1_route_c)

    def _ch1_route_a(self: GlobalStarApp) -> None:
        """路線 A：交給公司製作（003～006）。"""
        self._ch1_play_sequence(
            ["003", "004", "005", "006"],
            social_at=story.CH1_ROUTE_A_SOCIAL,
            on_finish=self._ch1_finish_route_a,
        )

    def _ch1_finish_route_a(self: GlobalStarApp) -> None:
        self.apply_effects({"fame": 8, "money": 5, "image": -3, "identity": -5})
        self.player["route"] = "stable"
        self.update_status_panel()
        self.show_chapter2()

    def _ch1_route_b_start(self: GlobalStarApp) -> None:
        """路線 B：自己創作（007 後隨機成功或失敗）。"""
        self._ch1_b_success = random.random() < 0.5
        scenes = ["007", "008", "009"] if self._ch1_b_success else ["007", "010"]
        social: Dict[str, List[str]] = {}
        for sid in scenes:
            if sid in story.CH1_ROUTE_B_SOCIAL:
                social[sid] = story.CH1_ROUTE_B_SOCIAL[sid]
        self._ch1_play_sequence(
            scenes,
            social_at=social,
            on_finish=self._ch1_finish_route_b,
        )

    def _ch1_finish_route_b(self: GlobalStarApp) -> None:
        if getattr(self, "_ch1_b_success", False):
            self.apply_effects(
                {"fame": 10, "image": 8, "identity": 5, "money": -3}
            )
            self.player["route"] = "rising"
        else:
            self.apply_effects(
                {"fame": -5, "image": 3, "identity": 3, "money": -3}
            )
            self.player["route"] = "hidden"
        self.update_status_panel()
        self.show_chapter2()

    def _ch1_route_c(self: GlobalStarApp) -> None:
        """路線 C：神秘製作人（011～015）。"""
        self._ch1_play_sequence(
            ["011", "012", "013", "014", "015"],
            social_at=story.CH1_ROUTE_C_SOCIAL,
            on_finish=self._ch1_finish_route_c,
        )

    def _ch1_finish_route_c(self: GlobalStarApp) -> None:
        self.apply_effects(
            {"fame": 10, "image": -3, "controversy": 8, "identity": -3}
        )
        self.player["hidden_producer"] = True
        self.player["route"] = "hidden"
        self.update_status_panel()
        self.show_chapter2()
