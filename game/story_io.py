"""讀取對照表旁白與佔位符替換。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from game.paths import CH1_STORY_FILE


def clean_story_text(text: str) -> str:
    """清理對照表中的格式殘留。"""
    cleaned = re.sub(r"^status_flavor\s*=\s*\"\"\"?\s*", "", text.strip())
    return cleaned.replace('"""', "").strip()


def load_story_map(path: Path) -> Dict[str, str]:
    """讀取圖片編號與旁白對照表。"""
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
    """讀取第一章圖片編號與旁白對照表。"""
    return load_story_map(path)


def format_narrative(text: str, player: Dict[str, Any]) -> str:
    """替換旁白中的城市、風格等佔位符。"""
    city = str(player.get("city") or "這座城市")
    style = str(player.get("style") or "流行")
    formatted = text.replace("{city_name}", city).replace("{style}", style)
    return formatted.replace("**", "")
