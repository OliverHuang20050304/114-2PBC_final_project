"""場景插圖路徑解析。"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from game.paths import (
    CH1_BRANCH_DIRS,
    CH1_INTRO_DIR,
    CH2A_EVENT1_DIR,
    CH2A_EVENT2_DIR,
    CH2A_ROOT,
    CH2B_EVENT1_DIR,
    CH2B_EVENT2_DIR,
    CH2B_ROOT,
    CH2C_ROOT,
    CH3_BRANCH1_DIR,
    CH3_BRANCH2_DIR,
    CH3_BRANCH3_DIR,
)


def ch1_image_path(scene_id: str) -> Optional[Path]:
    """依場景編號回傳第一章對應 JPG 路徑。"""
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
    """依場景編號回傳第二章 A 路線 JPG 路徑。"""
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
    """依場景編號回傳第二章 B 路線 JPG 路徑。"""
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


def ch2c_image_path(scene_id: str) -> Optional[Path]:
    """依場景編號回傳第二章 C 路線 JPG 路徑。"""
    sid = scene_id.zfill(3)
    if sid not in {"046", "047", "048"}:
        return None
    path = CH2C_ROOT / f"{sid}.jpg"
    return path if path.is_file() else None


def ch3_image_path(scene_id: str) -> Optional[Path]:
    """依場景編號回傳第三章對應 PNG 路徑。

    Args:
        scene_id: 場景編號，例如 "100"。100~120 對應 CH3_new_1，
            121~134 對應 CH3_new_2，135~148 對應 CH3_new_3。

    Returns:
        對應圖片的絕對路徑；若編號不在範圍內或檔案不存在則回傳 None。
    """
    sid = scene_id.zfill(3)
    num = int(sid)
    if 100 <= num <= 120:
        path = CH3_BRANCH1_DIR / f"{sid}.png"
    elif 121 <= num <= 134:
        path = CH3_BRANCH2_DIR / f"{sid}.png"
    elif 135 <= num <= 148:
        path = CH3_BRANCH3_DIR / f"{sid}.png"
    else:
        return None
    return path if path.is_file() else None
