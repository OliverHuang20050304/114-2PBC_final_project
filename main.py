"""
GLOBAL STAR：成名之路 — 以 CustomTkinter 製作的敘事模擬遊戲。
"""

from __future__ import annotations

import random
from typing import Any, Callable, Dict, List, Optional, Tuple

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
        "route": "",
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
        # 第二章 B 路線：第一張專輯選項 A/B 後的專輯類型（過場用）
        self._album_type: str = ""

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
    ) -> None:
        """顯示標題與故事正文（標題與內文分開顯示）。"""
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
        """第一章：第一首歌的代價。"""
        self.show_scene(
            "CHAPTER 1：第一首歌的代價",
            "「順利與當地最大的經紀公司 Creative Artist Records 簽約後的三個月，"
            "公司遲遲未聯絡你。某天夜裡，經紀人傳來訊息：『我們要決定你的第一首歌了，"
            "這將會定義你是誰。』」",
            ["（歌迷正在刷新頁面…）"],
        )
        self.clear_choice_buttons()

        def ch1_a() -> None:
            self.apply_effects(
                {"fame": 8, "money": 5, "image": -3, "identity": -5}
            )
            self.player["route"] = "stable"
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 1 RESULT：公司打造的穩健首單",
                "「單曲如期上架。A&R 團隊把副歌打磨得極其洗腦，MV 也在預算內準時完成。"
                "經紀人在群組裡貼了一排貼圖慶祝：『這就是新人該有的第一步。』\n\n"
                "你點開留言區，看見有人說你『很安全』。你還不確定那是不是讚美，但至少——"
                "你真的被聽見了。」",
                [
                    "@musicdaily：這新人很穩欸，感覺會紅。",
                    "@popfan：副歌也太洗腦了吧。",
                    "@critic_room：好聽是好聽，但有點沒特色。",
                ],
                self.show_chapter2,
            )

        def ch1_b() -> None:
            success = random.random() < 0.5
            if success:
                self.apply_effects(
                    {"fame": 10, "image": 8, "identity": 5, "money": -3}
                )
                self.player["route"] = "rising"
                self.update_status_panel()
                self.show_result_scene(
                    "CHAPTER 1 RESULT：自創曲意外成為話題",
                    "「你把最真實的一段心事寫進副歌。原本以為只會在小眾圈轉發，"
                    "沒想到幾天後，短影音平台開始出現各種翻唱與二創。"
                    "經紀人打來電話的聲音裡藏不住驚喜：『你小子……真的把流量撞開了。』\n\n"
                    "公司一邊開會一邊快速調整計畫，而你第一次感覺到：這條路，可能比你想像的更吵、更亮。」",
                    [
                        "@stanaccount：這首歌也太真實，我直接哭出來。",
                        "@musicdaily：新人自作曲意外爆紅。",
                        "@critic_room：粗糙，但有靈魂。",
                    ],
                    self.show_chapter2,
                )
            else:
                self.apply_effects(
                    {"fame": -5, "image": 3, "identity": 3, "money": -3}
                )
                self.player["route"] = "hidden"
                self.update_status_panel()
                self.show_result_scene(
                    "CHAPTER 1 RESULT：沒能引爆的初試啼聲",
                    "「數據不如預期。評論區很安靜，只有少數幾則留言替你說話。"
                    "經紀人回覆得很客氣：『我們再調整方向。』但你聽得出來，語氣裡有壓力。\n\n"
                    "你把手機放下，看著未完成的新 demo，第一次意識到：在這個產業裡，"
                    "被看見與不被看見，可能只隔著一個晚上的演算法。」",
                    [
                        "@popwatch：這首歌好像沒什麼聲量。",
                        "@industrytalk：公司應該開始緊張了。",
                        "@smallfan：我其實覺得很好聽，只是大家還沒發現。",
                    ],
                    self.show_chapter2,
                )

        def ch1_c() -> None:
            self.apply_effects(
                {"fame": 10, "image": -3, "controversy": 8, "identity": -3}
            )
            self.player["hidden_producer"] = True
            self.player["route"] = "hidden"
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 1 RESULT：神秘製作人的印記",
                "「成品出爐那天，你盯著波形圖發呆。你明明唱的是自己，"
                "卻總覺得有些地方『太剛好』——剛好刺中情緒、剛好適合循環、剛好讓人停不下來。"
                "製作人只淡淡說：『觀眾不需要懂，他們只需要被接住。』\n\n"
                "經紀人對外宣傳把功勞都歸給你，但你心裡知道：這首歌裡，還藏著另一雙手。」",
                [
                    "@musicdaily：這新人到底是誰？有點怪但會上癮。",
                    "@critic_room：我完全聽不懂，但我想再聽一次。",
                    "@rumorpage：聽說幕後製作人很神秘。",
                ],
                self.show_chapter2,
            )

        self.add_choice("交給公司製作", ch1_a)
        self.add_choice("自己創作（成功或失敗隨機）", ch1_b)
        self.add_choice("與神秘製作人合作", ch1_c)

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

    def _show_ch2a_tour(self) -> None:
        story = (
            "「發行單曲後，你的名字幾乎無處不在。推薦頁、短影片、排行榜——你是演算法寵兒，"
            "也是年度最受矚目的新人。有人開始模仿你，有人開始討論你的過去，也有人開始預言你什麼時候會掉下來。\n\n"
            "Creative Artist Records 為你爭取到許多表演機會。經紀人語重心長地說："
            "『流量可以讓人認識你，但舞台才會讓人留下來。』\n\n"
            "你看著行程表，城市一個接一個，掌聲與不確定性同時向你靠近。你要怎麼安排第一次巡演？」"
        )
        self.show_scene("CHAPTER 2A：爆紅路線 — 首次巡演", story, ["（巡演話題發燒中…）"])
        self.clear_choice_buttons()

        def pick_high() -> None:
            self.apply_effects(
                {
                    "fame": 12,
                    "money": 8,
                    "health": -15,
                    "controversy": 5,
                    "identity": -3,
                }
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：高強度巡演的代價",
                "「你把行程塞滿，每一站都拚盡全力。票房數字讓公司笑得很開心，"
                "但經紀人也忍不住在後台提醒你：『你眼底的黑眼圈快比舞台燈還亮。』\n\n"
                "你點頭，心裡卻清楚——你正在用身體換取存在感。」",
                [
                    "@musicdaily：這新人也太拼了吧，幾乎每週都有演出。",
                    "@tourfan：現場真的有感染力，感覺會越來越紅。",
                    "@popwatch：他是不是根本沒睡？公司也太狠。",
                ],
                self._show_ch2a_crisis,
            )

        def pick_small() -> None:
            self.apply_effects(
                {
                    "fame": 5,
                    "image": 10,
                    "health": -5,
                    "identity": 5,
                    "money": 3,
                }
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：精緻巡演的口碑累積",
                "「你刻意把場次變少，卻把每一場的細節拉滿。燈光、編曲、走位都一再調整。"
                "經紀人一邊看報表一邊嘀咕曝光量，卻也不得不承認：『至少沒人說你敷衍。』\n\n"
                "你走出場館，夜風很涼，心裡卻很穩。」",
                [
                    "@critic_room：他的 live 比錄音室版本更有生命力。",
                    "@indiefan：這不是普通新人，舞台設計很有想法。",
                    "@industrytalk：曝光少了一點，但質感很高。",
                ],
                self._show_ch2a_crisis,
            )

        self.add_choice("高強度巡演", pick_high)
        self.add_choice("精緻小型巡演", pick_small)

    def _show_ch2a_crisis(self) -> None:
        story = (
            "「今晚你參與了一場晚會。訪談中，主持人問你：『你覺得現在的音樂圈，最難的是什麼？』\n\n"
            "你停了一秒，回答：『有時候大家太在意表面工夫，反而失去了本質。』\n\n"
            "影片釋出後，輿論迅速發酵。有人說你真誠，也有人說你剛紅就開始高傲。第一次公關危機來了。」"
        )
        self.show_scene("CHAPTER 2A：第一次公關危機", story, ["（留言區兩極化…）"])
        self.clear_choice_buttons()

        def pick_apology() -> None:
            self.apply_effects(
                {"image": 8, "controversy": -5, "identity": 3, "fame": 3}
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：道歉之後的溫度",
                "「你選擇先把姿態放低。長文發出去後，留言區慢慢出現『至少很真誠』的聲音。"
                "經紀人鬆了一口氣：『先止血，後面我們再談作品。』\n\n"
                "你知道危機沒有完全消失，但至少——你拿回了一點敘事權。」",
                [
                    "@stanaccount：這個道歉蠻真誠的欸。",
                    "@musicdaily：新人危機處理得不錯。",
                    "@haterzone：現在才道歉也太晚。",
                ],
                self.show_chapter3,
            )

        def pick_statement() -> None:
            self.apply_effects(
                {"image": -5, "controversy": 8, "fame": 5, "identity": -3}
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：聲明與輿論的拉鋸",
                "「公司替你發出措辭嚴謹的聲明。媒體標題變得更聳動，黑粉與粉絲在線上對撞。"
                "經紀人拍拍你的肩：『話題也是資產。』\n\n"
                "你看著手機上跳動的通知，突然有種說不清的疲憊。」",
                [
                    "@popwatch：哇，公司開始硬起來了。",
                    "@critic_room：其實原本也沒那麼嚴重吧？",
                    "@haterzone：又是典型公關稿。",
                ],
                self.show_chapter3,
            )

        def pick_silent() -> None:
            self.apply_effects(
                {"image": -8, "controversy": 5, "health": -5, "fame": 3}
            )
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：沉默的代價",
                "「你什麼都沒說。世界卻把你的沉默解讀成一百種版本。"
                "經紀人急得跳腳，卻也拿你沒辦法：『你至少回個表情符號也好啊。』\n\n"
                "你把螢幕關掉，發現自己比想像中更累。」",
                [
                    "@rumorpage：他怎麼還沒回應？",
                    "@haterzone：冷處理是不是心虛？",
                    "@stanaccount：希望他只是太累了。",
                ],
                self.show_chapter3,
            )

        self.add_choice("承認表達不夠好，自己發文道歉", pick_apology)
        self.add_choice("發正式聲明，否認指控", pick_statement)
        self.add_choice("不回應，等待風波過去", pick_silent)

    # ----- Chapter 2B：穩定成長線 -----

    def _show_ch2b_album(self) -> None:
        story = (
            "「你的名字開始出現在某些地方。偶爾有人在留言區提到你，也有人說："
            "『他的新歌還不錯，期待未來發展。』\n\n"
            "你知道自己正在往上，但也隨時可能被取代。\n\n"
            "幾天後，你被叫進公司。經紀人把平板推到你面前：『打鐵趁熱，單曲之後就是專輯。"
            "專輯會定義你的風格，也會決定你是不是只是 one-hit wonder。』\n\n"
            "你要怎麼做這張專輯？」"
        )
        self.show_scene("CHAPTER 2B：穩定成長線 — 第一張專輯", story, ["（樂評與粉絲都在等專輯方向…）"])
        self.clear_choice_buttons()

        def pick_commercial() -> None:
            self.apply_effects(
                {"fame": 12, "money": 12, "image": -3, "identity": -8}
            )
            self._album_type = "commercial"
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：專輯發行結果：商業爆發",
                "「專輯上線後，首頁推薦、短影音背景音樂、排行榜幾乎都被你的名字佔據。"
                "Creative Artist Records 對結果非常滿意，商業合作也開始增加。\n\n"
                "但同時，有些樂評指出，這張專輯雖然完整，卻少了一點屬於你的危險感。"
                "你第一次感覺到：成功不一定代表自由。」",
                [
                    "@popfan：這張真的每首都能當主打。",
                    "@musicdaily：新生代商業流行代表出現了。",
                    "@critic_room：完成度很高，但也有點太安全。",
                ],
                self._show_ch2b_transition,
            )

        def pick_concept() -> None:
            self.apply_effects({"image": 12, "identity": 8, "fame": 5, "money": -3})
            self._album_type = "concept"
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：專輯發行結果：慢熱的深度",
                "「專輯上架的第一週，討論聲量不算爆，但樂評與核心聽眾開始一篇篇拆解你的概念線。"
                "經紀人看著曲線皺眉：『我們需要更多入口。』卻也不得不承認：『這張有靈魂。』\n\n"
                "你在深夜反覆聽完整張專輯，心裡知道——你終於把『自己』放進去了。」",
                [
                    "@critic_room：這張一開始不抓耳，但越聽越有東西。",
                    "@indiefan：終於有新人願意認真做概念專輯。",
                    "@popwatch：聲量好像沒有預期高。",
                ],
                self._show_ch2b_transition,
            )

        def pick_reject() -> None:
            self.apply_effects(
                {
                    "image": 8,
                    "identity": 12,
                    "money": -8,
                    "fame": -3,
                    "controversy": 5,
                }
            )
            self._album_type = ""
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：專輯之路：選擇獨行",
                "「你拒絕了公司替你寫好的『安全答案』。會議室安靜得可怕，"
                "經紀人收起平板，語氣變冷：『你知道這代表什麼嗎？』\n\n"
                "你點頭。你知道——接下來的每一步，都要自己負責。」",
                [
                    "@industrytalk：聽說他跟公司有點僵。",
                    "@indiefan：至少他沒有變成公司產品。",
                    "@popwatch：這樣真的撐得下去嗎？",
                ],
                self._show_ch2b_reject_bridge,
            )

        self.add_choice("全權交由 A&R 打造商業專輯", pick_commercial)
        self.add_choice("製作個人概念專輯", pick_concept)
        self.add_choice("拒絕公司干涉，自己摸索", pick_reject)

    def _show_ch2b_reject_bridge(self) -> None:
        """穩定線選「拒絕公司」後的第二章收束，再進入第三章（與 A/B 路線節奏對齊）。"""
        story = (
            "「你選擇自己摸索，會議室裡的氣氛變得緊繃。經紀人沒有多說什麼，只在離開前留下一句："
            "『那就用作品說話吧。』\n\n"
            "你知道接下來的每一步，都會更孤獨，也更接近真正的自己。」"
        )
        self.show_scene(
            "CHAPTER 2B：與公司之間",
            story,
            ["（業界都在猜你還能撐多久…）"],
        )
        self.clear_choice_buttons()
        self.add_choice("繼續", self.show_chapter3)

    def _show_ch2b_transition(self) -> None:
        at = self._album_type
        if at == "commercial":
            title = "CHAPTER 2B：成功之後的選擇"
            story = (
                "「首張專輯大成功，你變成『大家都聽過的人』。但會議室裡，經紀人的表情卻很嚴肅："
                "『你現在很成功，但有一個問題。你太容易被預測了，一個不小心就會被替代。』\n\n"
                "你要怎麼走下一步？」"
            )
        elif at == "concept":
            title = "CHAPTER 2B：藝術與市場的拉扯"
            story = (
                "「首張專輯發布後，許多人說你的作品很特別。不過對公司來說，成長太慢、商業轉換率太低。\n\n"
                "經紀人說：『你也要考慮長期發展。公司不會永遠投資在報酬率低的藝術家身上。』\n\n"
                "你要怎麼回應？」"
            )
        else:
            self.show_chapter3()
            return

        self.show_scene(title, story, ["（公司與你之間氣氛微妙…）"])
        self.clear_choice_buttons()

        if at == "commercial":

            def pick_safe() -> None:
                self.apply_effects(
                    {"fame": 10, "money": 10, "image": -3, "identity": -8}
                )
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

            def pick_art() -> None:
                self.apply_effects(
                    {"image": 10, "identity": 8, "fame": 3, "money": -3}
                )
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

            self.add_choice("延續商業路線，穩定賺錢", pick_safe)
            self.add_choice("嘗試更個人、更小眾的風格", pick_art)

        else:

            def pick_slow() -> None:
                self.apply_effects(
                    {"image": 10, "identity": 10, "fame": 3, "money": -3}
                )
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

            def pick_market() -> None:
                self.apply_effects(
                    {"fame": 10, "money": 8, "image": -3, "identity": -5}
                )
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

            self.add_choice("保持現在風格，慢慢累積", pick_slow)
            self.add_choice("改得更清楚、更市場化", pick_market)

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
            "你不知道這是真是假，但你知道一件事：你的成名之路，已經不只是娛樂圈的遊戲。」"
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
