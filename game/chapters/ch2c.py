"""第二章 C 流程。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from story import ch2c as story

if TYPE_CHECKING:
    from game.app import GlobalStarApp


class Chapter2CMixin:
    """第二章 C：地下黑暗線。"""

    def _show_ch2c_viral(self: GlobalStarApp) -> None:
        body = story.CH2C_OPEN_BODY
        if self.player.get("hidden_producer"):
            body += story.CH2C_HIDDEN_PRODUCER_EXTRA

        self.show_scene(story.CH2C_TITLE, body, story.CH2C_OPEN_COMMENTS)
        self.clear_choice_buttons()

        def pick_commerce() -> None:
            self.apply_effects(
                {"fame": 15, "money": 12, "image": -8, "identity": -10}
            )
            self.update_status_panel()
            self._ch2c_show_result("commerce")

        def pick_underground() -> None:
            self.apply_effects(
                {"image": 12, "identity": 12, "fame": 3, "money": -3}
            )
            self.update_status_panel()
            self._ch2c_show_result("underground")

        def pick_pr() -> None:
            self.apply_effects(
                {
                    "fame": 18,
                    "controversy": 18,
                    "image": -12,
                    "identity": -5,
                    "health": -5,
                }
            )
            self.update_status_panel()
            nxt = (
                self._show_hidden_producer_reveal
                if self.player.get("hidden_producer")
                else self.show_chapter3
            )
            self._ch2c_show_result("pr", on_finish=nxt)

        self.add_choice("抓緊機會，接受商業化", pick_commerce)
        self.add_choice("順其自然，堅持地下風格", pick_underground)
        self.add_choice("操作輿論，把影響力最大化", pick_pr)

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

    def _show_hidden_producer_reveal(self: GlobalStarApp) -> None:
        self.show_scene(
            story.CH2C_REVEAL_TITLE,
            story.CH2C_REVEAL_BODY,
            story.CH2C_REVEAL_COMMENTS,
        )
        self.clear_choice_buttons()

        def pick_use() -> None:
            self.apply_effects(
                {"fame": 10, "controversy": 10, "identity": -10, "image": -5}
            )
            self.update_status_panel()
            self._ch2c_show_reveal_result("use")

        def pick_cut() -> None:
            self.apply_effects(
                {"image": 8, "identity": 10, "fame": -5, "health": -3}
            )
            self.update_status_panel()
            self._ch2c_show_reveal_result("cut")

        self.add_choice("繼續利用這股力量", pick_use)
        self.add_choice("試著切斷與神秘製作人的關係", pick_cut)

    def _ch2c_show_reveal_result(self: GlobalStarApp, key: str) -> None:
        result_title, result_body, comments = story.CH2C_REVEAL_RESULT_SCENES[key]
        self.show_result_scene(
            result_title,
            result_body,
            comments,
            self.show_chapter3,
        )
