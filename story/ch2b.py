"""第二章 B：標題、過場旁白與社群留言（場景正文見 image/.../圖片文本對照Idol_CH2B.txt）。"""

from __future__ import annotations

from typing import Dict, List, Tuple

CH2B_ALBUM_TITLE = (
    "你剛結束一段公司安排的曝光行程，你的出道曲在發行一個月後仍在榜上，最近還時常被用來當作旅遊vlog的背景音。"
    "但你自己已經開始擔心：「這首迴響還不錯，但下一首呢？」、「這是我要走的風格嗎」"
    "幾天後，你被叫進公司，當天，會議室裡沒有寒暄，經紀人直接把平板推到你面前。"
    "「打鐵趁熱，單曲發行後接著就是專輯了，專輯將會定義你的風格、建構你的音樂世界。沒辦法用專輯證明自己的人，會被演算法與市場拋棄。"
    "你現在卡在一個不上不下的位置，你已經被看見了，但還沒被定義。」"
    "他們給了幾種方案，你想要怎麼做這張「會定義你的專輯」"
)

CH2B_DEFAULT_TITLE = "CHAPTER 2B"

CH2B_ALBUM_OPEN_SOCIAL: Dict[str, List[str]] = {
    "032": ["（你的名字開始被更多人看見…）"],
    "033": ["@popfan：他的新歌還不錯，期待未來發展。"],
}

CH2B_ALBUM_CHOICE_COMMENTS: List[str] = ["（樂評與粉絲都在等專輯方向…）"]

CH2B_COMMERCIAL_SOCIAL: Dict[str, List[str]] = {
    "036": [
        "@popfan：這張怎麼每首都可以當主打",
        "@musicdaily：我原本只想聽一首結果整張播完",
        "@critic_room：今年的聲音",
    ],
}

CH2B_CONCEPT_SOCIAL: Dict[str, List[str]] = {
    "039": ["@popwatch：專輯上線第一天，好安靜。"],
    "040": [
        "@critic_room：這張其實很好聽欸",
        "@indiefan：我一開始沒懂,現在回去整張重聽",
        "@musicdaily：怎麼越晚越紅?",
    ],
}

CH2B_REJECT_SOCIAL: Dict[str, List[str]] = {
    "041": [
        "@industrytalk：聽說他跟公司有點僵。",
        "@popwatch：這樣真的撐得下去嗎？",
    ],
    "043": [
        "@indiefan：至少他沒有變成公司產品。",
        "@critic_room：評價兩極,但很像他自己。",
    ],
}

CH2B_TRANSITION_TITLES: Dict[str, str] = {
    "commercial": "CHAPTER 2B：成功之後的選擇",
    "concept": "CHAPTER 2B：藝術與市場的拉扯",
}

CH2B_TRANSITION_SOCIAL: Dict[str, List[str]] = {
    "044": ["（公司與你之間氣氛微妙…）"],
    "045": ["（公司與你之間氣氛微妙…）"],
}

# (標題, 正文, 社群留言)
CH2B_RESULT_SCENES: Dict[str, Tuple[str, str, List[str]]] = {
    "safe": (
        "CHAPTER 2 RESULT：轉型之後｜商業加碼",
        "「你選擇把路走得更『可預測』。公司立刻排進更多代言與綜藝窗口，"
        "會議室的白板上寫滿下一步 KPI。經紀人笑得很真：『這才是長紅的打法。』\n\n"
        "你點頭，卻在深夜練歌時突然恍神——你還記得最初想唱的那句話嗎？」",
        [
            "@popfan：他真的很懂市場。",
            "@musicdaily：商業成績太強了。",
            "@critic_room：安全，但缺少驚喜。",
        ],
    ),
    "art": (
        "CHAPTER 2 RESULT：轉型之後｜往內走",
        "「你把下一張作品的母帶鎖進私人資料夾，只給少數信得過的人聽。"
        "經紀人嘆氣卻也點頭：『好吧，至少你還願意跟我們溝通。』\n\n"
        "你感覺到風向在變——慢，但往你想要的方向。」",
        [
            "@critic_room：這個轉向很聰明。",
            "@indiefan：終於看到他自己的東西了。",
            "@popfan：我有點懷念以前比較好懂的歌。",
        ],
    ),
    "slow": (
        "CHAPTER 2 RESULT：轉型之後｜慢火累積",
        "「你沒有為了榜單硬轉彎。公司嘴上抱怨，卻仍替你留了一條藝術行銷的窄路。"
        "經紀人把咖啡推到你面前：『你可以慢，但不能停。』\n\n"
        "你把那句話記下來，像記一句咒語。」",
        [
            "@critic_room：他可能不是最快紅的，但會紅很久。",
            "@indiefan：這才是藝術家的樣子。",
            "@industrytalk：商業面還是有疑慮。",
        ],
    ),
    "market": (
        "CHAPTER 2 RESULT：轉型之後｜更市場的入口",
        "「你把旋律線拉直、把副歌變得更『一聽就懂』。數據很快給出正向回饋，"
        "經紀人拍桌：『對嘛，這才是能養活團隊的作品。』\n\n"
        "你笑了笑，心裡卻知道：你交換了一些神秘，換來一些確定。」",
        [
            "@popfan：這次好聽很多欸。",
            "@critic_room：變好入口了，但也少了一點神秘感。",
            "@industrytalk：這是比較成熟的選擇。",
        ],
    ),
}
