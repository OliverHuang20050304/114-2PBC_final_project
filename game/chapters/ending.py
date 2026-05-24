"""結局流程。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from story import endings as story

if TYPE_CHECKING:
    from game.app import GlobalStarApp


class EndingMixin:
    """結局顯示與重新開始。"""

    def show_ending(self: GlobalStarApp) -> None:
        """顯示結局、最終數值與重新開始。"""
        self.clamp_stats()
        self.clear_scene_image()
        title, body = story.compute_ending(self.player)
        stats_block = self._format_final_stats()
        full_text = f"ENDING：{title}\n\n{body}\n\n{stats_block}"
        self.set_story(full_text)
        self.update_social_reactions(story.ENDING_SOCIAL)
        self.clear_choice_buttons()
        self.add_choice("重新開始", self.restart_game)

    def _format_final_stats(self: GlobalStarApp) -> str:
        """結局畫面用的最終數值摘要。"""
        p = self.player
        hp = "是" if p.get("hidden_producer") else "否"
        lines = [
            "── 最終狀態 ──",
            f"城市：{p.get('city') or '—'}",
            f"風格：{p.get('style') or '—'}",
            f"路線：{p.get('route') or '—'}",
            f"神秘製作線索：{hp}",
            f"名氣：{int(p['fame'])}　形象：{int(p['image'])}　健康：{int(p['health'])}",
            f"金錢：{int(p['money'])}　自我認同：{int(p['identity'])}　爭議度：{int(p['controversy'])}",
        ]
        return "\n".join(lines)
