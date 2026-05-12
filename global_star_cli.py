from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple


StatName = str
NodeId = str


@dataclass(slots=True)
class GameState:
    """遊戲狀態（數值 + 旗標）。

    Attributes:
        city_name: 出道城市。
        style: 出道風格（Rebel/Pop Idol/Indie）。
        fame: 名氣（0-100）。
        image: 形象（0-100）。
        health: 健康（0-100）。
        money: 金錢（0-100）。
        has_mystery_producer: 是否與神祕製作人合作（伏筆）。
        rng: 亂數產生器（可重現）。
    """

    city_name: str
    style: str
    fame: int
    image: int
    health: int
    money: int
    has_mystery_producer: bool = False
    rng: random.Random = field(default_factory=random.Random, repr=False)

    def clamp(self) -> None:
        """把所有數值限制在 0-100。"""
        self.fame = max(0, min(100, self.fame))
        self.image = max(0, min(100, self.image))
        self.health = max(0, min(100, self.health))
        self.money = max(0, min(100, self.money))


@dataclass(slots=True)
class Choice:
    """一個選項。"""

    key: str
    label: str
    next_node: NodeId
    apply: Optional[Callable[[GameState], None]] = None


@dataclass(slots=True)
class Node:
    """一個劇情節點：文字 + 多個選項。"""

    node_id: NodeId
    text: str
    choices: List[Choice]
    gate: Optional[Callable[[GameState], bool]] = None


def _print_hr() -> None:
    print("\n" + "=" * 72)


def _prompt_choice(choices: Sequence[Choice]) -> Choice:
    valid: Dict[str, Choice] = {c.key.lower(): c for c in choices}
    keys = ", ".join(sorted(valid.keys()))
    while True:
        raw = input(f"請輸入選項（{keys}）：").strip().lower()
        if raw in valid:
            return valid[raw]
        print("無效輸入，請再試一次。")


def _render_state(s: GameState) -> str:
    return f"fame={s.fame} | image={s.image} | health={s.health} | money={s.money}"


def _ending_name(s: GameState) -> str:
    """依條件回傳結局名稱。"""
    if s.fame >= 90 and s.image >= 60:
        return "POP ICON（商業神話）"
    if s.fame >= 80 and s.image <= 40:
        return "CONTROVERSIAL LEGEND（爭議巨星）"
    if s.image >= 85 and s.fame >= 60:
        return "ARTISTIC ICON（藝術傳奇）"
    if s.fame < 20 or s.health <= 0:
        return "FALLEN STAR（隕落巨星）"
    return "OPEN END（尚未被定義的明星）"


def _intro_pick_city(rng: random.Random) -> str:
    _print_hr()
    print("《GLOBAL STAR：成名之路》CLI 版")
    print("\nPROLOGUE：無名新人")
    print("你是一個來自普通家庭的新人。請選擇出道城市：")
    print("[a] 洛杉磯（競爭激烈）")
    print("[b] 倫敦（藝術氣息）")
    print("[c] 紐約（媒體中心）")

    raw = _prompt_choice(
        [
            Choice("a", "洛杉磯", "x"),
            Choice("b", "倫敦", "x"),
            Choice("c", "紐約", "x"),
        ]
    ).key.lower()

    if raw == "a":
        return "洛杉磯"
    if raw == "b":
        return "倫敦"
    return "紐約"


def _intro_pick_style() -> str:
    _print_hr()
    print("選擇出道風格（決定主線基調）：")
    print("[a] 叛逆流派（Rebel）：容易爆紅，也容易爭議")
    print("[b] 商業流行（Pop Idol）：穩定成長，公司控制較強")
    print("[c] 藝術地下（Indie）：成長慢，評價高")

    raw = _prompt_choice(
        [
            Choice("a", "Rebel", "x"),
            Choice("b", "Pop Idol", "x"),
            Choice("c", "Indie", "x"),
        ]
    ).key.lower()

    if raw == "a":
        return "Rebel"
    if raw == "b":
        return "Pop Idol"
    return "Indie"


def _initial_stats(city: str, style: str, seed: Optional[int]) -> GameState:
    rng = random.Random(seed)

    # 城市影響初始 fame/image（你可之後微調平衡）
    if city == "洛杉磯":
        fame, image = 12, 48
    elif city == "倫敦":
        fame, image = 8, 55
    else:  # 紐約
        fame, image = 10, 52

    # 風格影響初始與後續走向
    if style == "Rebel":
        fame += 4
        image -= 6
    elif style == "Indie":
        fame -= 2
        image += 6

    s = GameState(
        city_name=city,
        style=style,
        fame=fame,
        image=image,
        health=80,
        money=10,
        rng=rng,
    )
    s.clamp()
    return s


