"""
GLOBAL STAR：成名之路 — 以 CustomTkinter 製作的敘事模擬遊戲。
"""

from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import customtkinter as ctk

PROJECT_ROOT = Path(__file__).resolve().parent
CH1_IMAGE_ROOT = PROJECT_ROOT / "image" / "Pop_Idol_Base" / "CH1"
CH1_INTRO_DIR = CH1_IMAGE_ROOT / "引言"
CH1_STORY_FILE = CH1_IMAGE_ROOT / "圖片文本對照.txt"
CH1_BRANCH_DIRS: Dict[str, Path] = {
    "a": CH1_IMAGE_ROOT / "a.交給公司製作",
    "b": CH1_IMAGE_ROOT / "b.自己創作",
    "c": CH1_IMAGE_ROOT / "c.與神秘製作人合作",
}
CH2A_ROOT = PROJECT_ROOT / "image" / "Pop_Idol_Base" / "CH2" / "2A爆紅"
CH2A_STORY_FILE = CH2A_ROOT / "圖片文本對照Idol_CH2A.txt"
CH2A_EVENT1_DIR = CH2A_ROOT / "2A事件一"
CH2A_EVENT2_DIR = CH2A_ROOT / "2A事件二"
CH2B_ROOT = PROJECT_ROOT / "image" / "Pop_Idol_Base" / "CH2" / "2B穩定成長"
CH2B_STORY_FILE = CH2B_ROOT / "圖片文本對照Idol_CH2B.txt"
CH2B_EVENT1_DIR = CH2B_ROOT / "2B事件一"
CH2B_EVENT2_DIR = CH2B_ROOT / "2B事件二"
SCENE_IMAGE_MAX_SIZE = (680, 380)


def clamp_player(player: Dict[str, Any]) -> None:
    """將數值型屬性限制在 0 到 100 之間。"""
    for key in ("fame", "image", "health", "money", "identity", "controversy"):
        if key in player:
            val = int(player[key])
            player[key] = max(0, min(100, val))


def new_player() -> Dict[str, Any]:
    """建立新的玩家狀態字典。"""
    return {
        "city": "",
        "style": "",
        "fame": 30,
        "image": 50,
        "health": 80,
        "money": 20,
        "identity": 70,
        "controversy": 0,
        "hidden_producer": False,
        "route": "",
    }


def apply_deltas(player: Dict[str, Any], deltas: Dict[str, int]) -> None:
    """套用數值變化（不含 hidden_producer 布林）。"""
    for key, delta in deltas.items():
        if key in player and isinstance(player[key], (int, float)):
            player[key] += delta
    clamp_player(player)


def clean_story_text(text: str) -> str:
    """清理對照表中的格式殘留。"""
    cleaned = re.sub(r"^status_flavor\s*=\s*\"\"\"?\s*", "", text.strip())
    return cleaned.replace('"""', "").strip()


def load_story_map(path: Path) -> Dict[str, str]:
    """讀取圖片編號與旁白對照表。"""
    if not path.is_file():
        return {}
    stories: Dict[str, str] = {}
    current_id: Optional[str] = None
    buffer: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.fullmatch(r"\d{3}", line.strip()):
            if current_id is not None:
                stories[current_id] = clean_story_text("\n".join(buffer))
            current_id = line.strip()
            buffer = []
        elif current_id is not None:
            buffer.append(line)
    if current_id is not None:
        stories[current_id] = clean_story_text("\n".join(buffer))
    return stories


def load_ch1_story_map(path: Path = CH1_STORY_FILE) -> Dict[str, str]:
    """讀取第一章圖片編號與旁白對照表。"""
    return load_story_map(path)


def format_narrative(text: str, player: Dict[str, Any]) -> str:
    """替換旁白中的城市、風格等佔位符。"""
    city = str(player.get("city") or "這座城市")
    style = str(player.get("style") or "流行")
    formatted = text.replace("{city_name}", city).replace("{style}", style)
    return formatted.replace("**", "")


def format_ch1_narrative(text: str, player: Dict[str, Any]) -> str:
    """第一章旁白格式化（相容舊名稱）。"""
    return format_narrative(text, player)


def ch1_image_path(scene_id: str) -> Optional[Path]:
    """依場景編號回傳對應 JPG 路徑。"""
    sid = scene_id.zfill(3)
    intro = CH1_INTRO_DIR / f"{sid}.jpg"
    if intro.is_file():
        return intro
    num = int(sid)
    if 3 <= num <= 6:
        return CH1_BRANCH_DIRS["a"] / f"{sid}.jpg"
    if 7 <= num <= 10:
        return CH1_BRANCH_DIRS["b"] / f"{sid}.jpg"
    if 11 <= num <= 15:
        return CH1_BRANCH_DIRS["c"] / f"{sid}.jpg"
    return None


def ch2a_image_path(scene_id: str) -> Optional[Path]:
    """依場景編號回傳第二章 A 路線 JPG 路徑。"""
    sid = scene_id.zfill(3)
    num = int(sid)
    if 16 <= num <= 17:
        path = CH2A_ROOT / f"{sid}.jpg"
    elif 18 <= num <= 25:
        path = CH2A_EVENT1_DIR / f"{sid}.jpg"
    elif 26 <= num <= 31:
        path = CH2A_EVENT2_DIR / f"{sid}.jpg"
    else:
        return None
    return path if path.is_file() else None


def ch2b_image_path(scene_id: str) -> Optional[Path]:
    """依場景編號回傳第二章 B 路線 JPG 路徑。"""
    sid = scene_id.zfill(3)
    num = int(sid)
    if num == 32:
        path = CH2B_ROOT / f"{sid}.jpg"
    elif 33 <= num <= 43:
        path = CH2B_EVENT1_DIR / f"{sid}.jpg"
    elif 44 <= num <= 45:
        path = CH2B_EVENT2_DIR / f"{sid}.jpg"
    else:
        return None
    return path if path.is_file() else None


