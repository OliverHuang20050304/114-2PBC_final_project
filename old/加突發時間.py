"""
GLOBAL STAR：成名之路 — 以 CustomTkinter 製作的敘事模擬遊戲。
強化版：加入隨機事件系統 + NPC 關係系統
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

# ══════════════════════════════════════════════════════════════════
#  新增：NPC 定義
# ══════════════════════════════════════════════════════════════════

NPC_DEFS: Dict[str, Dict[str, str]] = {
    "manager": {
        "name": "林經紀",
        "role": "你的經紀人",
        "icon": "🧑‍💼",
        "desc": "老練、務實，以公司利益為優先，但內心仍在乎你的前途。",
    },
    "producer": {
        "name": "陳製作",
        "role": "首席製作人",
        "icon": "🎛️",
        "desc": "音樂品味極高，對商業妥協深惡痛絕，但欣賞有才華的人。",
    },
    "rival": {
        "name": "Sky",
        "role": "同期競爭對手",
        "icon": "⭐",
        "desc": "公司捧紅的頂流新星，對你的態度忽冷忽熱，充滿算計。",
    },
    "friend": {
        "name": "阿諾",
        "role": "青梅竹馬好友",
        "icon": "🤝",
        "desc": "不在圈子裡，但永遠支持你。是你最真實自我的見證人。",
    },
}

# ══════════════════════════════════════════════════════════════════
#  新增：隨機事件資料庫
# ══════════════════════════════════════════════════════════════════

# 每個事件格式：
# {
#   "id": str,
#   "title": str,
#   "story": str,
#   "comments": List[str],
#   "choices": [
#       {
#           "text": str,
#           "effects": Dict[str, int],
#           "npc_effects": Dict[str, int],   # npc_id -> 好感度變化
#           "result": str,                   # 結果描述文字
#           "result_comments": List[str],
#       }, ...
#   ]
# }

RANDOM_EVENTS: List[Dict[str, Any]] = [
    {
        "id": "rumor_scandal",
        "title": "🔥 突發事件：緋聞風波",
        "story": (
            "某八卦媒體突然爆出一張你與某位藝人的「親密照」，雖然照片角度曖昧，"
            "實際上只是在同一個活動的普通合照。\n\n"
            "林經紀火速打來：「你要怎麼處理？我們要搶在輿論發酵前決定！」"
        ),
        "comments": [
            "@rumorpage：等等，這兩個人？？",
            "@popwatch：有沒有更多照片……",
            "@stanaccount：先等官方說明！",
        ],
        "choices": [
            {
                "text": "立刻澄清，發聲明說是誤解",
                "effects": {"image": 5, "controversy": -5, "fame": 2},
                "npc_effects": {"manager": 10, "rival": -5},
                "result": (
                    "「你的聲明在一小時內發出，措辭冷靜、附上現場全景照。"
                    "大部分輿論接受了解釋，林經紀鬆了口氣：『這次處理得不錯。』」"
                ),
                "result_comments": [
                    "@musicdaily：一看就知道是誤會，還好有澄清。",
                    "@popfan：專業處理，加好感。",
                    "@haterzone：哼，這麼快澄清一定有鬼。",
                ],
            },
            {
                "text": "不回應，讓粉絲自行解讀",
                "effects": {"fame": 8, "controversy": 10, "image": -5},
                "npc_effects": {"manager": -10, "friend": 5},
                "result": (
                    "「沉默反而讓話題延燒三天。林經紀幾乎每小時都在催你，"
                    "你只是把手機靜音。阿諾傳來一句：『別理他們，做你自己。』\n\n"
                    "熱搜卻真的停不下來。」"
                ),
                "result_comments": [
                    "@rumorpage：他不回應就是默認吧？",
                    "@stanaccount：也有可能根本懶得理閒言閒語。",
                    "@popwatch：這波流量……他賺到了。",
                ],
            },
            {
                "text": "把事件寫進新歌，化危機為創作",
                "effects": {"image": 10, "identity": 8, "fame": 5, "money": -3},
                "npc_effects": {"producer": 15, "manager": -5},
                "result": (
                    "「你花了一個通宵寫出一首隱晦又真誠的歌，直接丟給陳製作。"
                    "他聽完沉默很久，最後說：『就這樣發。不用解釋。』\n\n"
                    "林經紀看著成品搖頭，但也沒有阻止你。」"
                ),
                "result_comments": [
                    "@critic_room：他把醜聞變成了藝術，我服了。",
                    "@musicdaily：這首歌意外地很好聽。",
                    "@popfan：真的假的，這反應也太帥了吧。",
                ],
            },
        ],
    },
    {
        "id": "health_crisis",
        "title": "🏥 突發事件：身體亮紅燈",
        "story": (
            "連續趕場三週後，你在後台突然眩暈，被工作人員扶住才沒倒下。"
            "隨行醫生警告：「再這樣下去，你會在台上暈倒。」\n\n"
            "林經紀一臉為難：「下週還有三場通告，你自己決定。」\n"
            "阿諾傳訊：「你還好嗎？比賽不是人生全部啊。」"
        ),
        "comments": [
            "@industrytalk：聽說他最近行程滿到快崩潰。",
            "@stanaccount：拜託公司讓他休息一下。",
            "@popwatch：他臉色最近真的很差……",
        ],
        "choices": [
            {
                "text": "撐下去，完成所有通告",
                "effects": {"fame": 8, "money": 8, "health": -20, "identity": -5},
                "npc_effects": {"manager": 15, "friend": -10},
                "result": (
                    "「你靠著止痛藥和咖啡硬撐過三場。林經紀豎起大拇指：『你真的很拚。』\n\n"
                    "但阿諾打來電話，沉默了很久才說：『你知道有些東西失去了就找不回來的。』」"
                ),
                "result_comments": [
                    "@popfan：他也太敬業了！",
                    "@critic_room：這種拚法感覺不太對。",
                    "@stanaccount：心疼，但也欣賞他的職業精神。",
                ],
            },
            {
                "text": "取消行程，強制休養一週",
                "effects": {"health": 25, "identity": 8, "fame": -5, "money": -5},
                "npc_effects": {"friend": 15, "manager": -10, "rival": 5},
                "result": (
                    "「你把手機交給助理，躺了整整兩天。第三天，你第一次在沒有鬧鐘的情況下自然醒來。\n\n"
                    "林經紀嘴上說『沒關係』，眼神卻寫著『你欠我的』。Sky趁機搶走了兩個代言。\n\n"
                    "阿諾送來了一鍋雞湯，什麼都沒說。」"
                ),
                "result_comments": [
                    "@popwatch：休養是對的！健康最重要。",
                    "@industrytalk：Sky動作真快……",
                    "@stanaccount：希望他好好休息，我們等他回來。",
                ],
            },
            {
                "text": "和陳製作商量，改以錄音代替現場通告",
                "effects": {"health": 10, "image": 5, "identity": 5, "money": 2},
                "npc_effects": {"producer": 10, "manager": 0},
                "result": (
                    "「陳製作二話不說幫你重新安排行程，用錄音特輯取代現場露出。"
                    "成品品質出乎意料地好，甚至有人說：『比現場版更有感。』\n\n"
                    "你終於在工作與身體之間找到一條縫。」"
                ),
                "result_comments": [
                    "@musicdaily：這個錄音特輯竟然比現場更動人。",
                    "@critic_room：聰明的處理方式。",
                    "@popfan：沒有看到真人有點失望，但理解。",
                ],
            },
        ],
    },
    {
        "id": "rival_collab",
        "title": "突發事件：Sky 的合作邀請",
        "story": (
            "你最大的競爭對手 Sky 突然私下聯繫你，提出要一起合作一首歌。\n\n"
            "「我知道我們一直在競爭，」Sky 說，「但我覺得我們放在一起會很有趣。\n"
            "你想想，兩個方向完全不同的聲音放在同一首歌裡——」\n\n"
            "林經紀在旁邊搖頭：「小心，他可能在算計你。」\n"
            "陳製作卻說：「音樂上的碰撞才是最好的。」"
        ),
        "comments": [
            "@musicdaily：Sky + 你？？這組合也太不可思議了吧",
            "@rumorpage：有緋聞嗎有緋聞嗎有緋聞嗎",
            "@critic_room：如果真的合作，我願意付錢聽。",
        ],
        "choices": [
            {
                "text": "接受合作，放下競爭",
                "effects": {"fame": 12, "image": 5, "identity": -3, "money": 8},
                "npc_effects": {"rival": 20, "producer": 8, "manager": 5},
                "result": (
                    "「合作的過程比你想像的更順。Sky 有你沒有的舞台控制力，"
                    "你有他沒有的情感深度。陳製作說：『這首歌會讓兩邊的粉絲都記住你們。』\n\n"
                    "上線當天，雙方粉絲同時涌入，數字漂亮得讓林經紀直接貼了截圖給老闆。」"
                ),
                "result_comments": [
                    "@stanaccount：合作曲直接榜一！！",
                    "@popfan：以前以為他們是對手，原來可以這麼搭。",
                    "@critic_room：今年最好的合作沒有之一。",
                ],
            },
            {
                "text": "婉拒，保持獨立路線",
                "effects": {"identity": 10, "image": 5, "fame": -3},
                "npc_effects": {"rival": -10, "friend": 8, "manager": -5},
                "result": (
                    "「你很禮貌地說不。Sky 沉默了幾秒，只說：『好，那以後再說。』\n\n"
                    "林經紀嘆氣，但阿諾說：『你有自己的路，不用因為別人的光環改變方向。』」"
                ),
                "result_comments": [
                    "@industrytalk：為什麼不合作啊，可惜了。",
                    "@indiefan：反而覺得他的堅持很迷人。",
                    "@popwatch：Sky 怎麼想？",
                ],
            },
            {
                "text": "接受，但要求主導創作方向",
                "effects": {"image": 8, "identity": 8, "fame": 8, "controversy": 5},
                "npc_effects": {"rival": 5, "producer": 15, "manager": -3},
                "result": (
                    "「你提出了條件：創作主導權必須是你。Sky 沒想到你會這樣談，"
                    "沉默之後同意了。\n\n陳製作幾乎整夜守在錄音室：『這才是你應該有的態度。』\n\n"
                    "最終成品帶著明顯你的風格，Sky 粉絲反應兩極，你的粉絲卻更愛你了。」"
                ),
                "result_comments": [
                    "@critic_room：這首歌明顯是他主導的，Sky 反而退讓了？",
                    "@stanaccount：他竟然談到主導權！好強！",
                    "@rumorpage：Sky 粉絲翻了，說被搶主角。",
                ],
            },
        ],
    },
    {
        "id": "contract_pressure",
        "title": "突發事件：合約修改風波",
        "story": (
            "公司突然送來一份新合約修訂版，要求你的創作版權全部歸公司所有，"
            "換取三倍的行銷預算與曝光保證。\n\n"
            "「這在業界很正常，」林經紀說，「要紅就要付出代價。」\n"
            "陳製作私下找你說：「他們不告訴你的是，你以後每一首歌都不再是你的了。」\n"
            "阿諾說：「你問問自己，你當初為什麼要唱歌。」"
        ),
        "comments": [
            "@industrytalk：這種合約在圈子裡很常見，但……",
            "@indiefan：版權這個問題太重要了，不能隨便簽。",
            "@popwatch：他會簽嗎？",
        ],
        "choices": [
            {
                "text": "簽下去，換取更大的舞台",
                "effects": {"fame": 15, "money": 15, "identity": -15, "image": -3},
                "npc_effects": {"manager": 20, "producer": -15, "friend": -10},
                "result": (
                    "「你在合約上簽下名字的時候，手有一點抖。\n\n"
                    "林經紀立刻啟動新的行銷計畫，三週內你的名字出現在更多地方。"
                    "陳製作沒有再傳訊息。阿諾說：『我支持你，但……你還好嗎？』」"
                ),
                "result_comments": [
                    "@popfan：他要大爆發了！！",
                    "@industrytalk：這個決定很大膽，也很有風險。",
                    "@indiefan：心疼，那些歌以後都不是他的了。",
                ],
            },
            {
                "text": "拒簽，找律師談判",
                "effects": {"identity": 15, "image": 8, "money": -8, "fame": -3},
                "npc_effects": {"producer": 15, "friend": 10, "manager": -15},
                "result": (
                    "「你找了一位獨立的娛樂律師，陳製作介紹的。談判拉鋸了兩週，"
                    "最後保住了五成的版權，但公司明顯把資源往別人身上移。\n\n"
                    "阿諾說：『你做對了。那些歌是你的命。』」"
                ),
                "result_comments": [
                    "@critic_room：藝人能保住版權真的很難得，佩服。",
                    "@industrytalk：跟公司槓，後面的路會不好走。",
                    "@indiefan：這才是有骨氣的藝人。",
                ],
            },
            {
                "text": "拖延決定，先觀察局勢",
                "effects": {"controversy": 5, "identity": 3, "image": -3},
                "npc_effects": {"manager": -8, "producer": 5},
                "result": (
                    "「你說需要時間考慮，林經紀臉色有點難看，但沒有催你。\n\n"
                    "一週後，公司推出了另一位新人，明顯是在給你壓力。\n"
                    "陳製作說：『他們在測試你的底線。』」"
                ),
                "result_comments": [
                    "@popwatch：他到底要不要簽？公司已經出新人了。",
                    "@industrytalk：這是公司給他的壓力，看他怎麼接招。",
                    "@stanaccount：等他，不要急。",
                ],
            },
        ],
    },
    {
        "id": "fan_meeting",
        "title": "🎤 突發事件：粉絲見面會意外",
        "story": (
            "粉絲見面會進行到一半，一位粉絲突然在台下暈倒。"
            "現場頓時混亂，工作人員趕緊處理，但所有人的鏡頭都對準了你——\n\n"
            "你接下來的反應，會被幾千支手機同步直播出去。\n\n"
            "林經紀在耳機裡說：「按照流程，先請粉絲退場。」\n"
            "你看著台下那個女孩，心裡有個聲音在說別的話。"
        ),
        "comments": [
            "@stanaccount：剛剛發生什麼了？直播斷了！",
            "@popfan：有粉絲昏倒？？希望沒事。",
            "@rumorpage：等等，他要怎麼處理……",
        ],
        "choices": [
            {
                "text": "立刻走下台，親自陪伴那位粉絲",
                "effects": {"image": 15, "identity": 10, "fame": 8, "money": -2},
                "npc_effects": {"friend": 10, "manager": -3, "rival": -5},
                "result": (
                    "「你跳下台，蹲在她旁邊，握著她的手說：『別怕，我在這。』\n\n"
                    "那個畫面被幾千支手機錄下來，十分鐘後洗版整個社群。\n"
                    "林經紀說：『這不在流程裡。』你說：『我知道。』」"
                ),
                "result_comments": [
                    "@stanaccount：我哭了，他真的衝下去了。",
                    "@musicdaily：這個畫面會被記住很久。",
                    "@popfan：今天之後我是真的粉了，不是飯。",
                ],
            },
            {
                "text": "在台上宣布暫停，讓工作人員處理",
                "effects": {"image": 5, "fame": 3, "identity": 2},
                "npc_effects": {"manager": 10},
                "result": (
                    "「你用穩定的語氣宣布暫時暫停，請觀眾保持冷靜，讓工作人員進場。\n\n"
                    "處理完後，見面會繼續。林經紀說：『你沒有讓現場失控，做得好。』\n\n"
                    "但你知道，今晚有一個機會，你選擇了最安全的那個。」"
                ),
                "result_comments": [
                    "@popwatch：處理得算專業，但感覺有點冷。",
                    "@stanaccount：希望那位粉絲沒事。",
                    "@industrytalk：危機處理中規中矩。",
                ],
            },
            {
                "text": "繼續表演，相信工作人員能處理",
                "effects": {"image": -10, "controversy": 10, "fame": 3, "money": 5},
                "npc_effects": {"manager": 5, "friend": -15, "rival": 5},
                "result": (
                    "「你繼續唱完那首歌。工作人員把粉絲帶出去，現場維持了秩序。\n\n"
                    "但事後一段影片流出：那位粉絲被抬走的時候，你仍然在台上。\n\n"
                    "阿諾只說了一句話：『你是不是忘記了，你當初說自己是為了什麼在唱歌？』」"
                ),
                "result_comments": [
                    "@haterzone：她昏倒你繼續唱？？？",
                    "@popwatch：我懂他可能是專業考量，但觀感真的很差。",
                    "@stanaccount：不想相信他是這種人……",
                ],
            },
        ],
    },
]


# ══════════════════════════════════════════════════════════════════
#  原有輔助函式（保留）
# ══════════════════════════════════════════════════════════════════

def clamp_player(player: Dict[str, Any]) -> None:
    for key in ("fame", "image", "health", "money", "identity", "controversy"):
        if key in player:
            val = int(player[key])
            player[key] = max(0, min(100, val))


def new_player() -> Dict[str, Any]:
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
        # 新增：NPC 好感度（0～100）
        "npc_affinity": {
            "manager": 50,
            "producer": 30,
            "rival": 20,
            "friend": 70,
        },
        # 新增：本局已觸發事件 ID 集合（避免重複）
        "triggered_events": [],
    }


def apply_deltas(player: Dict[str, Any], deltas: Dict[str, int]) -> None:
    for key, delta in deltas.items():
        if key in player and isinstance(player[key], (int, float)):
            player[key] += delta
    clamp_player(player)


def apply_npc_deltas(player: Dict[str, Any], npc_deltas: Dict[str, int]) -> None:
    """套用 NPC 好感度變化。"""
    affinity = player.setdefault("npc_affinity", {k: 50 for k in NPC_DEFS})
    for npc_id, delta in npc_deltas.items():
        if npc_id in affinity:
            affinity[npc_id] = max(0, min(100, affinity[npc_id] + delta))


def clean_story_text(text: str) -> str:
    cleaned = re.sub(r"^status_flavor\s*=\s*\"\"\"?\s*", "", text.strip())
    return cleaned.replace('"""', "").strip()


