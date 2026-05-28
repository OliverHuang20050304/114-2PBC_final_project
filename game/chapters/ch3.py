"""第三章流程。"""

from __future__ import annotations

import random
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
        if p.get("route") == "rising" and image >= 55:
            return "global_icon"
        if fame >= 75 and image >= 55:
            return "global_icon"
        return "mature_artist"

    def show_chapter3(self: GlobalStarApp) -> None:
        """第三章：依形象與名氣決定分支。"""
        branch = self._chapter3_branch()
        if branch == "controversial" and self.player.get("hidden_producer"):
            branch = "controversial_hidden"
        open_title, open_body, open_comments, choices = story.CH3_BRANCHES[branch]

        self.show_scene(open_title, open_body, open_comments)
        self.clear_choice_buttons()

        if branch == "global_icon":
            self.add_choice(
                "簽約，接受奢侈品牌代言",
                lambda: self._ch3_pick("global_icon", "brand"),
            )
            self.add_choice(
                "拒絕，保留創作與價值觀自由",
                lambda: self._ch3_pick("global_icon", "refuse"),
            )
        elif branch == "mature_artist":
            self.add_choice(
                "堅持自我，不配合負責人",
                lambda: self._ch3_pick("mature_artist", "integrity"),
            )
            self.add_choice(
                "達成協議，利益交換",
                self._ch3_pick_awards_deal,
            )
        elif branch == "controversial":
            self.add_choice(
                "反擊媒體，擁抱負面標籤",
                lambda: self._ch3_pick("controversial", "fight"),
            )
            self.add_choice(
                "低頭道歉，試圖洗白",
                lambda: self._ch3_pick("controversial", "apology"),
            )
        else:
            self.add_choice(
                "擁抱深淵，如約進行演唱會",
                lambda: self._ch3_pick("controversial_hidden", "abyss"),
            )
            self.add_choice(
                "魚死網破，在演唱會上揭穿真相",
                lambda: self._ch3_pick("controversial_hidden", "reveal"),
            )

    def _ch3_pick_awards_deal(self: GlobalStarApp) -> None:
        """獎季利益交換：成功或曝光隨機。"""
        choice = "deal" if random.random() < 0.5 else "deal_exposed"
        self._ch3_pick("mature_artist", choice)

    def _ch3_pick(self: GlobalStarApp, branch: str, choice: str) -> None:
        _, _, _, choices = story.CH3_BRANCHES[branch]
        result_title, result_body, comments = choices[choice]

        effects_map = {
            ("global_icon", "brand"): {
                "fame": 10,
                "money": 10,
                "image": 3,
                "identity": -10,
                "health": -5,
            },
            ("global_icon", "refuse"): {
                "image": 20,
                "identity": 18,
                "fame": 5,
                "money": -3,
            },
            ("mature_artist", "integrity"): {
                "image": 25,
                "identity": 20,
                "fame": 5,
                "money": -5,
            },
            ("mature_artist", "deal"): {
                "fame": 20,
                "image": 10,
                "money": 15,
                "identity": -15,
                "controversy": 5,
            },
            ("mature_artist", "deal_exposed"): {
                "fame": -35,
                "image": -35,
                "money": -20,
                "health": -20,
                "controversy": 35,
                "identity": -20,
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
            ("controversial_hidden", "abyss"): {
                "fame": 20,
                "controversy": 20,
                "image": -10,
                "identity": -20,
                "health": -8,
            },
            ("controversial_hidden", "reveal"): {
                "fame": -35,
                "image": -30,
                "health": -20,
                "money": -20,
                "controversy": 25,
            },
        }
        forced_endings = {
            ("global_icon", "brand"): "pop_icon",
            ("global_icon", "refuse"): "artistic",
            ("mature_artist", "integrity"): "artistic",
            ("mature_artist", "deal"): "pop_icon",
            ("mature_artist", "deal_exposed"): "fallen",
            ("controversial", "fight"): "controversial",
            ("controversial", "apology"): "fallen",
            ("controversial_hidden", "abyss"): "controversial",
            ("controversial_hidden", "reveal"): "fallen",
        }
        self.apply_effects(effects_map[(branch, choice)])
        self.player["forced_ending"] = forced_endings[(branch, choice)]
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
