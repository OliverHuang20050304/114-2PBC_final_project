"""第三章流程。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from story import ch3 as story

if TYPE_CHECKING:
    from game.app import GlobalStarApp


class Chapter3Mixin:
    """第三章：巨星的代價。"""

    def _chapter3_branch(self: GlobalStarApp) -> str:
        """決定第三章分支。"""
        p = self.player
        image = int(p["image"])
        fame = int(p["fame"])
        if image <= 40:
            return "controversial"
        if fame >= 75 and image >= 55:
            return "global_icon"
        return "mature_artist"

    def show_chapter3(self: GlobalStarApp) -> None:
        """第三章：依形象與名氣決定分支。"""
        branch = self._chapter3_branch()
        open_title, open_body, open_comments, choices = story.CH3_BRANCHES[branch]

        self.show_scene(open_title, open_body, open_comments)
        self.clear_choice_buttons()

        if branch == "global_icon":
            self.add_choice(
                "維持完美偶像人設",
                lambda: self._ch3_pick("global_icon", "idol"),
            )
            self.add_choice(
                "在作品中加入真正的自我",
                lambda: self._ch3_pick("global_icon", "self"),
            )
        elif branch == "mature_artist":
            self.add_choice(
                "配合獎季公關，穩定維持地位",
                lambda: self._ch3_pick("mature_artist", "pr"),
            )
            self.add_choice(
                "放棄部分商業利益，追求藝術突破",
                lambda: self._ch3_pick("mature_artist", "art"),
            )
        else:
            self.add_choice(
                "反擊媒體，擁抱負面標籤",
                lambda: self._ch3_pick("controversial", "fight"),
            )
            self.add_choice(
                "低頭道歉，試圖洗白",
                lambda: self._ch3_pick("controversial", "apology"),
            )

    def _ch3_pick(self: GlobalStarApp, branch: str, choice: str) -> None:
        _, _, _, choices = story.CH3_BRANCHES[branch]
        result_title, result_body, comments = choices[choice]

        effects_map = {
            ("global_icon", "idol"): {
                "fame": 10,
                "money": 10,
                "image": 3,
                "identity": -10,
                "health": -5,
            },
            ("global_icon", "self"): {
                "image": 12,
                "identity": 10,
                "fame": 3,
                "money": -3,
            },
            ("mature_artist", "pr"): {
                "fame": 10,
                "image": 5,
                "money": 8,
                "identity": -3,
            },
            ("mature_artist", "art"): {
                "image": 15,
                "identity": 12,
                "fame": 3,
                "money": -8,
            },
            ("controversial", "fight"): {
                "fame": 12,
                "controversy": 12,
                "image": -10,
                "identity": 3,
                "health": -5,
            },
            ("controversial", "apology"): {
                "image": 10,
                "controversy": -8,
                "fame": -5,
                "health": -3,
                "identity": -5,
            },
        }
        self.apply_effects(effects_map[(branch, choice)])
        self.update_status_panel()
        self.show_result_scene(
            result_title,
            result_body,
            comments,
            self._show_final_night,
        )

    def _show_final_night(self: GlobalStarApp) -> None:
        """第三章結束後、揭曉結局前的最終夜。"""
        self.show_scene(
            story.FINAL_NIGHT_TITLE,
            story.FINAL_NIGHT_BODY,
            story.FINAL_NIGHT_COMMENTS,
        )
        self.clear_choice_buttons()
        self.add_choice("查看最終結局", self.show_ending)