def load_story_map(path: Path) -> Dict[str, str]:
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
    return load_story_map(path)


def format_narrative(text: str, player: Dict[str, Any]) -> str:
    city = str(player.get("city") or "這座城市")
    style = str(player.get("style") or "流行")
    formatted = text.replace("{city_name}", city).replace("{style}", style)
    return formatted.replace("**", "")


def format_ch1_narrative(text: str, player: Dict[str, Any]) -> str:
    return format_narrative(text, player)


def ch1_image_path(scene_id: str) -> Optional[Path]:
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


# ══════════════════════════════════════════════════════════════════
#  主視窗
# ══════════════════════════════════════════════════════════════════

class GlobalStarApp(ctk.CTk):
    """主視窗與遊戲流程控制。"""

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("GLOBAL STAR：成名之路")
        self.geometry("1280x860")
        self.minsize(1000, 720)

        self.player: Dict[str, Any] = new_player()
        self._album_type: str = ""
        self._ch1_stories: Dict[str, str] = load_ch1_story_map()
        self._ch2a_stories: Dict[str, str] = load_story_map(CH2A_STORY_FILE)
        self._ch2b_stories: Dict[str, str] = load_story_map(CH2B_STORY_FILE)
        self._current_ctk_image: Optional[ctk.CTkImage] = None
        # 新增：隨機事件佇列（每章給 1 個）
        self._pending_event: Optional[Dict[str, Any]] = None
        # 新增：事件後繼續呼叫的函式
        self._after_event_callback: Optional[Callable[[], None]] = None

        self._build_layout()
        self.show_start()

    # ── 輔助函式 ──────────────────────────────────────────────────

    def clamp_stats(self) -> None:
        clamp_player(self.player)

    def apply_effects(self, effects: Dict[str, int]) -> None:
        apply_deltas(self.player, effects)

    def _apply_npc_effects(self, npc_effects: Dict[str, int]) -> None:
        apply_npc_deltas(self.player, npc_effects)
        self._update_npc_panel()

    def update_status_panel(self) -> None:
        self.clamp_stats()
        for key, lbl in self.stats_labels.items():
            lbl.configure(text=str(int(self.player[key])))

    def update_social_reactions(self, comments: List[str]) -> None:
        self.set_social(comments)

    def clear_choice_buttons(self) -> None:
        for w in self.choices_frame.winfo_children():
            w.destroy()

    def restart_game(self) -> None:
        self.show_start()

    def show_scene(
        self,
        title: str,
        story: str,
        comments: Optional[List[str]] = None,
        *,
        clear_image: bool = True,
    ) -> None:
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
        self.show_scene(title, story, comments)
        self.clear_choice_buttons()
        self.add_choice("繼續", next_function)

    # ── 新增：隨機事件系統 ────────────────────────────────────────

    def _pick_random_event(self) -> Optional[Dict[str, Any]]:
        """隨機選取一個本局尚未觸發過的事件。"""
        triggered = set(self.player.get("triggered_events", []))
        available = [e for e in RANDOM_EVENTS if e["id"] not in triggered]
        if not available:
            return None
        return random.choice(available)

    def maybe_trigger_event(self, after_callback: Callable[[], None]) -> None:
        """
        有 60% 機率在章節之間插入一個隨機事件。
        若不觸發，直接呼叫 after_callback。
        """
        event = self._pick_random_event()
        if event is None or random.random() > 0.6:
            after_callback()
            return
        # 標記為已觸發
        self.player.setdefault("triggered_events", []).append(event["id"])
        self._show_random_event(event, after_callback)

    def _show_random_event(
        self, event: Dict[str, Any], after_callback: Callable[[], None]
    ) -> None:
        """顯示隨機事件主畫面與選項。"""
        self.show_scene(
            event["title"],
            "【突發事件！】\n\n" + event["story"],
            event["comments"],
        )
        self.clear_choice_buttons()
        for choice in event["choices"]:
            # 用 default 參數捕獲 closure 變數
            def make_handler(c=choice):
                def handler():
                    self._resolve_event_choice(c, after_callback)
                return handler
            self.add_choice(choice["text"], make_handler())

    def _resolve_event_choice(
        self, choice: Dict[str, Any], after_callback: Callable[[], None]
    ) -> None:
        """套用選擇結果後顯示結果頁。"""
        self.apply_effects(choice["effects"])
        self._apply_npc_effects(choice.get("npc_effects", {}))
        self.update_status_panel()

        # 顯示事件結果中受影響的 NPC 提示
        npc_lines = self._npc_reaction_lines(choice.get("npc_effects", {}))
        comments = choice["result_comments"] + npc_lines

        self.show_result_scene(
            "【事件結果】",
            choice["result"],
            comments,
            after_callback,
        )

    def _npc_reaction_lines(self, npc_effects: Dict[str, int]) -> List[str]:
        """產生 NPC 好感度變化的提示文字。"""
        lines = []
        for npc_id, delta in npc_effects.items():
            if npc_id not in NPC_DEFS:
                continue
            name = NPC_DEFS[npc_id]["name"]
            if delta > 0:
                lines.append(f" {name} 好感度 +{delta}")
            elif delta < 0:
                lines.append(f" {name} 好感度 {delta}")
        return lines

    # ── 新增：NPC 面板 ────────────────────────────────────────────

    def _update_npc_panel(self) -> None:
        """重繪右側 NPC 好感度列。"""
        affinity = self.player.get("npc_affinity", {})
        for npc_id, bar in self._npc_bars.items():
            val = affinity.get(npc_id, 50)
            bar.set(val / 100)
        for npc_id, lbl in self._npc_val_labels.items():
            val = affinity.get(npc_id, 50)
            lbl.configure(text=str(val))

    # ── 介面建構 ──────────────────────────────────────────────────

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text="GLOBAL STAR：成名之路",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(16, 8), sticky="n")

        # 故事面板
        self.story_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.story_panel.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        self.story_panel.grid_columnconfigure(0, weight=1)
        self.story_panel.grid_rowconfigure(1, weight=1)

        self.scene_image_label = ctk.CTkLabel(self.story_panel, text="", corner_radius=12)
        self._scene_image_grid = {"row": 0, "column": 0, "pady": (0, 8), "sticky": "n"}

        self.story_box = ctk.CTkTextbox(
            self.story_panel,
            wrap="word",
            font=ctk.CTkFont(size=18),
            corner_radius=12,
            border_width=1,
        )
        self.story_box.grid(row=1, column=0, sticky="nsew")

        # 右側面板（數值 + NPC）
        right_panel = ctk.CTkFrame(self, corner_radius=12, border_width=1)
        right_panel.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")

        # ── 屬性數值 ──
        ctk.CTkLabel(
            right_panel,
            text="屬性",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(12, 4))

        self.stats_labels: Dict[str, ctk.CTkLabel] = {}
        stat_keys = [
            ("fame", "名氣"),
            ("image", "形象"),
            ("health", "健康"),
            ("money", "金錢"),
            ("identity", "自我"),
            ("controversy", "爭議"),
        ]
        for key, zh in stat_keys:
            row = ctk.CTkFrame(right_panel, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=3)
            ctk.CTkLabel(row, text=f"{zh}：", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
            lbl = ctk.CTkLabel(row, text="0", font=ctk.CTkFont(size=14))
            lbl.pack(side="right")
            self.stats_labels[key] = lbl

        ctk.CTkFrame(right_panel, height=1, fg_color="gray40").pack(fill="x", padx=10, pady=8)

        # ── NPC 好感度 ──
        ctk.CTkLabel(
            right_panel,
            text="人際關係",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(0, 6))

        self._npc_bars: Dict[str, ctk.CTkProgressBar] = {}
        self._npc_val_labels: Dict[str, ctk.CTkLabel] = {}

        for npc_id, info in NPC_DEFS.items():
            frame = ctk.CTkFrame(right_panel, fg_color="transparent")
            frame.pack(fill="x", padx=12, pady=4)

            top_row = ctk.CTkFrame(frame, fg_color="transparent")
            top_row.pack(fill="x")
            ctk.CTkLabel(
                top_row,
                text=f"{info['icon']} {info['name']}",
                font=ctk.CTkFont(size=13, weight="bold"),
            ).pack(side="left")
            val_lbl = ctk.CTkLabel(top_row, text="50", font=ctk.CTkFont(size=12))
            val_lbl.pack(side="right")
            self._npc_val_labels[npc_id] = val_lbl

            ctk.CTkLabel(
                frame,
                text=info["role"],
                font=ctk.CTkFont(size=11),
                text_color="gray60",
            ).pack(anchor="w")

            bar = ctk.CTkProgressBar(frame, height=8, corner_radius=4)
            bar.set(0.5)
            bar.pack(fill="x", pady=(2, 0))
            self._npc_bars[npc_id] = bar

        # ── 底部（選項 + 社群）──
        self.bottom = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))
        self.bottom.grid_columnconfigure(0, weight=1)
        self.bottom.grid_columnconfigure(1, weight=1)

        self.choices_outer = ctk.CTkFrame(self.bottom, corner_radius=12, border_width=1)
        self.choices_outer.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(
            self.choices_outer,
            text="你的抉擇",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(10, 4))
        self.choices_frame = ctk.CTkFrame(self.choices_outer, fg_color="transparent")
        self.choices_frame.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        self.social_frame = ctk.CTkFrame(self.bottom, corner_radius=12, border_width=1)
        self.social_frame.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
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
        self.story_box.configure(state="normal")
        self.story_box.delete("1.0", "end")
        self.story_box.insert("1.0", text.strip())
        self.story_box.configure(state="disabled")

    def clear_scene_image(self) -> None:
        self._current_ctk_image = None
        self.scene_image_label.grid_remove()

    def _show_scene_image_label(self) -> None:
        self.scene_image_label.grid(**self._scene_image_grid)

    def set_scene_image(self, image_path: Optional[Path]) -> None:
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
            self.scene_image_label.configure(image=self._current_ctk_image, text="")
        except ImportError:
            self.clear_scene_image()
            if not getattr(self, "_pil_warned", False):
                self._pil_warned = True
                print("提示：請安裝 Pillow 以顯示場景插圖：pip install Pillow", flush=True)
        except OSError:
            self.clear_scene_image()

    def _narrative(self, story_map: Dict[str, str], scene_id: str, fallback: str = "") -> str:
        raw = story_map.get(scene_id.zfill(3), fallback)
        return format_narrative(raw, self.player) if raw else fallback

    def _ch1_narrative(self, scene_id: str, fallback: str = "") -> str:
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
        resolver = image_resolver or ch1_image_path
        smap = story_map or self._ch1_stories
        self.set_scene_image(resolver(scene_id))
        story = self._narrative(smap, scene_id, fallback_story)
        self.show_scene(title, story, comments, clear_image=False)
        self.clear_choice_buttons()
        if on_continue is not None:
            self.add_choice("繼續", on_continue)

    def set_social(self, lines: List[str]) -> None:
        self.social_text.configure(state="normal")
        self.social_text.delete("1.0", "end")
        self.social_text.insert("1.0", "\n".join(lines))
        self.social_text.configure(state="disabled")

    def refresh_stats(self) -> None:
        self.update_status_panel()

    def clear_choices(self) -> None:
        self.clear_choice_buttons()

    def add_choice(self, text: str, command: Callable[[], None]) -> None:
        btn = ctk.CTkButton(
            self.choices_frame,
            text=text,
            command=command,
            corner_radius=14,
            height=40,
            font=ctk.CTkFont(size=15),
        )
        btn.pack(fill="x", padx=12, pady=8)

    # ══════════════════════════════════════════════════════════════
    #  遊戲流程（與原版相同，但章節銜接處加入 maybe_trigger_event）
    # ══════════════════════════════════════════════════════════════

    def show_start(self) -> None:
        self.player = new_player()
        self._album_type = ""
        self.update_status_panel()
        self._update_npc_panel()
        self.update_social_reactions(["（尚未有留言）"])
        self.show_scene(
            "PROLOGUE：成名之前",
            "「你是一位來自普通家庭的新人，剛與 Creative Artist Records 簽約。\n"
            "你即將踏上成名之路。」\n\n"
            "  - 林經紀：你的經紀人\n"
            "  - 陳製作：首席製作人\n"
            "  - Sky：同期競爭對手\n"
            "  - 阿諾：青梅竹馬好友",
            ["（尚未有留言）"],
        )
        self.clear_choice_buttons()
        self.add_choice("開始遊戲", self.show_city_selection)

    def show_city_selection(self) -> None:
        self.show_scene("PROLOGUE：落腳的城市", "請選擇你主要發展的城市：", ["（粉絲還在觀望中…）"])
        self.clear_choice_buttons()

        def pick_la() -> None:
            self.player["city"] = "洛杉磯"
            self.apply_effects({"fame": 5, "image": -3})
            self._apply_npc_effects({"manager": 5})
            self.update_status_panel()
            self.show_style_selection()

        def pick_london() -> None:
            self.player["city"] = "倫敦"
            self.apply_effects({"image": 5, "fame": 3})
            self._apply_npc_effects({"producer": 5})
            self.update_status_panel()
            self.show_style_selection()

        def pick_ny() -> None:
            self.player["city"] = "紐約"
            self.apply_effects({"fame": 3, "money": 5})
            self._apply_npc_effects({"manager": 3, "rival": 3})
            self.update_status_panel()
            self.show_style_selection()

        self.add_choice("洛杉磯", pick_la)
        self.add_choice("倫敦", pick_london)
        self.add_choice("紐約", pick_ny)

    def show_style_selection(self) -> None:
        self.show_scene("PROLOGUE：你要成為誰", "請選擇你的出道風格：", ["@musicdaily：新簽約藝人即將曝光？"])
        self.clear_choice_buttons()

        def pick_rebel() -> None:
            self.player["style"] = "叛逆流派 Rebel"
            self.apply_effects({"fame": 5, "controversy": 5, "image": -3})
            self._apply_npc_effects({"producer": 8, "manager": -5, "rival": 5})
            self.update_status_panel()
            self.show_chapter1()

        def pick_pop() -> None:
            self.player["style"] = "商業流行 Pop Idol"
            self.apply_effects({"fame": 3, "money": 5, "identity": -3})
            self._apply_npc_effects({"manager": 10, "rival": 3, "producer": -3})
            self.update_status_panel()
            self.show_chapter1()

        def pick_indie() -> None:
            self.player["style"] = "藝術地下 Indie"
            self.apply_effects({"image": 8, "fame": -3, "identity": 5})
            self._apply_npc_effects({"producer": 12, "friend": 5, "manager": -3})
            self.update_status_panel()
            self.show_chapter1()

        self.add_choice("叛逆流派 Rebel", pick_rebel)
        self.add_choice("商業流行 Pop Idol", pick_pop)
        self.add_choice("藝術地下 Indie", pick_indie)

    def show_chapter1(self) -> None:
        self._show_ch1_intro("000")

    def _show_ch1_intro(self, scene_id: str) -> None:
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

        self.show_visual_scene(scene_id, title, comments=comments, on_continue=nxt)
        if scene_id == "002":
            self.clear_choice_buttons()
            self.add_choice("交給公司製作", self._ch1_route_a)
            self.add_choice("自己創作（成功或失敗隨機）", self._ch1_route_b_start)
            self.add_choice("與神秘製作人合作", self._ch1_route_c)

    def _ch1_route_a(self) -> None:
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
        self._apply_npc_effects({"manager": 10, "producer": -5})
        self.player["route"] = "stable"
        self.update_status_panel()
        # ★ 加入隨機事件觸發點
        self.maybe_trigger_event(self.show_chapter2)

    def _ch1_route_b_start(self) -> None:
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
        self._ch1_play_sequence(scenes, social_at=social, on_finish=self._ch1_finish_route_b)

    def _ch1_finish_route_b(self) -> None:
        if getattr(self, "_ch1_b_success", False):
            self.apply_effects({"fame": 10, "image": 8, "identity": 5, "money": -3})
            self._apply_npc_effects({"producer": 12, "friend": 8, "manager": 3})
            self.player["route"] = "rising"
        else:
            self.apply_effects({"fame": -5, "image": 3, "identity": 3, "money": -3})
            self._apply_npc_effects({"producer": 5, "manager": -8, "friend": 5})
            self.player["route"] = "hidden"
        self.update_status_panel()
        self.maybe_trigger_event(self.show_chapter2)

    def _ch1_route_c(self) -> None:
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
        self.apply_effects({"fame": 10, "image": -3, "controversy": 8, "identity": -3})
        self._apply_npc_effects({"producer": -10, "manager": 5, "rival": 8})
        self.player["hidden_producer"] = True
        self.player["route"] = "hidden"
        self.update_status_panel()
        self.maybe_trigger_event(self.show_chapter2)

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
        social_at = social_at or {}

        def play_at(index: int) -> None:
            sid = scene_ids[index]
            comments = social_at.get(sid, ["（社群討論升溫中…）"])
            is_last = index + 1 >= len(scene_ids)
            if not is_last:
                nxt = lambda i=index + 1: play_at(i)
                self.show_visual_scene(sid, title, comments=comments, on_continue=nxt,
                                       story_map=story_map, image_resolver=image_resolver)
            elif final_continue:
                self.show_visual_scene(sid, title, comments=comments, on_continue=on_finish,
                                       story_map=story_map, image_resolver=image_resolver)
            else:
                self.show_visual_scene(sid, title, comments=comments, on_continue=None,
                                       story_map=story_map, image_resolver=image_resolver)
                on_finish()

        play_at(0)

    def _ch1_play_sequence(self, scene_ids, *, social_at=None, on_finish):
        self._play_scene_sequence(
            scene_ids, "CHAPTER 1",
            story_map=self._ch1_stories, image_resolver=ch1_image_path,
            social_at=social_at, on_finish=on_finish,
        )

    def show_chapter2(self) -> None:
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

    # ── Chapter 2A ──────────────────────────────────────────────

    def _ch2a_play(self, scene_ids, title, *, social_at=None, on_finish, final_continue=True):
        self._play_scene_sequence(
            scene_ids, title,
            story_map=self._ch2a_stories, image_resolver=ch2a_image_path,
            social_at=social_at, on_finish=on_finish, final_continue=final_continue,
        )

    def _show_ch2a_tour(self) -> None:
        title = "CHAPTER 2A：爆紅路線 — 首次巡演"

        def show_tour_choice() -> None:
            self.show_visual_scene("018", title,
                comments=["@musicdaily：現場表演才是藝人的靈魂。"],
                story_map=self._ch2a_stories, image_resolver=ch2a_image_path)
            self.clear_choice_buttons()
            self.add_choice("高強度巡演", self._ch2a_pick_high)
            self.add_choice("精緻小型巡演", self._ch2a_pick_small)

        self._ch2a_play(["016", "017"], title,
            social_at={"016": ["（巡演話題發燒中…）"], "017": ["@popwatch：他什麼時候會掉下來？"]},
            on_finish=show_tour_choice)

    def _ch2a_pick_high(self) -> None:
        self.apply_effects({"fame": 12, "money": 8, "health": -15, "controversy": 5, "identity": -3})
        self._apply_npc_effects({"manager": 15, "friend": -10, "rival": 5})
        self.update_status_panel()
        self._ch2a_play(["019", "020", "021", "022", "023"], "CHAPTER 2A",
            social_at={
                "021": ["@tourfan：他是不是根本沒睡?", "@popwatch：這行程也太地獄"],
                "022": ["@haterzone：現場翻車?"],
                "023": ["@stanaccount：應該只是累了?", "@critic_room：這經紀公司也是想錢想瘋了"],
            },
            on_finish=self._show_ch2a_crisis)

    def _ch2a_pick_small(self) -> None:
        self.apply_effects({"fame": 5, "image": 10, "health": -5, "identity": 5, "money": 3})
        self._apply_npc_effects({"producer": 8, "friend": 8, "manager": -5})
        self.update_status_panel()
        self._ch2a_play(["024", "025"], "CHAPTER 2A",
            social_at={
                "024": ["@critic_room：他的live比錄音還強", "@indiefan：完全不是流水線藝人"],
                "025": ["@industrytalk：怎麼都不跑場?感覺沒什麼野心?"],
            },
            on_finish=self._show_ch2a_crisis)

    def _show_ch2a_crisis(self) -> None:
        title = "CHAPTER 2A：第一次公關危機"

        def show_crisis_choice() -> None:
            self.clear_choice_buttons()
            self.add_choice("承認表達不夠好，自己發文道歉", self._ch2a_pick_apology)
            self.add_choice("發正式聲明，否認指控", self._ch2a_pick_statement)
            self.add_choice("不回應，等待風波過去", self._ch2a_pick_silent)

        self._ch2a_play(["026", "027", "028"], title,
            social_at={"028": [
                "@haterzone：他是在說粉絲嗎?",
                "@popwatch：剛紅就這樣?",
                "@rumorpage：從大牌經紀公司出來的人講這種話好諷刺",
            ]},
            on_finish=show_crisis_choice, final_continue=False)

    def _ch2a_pick_apology(self) -> None:
        self.apply_effects({"image": 8, "controversy": -5, "identity": 3, "fame": 3})
        self._apply_npc_effects({"manager": 5, "friend": 8})
        self.update_status_panel()
        self._ch2a_play(["029"], "CHAPTER 2A",
            social_at={"029": [
                "@stanaccount：他說的本來就是實話",
                "@musicdaily：這種反應反而有點可愛",
                "@critic_room：很真誠的道歉",
            ]},
            on_finish=lambda: self.maybe_trigger_event(self.show_chapter3))

    def _ch2a_pick_statement(self) -> None:
        self.apply_effects({"image": -5, "controversy": 8, "fame": 5, "identity": -3})
        self._apply_npc_effects({"manager": 10, "producer": -5, "rival": 5})
        self.update_status_panel()
        self._ch2a_play(["030"], "CHAPTER 2A",
            social_at={"030": [
                "@haterzone：想賺市場的錢又瞧不起主流聽眾",
                "@popwatch：不是,這也沒什麼吧",
                "@critic_room：酸民們真嗜血",
            ]},
            on_finish=lambda: self.maybe_trigger_event(self.show_chapter3))

    def _ch2a_pick_silent(self) -> None:
        self.apply_effects({"image": -8, "controversy": 5, "health": -5, "fame": 3})
        self._apply_npc_effects({"manager": -8, "friend": 5, "rival": 3})
        self.update_status_panel()
        self._ch2a_play(["031"], "CHAPTER 2A",
            social_at={"031": [
                "@rumorpage：他怎麼還沒回應?",
                "@haterzone：公司應該想息事寧人吧",
                "@industrytalk：他應該是因為太難搞被冷凍了",
            ]},
            on_finish=lambda: self.maybe_trigger_event(self.show_chapter3))

    # ── Chapter 2B ──────────────────────────────────────────────

    def _ch2b_play(self, scene_ids, title, *, social_at=None, on_finish, final_continue=True):
        self._play_scene_sequence(
            scene_ids, title,
            story_map=self._ch2b_stories, image_resolver=ch2b_image_path,
            social_at=social_at, on_finish=on_finish, final_continue=final_continue,
        )

    def _show_ch2b_album(self) -> None:
        title = "CHAPTER 2B：穩定成長線 — 第一張專輯"

        def show_album_choice() -> None:
            self.show_visual_scene("034", title,
                comments=["（樂評與粉絲都在等專輯方向…）"],
                story_map=self._ch2b_stories, image_resolver=ch2b_image_path)
            self.clear_choice_buttons()
            self.add_choice("全權交由 A&R 打造商業專輯", self._ch2b_pick_commercial)
            self.add_choice("製作個人概念專輯", self._ch2b_pick_concept)
            self.add_choice("拒絕公司干涉，自己摸索", self._ch2b_pick_reject)

        self._ch2b_play(["032", "033"], title,
            social_at={
                "032": ["（你的名字開始被更多人看見…）"],
                "033": ["@popfan：他的新歌還不錯，期待未來發展。"],
            },
            on_finish=show_album_choice)

    def _ch2b_pick_commercial(self) -> None:
        self.apply_effects({"fame": 12, "money": 12, "image": -3, "identity": -8})
        self._apply_npc_effects({"manager": 15, "producer": -10})
        self._album_type = "commercial"
        self.update_status_panel()
        self._ch2b_play(["035", "036"], "CHAPTER 2B",
            social_at={"036": [
                "@popfan：這張怎麼每首都可以當主打",
                "@musicdaily：我原本只想聽一首結果整張播完",
                "@critic_room：今年的聲音",
            ]},
            on_finish=self._show_ch2b_transition)

    def _ch2b_pick_concept(self) -> None:
        self.apply_effects({"image": 12, "identity": 8, "fame": 5, "money": -3})
        self._apply_npc_effects({"producer": 15, "friend": 8, "manager": -5})
        self._album_type = "concept"
        self.update_status_panel()
        self._ch2b_play(["037", "038", "039", "040"], "CHAPTER 2B",
            social_at={
                "039": ["@popwatch：專輯上線第一天，好安靜。"],
                "040": [
                    "@critic_room：這張其實很好聽欸",
                    "@indiefan：我一開始沒懂,現在回去整張重聽",
                    "@musicdaily：怎麼越晚越紅?",
                ],
            },
            on_finish=self._show_ch2b_transition)

    def _ch2b_pick_reject(self) -> None:
        self.apply_effects({"image": 8, "identity": 12, "money": -8, "fame": -3, "controversy": 5})
        self._apply_npc_effects({"producer": 10, "friend": 12, "manager": -15, "rival": 3})
        self._album_type = ""
        self.update_status_panel()
        self._ch2b_play(["041", "042", "043"], "CHAPTER 2B",
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
            on_finish=lambda: self.maybe_trigger_event(self.show_chapter3))

    def _show_ch2b_transition(self) -> None:
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
                self.add_choice("嘗試更個人、更小眾的風格", self._ch2b_pick_art)
            else:
                self.add_choice("保持現在風格，慢慢累積", self._ch2b_pick_slow)
                self.add_choice("改得更清楚、更市場化", self._ch2b_pick_market)

        self._ch2b_play([scene_id], title,
            social_at={scene_id: ["（公司與你之間氣氛微妙…）"]},
            on_finish=show_transition_choice, final_continue=False)

    def _ch2b_pick_safe(self) -> None:
        self.apply_effects({"fame": 10, "money": 10, "image": -3, "identity": -8})
        self._apply_npc_effects({"manager": 12, "producer": -8})
        self.update_status_panel()
        self.show_result_scene(
            "CHAPTER 2 RESULT：轉型之後｜商業加碼",
            "「你選擇把路走得更『可預測』。公司立刻排進更多代言與綜藝窗口，"
            "會議室的白板上寫滿下一步 KPI。經紀人笑得很真：『這才是長紅的打法。』\n\n"
            "你點頭，卻在深夜練歌時突然恍神——你還記得最初想唱的那句話嗎？」",
            ["@popfan：他真的很懂市場。", "@musicdaily：商業成績太強了。", "@critic_room：安全，但缺少驚喜。"],
            lambda: self.maybe_trigger_event(self.show_chapter3),
        )

    def _ch2b_pick_art(self) -> None:
        self.apply_effects({"image": 10, "identity": 8, "fame": 3, "money": -3})
        self._apply_npc_effects({"producer": 12, "friend": 8, "manager": -5})
        self.update_status_panel()
        self.show_result_scene(
            "CHAPTER 2 RESULT：轉型之後｜往內走",
            "「你把下一張作品的母帶鎖進私人資料夾，只給少數信得過的人聽。"
            "經紀人嘆氣卻也點頭：『好吧，至少你還願意跟我們溝通。』\n\n"
            "你感覺到風向在變——慢，但往你想要的方向。」",
            ["@critic_room：這個轉向很聰明。", "@indiefan：終於看到他自己的東西了。", "@popfan：我有點懷念以前比較好懂的歌。"],
            lambda: self.maybe_trigger_event(self.show_chapter3),
        )

    def _ch2b_pick_slow(self) -> None:
        self.apply_effects({"image": 10, "identity": 10, "fame": 3, "money": -3})
        self._apply_npc_effects({"producer": 10, "friend": 10})
        self.update_status_panel()
        self.show_result_scene(
            "CHAPTER 2 RESULT：轉型之後｜慢火累積",
            "「你沒有為了榜單硬轉彎。公司嘴上抱怨，卻仍替你留了一條藝術行銷的窄路。"
            "經紀人把咖啡推到你面前：『你可以慢，但不能停。』\n\n"
            "你把那句話記下來，像記一句咒語。」",
            ["@critic_room：他可能不是最快紅的，但會紅很久。", "@indiefan：這才是藝術家的樣子。", "@industrytalk：商業面還是有疑慮。"],
            lambda: self.maybe_trigger_event(self.show_chapter3),
        )

    def _ch2b_pick_market(self) -> None:
        self.apply_effects({"fame": 10, "money": 8, "image": -3, "identity": -5})
        self._apply_npc_effects({"manager": 10, "producer": -5, "rival": 3})
        self.update_status_panel()
        self.show_result_scene(
            "CHAPTER 2 RESULT：轉型之後｜更市場的入口",
            "「你把旋律線拉直、把副歌變得更『一聽就懂』。數據很快給出正向回饋，"
            "經紀人拍桌：『對嘛，這才是能養活團隊的作品。』\n\n"
            "你笑了笑，心裡卻知道：你交換了一些神秘，換來一些確定。」",
            ["@popfan：這次好聽很多欸。", "@critic_room：變好入口了，但也少了一點神秘感。", "@industrytalk：這是比較成熟的選擇。"],
            lambda: self.maybe_trigger_event(self.show_chapter3),
        )

    # ── Chapter 2C ──────────────────────────────────────────────

    def _show_ch2c_viral(self) -> None:
        story = (
            "「你原本以為那首歌已經結束了，沒想到某天，它突然出現在社群平台，"
            "被網友用來當作短影音配樂。幾小時後，它不是慢慢紅，而是直接被瘋傳。\n\n"
            "『這是誰的歌？』\n『有點怪，但會上癮。』\n『停不下來。』\n\n"
            "凌晨兩點，經紀人打來電話：『你的歌爆了，你現在要決定怎麼處理這波流量。』」"
        )
        if self.player.get("hidden_producer"):
            story += (
                "\n\n「更奇怪的是，爆紅的不是原曲，而是一個被重新編曲過的版本。"
                "節奏更緊、情緒更集中，像是有人精準地改造了它。你突然想起那位神秘製作人，"
                "以及他錄音時近乎不安的沉默。」"
            )

        self.show_scene("CHAPTER 2C：地下黑暗線 — 病毒式爆紅", story, ["（全網都在問你是誰…）"])
        self.clear_choice_buttons()

        def pick_commerce() -> None:
            self.apply_effects({"fame": 15, "money": 12, "image": -8, "identity": -10})
            self._apply_npc_effects({"manager": 20, "producer": -10, "friend": -8})
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：病毒爆紅之後｜接住流量",
                "「你選擇讓作品更靠近大眾的耳朵。混音、剪輯、視覺素材在一週內全部重排，"
                "公司把資源堆到你面前，像堆一座橋。\n\n當你終於躺下，腦中卻不停回放那些被改短的旋律。」",
                ["@musicdaily：他真的接住這波流量了。", "@popfan：商業化之後反而更好聽。", "@indiefan：感覺他被市場吃掉了。"],
                lambda: self.maybe_trigger_event(self.show_chapter3),
            )

        def pick_underground() -> None:
            self.apply_effects({"image": 12, "identity": 12, "fame": 3, "money": -3})
            self._apply_npc_effects({"producer": 15, "friend": 12, "manager": -8})
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：病毒爆紅之後｜留在地下",
                "「你沒有把作品磨成最容易傳播的形狀。你拒絕了幾個過度包裝的企劃，"
                "經紀人急得冒汗，卻也拿你沒辦法：『你至少讓我發一張現場照吧？』\n\n"
                "你答應了最小的讓步，心裡卻清楚——你守住了某條線。」",
                ["@indiefan：拜託不要把這首歌做成罐頭流行。", "@critic_room：他好像真的不太在乎爆紅。", "@popwatch：錯過這波會不會很可惜？"],
                lambda: self.maybe_trigger_event(self.show_chapter3),
            )

        def pick_pr() -> None:
            self.apply_effects({"fame": 18, "controversy": 18, "image": -12, "identity": -5, "health": -5})
            self._apply_npc_effects({"manager": 15, "rival": 10, "friend": -12, "producer": -5})
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：病毒爆紅之後｜輿論操作",
                "「話題像雪球愈滾愈大。你與團隊幾乎不再睡覺，會議室裡全是紅色提醒。"
                "經紀人盯著曲線喃喃自語：『我們在贏…吧？』\n\n"
                "你看著鏡子裡的自己，突然有一瞬間認不出來。」",
                ["@rumorpage：這波操作感超重。", "@haterzone：他是不是故意製造爭議？", "@musicdaily：不管你喜不喜歡，他確實成功讓所有人都在討論。"],
                self._show_hidden_producer_reveal if self.player.get("hidden_producer") else lambda: self.maybe_trigger_event(self.show_chapter3),
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
            self.apply_effects({"fame": 10, "controversy": 10, "identity": -10, "image": -5})
            self._apply_npc_effects({"manager": 5, "rival": 8, "friend": -10})
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：星辰議會之後｜更深的水",
                "「你告訴自己：先把作品完成，再去想真相。但你也開始注意到——"
                "某些邀約來得太剛好、某些熱搜來得太整齊。\n\n"
                "你在深夜把通訊錄裡一個名字標成紅色。」",
                ["@rumorpage：他身邊的人真的越來越神秘。", "@haterzone：這人根本像邪教偶像。", "@stanaccount：我不知道發生什麼事，但我停不下來。"],
                lambda: self.maybe_trigger_event(self.show_chapter3),
            )

        def pick_cut() -> None:
            self.apply_effects({"image": 8, "identity": 10, "fame": -5, "health": -3})
            self._apply_npc_effects({"friend": 15, "producer": 8, "manager": -5})
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 2 RESULT：星辰議會之後｜抽身",
                "「你開始刻意缺席某些聚會，也婉拒了幾個來路不明的合作。"
                "經紀人皺眉：『你確定要放棄這些曝光？』你回答得很慢，卻很堅定。\n\n"
                "你失去一些熱度，但睡覺變得比較容易。」",
                ["@critic_room：他好像在刻意避開某種成功公式。", "@indiefan：這個選擇很勇敢。", "@popwatch：怎麼突然消失一陣子？"],
                lambda: self.maybe_trigger_event(self.show_chapter3),
            )

        self.add_choice("繼續利用這股力量", pick_use)
        self.add_choice("試著切斷與神秘製作人的關係", pick_cut)

    # ── Chapter 3 ────────────────────────────────────────────────

    def _chapter3_branch(self) -> str:
        p = self.player
        image = int(p["image"])
        fame = int(p["fame"])
        if image <= 40:
            return "controversial"
        if fame >= 75 and image >= 55:
            return "global_icon"
        return "mature_artist"

    def show_chapter3(self) -> None:
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
            self.apply_effects({"fame": 10, "money": 10, "image": 3, "identity": -10, "health": -5})
            self._apply_npc_effects({"manager": 15, "rival": 5, "friend": -12, "producer": -5})
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：完美人設的燈光下",
                "「你把笑容練到剛好的角度，把每句話都收進安全範圍。"
                "品牌方滿意地點頭，經紀人看著排程表說：『這就是頂流的樣子。』\n\n"
                "你在後台望著鏡子，突然覺得那張臉既熟悉又陌生。」",
                ["@musicdaily：他真的成為全球級偶像了。", "@popfan：這場巡演根本時代記憶。", "@critic_room：完美到有點不像真人。"],
                self._show_final_night,
            )

        def pick_self() -> None:
            self.apply_effects({"image": 12, "identity": 10, "fame": 3, "money": -3})
            self._apply_npc_effects({"producer": 15, "friend": 12, "manager": -8})
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：把真實放回作品裡",
                "「你在新歌裡放進一段沒那麼『好聽』、卻很真誠的念白。"
                "經紀人看完母帶沉默很久，最後只說：『你確定要冒這個險？』你點頭。\n\n"
                "幾天後，留言區開始出現『我好像比較認識他了』。」",
                ["@critic_room：他終於不只是流行明星，而是創作者。", "@stanaccount：這張新作品讓我重新認識他。", "@popwatch：有些粉絲可能不習慣，但這很重要。"],
                self._show_final_night,
            )

        self.add_choice("維持完美偶像人設", pick_idol)
        self.add_choice("在作品中加入真正的自我", pick_self)

    def _show_ch3_mature_artist(self) -> None:
        story = (
            "「你沒有用最爆炸的方式成名，卻一步一步累積出自己的位置。如今，獎季來臨，"
            "你第一次被正式放進『實力派』的討論中。\n\n"
            "公司希望你配合獎季公關，穩定維持地位。但你心裡知道，"
            "真正的突破往往不會發生在最安全的選擇裡。」"
        )
        self.show_scene("CHAPTER 3：獎季與成熟巨星", story, ["（獎季預測文洗版中…）"])
        self.clear_choice_buttons()

        def pick_pr() -> None:
            self.apply_effects({"fame": 10, "image": 5, "money": 8, "identity": -3})
            self._apply_npc_effects({"manager": 12, "rival": 5})
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：獎季的穩健打法",
                "「你照表操課跑完每一場訪談、每一次紅毯、每一支短片。"
                "公關團隊在群組裡貼滿『OK』，經紀人拍拍你：『你做得很好。』\n\n"
                "你點頭，卻在某個頒獎夜後台，突然很想一個人走一段路。」",
                ["@musicdaily：他終於被主流獎項看見了。", "@industrytalk：這一步走得很穩。", "@critic_room：成熟，但不算冒險。"],
                self._show_final_night,
            )

        def pick_art() -> None:
            self.apply_effects({"image": 15, "identity": 12, "fame": 3, "money": -8})
            self._apply_npc_effects({"producer": 18, "friend": 10, "manager": -10})
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：冒險的那條路",
                "「你推掉幾個更賺錢的合作，把時間留給一個更瘋狂的創作計畫。"
                "經紀人臉色不好看，卻仍替你擋下外界質疑：『他至少知道自己要什麼。』\n\n"
                "你把耳機戴上，覺得世界安靜了一點。」",
                ["@critic_room：這可能是他目前最重要的作品。", "@indiefan：他沒有背叛自己。", "@popwatch：商業成績可能會受影響，但評價很高。"],
                self._show_final_night,
            )

        self.add_choice("配合獎季公關，穩定維持地位", pick_pr)
        self.add_choice("放棄部分商業利益，追求藝術突破", pick_art)

    def _show_ch3_controversial(self) -> None:
        story = (
            "「你的名字已經不只是名字，而是一場永遠不會結束的爭論。大型爭議爆發後，"
            "媒體、粉絲、黑粉、品牌全都盯著你。\n\n"
            "公司希望你低頭道歉，重新包裝形象。但另一個聲音告訴你："
            "既然世界已經把你變成怪物，也許你可以直接成為傳奇。」"
        )
        self.show_scene("CHAPTER 3：爭議巨星", story, ["（全網吵翻天…）"])
        self.clear_choice_buttons()

        def pick_fight() -> None:
            self.apply_effects({"fame": 12, "controversy": 12, "image": -10, "identity": 3, "health": -5})
            self._apply_npc_effects({"rival": 8, "manager": 5, "friend": -8, "producer": -5})
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：擁抱標籤之後",
                "「你不再試圖解釋所有誤讀。你把爭議寫進歌里，把攻擊變成舞台效果。"
                "經紀人一边擦汗一边笑：『你瘋了…但數據真的在跳。』\n\n"
                "你望著台下，突然覺得自己像站在刀尖上跳舞。」",
                ["@haterzone：他真的完全不演了。", "@stanaccount：我知道他很瘋，但我就是移不開眼睛。", "@musicdaily：不論喜不喜歡，他就是現在最有話題的人。"],
                self._show_final_night,
            )

        def pick_apology() -> None:
            self.apply_effects({"image": 10, "controversy": -8, "fame": -5, "health": -3, "identity": -5})
            self._apply_npc_effects({"manager": 10, "friend": 8, "rival": -5})
            self.update_status_panel()
            self.show_result_scene(
                "CHAPTER 3 RESULT：道歉與修補",
                "「你在鏡頭前低頭，語氣克制，努力把每一句話說得真誠。"
                "公司在旁邊緊盯逐字稿，經紀人小聲說：『先活下來，再談下一步。』\n\n"
                "你說完最後一句，才發現自己手心全是汗。」",
                ["@popwatch：這次道歉有救回來嗎？", "@haterzone：太假了吧，現在才想洗白。", "@stanaccount：至少他願意面對。"],
                self._show_final_night,
            )

        self.add_choice("反擊媒體，擁抱負面標籤", pick_fight)
        self.add_choice("低頭道歉，試圖洗白", pick_apology)

    def _show_final_night(self) -> None:
        # 根據 NPC 好感度給出特殊提示
        affinity = self.player.get("npc_affinity", {})
        extra = []
        if affinity.get("friend", 0) >= 80:
            extra.append("\n阿諾傳來一條語音：「不管結果怎樣，你還是你。」")
        if affinity.get("producer", 0) >= 80:
            extra.append("\n陳製作留下一張便條：「那首歌，你沒有背叛它。」")
        if affinity.get("manager", 0) >= 80:
            extra.append("\n林經紀難得說了句：「你讓我想起了我當年也有夢想。」")
        if affinity.get("rival", 0) >= 70:
            extra.append("\nSky 傳來一個訊息：「下次我們要再合作。不是競爭。」")

        extra_text = "".join(extra)
        self.show_scene(
            "FINAL NIGHT：最終夜 — 成名前的回望",
            "「在最終結果揭曉前，你獨自坐在休息室裡。外面是粉絲、媒體、公司、品牌與整個世界的聲音。"
            "你看著鏡中的自己，突然想起剛簽約的那一天。\n\n"
            "你已經走了很遠，但你也不確定自己失去了什麼。」" + extra_text,
            ["（手機震動不停，但你暫時不想看。）"],
        )
        self.clear_choice_buttons()
        self.add_choice("查看最終結局", self.show_ending)

    # ── 結局 ─────────────────────────────────────────────────────

    def compute_ending(self) -> Tuple[str, str]:
        self.clamp_stats()
        p = self.player
        fame = int(p["fame"])
        image = int(p["image"])
        health = int(p["health"])
        controversy = int(p["controversy"])
        identity = int(p["identity"])
        affinity = p.get("npc_affinity", {})

        # 新增：NPC 好感度加成判斷
        friend_bonus = affinity.get("friend", 0) >= 75
        producer_bonus = affinity.get("producer", 0) >= 75

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
            if producer_bonus:
                return (
                    "ARTISTIC ICON：藝術傳奇（陳製作特別版）",
                    "「你沒有成為最容易被消費的明星，卻成為最難被取代的存在。"
                    "多年後，音樂學院開始研究你的作品。而陳製作在採訪中說：\n"
                    "『我只是打開了一扇門，走進去的是他自己。』」",
                )
            return (
                "ARTISTIC ICON：藝術傳奇",
                "「你沒有成為最容易被消費的明星，卻成為最難被取代的存在。"
                "多年後，音樂學院開始研究你的作品，稱你為不屬於時代的人。」",
            )
        if fame < 20 or health <= 10:
            if friend_bonus:
                return (
                    "FALLEN STAR：隕落巨星（阿諾特別版）",
                    "「名氣散去，合約終止，媒體不再提起你的名字。"
                    "但阿諾在你最低谷的那個夜晚，仍然坐在你旁邊。\n\n"
                    "也許這才是最重要的東西。」",
                )
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
        p = self.player
        hp = "是" if p.get("hidden_producer") else "否"
        affinity = p.get("npc_affinity", {})
        events = p.get("triggered_events", [])
        lines = [
            "── 最終狀態 ──",
            f"城市：{p.get('city') or '—'}　風格：{p.get('style') or '—'}　路線：{p.get('route') or '—'}",
            f"神秘製作線索：{hp}",
            f"名氣：{int(p['fame'])}　形象：{int(p['image'])}　健康：{int(p['health'])}",
            f"金錢：{int(p['money'])}　自我認同：{int(p['identity'])}　爭議度：{int(p['controversy'])}",
            "",
            "── NPC 好感度 ──",
        ]
        for npc_id, info in NPC_DEFS.items():
            val = affinity.get(npc_id, 50)
            bar = "█" * (val // 10) + "░" * (10 - val // 10)
            lines.append(f"{info['icon']} {info['name']}：{bar} {val}")
        lines.append("")
        lines.append(f"觸發突發事件：{len(events)} 個")
        if events:
            event_titles = {e["id"]: e["title"] for e in RANDOM_EVENTS}
            for eid in events:
                lines.append(f"  • {event_titles.get(eid, eid)}")
        return "\n".join(lines)

    def show_ending(self) -> None:
        title, body = self.compute_ending()
        stats_block = self._format_final_stats()
        full_text = f"ENDING：{title}\n\n{body}\n\n{stats_block}"
        self.set_story(full_text)
        self.update_social_reactions([
            "@musicdaily：故事告一段落，但音樂還在。",
            "@you：點擊「重新開始」再玩一次不同選擇吧。",
        ])
        self.clear_choice_buttons()
        self.add_choice("重新開始", self.restart_game)


def main() -> None:
    app = GlobalStarApp()
    app.mainloop()


if __name__ == "__main__":
    main()
    
