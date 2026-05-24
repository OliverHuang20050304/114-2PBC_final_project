"""第一章：UI 標題、社群留言（場景正文見 image/Pop_Idol_Base/CH1/圖片文本對照.txt）。"""

from __future__ import annotations

from typing import Dict, List

# 引言 000～002 畫面上方重複顯示的提問標題（含 {style} 佔位符）
CH1_INTRO_TITLE = (
    "出道曲對一位藝人來說至關重要，它奠定眾人對你的第一印象。Creative Artist Recordss有許多老牌的製作人能夠為你提供你想要的{style}歌曲。"
    "不過，在這個快速變動的網路世代，能夠真實傳遞自我的自作曲或許更能抓人眼球。與此同時，先前在聚會上結識的神祕製作人也主動向你地出橄欖枝，你希望你的第一首歌是："
)

CH1_INTRO_COMMENTS: Dict[str, List[str]] = {
    "000": ["（歌迷正在刷新頁面…）"],
    "001": ["@agent_creative：我們要決定你的第一首歌了。"],
    "002": ["@musicdaily：新人的出道曲會走哪條路？"],
}

CH1_DEFAULT_SOCIAL: List[str] = ["（社群討論升溫中…）"]

CH1_ROUTE_A_SOCIAL: Dict[str, List[str]] = {
    "005": [
        "@musicdaily：這新人很穩欸",
        "@popfan：感覺會紅",
        "@critic_room：但有點……沒特色？",
    ],
}

CH1_ROUTE_B_SOCIAL: Dict[str, List[str]] = {
    "008": [
        "@stanaccount：這首歌是誰寫的？",
        "@musicdaily：有點太真實了吧…",
        "@critic_room：我直接哭出來",
    ],
    "010": [
        "@popwatch：這首歌好像沒什麼聲量。",
        "@industrytalk：公司應該開始緊張了。",
        "@smallfan：我其實覺得很好聽，只是大家還沒發現。",
    ],
}

CH1_ROUTE_C_SOCIAL: Dict[str, List[str]] = {
    "014": [
        "@musicdaily：這很天才，我馬上就上癮了",
        "@critic_room：我完全聽不懂",
        "@rumorpage：這人是誰？",
    ],
}
