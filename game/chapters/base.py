"""章節共用：場景序列播放。"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from game.images import ch1_image_path, ch2a_image_path, ch2b_image_path
from story.ch1 import CH1_DEFAULT_SOCIAL

if TYPE_CHECKING:
    from game.app import GlobalStarApp


class SceneSequenceMixin:
    """依序播放帶圖場景的共用方法。"""

    def _play_scene_sequence(
        self: GlobalStarApp,
        scene_ids: List[str],
        title: str,
        *,
        story_map: Dict[str, str],
        image_resolver: Callable[[str], Optional[Path]],
        social_at: Optional[Dict[str, List[str]]] = None,
        on_finish: Callable[[], None],
        final_continue: bool = True,
    ) -> None:
        """依序播放多個帶圖場景，最後執行 on_finish。"""
        social_at = social_at or {}

        def play_at(index: int) -> None:
            sid = scene_ids[index]
            comments = social_at.get(sid, CH1_DEFAULT_SOCIAL)
            is_last = index + 1 >= len(scene_ids)
            if not is_last:
                nxt = lambda i=index + 1: play_at(i)
                self.show_visual_scene(
                    sid,
                    title,
                    comments=comments,
                    on_continue=nxt,
                    story_map=story_map,
                    image_resolver=image_resolver,
                )
            elif final_continue:
                self.show_visual_scene(
                    sid,
                    title,
                    comments=comments,
                    on_continue=on_finish,
                    story_map=story_map,
                    image_resolver=image_resolver,
                )
            else:
                self.show_visual_scene(
                    sid,
                    title,
                    comments=comments,
                    on_continue=None,
                    story_map=story_map,
                    image_resolver=image_resolver,
                )
                on_finish()

        play_at(0)

    def _ch1_play_sequence(
        self: GlobalStarApp,
        scene_ids: List[str],
        *,
        social_at: Optional[Dict[str, List[str]]] = None,
        on_finish: Callable[[], None],
    ) -> None:
        """第一章：依序播放帶圖場景。"""
        self._play_scene_sequence(
            scene_ids,
            "",
            story_map=self._ch1_stories,
            image_resolver=ch1_image_path,
            social_at=social_at,
            on_finish=on_finish,
        )

    def _ch2a_play(
        self: GlobalStarApp,
        scene_ids: List[str],
        title: str,
        *,
        social_at: Optional[Dict[str, List[str]]] = None,
        on_finish: Callable[[], None],
        final_continue: bool = True,
    ) -> None:
        """第二章 A：依序播放帶圖場景。"""
        self._play_scene_sequence(
            scene_ids,
            title,
            story_map=self._ch2a_stories,
            image_resolver=ch2a_image_path,
            social_at=social_at,
            on_finish=on_finish,
            final_continue=final_continue,
        )

    def _ch2b_play(
        self: GlobalStarApp,
        scene_ids: List[str],
        title: str,
        *,
        social_at: Optional[Dict[str, List[str]]] = None,
        on_finish: Callable[[], None],
        final_continue: bool = True,
    ) -> None:
        """第二章 B：依序播放帶圖場景。"""
        self._play_scene_sequence(
            scene_ids,
            title,
            story_map=self._ch2b_stories,
            image_resolver=ch2b_image_path,
            social_at=social_at,
            on_finish=on_finish,
            final_continue=final_continue,
        )