def _chapter1_result_bucket(s: GameState) -> str:
    """依 fame/image + 些微隨機，分到 爆紅/普通成功/失敗。"""
    # base 分數：名氣權重大、形象次之，並加入小幅隨機
    score = (s.fame * 1.1) + (s.image * 0.5) + s.rng.uniform(-10.0, 10.0)

    # Rebel 稍微偏「爆紅或翻車」，Indie 稍微偏「普通但評價穩」
    if s.style == "Rebel":
        score += s.rng.uniform(-6.0, 6.0)
    elif s.style == "Indie":
        score += 2.0

    if score >= 75:
        return "爆紅"
    if score >= 55:
        return "普通成功"
    return "失敗"


def build_nodes() -> Mapping[NodeId, Node]:
    def eff_company(s: GameState) -> None:
        s.fame += 10
        s.image -= 5
        s.money += 5

    def eff_self_write(s: GameState) -> None:
        s.image += 12
        # 自作曲比較吃運氣：小幅隨機讓它「可能爆紅 or 撲街」
        swing = s.rng.randint(-8, 12)
        s.fame += swing
        s.money += 2

    def eff_mystery(s: GameState) -> None:
        s.has_mystery_producer = True
        s.fame += 6
        s.image += 6
        s.money += 1

    def eff_tour_hard(s: GameState) -> None:
        s.fame += 12
        s.money += 10
        s.health -= 22

    def eff_tour_fine(s: GameState) -> None:
        s.image += 12
        s.fame += 5
        s.health -= 10
        s.money += 4

    def eff_contro_apologize(s: GameState) -> None:
        s.image += 10
        s.fame += 2

    def eff_contro_deny(s: GameState) -> None:
        s.fame += 4
        s.image -= 10

    def eff_contro_silent(s: GameState) -> None:
        s.image -= 6

    def eff_album_commercial(s: GameState) -> None:
        s.money += 15
        s.fame += 8
        s.image -= 2

    def eff_album_concept(s: GameState) -> None:
        s.image += 14
        s.fame += 2
        s.money += 4

    def eff_album_refuse(s: GameState) -> None:
        s.image += 6
        s.fame -= 6
        s.money -= 2

    def eff_viral_catch(s: GameState) -> None:
        s.fame += 12
        s.money += 8
        s.image -= 4

    def eff_viral_natural(s: GameState) -> None:
        s.fame += 6
        s.image += 2

    def eff_viral_spin(s: GameState) -> None:
        s.fame += 10
        s.image -= 10

    return {
        "ch1_intro": Node(
            node_id="ch1_intro",
            text=(
                "引言\n\n"
                "順利與 {city_name} 當地最大的經紀公司 Creative Artist Records 簽約後的三個月，\n"
                "公司遲遲未連絡你。你站在 {city_name} 的街頭，夜幕低垂，霓虹燈一一亮起。\n\n"
                "突然，手機傳來震動，你收到經紀人訊息：\n"
                "「我們要決定你的第一首歌了，這將會定義你是誰。」\n\n"
                "你希望你的第一首歌是："
            ),
            choices=[
                Choice("a", "交給公司製作", "ch1_company", eff_company),
                Choice("b", "自己創作", "ch1_self", eff_self_write),
                Choice("c", "與神祕製作人合作", "ch1_mystery", eff_mystery),
            ],
        ),
        "ch1_company": Node(
            node_id="ch1_company",
            text=(
                "你決定交給公司製作你的出道曲。\n"
                "旋律洗腦、節奏精準、封面完美，社群開始出現你的名字。\n"
                "「這新人很穩欸」\n"
                "「但有點……沒特色？」\n"
                "你看著數字上升，心裡卻莫名空虛。"
            ),
            choices=[Choice("a", "進入發行後反應判定", "ch1_react")],
        ),
        "ch1_self": Node(
            node_id="ch1_self",
            text=(
                "你拒絕公司提供的 demo，一個人關在房間裡反覆修改旋律。\n"
                "那首歌不像商品，更像日記。你忐忑等待市場的驗證。"
            ),
            choices=[Choice("a", "進入發行後反應判定", "ch1_react")],
        ),
        "ch1_mystery": Node(
            node_id="ch1_mystery",
            text=(
                "你聯繫了那位神祕製作人。\n"
                "舊錄音室裡沒有團隊，只有他一個人。\n"
                "他幾乎沉默，但總是知道如何放大你的優勢。\n"
                "發行後反應兩極：「天才」與「聽不懂」並存。"
            ),
            choices=[Choice("a", "進入發行後反應判定", "ch1_react")],
        ),
        "ch1_react": Node(
            node_id="ch1_react",
            text=(
                "🎬 CHAPTER 1：第一首歌的代價（發行後反應）\n"
                "接下來會依你的數值，判定是爆紅、普通成功或失敗。"
            ),
            choices=[Choice("a", "判定結果", "ch1_route")],
        ),
        "ch1_route": Node(
            node_id="ch1_route",
            text="",
            choices=[
                Choice("a", "前往下一章", "ch2_dispatch"),
            ],
        ),
        "ch2_dispatch": Node(
            node_id="ch2_dispatch",
            text=(
                "🎬 CHAPTER 2：名氣的分裂\n"
                "你的下一步會依 Chapter 1 的反應進入：\n"
                "- 2A 爆紅路線（Rising Star）\n"
                "- 2B 穩定成長線（Industry Artist）\n"
                "- 2C 地下/黑暗線（Hidden Rise）"
            ),
            choices=[Choice("a", "繼續", "ch2_enter")],
        ),
        "ch2_enter": Node(
            node_id="ch2_enter",
            text="",
            choices=[Choice("a", "（系統）依結果進入對應路線", "ch2_enter")],
        ),
        "2a_status": Node(
            node_id="2a_status",
            text=(
                "2A：爆紅路線（Rising Star）\n\n"
                "發行單曲後，你的名字幾乎無處不在。\n"
                "推薦頁、短影片、排行榜——你是演算法寵兒。\n"
                "同時，大家也開始討論你什麼時候會「掉下來」。"
            ),
            choices=[Choice("a", "進入首次巡演事件", "2a_tour")],
        ),
        "2a_tour": Node(
            node_id="2a_tour",
            text=(
                "🎤 事件：首次巡演\n"
                "經紀人說：「流量可以讓人認識你，但舞台才會讓人留下來。」\n"
                "你看著行程表，城市一個接一個。你要怎麼選？"
            ),
            choices=[
                Choice("a", "高強度巡演（賺錢、fame↑↑、health↓）", "2a_media", eff_tour_hard),
                Choice("b", "精緻小型巡演（image↑、成長慢）", "2a_media", eff_tour_fine),
            ],
        ),
        "2a_media": Node(
            node_id="2a_media",
            text=(
                "💥 媒體事件（爭議）\n"
                "訪談中你說：「有時候大家太在意表面工夫，反而失去了本質。」\n"
                "影片釋出後輿論發酵：暗諷市場？批評粉絲？\n\n"
                "面對首次公關危機，你選擇："
            ),
            choices=[
                Choice("a", "全面接受批評、承認錯誤（真誠道歉）", "ch3_entry", eff_contro_apologize),
                Choice("b", "否認指控、發正式聲明（硬起來）", "ch3_entry", eff_contro_deny),
                Choice("c", "不回應、冷處理", "ch3_entry", eff_contro_silent),
            ],
        ),
        "2b_status": Node(
            node_id="2b_status",
            text=(
                "2B：穩定成長線（Industry Artist）\n\n"
                "你的名字開始出現在某些地方。\n"
                "你知道自己正在往上，但也隨時可能被取代。"
            ),
            choices=[Choice("a", "進入專輯製作會議", "2b_album")],
        ),
        "2b_album": Node(
            node_id="2b_album",
            text=(
                "🎤 事件：專輯製作機會\n"
                "經紀人說：「打鐵趁熱，單曲後就是專輯。沒辦法用專輯證明自己的人，會被市場拋棄。」\n"
                "你要怎麼做這張『會定義你的專輯』？"
            ),
            choices=[
                Choice("a", "商業流行專輯（money↑↑、fame+、公式化風險）", "2b_transition", eff_album_commercial),
                Choice("b", "個人概念專輯（image↑↑、fame不穩）", "2b_transition", eff_album_concept),
                Choice("c", "拒絕公司干涉（衝突、資源變少）", "2b_transition", eff_album_refuse),
            ],
        ),
        "2b_transition": Node(
            node_id="2b_transition",
            text=(
                "💼 公司壓力與轉型考驗\n"
                "你感受到公司與市場的期待正在收緊。\n"
                "（此處先把 Chapter 2B 的主要決策收束到 Chapter 3 匯流點。）"
            ),
            choices=[Choice("a", "前往 Chapter 3 匯流點", "ch3_entry")],
        ),
        "2c_status": Node(
            node_id="2c_status",
            text=(
                "2C：地下/黑暗線（Hidden Rise）\n\n"
                "你的歌突然被社群瘋傳。\n"
                "「有點怪，但會上癮」\n"
                "經紀人半夜打來：『你的歌爆了，你現在要決定怎麼處理這波流量。』"
            ),
            choices=[Choice("a", "進入病毒式爆紅的選擇", "2c_viral")],
        ),
        "2c_viral": Node(
            node_id="2c_viral",
            text=(
                "🎧 事件：病毒式爆紅\n"
                "你要怎麼處理突如其來的流量？"
            ),
            choices=[
                Choice("a", "抓緊機會，接住流量（商業化）", "ch3_entry", eff_viral_catch),
                Choice("b", "順其自然，沒有大動作（保留空間）", "ch3_entry", eff_viral_natural),
                Choice("c", "把影響力最大化，操作輿論（爭議風險）", "ch3_entry", eff_viral_spin),
            ],
        ),
        "ch3_entry": Node(
            node_id="ch3_entry",
            text=(
                "🎬 CHAPTER 3：巨星的代價（匯流點）\n"
                "你站上更大的舞台，但代價也開始成形。\n"
                "接下來會進入結局判定。"
            ),
            choices=[Choice("a", "進入結局", "final")],
        ),
        "final": Node(
            node_id="final",
            text="🧠 FINAL CHAPTER：結局分支（依 fame/image/health 判定）",
            choices=[Choice("a", "看我的結局", "end")],
        ),
        "end": Node(
            node_id="end",
            text="",
            choices=[],
        ),
    }


