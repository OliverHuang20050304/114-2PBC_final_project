"""結局判定與結局文案。"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

ENDING_POP_ICON = (
    "POP ICON：商業神話",
    "\"You are not in the industry, YOU ARE THE MUSIC INDUSTRY.\"\n\n"
    "#全球巡演 #時代巨星 #被觀看的人生\n\n"
    "你成為時代的代表，全球巡演售罄，廣告、獎項與時尚資源接踵而來。"
    "所有人都知道你的名字，而你的一言一行都能定義流行文化。"
    "只是某些深夜裡，你偶爾會懷疑，舞台上的那個人是否還是最初的自己。\n\n"
    "Part of growing up and moving into new chapters of your life is about catch and release.——Taylor Swift\n\n"
    "You’re not getting it. It’s not clocking to you … I don’t give a f—k if you’re on the sidewalk. I’m a human f–king being, you’re standing around my car, at the beach!——Justin Bieber\n\n",
)

ENDING_CONTROVERSIAL = (
    "CONTROVERSIAL LEGEND：爭議巨星",
    "\"They called you a villain, BUT THE WORLD STILL BOWED.\"\n\n"
    "#瘋狂天才 #失控 #混亂 #拒絕被馴服的靈魂\n\n"
    "一半的人愛你，一半的人恨你。你不只是歌手，而是話題本身。"
    "每一次發言、沉默、轉身，都能讓世界再次討論你。"
    "你站在傳奇與災難之間，永遠被觀看，也永遠不能鬆手。\n\n"
    "Truth is my goal. Controversy is my gym. I'll do a hundred reps of controversy for a 6 pack of truth.——Kanye West\n\n"
    "I want to tell the people out there, thank you for supporting me. And if you don't, suck my dick——Cardi B\n\n",
)

ENDING_ARTISTIC = (
    "ARTISTIC ICON：藝術傳奇",
    "\"Greatness revealed in silence.\"\n\n"
    "#拒絕營業 #十年磨一劍 #有時會不見\n\n"
    "你沒有成為最容易被消費的明星，卻成為最難被取代的存在。"
    "多年後，音樂學院與樂評人開始研究你的作品。"
    "世界曾經嫌你太慢、太安靜、太難懂，最後卻承認你留下了真正能穿越時間的聲音。\n\n"
    "When your art comes from a real place, the noise of the world just fades away——Lana Del Rey\n\n"
    "My pussy tastes like Pepsi Cola——also Lana Del Rey\n\n"
    "My music is great for crying, but please don’t cry in front of me. It’s awkward.——Frank Ocean\n\n",
)

ENDING_FALLEN = (
    "FALLEN STAR：隕落巨星",
    "遊戲結束，你未能繼續歌手生涯。\n\n"
    "娛樂圈是一座黃金打造的囚牢，它複雜、殘酷且從不為任何人停下。"
    "一失足，全盤皆輸。\n\n"
    "名氣散去，合約終止，媒體不再提起你的名字。"
    "你消失在人群之中，也許某天會以製作人的身份重新開始，也許只是安靜地離開。",
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
    forced = player.get("forced_ending")
    forced_endings = {
        "pop_icon": ENDING_POP_ICON,
        "controversial": ENDING_CONTROVERSIAL,
        "artistic": ENDING_ARTISTIC,
        "fallen": ENDING_FALLEN,
    }
    if forced in forced_endings:
        return forced_endings[forced]

    fame = int(player["fame"])
    image = int(player["image"])
    health = int(player["health"])
    identity = int(player["identity"])

    if fame >= 90 and image >= 60:
        return ENDING_POP_ICON
    if fame >= 80 and image <= 40:
        return ENDING_CONTROVERSIAL
    if image >= 85 and fame >= 60 and identity >= 60:
        return ENDING_ARTISTIC
    if fame < 20 or health <= 10:
        return ENDING_FALLEN
    return ENDING_DEFAULT
