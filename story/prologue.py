"""序章：標題、旁白與社群留言。"""

from __future__ import annotations

from typing import Dict, List

PROLOGUE_START_TITLE = "PROLOGUE：成名之前"
PROLOGUE_START_BODY = (
    "「你是一位來自普通家庭的新人，剛與 Creative Artist Records 簽約。"
    "你即將踏上成名之路。」"
)
PROLOGUE_START_COMMENTS: List[str] = ["（尚未有留言）"]

PROLOGUE_CITY_TITLE = "PROLOGUE：落腳的城市"
PROLOGUE_CITY_BODY = "請選擇你主要發展的城市："
PROLOGUE_CITY_COMMENTS: List[str] = ["（粉絲還在觀望中…）"]

PROLOGUE_STYLE_TITLE = "PROLOGUE：你要成為誰"
PROLOGUE_STYLE_BODY = "請選擇你的出道風格："
PROLOGUE_STYLE_COMMENTS: List[str] = ["@musicdaily：新簽約藝人即將曝光？"]

CITY_EFFECTS: Dict[str, Dict[str, int]] = {
    "洛杉磯": {"fame": 5, "image": -3},
    "倫敦": {"image": 5, "fame": 3},
    "紐約": {"fame": 3, "money": 5},
}

STYLE_EFFECTS: Dict[str, Dict[str, int]] = {
    "叛逆流派 Rebel": {"fame": 5, "controversy": 5, "image": -3},
    "商業流行 Pop Idol": {"fame": 3, "money": 5, "identity": -3},
    "藝術地下 Indie": {"image": 8, "fame": -3, "identity": 5},
}