def _format_text(text: str, s: GameState) -> str:
    return (
        text.replace("{city_name}", s.city_name)
        .replace("{style}", s.style)
    )


def _dispatch_ch2(s: GameState) -> NodeId:
    """根據 Chapter 1 的結果，決定進入 2A/2B/2C。"""
    bucket = _chapter1_result_bucket(s)

    # 對應你原本的大綱：爆紅→2A、普通→2B、失敗→重新定位/黑暗（這裡先接 2C）
    if bucket == "爆紅":
        s.fame += 10
        s.money += 5
        return "2a_status"
    if bucket == "普通成功":
        s.fame += 4
        s.money += 3
        return "2b_status"

    # 失敗：名氣下滑，可能觸發「重新定位事件」
    s.fame -= 8
    s.image += 2  # 有些人覺得你真實
    return "2c_status"


def _maybe_force_controversy(s: GameState) -> bool:
    """若 image 過低，強制進入爭議巨星線（簡化版：直接影響結局）。"""
    return s.image <= 40


def run(seed: Optional[int] = None) -> None:
    """啟動 CLI 遊戲。

    Args:
        seed: 亂數種子。若提供，可重現遊戲結果。
    """
    city = _intro_pick_city(random.Random(seed))
    style = _intro_pick_style()
    s = _initial_stats(city=city, style=style, seed=seed)
    nodes = build_nodes()

    current: NodeId = "ch1_intro"
    ch1_bucket: Optional[str] = None

    while True:
        node = nodes[current]
        if node.gate is not None and not node.gate(s):
            raise RuntimeError(f"節點無法進入：{current}")

        _print_hr()
        if node.text:
            print(_format_text(node.text, s))

        if current == "ch1_route":
            ch1_bucket = _chapter1_result_bucket(s)
            if ch1_bucket == "爆紅":
                print("\n結果：📈 爆紅！你的名字在社群與排行榜上快速擴散。")
            elif ch1_bucket == "普通成功":
                print("\n結果：⚖️ 普通成功。你被看見了，但還沒被定義。")
            else:
                print("\n結果：💥 失敗。你感到市場的冷淡與公司的不耐。")

        if current == "ch2_enter":
            assert ch1_bucket is not None
            current = _dispatch_ch2(s)
            s.clamp()
            continue

        if current == "end":
            print(f"城市：{s.city_name} | 風格：{s.style}")
            print(f"最終數值：{_render_state(s)}")
            if s.has_mystery_producer:
                print("伏筆：你曾與神祕製作人合作（星辰議會的影子仍在）。")

            # 若形象太低，提醒玩家：這條線容易走向爭議結局
            if _maybe_force_controversy(s):
                print("提示：你的 image 偏低，輿論會更容易把你推向爭議巨星型態。")

            print(f"\n結局：{_ending_name(s)}")
            break

        print(f"\n目前狀態：{_render_state(s)}")
        for c in node.choices:
            print(f"[{c.key}] {c.label}")

        choice = _prompt_choice(node.choices)
        if choice.apply is not None:
            choice.apply(s)
            s.clamp()
        current = choice.next_node


if __name__ == "__main__":
    # 你可以把 seed 改成固定數字來重現結果，例如 run(seed=42)
    run(seed=None)
