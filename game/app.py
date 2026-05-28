"""
GLOBAL STAR：成名之路 — 主視窗與 UI。

劇情文字請編輯 story/ 套件；帶圖場景旁白請編輯 image/ 下的對照表 .txt。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import customtkinter as ctk
import pyglet

from game.chapters.base import SceneSequenceMixin
from game.chapters.ch1 import Chapter1Mixin
from game.chapters.ch2 import Chapter2Mixin
from game.chapters.ch2a import Chapter2AMixin
from game.chapters.ch2b import Chapter2BMixin
from game.chapters.ch2c import Chapter2CMixin
from game.chapters.ch3 import Chapter3Mixin
from game.chapters.ending import EndingMixin
from game.chapters.prologue import PrologueMixin
from game.images import ch1_image_path
from game.paths import (
    CH2A_STORY_FILE,
    CH2B_STORY_FILE,
    CH2C_STORY_FILE,
    SCENE_IMAGE_MAX_SIZE,
)
from game.player import apply_deltas, clamp_player, new_player
from game.story_io import format_narrative, load_ch1_story_map, load_story_map


class GlobalStarApp(
    SceneSequenceMixin,
    PrologueMixin,
    Chapter1Mixin,
    Chapter2Mixin,
    Chapter2AMixin,
    Chapter2BMixin,
    Chapter2CMixin,
    Chapter3Mixin,
    EndingMixin,
    ctk.CTk,
):
    """主視窗與遊戲流程控制。"""

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("GLOBAL STAR：成名之路")
        self.geometry("1180x820")
        self.minsize(960, 680)

        self.player: Dict[str, Any] = new_player()
        self._album_type: str = ""
        self._ch1_stories: Dict[str, str] = load_ch1_story_map()
        self._ch2a_stories: Dict[str, str] = load_story_map(CH2A_STORY_FILE)
        self._ch2b_stories: Dict[str, str] = load_story_map(CH2B_STORY_FILE)
        self._ch2c_stories: Dict[str, str] = load_story_map(CH2C_STORY_FILE)
        self._current_ctk_image: Optional[ctk.CTkImage] = None
        self._bgm_player = pyglet.media.Player()
        self._bgm_player.loop = True
        bgm_path = Path(__file__).resolve().parent.parent / "music" / "Bgm.mp3"
        if bgm_path.is_file():
            source = pyglet.media.load(str(bgm_path))
            self._bgm_player.queue(source)
            self._bgm_player.play()
        else:
            print(f"[BGM] 找不到音樂檔案：{bgm_path}")

        self._build_layout()
        self.show_cover()

    def _new_player_reset(self) -> Dict[str, Any]:
        """重新開始時建立新玩家狀態。"""
        return new_player()

    def clamp_stats(self) -> None:
        """將玩家數值限制在 0～100。"""
        clamp_player(self.player)

    def apply_effects(self, effects: Dict[str, int]) -> None:
        """套用屬性增減並重新 clamp。"""
        apply_deltas(self.player, effects)

    def update_status_panel(self) -> None:
        """更新右側狀態面板。"""
        self.clamp_stats()
        for key, lbl in self.stats_labels.items():
            val = int(self.player[key])
            lbl.configure(text=str(val))
            self.stats_bars[key].set(val / 100)

    def update_social_reactions(self, comments: List[str]) -> None:
        """更新社群留言區。"""
        self.set_social(comments)

    def clear_choice_buttons(self) -> None:
        """清除所有選項按鈕。"""
        for w in self.choices_frame.winfo_children():
            w.destroy()

    def restart_game(self) -> None:
        """重新開始遊戲。"""
        self.show_start()

    def restart_game(self) -> None:
        """重新開始遊戲。"""
        self.show_start()

    def show_cover(self) -> None:
        """開場封面畫面。"""
        self.clear_choice_buttons()
        self.update_social_reactions([""])
        
        cover_path = Path(__file__).resolve().parent.parent / "image" / "Pop_Idol_Base" / "封面圖.png"
        self.set_scene_image(cover_path)
        
        self.show_scene(
            "GLOBAL STAR：成名之路",
            "一位普通家庭的新人，即將踏上成名之路。",
            [""],
            clear_image=False,
        )
        self.add_choice("開始遊戲", self.show_start)

    def change_bgm(self, music_name: str) -> None:
        """切換背景音樂（重製播放器無敵版）
        :param music_name: 音樂檔案名稱，例如 "Pop.mp3", "Rebel.mp3", "Indie.mp3"
        """
        # 計算 music 資料夾的絕對路徑
        bgm_path = Path(__file__).resolve().parent.parent / "music" / music_name
        
        if bgm_path.is_file():
            try:
                # 1. 徹底停下舊的播放器並釋放
                if hasattr(self, "_bgm_player") and self._bgm_player:
                    self._bgm_player.pause()
                    self._bgm_player.delete()
                
                # 2. 直接重新創立一個乾淨的全新 Player 物件
                self._bgm_player = pyglet.media.Player()
                self._bgm_player.loop = True
                
                # 3. 載入並播放新音樂
                source = pyglet.media.load(str(bgm_path))
                self._bgm_player.queue(source)
                self._bgm_player.play()
                
            except Exception as e:
                print(f"❌ [BGM 失敗] 切換音樂時發生錯誤：{e}")
        else:
            print(f"⚠️ [BGM 錯誤] 找不到切換的音樂檔案：{bgm_path}")

    def show_scene(
        self,
        title: str,
        story: str,
        comments: Optional[List[str]] = None,
        *,
        clear_image: bool = True,
    ) -> None:
        """顯示標題與故事正文。"""
        if clear_image:
            self.clear_scene_image()
        body = f"{title}\n\n{story.strip()}" if title else story.strip()
        self.set_story(body)
        if comments is not None:
            self.update_social_reactions(comments)

    def show_result_scene(
        self,
        title: str,
        story: str,
        comments: List[str],
        next_function: Callable[[], None],
    ) -> None:
        """結果場景：敘述、社群反應、單一「繼續」按鈕。"""
        self.show_scene(title, story, comments)
        self.clear_choice_buttons()
        self.add_choice("繼續", next_function)

    def _build_layout(self) -> None:
        """建立介面區塊。"""
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self.title_label = ctk.CTkLabel(
            self,
            text="GLOBAL STAR：成名之路",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(12, 4), sticky="n")

        self.story_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.story_panel.grid(row=1, column=0, padx=(20, 10), pady=(6, 4), sticky="nsew")
        self.story_panel.grid_columnconfigure(0, weight=1)
        self.story_panel.grid_rowconfigure(0, weight=1)

        # 單一故事卡片：插圖與文字共用同一個有邊框的區域
        self.story_card = ctk.CTkFrame(
            self.story_panel,
            corner_radius=12,
            border_width=1,
        )
        self.story_card.grid(row=0, column=0, sticky="nsew")
        self.story_card.grid_columnconfigure(0, weight=1)
        self.story_card.grid_rowconfigure(0, weight=1)
        self.story_card.grid_rowconfigure(1, weight=0)

        self.scene_image_label = ctk.CTkLabel(
            self.story_card,
            text="",
            corner_radius=8,
        )
        self._story_card_padx = 12
        self._story_image_pady = (12, 8)
        self._story_text_pady = (0, 12)

        self.story_box = ctk.CTkTextbox(
            self.story_card,
            wrap="word",
            font=ctk.CTkFont(size=18),
            corner_radius=0,
            border_width=0,
            fg_color="transparent",
        )
        self.story_box.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=self._story_card_padx,
            pady=self._story_text_pady,
        )

        self.stats_frame = ctk.CTkFrame(self, corner_radius=12, border_width=1)
        self.stats_frame.grid(row=1, column=1, padx=(10, 20), pady=(6, 4), sticky="nsew")
        self.stats_labels: Dict[str, ctk.CTkLabel] = {}
        self.stats_bars: Dict[str, ctk.CTkProgressBar] = {}
        stat_keys = [
            ("fame", "名氣", "#F5C542"),
            ("image", "形象", "#5B9BD5"),
            ("health", "健康", "#6BCB77"),
            ("money", "金錢", "#E8A838"),
            ("identity", "自我認同", "#9B7EDE"),
            ("controversy", "爭議度", "#E05C5C"),
        ]
        for key, zh, bar_color in stat_keys:
            block = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            block.pack(fill="x", padx=14, pady=8)

            header = ctk.CTkFrame(block, fg_color="transparent")
            header.pack(fill="x")
            ctk.CTkLabel(
                header, text=zh, font=ctk.CTkFont(size=15, weight="bold")
            ).pack(side="left")
            lbl = ctk.CTkLabel(header, text="0", font=ctk.CTkFont(size=15))
            lbl.pack(side="right")
            self.stats_labels[key] = lbl

            bar = ctk.CTkProgressBar(
                block,
                height=14,
                corner_radius=7,
                progress_color=bar_color,
            )
            bar.pack(fill="x", pady=(6, 0))
            bar.set(0)
            self.stats_bars[key] = bar

        self.bottom = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 8))
        self.bottom.grid_columnconfigure(0, weight=1)
        self.bottom.grid_columnconfigure(1, weight=1)

        self.choices_outer = ctk.CTkFrame(self.bottom, corner_radius=12, border_width=1)
        self.choices_outer.grid(row=0, column=0, padx=(0, 8), pady=0, sticky="ew")
        ctk.CTkLabel(
            self.choices_outer,
            text="你的抉擇",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(6, 2))
        self.choices_frame = ctk.CTkFrame(self.choices_outer, fg_color="transparent")
        self.choices_frame.pack(fill="x", padx=4, pady=(0, 6))

        self.social_frame = ctk.CTkFrame(self.bottom, corner_radius=12, border_width=1)
        self.social_frame.grid(row=0, column=1, padx=(8, 0), pady=0, sticky="ew")

        ctk.CTkLabel(
            self.social_frame,
            text="社群反應",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=10, pady=(6, 2))

        self.social_text = ctk.CTkTextbox(
            self.social_frame,
            height=88,
            wrap="word",
            font=ctk.CTkFont(size=13),
            corner_radius=8,
        )
        self.social_text.pack(fill="x", expand=False, padx=8, pady=(0, 6))

    def set_story(self, text: str) -> None:
        """更新故事文字區。"""
        self.story_box.configure(state="normal")
        self.story_box.delete("1.0", "end")
        self.story_box.insert("1.0", text.strip())
        self.story_box.see("1.0")
        self.story_box.yview_moveto(0)
        self.story_box.configure(state="disabled")
        self.story_box.update_idletasks()

    def clear_scene_image(self) -> None:
        """隱藏場景插圖，文字區占滿故事卡片。"""
        self.scene_image_label.grid_remove()
        self.scene_image_label.configure(text="")
        self._current_ctk_image = None
        self.story_card.grid_rowconfigure(0, weight=1)
        self.story_card.grid_rowconfigure(1, weight=0)
        self.story_box.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=self._story_card_padx,
            pady=self._story_text_pady,
        )

    def _show_scene_image_label(self) -> None:
        """在故事卡片頂部顯示插圖，文字緊接在下方。"""
        self.story_card.grid_rowconfigure(0, weight=0)
        self.story_card.grid_rowconfigure(1, weight=1)
        self.scene_image_label.grid(
            row=0,
            column=0,
            sticky="n",
            padx=self._story_card_padx,
            pady=self._story_image_pady,
        )
        self.story_box.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=self._story_card_padx,
            pady=self._story_text_pady,
        )

    def set_scene_image(self, image_path: Optional[Path]) -> None:
        """顯示場景插圖（嵌入故事卡片頂部）。"""
        if image_path is None or not image_path.is_file():
            self.clear_scene_image()
            return
        try:
            from PIL import Image

            pil_img = Image.open(image_path).convert("RGB")
            # 依故事卡片寬度縮放，避免插圖過大把文字擠出視野
            max_w = min(SCENE_IMAGE_MAX_SIZE[0], 620)
            max_h = min(SCENE_IMAGE_MAX_SIZE[1], 240)
            pil_img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            self._current_ctk_image = ctk.CTkImage(
                light_image=pil_img,
                dark_image=pil_img,
                size=pil_img.size,
            )
            self._show_scene_image_label()
            self.scene_image_label.configure(
                image=self._current_ctk_image,
                text="",
            )
        except ImportError:
            self.clear_scene_image()
            if not getattr(self, "_pil_warned", False):
                self._pil_warned = True
                print(
                    "提示：請安裝 Pillow 以顯示場景插圖：pip install Pillow",
                    flush=True,
                )
        except OSError:
            self.clear_scene_image()

    def _narrative(
        self,
        story_map: Dict[str, str],
        scene_id: str,
        fallback: str = "",
    ) -> str:
        """從對照表取得並格式化旁白。"""
        raw = story_map.get(scene_id.zfill(3), fallback)
        return format_narrative(raw, self.player) if raw else fallback

    def show_visual_scene(
        self,
        scene_id: str,
        title: str,
        *,
        comments: Optional[List[str]] = None,
        fallback_story: str = "",
        on_continue: Optional[Callable[[], None]] = None,
        story_map: Optional[Dict[str, str]] = None,
        image_resolver: Optional[Callable[[str], Optional[Path]]] = None,
    ) -> None:
        """顯示帶插圖的場景，可選「繼續」按鈕。"""
        resolver = image_resolver or ch1_image_path
        smap = story_map or self._ch1_stories
        self.set_scene_image(resolver(scene_id))
        story = self._narrative(smap, scene_id, fallback_story)
        self.show_scene(title, story, comments, clear_image=False)
        self.clear_choice_buttons()
        if on_continue is not None:
            self.add_choice("繼續", on_continue)

    def set_social(self, lines: List[str]) -> None:
        """更新社群反應區。"""
        self.social_text.configure(state="normal")
        self.social_text.delete("1.0", "end")
        self.social_text.insert("1.0", "\n".join(lines))
        self.social_text.configure(state="disabled")

    def add_choice(self, text: str, command: Callable[[], None]) -> None:
        """新增一顆選項按鈕。"""
        btn = ctk.CTkButton(
            self.choices_frame,
            text=text,
            command=command,
            corner_radius=12,
            height=34,
            font=ctk.CTkFont(size=14),
        )
        btn.pack(fill="x", padx=8, pady=4)


def main() -> None:
    """程式進入點。"""
    app = GlobalStarApp()
    app.mainloop()
    
