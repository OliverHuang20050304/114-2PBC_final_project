"""結局判定與結局文案。"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

ENDING_POP_ICON = (
    "POP ICON：商業神話",
    "「你成為時代的代表，全球巡演售罄，廣告與獎項接踵而來。所有人都知道你的名字。"
    "但某些深夜裡，你偶爾會懷疑，舞台上的那個人是否還是最初的自己。」",
)

ENDING_CONTROVERSIAL = (
    "CONTROVERSIAL LEGEND：爭議巨星",
    "「一半的人愛你，一半的人恨你。你不只是歌手，而是話題本身。"
    "每一次發言、沉默、轉身，都能讓世界再次討論你。」",
)

ENDING_ARTISTIC = (
    "ARTISTIC ICON：藝術傳奇",
    "「你沒有成為最容易被消費的明星，卻成為最難被取代的存在。"
    "多年後，音樂學院開始研究你的作品，稱你為不屬於時代的人。」",
)

ENDING_FALLEN = (
    "FALLEN STAR：隕落巨星",
    "「名氣散去，合約終止，媒體不再提起你的名字。你消失在人群之中，"
    "也許某天會以製作人的身份重新開始，也許只是安靜地離開。」",
)

ENDING_DEFAULT = (
    "INDUSTRY SURVIVOR：產業倖存者",
    "「你沒有登上神壇，也沒有徹底墜落。你學會在市場、公司、粉絲與自我之間生存。"
    "下一首歌還沒有完成，而你也還沒有結束。」",
)

ENDING_SOCIAL: List[str] = [
    "@musicdaily：故事告一段落，但音樂還在。",
    "@you：點擊「重新開始」再玩一次不同選擇吧。",
]


def compute_ending(player: Dict[str, Any]) -> Tuple[str, str]:
    """依指定順序計算結局標題與內文。"""
    fame = int(player["fame"])
    image = int(player["image"])
    health = int(player["health"])
    controversy = int(player["controversy"])
    identity = int(player["identity"])

    if fame >= 85 and image >= 55 and controversy <= 60:
        return ENDING_POP_ICON
    if fame >= 80 and image <= 45 and controversy >= 40:
        return ENDING_CONTROVERSIAL
    if image >= 80 and fame >= 55 and identity >= 60:
        return ENDING_ARTISTIC
    if fame < 20 or health <= 10:
        return ENDING_FALLEN
    return ENDING_DEFAULT