class GlobalStarApp(ctk.CTk):
    """主視窗與遊戲流程控制。"""

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("GLOBAL STAR：成名之路")
        self.geometry("1180x820")
        self.minsize(960, 680)

        self.player: Dict[str, Any] = new_player()
        # 第二章 B 路線：第一張專輯選項 A/B 後的專輯類型（過場用）
        self._album_type: str = ""
        self._ch1_stories: Dict[str, str] = load_ch1_story_map()
        self._ch2a_stories: Dict[str, str] = load_story_map(CH2A_STORY_FILE)
        self._ch2b_stories: Dict[str, str] = load_story_map(CH2B_STORY_FILE)
        self._current_ctk_image: Optional[ctk.CTkImage] = None

        self._build_layout()
        self.show_start()

    # --- 輔助函式（與規格命名對齊） ---

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
            lbl.configure(text=str(int(self.player[key])))

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

    def show_scene(
        self,
        title: str,
        story: str,
        comments: Optional[List[str]] = None,
        *,
        clear_image: bool = True,
    ) -> None:
        """顯示標題與故事正文（標題與內文分開顯示）。"""
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
        """結果場景：一段敘述、社群反應、單一「繼續」按鈕後進入下一階段。"""
        self.show_scene(title, story, comments)
        self.clear_choice_buttons()
        self.add_choice("繼續", next_function)

    def _build_layout(self) -> None:
        """建立介面區塊。"""
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text="GLOBAL STAR：成名之路",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(16, 8), sticky="n")

        self.story_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.story_panel.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        self.story_panel.grid_columnconfigure(0, weight=1)
        self.story_panel.grid_rowconfigure(1, weight=1)

        self.scene_image_label = ctk.CTkLabel(
            self.story_panel,
            text="",
            corner_radius=12,
        )
        self._scene_image_grid = {"row": 0, "column": 0, "pady": (0, 8), "sticky": "n"}
        # 初始不佔版面；有插圖時再 grid

        self.story_box = ctk.CTkTextbox(
            self.story_panel,
            wrap="word",
            font=ctk.CTkFont(size=18),
            corner_radius=12,
            border_width=1,
        )
        self.story_box.grid(row=1, column=0, sticky="nsew")

        self.stats_frame = ctk.CTkFrame(self, corner_radius=12, border_width=1)
        self.stats_frame.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        self.stats_labels: Dict[str, ctk.CTkLabel] = {}
        stat_keys = [
            ("fame", "名氣"),
            ("image", "形象"),
            ("health", "健康"),
            ("money", "金錢"),
            ("identity", "自我認同"),
            ("controversy", "爭議度"),
        ]
        for _i, (key, zh) in enumerate(stat_keys):
            row = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=6)
            ctk.CTkLabel(
                row, text=f"{zh}：", font=ctk.CTkFont(size=15, weight="bold")
            ).pack(side="left")
            lbl = ctk.CTkLabel(row, text="0", font=ctk.CTkFont(size=15))
            lbl.pack(side="right")
            self.stats_labels[key] = lbl

        self.bottom = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))
        self.bottom.grid_columnconfigure(0, weight=1)
        self.bottom.grid_columnconfigure(1, weight=1)

        self.choices_outer = ctk.CTkFrame(self.bottom, corner_radius=12, border_width=1)
        self.choices_outer.grid(row=0, column=0, padx=(0, 8), pady=0, sticky="nsew")
        ctk.CTkLabel(
            self.choices_outer,
            text="你的抉擇",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(10, 4))
        self.choices_frame = ctk.CTkFrame(self.choices_outer, fg_color="transparent")
        self.choices_frame.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        self.social_frame = ctk.CTkFrame(self.bottom, corner_radius=12, border_width=1)
        self.social_frame.grid(row=0, column=1, padx=(8, 0), pady=0, sticky="nsew")

        ctk.CTkLabel(
            self.social_frame,
            text="社群反應",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(10, 4))

        self.social_text = ctk.CTkTextbox(
            self.social_frame,
            height=160,
            wrap="word",
            font=ctk.CTkFont(size=14),
            corner_radius=10,
        )
        self.social_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def set_story(self, text: str) -> None:
        """更新故事文字區。"""
        self.story_box.configure(state="normal")
        self.story_box.delete("1.0", "end")
        self.story_box.insert("1.0", text.strip())
        self.story_box.configure(state="disabled")

    def clear_scene_image(self) -> None:
        """隱藏場景插圖（避免 image=None 觸發 TclError）。"""
        self._current_ctk_image = None
        self.scene_image_label.grid_remove()

    def _show_scene_image_label(self) -> None:
        """顯示插圖區塊。"""
        self.scene_image_label.grid(**self._scene_image_grid)

    def set_scene_image(self, image_path: Optional[Path]) -> None:
        """顯示場景插圖（依視窗比例縮放）；缺少 Pillow 時略過圖片但不阻斷流程。"""
        if image_path is None or not image_path.is_file():
            self.clear_scene_image()
            return
        try:
            from PIL import Image

            pil_img = Image.open(image_path).convert("RGB")
            pil_img.thumbnail(SCENE_IMAGE_MAX_SIZE, Image.Resampling.LANCZOS)
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

    def _ch1_narrative(self, scene_id: str, fallback: str = "") -> str:
        """取得第一章某場景的旁白文字。"""
        return self._narrative(self._ch1_stories, scene_id, fallback)

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

    def refresh_stats(self) -> None:
        """與 update_status_panel 相同，保留舊名稱相容。"""
        self.update_status_panel()

    def clear_choices(self) -> None:
        """與 clear_choice_buttons 相同。"""
        self.clear_choice_buttons()

    def add_choice(self, text: str, command: Callable[[], None]) -> None:
        """新增一顆選項按鈕。"""
        btn = ctk.CTkButton(
            self.choices_frame,
            text=text,
            command=command,
            corner_radius=14,
            height=40,
            font=ctk.CTkFont(size=15),
        )
        btn.pack(fill="x", padx=12, pady=8)

    # --- 遊戲流程 ---

    def show_start(self) -> None:
        """序章開始畫面。"""
        self.player = new_player()
        self._album_type = ""
        self.update_status_panel()
        self.update_social_reactions(["（尚未有留言）"])
        self.show_scene(
            "PROLOGUE：成名之前",
            "「你是一位來自普通家庭的新人，剛與 Creative Artist Records 簽約。"
            "你即將踏上成名之路。」",
            ["（尚未有留言）"],
        )
        self.clear_choice_buttons()
        self.add_choice("開始遊戲", self.show_city_selection)

    def show_city_selection(self) -> None:
        """序章：選擇發展城市。"""
        self.show_scene(
            "PROLOGUE：落腳的城市",
            "請選擇你主要發展的城市：",
            ["（粉絲還在觀望中…）"],
        )
        self.clear_choice_buttons()

        def pick_la() -> None:
            self.player["city"] = "洛杉磯"
            self.apply_effects({"fame": 5, "image": -3})
            self.update_status_panel()
            self.show_style_selection()

        def pick_london() -> None:
            self.player["city"] = "倫敦"
            self.apply_effects({"image": 5, "fame": 3})
            self.update_status_panel()
            self.show_style_selection()

        def pick_ny() -> None:
            self.player["city"] = "紐約"
            self.apply_effects({"fame": 3, "money": 5})
            self.update_status_panel()
            self.show_style_selection()

        self.add_choice("洛杉磯", pick_la)
        self.add_choice("倫敦", pick_london)
        self.add_choice("紐約", pick_ny)

    def show_style_selection(self) -> None:
        """序章：選擇出道風格。"""
        self.show_scene(
            "PROLOGUE：你要成為誰",
            "請選擇你的出道風格：",
            ["@musicdaily：新簽約藝人即將曝光？"],
        )
        self.clear_choice_buttons()

        def pick_rebel() -> None:
            self.player["style"] = "叛逆流派 Rebel"
            self.apply_effects({"fame": 5, "controversy": 5, "image": -3})
            self.update_status_panel()
            self.show_chapter1()

        def pick_pop() -> None:
            self.player["style"] = "商業流行 Pop Idol"
            self.apply_effects({"fame": 3, "money": 5, "identity": -3})
            self.update_status_panel()
            self.show_chapter1()

        def pick_indie() -> None:
            self.player["style"] = "藝術地下 Indie"
            self.apply_effects({"image": 8, "fame": -3, "identity": 5})
            self.update_status_panel()
            self.show_chapter1()

        self.add_choice("叛逆流派 Rebel", pick_rebel)
        self.add_choice("商業流行 Pop Idol", pick_pop)
        self.add_choice("藝術地下 Indie", pick_indie)

    def show_chapter1(self) -> None:
        """第一章：第一首歌的代價（插圖 + 對照旁白）。"""
        self._show_ch1_intro("000")

    def _show_ch1_intro(self, scene_id: str) -> None:
        """第一章引言段落（000～002）。"""
        title = "CHAPTER 1：第一首歌的代價"
        comments = ["（歌迷正在刷新頁面…）"]
        if scene_id == "001":
            comments = ["@agent_creative：我們要決定你的第一首歌了。"]
        elif scene_id == "002":
            comments = ["@musicdaily：新人的出道曲會走哪條路？"]

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

    def _ch1_route_a(self) -> None:
        """路線 A：交給公司製作（003～006）。"""
        self._ch1_play_sequence(
            ["003", "004", "005", "006"],
            social_at={"005": [
                "@musicdaily：這新人很穩欸",
                "@popfan：感覺會紅",
                "@critic_room：但有點……沒特色?",
            ]},
            on_finish=self._ch1_finish_route_a,
        )

    def _ch1_finish_route_a(self) -> None:
        self.apply_effects({"fame": 8, "money": 5, "image": -3, "identity": -5})
        self.player["route"] = "stable"
        self.update_status_panel()
        self.show_chapter2()

    def _ch1_route_b_start(self) -> None:
        """路線 B：自己創作（007 後隨機成功或失敗）。"""
        self._ch1_b_success = random.random() < 0.5
        scenes = ["007", "008", "009"] if self._ch1_b_success else ["007", "010"]
        social: Dict[str, List[str]] = {}
        if "008" in scenes:
            social["008"] = [
                "@stanaccount：這首歌是誰寫的?",
                "@musicdaily：有點太真實了吧...",
                "@critic_room：我直接哭出來",
            ]
        if "010" in scenes:
            social["010"] = [
                "@popwatch：這首歌好像沒什麼聲量。",
                "@industrytalk：公司應該開始緊張了。",
                "@smallfan：我其實覺得很好聽，只是大家還沒發現。",
            ]
        self._ch1_play_sequence(
            scenes,
            social_at=social,
            on_finish=self._ch1_finish_route_b,
        )

    def _ch1_finish_route_b(self) -> None:
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

    def _ch1_route_c(self) -> None:
        """路線 C：神秘製作人（011～015）。"""
        self._ch1_play_sequence(
            ["011", "012", "013", "014", "015"],
            social_at={"014": [
                "@musicdaily：這很天才,我馬上就上癮了",
                "@critic_room：我完全聽不懂",
                "@rumorpage：這人是誰?",
            ]},
            on_finish=self._ch1_finish_route_c,
        )

    def _ch1_finish_route_c(self) -> None:
        self.apply_effects(
            {"fame": 10, "image": -3, "controversy": 8, "identity": -3}
        )
        self.player["hidden_producer"] = True
        self.player["route"] = "hidden"
        self.update_status_panel()
        self.show_chapter2()

    def _play_scene_sequence(
        self,
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
            comments = social_at.get(sid, ["（社群討論升溫中…）"])
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
        self,
        scene_ids: List[str],
        *,
        social_at: Optional[Dict[str, List[str]]] = None,
        on_finish: Callable[[], None],
    ) -> None:
        """第一章：依序播放帶圖場景。"""
        self._play_scene_sequence(
            scene_ids,
            "CHAPTER 1",
            story_map=self._ch1_stories,
            image_resolver=ch1_image_path,
            social_at=social_at,
            on_finish=on_finish,
        )

    def show_chapter2(self) -> None:
        """第二章：依 player['route'] 分流。"""
        route = self.player.get("route", "")
        if route == "rising":
            self._show_ch2a_tour()
        elif route == "stable":
            self._show_ch2b_album()
        elif route == "hidden":
            self._show_ch2c_viral()
        else:
            self.player["route"] = "stable"
            self._show_ch2b_album()

    # ----- Chapter 2A：爆紅路線 -----

    def _ch2a_play(
        self,
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

    def _show_ch2a_tour(self) -> None:
        """第二章 A：爆紅路線開場（016～018）與巡演抉擇。"""
        title = "CHAPTER 2A：爆紅路線 — 首次巡演"

        def show_tour_choice() -> None:
            self.show_visual_scene(
                "018",
                title,
                comments=["@musicdaily：現場表演才是藝人的靈魂。"],
                story_map=self._ch2a_stories,
                image_resolver=ch2a_image_path,
            )
            self.clear_choice_buttons()
            self.add_choice("高強度巡演", self._ch2a_pick_high)
            self.add_choice("精緻小型巡演", self._ch2a_pick_small)

        self._ch2a_play(
            ["016", "017"],
            title,
            social_at={
                "016": ["（巡演話題發燒中…）"],
                "017": ["@popwatch：他什麼時候會掉下來？"],
            },
            on_finish=show_tour_choice,
        )

    def _ch2a_pick_high(self) -> None:
        self.apply_effects(
            {"fame": 12, "money": 8, "health": -15, "controversy": 5, "identity": -3}
        )
        self.update_status_panel()
        self._ch2a_play(
            ["019", "020", "021", "022", "023"],
            "CHAPTER 2A",
            social_at={
                "021": [
                    "@tourfan：他是不是根本沒睡?",
                    "@popwatch：這行程也太地獄",
                ],
                "022": ["@haterzone：現場翻車?"],
                "023": [
                    "@stanaccount：應該只是累了?",
                    "@critic_room：這經紀公司也是想錢想瘋了",
                ],
            },
            on_finish=self._show_ch2a_crisis,
        )

    def _ch2a_pick_small(self) -> None:
        self.apply_effects(
            {"fame": 5, "image": 10, "health": -5, "identity": 5, "money": 3}
        )
        self.update_status_panel()
        self._ch2a_play(
            ["024", "025"],
            "CHAPTER 2A",
            social_at={
                "024": [
                    "@critic_room：他的live比錄音還強",
                    "@indiefan：完全不是流水線藝人",
                ],
                "025": ["@industrytalk：怎麼都不跑場?感覺沒什麼野心?"],
            },
            on_finish=self._show_ch2a_crisis,
        )

    def _show_ch2a_crisis(self) -> None:
        """第二章 A：公關危機（026～028）與危機處置抉擇。"""
        title = "CHAPTER 2A：第一次公關危機"

        def show_crisis_choice() -> None:
            self.clear_choice_buttons()
            self.add_choice(
                "承認表達不夠好，自己發文道歉", self._ch2a_pick_apology
            )
            self.add_choice("發正式聲明，否認指控", self._ch2a_pick_statement)
            self.add_choice("不回應，等待風波過去", self._ch2a_pick_silent)

        self._ch2a_play(
            ["026", "027", "028"],
            title,
            social_at={
                "028": [
                    "@haterzone：他是在說粉絲嗎?",
                    "@popwatch：剛紅就這樣?",
                    "@rumorpage：從大牌經紀公司出來的人講這種話好諷刺",
                ],
            },
            on_finish=show_crisis_choice,
            final_continue=False,
        )

    def _ch2a_pick_apology(self) -> None:
        self.apply_effects({"image": 8, "controversy": -5, "identity": 3, "fame": 3})
        self.update_status_panel()
        self._ch2a_play(
            ["029"],
            "CHAPTER 2A",
            social_at={
                "029": [
                    "@stanaccount：他說的本來就是實話",
                    "@musicdaily：這種反應反而有點可愛",
                    "@critic_room：很真誠的道歉",
                ],
            },
            on_finish=self.show_chapter3,
        )

    def _ch2a_pick_statement(self) -> None:
        self.apply_effects({"image": -5, "controversy": 8, "fame": 5, "identity": -3})
        self.update_status_panel()
        self._ch2a_play(
            ["030"],
            "CHAPTER 2A",
            social_at={
                "030": [
                    "@haterzone：想賺市場的錢又瞧不起主流聽眾",
                    "@popwatch：不是,這也沒什麼吧",
                    "@critic_room：酸民們真嗜血",
                ],
            },
            on_finish=self.show_chapter3,
        )

    def _ch2a_pick_silent(self) -> None:
        self.apply_effects({"image": -8, "controversy": 5, "health": -5, "fame": 3})
        self.update_status_panel()
        self._ch2a_play(
            ["031"],
            "CHAPTER 2A",
            social_at={
                "031": [
                    "@rumorpage：他怎麼還沒回應?",
                    "@haterzone：公司應該想息事寧人吧",
                    "@industrytalk：他應該是因為太難搞被冷凍了",
                ],
            },
            on_finish=self.show_chapter3,
        )

    # ----- Chapter 2B：穩定成長線 -----

    def _ch2b_play(
        self,
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

    def _show_ch2b_album(self) -> None:
        """第二章 B：開場（032～034）與專輯方向抉擇。"""
        title = "你剛結束一段公司安排的曝光行程，你的出道曲在發行一個月後仍在榜上，最近還時常被用來當作旅遊vlog的背景音。"
                "但你自己已經開始擔心：「這首迴響還不錯，但下一首呢？」、「這是我要走的風格嗎」"
                "幾天後，你被叫進公司，當天，會議室裡沒有寒暄，經紀人直接把平板推到你面前。"
                "「打鐵趁熱，單曲發行後接著就是專輯了，專輯將會定義你的風格、建構你的音樂世界。沒辦法用專輯證明自己的人，會被演算法與市場拋棄。"
                "你現在卡在一個不上不下的位置，你已經被看見了，但還沒被定義。」"
                "他們給了幾種方案，你想要怎麼做這張「會定義你的專輯」"

        def show_album_choice() -> None:
            self.show_visual_scene(
                "034",
                title,
                comments=["（樂評與粉絲都在等專輯方向…）"],
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
            title,
            social_at={
                "032": ["（你的名字開始被更多人看見…）"],
                "033": ["@popfan：他的新歌還不錯，期待未來發展。"],
            },
            on_finish=show_album_choice,
        )

    def _ch2b_pick_commercial(self) -> None:
        self.apply_effects({"fame": 12, "money": 12, "image": -3, "identity": -8})
        self._album_type = "commercial"
        self.update_status_panel()
        self._ch2b_play(
            ["035", "036"],
            "CHAPTER 2B",
            social_at={
                "036": [
                    "@popfan：這張怎麼每首都可以當主打",
                    "@musicdaily：我原本只想聽一首結果整張播完",
                    "@critic_room：今年的聲音",
                ],
            },
            on_finish=self._show_ch2b_transition,
        )

    def _ch2b_pick_concept(self) -> None:
        self.apply_effects({"image": 12, "identity": 8, "fame": 5, "money": -3})
        self._album_type = "concept"
        self.update_status_panel()
        self._ch2b_play(
            ["037", "038", "039", "040"],
            "CHAPTER 2B",
            social_at={
                "039": ["@popwatch：專輯上線第一天，好安靜。"],
                "040": [
                    "@critic_room：這張其實很好聽欸",
                    "@indiefan：我一開始沒懂,現在回去整張重聽",
                    "@musicdaily：怎麼越晚越紅?",
                ],
            },
            on_finish=self._show_ch2b_transition,
        )

    def _ch2b_pick_reject(self) -> None:
        self.apply_effects(
            {"image": 8, "identity": 12, "money": -8, "fame": -3, "controversy": 5}
        )
        self._album_type = ""
        self.update_status_panel()
        self._ch2b_play(
            ["041", "042", "043"],
            "CHAPTER 2B",
            social_at={
                "041": [
                    "@industrytalk：聽說他跟公司有點僵。",
                    "@popwatch：這樣真的撐得下去嗎？",
                ],
                "043": [
                    "@indiefan：至少他沒有變成公司產品。",
                    "@critic_room：評價兩極,但很像他自己。",
                ],
            },
            on_finish=self.show_chapter3,
        )

    def _show_ch2b_transition(self) -> None:
        """第二章 B：專輯後續抉擇（044 商業線 / 045 概念線）。"""
        at = self._album_type
        if at == "commercial":
            title = "CHAPTER 2B：成功之後的選擇"
            scene_id = "044"
        elif at == "concept":
            title = "CHAPTER 2B：藝術與市場的拉扯"
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
            social_at={scene_id: ["（公司與你之間氣氛微妙…）"]},
            on_finish=show_transition_choice,
            final_continue=False,
        )

    def _ch2b_pick_safe(self) -> None:
        self.apply_effects({"fame": 10, "money": 10, "image": -3, "identity": -8})
        self.update_status_panel()
        self.show_result_scene(
            "CHAPTER 2 RESULT：轉型之後｜商業加碼",
            "「你選擇把路走得更『可預測』。公司立刻排進更多代言與綜藝窗口，"
            "會議室的白板上寫滿下一步 KPI。經紀人笑得很真：『這才是長紅的打法。』\n\n"
            "你點頭，卻在深夜練歌時突然恍神——你還記得最初想唱的那句話嗎？」",
            [
                "@popfan：他真的很懂市場。",
                "@musicdaily：商業成績太強了。",
                "@critic_room：安全，但缺少驚喜。",
            ],
            self.show_chapter3,
        )

    def _ch2b_pick_art(self) -> None:
        self.apply_effects({"image": 10, "identity": 8, "fame": 3, "money": -3})
        self.update_status_panel()
        self.show_result_scene(
            "CHAPTER 2 RESULT：轉型之後｜往內走",
            "「你把下一張作品的母帶鎖進私人資料夾，只給少數信得過的人聽。"
            "經紀人嘆氣卻也點頭：『好吧，至少你還願意跟我們溝通。』\n\n"
            "你感覺到風向在變——慢，但往你想要的方向。」",
            [
                "@critic_room：這個轉向很聰明。",
                "@indiefan：終於看到他自己的東西了。",
                "@popfan：我有點懷念以前比較好懂的歌。",
            ],
            self.show_chapter3,
        )

    def _ch2b_pick_slow(self) -> None:
        self.apply_effects({"image": 10, "identity": 10, "fame": 3, "money": -3})
        self.update_status_panel()
        self.show_result_scene(
            "CHAPTER 2 RESULT：轉型之後｜慢火累積",
            "「你沒有為了榜單硬轉彎。公司嘴上抱怨，卻仍替你留了一條藝術行銷的窄路。"
            "經紀人把咖啡推到你面前：『你可以慢，但不能停。』\n\n"
            "你把那句話記下來，像記一句咒語。」",
            [
                "@critic_room：他可能不是最快紅的，但會紅很久。",
                "@indiefan：這才是藝術家的樣子。",
                "@industrytalk：商業面還是有疑慮。",
            ],
            self.show_chapter3,
        )

    def _ch2b_pick_market(self) -> None:
        self.apply_effects({"fame": 10, "money": 8, "image": -3, "identity": -5})
        self.update_status_panel()
        self.show_result_scene(
            "CHAPTER 2 RESULT：轉型之後｜更市場的入口",
            "「你把旋律線拉直、把副歌變得更『一聽就懂』。數據很快給出正向回饋，"
            "經紀人拍桌：『對嘛，這才是能養活團隊的作品。』\n\n"
            "你笑了笑，心裡卻知道：你交換了一些神秘，換來一些確定。」",
            [
                "@popfan：這次好聽很多欸。",
                "@critic_room：變好入口了，但也少了一點神秘感。",
                "@industrytalk：這是比較成熟的選擇。",
            ],
            self.show_chapter3,
        )

    # ----- Chapter 2C：地下黑暗線 -----

    def _show_ch2c_viral(self) -> None:
        story = (
            "「你原本以為那首歌已經結束了，沒想到某天，它突然出現在社群平台，被網友用來當作短影音配樂。"
            "幾小時後，它不是慢慢紅，而是直接被瘋傳。\n\n"
            "『這是誰的歌？』\n"
            "『有點怪，但會上癮。』\n"
            "『停不下來。』\n\n"
            "凌晨兩點，經紀人打來電話：『你的歌爆了，你現在要決定怎麼處理這波流量。』」"
        )
        if self.player.get("hidden_producer"):
            story += (
                "\n\n「更奇怪的是，爆紅的不是原曲，而是一個被重新編曲過的版本。節奏更緊、情緒更集中，"
                "像是有人精準地改造了它。你突然想起那位神秘製作人，以及他錄音時近乎不安的沉默。」"
            )

        self.show_scene("CHAPTER 2C：地下黑暗線 — 病毒式爆紅", story, ["（全網都在問你是誰…）"])
        self.clear_choice_buttons()

        def pick_commerce() -> None:
            self.apply_effects(
                {"fame": 15, "money": 12, "image": -8, "identity": -10}
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：病毒爆紅之後｜接住流量",
                "「你選擇讓作品更靠近大眾的耳朵。混音、剪輯、視覺素材在一週內全部重排，"
                "公司把資源堆到你面前，像堆一座橋。經紀人幾乎住在你旁邊：『這波不接住就虧大了。』\n\n"
                "當你終於躺下，腦中卻不停回放那些被改短的旋律。」",
                [
                    "@musicdaily：他真的接住這波流量了。",
                    "@popfan：商業化之後反而更好聽。",
                    "@indiefan：感覺他被市場吃掉了。",
                ],
                self.show_chapter3,
            )

        def pick_underground() -> None:
            self.apply_effects(
                {"image": 12, "identity": 12, "fame": 3, "money": -3}
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：病毒爆紅之後｜留在地下",
                "「你沒有把作品磨成最容易傳播的形狀。你拒絕了幾個過度包裝的企劃，"
                "經紀人急得冒汗，卻也拿你沒辦法：『你至少讓我發一張現場照吧？』\n\n"
                "你答應了最小的讓步，心裡卻清楚——你守住了某條線。」",
                [
                    "@indiefan：拜託不要把這首歌做成罐頭流行。",
                    "@critic_room：他好像真的不太在乎爆紅。",
                    "@popwatch：錯過這波會不會很可惜？",
                ],
                self.show_chapter3,
            )

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
            self.show_result_scene(
                "CHAPTER 2 RESULT：病毒爆紅之後｜輿論操作",
                "「話題像雪球愈滾愈大。你與團隊幾乎不再睡覺，會議室裡全是紅色提醒。"
                "經紀人盯著曲線喃喃自語：『我們在贏…吧？』\n\n"
                "你看著鏡子裡的自己，突然有一瞬間認不出來。」",
                [
                    "@rumorpage：這波操作感超重。",
                    "@haterzone：他是不是故意製造爭議？",
                    "@musicdaily：不管你喜不喜歡，他確實成功讓所有人都在討論。",
                ],
                self._show_hidden_producer_reveal
                if self.player.get("hidden_producer")
                else self.show_chapter3,
            )

        self.add_choice("抓緊機會，接受商業化", pick_commerce)
        self.add_choice("順其自然，堅持地下風格", pick_underground)
        self.add_choice("操作輿論，把影響力最大化", pick_pr)

    def _show_hidden_producer_reveal(self) -> None:
        story = (
            "「幾天後，你收到一封沒有署名的訊息，只有一句話：『你已經證明自己能引發共鳴。』\n\n"
            "你開始調查那位神秘製作人，才發現他曾經參與無數爆紅作品的幕後設計。"
            "所有他改過的作品都有一個共同點：它們都變成更容易被傳播的情緒結構。\n\n"
            "傳聞中，他並不只是音樂人，而是某個古老組織『星辰議會』的牧羊人。"
            "他們相信大眾是盲目的羊群，而音樂可以收割情緒能量，讓人類意識停留在特定頻率。\n\n"
            "你不知道這是真是假，但你知道一件事：「你的成名之路，已經不只是娛樂圈的遊戲。」"
        )
        self.show_scene("CHAPTER 2C：隱藏事件 — 星辰議會", story, ["（真相與流量一樣讓人上癮…）"])
        self.clear_choice_buttons()

        def pick_use() -> None:
            self.apply_effects(
                {"fame": 10, "controversy": 10, "identity": -10, "image": -5}
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：星辰議會之後｜更深的水",
                "「你告訴自己：先把作品完成，再去想真相。但你也開始注意到——"
                "某些邀約來得太剛好、某些熱搜來得太整齊。經紀人只說：『別想太多，專心表演。』\n\n"
                "你點頭，卻在深夜把通訊錄裡一個名字標成紅色。」",
                [
                    "@rumorpage：他身邊的人真的越來越神秘。",
                    "@haterzone：這人根本像邪教偶像。",
                    "@stanaccount：我不知道發生什麼事，但我停不下來。",
                ],
                self.show_chapter3,
            )

        def pick_cut() -> None:
            self.apply_effects(
                {"image": 8, "identity": 10, "fame": -5, "health": -3}
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：星辰議會之後｜抽身",
                "「你開始刻意缺席某些聚會，也婉拒了幾個來路不明的合作。"
                "經紀人皺眉：『你確定要放棄這些曝光？』你回答得很慢，卻很堅定。\n\n"
                "你失去一些熱度，但睡覺變得比較容易。」",
                [
                    "@critic_room：他好像在刻意避開某種成功公式。",
                    "@indiefan：這個選擇很勇敢。",
                    "@popwatch：怎麼突然消失一陣子？",
                ],
                self.show_chapter3,
            )

        self.add_choice("繼續利用這股力量", pick_use)
        self.add_choice("試著切斷與神秘製作人的關係", pick_cut)

    # ----- Chapter 3：巨星的代價 -----

    def _chapter3_branch(self) -> str:
        """決定第三章分支。"""
        p = self.player
        image = int(p["image"])
        fame = int(p["fame"])
        if image <= 40:
            return "controversial"
        if fame >= 75 and image >= 55:
            return "global_icon"
        return "mature_artist"

    def show_chapter3(self) -> None:
        """第三章：依形象與名氣決定分支。"""
        branch = self._chapter3_branch()
        if branch == "global_icon":
            self._show_ch3_global_icon()
        elif branch == "controversial":
            self._show_ch3_controversial()
        else:
            self._show_ch3_mature_artist()

    def _show_ch3_global_icon(self) -> None:
        story = (
            "「你站上了真正的世界舞台。全球巡演、品牌合作、媒體邀約、粉絲尖叫，一切都來得太快。"
            "公司希望你維持完美人設，把這段高峰變成商業神話。\n\n"
            "但你也開始懷疑，如果每一步都完美，那你還剩下多少真實？」"
        )
        self.show_scene("CHAPTER 3：全球巡演", story, ["（世界等著看你的下一步…）"])
        self.clear_choice_buttons()

        def pick_idol() -> None:
            self.apply_effects(
                {"fame": 10, "money": 10, "image": 3, "identity": -10, "health": -5}
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：完美人設的燈光下",
                "「你把笑容練到剛好的角度，把每句話都收進安全範圍。"
                "品牌方滿意地點頭，經紀人看著排程表說：『這就是頂流的樣子。』\n\n"
                "你在後台望著鏡子，突然覺得那張臉既熟悉又陌生。」",
                [
                    "@musicdaily：他真的成為全球級偶像了。",
                    "@popfan：這場巡演根本時代記憶。",
                    "@critic_room：完美到有點不像真人。",
                ],
                self._show_final_night,
            )

        def pick_self() -> None:
            self.apply_effects(
                {"image": 12, "identity": 10, "fame": 3, "money": -3}
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：把真實放回作品裡",
                "「你在新歌裡放進一段沒那麼『好聽』、卻很真誠的念白。"
                "經紀人看完母帶沉默很久，最後只說：『你確定要冒這個險？』你點頭。\n\n"
                "幾天後，留言區開始出現『我好像比較認識他了』。」",
                [
                    "@critic_room：他終於不只是流行明星，而是創作者。",
                    "@stanaccount：這張新作品讓我重新認識他。",
                    "@popwatch：有些粉絲可能不習慣，但這很重要。",
                ],
                self._show_final_night,
            )

        self.add_choice("維持完美偶像人設", pick_idol)
        self.add_choice("在作品中加入真正的自我", pick_self)

    def _show_ch3_mature_artist(self) -> None:
        story = (
            "「你沒有用最爆炸的方式成名，卻一步一步累積出自己的位置。如今，獎季來臨，"
            "你第一次被正式放進『實力派』的討論中。\n\n"
            "公司希望你配合獎季公關，穩定維持地位。但你心裡知道，真正的突破往往不會發生在最安全的選擇裡。」"
        )
        self.show_scene("CHAPTER 3：獎季與成熟巨星", story, ["（獎季預測文洗版中…）"])
        self.clear_choice_buttons()

        def pick_pr() -> None:
            self.apply_effects(
                {"fame": 10, "image": 5, "money": 8, "identity": -3}
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：獎季的穩健打法",
                "「你照表操課跑完每一場訪談、每一次紅毯、每一支短片。"
                "公關團隊在群組裡貼滿『OK』，經紀人拍拍你：『你做得很好。』\n\n"
                "你點頭，卻在某個頒獎夜後台，突然很想一個人走一段路。」",
                [
                    "@musicdaily：他終於被主流獎項看見了。",
                    "@industrytalk：這一步走得很穩。",
                    "@critic_room：成熟，但不算冒險。",
                ],
                self._show_final_night,
            )

        def pick_art() -> None:
            self.apply_effects(
                {"image": 15, "identity": 12, "fame": 3, "money": -8}
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：冒險的那條路",
                "「你推掉幾個更賺錢的合作，把時間留給一個更瘋狂的創作計畫。"
                "經紀人臉色不好看，卻仍替你擋下外界質疑：『他至少知道自己要什麼。』\n\n"
                "你把耳機戴上，覺得世界安靜了一點。」",
                [
                    "@critic_room：這可能是他目前最重要的作品。",
                    "@indiefan：他沒有背叛自己。",
                    "@popwatch：商業成績可能會受影響，但評價很高。",
                ],
                self._show_final_night,
            )

        self.add_choice("配合獎季公關，穩定維持地位", pick_pr)
        self.add_choice("放棄部分商業利益，追求藝術突破", pick_art)

    def _show_ch3_controversial(self) -> None:
        story = (
            "「你的名字已經不只是名字，而是一場永遠不會結束的爭論。大型爭議爆發後，媒體、粉絲、黑粉、品牌全都盯著你。\n\n"
            "公司希望你低頭道歉，重新包裝形象。但另一個聲音告訴你：既然世界已經把你變成怪物，也許你可以直接成為傳奇。」"
        )
        self.show_scene("CHAPTER 3：爭議巨星", story, ["（全網吵翻天…）"])
        self.clear_choice_buttons()

        def pick_fight() -> None:
            self.apply_effects(
                {
                    "fame": 12,
                    "controversy": 12,
                    "image": -10,
                    "identity": 3,
                    "health": -5,
                }
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：擁抱標籤之後",
                "「你不再試圖解釋所有誤讀。你把爭議寫進歌里，把攻擊變成舞台效果。"
                "經紀人一边擦汗一边笑：『你瘋了…但數據真的在跳。』\n\n"
                "你望著台下，突然覺得自己像站在刀尖上跳舞。」",
                [
                    "@haterzone：他真的完全不演了。",
                    "@stanaccount：我知道他很瘋，但我就是移不開眼睛。",
                    "@musicdaily：不論喜不喜歡，他就是現在最有話題的人。",
                ],
                self._show_final_night,
            )

        def pick_apology() -> None:
            self.apply_effects(
                {
                    "image": 10,
                    "controversy": -8,
                    "fame": -5,
                    "health": -3,
                    "identity": -5,
                }
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：道歉與修補",
                "「你在鏡頭前低頭，語氣克制，努力把每一句話說得真誠。"
                "公司在旁邊緊盯逐字稿，經紀人小聲說：『先活下來，再談下一步。』\n\n"
                "你說完最後一句，才發現自己手心全是汗。」",
                [
                    "@popwatch：這次道歉有救回來嗎？",
                    "@haterzone：太假了吧，現在才想洗白。",
                    "@stanaccount：至少他願意面對。",
                ],
                self._show_final_night,
            )

        self.add_choice("反擊媒體，擁抱負面標籤", pick_fight)
        self.add_choice("低頭道歉，試圖洗白", pick_apology)

    def _show_final_night(self) -> None:
        """第三章結束後、揭曉結局前的最終夜。"""
        self.show_scene(
            "FINAL NIGHT：最終夜 — 成名前的回望",
            "「在最終結果揭曉前，你獨自坐在休息室裡。外面是粉絲、媒體、公司、品牌與整個世界的聲音。"
            "你看著鏡中的自己，突然想起剛簽約的那一天。\n\n"
            "你已經走了很遠，但你也不確定自己失去了什麼。」",
            ["（手機震動不停，但你暫時不想看。）"],
        )
        self.clear_choice_buttons()
        self.add_choice("查看最終結局", self.show_ending)

    # ----- 結局 -----

    def compute_ending(self) -> Tuple[str, str]:
        """依指定順序計算結局標題與內文（門檻提高並納入爭議度／自我認同）。"""
        self.clamp_stats()
        p = self.player
        fame = int(p["fame"])
        image = int(p["image"])
        health = int(p["health"])
        controversy = int(p["controversy"])
        identity = int(p["identity"])

        if fame >= 85 and image >= 55 and controversy <= 60:
            return (
                "POP ICON：商業神話",
                "「你成為時代的代表，全球巡演售罄，廣告與獎項接踵而來。所有人都知道你的名字。"
                "但某些深夜裡，你偶爾會懷疑，舞台上的那個人是否還是最初的自己。」",
            )
        if fame >= 80 and image <= 45 and controversy >= 40:
            return (
                "CONTROVERSIAL LEGEND：爭議巨星",
                "「一半的人愛你，一半的人恨你。你不只是歌手，而是話題本身。"
                "每一次發言、沉默、轉身，都能讓世界再次討論你。」",
            )
        if image >= 80 and fame >= 55 and identity >= 60:
            return (
                "ARTISTIC ICON：藝術傳奇",
                "「你沒有成為最容易被消費的明星，卻成為最難被取代的存在。"
                "多年後，音樂學院開始研究你的作品，稱你為不屬於時代的人。」",
            )
        if fame < 20 or health <= 10:
            return (
                "FALLEN STAR：隕落巨星",
                "「名氣散去，合約終止，媒體不再提起你的名字。你消失在人群之中，"
                "也許某天會以製作人的身份重新開始，也許只是安靜地離開。」",
            )
        return (
            "INDUSTRY SURVIVOR：產業倖存者",
            "「你沒有登上神壇，也沒有徹底墜落。你學會在市場、公司、粉絲與自我之間生存。"
            "下一首歌還沒有完成，而你也還沒有結束。」",
        )

    def _format_final_stats(self) -> str:
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

    def show_ending(self) -> None:
        """顯示結局、最終數值與重新開始。"""
        title, body = self.compute_ending()
        stats_block = self._format_final_stats()
        full_text = (
            f"ENDING：{title}\n\n{body}\n\n{stats_block}"
        )
        self.set_story(full_text)
        self.update_social_reactions(
            [
                "@musicdaily：故事告一段落，但音樂還在。",
                "@you：點擊「重新開始」再玩一次不同選擇吧。",
            ]
        )
        self.clear_choice_buttons()
        self.add_choice("重新開始", self.restart_game)


def main() -> None:
    """程式進入點。"""
    app = GlobalStarApp()
    app.mainloop()


if __name__ == "__main__":
    main()
