from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .config import AppConfig
from .scanner import MaterialSet


@dataclass(frozen=True)
class EditPlan:
    date: str
    prompt: str
    videos: list[Path]
    music: Path | None
    target_duration_seconds: int
    resolution: str
    pace: str
    title: str | None
    outro: str | None
    keep_original_audio: bool


def build_plan(materials: MaterialSet, config: AppConfig) -> EditPlan:
    prompt = materials.prompt
    duration = _parse_duration(prompt) or config.default_duration_seconds
    pace = _parse_pace(prompt)
    title = _parse_title(prompt)
    outro = "关注我，查看更多" if any(word in prompt for word in ("关注", "结尾", "片尾")) else None
    keep_original_audio = not any(word in prompt for word in ("静音", "不要原声", "去掉原声"))
    music = materials.audios[0] if materials.audios and any(word in prompt for word in ("音乐", "配乐", "bgm", "BGM")) else None

    return EditPlan(
        date=materials.date,
        prompt=prompt,
        videos=materials.videos,
        music=music,
        target_duration_seconds=duration,
        resolution=config.default_resolution,
        pace=pace,
        title=title,
        outro=outro,
        keep_original_audio=keep_original_audio,
    )


def _parse_duration(prompt: str) -> int | None:
    patterns = [
        r"(\d+)\s*秒",
        r"(\d+)\s*s",
        r"(\d+)\s*分钟",
        r"(\d+)\s*min",
    ]
    for pattern in patterns:
        match = re.search(pattern, prompt, flags=re.IGNORECASE)
        if not match:
            continue
        value = int(match.group(1))
        if "分钟" in match.group(0) or "min" in match.group(0).lower():
            value *= 60
        return max(5, min(value, 3600))
    return None


def _parse_pace(prompt: str) -> str:
    if any(word in prompt for word in ("快节奏", "节奏快", "紧凑", "高能")):
        return "fast"
    if any(word in prompt for word in ("慢节奏", "舒缓", "慢一点")):
        return "slow"
    return "normal"


def _parse_title(prompt: str) -> str | None:
    title_match = re.search(r"(?:标题|开头文字|片头)[：:]\s*(.+)", prompt)
    if title_match:
        return title_match.group(1).strip()[:40]
    if any(word in prompt for word in ("标题", "片头", "开头")):
        return "今日精彩片段"
    return None

