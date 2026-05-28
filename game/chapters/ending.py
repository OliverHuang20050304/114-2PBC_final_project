"""結局流程。"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from game.paths import ENDING_VIDEO_DIR
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
        video_path = self._ending_video_path(title)
        if video_path is not None:
            self.add_choice(
                "播放結局影片",
                lambda p=video_path: self._open_ending_video(p),
            )
        self.add_choice("重新開始", self.restart_game)

    def _ending_video_path(self: GlobalStarApp, title: str) -> Path | None:
        """依結局標題回傳對應影片路徑。"""
        video_name = None
        if title.startswith("POP ICON"):
            video_name = "結局1.mp4"
        elif title.startswith("CONTROVERSIAL LEGEND"):
            video_name = "結局2.mp4"
        elif title.startswith("ARTISTIC ICON"):
            video_name = "結局3.mp4"
        elif title.startswith("FALLEN STAR"):
            video_name = "結局4.mp4"

        if video_name is None:
            return None
        path = ENDING_VIDEO_DIR / video_name
        return path if path.is_file() else None

    def _open_ending_video(self: GlobalStarApp, video_path: Path) -> None:
        """用系統預設播放器開啟結局影片。"""
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", str(video_path)])
            elif os.name == "nt":
                os.startfile(video_path)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(video_path)])
        except OSError as exc:
            self.update_social_reactions([f"影片無法開啟：{exc}"])

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
