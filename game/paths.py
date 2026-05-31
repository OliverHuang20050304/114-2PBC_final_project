"""資源路徑與常數。"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent

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

CH2C_ROOT = PROJECT_ROOT / "image" / "Pop_Idol_Base" / "2C黑暗"
CH2C_STORY_FILE = CH2C_ROOT / "圖片文本對照Idol_CH2C.txt"

CH3_ROOT = PROJECT_ROOT / "image" / "Pop_Idol_Base" / "CH3"
CH3_STORY_FILE = CH3_ROOT / "圖片文本對照CH3.txt"
CH3_BRANCH1_DIR = CH3_ROOT / "CH3_new_1"
CH3_BRANCH2_DIR = CH3_ROOT / "CH3_new_2"
CH3_BRANCH3_DIR = CH3_ROOT / "CH3_new_3"

ENDING_VIDEO_DIR = PROJECT_ROOT / "image" / "Pop_Idol_Base" / "結局"

SCENE_IMAGE_MAX_SIZE = (680, 380)
