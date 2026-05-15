"""
GLOBAL STAR：成名之路 — 以 CustomTkinter 製作的簡易敘事模擬遊戲 MVP。
"""

from __future__ import annotations

import random
from typing import Any, Callable, Dict, List, Tuple

import customtkinter as ctk


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
    }


def apply_deltas(player: Dict[str, Any], deltas: Dict[str, int]) -> None:
    """套用數值變化（不含 hidden_producer 布林）。"""
    for key, delta in deltas.items():
        if key in player and isinstance(player[key], (int, float)):
            player[key] += delta
    clamp_player(player)


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
        self.chapter_route: str = ""

        self._build_layout()
        self.show_start()

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

        self.story_box = ctk.CTkTextbox(
            self,
            wrap="word",
            font=ctk.CTkFont(size=18),
            corner_radius=12,
            border_width=1,
        )
        self.story_box.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")

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
        for i, (key, zh) in enumerate(stat_keys):
            row = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=6)
            ctk.CTkLabel(row, text=f"{zh}：", font=ctk.CTkFont(size=15, weight="bold")).pack(
                side="left"
            )
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

    def set_social(self, lines: List[str]) -> None:
        """更新社群反應區。"""
        self.social_text.configure(state="normal")
        self.social_text.delete("1.0", "end")
        self.social_text.insert("1.0", "\n".join(lines))
        self.social_text.configure(state="disabled")

    def refresh_stats(self) -> None:
        """重新整理狀態面板。"""
        clamp_player(self.player)
        for key, lbl in self.stats_labels.items():
            lbl.configure(text=str(int(self.player[key])))

    def clear_choices(self) -> None:
        """移除所有選項按鈕。"""
        for w in self.choices_frame.winfo_children():
            w.destroy()

    def add_choice(
        self,
        text: str,
        command: Callable[[], None],
    ) -> None:
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

    def show_start(self) -> None:
        """開始畫面。"""
        self.player = new_player()
        self.chapter_route = ""
        self.refresh_stats()
        self.set_social(["（尚未有留言）"])
        self.set_story(
            "「你是一位來自普通家庭的新人，剛與 Creative Artist Records 簽約。"
            "你即將踏上成名之路。」"
        )
        self.clear_choices()
        self.add_choice("開始遊戲", self.show_city_selection)

    def show_city_selection(self) -> None:
        """選擇發展城市。"""
        self.set_story("請選擇你主要發展的城市：")
        self.set_social(["（粉絲還在觀望中…）"])
        self.clear_choices()

        def pick_la() -> None:
            self.player["city"] = "洛杉磯"
            apply_deltas(self.player, {"fame": 10, "image": -5})
            self.refresh_stats()
            self.show_style_selection()

        def pick_london() -> None:
            self.player["city"] = "倫敦"
            apply_deltas(self.player, {"image": 10, "fame": 3})
            self.refresh_stats()
            self.show_style_selection()

        def pick_ny() -> None:
            self.player["city"] = "紐約"
            apply_deltas(self.player, {"fame": 5, "money": 5})
            self.refresh_stats()
            self.show_style_selection()

        self.add_choice("洛杉磯（名氣 +10，形象 -5）", pick_la)
        self.add_choice("倫敦（形象 +10，名氣 +3）", pick_london)
        self.add_choice("紐約（名氣 +5，金錢 +5）", pick_ny)

    def show_style_selection(self) -> None:
        """選擇出道風格。"""
        self.set_story("請選擇你的出道風格：")
        self.set_social(["@musicdaily：新簽約藝人即將曝光？"])
        self.clear_choices()

        def pick_rebel() -> None:
            self.player["style"] = "叛逆流派 Rebel"
            apply_deltas(self.player, {"fame": 10, "controversy": 10, "image": -5})
            self.refresh_stats()
            self.show_chapter1()

        def pick_pop() -> None:
            self.player["style"] = "商業流行 Pop Idol"
            apply_deltas(self.player, {"fame": 5, "money": 10, "identity": -5})
            self.refresh_stats()
            self.show_chapter1()

        def pick_indie() -> None:
            self.player["style"] = "藝術地下 Indie"
            apply_deltas(self.player, {"image": 15, "fame": -5, "identity": 10})
            self.refresh_stats()
            self.show_chapter1()

        self.add_choice("叛逆流派 Rebel", pick_rebel)
        self.add_choice("商業流行 Pop Idol", pick_pop)
        self.add_choice("藝術地下 Indie", pick_indie)

    def show_chapter1(self) -> None:
        """第一章：第一首歌的代價。"""
        self.set_story(
            "「順利與當地最大的經紀公司 Creative Artist Records 簽約後的三個月，"
            "公司遲遲未聯絡你。某天夜裡，經紀人傳來訊息：『我們要決定你的第一首歌了，"
            "這將會定義你是誰。』」"
        )
        self.set_social(["（歌迷正在刷新頁面…）"])
        self.clear_choices()

        def ch1_a() -> None:
            apply_deltas(self.player, {"fame": 15, "money": 10, "image": -5, "identity": -10})
            self.chapter_route = "stable"
            self.refresh_stats()
            self.set_social(
                [
                    "@musicdaily：這新人很穩欸，感覺會紅。",
                    "@popfan：副歌也太洗腦了吧。",
                    "@critic_room：好聽是好聽，但有點沒特色。",
                ]
            )
            self.show_chapter2()

        def ch1_b() -> None:
            success = random.random() < 0.5
            if success:
                apply_deltas(
                    self.player,
                    {"fame": 20, "image": 15, "identity": 10, "money": -5},
                )
                self.chapter_route = "rising"
                self.set_social(
                    [
                        "@stanaccount：這首歌也太真實，我直接哭出來。",
                        "@musicdaily：新人自作曲意外爆紅。",
                        "@critic_room：粗糙，但有靈魂。",
                    ]
                )
            else:
                apply_deltas(
                    self.player,
                    {"fame": -10, "image": 5, "identity": 5, "money": -5},
                )
                self.chapter_route = "hidden_rise"
                self.set_social(
                    [
                        "@popwatch：這首歌好像沒什麼聲量。",
                        "@industrytalk：公司應該開始緊張了。",
                        "@smallfan：我其實覺得很好聽，只是大家還沒發現。",
                    ]
                )
            self.refresh_stats()
            self.show_chapter2()

        def ch1_c() -> None:
            apply_deltas(
                self.player,
                {"fame": 20, "image": -5, "controversy": 15, "identity": -5},
            )
            self.player["hidden_producer"] = True
            self.chapter_route = "hidden"
            self.refresh_stats()
            self.set_social(
                [
                    "@musicdaily：這新人到底是誰？有點怪但會上癮。",
                    "@critic_room：我完全聽不懂，但我想再聽一次。",
                    "@rumorpage：聽說幕後製作人很神秘。",
                ]
            )
            self.show_chapter2()

        self.add_choice("交給公司製作", ch1_a)
        self.add_choice("自己創作（成功或失敗隨機）", ch1_b)
        self.add_choice("與神秘製作人合作", ch1_c)

    def show_chapter2(self) -> None:
        """第二章：依路線顯示簡化事件。"""
        route = self.chapter_route
        extra = ""
        if route == "hidden" and self.player.get("hidden_producer"):
            extra = (
                "\n\n（你隱約覺得那位製作人的背景不單純——坊間傳聞與一個名為"
                "「星辰議會」的秘密組織有關。你還沒有證據，但旋律裡總透著一股"
                "令人不安的熟悉感。）"
            )

        if route == "rising":
            self.set_story(
                "【第二章｜首次巡演】\n\n"
                "你的作品開始受到關注，公司安排首次巡演。"
                "你要如何面對舞台與體力的拉鋸？" + extra
            )
            self.clear_choices()

            def c2_ra() -> None:
                apply_deltas(
                    self.player,
                    {"fame": 25, "money": 15, "health": -30, "controversy": 5},
                )
                self.refresh_stats()
                self.set_social(
                    [
                        "@tourlife：場場爆滿，但藝人看起來快累垮了…",
                        "@moneytalk：票房數字很亮眼。",
                    ]
                )
                self.show_final()

            def c2_rb() -> None:
                apply_deltas(
                    self.player,
                    {"image": 20, "fame": 10, "health": -10, "identity": 10},
                )
                self.refresh_stats()
                self.set_social(
                    [
                        "@intimategig：小而美的演出，氛圍超好。",
                        "@critic_room：這條路走得慢，但走得穩。",
                    ]
                )
                self.show_final()

            self.add_choice("高強度巡演", c2_ra)
            self.add_choice("精緻小型巡演", c2_rb)

        elif route == "stable":
            self.set_story(
                "【第二章｜第一張專輯】\n\n"
                "公司要你交出第一張專輯，這將決定市場對你的定位。" + extra
            )
            self.clear_choices()

            def c2_sa() -> None:
                apply_deltas(
                    self.player,
                    {"fame": 25, "money": 20, "image": -5, "identity": -15},
                )
                self.refresh_stats()
                self.set_social(
                    [
                        "@charts：空降排行榜，商業表現亮眼。",
                        "@deepcut：聽得出來犧牲了個人特色。",
                    ]
                )
                self.show_final()

            def c2_sb() -> None:
                apply_deltas(
                    self.player,
                    {"image": 25, "identity": 15, "fame": 5, "money": -5},
                )
                self.refresh_stats()
                self.set_social(
                    [
                        "@artweekly：概念完整，值得細聽。",
                        "@popfan：需要時間消化，但越聽越上癮。",
                    ]
                )
                self.show_final()

            def c2_sc() -> None:
                apply_deltas(
                    self.player,
                    {
                        "image": 15,
                        "identity": 20,
                        "money": -15,
                        "fame": -5,
                        "controversy": 10,
                    },
                )
                self.refresh_stats()
                self.set_social(
                    [
                        "@industrytalk：和公司槓上了？話題瞬間炸開。",
                        "@supportfan：我們挺你做自己！",
                    ]
                )
                self.show_final()

            self.add_choice("商業專輯", c2_sa)
            self.add_choice("個人概念專輯", c2_sb)
            self.add_choice("拒絕公司干涉", c2_sc)

        elif route == "hidden":
            self.set_story(
                "【第二章｜病毒式爆紅】\n\n"
                "你的作品以意想不到的方式在網路上擴散，輿論兩極。"
                "你必須決定下一步。" + extra
            )
            self.clear_choices()

            def c2_ha() -> None:
                apply_deltas(
                    self.player,
                    {"fame": 30, "money": 20, "image": -15, "identity": -20},
                )
                self.refresh_stats()
                self.set_social(
                    [
                        "@branddeals：代言邀約湧入。",
                        "@oldfan：感覺變味了…",
                    ]
                )
                self.show_final()

            def c2_hb() -> None:
                apply_deltas(
                    self.player,
                    {"image": 25, "identity": 20, "fame": 5, "money": -5},
                )
                self.refresh_stats()
                self.set_social(
                    [
                        "@underground：地下圈尊敬你沒有賣掉靈魂。",
                        "@charts：主流榜單能見度普通。",
                    ]
                )
                self.show_final()

            def c2_hc() -> None:
                apply_deltas(
                    self.player,
                    {"fame": 35, "controversy": 30, "image": -25, "identity": -10},
                )
                self.refresh_stats()
                self.set_social(
                    [
                        "@rumorpage：操作痕跡？陰謀論滿天飛。",
                        "@ethics：這樣玩火真的沒問題嗎？",
                    ]
                )
                self.show_final()

            self.add_choice("接受商業化", c2_ha)
            self.add_choice("堅持地下風格", c2_hb)
            self.add_choice("操作輿論", c2_hc)

        else:
            # hidden_rise：第一章自創作失敗後的簡化第二章
            self.set_story(
                "【第二章｜小眾逆襲】\n\n"
                "雖然沒有一炮而紅，你的作品在社群與小眾圈慢慢發酵。"
                "你要把力氣放在哪裡？" + extra
            )
            self.clear_choices()

            def c2_hr_a() -> None:
                apply_deltas(
                    self.player,
                    {"fame": 18, "image": 12, "health": -18, "money": 8},
                )
                self.refresh_stats()
                self.set_social(
                    [
                        "@festivalfan：現場演出圈粉無數。",
                        "@sleepdeprived：行程看起來很硬…",
                    ]
                )
                self.show_final()

            def c2_hr_b() -> None:
                apply_deltas(
                    self.player,
                    {"identity": 18, "image": 12, "fame": 8, "money": -6},
                )
                self.refresh_stats()
                self.set_social(
                    [
                        "@slowburn：慢火細燉，作品深度被看見。",
                        "@critic_room：值得等待的第二波。",
                    ]
                )
                self.show_final()

            self.add_choice("拚命跑活動與音樂節", c2_hr_a)
            self.add_choice("沉澱創作、累積口碑", c2_hr_b)

    def show_final(self) -> None:
        """最終事件前導。"""
        self.set_story(
            "「幾年後，你站在世界巡演、獎季與輿論風暴的交叉點。"
            "你的選擇即將決定你會成為哪一種傳奇。」"
        )
        self.clear_choices()
        self.add_choice("查看結局", self.show_ending)

    def compute_ending(self) -> Tuple[str, str]:
        """依指定順序計算結局標題與內文。"""
        p = self.player
        fame = int(p["fame"])
        image = int(p["image"])
        health = int(p["health"])

        if fame >= 90 and image >= 60:
            return (
                "POP ICON 商業神話",
                "「你成為時代的代表，全球巡演售罄，廣告與獎項接踵而來。"
                "但某些深夜裡，你偶爾會懷疑，舞台上的那個人是否還是最初的自己。」",
            )
        if fame >= 80 and image <= 40:
            return (
                "CONTROVERSIAL LEGEND 爭議巨星",
                "「一半的人愛你，一半的人恨你。你不只是歌手，而是話題本身。"
                "每一次發言、沉默、轉身，都能讓世界再次討論你。」",
            )
        if image >= 85 and fame >= 60:
            return (
                "ARTISTIC ICON 藝術傳奇",
                "「你沒有成為最容易被消費的明星，卻成為最難被取代的存在。"
                "多年後，音樂學院開始研究你的作品，稱你為不屬於時代的人。」",
            )
        if fame < 20 or health <= 0:
            return (
                "FALLEN STAR 隕落巨星",
                "「名氣散去，合約終止，媒體不再提起你的名字。"
                "你消失在人群之中，也許某天會以製作人的身份重新開始。」",
            )
        return (
            "INDUSTRY SURVIVOR 產業倖存者",
            "「你沒有登上神壇，也沒有徹底墜落。"
            "你學會在市場、公司、粉絲與自我之間生存，繼續唱著下一首歌。」",
        )

    def show_ending(self) -> None:
        """顯示結局與重新開始。"""
        title, body = self.compute_ending()
        self.set_story(f"【結局｜{title}】\n\n{body}")
        self.set_social(
            [
                "@musicdaily：故事告一段落，但音樂還在。",
                "@you：點擊「重新開始」再玩一次不同選擇吧。",
            ]
        )
        self.clear_choices()
        self.add_choice("重新開始", self.show_start)


def main() -> None:
    """程式進入點。"""
    app = GlobalStarApp()
    app.mainloop()


if __name__ == "__main__":
    main()
