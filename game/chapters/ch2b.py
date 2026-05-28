"""第二章 B 流程。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from game.images import ch2b_image_path
from story import ch2b as story

if TYPE_CHECKING:
    from game.app import GlobalStarApp


class Chapter2BMixin:
    """第二章 B：穩定成長線。"""

    def _show_ch2b_album(self: GlobalStarApp) -> None:
        """第二章 B：開場（032～034）與專輯方向抉擇。"""
        def show_album_choice() -> None:
            self.show_visual_scene(
                "034",
                story.CH2B_ALBUM_TITLE,
                comments=story.CH2B_ALBUM_CHOICE_COMMENTS,
                story_map=self._ch2b_stories,
                image_resolver=ch2b_image_path,
            )
            self.clear_choice_buttons()
            self.add_choice(
                "全權交由 A&R 打造商業專輯", self._ch2b_pick_commercial
            )
            self.add_choice("製作個人概念專輯", self._ch2b_pick_concept)
            self.add_choice("拒絕公司干涉，自己摸索", self._ch2b_pick_reject)

        self._ch2b_play(
            ["032", "033"],
            "",
            social_at=story.CH2B_ALBUM_OPEN_SOCIAL,
            on_finish=show_album_choice,
        )

    def _ch2b_pick_commercial(self: GlobalStarApp) -> None:
        self.apply_effects({"fame": 12, "money": 12, "image": -3, "identity": -8})
        self._album_type = "commercial"
        self.update_status_panel()
        self._ch2b_play(
            ["035", "036"],
            story.CH2B_DEFAULT_TITLE,
            social_at=story.CH2B_COMMERCIAL_SOCIAL,
            on_finish=self._show_ch2b_transition,
        )

    def _ch2b_pick_concept(self: GlobalStarApp) -> None:
        self.apply_effects({"image": 12, "identity": 8, "fame": 5, "money": -3})
        self._album_type = "concept"
        self.update_status_panel()
        self._ch2b_play(
            ["037", "038", "039", "040"],
            story.CH2B_DEFAULT_TITLE,
            social_at=story.CH2B_CONCEPT_SOCIAL,
            on_finish=self._show_ch2b_transition,
        )

    def _ch2b_pick_reject(self: GlobalStarApp) -> None:
        self.apply_effects(
            {"image": 8, "identity": 12, "money": -8, "fame": -3, "controversy": 5}
        )
        self._album_type = ""
        self.update_status_panel()
        self._ch2b_play(
            ["041", "042", "043"],
            story.CH2B_DEFAULT_TITLE,
            social_at=story.CH2B_REJECT_SOCIAL,
            on_finish=self.show_chapter3,
        )

    def _show_ch2b_transition(self: GlobalStarApp) -> None:
        """第二章 B：專輯後續抉擇（044 商業線 / 045 概念線）。"""
        at = self._album_type
        if at == "commercial":
            title = story.CH2B_TRANSITION_TITLES["commercial"]
            scene_id = "044"
        elif at == "concept":
            title = story.CH2B_TRANSITION_TITLES["concept"]
            scene_id = "045"
        else:
            self.show_chapter3()
            return

        def show_transition_choice() -> None:
            self.clear_choice_buttons()
            if at == "commercial":
                self.add_choice("延續商業路線，穩定賺錢", self._ch2b_pick_safe)
                self.add_choice(
                    "嘗試更個人、更小眾的風格", self._ch2b_pick_art
                )
            else:
                self.add_choice("保持現在風格，慢慢累積", self._ch2b_pick_slow)
                self.add_choice("改得更清楚、更市場化", self._ch2b_pick_market)

        self._ch2b_play(
            [scene_id],
            title,
            social_at={scene_id: story.CH2B_TRANSITION_SOCIAL[scene_id]},
            on_finish=show_transition_choice,
            final_continue=False,
        )

    def _ch2b_show_result(self: GlobalStarApp, key: str, *, on_finish=None) -> None:
        result_title, result_body, comments = story.CH2B_RESULT_SCENES[key]
        self.show_result_scene(
            result_title,
            result_body,
            comments,
            on_finish or self.show_chapter3,
        )

    def _ch2b_pick_safe(self: GlobalStarApp) -> None:
        self.apply_effects(
            {"fame": -25, "money": -5, "image": -20, "health": -70, "identity": -20}
        )
        self.player["forced_ending"] = "fallen"
        self.update_status_panel()
        self._ch2b_show_result("safe", on_finish=self.show_ending)

    def _ch2b_pick_art(self: GlobalStarApp) -> None:
        self.apply_effects({"image": 10, "identity": 8, "fame": 3, "money": -3})
        self.update_status_panel()
        self._ch2b_show_result("art")

    def _ch2b_pick_slow(self: GlobalStarApp) -> None:
        self.apply_effects({"image": 10, "identity": 10, "fame": 3, "money": -3})
        self.update_status_panel()
        self._ch2b_show_result("slow")

    def _ch2b_pick_market(self: GlobalStarApp) -> None:
        self.apply_effects(
            {"fame": 18, "money": 8, "image": -8, "health": -70, "identity": -18}
        )
        self.player["forced_ending"] = "fallen"
        self.update_status_panel()
        self._ch2b_show_result("market", on_finish=self.show_ending)
