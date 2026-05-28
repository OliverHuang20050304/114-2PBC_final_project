"""第二章 C 流程。"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from game.images import ch2c_image_path
from story import ch2c as story

if TYPE_CHECKING:
    from game.app import GlobalStarApp


class Chapter2CMixin:
    """第二章 C：地下黑暗線。"""

    def _show_ch2c_viral(self: GlobalStarApp) -> None:
        has_producer = bool(self.player.get("hidden_producer"))
        self.set_scene_image(ch2c_image_path("046"))
        self.show_scene(
            story.CH2C_TITLE,
            story.CH2C_OPEN_BODY,
            story.CH2C_OPEN_COMMENTS,
            clear_image=False,
        )
        self.clear_choice_buttons()
        self.add_choice("繼續", lambda: self._show_ch2c_decision(has_producer))

    def _show_ch2c_decision(self: GlobalStarApp, has_producer: bool) -> None:
        body = (
            story.CH2C_HIDDEN_PRODUCER_EXTRA
            if has_producer
            else story.CH2C_NO_PRODUCER_EXTRA
        )
        self.set_scene_image(ch2c_image_path("048" if has_producer else "047"))
        self.show_scene(
            story.CH2C_TITLE,
            body,
            story.CH2C_OPEN_COMMENTS,
            clear_image=False,
        )
        self.clear_choice_buttons()

        def pick_commerce() -> None:
            self.apply_effects(
                {"fame": 15, "money": 12, "image": -8, "identity": -10}
            )
            self.update_status_panel()
            self._ch2c_show_result("commerce", on_finish=self.show_chapter3)

        def pick_underground() -> None:
            self.apply_effects(
                {"fame": -15, "image": 5, "identity": 8, "money": -5}
            )
            self.player["forced_ending"] = "fallen"
            self.update_status_panel()
            self._ch2c_show_result("underground", on_finish=self.show_ending)

        def pick_respond() -> None:
            self.apply_effects(
                {
                    "fame": 20,
                    "controversy": 25,
                    "image": -18,
                    "identity": -5,
                    "health": -5,
                }
            )
            self.update_status_panel()
            self._ch2c_show_result("respond", on_finish=self.show_chapter3)

        def pick_investigate() -> None:
            if random.random() < 0.5:
                self.apply_effects(
                    {"fame": 12, "image": 25, "identity": 15, "controversy": -10}
                )
                self.player["route"] = "stable"
                self.update_status_panel()
                self._ch2c_show_result(
                    "investigate_success",
                    on_finish=self.show_chapter3,
                )
            else:
                self.apply_effects(
                    {
                        "fame": -30,
                        "image": -30,
                        "health": -20,
                        "controversy": 25,
                        "money": -10,
                    }
                )
                self.player["forced_ending"] = "fallen"
                self.update_status_panel()
                self._ch2c_show_result(
                    "investigate_fail",
                    on_finish=self.show_ending,
                )

        self.add_choice("抓緊機會，接受商業化", pick_commerce)
        self.add_choice("順其自然，沒有大動作", pick_underground)
        if has_producer:
            self.add_choice("回應網路反應", pick_respond)
            self.add_choice("私下展開調查", pick_investigate)

    def _ch2c_show_result(
        self: GlobalStarApp,
        key: str,
        *,
        on_finish=None,
    ) -> None:
        result_title, result_body, comments = story.CH2C_RESULT_SCENES[key]
        self.show_result_scene(
            result_title,
            result_body,
            comments,
            on_finish or self.show_chapter3,
        )
