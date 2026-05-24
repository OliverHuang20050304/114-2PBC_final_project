"""第二章 A：標題與社群留言（場景正文見 image/.../圖片文本對照Idol_CH2A.txt）。"""

from __future__ import annotations

from typing import Dict, List

CH2A_TOUR_TITLE = "CHAPTER 2A：爆紅路線 — 首次巡演"
CH2A_DEFAULT_TITLE = "CHAPTER 2A"
CH2A_CRISIS_TITLE = "CHAPTER 2A：第一次公關危機"

CH2A_TOUR_OPEN_SOCIAL: Dict[str, List[str]] = {
    "016": ["（巡演話題發燒中…）"],
    "017": ["@popwatch：他什麼時候會掉下來？"],
}

CH2A_TOUR_CHOICE_COMMENTS: List[str] = ["@musicdaily：現場表演才是藝人的靈魂。"]

CH2A_HIGH_TOUR_SOCIAL: Dict[str, List[str]] = {
    "021": [
        "@tourfan：他是不是根本沒睡?",
        "@popwatch：這行程也太地獄",
    ],
    "022": ["@haterzone：現場翻車?"],
    "023": [
        "@stanaccount：應該只是累了?",
        "@critic_room：這經紀公司也是想錢想瘋了",
    ],
}

CH2A_SMALL_TOUR_SOCIAL: Dict[str, List[str]] = {
    "024": [
        "@critic_room：他的live比錄音還強",
        "@indiefan：完全不是流水線藝人",
    ],
    "025": ["@industrytalk：怎麼都不跑場?感覺沒什麼野心?"],
}

CH2A_CRISIS_SOCIAL: Dict[str, List[str]] = {
    "028": [
        "@haterzone：他是在說粉絲嗎?",
        "@popwatch：剛紅就這樣?",
        "@rumorpage：從大牌經紀公司出來的人講這種話好諷刺",
    ],
}

CH2A_APOLOGY_SOCIAL: Dict[str, List[str]] = {
    "029": [
        "@stanaccount：他說的本來就是實話",
        "@musicdaily：這種反應反而有點可愛",
        "@critic_room：很真誠的道歉",
    ],
}

CH2A_STATEMENT_SOCIAL: Dict[str, List[str]] = {
    "030": [
        "@haterzone：想賺市場的錢又瞧不起主流聽眾",
        "@popwatch：不是,這也沒什麼吧",
        "@critic_room：酸民們真嗜血",
    ],
}

CH2A_SILENT_SOCIAL: Dict[str, List[str]] = {
    "031": [
        "@rumorpage：他怎麼還沒回應?",
        "@haterzone：公司應該想息事寧人吧",
        "@industrytalk：他應該是因為太難搞被冷凍了",
    ],
}
